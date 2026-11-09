// Unit-test the browser-local trip controller without running a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function setup(user) {
  const handlers={},values={'form.trip_name':'Family day','form.party_notes':'<script>unsafe()</script>','form.morning':'7','form.morning_rides':['1','2'],'form.afternoon_rides':['*'],'form.afternoon':'5','form.visit_date':'2026-12-01','form.entry_time':'09:00','form.leave_time':'13:00','form.transfer':'90','form.days':'1'},stored=new Map(),texts=[];
  function $(selector) {return {on:(event,fn)=>{handlers[selector]=fn;},text:(v)=>{texts.push(String(v));return $(selector);},empty:()=>$(selector),append:()=>$(selector),appendTo:()=>$(selector)};}
  const mvc={Components:{get:(name)=>name==='env'?{get:()=>user}:{get:(k)=>values[k],on:(event,fn)=>{handlers[event]=fn;},set:(k,v)=>{values[k]=v;}}}};
  const context={require:(deps,fn)=>fn($,mvc),localStorage:{getItem:k=>stored.get(k),setItem:(k,v)=>stored.set(k,v)},document:{createTextNode:v=>String(v)},FileReader:class { readAsText(file){this.result=file.text;this.onload();} },Date,JSON,Array,String,Error};
  vm.runInNewContext(fs.readFileSync('queue_times/appserver/static/trip.js','utf8'),context);
  return {handlers,values,stored,texts};
}
const a=setup('alice');a.handlers['#trip-save']();
assert(a.stored.has('park-atlas-trip-v1:alice'));
assert.equal(JSON.parse(a.stored.values().next().value).fields.party_notes,'<script>unsafe()</script>');
a.values['form.trip_name']='Changed';a.handlers['#trip-load']();assert.equal(a.values['form.trip_name'],'Family day');
a.stored.set('park-atlas-trip-v1:alice','{"schema":99}');a.handlers['#trip-load']();assert(a.texts.some(t=>t.includes('could not be loaded')));
a.values['form.visit_date']='2026-02-31';a.handlers['#trip-save']();assert(a.texts.some(t=>t.includes('real calendar date')));
a.values['form.visit_date']='2026-12-01';a.values['form.leave_time']='08:00';a.handlers['#trip-save']();assert(a.texts.some(t=>t.includes('Departure must be later')));
a.values['form.leave_time']='13:00';a.handlers['change:form.morning_rides'](null,['*','123']);assert.deepEqual(Array.from(a.values['form.morning_rides']),['123']);
a.handlers['change:form.morning_rides']({previous:()=>['123']},['*','123']);assert.deepEqual(Array.from(a.values['form.morning_rides']),['*']);
const anonymous=setup(null);anonymous.handlers['#trip-save']();assert.equal(anonymous.stored.size,0);
const imported=setup('bob');imported.handlers['#trip-import']({target:{files:[{size:50,text:JSON.stringify({schema:1,fields:{...a.values}})}]}});assert(imported.texts.some(t=>t.includes('Import rejected')));
const source=setup('source');source.handlers['#trip-save']();const payload=source.stored.get('park-atlas-trip-v1:source');imported.handlers['#trip-import']({target:{files:[{size:payload.length,text:payload}]}});assert.equal(imported.values['form.trip_name'],'Family day');
assert(!fs.readFileSync('queue_times/appserver/static/trip.js','utf8').includes('.html('));
console.log('Trip controller tests passed: user scoping, save/load, malformed data, anonymous guard, text-only rendering.');
