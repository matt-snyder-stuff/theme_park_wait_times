/* Local trip persistence only. User text is rendered as text, never HTML. */
require(['jquery','splunkjs/mvc','splunkjs/mvc/simplexml/ready!'], function ($, mvc) {
    'use strict';
    var fields = ['trip_name','visit_date','morning','afternoon','entry','entry_time','leave_time','transfer','days','party_notes','commitments','backup','morning_rides','afternoon_rides'];
    var titles = {trip_name:'Trip',visit_date:'Visit date',morning:'First park',afternoon:'Second park',entry:'Entry eligibility',entry_time:'Confirmed entry time',leave_time:'Leave first park',transfer:'Transfer minutes',days:'Minimum matched weekdays',party_notes:'Party reminders',commitments:'Fixed commitments',backup:'Backup plan',morning_rides:'Morning shortlist',afternoon_rides:'Afternoon shortlist'};
    var parkNames = {'5':'EPCOT','6':'Magic Kingdom','7':'Hollywood Studios','8':'Animal Kingdom'};
    var tokens = mvc.Components.get('default'), env = mvc.Components.get('env');
    var user = env && env.get('user'), key = user ? 'park-atlas-trip-v1:' + user : null;
    function message(text) { $('#trip-status').text(text); }
    function normalize(value) {
        var list=Array.isArray(value)?value.map(String):String(value || '*').split(',');
        if(list.length>1) {list=list.filter(function(v){return v!=='*';});}
        return list.length?list:['*'];
    }
    ['morning_rides','afternoon_rides'].forEach(function(name){
        tokens.on('change:form.'+name,function(model,value){
            var current=Array.isArray(value)?value:String(value || '*').split(',');
            var previous=model && model.previous ? model.previous('form.'+name) : null;
            var before=Array.isArray(previous)?previous:String(previous || '*').split(',');
            var clean=current.indexOf('*')>=0 && before.indexOf('*')<0 ? ['*'] : normalize(current);
            if(JSON.stringify(current)!==JSON.stringify(clean)){tokens.set('form.'+name,clean);}
        });
    });
    function validate(trip) {
        if(!trip || trip.schema!==1 || !trip.fields || typeof trip.fields!=='object' || Array.isArray(trip.fields)){throw new Error('Invalid trip file format.');}
        var f=trip.fields;
        fields.forEach(function(name){
            var v=f[name];
            if(v!==undefined && typeof v!=='string' && typeof v!=='number' && !Array.isArray(v)){throw new Error('Invalid trip field: '+name);}
            if(Array.isArray(v) && v.some(function(x){return typeof x!=='string' && typeof x!=='number';})){throw new Error('Invalid shortlist.');}
        });
        if(!/^\d{4}-\d{2}-\d{2}$/.test(f.visit_date || '')){throw new Error('Enter a visit date as YYYY-MM-DD.');}
        var d=new Date(f.visit_date+'T00:00:00Z');
        if(isNaN(d.getTime()) || d.toISOString().slice(0,10)!==f.visit_date){throw new Error('Enter a real calendar date.');}
        var re=/^([01][0-9]|2[0-3]):[0-5][0-9]$/;
        if(!re.test(f.entry_time || '') || !re.test(f.leave_time || '')){throw new Error('Entry and departure must use HH:MM, 24-hour time.');}
        function minutes(s){return Number(s.slice(0,2))*60+Number(s.slice(3));}
        if(minutes(f.leave_time)<=minutes(f.entry_time)){throw new Error('Departure must be later than entry.');}
        if(['30','60','90','120'].indexOf(String(f.transfer))<0 || minutes(f.leave_time)+Number(f.transfer)>=1440){throw new Error('Choose a supported transfer that arrives before midnight.');}
        ['morning','afternoon'].forEach(function(name){if(!/^[1-9][0-9]*$/.test(String(f[name]))){throw new Error('Choose both parks.');}});
        if(['1','3','7'].indexOf(String(f.days))<0){throw new Error('Choose 1, 3 or 7 matched weekdays.');}
        ['morning_rides','afternoon_rides'].forEach(function(name){
            f[name]=normalize(f[name]);
            if(f[name].some(function(v){return !/^(\*|[1-9][0-9]*)$/.test(v);})){throw new Error('Shortlists must contain park ride IDs.');}
        });
        return trip;
    }
    function capture() {
        var result={schema:1,saved_at:new Date().toISOString(),fields:{},labels:{}};
        fields.forEach(function(name){var v=tokens.get('form.'+name);result.fields[name]=v===undefined?tokens.get(name):v;var label=tokens.get('form.'+name+'_label');if(label){result.labels[name]=String(label);}});
        return validate(result);
    }
    function summary(trip) {
        var out=$('#trip-summary').empty();
        fields.forEach(function(name){
            var value=trip.fields[name];
            if(value===undefined || value===null){return;}
            if(trip.labels && typeof trip.labels[name]==='string'){value=trip.labels[name];}
            else if(name==='morning' || name==='afternoon'){value=parkNames[value] || 'Park ID '+value;}
            else if(name==='entry'){value=value==='early'?'Eligible for early entry (confirm separately)':'General admission';}
            else if(name.indexOf('_rides')>=0){value=normalize(value).join(', ');value=value==='*'?'All rides · exploratory':'Ride IDs: '+value;}
            $('<p>').append($('<strong>').text(titles[name]+': ')).append(document.createTextNode(String(value))).appendTo(out);
        });
    }
    function restore(trip) {
        validate(trip); // Validate everything before touching current controls.
        fields.forEach(function(name){if(trip.fields[name]!==undefined){tokens.set('form.'+name,trip.fields[name]);}});
        Object.keys(trip.labels || {}).forEach(function(name){if(fields.indexOf(name)>=0 && typeof trip.labels[name]==='string'){tokens.set('form.'+name+'_label',trip.labels[name]);}});
        summary(trip);message('Loaded. Check your ride choices after the menus refresh, then Apply to run research.');
    }
    $('#trip-save').on('click',function(){
        if(!key){message('User identity unavailable. Download JSON instead of saving to shared browser storage.');return;}
        try{var trip=capture();localStorage.setItem(key,JSON.stringify(trip));summary(trip);message('Saved on this browser for your Splunk user. Apply to refresh research.');}catch(e){message(e.message || 'Unable to save.');}
    });
    $('#trip-load').on('click',function(){
        try{var raw=key && localStorage.getItem(key);if(!raw){message('No saved trip found for this user on this browser.');return;}restore(JSON.parse(raw));}catch(e){message('The saved trip could not be loaded. '+e.message);}
    });
    $('#trip-import').on('change',function(event){
        var file=event.target.files && event.target.files[0];if(!file){return;}
        if(file.size>100000){message('Trip files must be smaller than 100 KB.');return;}
        var reader=new FileReader();reader.onload=function(){try{restore(JSON.parse(reader.result));}catch(e){message('Import rejected. '+e.message);}};reader.onerror=function(){message('Unable to read this trip file.');};reader.readAsText(file);
    });
    $('#trip-export').on('click',function(){
        try{var trip=capture(),blob=new Blob([JSON.stringify(trip,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='park-atlas-trip.json';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000);summary(trip);message('Downloaded a private trip backup. Use Import trip JSON to restore it on another browser.');}catch(e){message(e.message);}
    });
    $('#trip-print').on('click',function(){try{summary(capture());document.body.classList.add('pp-print-trip');try{window.print();}finally{document.body.classList.remove('pp-print-trip');}}catch(e){message(e.message);}});
});
