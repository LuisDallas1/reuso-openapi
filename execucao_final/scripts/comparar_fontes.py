"""Sensibilidade exploratória: comparação do clone fixado com índice atual."""
import csv,statistics,sys
from collections import Counter
from pathlib import Path

def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def run(metrics,crosswalk,out,schema_csv=None):
 docs=read(metrics)
 if schema_csv is not None:
  allowed={r['arquivo'] for r in read(schema_csv) if r['status']=='conforme_schema'}
  docs=[d for d in docs if d['spec_id'] in allowed]
  if {d['spec_id'] for d in docs}!=allowed:raise ValueError('Conjunto do esquema difere dos dados')
 cross={r['id_clone']:r for r in read(crosswalk)};groups={}
 for d in docs:
  parts=d['spec_id'].split('/');api='/'.join(parts[1:-2]);rec=cross.get(api)
  if rec is None:raise ValueError('ID não localizado no cruzamento: '+api)
  groups.setdefault(rec['status_comparacao'],[]).append(d)
 rows=[]
 for group,items in sorted(groups.items()):
  n=len(items);refs=[int(r['refs_total']) for r in items];per=[float(r['reuse_percent']) for r in items if r['reuse_percent']!=''];defined=sum(int(r['defined_total']) for r in items);reused=sum(int(r['reused_total']) for r in items)
  rows.append({'comparacao':group,'documentos':n,'documentos_com_refs':sum(x>0 for x in refs),'percentual_com_refs':100*sum(x>0 for x in refs)/n,'mediana_refs':statistics.median(refs),'componentes_definidos':defined,'componentes_reutilizados':reused,'proporcao_agregada_reutilizada':100*reused/defined if defined else '', 'documentos_reuso_aplicavel':len(per),'mediana_percentual_reuso':statistics.median(per) if per else ''})
 with Path(out).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('grupos',[(r['comparacao'],r['documentos']) for r in rows]);print('total',sum(r['documentos'] for r in rows))
if __name__=='__main__':run(*sys.argv[1:])
