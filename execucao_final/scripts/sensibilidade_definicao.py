"""Compara regras de contagem sem alterar a métrica principal do estudo."""
import csv,json,statistics,sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

def decode(x):return x.replace('~1','/').replace('~0','~')
def target_key(t):
 p=unquote(t[1:]).split('/')
 return (decode(p[2]),decode(p[3]))
def is_self(r,key):
 p=r['source_pointer'].split('/')
 return len(p)>=4 and p[1]=='components' and (decode(p[2]),decode(p[3]))==key

def run(source,out,schema_csv=None):
 allowed=None
 if schema_csv is not None:
  with Path(schema_csv).open(encoding='utf-8-sig',newline='') as f:allowed={r['arquivo'] for r in csv.DictReader(f) if r['status']=='conforme_schema'}
 rows=[]
 for p in sorted((source/'por_documento').glob('*.json')):
  d=json.loads(p.read_text(encoding='utf8'));m=d['metrics']
  if allowed is not None and m['spec_id'] not in allowed:continue
  path_refs=Counter();nonself_refs=Counter()
  for r in d['refs']:
   if r['status']!='valida':continue
   key=target_key(r['target'])
   if r['source_pointer'].startswith('/paths/'):path_refs[key]+=1
   if not is_self(r,key):nonself_refs[key]+=1
  names=[(c['categoria'],c['nome']) for c in d['components']];den=len(names)
  rp=sum(path_refs[k]>=2 for k in names);rs=sum(nonself_refs[k]>=2 for k in names)
  rows.append({'spec_id':m['spec_id'],'definidos':den,'refs_todas':m['refs_total'],'refs_em_paths':sum(path_refs.values()),'reutilizados_todas':m['reused_total'],'reutilizados_em_paths':rp,'reutilizados_sem_autorreferencia':rs,'reuso_todas_pct':m['reuse_percent'],'reuso_em_paths_pct':round(100*rp/den,4) if den else '', 'reuso_sem_autorreferencia_pct':round(100*rs/den,4) if den else ''})
 if allowed is not None and {r['spec_id'] for r in rows} != allowed:raise ValueError('Seleção do esquema difere dos documentos disponíveis')
 out.mkdir(parents=True,exist_ok=True)
 with (out/'sensibilidade_definicao.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 applicable=[r for r in rows if r['definidos']]
 summary={'documentos':len(rows),'documentos_com_componentes':len(applicable),'refs_todas':sum(r['refs_todas'] for r in rows),'refs_em_paths':sum(r['refs_em_paths'] for r in rows),'reutilizados_todas':sum(r['reutilizados_todas'] for r in rows),'reutilizados_em_paths':sum(r['reutilizados_em_paths'] for r in rows),'reutilizados_sem_autorreferencia':sum(r['reutilizados_sem_autorreferencia'] for r in rows),'mediana_reuso_todas_pct':statistics.median(r['reuso_todas_pct'] for r in applicable),'mediana_reuso_em_paths_pct':statistics.median(r['reuso_em_paths_pct'] for r in applicable),'mediana_reuso_sem_autorreferencia_pct':statistics.median(r['reuso_sem_autorreferencia_pct'] for r in applicable),'documentos_com_alguma_diferenca_paths':sum(r['reutilizados_todas']!=r['reutilizados_em_paths'] for r in rows),'documentos_com_alguma_diferenca_autorreferencia':sum(r['reutilizados_todas']!=r['reutilizados_sem_autorreferencia'] for r in rows)}
 assert all(r['reutilizados_em_paths']<=r['reutilizados_todas'] and r['reutilizados_sem_autorreferencia']<=r['reutilizados_todas'] for r in rows)
 (out/'sensibilidade_definicao_resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
