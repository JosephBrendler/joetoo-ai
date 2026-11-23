'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'..','joetoo-kwin-resident.js'),'utf8');
const implementation=source.slice(source.indexOf('function controlFocusFromBroker()'));
function harness(action='restore') {
    const desktop={x11DesktopNumber:1};
    const control={id:'control',desktops:[desktop],deleted:false,minimized:false};
    const other={id:'other',desktops:[desktop]};
    let active=other, activations=0, callback, result;
    const workspace={currentDesktop:desktop,windowList:()=>[control,other]};
    Object.defineProperty(workspace,'activeWindow',{get:()=>active,set(w){active=w;activations++;}});
    const c={workspace,observerSource:'source',BRIDGE:'b',PATH:'/b',windowUUID:w=>w?w.id:'',registerShortcut:()=>{},
        callDBus(...args){if(args[3]==='TakeControlFocus')callback=args.at(-1);else result=JSON.parse(args[5]);}};
    vm.runInNewContext(implementation,c);
    return {control,other,workspace,c,get activations(){return activations;},get result(){return result;},
        setActive(w){active=w;},start(){c.controlFocusFromBroker();},
        reply(extra={}){callback(JSON.stringify({id:'request',source:'source',action,remaining_ms:3000,window_uuid:'control',...extra}));}};
}
test('capture saves active UUID before asynchronous claim completes',()=>{
    const h=harness('capture');h.setActive(h.control);h.start();h.setActive(h.other);h.reply();
    assert.deepEqual(h.result,{state:'captured',window_uuid:'control'});assert.equal(h.activations,0);
});
test('no active window produces harmless empty capture',()=>{
    const h=harness('capture');h.setActive(null);h.start();h.reply();
    assert.deepEqual(h.result,{state:'no_active_window',window_uuid:null});
});
test('one normal KWin activation only, without placement or desktop mutation',()=>{
    const h=harness();h.control.desktops=[{x11DesktopNumber:1}];const before=JSON.stringify(h.control);const desktop=h.workspace.currentDesktop;
    h.start();h.reply();assert.equal(h.activations,1);assert.equal(h.workspace.activeWindow,h.control);
    assert.equal(JSON.stringify(h.control),before);assert.equal(h.workspace.currentDesktop,desktop);
    assert.equal(h.result.state,'requested');
});
for(const [name,change,state] of [
    ['deleted',h=>h.control.deleted=true,'missing'],
    ['minimized',h=>h.control.minimized=true,'minimized'],
    ['other desktop',h=>h.control.desktops=[{x11DesktopNumber:2}],'off_desktop'],
    ['already active',h=>h.setActive({id:'control'}),'already_active']]) {
    test(name+' never activates',()=>{const h=harness();change(h);h.start();h.reply();
        assert.equal(h.activations,0);assert.equal(h.result.state,state);});
}
test('all-desktops control may reactivate on current displayed desktop',()=>{
    const h=harness();h.control.onAllDesktops=true;h.control.desktops=[];h.start();h.reply();assert.equal(h.activations,1);
});
test('resident replacement or malformed claim cannot activate',()=>{
    const h=harness();h.start();h.reply({source:'old'});assert.equal(h.activations,0);assert.equal(h.result,undefined);
});

test('expired or absent claim never activates a window',()=>{
    const h=harness();h.start();h.reply({remaining_ms:0});assert.equal(h.activations,0);
    assert.equal(h.result,undefined);
});
test('duplicate live UUIDs fail closed instead of choosing a window',()=>{
    const h=harness();h.other.id='control';h.start();h.reply();
    assert.equal(h.activations,0);assert.equal(h.result.state,'missing');
});
