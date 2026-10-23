import copy,importlib.util,json,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
spec=importlib.util.spec_from_file_location('build',Path(__file__).resolve().parents[1]/'scripts/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class TestProfile(unittest.TestCase):
 def setUp(self):
  self.source=json.loads((b.ROOT/'source.json').read_text());self.raw=(b.ROOT/'contributions-source.html').read_text();self.days=b.calendar(self.raw)
 def summary(self):return b.summarize(self.source,self.days)
 def test_live_fixture(self):
  s=self.summary();self.assertEqual(s['repos'],7);self.assertGreaterEqual(s['stars'],159);self.assertGreaterEqual(s['downloads'],3711)
 def test_stable_not_canary(self):
  self.source['releases']['Bilibili_Innocent_Lab'].append({'id':999999999,'draft':False,'prerelease':True,'published_at':'2099-01-01','tag_name':'Canary999','assets':[]})
  self.assertEqual(self.summary()['projects'][0]['version'],'v1.2.1')
 def test_draft_download_excluded(self):
  before=self.summary()['downloads'];self.source['releases']['Bilibili_Innocent_Lab'].append({'id':999999999,'draft':True,'prerelease':False,'published_at':'2099-01-01','tag_name':'v999','assets':[{'download_count':99999}]})
  self.assertEqual(self.summary()['downloads'],before)
 def test_private_excluded(self):
  r=copy.deepcopy(self.source['repos'][0]);r.update(name='private',full_name='jichuo1/private',private=True,stargazers_count=999999);self.source['repos'].append(r);self.assertEqual(self.summary()['repos'],7)
 def test_duplicate_repo(self):
  self.source['repos'].append(self.source['repos'][0]);self.assertRaises(ValueError,self.summary)
 def test_duplicate_release(self):
  r=self.source['releases']['Bilibili_Innocent_Lab'];r.append(r[0]);self.assertRaises(ValueError,self.summary)
 def test_negative_count(self):
  self.source['repos'][0]['stargazers_count']=-1;self.assertRaises(ValueError,self.summary)
 def test_missing_featured(self):
  self.source['repos']=[r for r in self.source['repos'] if r['name']!='Bilibili_Innocent_Lab'];self.assertRaises(KeyError,self.summary)
 def test_other_owner(self):
  self.source['repos'][0]['full_name']='other/foo';self.assertRaises(ValueError,self.summary)
 def test_calendar_no_dummy(self):
  self.assertTrue(any(level>0 for _,level in self.days));self.assertGreater(len(self.days),350)
 def test_calendar_empty_rejected(self):self.assertRaises(ValueError,b.calendar,'<html>sign in</html>')
 def test_calendar_duplicate(self):self.assertRaises(ValueError,b.calendar,self.raw+self.raw)
 def test_xml_every_asset(self):
  for dark in (False,True):
   for value in {**b.render(self.summary(),dark),**{k+"-mobile":v for k,v in b.mobile_render(self.summary(),dark).items()}}.values():ET.fromstring(value)
 def test_xml_escape(self):self.assertIn('&lt;',b.text(0,0,'<a & b>'))
 def test_language_counts(self):self.assertEqual(sum(self.summary()['languages'].values()),7)
 def test_fork_included(self):self.assertEqual(len([r for r in self.source['repos'] if r['fork']]),2)
 def test_clickable(self):
  readme=b.outputs(self.summary())['README.md'];self.assertEqual(readme.count('<a href='),6);self.assertIn('prefers-color-scheme: dark',readme)
 def test_pagination(self):
  calls=[]
  def fetch(url,token):calls.append(url);return json.dumps([{}]*100 if len(calls)==1 else [{}])
  self.assertEqual(len(b.pages('/x',fetch=fetch)),101);self.assertIn('page=2',calls[1])
 def test_bad_collection(self):self.assertRaises(ValueError,b.pages,'/x',fetch=lambda *args:'{}')
 def test_write(self):
  with tempfile.TemporaryDirectory() as d:
   b.write_all({'x/test':'good'},Path(d));self.assertEqual((Path(d)/'x/test').read_text(),'good')
 def test_no_placeholders(self):self.assertNotIn('Illustrative',str(b.outputs(self.summary())))


class TestOriginalDecorations(unittest.TestCase):
    def test_ornaments_safe_and_accessible(self):
        for dark in (False, True):
            for mobile in (False, True):
                for kind in ('cat', 'orbit'):
                    art = b.ornaments(kind, dark, mobile)
                    self.assertIn('prefers-reduced-motion:reduce', art)
                    self.assertNotIn('<script', art)
                    self.assertNotIn('href=', art)
                    self.assertIn('@keyframes', art)

class TestDataOrnaments(unittest.TestCase):
    def test_data_bindings(self):
        self.assertNotEqual(b.data_ornament('stars',49,0,0),b.data_ornament('stars',50,0,0))
        self.assertNotEqual(b.data_ornament('repos',8,0,0),b.data_ornament('repos',9,0,0))
        self.assertIn('toward next 1000',b.data_ornament('downloads',3746,0,0))
        self.assertEqual(b.calendar_companion([('2026-10-22',0)]),'')
        self.assertIn('2026-10-21',b.calendar_companion([('2026-10-21',3),('2026-10-22',0)]))
    def test_deterministic(self):
        self.assertEqual(b.data_ornament('stars',160,1,2),b.data_ornament('stars',160,1,2))



class TestProjectScenes(unittest.TestCase):
    def test_zero_interest(self):
        self.assertIn('width="0.000"',b.project_scene('GlobalTokenTracker',0,132))
        self.assertIn('not recent traffic or trend',b.project_scene('GlobalTokenTracker',0,0))
    def test_proportional_interest(self):
        self.assertIn('width="30.000"',b.project_scene('LumenCoacervationEngine',5,10))
        self.assertIn('prefers-reduced-motion',b.project_scene('SplashScreenAdvanced',23,132))

class TestNaturalMotion(unittest.TestCase):
    def test_sun_arc(self):
        art=b.project_scene('SplashScreenAdvanced',23,132)
        self.assertIn('rotate(180deg)',art)
        self.assertIn('class="sun-arc"',art)
        self.assertIn('animation:none',art)
    def test_vector_letters_and_motto(self):
        self.assertIn('pixel-type',b.text(0,30,'Projects'))
        self.assertIn('<text',b.text(0,30,'Many begin well;',extra='font-style="italic"'))
        self.assertIn('aria-label="160"',b.text(0,30,160))

class TestGustPoster(unittest.TestCase):
    def test_shared_clock_and_reduced_motion(self):
        source=Path(b.__file__).read_text()
        self.assertIn('paper-gust 7.1s',source)
        self.assertIn('paper-flutter 2.31s',source)
        self.assertIn('.poster-sheet,.poster-flutter,.poster-curl,.paper-shadow{animation:none}',source)
    def test_detailed_scene_geometry(self):
        for name in b.FEATURED:
            art=b.project_scene(name,1,1)
            self.assertIn('cubic-bezier',art)
            self.assertNotIn('<script',art)

class TestIntroReels(unittest.TestCase):
    def test_reels_once_and_accessible(self):
        art=b.text(0,30,160)
        self.assertIn('reel-column',art)
        self.assertIn('1 both',art)
        self.assertIn('aria-label="160"',art)
        self.assertNotIn('infinite',art)
    def test_motto_never_rolls(self):
        self.assertNotIn('reel',b.text(0,30,'Motto',extra='font-style="italic"'))

class TestEntrances(unittest.TestCase):
    def test_wrapped_without_changing_data(self):
        art=b.entrance_pass(b.svg(100,'<rect x="10" y="10" width="12" height="12"/>'),'contributions')
        self.assertIn('enter-cell',art)
        self.assertIn('prefers-reduced-motion',art)
        self.assertIn('width="12"',art)
    def test_motto_not_wrapped(self):
        art=b.entrance_pass(b.svg(100,b.text(20,40,'Motto',extra='font-style="italic"')),'header')
        self.assertNotIn('class="entrance"',art)

if __name__=='__main__':unittest.main()
