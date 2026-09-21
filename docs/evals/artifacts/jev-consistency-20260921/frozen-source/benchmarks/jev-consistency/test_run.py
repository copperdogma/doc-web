import copy,json,unittest
from pathlib import Path
import run
class Contracts(unittest.TestCase):
 def test_payload_excludes_gold(self):
  for c in json.loads(Path(__file__).with_name('fixtures.json').read_text()):
   for p in ('jev','gpt'):
    raw=json.dumps(run.payload(p,c['input']))
    self.assertNotIn('rationale',raw);self.assertNotIn('"gold"',raw)
 def test_jev_contract_rejects_bad_probability_and_identity(self):
  raw={'model':'jev-1.13.0','usage':{'input_tokens':100,'output_tokens':20},'answers':{'status':{'type':'choice','choice':'conformant','confidence':1,'probabilities':dict.fromkeys(run.LABELS,0)}}}
  raw['answers']['status']['probabilities']['conformant']=1
  self.assertEqual(run.parse('jev',raw)[0],'conformant')
  for field,value in [('model','jev-latest'),('status','failed')]:
   bad=copy.deepcopy(raw);bad[field]=value
   with self.assertRaises(ValueError):run.parse('jev',bad)
  raw['answers']['status']['probabilities']['mixed']=.3
  with self.assertRaises(ValueError):run.parse('jev',raw)
 def test_gpt_truncation_rejected(self):
  raw={'model':run.MODEL,'usage':{'prompt_tokens':50,'completion_tokens':10},'choices':[{'finish_reason':'length','message':{'content':'{}'}}]}
  with self.assertRaises(ValueError):run.parse('gpt',raw)
 def test_macro_and_dangerous_misses(self):
  m=run.metrics([{'id':'a','gold':'mixed','label':'conformant','cost_usd':0,'latency_ms':0}])
  self.assertEqual(m['defects_called_clean'],1);self.assertEqual(m['accuracy'],0)
 def test_structural_baseline_frozen_failures(self):
  cs=json.loads(Path(__file__).with_name('fixtures.json').read_text())
  self.assertEqual(sum(run.deterministic(c['input'])==c['gold'] for c in cs),8)
if __name__=='__main__':unittest.main()
