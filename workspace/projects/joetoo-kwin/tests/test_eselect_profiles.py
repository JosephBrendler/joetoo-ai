# Copyright 2026 Joseph Brendler
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real eselect core, disposable executable/module path and user profiles only."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from test_step1_5a_plan import ROOT, PlannerHarness


@unittest.skipUnless(Path('/usr/bin/eselect').is_file(), 'installed eselect framework unavailable')
class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.home = self.base / 'home'; self.home.mkdir(mode=0o700)
        self.xdg = self.home / '.config'; self.xdg.mkdir(mode=0o700)
        self.root = self.xdg / 'joetoo-kwin'
        self.profiles = self.root / 'profiles'
        self.active = self.root / 'joetoo-kwin.conf'
        modules = self.base / 'modules'; modules.mkdir()
        shutil.copyfile(ROOT / 'eselect/joetoo-kwin.eselect', modules / 'joetoo-kwin.eselect')
        self.command = self.base / 'eselect'
        self.command.write_text(Path('/usr/bin/eselect').read_text().replace(
            'ESELECT_DEFAULT_MODULES_PATH="${ESELECT_DATA_PATH}/modules"',
            'ESELECT_DEFAULT_MODULES_PATH="' + str(modules) + '"', 1))
        self.command.chmod(0o755)
        self.env = {**os.environ, 'HOME': str(self.home), 'XDG_CONFIG_HOME': str(self.xdg)}

    def run_selector(self, action, *args, good=True):
        run = subprocess.run([str(self.command), '--colour=no', 'joetoo-kwin', action, *args],
                             env=self.env, capture_output=True, text=True, timeout=5)
        if good: self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        else: self.assertNotEqual(run.returncode, 0, run.stdout + run.stderr)
        return run.stdout + run.stderr

    def profile(self, name='a.conf', contents=None):
        self.profiles.mkdir(parents=True, exist_ok=True, mode=0o700)
        file = self.profiles / name
        file.write_text(contents or "screen_width=1920\nscreen_height=1080\ndesktop_session_list=('1|konsole|local|btop')\n")
        file.chmod(0o600)
        return file

    def test_list_show_no_automatic_home_setup(self):
        before=sorted(str(p.relative_to(self.home)) for p in self.home.rglob('*'))
        self.assertIn('none', self.run_selector('list'))
        self.assertIn('no user selection', self.run_selector('show'))
        self.assertFalse(self.root.exists())
        self.assertEqual(sorted(str(p.relative_to(self.home)) for p in self.home.rglob('*')),before)

    def test_list_show_set_names_and_numbers_use_relative_link(self):
        self.profile(); self.profile('b.conf')
        self.assertIn('a.conf', self.run_selector('list'))
        self.run_selector('set', '1')
        self.assertEqual(os.readlink(self.active), 'profiles/a.conf')
        self.assertIn('a.conf', self.run_selector('show'))
        self.run_selector('set', 'b.conf')
        self.assertEqual(os.readlink(self.active), 'profiles/b.conf')
        self.assertIn('b.conf', self.run_selector('show'))

    def test_list_marks_only_the_valid_selected_profile(self):
        self.profile(); self.profile('b.conf')
        self.assertNotIn('*', self.run_selector('list'))
        for selection, name in (('1', 'a.conf'), ('b.conf', 'b.conf')):
            self.run_selector('set', selection)
            output = self.run_selector('list')
            self.assertEqual(output.count('*'), 1)
            self.assertIn(name + ' *', output)
            self.run_selector('set', 'absent.conf', good=False)
            self.assertEqual(self.run_selector('list'), output)
            self.assertEqual(self.run_selector('show').strip(), name)

    def test_list_does_not_mark_regular_invalid_or_dangling_selection(self):
        self.profile()
        self.active.write_text('# regular plan\n')
        self.assertNotIn('*', self.run_selector('list'))
        self.active.unlink()
        outside = self.home / 'outside.conf'; outside.write_text('# outside\n')
        for target in ('profiles/absent.conf', str(outside)):
            self.active.symlink_to(target)
            self.assertNotIn('*', self.run_selector('list'))
            self.run_selector('show', good=False)
            self.active.unlink()

    def test_profile_commands_never_execute_bash_contents(self):
        marker = self.home / 'executed'
        self.profile(contents='touch "' + str(marker) + '"\n')
        self.run_selector('list'); self.run_selector('set', 'a.conf'); self.run_selector('show')
        self.assertFalse(marker.exists())

    def test_regular_plan_is_never_overwritten_or_migrated(self):
        self.profile(); self.active.write_text('# keep me\n')
        self.run_selector('set', 'a.conf', good=False)
        self.assertFalse(self.active.is_symlink())
        self.assertEqual(self.active.read_text(), '# keep me\n')
        self.assertIn('regular configuration', self.run_selector('show'))

    def test_reject_missing_traversal_absolute_and_option_targets(self):
        self.profile()
        for name in ('absent.conf', '../a.conf', str(self.profiles / 'a.conf'), '--help', '0', '999999'):
            with self.subTest(name=name): self.run_selector('set', name, good=False)
        self.assertFalse(self.active.exists())

    def test_reject_symlink_hardlink_unreadable_and_invalid_profiles(self):
        original = self.profile()
        outside = self.home / 'outside.conf'; outside.write_text('# outside\n')
        (self.profiles / 'link.conf').symlink_to(outside)
        os.link(outside, self.profiles / 'hard.conf')
        self.profile('invalid.conf', 'broken=(\n')
        self.profile('unreadable.conf').chmod(0)
        for name in ('link.conf', 'hard.conf', 'invalid.conf', 'unreadable.conf'):
            with self.subTest(name=name): self.run_selector('set', name, good=False)
        self.assertIn(original.name, self.run_selector('list'))
        self.assertNotIn('link.conf', self.run_selector('list'))
        self.assertFalse(self.active.exists())

    def test_dangling_and_foreign_active_symlinks_require_manual_review(self):
        self.profile()
        outside = self.home / 'other.conf'; outside.write_text('# retain\n')
        for target in ('profiles/absent.conf', str(outside)):
            with self.subTest(target=target):
                self.active.symlink_to(target)
                self.run_selector('show', good=False)
                self.run_selector('set', 'a.conf', good=False)
                self.assertEqual(os.readlink(self.active), target)
                self.active.unlink()
        self.assertEqual(outside.read_text(), '# retain\n')

    def test_unsafe_directories_and_profile_modes_are_rejected(self):
        profile = self.profile()
        for path in (self.root, self.profiles, profile):
            with self.subTest(path=path):
                old = path.stat().st_mode & 0o777
                path.chmod(0o777)
                self.run_selector('set', 'a.conf', good=False)
                path.chmod(old)
        self.assertFalse(self.active.exists())

    def test_selector_lock_is_exclusive_and_retained(self):
        import fcntl
        self.profile(); self.run_selector('set', 'a.conf')
        lock = self.root / '.profile-selection.lock'
        with lock.open('r') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.run_selector('set', 'a.conf', good=False)
        self.run_selector('set', 'a.conf')
        self.assertTrue(lock.is_file())
        self.assertFalse(list(self.root.glob('.profile-select.*')))

    def test_target_removed_during_switch_restores_previous_selection(self):
        self.profile(); target=self.profile('b.conf');self.run_selector('set','a.conf')
        commands=self.base/'bin';commands.mkdir()
        mover=commands/'mv'
        mover.write_text('#!/bin/bash\nrm -- "$DROP_PROFILE"\nexec /bin/mv "$@"\n');mover.chmod(0o755)
        self.env.update(PATH=str(commands)+os.pathsep+os.environ['PATH'],DROP_PROFILE=str(target))
        self.run_selector('set','b.conf',good=False)
        self.assertEqual(os.readlink(self.active),'profiles/a.conf')
        self.assertTrue(self.active.is_file())
        self.assertFalse(list(self.root.glob('.profile-select.*')))

    def test_first_selection_does_not_clobber_a_concurrently_created_regular_file(self):
        self.profile()
        commands=self.base/'bin';commands.mkdir()
        mover=commands/'mv'
        mover.write_text('#!/bin/bash\nprintf "preserve\\n" > "$NEW_PLAN"\nexec /bin/mv "$@"\n');mover.chmod(0o755)
        self.env.update(PATH=str(commands)+os.pathsep+os.environ['PATH'],NEW_PLAN=str(self.active))
        self.run_selector('set','a.conf',good=False)
        self.assertFalse(self.active.is_symlink())
        self.assertEqual(self.active.read_text(),'preserve\n')

    def test_existing_selection_exchange_preserves_a_racing_regular_file(self):
        self.profile();self.profile('b.conf');self.run_selector('set','a.conf')
        commands=self.base/'bin';commands.mkdir();flag=self.base/'once'
        mover=commands/'mv'
        mover.write_text('#!/bin/bash\nif [[ ! -e $ONCE ]]; then touch "$ONCE"; rm -- "$NEW_PLAN"; printf "preserve\\n" > "$NEW_PLAN"; fi\nexec /bin/mv "$@"\n')
        mover.chmod(0o755)
        self.env.update(PATH=str(commands)+os.pathsep+os.environ['PATH'],NEW_PLAN=str(self.active),ONCE=str(flag))
        self.run_selector('set','b.conf',good=False)
        self.assertFalse(self.active.is_symlink())
        self.assertEqual(self.active.read_text(),'preserve\n')
        self.assertFalse(list(self.root.glob('.profile-select.*')))

    def test_relative_xdg_falls_back_to_home(self):
        self.profile(); self.env['XDG_CONFIG_HOME'] = 'relative'
        self.run_selector('set', 'a.conf')
        self.assertEqual(os.readlink(self.active), 'profiles/a.conf')

    def test_selected_profile_loaded_and_explicit_f_bypasses_it(self):
        self.profile(); self.run_selector('set', 'a.conf')
        class Harness(PlannerHarness, unittest.TestCase): pass
        h = Harness()
        try:
            h.setUp()
            h.env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.xdg))
            self.assertIn('DRY RUN: [1]', h.run_cli('-c'))
            h.write_config(['2|konsole|local|btop', '2|konsole|local|btop'])
            self.assertIn('DRY RUN: [2]', h.run_cli('-c', '-f', str(h.config)))
            self.assertEqual(os.readlink(self.active), 'profiles/a.conf')
        finally: h.doCleanups()
