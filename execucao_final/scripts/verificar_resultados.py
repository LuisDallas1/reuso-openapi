import json,csv,collections,sys
from pathlib import Path
base=Path(sys.argv[1]); files=sorted((base/'por_documento').glob('*.json')); rows=[];errors=[];status=collections.Counter();samples={}
for p in files:
 try:
  d=json.loads(p.read_text(encoding='utf8'));m=d['metrics'];cs=d['components'];refs=d['refs'];rows.append(m);status.update(x['status'] for x in refs)
  cats=('schemas','parameters','responses','requestBodies')
  checks=[m['defined_total']==len(cs),m['defined_total']==sum(m['defined_'+c] for c in cats),m['refs_total']==sum(m['refs_'+c] for c in cats),m['refs_total']==sum(x['status']=='valida' for x in refs),m['reused_total']<=m['referenced_total']<=m['defined_total'],m['refs_total']==sum(x['refs_count'] for x in cs)]
  if not all(checks): errors.append([m['spec_id'],checks])
  for r in refs:
   if r['status'] in ('externa','invalida','tipo_incompativel') and r['status'] not in samples: samples[r['status']]=(m['spec_id'],r['source_pointer'],r['target'])
 except Exception as e: errors.append([str(p),str(e)])
if not rows: raise SystemExit('nenhum resultado')
with (base/'spec_metrics.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'documentos':len(rows),'inconsistencias':errors,'status_ref':dict(status),'sem_refs':sum(m['refs_total']==0 for m in rows),'sem_components':sum(m['defined_total']==0 for m in rows),'amostras_para_conferencia':samples}
(base/'verificacao.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('documentos',len(rows),'inconsistencias',len(errors),'status_ref',dict(status),'sem_refs',summary['sem_refs'],'sem_components',summary['sem_components']);print('amostras',samples)
