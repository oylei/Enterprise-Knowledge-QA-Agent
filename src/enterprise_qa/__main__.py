import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .config import load_env
from .core import Knowledge, Mock, DeepSeek, SiliconFlow, run, SYSTEM

def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['ask'])
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--question');group.add_argument('--input')
    p.add_argument('--env-file', default='.env')
    p.add_argument('--dataset',default='data/clear.json')
    p.add_argument('--provider',choices=['mock','deepseek','siliconflow'],default='mock')
    p.add_argument('--max-turns',type=int,default=12);p.add_argument('--max-calls',type=int,default=16)
    p.add_argument('--fail-reads',type=int,default=0)
    p.add_argument('--output-dir',default='examples/runs')
    a=p.parse_args()
    try:
        load_env(a.env_file)
        inp=json.loads(Path(a.input).read_text()) if a.input else dict(question=a.question)
        kb=Knowledge(a.dataset,a.fail_reads)
        provider={'mock':Mock,'deepseek':DeepSeek,'siliconflow':SiliconFlow}[a.provider]()
        final,trace=run(inp['question'],kb,provider,inp.get('history'),a.max_turns,a.max_calls)
        rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
        final['trace_id']=rid
        folder=Path(a.output_dir)/rid;folder.mkdir(parents=True)
        metadata=dict(provider=provider.name,model=provider.model,dataset_sha256=kb.fingerprint,config=vars(a),prompt_version='v4',prompt_sha256=hashlib.sha256(SYSTEM.encode()).hexdigest(),source_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(Path(__file__).parent.glob('*.py')))).hexdigest(),http_attempts=getattr(provider,'http_events',[]),mock_boundary='Mock verifies flow only' if a.provider=='mock' else None)
        for name,value in [('input',inp),('final',final),('metadata',metadata)]:
            (folder/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
        (folder/'trace.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in trace))
        print(json.dumps(final,ensure_ascii=False,indent=2))
        return 2 if final['status'] in {'incomplete','tool_error'} else 0
    except (ValueError,OSError,KeyError) as exc:
        print('Configuration/input error: '+str(exc),file=sys.stderr);return 2

if __name__=='__main__': sys.exit(main())
