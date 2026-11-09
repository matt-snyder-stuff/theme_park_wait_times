// Unit-test the browser-local trip controller without running a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function setup(user) {
  const handlers={},values={'form.trip_name':'Family day','form.party_notes':'<script>unsafe()</script>','form.morning':'7','form.morning_rides':['1','2']},stored=new Map(),texts=[];
  function $(selector) {return {on:(event,fn)=>{handlers[selector]=fn;},text:(v)=>{texts.push(String(v));return $(selector);},empty:()=>$(selector),append:()=>$(selector),appendTo:()=>$(selector)};}
  const mvc={Components:{get:(name)=>name==='env'?{get:()=>user}:{get:(k)=>values[k],set:(k,v)=>{values[k]=v;}}}};
  const context={require:(deps,fn)=>fn($,mvc),localStorage:{getItem:k=>stored.get(k),setItem:(k,v)=>stored.set(k,v)},document:{createTextNode:v=>String(v)},Date,JSON,Array,String,Error};
  vm.runInNewContext(fs.readFileSync('queue_times/appserver/static/trip.js','utf8'),context);
  return {handlers,values,stored,texts};
}
const a=setup('alice');a.handlers['#trip-save']();
assert(a.stored.has('park-atlas-trip-v1:alice'));
assert.equal(JSON.parse(a.stored.values().next().value).fields.party_notes,'<script>unsafe()</script>');
a.values['form.trip_name']='Changed';a.handlers['#trip-load']();assert.equal(a.values['form.trip_name'],'Family day');
a.stored.set('park-atlas-trip-v1:alice','{"schema":99}');a.handlers['#trip-load']();assert(a.texts.some(t=>t.includes('could not be loaded')));
const anonymous=setup(null);anonymous.handlers['#trip-save']();assert.equal(anonymous.stored.size,0);
assert(!fs.readFileSync('queue_times/appserver/static/trip.js','utf8').includes('.html('));
console.log('Trip controller tests passed: user scoping, save/load, malformed data, anonymous guard, text-only rendering.');
