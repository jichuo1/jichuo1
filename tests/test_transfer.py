import copy,json,unittest
from test_build import b

class TestTransferredRepository(unittest.TestCase):
 def setUp(self):
  self.source=json.loads((b.ROOT/'source.json').read_text())
  for i,r in enumerate(self.source['repos']):r.setdefault('id',i+1)
  self.lce=next(r for r in self.source['repos'] if r['name']=='LumenCoacervationEngine')
  self.repos={r['full_name']:r for r in self.source['repos']}
 def fetch(self,url,token):
  if '/users/' in url:return json.dumps([r for r in self.source['repos'] if r['full_name'].startswith('jichuo1/')])
  return json.dumps(self.repos[url.split('/repos/')[1]])
 def test_transfer_included_once(self):
  rows=b.collect_repositories(fetch=self.fetch)
  self.assertEqual(len(rows),7)
  self.assertEqual(sum(r['id']==1391143536 for r in rows),1)
  self.source['repos']=rows
  self.assertEqual(b.summarize(self.source,[])['stars'],sum(r['stargazers_count'] for r in rows))
 def test_same_id_alias_deduplicated(self):
  alias=dict(self.lce,full_name='jichuo1/LumenCoacervationEngine')
  self.source['repos'].append(alias)
  rows=b.collect_repositories(fetch=self.fetch)
  self.assertEqual(len(rows),7)
  self.assertEqual(sum(r['id']==1391143536 for r in rows),1)
 def test_wrong_external_identity_rejected(self):
  self.lce['id']=123
  self.assertRaises(ValueError,b.collect_repositories,fetch=self.fetch)
 def test_unlisted_org_rejected(self):
  self.source['repos'].append(dict(self.lce,id=123,full_name='other/LumenCoacervationEngine'))
  self.assertRaises(ValueError,b.summarize,self.source,[])
 def test_private_featured_rejected(self):
  self.lce['private']=True
  self.assertRaises(ValueError,b.collect_repositories,fetch=self.fetch)
 def test_duplicate_identity_rejected(self):
  self.source['repos'].append(dict(self.source['repos'][0],name='alias',full_name='jichuo1/alias'))
  self.assertRaises(ValueError,b.summarize,self.source,[])
 def test_canonical_project_link(self):
  out=b.outputs(b.summarize(self.source,b.calendar((b.ROOT/'contributions-source.html').read_text())))
  self.assertIn('https://github.com/Meguvizarchic/LumenCoacervationEngine',out['README.md'])
