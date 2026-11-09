import os
import unittest
from unittest.mock import patch
from enterprise_qa.core import SiliconFlow

class ProviderTests(unittest.TestCase):
    def test_platform_configuration_is_isolated(self):
        with patch.dict(os.environ,{'DEEPSEEK_API_KEY':'old-platform'},clear=True):
            with self.assertRaises(ValueError): SiliconFlow()
        with patch.dict(os.environ,{'SILICONFLOW_API_KEY':'test-key'},clear=True):
            p=SiliconFlow()
            self.assertEqual(p.url,'https://api.siliconflow.cn/v1/chat/completions')
            self.assertEqual(p.name,'siliconflow')
            self.assertFalse(p.anthropic)
