"""Independent new queries, frozen retrieval implementation; no tuning on results.
This is author-created holdout data, not an external benchmark.
"""
import json
from pathlib import Path
from enterprise_qa.core import Knowledge
from evaluate_retrieval import baseline

CASES=[
 ('H01','酒店一晚上花六百可以全额报吗','rich',['D10']),
 ('H02','去国外住宾馆的费用上限','rich',['D11']),
 ('H03','财务审核完打款要等几个工作日','rich',['D13']),
 ('H04','餐饮补贴报账要不要票据','rich',['D14']),
 ('H05','住宿的票找不着了怎么补','rich',['D15']),
 ('H06','报销五千以上由谁批准','rich',['D16']),
 ('H07','每天从家到办公室的路费能算出差吗','rich',['D17']),
 ('H08','坐动车二等座能报账不','rich',['D18']),
 ('H09','出差借支结清的截止时间','rich',['D19']),
 ('H10','报账申请应该在差旅结束几天内交','rich_conflict',['D01','D02']),
 ('H11','公务出行乘出租车费用怎么处理','same_date_conflict',['D30','D31']),
 ('H12','旧住宿标准与六月生效的新规','superseded',['D20','D21']),
]
rows=[]
for ident,q,ds,relevant in CASES:
 kb=Knowledge('data/'+ds+'.json');row=dict(id=ident,query=q,dataset=ds,relevant=relevant)
 for name,ids in [('baseline',baseline(kb,q)),('current',[c['doc_id'] for c in kb.search(q,5)['candidates']])]:
  row[name]=dict(ids=ids,recall_at_5=len(set(ids)&set(relevant))/len(relevant),all_required_recalled=set(relevant)<=set(ids))
 rows.append(row)
summary={name:dict(mean_recall_at_5=sum(r[name]['recall_at_5'] for r in rows)/len(rows),all_required_rate=sum(r[name]['all_required_recalled'] for r in rows)/len(rows)) for name in ['baseline','current']}
Path('examples/检索对照_独立集12问.json').write_text(json.dumps(dict(boundary='12 new author-created queries, frozen implementation; not external or blind benchmark. No retrieval tuning after observing results.',summary=summary,cases=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary));print('Current failures:',[r['id'] for r in rows if not r['current']['all_required_recalled']])
