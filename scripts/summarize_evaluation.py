import argparse
import json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('directory',nargs='?',default='examples/new-evaluation');a=p.parse_args();root=Path(a.directory)
rows=json.loads((root/'summary.json').read_text())
stability={}
for name in ['E01','E04','E12','E14','E19']:
 selected=[r for r in rows if r['case']==name or r['case'].startswith(name+'_repeat')]
 stability[name]=dict(runs=len(selected),mechanical_passes=sum(r['mechanical_pass'] for r in selected),statuses=[r.get('status') for r in selected])
result=dict(total_runs=len(rows),mechanical_passes=sum(r['mechanical_pass'] for r in rows),mechanical_failures=[r['case'] for r in rows if not r['mechanical_pass']],stability=stability,warning='Mechanical pass checks status and required read documents, not semantic correctness. See review.json.')
(root/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
