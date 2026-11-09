"""Deterministic small-set retrieval comparison; not model-answer evaluation.
Run: PYTHONPATH=src python3 scripts/evaluate_retrieval.py
"""
import json
import re
from pathlib import Path
from enterprise_qa.core import Knowledge

CASES = [
 ('报销期限多久', 'data/rich_conflict.json', ['D01','D02']),
 ('出差的钱最晚啥时候能报', 'data/rich_conflict.json', ['D01','D02']),
 ('住宿限额', 'data/scoped.json', ['D10','D11','D12']),
 ('出租车费用报销', 'data/same_date_conflict.json', ['D30','D31']),
 ('审批通过后多久能到账', 'data/rich.json', ['D13']),
 ('差旅预借款归还', 'data/rich.json', ['D19']),
 ('机票报销材料', 'data/partial.json', ['D40']),
 ('上下班通勤', 'data/rich.json', ['D17']),
]

def raw_features(text):
    text=''.join(re.findall(r'[\w]',text.lower()))
    return set(text[i:i+2] for i in range(len(text)-1))

def baseline(kb, query):
    q=raw_features(query)
    ranked=[]
    for d in kb.docs:
        score=len(q & raw_features(d['title']))*2 + max(len(q & raw_features(t)) for t in d['chunks'].values())
        if score:ranked.append((score,d['doc_id']))
    return [i for _,i in sorted(ranked,key=lambda x:(-x[0],x[1]))[:5]]

def main():
    rows=[]
    for query,dataset,relevant in CASES:
        kb=Knowledge(dataset)
        row=dict(query=query,dataset=dataset,relevant=relevant)
        for name,ids in [('baseline',baseline(kb,query)),('current',[c['doc_id'] for c in kb.search(query,5)['candidates']])]:
            row[name]=dict(ids=ids,recall_at_5=len(set(ids)&set(relevant))/len(relevant),all_required_recalled=set(relevant)<=set(ids))
        rows.append(row)
    summary={name:dict(mean_recall_at_5=sum(r[name]['recall_at_5'] for r in rows)/len(rows),all_required_rate=sum(r[name]['all_required_recalled'] for r in rows)/len(rows)) for name in ['baseline','current']}
    result=dict(sample_size=len(rows),boundary='Small development set, not held-out; baseline differs only by synonym normalization. Not evidence of generalization or answer correctness.',summary=summary,cases=rows)
    Path('examples/retrieval-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
