#!/usr/bin/env python3
"""Queue-Times Splunk modular input. Python standard library only."""
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

BASE = 'https://queue-times.com'


def fetch(path):
    request = urllib.request.Request(BASE + path, headers={'User-Agent': 'Splunk-Queue-Times/1.0', 'Accept': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def validate(params):
    value = params.get('park_ids', '').strip()
    if value != '*' and (not value or any(not p.strip().isdigit() or int(p) <= 0 for p in value.split(','))):
        raise ValueError('park_ids must be * (all parks) or a comma-separated list of positive park IDs.')
    if int(params.get('interval', '300')) < 300:
        raise ValueError('interval must be at least 300 seconds.')
    excluded = params.get('exclude_park_ids', '').strip()
    if excluded and any(not p.strip().isdigit() or int(p) <= 0 for p in excluded.split(',')):
        raise ValueError('exclude_park_ids must be comma-separated positive park IDs.')
    return None if value == '*' else sorted(set(int(p.strip()) for p in value.split(',')))


def normalize(payload, park, group, observed):
    local = datetime.fromtimestamp(observed, ZoneInfo(park.get('timezone') or 'UTC'))
    common = dict(park_local_date=local.strftime('%Y-%m-%d'),
                  park_local_hour=local.strftime('%H'),
                  park_local_time=local.isoformat(),
                  park_day_end=datetime.combine(local.date() + timedelta(days=1), datetime.min.time(), local.tzinfo).timestamp(),
                  park_id=park['id'], park_name=park['name'], group_name=group,
                  country=park.get('country'), continent=park.get('continent'),
                  latitude=park.get('latitude'), longitude=park.get('longitude'),
                  park_timezone=park.get('timezone'), observed_at=observed)
    seen = set()
    containers = [(land.get('id'), land.get('name'), land.get('rides', [])) for land in payload.get('lands', [])]
    containers.append((None, 'Other rides', payload.get('rides', [])))
    for land_id, land_name, rides in containers:
        for ride in rides:
            if ride['id'] in seen:
                continue
            seen.add(ride['id'])
            yield dict(common, land_id=land_id, land_name=land_name, ride_id=ride['id'],
                       ride_name=ride['name'], is_open=ride['is_open'],
                       wait_time=ride['wait_time'], last_updated=ride.get('last_updated'))


def emit(stanza, index, sourcetype, data, observed):
    event = ET.Element('event', {'stanza': stanza})
    for name, value in [('time', observed), ('index', index), ('source', 'queue-times.com'),
                        ('sourcetype', sourcetype), ('data', json.dumps(data, separators=(',', ':')))]:
        ET.SubElement(event, name).text = str(value)
    sys.stdout.write(ET.tostring(event, encoding='unicode'))
    sys.stdout.flush()


def collect(stanza, params):
    ids = validate(params)
    index = params.get('index', 'queue_times')
    started = time.time()
    try:
        parks = {p['id']: (p, g['name']) for g in fetch('/parks.json') for p in g['parks']}
    except Exception as exc:
        emit(stanza, index, 'queue_times:health', dict(status='error', stage='catalog', error=str(exc)), time.time())
        return
    excluded = {int(p.strip()) for p in params.get('exclude_park_ids', '').split(',') if p.strip()}
    for park_id in sorted(parks) if ids is None else ids:
        if park_id in excluded:
            continue
        start = time.time()
        try:
            park, group = parks[park_id]
            payload = fetch('/parks/{}/queue_times.json'.format(park_id))
            observed = time.time()
            events = list(normalize(payload, park, group, observed))
            for event in events:
                event['poll_interval_seconds'] = int(params.get('interval', '300'))
                emit(stanza, index, 'queue_times:ride', event, observed)
            health = dict(status='ok', park_id=park_id, park_name=park['name'], ride_count=len(events))
        except Exception as exc:
            health = dict(status='error', park_id=park_id, error=str(exc))
        health.update(poll_interval_seconds=int(params.get('interval', '300')), duration_seconds=round(time.time() - start, 3), collection_started=started)
        emit(stanza, index, 'queue_times:health', health, time.time())


def scheme():
    root = ET.Element('scheme')
    for key, value in [('title', 'Queue-Times'), ('description', 'Collect live theme park ride snapshots.'),
                       ('use_external_validation', 'true'), ('use_single_instance', 'false'), ('streaming_mode', 'xml')]:
        ET.SubElement(root, key).text = value
    args = ET.SubElement(ET.SubElement(root, 'endpoint'), 'args')
    for name, title in [('name', 'Input name'), ('park_ids', 'Park IDs (* for all, or comma separated)'), ('exclude_park_ids', 'Excluded park IDs (optional)')]:
        arg = ET.SubElement(args, 'arg', {'name': name})
        for key, value in [('title', title), ('data_type', 'string'), ('required_on_create', 'false' if name == 'exclude_park_ids' else 'true')]:
            ET.SubElement(arg, key).text = value
    return ET.tostring(root, encoding='unicode')


def main():
    if '--scheme' in sys.argv:
        print(scheme())
        return
    root = ET.fromstring(sys.stdin.read())
    if '--validate-arguments' in sys.argv:
        try:
            validate({p.attrib['name']: p.text or '' for p in root.findall('./item/param')})
        except (ValueError, TypeError) as exc:
            error = ET.Element('error')
            ET.SubElement(error, 'message').text = str(exc)
            print(ET.tostring(error, encoding='unicode'))
            sys.exit(1)
        return
    sys.stdout.write('<stream>')
    try:
        for stanza in root.findall('./configuration/stanza'):
            collect(stanza.attrib['name'], {p.attrib['name']: p.text or '' for p in stanza.findall('param')})
    finally:
        sys.stdout.write('</stream>')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
