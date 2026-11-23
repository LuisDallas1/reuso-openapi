"""Exporta tabelas detalhadas em CSV compactado para auditoria local."""
import csv,gzip,json,sys
from pathlib import Path

def run(root,out,schema_csv=None):
 allowed=None
 if schema_csv is not None:
  with Path(schema_csv).open(encoding='utf-8-sig',newline='') as f:allowed={r['arquivo'] for r in csv.DictReader(f) if r['status']=='conforme_schema'}
 out.mkdir(parents=True,exist_ok=True)
 fields_components=['spec_id','categoria','nome','refs_count','classificacao']
 fields_refs=['spec_id','source_pointer','target','categoria','status']
 with gzip.open(out/'components.csv.gz','wt',encoding='utf-8-sig',newline='') as fc, gzip.open(out/'references.csv.gz','wt',encoding='utf-8-sig',newline='') as fr:
  cw=csv.DictWriter(fc,fieldnames=fields_components);rw=csv.DictWriter(fr,fieldnames=fields_refs);cw.writeheader();rw.writeheader();n=c=r=0
  for p in sorted((root/'por_documento').glob('*.json')):
   d=json.loads(p.read_text(encoding='utf8'))
   if allowed is not None and d['metrics']['spec_id'] not in allowed:continue
   cw.writerows(d['components']);rw.writerows(d['refs']);n+=1;c+=len(d['components']);r+=len(d['refs'])
 if allowed is not None and n!=len(allowed):raise ValueError('Seleção do esquema difere dos documentos disponíveis')
 print('documentos',n,'componentes',c,'referencias_todos_status',r)
if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
