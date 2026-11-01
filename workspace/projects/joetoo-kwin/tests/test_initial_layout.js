'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '..', 'joetoo-kwin-resident.js'), 'utf8');
const implementation = source.slice(source.indexOf('function initialLayoutFromBroker()'));
function harness(layers, current=3, nativeIds=false) {
    const desktop = {x11DesktopNumber:3};
    const windows = layers.map((layer,i) => ({internalId:nativeIds ?
        'abcdef00-0000-4000-8000-'+String(i+1).padStart(12,'0') : 'w'+i, layer, deleted:false, tile:null,
        maximizeMode:0, fullScreen:false, keepAbove:false, keepBelow:false, desktops:[desktop], onAllDesktops:false,
        frameGeometry:{x:i*100,y:0,width:100,height:100}}));
    const unrelated = {internalId:'unrelated'};
    const workspace = {activeWindow:unrelated, currentDesktop:current===3?desktop:{x11DesktopNumber:current},
        stackingOrder:[unrelated,...windows],
        raiseWindow(w) {this.stackingOrder=this.stackingOrder.filter(x=>x!==w).concat(w);}};
    const entries = windows.map(w => ({uuid:w.internalId,layer:w.layer,desktop:3,
        geometry:{...w.frameGeometry},desktops:[3],on_all_desktops:false}));
    const order = ['under','panel','over'].flatMap(l=>entries.filter(e=>e.layer===l).map(e=>e.uuid));
    const preferred = [...entries].reverse().find(e=>e.layer==='over') || [...entries].reverse().find(e=>e.layer==='panel');
    function signal() {
        const handlers=new Set();
        return {handlers,connect(fn){handlers.add(fn);},disconnect(fn){handlers.delete(fn);},
            emit(...args){for(const fn of [...handlers])fn(...args);}};
    }
    workspace.windowActivated=signal();workspace.currentDesktopChanged=signal();workspace.windowRemoved=signal();
    let now=10, callback, result, activationRequests=0, completions=0, delayed=false;
    let active=workspace.activeWindow;
    Object.defineProperty(workspace,'activeWindow',{configurable:true,get(){return active;},set(w){
        activationRequests++;if(!delayed)active=w;
    }});
    const timers=[];
    class Timer {
        constructor(){this.timeout=signal();this.active=false;timers.push(this);}
        start(ms){this.active=true;this.due=now+ms;}
        stop(){this.active=false;}
        deleteLater(){this.deleted=true;}
    }
    const context = {workspace,observerSource:'source',BRIDGE:'b',PATH:'/b', Date:{now:()=>now},QTimer:Timer,
        windowUUID:w=>w?w.internalId:'',registerShortcut:()=>{},
        brokerState:'RUNNING',holdStatus:false,statusCallbacks:[],
        callDBus(...args) {
            if(args[3]==='TakeInitialLayout')callback=args.at(-1);
            else if(args[3]==='InitialLayoutStatus'){
                const fn=args.at(-1);
                if(context.holdStatus)context.statusCallbacks.push(fn);
                else fn(JSON.stringify({id:'id',state:context.brokerState}));
            }else {result=JSON.parse(args[5]);completions++;}
        }};
    vm.runInNewContext(implementation, context);
    return {windows,workspace,context,timers,get activationRequests(){return activationRequests;},
        get completions(){return completions;},get result(){return result;},
        delayActivation(){delayed=true;},
        activate(w){active=w;workspace.windowActivated.emit(w);},
        advance(ms){now+=ms;for(const t of timers){if(t.active && now>=t.due){t.active=false;t.timeout.emit();}}},
        assertClean(){assert.ok(timers.every(t=>!t.active && t.timeout.handlers.size===0));
            for(const key of ['windowActivated','currentDesktopChanged','windowRemoved'])
                assert.equal(workspace[key].handlers.size,0);},
        reply(overrides={}) {callback(JSON.stringify({id:'id',source:'source',entries,order,
                                         preferred_uuid:preferred?preferred.uuid:null,remaining_ms:1000,focus_timeout_ms:500,focus_poll_interval_ms:25,...overrides}));}};
}

