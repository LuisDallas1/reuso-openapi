"""Análises descritivas exploratórias sobre a extração preliminar v3."""
import csv,json,math,statistics,sys
from collections import Counter
from pathlib import Path

CATS=('schemas','parameters','responses','requestBodies')
def frac(x,y):return 100*x/y if y else None
def q(values,p):
 a=sorted(values)
 if not a:return None
 j=(len(a)-1)*p;lo=int(j);hi=math.ceil(j)
 return a[lo]+(a[hi]-a[lo])*(j-lo)
def describe(a):
 return {'n':len(a),'min':min(a) if a else None,'q1':q(a,.25),'mediana':statistics.median(a) if a else None,'q3':q(a,.75),'max':max(a) if a else None,'media':statistics.mean(a) if a else None}
def write(path,rows):
 if rows:
  with path.open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def rank(a):
 ordered=sorted(enumerate(a),key=lambda x:x[1]);out=[0.0]*len(a);i=0
 while i<len(a):
  j=i+1
  while j<len(a) and ordered[j][1]==ordered[i][1]:j+=1
  r=(i+1+j)/2
  for k in range(i,j):out[ordered[k][0]]=r
  i=j
 return out
def spearman(a,b):
 if len(a)<2:return None
 x,y=rank(a),rank(b);mx=statistics.mean(x);my=statistics.mean(y)
 num=sum((u-mx)*(v-my) for u,v in zip(x,y));den=(sum((u-mx)**2 for u in x)*sum((v-my)**2 for v in y))**.5
 return num/den if den else None

