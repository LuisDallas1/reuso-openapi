import csv,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def run(base):
 cats=read(base/'categorias_detalhadas.csv');labels=[x['categoria']+' (n='+format(int(x['definidos']),',').replace(',','.')+')' for x in cats]
 series=[('Sem referência','pct_componentes_sem_ref','#b56a51'),('Uma referência','pct_componentes_uma_vez','#d7a849'),('Duas ou mais','pct_componentes_reutilizados','#427c73')]
 fig,ax=plt.subplots(figsize=(9,4.8));left=[0.0]*len(cats)
 for label,key,color in series:
  vals=[float(x[key]) for x in cats];ax.barh(labels,vals,left=left,label=label,color=color)
  for i,v in enumerate(vals):
   if v>=6:ax.text(left[i]+v/2,i,f'{v:.1f}%',ha='center',va='center',color='white' if color!='#d7a849' else '#222',fontsize=9)
  left=[a+b for a,b in zip(left,vals)]
 ax.set_xlim(0,100);ax.set_xlabel('Percentual dos componentes definidos na categoria');ax.set_title('Uso dos componentes por categoria — preliminar');ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.5,-.15),ncol=3,frameon=False);fig.tight_layout();fig.savefig(base/'uso_por_categoria.png',dpi=160);plt.close(fig)
 data=read(base/'concentracao_referencias.csv');x=[0]+[100*int(r['primeiros_documentos'])/int(r['base_documentos']) for r in data];y=[0]+[float(r['percentual_de_todas_as_referencias']) for r in data]
 fig,ax=plt.subplots(figsize=(7.8,4.5));ax.plot(x,y,marker='o',color='#386b87');ax.set(xlabel='Percentual dos documentos com mais referências',ylabel='Percentual acumulado das referências',title='Concentração de referências — preliminar');ax.set_ylim(0,100);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(base/'concentracao.png',dpi=160);plt.close(fig)
if __name__=='__main__':run(Path(sys.argv[1]))
