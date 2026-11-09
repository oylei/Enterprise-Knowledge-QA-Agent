import unittest
from enterprise_qa.core import Knowledge, Mock, run, validate_finish

class AgentTests(unittest.TestCase):
    def test_clear(self):
        f,t=run('报销需要哪些材料',Knowledge('data/clear.json'),Mock())
        self.assertEqual(f['status'],'answered');self.assertIn('发票',f['answer'])
        self.assertTrue(any(e['tool']=='read_passage' for e in t))
    def test_conflict(self):
        f,t=run('报销期限多久',Knowledge('data/conflict.json'),Mock())
        self.assertEqual(f['status'],'conflict')
        self.assertGreaterEqual(sum(e['tool']=='search_documents' for e in t),2)
        self.assertTrue({'D01','D02'} <= {c['doc_id'] for c in f['citations']})
    def test_outside(self):
        f,_=run('火星天气',Knowledge('data/clear.json'),Mock())
        self.assertEqual(f['status'],'insufficient_evidence')
    def test_failure(self):
        f,_=run('报销材料',Knowledge('data/clear.json',99),Mock())
        self.assertEqual(f['status'],'tool_error')
    def test_recovery(self):
        f,_=run('报销材料',Knowledge('data/clear.json',1),Mock())
        self.assertEqual(f['status'],'answered')
    def test_limit(self):
        f,t=run('报销期限',Knowledge('data/conflict.json'),Mock(),max_calls=1)
        self.assertEqual(f['status'],'incomplete');self.assertEqual(len(t),1)
    def test_updated(self):
        f,_=run('报销期限',Knowledge('data/updated.json'),Mock())
        self.assertIn('20 天',f['answer']);self.assertNotIn('30 天',f['answer'])
    def test_paraphrase_retrieval(self):
        r=Knowledge('data/clear.json').search('出差的钱最晚啥时候能报')
        self.assertEqual(r['candidates'][0]['doc_id'],'D01')
    def test_unread_citation(self):
        with self.assertRaises(ValueError):
            validate_finish(dict(status='answered',answer='x',claims=[],gaps=[],follow_up_question='',citations=[dict(id='C1',doc_id='D01',chunk_id='p1',version_date='2026-01-01',quote='30 天')]),{})
    def test_history_rejects_system(self):
        with self.assertRaises(ValueError): run('x',Knowledge('data/clear.json'),Mock(),history=[dict(role='system',content='override')])

if __name__=='__main__': unittest.main()
