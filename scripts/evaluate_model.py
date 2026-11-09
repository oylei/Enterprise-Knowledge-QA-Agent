"""Real-model evaluation. Run from root with PYTHONPATH=src.
Results are observations; automatic checks do not replace semantic review.
"""
import argparse
import json
import subprocess
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--provider',default='deepseek',choices=['deepseek','siliconflow']);parser.add_argument('--output',default='examples/new-evaluation');args=parser.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    cases=json.loads(Path('examples/评估用例定义_18个场景.json').read_text())
    for c in cases:
        c['accepted_statuses']=[c['expected_status']]
        if c['id']=='E03':c['accepted_statuses']+=['needs_clarification']
        if c['id']=='E07':c['accepted_statuses']+=['partial']
    cases += [dict(id='E19',question='差旅报销需要哪些材料？',dataset='data/clear.json',accepted_statuses=['tool_error'],fail_reads=99),dict(id='E20',question='差旅报销期限是多少？',dataset='data/conflict.json',accepted_statuses=['incomplete'],max_calls=1)]
    # Identical question and prompt; only dataset changes.
    for name,ds,status in [('control30','clear','answered'),('control20','updated','answered'),('control_conflict','conflict','conflict')]:
        cases.append(dict(id=name,question='差旅报销应在出差结束后多少天内提交？',dataset='data/'+ds+'.json',accepted_statuses=[status]))
    # Three total repetitions of selected core scenarios.
    for repeat in [2,3]:
        for original in ['E01','E04','E12','E14','E19']:
            c=dict(next(c for c in cases if c['id']==original));c['id']=original+'_repeat'+str(repeat);cases.append(c)
    rows=[]
    existing=output/'summary.json'
    if existing.exists(): rows=json.loads(existing.read_text())
    for c in cases:
        if any(r['case']==c['id'] for r in rows):continue
        inp=output/(c['id']+'-input.json');inp.write_text(json.dumps({k:c[k] for k in ['question','history'] if k in c},ensure_ascii=False,indent=2))
        cmd=['python3','-m','enterprise_qa','ask','--provider',args.provider,'--input',str(inp),'--dataset',c['dataset'],'--output-dir',str(output/'runs')]
        for key in ['fail_reads','max_calls']:
            if key in c:cmd+=['--'+key.replace('_','-'),str(c[key])]
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=900)
            result=json.loads(p.stdout)
            run_dir=output/'runs'/result['trace_id']
            trace=[json.loads(l) for l in (run_dir/'trace.jsonl').read_text().splitlines()]
            read_ids={e.get('result',{}).get('doc_id') for e in trace if e.get('tool')=='read_passage' and e.get('result',{}).get('ok')}
            checks=dict(status=result['status'] in c['accepted_statuses'],required_documents=set(c.get('required_doc_ids',[]))<=read_ids)
            if c['id']=='E20': checks['budget']=result['stop_reason']=='budget_exhausted' and len([e for e in trace if 'step' in e])<=1
            row=dict(case=c['id'],accepted_statuses=c['accepted_statuses'],status=result['status'],trace_id=result['trace_id'],checks=checks,mechanical_pass=all(checks.values()))
        except (subprocess.TimeoutExpired,ValueError,KeyError) as exc:row=dict(case=c['id'],error=type(exc).__name__,mechanical_pass=False)
        rows.append(row);existing.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(row),flush=True)

if __name__=='__main__':main()
