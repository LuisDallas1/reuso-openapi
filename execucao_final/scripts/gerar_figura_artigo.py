import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with Path('resultados_schema/categorias_detalhadas.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(4.6,3.15));left=[0.0]*len(rows)
for label,key,color in [('0 refs','pct_componentes_sem_ref','#b56a51'),('1 ref','pct_componentes_uma_vez','#d7a849'),('2 ou mais','pct_componentes_reutilizados','#427c73')]:
 vals=[float(x[key]) for x in rows];ax.barh([x['categoria'] for x in rows],vals,left=left,label=label,color=color)
 for i,v in enumerate(vals):
  if v>=9:ax.text(left[i]+v/2,i,f'{v:.0f}%',ha='center',va='center',fontsize=10,color='white' if color!='#d7a849' else '#222')
 left=[a+b for a,b in zip(left,vals)]
ax.set_xlim(0,100);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Percentual dos componentes',fontsize=11);ax.tick_params(labelsize=10);ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),ncol=3,frameon=False,fontsize=9)
fig.subplots_adjust(left=.26,right=.93,bottom=.31,top=.97);fig.savefig('artigo_rascunho/figures/uso_por_categoria.png',dpi=240);plt.close(fig)
