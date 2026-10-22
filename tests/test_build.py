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
  readme=b.outputs(self.summary())['README.md'];self.assertEqual(readme.count('<a href='),5);self.assertIn('prefers-color-scheme: dark',readme)
 def test_pagination(self):
  calls=[]
  def fetch(url,token):calls.append(url);return json.dumps([{}]*100 if len(calls)==1 else [{}])
  self.assertEqual(len(b.pages('/x',fetch=fetch)),101);self.assertIn('page=2',calls[1])
 def test_bad_collection(self):self.assertRaises(ValueError,b.pages,'/x',fetch=lambda *args:'{}')
 def test_write(self):
  with tempfile.TemporaryDirectory() as d:
   b.write_all({'x/test':'good'},Path(d));self.assertEqual((Path(d)/'x/test').read_text(),'good')
 def test_no_placeholders(self):self.assertNotIn('Illustrative',str(b.outputs(self.summary())))
if __name__=='__main__':unittest.main()
