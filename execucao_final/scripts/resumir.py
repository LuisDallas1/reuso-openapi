"""Tabelas e figuras exploratórias; não representam conclusão definitiva."""
import csv,json,statistics,sys
from pathlib import Path
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CATS=('schemas','parameters','responses','requestBodies')
def csvwrite(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(source,out,schema_csv=None):
 allowed=None
 if schema_csv is not None:
  with Path(schema_csv).open(encoding='utf-8-sig',newline='') as f:allowed={r['arquivo'] for r in csv.DictReader(f) if r['status']=='conforme_schema'}
 files=sorted((source/'por_documento').glob('*.json'));data=[]; categories={c:Counter() for c in CATS}
 for p in files:
  d=json.loads(p.read_text(encoding='utf8'))
  if allowed is not None and d['metrics']['spec_id'] not in allowed:continue
  data.append(d['metrics'])
  for c in d['components']:
   k=categories[c['categoria']];k['definidos']+=1;k['referenciados']+=c['refs_count']>=1;k['reutilizados']+=c['refs_count']>=2
 n=len(data)
 if allowed is not None and {m['spec_id'] for m in data} != allowed:raise ValueError('Seleção do esquema difere dos documentos disponíveis')
 if not n:raise ValueError('Nenhum documento')
 refs=[x['refs_total'] for x in data]; per=[x['reuse_percent'] for x in data if x['reuse_percent']!='']
 q1=sum(x>0 for x in refs); defs=sum(categories[c]['definidos'] for c in CATS)
 cat_rows=[{'categoria':c,'definidos':categories[c]['definidos'],'percentual_das_definicoes':round(100*categories[c]['definidos']/defs,2) if defs else '', 'referenciados':categories[c]['referenciados'],'reutilizados':categories[c]['reutilizados']} for c in CATS]
 quartiles=statistics.quantiles(per,n=4,method='inclusive') if len(per)>1 else [per[0]]*3
 summary=[{'indicador':'documentos_analisados','valor':n},{'indicador':'documentos_com_refs','valor':q1},{'indicador':'percentual_documentos_com_refs','valor':round(100*q1/n,2)},{'indicador':'documentos_sem_refs','valor':n-q1},{'indicador':'mediana_refs_por_documento','valor':statistics.median(refs)},{'indicador':'total_refs_centrales','valor':sum(refs)},{'indicador':'total_componentes_definidos','valor':defs},{'indicador':'documentos_com_reuso_aplicavel','valor':len(per)},{'indicador':'documentos_reuso_na','valor':n-len(per)},{'indicador':'reuso_q1_pct','valor':quartiles[0]},{'indicador':'reuso_mediana_pct','valor':statistics.median(per)},{'indicador':'reuso_q3_pct','valor':quartiles[2]},{'indicador':'reuso_min_pct','valor':min(per)},{'indicador':'reuso_max_pct','valor':max(per)}]
 out.mkdir(parents=True,exist_ok=True);csvwrite(out/'indicadores.csv',summary);csvwrite(out/'categorias.csv',cat_rows)
 fig,ax=plt.subplots(figsize=(7.5,4.5)); names=[c['categoria'] for c in cat_rows]; values=[c['definidos'] for c in cat_rows]
 ax.bar(names,values,color='#386b87');ax.set_ylabel('Componentes definidos');ax.set_title('Componentes definidos por categoria — preliminar');ax.ticklabel_format(style='plain',axis='y');fig.tight_layout();fig.savefig(out/'componentes.png',dpi=160);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.5,4.5));ax.hist(per,bins=range(0,101,10),color='#386b87',edgecolor='white');ax.set(xlabel='Componentes reutilizados por documento (%)',ylabel='Documentos',title='Distribuição de reuso — preliminar');fig.tight_layout();fig.savefig(out/'reuso.png',dpi=160);plt.close(fig)
 print('documentos',n,'com_ref',q1,'mediana_refs',statistics.median(refs),'defs',defs,'reuso_mediana',statistics.median(per),'na',n-len(per))
if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
