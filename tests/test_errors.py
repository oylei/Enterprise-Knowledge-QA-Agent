import io
import json
import unittest
import urllib.error
from unittest.mock import patch
from enterprise_qa.core import Knowledge,run,request_json,ModelError,classify_error,validate_schema,TOOLS,DeepSeek

class Script:
    def __init__(self, messages): self.messages=iter(messages)
    def next(self, history): return next(self.messages)
def call(name,args,ident='1'):
    return dict(id=ident,function=dict(name=name,arguments=json.dumps(args)))
def message(*calls):return dict(role='assistant',tool_calls=list(calls))

class ErrorTests(unittest.TestCase):
    def run_script(self,*messages,max_calls=16):return run('报销材料',Knowledge('data/clear.json'),Script(messages),max_calls=max_calls)
    def test_invalid_protocol(self):
        for m in [None,[],{},message({'id':1}),message(call('x',{},'a'),call('x',{},'a'))]:
            with self.subTest(m=m):
                f,t=self.run_script(m);self.assertEqual(f['stop_reason'],'model_protocol_error')
    def test_batch_cannot_exceed_budget(self):
        f,t=self.run_script(message(call('search_documents',dict(query='期限',reason='test'),'1'),call('search_documents',dict(query='材料',reason='test'),'2')),max_calls=1)
        self.assertEqual(len(t),1);self.assertEqual(f['status'],'incomplete')
    def test_unknown_extra_and_nested_parameters(self):
        for c in [call('shell',{'reason':'x'}),call('search_documents',dict(query='期限',reason='x',extra=True)),call('read_passage',dict(doc_id=[],chunk_id='p1',reason='x'))]:
            f,t=self.run_script(message(c),max_calls=1);self.assertEqual(t[0]['result']['code'],'INVALID_ACTION')
        schema=TOOLS[-1]['function']['parameters']
        with self.assertRaises(ValueError):validate_schema({'status':'answered','answer':'x','claims':[3],'citations':[],'gaps':[],'follow_up_question':'','reason':'x'},schema)
    def test_invalid_json(self):
        c=call('search_documents',{});c['function']['arguments']='{'
        f,t=self.run_script(message(c),max_calls=1);self.assertEqual(t[0]['result']['code'],'INVALID_ACTION')
    def test_tool_exception_is_observation(self):
        with patch.object(Knowledge,'read',side_effect=RuntimeError('private token')):
            f,t=self.run_script(message(call('read_passage',dict(doc_id='D01',chunk_id='p1',reason='x'))),max_calls=1)
        self.assertEqual(t[0]['result']['code'],'TOOL_EXCEPTION');self.assertNotIn('private',json.dumps(t))
    def test_transient_http_retries_once(self):
        p=Script([])
        with patch('urllib.request.urlopen',side_effect=[urllib.error.HTTPError('url',429,'secret',{},None),io.BytesIO(b'{"ok":true}')]),patch('time.sleep'):
            self.assertEqual(request_json(p,None),{'ok':True})
        self.assertEqual(len(p.http_events),2)
    def test_permanent_http_does_not_retry(self):
        for status,category in [(401,'authentication'),(402,'insufficient_balance'),(403,'permission')]:
            p=Script([])
            with patch('urllib.request.urlopen',side_effect=urllib.error.HTTPError('url',status,'secret',{},None)) as mock:
                with self.assertRaises(ModelError) as ctx:request_json(p,None)
                self.assertEqual(ctx.exception.category,category);self.assertEqual(mock.call_count,1)
                self.assertNotIn('secret',json.dumps(p.http_events))
    def test_timeout_bounded(self):
        with patch('urllib.request.urlopen',side_effect=TimeoutError()),patch('time.sleep'):
            p=Script([])
            with self.assertRaises(ModelError):request_json(p,None)
            self.assertEqual(len(p.http_events),2)
    def test_malformed_api_json(self):
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'not-json')):
            with self.assertRaises(ModelError) as ctx:request_json(Script([]),None)
            self.assertEqual(ctx.exception.category,'protocol')
    def test_model_error_record_is_sanitized(self):
        p=Script([])
        with patch.object(p,'next',side_effect=ModelError('insufficient_balance',402)):
            f,t=run('x',Knowledge('data/clear.json'),p)
        self.assertEqual(t[0]['http_status'],402);self.assertEqual(f['status'],'incomplete')
    def test_history_and_fault_inputs(self):
        with self.assertRaises(ValueError):run('x',Knowledge('data/clear.json'),Script([]),history=[1])
        with self.assertRaises(ValueError):Knowledge('data/clear.json',-1)

if __name__=='__main__':unittest.main()

class AdapterTests(unittest.TestCase):
    def make_provider(self,anthropic=False):
        p=DeepSeek.__new__(DeepSeek);p.key='test';p.model='test';p.url='https://example.invalid/api';p.anthropic=anthropic;return p
    def test_chat_truncated_response(self):
        with patch('enterprise_qa.core.request_json',return_value={'choices':[{'finish_reason':'length','message':{}}]}):
            with self.assertRaises(ValueError):self.make_provider().next([{'role':'user','content':'x'}])
    def test_chat_roundtrip_tool_result(self):
        m=message(call('read_passage',dict(doc_id='D01',chunk_id='p1',reason='x')))
        with patch('enterprise_qa.core.request_json',return_value={'choices':[{'finish_reason':'tool_calls','message':m}]}) as request:
            result=self.make_provider().next([{'role':'user','content':'x'}])
        self.assertEqual(result,m)
        body=json.loads(request.call_args.args[1].data);self.assertIn('tools',body)
    def test_anthropic_multiple_results_grouped(self):
        messages=[{'role':'system','content':'rules'},{'role':'user','content':'x'},message(call('read_passage',{},'a'),call('read_passage',{},'b')),{'role':'tool','tool_call_id':'a','content':'{}'},{'role':'tool','tool_call_id':'b','content':'{}'}]
        response={'stop_reason':'tool_use','content':[{'type':'tool_use','id':'c','name':'search_documents','input':{'query':'x','reason':'x'}}]}
        with patch('enterprise_qa.core.request_json',return_value=response) as request:
            result=self.make_provider(True).next(messages)
        body=json.loads(request.call_args.args[1].data)
        self.assertEqual([c['tool_use_id'] for c in body['messages'][-1]['content']],['a','b'])
        self.assertEqual(result['tool_calls'][0]['id'],'c')
        self.assertEqual(body['thinking']['type'],'disabled')
