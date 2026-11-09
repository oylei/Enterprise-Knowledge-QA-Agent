import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from enterprise_qa.config import load_env
from enterprise_qa.core import Knowledge

class ConfigDataTests(unittest.TestCase):
    def test_literal_and_precedence(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'DEEPSEEK_MODEL':'shell-model'}, clear=True):
            p=Path(tmp)/'.env'
            p.write_text('# comment\nDEEPSEEK_MODEL=file-model\nDEEPSEEK_API_KEY="literal-$(no-execution)"\nUNRELATED=value\n')
            load_env(p)
            self.assertEqual(os.environ['DEEPSEEK_MODEL'],'shell-model')
            self.assertEqual(os.environ['DEEPSEEK_API_KEY'],'literal-$(no-execution)')
            self.assertNotIn('UNRELATED',os.environ)
    def test_error_does_not_disclose_value_or_partially_load(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            p=Path(tmp)/'.env';p.write_text('DEEPSEEK_MODEL=model\nDEEPSEEK_API_KEY="secret\n')
            with self.assertRaises(ValueError) as ctx: load_env(p)
            self.assertNotIn('secret',str(ctx.exception))
            self.assertNotIn('DEEPSEEK_MODEL',os.environ)
    def test_all_datasets_and_case_references(self):
        for path in Path('data').glob('*.json'):
            kb=Knowledge(path)
            for d in kb.docs:
                self.assertRegex(d['version_date'],r'^\d{4}-\d{2}-\d{2}$')
                self.assertTrue(d['chunks'])
        cases=json.loads(Path('examples/evaluation-cases.json').read_text())
        self.assertEqual(len({c['id'] for c in cases}),len(cases))
        for c in cases:
            ids={d['doc_id'] for d in Knowledge(c['dataset']).docs}
            self.assertTrue(set(c['required_doc_ids']) <= ids)
    def test_rich_retrieval_retains_both_conflicting_documents(self):
        results=Knowledge('data/rich_conflict.json').search('报销期限多久',5)['candidates']
        self.assertTrue({'D01','D02'} <= {r['doc_id'] for r in results})
    def test_same_date_non_numeric_conflict(self):
        results=Knowledge('data/same_date_conflict.json').search('出租车费用报销')['candidates']
        self.assertEqual({r['doc_id'] for r in results},{'D30','D31'})