test('initial stack respects layers, last over, and targets only cohort UUIDs',()=>{
    const h=harness(['over','under','panel','over','under']);
    h.context.initialLayoutFromBroker(); h.reply();
    assert.deepEqual(h.result.order,['w1','w4','w2','w0','w3']);
    assert.equal(h.result.active_uuid,'w3'); assert.equal(h.result.focus_attempted,true);
    assert.equal(h.workspace.stackingOrder[0].internalId,'unrelated');
    assert.equal(h.result.geometry_unchanged,true);
    // Manual raise/focus after completion has no subscription that repairs it.
    h.workspace.raiseWindow(h.windows[1]);h.workspace.activeWindow=h.windows[1];
    assert.equal(h.workspace.stackingOrder.at(-1),h.windows[1]);
});
test('last panel beats a final under; under-only and inactive groups do not activate',()=>{
    const h=harness(['panel','panel','under']);h.context.initialLayoutFromBroker();h.reply();
    assert.equal(h.result.active_uuid,'w1');
    for(const [layers,current] of [[['under','under'],3],[['over','panel'],1]]) {
        const other=harness(layers,current);other.context.initialLayoutFromBroker();other.reply();
        assert.equal(other.result.focus_attempted,false);assert.equal(other.result.active_uuid,'unrelated');
    }
});
test('focus changes during claim and deleted cohort fail before stack mutation',()=>{
    const h=harness(['panel']);h.context.initialLayoutFromBroker();h.workspace.activeWindow=h.windows[0];h.reply();
    assert.match(h.result.error,/focus/);
    const d=harness(['panel']);d.context.initialLayoutFromBroker();d.windows[0].deleted=true;d.reply();
    assert.match(d.result.error,/UUID \[w0\]: incompatible deleted=true \(type=boolean\)/);
});

test('ordinary floating windows remain compatible on displayed and inactive desktops',()=>{
    for (const current of [3,1]) {
        const h=harness(['panel','over'],current);
        h.context.initialLayoutFromBroker();h.reply();
        assert.equal(h.result.error,undefined);
        assert.deepEqual(h.result.order,['w0','w1']);
        assert.equal(h.result.geometry_unchanged,true);
    }
});

test('canonical broker UUIDs resolve braced uppercase Qt internalIds without adopting another window',()=>{
    const h=harness(['panel','over'],3,true);
    const expected=h.windows.map(w=>w.internalId);
    h.windows.forEach(w=>{w.internalId='{'+w.internalId.toUpperCase()+'}';});
    h.context.initialLayoutFromBroker();h.reply();
    assert.equal(h.result.error,undefined);
    assert.deepEqual(h.result.order,expected);
    assert.equal(h.result.active_uuid,expected[1]);
    assert.equal(h.result.geometry_unchanged,true);
    assert.equal(h.workspace.stackingOrder[0].internalId,'unrelated');
});

for (const [property,value,description] of [
    ['deleted',true,'deleted'], ['fullScreen',true,'fullscreen'],
    ['keepAbove',true,'keep-above'], ['keepBelow',true,'keep-below'],
    ['tile',{},'tile pointer'], ['maximizeMode',1,'vertical maximize'],
    ['maximizeMode',2,'horizontal maximize'], ['maximizeMode',3,'full maximize'],
    ['maximizeMode',undefined,'missing maximize property'],
    ['maximizeMode','0','string zero is not a numeric enum'],
    ['maximizeMode',null,'null is not restore']
]) {
    test('exact UUID/property diagnostic without mutation: '+description,()=>{
        const h=harness(['panel']);
        h.windows[0][property]=value;
        const order=h.workspace.stackingOrder.slice();
        const active=h.workspace.activeWindow;
        h.context.initialLayoutFromBroker();h.reply();
        assert.ok(h.result.error.includes('UUID [w0]: incompatible '+property+'='+String(value)));
        assert.ok(h.result.error.includes('(type='+typeof value+')'));
        assert.deepEqual(h.workspace.stackingOrder,order);
        assert.equal(h.workspace.activeWindow,active);
        assert.equal(h.windows[0][property],value);
        assert.equal(h.result.focus_attempted,false);
    });
}

