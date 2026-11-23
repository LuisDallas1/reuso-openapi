import csv, json, hashlib, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
from yaml_aberto import load_document

CATS = ('schemas', 'parameters', 'responses', 'requestBodies')
METHODS = {'get','put','post','delete','options','head','patch','trace'}
def esc(s): return str(s).replace('~','~0').replace('/','~1')
def unesc(s):
    if re.search(r'~(?![01])', s): raise ValueError('escape invalido')
    return s.replace('~1','/').replace('~0','~')
def extract(doc, spec_id):
    if not isinstance(doc,dict) or not re.fullmatch(r'3\.0\.\d+',str(doc.get('openapi',''))): raise ValueError('versao fora de escopo')
    paths=doc.get('paths')
    if not isinstance(paths,dict): raise ValueError('paths ausente ou invalido')
    ops=sum(1 for path,p in paths.items() if isinstance(path,str) and path.startswith('/') and isinstance(p,dict) for k,v in p.items() if k in METHODS and isinstance(v,dict))
    if not ops: raise ValueError('sem operacoes HTTP')
    comp=doc.get('components',{})
    if not isinstance(comp,dict): raise ValueError('components invalido')
    components={}
    for c in CATS:
        v=comp.get(c,{})
        if not isinstance(v,dict): raise ValueError('categoria de components invalida: '+c)
        for name in v: components[(c,str(name))]=0
    refs=[]
    # Traverse OAS structural locations only. Values of examples, defaults and
    # vendor extensions are data, not Reference Objects.
    def record(v,loc,kind):
        cat=''; name=''; status='fora_de_escopo'
        if not isinstance(v,str): status='invalida'
        elif not v.startswith('#'): status='externa'
        elif v.startswith('#'):
            try:
                fragment=unquote(v[1:], encoding='utf-8', errors='strict')
                if re.search(r'%(?![0-9a-fA-F]{2})',v[1:]): raise ValueError('percent-escape invalido')
            except (UnicodeError,ValueError): fragment=''; status='invalida'
            parts=('#'+fragment).split('/')
            if len(parts)>=4 and parts[1]=='components':
                try: cat=unesc(parts[2]); name=unesc(parts[3])
                except ValueError: status='invalida'
                else:
                    if cat in CATS:
                        if len(parts)!=4: status='fora_de_escopo'
                        elif (cat,name) not in components: status='invalida'
                        elif cat != {'schema':'schemas','parameter':'parameters','response':'responses','requestBody':'requestBodies'}.get(kind): status='tipo_incompativel'
                        else: status='valida'; components[(cat,name)]+=1
        refs.append({'spec_id':spec_id,'source_pointer':loc,'target':v,'categoria':cat,'status':status})
    def walk(obj,kind,pointer=''):
        if not isinstance(obj,dict): return
        if kind in {'schema','parameter','response','requestBody','header','example','link','callback','securityScheme','path'} and '$ref' in obj:
            record(obj['$ref'],pointer+'/$ref',kind)
            # Reference Objects do not have meaningful sibling fields in OAS 3.0.
            if kind!='path': return
        def one(key, child):
            if key in obj: walk(obj[key],child,pointer+'/'+esc(key))
        def mapping(key, child):
            value=obj.get(key)
            if isinstance(value,dict):
                for name,item in value.items(): walk(item,child,pointer+'/'+esc(key)+'/'+esc(name))
        def array(key, child):
            value=obj.get(key)
            if isinstance(value,list):
                for i,item in enumerate(value): walk(item,child,pointer+'/'+esc(key)+'/'+str(i))
        if kind=='root':
            paths_obj=obj.get('paths')
            if isinstance(paths_obj,dict):
                for name,item in paths_obj.items():
                    if isinstance(name,str) and name.startswith('/'): walk(item,'path',pointer+'/paths/'+esc(name))
            one('components','components')
        elif kind=='components':
            for key,child in [('schemas','schema'),('parameters','parameter'),('responses','response'),('requestBodies','requestBody'),('headers','header'),('examples','example'),('links','link'),('callbacks','callback'),('securitySchemes','securityScheme')]: mapping(key,child)
        elif kind=='path':
            for method in sorted(METHODS): one(method,'operation')
            array('parameters','parameter')
        elif kind=='operation':
            array('parameters','parameter'); one('requestBody','requestBody'); mapping('responses','response'); mapping('callbacks','callback')
        elif kind=='callback':
            for key,item in obj.items():
                if key!='$ref' and not str(key).startswith('x-'): walk(item,'path',pointer+'/'+esc(key))
        elif kind in {'parameter','header'}:
            one('schema','schema'); mapping('content','media'); mapping('examples','example')
        elif kind=='requestBody': mapping('content','media')
        elif kind=='response':
            mapping('headers','header'); mapping('content','media'); mapping('links','link')
        elif kind=='media':
            one('schema','schema'); mapping('examples','example'); mapping('encoding','encoding')
        elif kind=='encoding': mapping('headers','header')
        elif kind=='schema':
            for key in ('items','not','additionalProperties'): one(key,'schema')
            for key in ('allOf','oneOf','anyOf'): array(key,'schema')
            mapping('properties','schema')
    walk(doc,'root')
    rows=[{'spec_id':spec_id,'categoria':c,'nome':n,'refs_count':count,'classificacao':'reutilizado' if count>=2 else 'referenciado_uma_vez' if count else 'nao_referenciado'} for (c,n),count in components.items()]
    valid=Counter(x['categoria'] for x in refs if x['status']=='valida')
    m={'spec_id':spec_id,'openapi_version':doc['openapi'],'operations_count':ops}
    m.update({'defined_'+c:sum(1 for cat,_ in components if cat==c) for c in CATS})
    m.update({'refs_'+c:valid[c] for c in CATS})
    m.update(defined_total=len(components), refs_total=sum(valid.values()),referenced_total=sum(n>=1 for n in components.values()),reused_total=sum(n>=2 for n in components.values()),reuse_percent=round(100*sum(n>=2 for n in components.values())/len(components),4) if components else '', invalid_ref_count=sum(x['status'] in ('invalida','tipo_incompativel') for x in refs), incompatible_ref_count=sum(x['status']=='tipo_incompativel' for x in refs),external_ref_count=sum(x['status']=='externa' for x in refs),out_of_scope_ref_count=sum(x['status']=='fora_de_escopo' for x in refs))
    return m,rows,refs

