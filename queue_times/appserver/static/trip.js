/* User-entered text is never inserted as HTML. Nothing leaves this Splunk origin. */
require(['jquery','splunkjs/mvc','splunkjs/mvc/simplexml/ready!'], function ($, mvc) {
    'use strict';
    var fields = ['trip_name','visit_date','morning','afternoon','entry','entry_time','leave_time','transfer','days','party_notes','commitments','backup','morning_rides','afternoon_rides'];
    var tokens = mvc.Components.get('default');
    var env = mvc.Components.get('env');
    var user = env && env.get('user');
    var key = user ? 'park-atlas-trip-v1:' + user : null;
    function message(text) { $('#trip-status').text(text); }
    function capture() {
        var result = {schema:1,saved_at:new Date().toISOString(),fields:{}};
        fields.forEach(function (name) { result.fields[name] = tokens.get('form.'+name); });
        return result;
    }
    function summary(trip) {
        var out = $('#trip-summary').empty();
        fields.forEach(function (name) {
            var value = trip.fields[name];
            if (value !== undefined && value !== null) {
                $('<p>').append($('<strong>').text(name.replace(/_/g,' ') + ': ')).append(document.createTextNode(Array.isArray(value)?value.join(', '):String(value))).appendTo(out);
            }
        });
    }
    $('#trip-save').on('click', function () {
        if (!key) { message('User identity unavailable. Download JSON instead of saving to shared browser storage.');return; }
        try { var trip=capture();localStorage.setItem(key,JSON.stringify(trip));summary(trip);message('Saved on this browser for your Splunk user. Apply to refresh research.'); }
        catch (e) { message('Browser storage is unavailable. Download JSON instead.'); }
    });
    $('#trip-load').on('click', function () {
        try {
            var raw=key && localStorage.getItem(key);
            if(!raw){message('No saved trip found for this user on this browser.');return;}
            var trip=JSON.parse(raw);
            if(trip.schema!==1 || !trip.fields){throw new Error('Invalid saved trip');}
            // Set park choices first so cascading resets do not erase restored ride choices.
            fields.forEach(function(name){if(trip.fields[name]!==undefined){tokens.set('form.'+name,trip.fields[name]);}});
            summary(trip);message('Loaded. Check the shortlist and click Apply to refresh research.');
        } catch(e){message('The saved trip could not be loaded. Current selections were not submitted.');}
    });
    $('#trip-export').on('click', function () {
        var trip=capture(), blob=new Blob([JSON.stringify(trip,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
        a.href=url;a.download='park-atlas-trip.json';a.click();setTimeout(function(){URL.revokeObjectURL(url);},1000);summary(trip);message('Downloaded a private trip backup. It is not uploaded to GitHub.');
    });
    $('#trip-print').on('click', function () {summary(capture());window.print();});
});
