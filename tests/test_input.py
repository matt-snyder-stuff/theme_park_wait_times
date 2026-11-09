import contextlib
import importlib.util
import io
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from pathlib import Path

spec = importlib.util.spec_from_file_location('collector', 'queue_times/bin/queue_times.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
PARK = {'id': 2, 'name': 'Park & Co', 'timezone': 'Europe/London'}
RIDE = {'id': 1, 'name': 'Ride <One>', 'is_open': False, 'wait_time': 0, 'last_updated': '2026-11-03T12:00:00.000Z'}

class InputTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(m.validate({'park_ids':'2, 1,2'}), [1,2])
        self.assertIsNone(m.validate({'park_ids':'*'}))
        for params in ({'park_ids':''}, {'park_ids':'../2'}, {'park_ids':'0'}, {'park_ids':'2','interval':'60'}):
            with self.assertRaises(ValueError): m.validate(params)

    def test_nested_flat_and_duplicates(self):
        payload={'lands':[{'id':10,'name':'Land','rides':[RIDE]}], 'rides':[RIDE,dict(RIDE,id=2)]}
        events=list(m.normalize(payload,PARK,'Group',123))
        self.assertEqual(len(events),2)
        self.assertEqual(events[0]['land_id'],10)
        self.assertEqual(events[1]['land_name'],'Other rides')
        self.assertFalse(events[0]['is_open'])
        self.assertEqual(events[0]['observed_at'],123)

    def test_xml_escaping(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output): m.emit('queue_times://a','queue_times','queue_times:ride',RIDE,123)
        event=ET.fromstring(output.getvalue())
        self.assertIn('Ride <One>',event.findtext('data'))
        self.assertEqual(event.findtext('time'),'123')

    def test_park_failure_isolated(self):
        catalog=[{'name':'Group','parks':[PARK,dict(PARK,id=3)]}]
        output=io.StringIO()
        with patch.object(m,'fetch',side_effect=[catalog,ValueError('bad payload'),{'rides':[RIDE]}]), contextlib.redirect_stdout(output):
            m.collect('queue_times://test',{'park_ids':'2,3'})
        events=ET.fromstring('<stream>'+output.getvalue()+'</stream>')
        self.assertEqual(len(events),3)
        self.assertIn('error',events[0].findtext('data'))
        self.assertEqual(events[1].findtext('sourcetype'),'queue_times:ride')

    def test_all_parks_discovery(self):
        catalog=[{'name':'Group','parks':[PARK,dict(PARK,id=3)]}]
        output=io.StringIO()
        with patch.object(m,'fetch',side_effect=[catalog,{'rides':[RIDE]},{'rides':[RIDE]}]) as fetch, contextlib.redirect_stdout(output):
            m.collect('queue_times://test',{'park_ids':'*'})
        self.assertEqual(fetch.call_args_list[1].args[0],'/parks/2/queue_times.json')
        self.assertEqual(fetch.call_args_list[2].args[0],'/parks/3/queue_times.json')
        self.assertEqual(len(ET.fromstring('<stream>'+output.getvalue()+'</stream>')),4)

    def test_excluded_parks(self):
        with self.assertRaises(ValueError): m.validate({'park_ids':'*','exclude_park_ids':'*'})
        catalog=[{'name':'Group','parks':[PARK,dict(PARK,id=3)]}]
        output=io.StringIO()
        with patch.object(m,'fetch',side_effect=[catalog,{'rides':[RIDE]}]) as fetch, contextlib.redirect_stdout(output):
            m.collect('queue_times://test',{'park_ids':'*','exclude_park_ids':'2'})
        self.assertEqual(fetch.call_count,2)
        self.assertEqual(fetch.call_args_list[1].args[0],'/parks/3/queue_times.json')

    def test_catalog_failure_emits_health(self):
        output=io.StringIO()
        with patch.object(m,'fetch',side_effect=TimeoutError('timeout')),contextlib.redirect_stdout(output):
            m.collect('queue_times://test',{'park_ids':'2'})
        self.assertIn('catalog',ET.fromstring(output.getvalue()).findtext('data'))

    def test_park_local_time_and_dst_day_end(self):
        from datetime import datetime, timezone
        observed=datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc).timestamp()
        event=next(m.normalize({'rides':[RIDE]},dict(PARK,timezone='America/New_York'),'Group',observed))
        self.assertEqual(event['park_local_hour'],'01')
        self.assertEqual(event['park_local_date'],'2026-11-01')
        self.assertEqual(event['park_local_time'],'2026-11-01T01:30:00-04:00')
        self.assertEqual(event['park_day_end'],datetime(2026,11,2,5,tzinfo=timezone.utc).timestamp())

    def test_xml_files_and_scheme(self):
        for path in Path('queue_times/default/data/ui').rglob('*.xml'): ET.parse(path)
        self.assertEqual(ET.fromstring(m.scheme()).findtext('streaming_mode'),'xml')

if __name__=='__main__': unittest.main()
