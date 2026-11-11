#!/usr/bin/env python3
# Copyright 2025-2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dedicated VNC SSH/viewer supervisor. stdin is a validated launch job.

The short-lived frontend returns a managed placement result; its detached worker
owns both children until viewer exit. Broker/service restart never owns or kills
these applications. All control sockets and status files live in a private runtime
directory. No SSH backgrounding, -via shell command, shared master or credentials.
"""
import json
import secrets
import os
import re
from pathlib import Path
import select
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
from joetoo_kwin_vnc_target import target, settings
from joetoo_kwin_vnc_identity import ctypes_library

BUS='org.joetoo.KWinBridge'
PATH='/org/joetoo/KWinBridge'


def dbus(method, *args, timeout, destination=BUS):
    r=subprocess.run(['qdbus6',destination,PATH,BUS+'.'+method,*map(str,args)],
                     capture_output=True,text=True,timeout=timeout,check=False)
    if r.returncode:
        # D-Bus stderr can contain untrusted remote text or argument echoes.
        # Report the error namespace and only recognized local rejection text,
        # never a raw traceback, URI, credential, or complete stderr dump.
        name=re.search(r'org\.(?:joetoo\.KWinBridge|freedesktop\.DBus\.Error)\.[A-Za-z0-9_]+',r.stderr)
        details=(
            'Broker requires a local DISPLAY for the X11/XWayland identity observer',
            'X11 identity observer startup timed out', 'X11 identity observer exited',
            'X11 identity observer pipe closed',
            'Resident cannot resolve X11/XWayland viewer identity',
            'Managed desktop/slot conflict', 'Viewer readiness or cleanup is pending',
            'Previous request has not completed', 'Initial layout is still active',
            'diagnostic correlation is still active', 'managed correlation is still active',
            'Invalid VNC operational bounds', 'Invalid viewer layout',
            'Identity startup bound must be below the D-Bus bound')
        detail=next((message for message in details if message in r.stderr),
                    'Unclassified broker rejection; inspect the broker log')
        raise RuntimeError('Broker call failed: '+method+' ['+(name.group(0) if name else 'D-Bus error')+']: '+detail)
    return r.stdout.strip()


def broker_owner(timeout):
    r=subprocess.run(['qdbus6','org.freedesktop.DBus','/org/freedesktop/DBus',
        'org.freedesktop.DBus.GetNameOwner',BUS],capture_output=True,text=True,timeout=timeout,check=True)
    name=r.stdout.strip()
    if not re.fullmatch(r':[0-9]+\.[0-9]+',name): raise RuntimeError('Broker owner unavailable')
    return name


def read_status(folder):
    fd=os.open(folder/'status',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        st=os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid!=os.geteuid() or
            stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1 or st.st_size>65536):
            raise RuntimeError('Unsafe VNC status')
        raw=os.read(fd,65537)
        if len(raw)>65536: raise RuntimeError('VNC status budget exceeded')
        value=json.loads(raw)
        if not isinstance(value,dict) or value.get('state') not in ('pending','completed','failed','cancelled','unresolved'):
            raise ValueError('Invalid VNC status schema')
        return value
    finally: os.close(fd)


def ssh_argv(endpoint, control):
    args=['ssh','-N','-T','-M','-S',str(control),'-oControlMaster=yes',
          '-oControlPersist=no','-oForkAfterAuthentication=no','-oExitOnForwardFailure=yes',
          '-oGatewayPorts=no','-oClearAllForwardings=yes','-oStrictHostKeyChecking=yes',
          '-oBatchMode=yes','-oForwardAgent=no','-oForwardX11=no','-oPermitLocalCommand=no',
          '-oRemoteCommand=none']
    if endpoint['ssh_port'] is not None: args+=['-p',str(endpoint['ssh_port'])]
    destination=(endpoint['user']+'@' if endpoint['user'] else '')+endpoint['host']
    return args+['--',destination]


def control_argv(control, endpoint, command, forwarding=None):
    # Do not import other configured forwards into a control operation. Never
    # fall back to a new connection or send commands to a preexisting master.
    args=['ssh','-F','/dev/null','-S',str(control),'-O',command]
    if forwarding: args+=['-L',forwarding,'-oExitOnForwardFailure=yes']
    return args+['--',endpoint['host']]


def free_port():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1',0));return s.getsockname()[1]


def stop_owned(process, timeout):
    """Only the new child session created by this supervisor is signalled."""
    if process is None: return
    if process.poll() is None:
        os.killpg(process.pid,signal.SIGTERM)
        try: process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=timeout)
    else: process.wait()


def write_status(folder, payload):
    temporary=folder/'status.tmp'
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream: json.dump(payload,stream)
    temporary.replace(folder/'status')


class Supervisor:
    def __init__(self, job, folder):
        self.job=job;self.folder=folder;self.bounds=settings(job)
        self.endpoint=target(job['target']);self.ssh=None;self.viewer=None
        self.registration='';self.placement='';self.registered=False;self.interrupted=False
        self.owner=None;self.source=None;self.protected=False
        self.control=folder/'ssh';self.parent_fd=os.pidfd_open(job['frontend_pid'])

    def cancelled(self):
        return self.interrupted or (self.folder/'cancel').exists() or bool(select.select([self.parent_fd],[],[],0)[0])

    def pause(self):
        if self.cancelled(): raise RuntimeError('Launch cancelled before handoff')
        time.sleep(self.bounds['vnc_supervisor_poll_interval_ms']/1000)

    def call(self, method, *args):
        timeout=self.bounds['vnc_dbus_timeout_ms']/1000
        if self.owner is None or broker_owner(timeout)!=self.owner:
            raise RuntimeError('Broker owner changed or unavailable')
        return dbus(method,*args,timeout=timeout,destination=self.owner)

    def start_tunnel(self):
        self.ssh=subprocess.Popen(ssh_argv(self.endpoint,self.control),stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,close_fds=True)
        deadline=time.monotonic()+self.bounds['vnc_ssh_start_timeout_ms']/1000
        ready=False
        while time.monotonic()<deadline:
            if self.ssh.poll() is not None:
                raise RuntimeError('SSH exited; key/agent, host trust or transport may be incompatible with noninteractive mode')
            if self.control.exists():
                try:
                    r=subprocess.run(control_argv(self.control,self.endpoint,'check'),capture_output=True,
                        timeout=min(self.bounds['vnc_dbus_timeout_ms']/1000,max(.001,deadline-time.monotonic())))
                    if r.returncode==0: ready=True;break
                except subprocess.TimeoutExpired: pass
            self.pause()
        if not ready: raise RuntimeError('SSH startup timed out; authentication/transport outcome unverified')
        for _ in range(self.bounds['vnc_local_port_attempts']):
            if time.monotonic()>=deadline: break
            port=free_port()
            forwarding=f'127.0.0.1:{port}:127.0.0.1:{self.endpoint["vnc_port"]}'
            r=subprocess.run(control_argv(self.control,self.endpoint,'forward',forwarding),capture_output=True,
                timeout=max(.001,deadline-time.monotonic()))
            if r.returncode==0: return port
            self.pause()
        raise RuntimeError('SSH forwarding failed; local port collision or forwarding restriction possible')

    def run(self):
        outcome=dict(state='failed',detail='Viewer did not start',registration_request_id='',placement_request_id='')
        handed_off=False
        try:
            self.owner=broker_owner(self.bounds['vnc_dbus_timeout_ms']/1000)
            initial=json.loads(self.call('RegistryStatus'))
            if initial['observation']['synchronized'] is not True:
                raise RuntimeError('Observation unavailable')
            self.source=initial['observation']['source']
            spec={key:self.job[key] for key in ('desktop','slot','x','y','width','height')}
            spec.update(self.bounds)
            ids=json.loads(self.call('SubmitManagedViewerLaunch',json.dumps(spec)))
            self.registration=ids['registration_request_id'];self.placement=ids['placement_request_id']
            write_status(self.folder,dict(state='pending',detail='Starting dedicated noninteractive SSH tunnel'))
            port=self.start_tunnel()
            # The spawned viewer itself owns the windows. Never report this
            # worker or the SSH master as the managed launch PID.
            # An explicit empty -via overrides saved viewer configuration.
            # TigerVNC 1.16.2 calls mktunnel() only when strlen(via) > 0;
            # keep the empty argv element so it cannot create a second tunnel.
            self.viewer=subprocess.Popen(['vncviewer','-via','','-Fullcolor','-QualityLevel','9','-FullScreen=0',
                f'127.0.0.1::{port}'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,start_new_session=True,close_fds=True)
            self.call('SetManagedLaunchPid',self.registration,self.viewer.pid)
            deadline=time.monotonic()+self.bounds['vnc_viewer_ready_timeout_ms']/1000
            while time.monotonic()<deadline:
                if self.viewer.poll() is not None:
                    raise RuntimeError('Viewer exited before desktop readiness; cancellation versus connection failure unverified')
                if self.ssh.poll() is not None: raise RuntimeError('Owned SSH tunnel exited')
                if self.cancelled(): raise RuntimeError('Launch cancelled before handoff')
                subprocess.run(['qdbus6','org.kde.kglobalaccel','/component/kwin',
                    'org.kde.kglobalaccel.Component.invokeShortcut','joetoo_bridge_viewer'],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,
                    timeout=self.bounds['vnc_dbus_timeout_ms']/1000)
                status=json.loads(self.call('PollManagedLaunch',self.registration))
                if status['state']=='registered':
                    if not self.registered:
                        deadline=time.monotonic()+self.bounds['vnc_placement_timeout_ms']/1000
                    self.registered=True
                    placement=self.call('Status',self.placement)
                    if placement.startswith(('OK','ERROR')):
                        outcome=dict(state='completed' if placement.startswith('OK') else 'failed',
                            detail=placement,window_uuid=status['window_uuid'],managed_id=status['managed_id'])
                        handed_off=True;break
                elif status['state']!='pending':
                    raise RuntimeError(status.get('detail','Viewer identity failed'))
                write_status(self.folder,dict(state='pending',detail='SSH forward established; waiting for TigerVNC desktop readiness (authentication may be pending)'))
                self.pause()
            if not handed_off: raise RuntimeError('Viewer readiness/placement timed out; remote outcome unverified')
        except (OSError,RuntimeError,ValueError,KeyError,subprocess.SubprocessError) as exc:
            # Never echo raw command output, credentials or target input.
            outcome=dict(state='failed',detail=str(exc) if isinstance(exc,RuntimeError) else 'VNC launch operation failed')
        finally:
            cleanup=dict(eligible=False,broker_terminal=False,children_reaped=False)
            if not self.registered:
                cleanup_known=False
                try:
                    if not self.registration: raise RuntimeError('No owned broker request')
                    self.call('CancelManagedViewerLaunch',self.registration)
                    terminal=json.loads(self.call('PollManagedLaunch',self.registration))
                    if terminal.get('state')=='registered':
                        # Never kill a viewer enrolled before a lost/cancelled reply.
                        self.registered=True
                        raise RuntimeError('Cancellation raced viewer registration')
                    status=self.call('Status',self.placement)
                    snapshot=json.loads(self.call('RegistryStatus'))
                    windows=json.loads(self.call('ListManaged'))['windows']
                    cleanup_known=(terminal.get('request_id')==self.registration and
                        terminal.get('state') in ('failed','timeout') and
                        terminal.get('detail') in (
                            'Viewer launch cancelled or exited before readiness; cause unverified',
                            'Viewer readiness timed out; authentication outcome unknown') and
                        status.startswith('ERROR') and
                        snapshot['observation']['synchronized'] is True and
                        snapshot['observation']['source']==self.source and
                        snapshot.get('viewer_cleanup_uncertain') is False and
                        snapshot.get('initial_layout_active') is False and
                        snapshot['request_counts']['pending']==snapshot['request_counts']['running']==0 and
                        snapshot['presence_counts']['uncertain']==0 and
                        snapshot['placement_transaction']['state'] in ('IDLE','OK','ERROR') and
                        not any(w['intended']==dict(desktop=self.job['desktop'],slot=self.job['slot']) for w in windows))
                    cleanup.update(broker_terminal=cleanup_known,terminal=terminal,
                        registration_request_id=self.registration,placement_request_id=self.placement,
                        broker_owner=self.owner,source=self.source)
                except (OSError,RuntimeError,ValueError,KeyError,subprocess.SubprocessError):
                    self.protected=self.viewer is not None
                # Attempt both owned children, even when broker evidence is lost.
                reaped=True
                if not self.registered and not self.protected:
                    for process in (self.viewer,self.ssh):
                        try:
                            stop_owned(process,self.bounds['vnc_cleanup_timeout_ms']/1000)
                            if process is not None and process.returncode is None: reaped=False
                        except (OSError,RuntimeError,subprocess.SubprocessError): reaped=False
                    self.ssh=None  # Both cleanup attempts finished; uncertainty stays explicit.
                else: reaped=False
                cleanup.update(children_reaped=reaped,eligible=cleanup_known and reaped)
                if not cleanup['eligible']:
                    outcome=dict(state='unresolved',detail='Owned VNC cleanup or broker cancellation is uncertain')
            elif not handed_off:
                # Never close an enrolled viewer because placement/reporting
                # failed. Stop subsequent launches until broker state is known.
                outcome=dict(state='unresolved',detail='Registered viewer retained; layout finalization uncertain')
            outcome.update(cleanup=cleanup,nonce=self.job.get('nonce'),worker_pid=os.getpid(),
                registration_request_id=self.registration,placement_request_id=self.placement,
                viewer_pid=self.viewer.pid if self.viewer else None,
                ssh_pid=self.ssh.pid if self.ssh else None,
                desktop_readiness="verified" if self.registered else "not_verified",
                vnc_authentication="unverified", remote_session_usability="unverified")
            write_status(self.folder,outcome)
        try:
            if (self.registered or self.protected) and self.viewer is not None:
                # No more broker dependence after handoff. Signals to this
                # detached worker mean explicit cancellation, not broker stop.
                os.close(self.parent_fd);self.parent_fd=None
                while not self.interrupted:
                    try:
                        self.viewer.wait(timeout=self.bounds['vnc_supervisor_poll_interval_ms']/1000);break
                    except subprocess.TimeoutExpired: pass
                if self.interrupted: stop_owned(self.viewer,self.bounds['vnc_cleanup_timeout_ms']/1000)
        finally:
            if self.ssh is not None: stop_owned(self.ssh,self.bounds['vnc_cleanup_timeout_ms']/1000)
            if self.parent_fd is not None: os.close(self.parent_fd)
        (self.folder/'worker-exited').touch()
        # The frontend can still be consuming the final status; retain only
        # this small private record until it acknowledges receipt.
        if (self.folder/'ack').exists(): shutil.rmtree(self.folder,ignore_errors=True)


def preflight():
    for command in ('ssh','vncviewer','qdbus6'):
        if not shutil.which(command): raise RuntimeError('Missing VNC prerequisite: '+command)
    ctypes_library()
    if not re.fullmatch(r'(?:unix)?:[0-9]+(?:\.[0-9]+)?',os.environ.get('DISPLAY','')):
        raise RuntimeError('A local X11/XWayland DISPLAY is required')
    if not hasattr(os,'pidfd_open'): raise RuntimeError('VNC supervisor requires Linux pidfd support')
    descriptor=os.pidfd_open(os.getpid());os.close(descriptor)


def launch(job):
    preflight();settings(job);target(job['target'])
    runtime=Path(os.environ.get('XDG_RUNTIME_DIR',''))
    info=runtime.stat()
    if not runtime.is_absolute() or info.st_uid!=os.getuid() or not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o700:
        raise RuntimeError('Private user runtime directory required')
    folder=Path(tempfile.mkdtemp(prefix='joetoo-vnc-',dir=runtime))
    job['frontend_pid']=os.getpid()
    job['nonce']=secrets.token_hex(16)
    worker=subprocess.Popen([sys.executable,__file__,'--worker',str(folder)],stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,close_fds=True,text=True)
    worker.stdin.write(json.dumps(job));worker.stdin.close()
    bounds=settings(job)
    # Include pinned-owner lookups, startup/last-poll RPCs and terminal cleanup
    # in the frontend envelope; each individual mechanical call keeps its bound.
    deadline=time.monotonic()+(bounds['vnc_ssh_start_timeout_ms']+bounds['vnc_viewer_ready_timeout_ms']+
        bounds['vnc_cleanup_timeout_ms']*2+bounds['vnc_dbus_timeout_ms']*20+bounds['vnc_placement_timeout_ms'])/1000
    result=None
    def interrupt(signum,frame): raise KeyboardInterrupt
    for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP): signal.signal(sig,interrupt)
    try:
        while time.monotonic()<deadline:
            try: result=read_status(folder)
            except FileNotFoundError: result=None
            except (OSError,ValueError,RuntimeError):
                result=dict(state='unresolved',detail='VNC status unavailable or invalid');break
            if result and result['state']!='pending':
                if result.get('nonce')!=job['nonce'] or result.get('worker_pid')!=worker.pid:
                    result=None
                break
            if worker.poll() is not None: break
            time.sleep(bounds['vnc_supervisor_poll_interval_ms']/1000)
    except KeyboardInterrupt:
        (folder/'cancel').touch()
        try: worker.wait(timeout=(bounds['vnc_cleanup_timeout_ms']*2+bounds['vnc_dbus_timeout_ms'])/1000)
        except subprocess.TimeoutExpired: pass
        try:
            final=read_status(folder)
            if final.get('nonce')!=job['nonce'] or final.get('worker_pid')!=worker.pid: raise ValueError('Foreign VNC outcome')
            result=dict(final,state='cancelled',detail='Configured launch interrupted; consult registration and cleanup evidence') if final['state'] not in ('pending','unresolved') else None
        except (OSError,ValueError): result=None
    if not result or result['state']=='pending':
        (folder/'cancel').touch()
        result=dict(state='unresolved',detail='VNC supervisor final outcome unavailable; subsequent launches must stop')
    result['continuation_eligible']=False
    c=result.get('cleanup',{})
    if not isinstance(c,dict):
        result=dict(state='unresolved',detail='Invalid VNC cleanup schema',continuation_eligible=False);c={}
    if c.get('eligible') is True:
        try:
            t=c.get('terminal',{})
            if (result.get('state') not in ('failed','cancelled') or
                any(c.get(k) is not True for k in ('broker_terminal','children_reaped')) or
                t.get('request_id')!=result.get('registration_request_id') or
                c.get('registration_request_id')!=result.get('registration_request_id') or
                c.get('placement_request_id')!=result.get('placement_request_id') or
                t.get('state') not in ('failed','timeout') or
                t.get('detail') not in ('Viewer launch cancelled or exited before readiness; cause unverified',
                    'Viewer readiness timed out; authentication outcome unknown') or
                not c.get('source') or c.get('broker_owner')!=broker_owner(bounds['vnc_dbus_timeout_ms']/1000)):
                raise RuntimeError('Invalid VNC cleanup receipt')
            if worker.wait(timeout=bounds['vnc_cleanup_timeout_ms']/1000)!=0: raise RuntimeError('Worker cleanup exit failed')
            if not (folder/'worker-exited').is_file(): raise RuntimeError('Worker exit unavailable')
            snapshot=json.loads(dbus('RegistryStatus',timeout=bounds['vnc_dbus_timeout_ms']/1000,destination=c['broker_owner']))
            windows=json.loads(dbus('ListManaged',timeout=bounds['vnc_dbus_timeout_ms']/1000,destination=c['broker_owner']))['windows']
            if (snapshot['observation']['source']!=c['source'] or snapshot['observation']['synchronized'] is not True or
                snapshot.get('viewer_cleanup_uncertain') is not False or snapshot.get('initial_layout_active') is not False or
                snapshot['request_counts']['pending'] or snapshot['request_counts']['running'] or
                snapshot['presence_counts']['uncertain'] or snapshot['placement_transaction']['state'] not in ('IDLE','OK','ERROR') or
                any(w['intended']==dict(desktop=job['desktop'],slot=job['slot']) for w in windows) or
                broker_owner(bounds['vnc_dbus_timeout_ms']/1000)!=c['broker_owner']):
                raise RuntimeError('VNC cleanup session unavailable')
            result['continuation_eligible']=True
        except (OSError,RuntimeError,ValueError,KeyError,subprocess.SubprocessError):
            result=dict(state='unresolved',detail='VNC cleanup receipt unavailable',continuation_eligible=False)
    (folder/'ack').touch()
    if (folder/'worker-exited').exists(): shutil.rmtree(folder,ignore_errors=True)
    print(json.dumps(result))
    return 0 if result['state']=='completed' else (2 if result['state']=='unresolved' else 1)


if __name__=='__main__':
    try:
        if len(sys.argv)>1 and sys.argv[1]=='--worker':
            supervisor=Supervisor(json.load(sys.stdin),Path(sys.argv[2]))
            def cancel_worker(signum,frame): supervisor.interrupted=True
            for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP): signal.signal(sig,cancel_worker)
            supervisor.run();sys.exit(0)
        if len(sys.argv)>1 and sys.argv[1]=='--preflight': preflight();sys.exit(0)
        sys.exit(launch(json.load(sys.stdin)))
    except (ValueError,KeyError,OSError,RuntimeError) as exc:
        print(json.dumps(dict(state='failed',detail='VNC helper preflight/start failed (input redacted)')))
        sys.exit(1)
