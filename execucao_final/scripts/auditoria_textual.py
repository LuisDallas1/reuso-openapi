"""Checagem textual limitada: compara linhas com $ref com registros extraídos."""
import csv,re,sys
from pathlib import Path
WANTED=['APIs/microsoft.com/graph-beta/1.0.1/openapi.yaml','APIs/1password.com/events/1.2.0/openapi.yaml','APIs/6-dot-authentiqio.appspot.com/6/openapi.yaml','APIs/mermade.org.uk/openapi-converter/1.0.0/openapi.yaml','APIs/etherpad.local/1.2.15/openapi.yaml','APIs/statsocial.com/1.0.0/openapi.yaml','APIs/rev.ai/v1/openapi.yaml']
def run(root,metric_csv,out):
 with metric_csv.open(encoding='utf-8-sig',newline='') as f:metrics={r['spec_id']:r for r in csv.DictReader(f)}
 rows=[]
 for rel in WANTED:
  text=(root/rel).read_text(encoding='utf8');lines=text.splitlines();textual=sum(bool(re.match(r'^\s*(?:-\s*)?\$ref\s*:',line)) for line in lines);r=metrics[rel]
  extracted=sum(int(r[x]) for x in ['refs_total','invalid_ref_count','external_ref_count','out_of_scope_ref_count'])
  rows.append({'arquivo':rel,'linhas_ref_textual':textual,'referencias_registradas_todos_status':extracted,'diferenca':textual-extracted})
 with out.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('arquivos',len(rows),'diferencas',sum(x['diferenca']!=0 for x in rows))
if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