def run(source,out,schema_csv=None):
 allowed=None
 if schema_csv is not None:
  with Path(schema_csv).open(encoding='utf-8-sig',newline='') as f:allowed={r['arquivo'] for r in csv.DictReader(f) if r['status']=='conforme_schema'}
 files=sorted((source/'por_documento').glob('*.json'));rows=[];cats={c:Counter() for c in CATS};positions=Counter();status=Counter(); providers=Counter();valid_source_components=0;self_refs=0
 for f in files:
  data=json.loads(f.read_text(encoding='utf8'));m=data['metrics']; spec=m['spec_id']
  if allowed is not None and spec not in allowed:continue
  doc={'spec_id':spec,'provedor_pasta':spec.split('/')[1], 'operacoes':m['operations_count'],'definidos':m['defined_total'],'referencias':m['refs_total'],'referenciados':m['referenced_total'],'reutilizados':m['reused_total'],'percentual_reuso':m['reuse_percent']}
  providers[doc['provedor_pasta']]+=1;counter={c:Counter() for c in CATS}
  for comp in data['components']:
   k=counter[comp['categoria']];k['definidos']+=1;k['referenciado']+=comp['refs_count']>=1;k['uma_vez']+=comp['refs_count']==1;k['reutilizado']+=comp['refs_count']>=2;k['sem_ref']+=comp['refs_count']==0
  for c in CATS:
   k=counter[c];cats[c].update(k)
   for name in ('definidos','sem_ref','uma_vez','referenciado','reutilizado'):doc[c+'_'+name]=k[name]
   doc[c+'_refs']=m['refs_'+c]
  for r in data['refs']:
   status[r['status']]+=1
   if r['status']!='valida':continue
   p=r['source_pointer']; source_group='paths' if p.startswith('/paths/') else 'components' if p.startswith('/components/') else 'outra'
   positions[source_group]+=1
   if source_group=='components':
    valid_source_components+=1
    # Detect only exact self-reference from inside the target component's definition.
    from urllib.parse import unquote
    def decode(x):return x.replace('~1','/').replace('~0','~')
    src=p.split('/');target=unquote(r['target'][1:]).split('/')
    if len(src)>=4 and len(target)==4 and src[1]=='components' and target[1]=='components' and decode(src[2])==decode(target[2]) and decode(src[3])==decode(target[3]):self_refs+=1
  rows.append(doc)
 if allowed is not None and {r['spec_id'] for r in rows} != allowed:raise ValueError('Seleção do esquema difere dos documentos disponíveis')
 if not rows:raise ValueError('nenhum resultado')
 n=len(rows);out.mkdir(parents=True,exist_ok=True);write(out/'por_documento.csv',rows)
 catrows=[]
 for c in CATS:
  k=cats[c];defined=k['definidos'];present=sum(r[c+'_definidos']>0 for r in rows);withref=sum(r[c+'_refs']>0 for r in rows)
  catrows.append({'categoria':c,'documentos_com_definicao':present,'documentos_com_referencia':withref,'definidos':defined,'nao_referenciados':k['sem_ref'],'referenciados_uma_vez':k['uma_vez'],'reutilizados':k['reutilizado'],'pct_componentes_sem_ref':frac(k['sem_ref'],defined),'pct_componentes_uma_vez':frac(k['uma_vez'],defined),'pct_componentes_reutilizados':frac(k['reutilizado'],defined),'ocorrencias_refs':sum(r[c+'_refs'] for r in rows)})
 write(out/'categorias_detalhadas.csv',catrows)
 category_doc=[]; cooccurrence=[]
 for c in CATS:
  present=[r for r in rows if r[c+'_definidos']>0]
  percentages=[100*r[c+'_reutilizado']/r[c+'_definidos'] for r in present]
  category_doc.append({'categoria':c,'documentos_com_categoria':len(present),'documentos_sem_categoria':n-len(present),'mediana_pct_reuso_por_documento':statistics.median(percentages) if percentages else None,'q1_pct_reuso_por_documento':q(percentages,.25),'q3_pct_reuso_por_documento':q(percentages,.75),'documentos_com_algum_reutilizado':sum(r[c+'_reutilizado']>0 for r in present)})
  for other in CATS:cooccurrence.append({'categoria_a':c,'categoria_b':other,'documentos_com_ambas':sum(r[c+'_definidos']>0 and r[other+'_definidos']>0 for r in rows),'base_documentos':n})
 write(out/'categorias_por_documento.csv',category_doc);write(out/'coocorrencia_categorias.csv',cooccurrence)
 measure={'operacoes':[r['operacoes'] for r in rows],'componentes_definidos':[r['definidos'] for r in rows],'referencias':[r['referencias'] for r in rows],'percentual_reuso':[r['percentual_reuso'] for r in rows if r['percentual_reuso']!='']}
 stats=[]
 for k,arr in measure.items():stats.append({'medida':k,**describe(arr)})
 write(out/'distribuicoes.csv',stats)
 top=sorted(rows,key=lambda r:(-r['referencias'],r['spec_id']));write(out/'maiores_referencias.csv',[{'posicao':i+1,**r} for i,r in enumerate(top[:25])])
 totalrefs=sum(r['referencias'] for r in rows);totaldefs=sum(r['definidos'] for r in rows);nonzero_defs=[r for r in rows if r['definidos']>0]
 share=[]
 for count in (1,5,10,math.ceil(.01*n),math.ceil(.1*n)):
  share.append({'primeiros_documentos':count,'base_documentos':n,'referencias_desses_documentos':sum(r['referencias'] for r in top[:count]),'percentual_de_todas_as_referencias':frac(sum(r['referencias'] for r in top[:count]),totalrefs)})
 write(out/'concentracao_referencias.csv',share)
 sensitivity=[]
 for removed in (0,1,5,math.ceil(.01*n)):
  subset=top[removed:]; eligible=[r['percentual_reuso'] for r in subset if r['percentual_reuso']!='']
  sensitivity.append({'maiores_documentos_excluidos':removed,'documentos_restantes':len(subset),'referencias_restantes':sum(r['referencias'] for r in subset),'mediana_referencias':statistics.median(r['referencias'] for r in subset),'mediana_reuso_pct':statistics.median(eligible) if eligible else None,'n_reuso_aplicavel':len(eligible)})
 write(out/'sensibilidade_extremos.csv',sensitivity)
 correlations=[]
 for x,y in [('operacoes','referencias'),('definidos','referencias'),('operacoes','definidos')]:
  correlations.append({'x':x,'y':y,'n':n,'spearman':spearman([r[x] for r in rows],[r[y] for r in rows]),'observacao':'descritivo; sem interpretacao causal'})
 write(out/'associacoes_exploratorias.csv',correlations)
 totals={'documentos':n,'provedores_por_pasta':len(providers),'operacoes':sum(r['operacoes'] for r in rows),'componentes_definidos':totaldefs,'componentes_sem_referencia':sum(k['sem_ref'] for k in cats.values()),'componentes_com_uma_referencia':sum(k['uma_vez'] for k in cats.values()),'componentes_reutilizados':sum(k['reutilizado'] for k in cats.values()),'documentos_sem_componentes':sum(r['definidos']==0 for r in rows),'documentos_com_componentes_sem_referencias':sum(r['definidos']>0 and r['referencias']==0 for r in rows),'documentos_com_refs':sum(r['referencias']>0 for r in rows),'documentos_com_reutilizados':sum(r['reutilizados']>0 for r in rows),'refs_centrais':totalrefs,'origem_refs_centrais':dict(positions),'refs_centrais_no_proprio_componente':self_refs,'contagem_status_ref':dict(status),'tratamento':'preliminar; sem inferencia causal; quartis por interpolacao inclusiva; componentes e documentos sao bases distintas'}
 (out/'totais.json').write_text(json.dumps(totals,ensure_ascii=False,indent=2),encoding='utf8')
 assert totals['componentes_sem_referencia']+totals['componentes_com_uma_referencia']+totals['componentes_reutilizados']==totaldefs
 assert sum(positions.values())==totalrefs
 assert sum(x['ocorrencias_refs'] for x in catrows)==totalrefs
 print(json.dumps(totals,ensure_ascii=False,indent=2));print('quartis',stats);print('concentracao',share);print('associacoes',correlations)
if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
