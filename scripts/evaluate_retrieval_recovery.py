import json, subprocess
from pathlib import Path
root=Path('examples/retrieval-recovery');root.mkdir(parents=True,exist_ok=True)
held=json.loads(Path('examples/retrieval-holdout.json').read_text())
rows=[]
for c in held['cases']:
 if c['current']['all_required_recalled']:continue
 p=subprocess.run(['python3','-m','enterprise_qa','ask','--provider','deepseek','--question',c['query'],'--dataset','data/'+c['dataset']+'.json','--output-dir',str(root/'runs')],capture_output=True,text=True)
 r=json.loads(p.stdout)
 trace=[json.loads(l) for l in (root/'runs'/r['trace_id']/'trace.jsonl').read_text().splitlines()]
 reads={e.get('result',{}).get('doc_id') for e in trace if e.get('tool')=='read_passage' and e.get('result',{}).get('ok')}
 rows.append(dict(case=c['id'],question=c['query'],status=r['status'],trace_id=r['trace_id'],required=c['relevant'],recovered=set(c['relevant'])<=reads))
 (root/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows[-1]),flush=True)