test('missing stack UUID is never adopted from windowList',()=>{
    for (const listed of [true,false]) {
        const h=harness(['panel']);
        h.workspace.windowList=()=>listed?h.windows:[];
        h.workspace.stackingOrder=h.workspace.stackingOrder.slice(0,1);
        h.context.initialLayoutFromBroker();h.reply();
        assert.equal(h.result.error,'Error: Cohort UUID [w0]: stackingOrder match=false; windowList match='+listed);
        assert.equal(h.workspace.stackingOrder.length,1);
        assert.equal(h.result.focus_attempted,false);
    }
});
test('post-activation ordering is observed rather than inferred from raise return',()=>{
    const h=harness(['under','panel','over']);let active=h.workspace.activeWindow;
    Object.defineProperty(h.workspace,'activeWindow',{get(){return active;},set(w){active=w;h.workspace.raiseWindow(h.windows[0]);}});
    h.context.initialLayoutFromBroker();h.reply();
    assert.deepEqual(h.result.order,['w1','w2','w0']); // broker must reject this order
});
test('expired, moved and preexisting special-mode targets fail before mutation',()=>{
    const h=harness(['panel']);h.context.initialLayoutFromBroker();h.context.Date.now=()=>2000;h.reply();
    assert.match(h.result.error,/expired/);
    const moved=harness(['panel']);moved.context.initialLayoutFromBroker();moved.windows[0].frameGeometry.x=999;moved.reply();
    assert.match(moved.result.error,/changed/);
    const special=harness(['panel']);special.windows[0].keepBelow=true;special.context.initialLayoutFromBroker();special.reply();
    assert.match(special.result.error,/incompatible/);assert.equal(special.windows[0].keepBelow,true);
});


