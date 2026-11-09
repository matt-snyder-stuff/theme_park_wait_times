"""Guard user-flow and release regressions without claiming browser rendering QA."""
import unittest
import xml.etree.ElementTree as E
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class ReleaseStructure(unittest.TestCase):
    def test_trip_lookups_follow_current_form(self):
        r=E.parse(ROOT/'queue_times/default/data/ui/views/trip_builder.xml')
        for ride,park in [('morning_rides','morning'),('afternoon_rides','afternoon')]:
            q=r.findtext('.//input[@token="'+ride+'"]/search/query')
            self.assertIn('$form.'+park+'|s$',q)
        for search in r.findall('.//table/search'):
            self.assertEqual(search.findtext('earliest'),'-60d')
        self.assertIsNotNone(r.find('.//div[@id="trip-summary"]'))

    def test_view_assets_and_navigation(self):
        root=ROOT/'queue_times/default/data/ui'
        views={p.stem for p in (root/'views').glob('*.xml')}
        for p in (root/'views').glob('*.xml'):
            r=E.parse(p).getroot()
            for attr in ['script','stylesheet']:
                for name in r.get(attr,'').split(','):
                    if name:self.assertTrue((ROOT/'queue_times/appserver/static'/name).is_file(),name)
        names=[v.get('name') for v in E.parse(root/'nav/default.xml').findall('.//view')]
        self.assertEqual(len(names),len(set(names)))
        self.assertTrue(set(names)<=views|{'search'})

    def test_readme_pictures_exist(self):
        import re
        text=(ROOT/'README.md').read_text()
        for path in re.findall(r'!\[[^\]]*\]\((docs/images/[^)]+)\)',text):
            self.assertTrue((ROOT/path).is_file(),path)
