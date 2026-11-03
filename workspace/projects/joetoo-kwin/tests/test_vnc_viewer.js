'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname,'..','joetoo-kwin-resident.js'),'utf8');
const implementation = source.slice(source.indexOf('function managedViewerFromBroker()'));
function harness(kind='normal') {
    const calls=[], moves=[];
    const auth={pid:42,resourceClass:'Vncviewer',normalWindow:true,internalId:'auth'};
    const desktop={pid:42,resourceClass:'Vncviewer',normalWindow:true,internalId:'viewer'};
    const unrelated={...desktop,pid:99,internalId:'other'};
    const windows={10:auth,20:desktop,30:unrelated};
    if(kind==='gone')desktop.deleted=true;
    const c={workspace:{getClient(xid){calls.push(xid);return windows[xid];}},
        BRIDGE:'bridge',PATH:'/path',observerSource:'source',windowUUID:w=>w.internalId,
        registerShortcut(){},placeWindow:(win,r)=>moves.push([win.internalId,r.window_uuid]),finish(){},
        callDBus(bus,path,iface,method,payload,callback){
            if(method==='TakeManagedViewer') callback(JSON.stringify({id:'request',claim:'claim',source:'source',pid:42,xids:[20,30]}));
            else {const r=JSON.parse(payload);c.result=r;callback(kind==='place'?JSON.stringify({id:'placement',source:'source',window_uuid:'viewer',remaining_ms:15000}):'');}
        }};
    vm.createContext(c);vm.runInContext(implementation,c);c.managedViewerFromBroker();return {c,calls,moves};
}
test('desktop XID resolves to correct UUID without selecting same-PID normal auth window',()=>{
    const {c,calls}=harness();assert.deepEqual(JSON.parse(JSON.stringify(c.result.matches)),[{xid:20,uuid:'viewer'}]);assert.ok(!calls.includes(10));
});
test('only broker-approved same UUID is placed',()=>assert.deepEqual(harness('place').moves,[['viewer','viewer']]));
test('disappeared viewer is not offered for registration',()=>assert.equal(harness('gone').c.result.matches.length,0));