def write_csv(path, rows, fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)

def run(root,out,limit=20):
    # Deliberately exploratory: sorted first successful files; not a representative sample.
    files=sorted(root.glob('APIs/**/openapi.yaml'))
    metrics=[]; comps=[]; refs=[]; log=[]
    for path in files:
        if len(metrics)>=limit: break
        rel=path.relative_to(root).as_posix()
        try:
            raw=path.read_bytes(); doc,parser=load_document(raw); m,c,r=extract(doc,rel)
            m['sha256']=hashlib.sha256(raw).hexdigest(); metrics.append(m); comps.extend(c); refs.extend(r)
            log.append({'arquivo':rel,'status':'incluido','motivo':''})
        except Exception as e: log.append({'arquivo':rel,'status':'excluido','motivo':str(e)})
    out.mkdir(parents=True,exist_ok=True)
    if metrics: write_csv(out/'spec_metrics.csv',metrics,list(metrics[0]))
    write_csv(out/'components.csv',comps,['spec_id','categoria','nome','refs_count','classificacao'])
    write_csv(out/'references.csv',refs,['spec_id','source_pointer','target','categoria','status'])
    write_csv(out/'selection_log.csv',log,['arquivo','status','motivo'])
    print(f'candidatos={len(log)}, aceitos={len(metrics)}, excluidos={len(log)-len(metrics)}, componentes={len(comps)}, referencias={len(refs)}')
if __name__=='__main__': run(Path(sys.argv[1]),Path(sys.argv[2]))
