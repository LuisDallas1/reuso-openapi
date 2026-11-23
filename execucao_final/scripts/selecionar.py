"""Inventory repository versions; decisions are preliminary until protocol freeze."""
import csv, hashlib, sys, json, os
from pathlib import Path
from collections import defaultdict
import yaml
LOADER = getattr(yaml,'CSafeLoader',yaml.SafeLoader)

def select(group):
    # Unknown/failed metadata means preferred status cannot be established.
    if any(r['metadata_status'] != 'ok' for r in group): return None,'metadata_indisponivel'
    preferred=[r for r in group if r['preferred'] is True]
    if len(preferred)==1: return preferred[0], 'preferred_unica'
    if len(preferred)>1: return None,'preferred_ambigua'
    if len(group)==1 and group[0]['preferred'] is None: return group[0], 'unica_versao_sem_marcador'
    return None,'sem_preferred'

def read_preferred(raw):
    # Parse only the top-level info mapping: this is metadata reading, not OAS validation.
    events=iter(yaml.parse(raw, Loader=yaml.SafeLoader))
    from yaml.events import MappingStartEvent, MappingEndEvent, ScalarEvent, SequenceStartEvent, SequenceEndEvent
    depth=0; info_depth=None; root_key=None; info_key=None; seen_info=False; result=None
    for ev in events:
        if isinstance(ev,(MappingStartEvent,SequenceStartEvent)):
            depth+=1
            if depth==2 and root_key is not None:
                if root_key=='info' and isinstance(ev,MappingStartEvent): seen_info=True; info_depth=depth
                root_key=None
            elif info_depth is not None and depth==info_depth+1 and info_key is not None:
                info_key=None
        elif isinstance(ev,(MappingEndEvent,SequenceEndEvent)):
            if info_depth is not None and depth==info_depth: return result
            depth-=1
        elif isinstance(ev,ScalarEvent):
            if depth==1:
                if root_key is None: root_key=ev.value
                else: root_key=None
            elif info_depth is not None and depth==info_depth:
                if info_key is None: info_key=ev.value
                else:
                    if info_key=='x-preferred':
                        if ev.value.lower() not in ('true','false'): raise ValueError('x-preferred nao booleano')
                        result=ev.value.lower()=='true'
                    info_key=None
            elif info_depth is None and depth==2 and root_key is not None:
                root_key=None
    if not seen_info: raise ValueError('info ausente ou invalido')
    return result

def inventory(root,out):
    files=sorted(p for name in ('openapi.yaml','swagger.yaml') for p in root.glob('APIs/**/'+name))
    versions={}; alternatives=[]
    for p in files:
        key=p.parent.relative_to(root).as_posix()
        if key not in versions: versions[key]=p
        elif p.name=='openapi.yaml': alternatives.append(versions[key].relative_to(root).as_posix()); versions[key]=p
        else: alternatives.append(p.relative_to(root).as_posix())
    out.parent.mkdir(parents=True,exist_ok=True)
    checkpoint=out.with_suffix('.checkpoint.json')
    cache=json.loads(checkpoint.read_text(encoding='utf8')) if checkpoint.exists() else {}
    groups=defaultdict(list)
    def save():
        temp=checkpoint.with_suffix('.tmp'); temp.write_text(json.dumps(cache,ensure_ascii=False),encoding='utf8'); os.replace(temp,checkpoint)
    for n,(key,p) in enumerate(sorted(versions.items()),1):
        rel=p.relative_to(root).as_posix(); api=p.parent.parent.relative_to(root/'APIs').as_posix()
        stat=p.stat(); signature=[stat.st_size,stat.st_mtime_ns]
        entry=cache.get(rel)
        if not entry or entry['signature']!=signature:
            entry={'signature':signature,'metadata_status':'ok','preferred':None,'sha256':''}
            try:
                raw=p.read_bytes(); entry['sha256']=hashlib.sha256(raw).hexdigest(); entry['preferred']=read_preferred(raw)
            except Exception as e: entry['metadata_status']='erro: '+str(e)[:180]
            cache[rel]=entry
        row={'api_id':api,'versao_pasta':p.parent.name,'arquivo':rel,'metadata_status':entry['metadata_status'],'preferred':entry['preferred'],'sha256':entry['sha256'],'motivo_versao':'','status':'pendente'}
        groups[api].append(row)
        if n%100==0: save()
        if n%500==0: print('lidos:',n,flush=True)
    save(); rows=[]; hashes={}
    for api,group in sorted(groups.items()):
        chosen,reason=select(group)
        for r in group:
            r['motivo_versao']=reason if r is chosen or chosen is None else 'outra_versao'
            r['status']='candidato' if r is chosen else ('revisao' if chosen is None else 'excluido_versao')
            if r is chosen:
                h=r['sha256']
                if h in hashes: r['status']='excluido_duplicado'; r['motivo_versao']='duplicado_de:'+hashes[h]
                else: hashes[h]=r['arquivo']
            rows.append(r)
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (out.parent/'arquivos_alternativos.txt').write_text('\n'.join(alternatives),encoding='utf8')
    from collections import Counter
    print('versoes:',len(rows),'apis:',len(groups),'status:',dict(Counter(r['status'] for r in rows)),flush=True)
if __name__=='__main__': inventory(Path(sys.argv[1]),Path(sys.argv[2]))