test('immediate success records one request and no temporary observers',()=>{
    const h=harness(['panel','under']);h.context.initialLayoutFromBroker();h.reply();
    assert.equal(h.result.focus_observation,'immediate');assert.equal(h.activationRequests,1);
    h.assertClean();
});
test('delayed activation succeeds after one request, rechecks stack, and releases observers',()=>{
    const h=harness(['panel','under']);h.delayActivation();h.context.initialLayoutFromBroker();h.reply();
    assert.equal(h.result,undefined);h.advance(25);assert.equal(h.result,undefined);
    h.activate(h.windows[0]);
    assert.equal(h.result.focus_observation,'delayed');assert.equal(h.result.focus_elapsed_ms,25);
    assert.equal(h.result.initial_active_uuid,'unrelated');assert.equal(h.result.active_uuid,'w0');
    assert.equal(h.activationRequests,1);assert.deepEqual(h.result.order,['w1','w0']);h.assertClean();
    h.activate(h.windows[1]);h.advance(1000);
    assert.equal(h.workspace.activeWindow,h.windows[1]);assert.equal(h.completions,1);
});
test('nonconvergence times out, retains stack/geometry evidence, and does not reclaim focus',()=>{
    const h=harness(['panel']);h.delayActivation();h.context.initialLayoutFromBroker();h.reply();
    for(let i=0;i<20;i++)h.advance(25);
    assert.equal(h.result.focus_observation,'timeout');assert.match(h.result.error,/timed out/);
    assert.deepEqual(h.result.order,['w0']);assert.equal(h.result.geometry_unchanged,true);
    assert.equal(h.activationRequests,1);h.assertClean();
});
test('unchanged preexisting active UUID is allowed; newly competing activation interrupts',()=>{
    const h=harness(['panel','under']);h.delayActivation();h.context.initialLayoutFromBroker();h.reply();
    h.advance(25);assert.equal(h.result,undefined);
    h.activate(h.windows[1]);assert.match(h.result.error,/Competing activation.*w1.*unknown/);
    assert.equal(h.activationRequests,1);h.assertClean();
});
for(const mode of ['desktop','deleted','removed','special','geometry','source','broker source']) {
    test('bounded observation interruption: '+mode,()=>{
        const h=harness(['panel','under']);h.delayActivation();h.context.initialLayoutFromBroker();h.reply();
        if(mode==='desktop') {h.workspace.currentDesktop={x11DesktopNumber:1};h.workspace.currentDesktopChanged.emit();}
        if(mode==='deleted')h.windows[0].deleted=true;
        if(mode==='removed'){h.workspace.stackingOrder=h.workspace.stackingOrder.filter(w=>w!==h.windows[0]);h.workspace.windowRemoved.emit(h.windows[0]);}
        if(mode==='special')h.windows[0].keepAbove=true;
        if(mode==='geometry')h.windows[0].frameGeometry.x++;
        if(mode==='source')h.context.observerSource='replacement';
        if(mode==='broker source')h.context.brokerState='FAILED';
        h.advance(25);
        assert.ok(h.result.error);assert.equal(h.activationRequests,1);h.assertClean();
    });
}
test('expiry and queued callbacks cannot renew lease or reactivate',()=>{
    const h=harness(['panel']);h.delayActivation();h.context.holdStatus=true;
    h.context.initialLayoutFromBroker();h.reply();
    const late=h.context.statusCallbacks[0];h.advance(1000);
    assert.match(h.result.error,/expired/);h.assertClean();
    late(JSON.stringify({id:'id',state:'RUNNING'}));h.activate(h.windows[0]);
    assert.equal(h.activationRequests,1);assert.equal(h.completions,1);
});
test('focus success returns actual post-convergence order without repairing a mismatch',()=>{
    const h=harness(['panel','under']);h.delayActivation();h.context.initialLayoutFromBroker();h.reply();
    h.workspace.raiseWindow(h.windows[1]);h.activate(h.windows[0]);
    assert.equal(h.result.focus_observation,'delayed');assert.deepEqual(h.result.order,['w0','w1']);
    assert.equal(h.activationRequests,1);h.assertClean();
});
test('timer polling fallback works without activation signals',()=>{
    const h=harness(['panel']);h.delayActivation();delete h.workspace.windowActivated;
    h.context.initialLayoutFromBroker();h.reply();
    // Change active state without emitting a usable event, then observe on timer.
    h.workspace.windowActivated={emit(){}};h.activate(h.windows[0]);h.advance(25);
    assert.equal(h.result.focus_observation,'delayed');assert.equal(h.activationRequests,1);
    assert.ok(h.timers.every(t=>!t.active));
});

test('a new activation event for the preexisting window is distinct from unchanged polling',()=>{
    const h=harness(['panel']);h.delayActivation();const prior=h.workspace.activeWindow;
    h.context.initialLayoutFromBroker();h.reply();h.advance(25);assert.equal(h.result,undefined);
    h.activate(prior);assert.match(h.result.error,/Competing activation event.*unrelated/);
    assert.equal(h.activationRequests,1);h.assertClean();
});
test('unavailable timer reports unsupported delay without repeatedly activating',()=>{
    const h=harness(['panel']);h.delayActivation();delete h.context.QTimer;
    h.context.initialLayoutFromBroker();h.reply();
    assert.equal(h.result.focus_observation,'unsupported');assert.equal(h.activationRequests,1);h.assertClean();
});

test('effective observation timing and the remaining transaction lease both bound the wait',()=>{
    const h=harness(['panel']);h.delayActivation();h.context.initialLayoutFromBroker();
    h.reply({focus_timeout_ms:60,focus_poll_interval_ms:20});
    h.advance(20);h.advance(20);assert.equal(h.result,undefined);h.advance(20);
    assert.equal(h.result.focus_observation,'timeout');assert.equal(h.result.focus_elapsed_ms,60);h.assertClean();
    const short=harness(['panel']);short.delayActivation();short.context.initialLayoutFromBroker();
    short.reply({remaining_ms:40});short.advance(40);
    assert.match(short.result.error,/expired/);assert.equal(short.activationRequests,1);short.assertClean();
});
