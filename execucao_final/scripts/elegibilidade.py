import csv, hashlib, json, subprocess, sys, os
from pathlib import Path

def inspect(path, expected):
    try:
        raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
        if digest!=expected: return {'status':'revisao','motivo':'hash_divergente'}
        from yaml_aberto import load_document
        doc,parser=load_document(raw)
        if not isinstance(doc,dict): return {'status':'excluido','motivo':'raiz_nao_objeto','parser':parser}
        import re
        ver=doc.get('openapi','')
        if not isinstance(ver,str) or not re.fullmatch(r'3\.0\.\d+',ver): return {'status':'excluido','motivo':'versao_fora_escopo','parser':parser,'versao':str(ver)}
        paths=doc.get('paths')
        if not isinstance(paths,dict): return {'status':'excluido','motivo':'paths_invalido','parser':parser,'versao':ver}
        methods={'get','post','put','patch','delete','head','options','trace'}
        ops=sum(1 for path,p in paths.items() if isinstance(path,str) and path.startswith('/') and isinstance(p,dict) for k,v in p.items() if k in methods and isinstance(v,dict))
        if not ops: return {'status':'excluido','motivo':'sem_operacao','parser':parser,'versao':ver}
        info=doc.get('info'); components=doc.get('components',{})
        if not isinstance(info,dict) or not isinstance(components,dict): return {'status':'excluido','motivo':'estrutura_minima_invalida','parser':parser,'versao':ver}
        for c in ('schemas','parameters','responses','requestBodies'):
            if c in components and not isinstance(components[c],dict): return {'status':'excluido','motivo':'categoria_invalida_'+c,'parser':parser,'versao':ver}
        return {'status':'elegivel_preliminar','motivo':'','parser':parser,'versao':ver,'operacoes':ops}
    except Exception as e: return {'status':'revisao','motivo':'erro_leitura: '+str(e)[:250]}

def run(root,inventory,out,timeout):
    with inventory.open(encoding='utf-8-sig',newline='') as f: rows=[x for x in csv.DictReader(f) if x['status']=='candidato']
    out.parent.mkdir(parents=True,exist_ok=True); checkpoint=out.with_suffix('.checkpoint.json')
    cache=json.loads(checkpoint.read_text(encoding='utf8')) if checkpoint.exists() else {}
    def save():
        tmp=checkpoint.with_suffix('.tmp'); tmp.write_text(json.dumps(cache,ensure_ascii=False),encoding='utf8'); os.replace(tmp,checkpoint)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    def process(r):
        rel=r['arquivo']; expected=r['sha256']; key=rel+'|'+expected
        try:
            p=subprocess.run([sys.executable,__file__,'--worker',str(root/rel),expected],capture_output=True,text=True,encoding='utf8',timeout=timeout)
            result=json.loads(p.stdout) if p.returncode==0 else {'status':'revisao','motivo':'processo_falhou: '+p.stderr[-250:]}
        except subprocess.TimeoutExpired: result={'status':'revisao','motivo':'tempo_limite_'+str(timeout)+'s'}
        except Exception as e: result={'status':'revisao','motivo':'erro_processo: '+str(e)[:200]}
        return key,result
    pending=[r for r in rows if r['arquivo']+'|'+r['sha256'] not in cache]
    print('retomados:',len(rows)-len(pending),'pendentes:',len(pending),flush=True)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(process,r) for r in pending]
        for i,future in enumerate(as_completed(futures),1):
            key,result=future.result();cache[key]=result
            if i%25==0: save()
            if i%200==0: print('novos avaliados:',i,flush=True)
    results=[]
    for r in rows:
        expected=r['sha256'];rel=r['arquivo'];result=cache[rel+'|'+expected]
        results.append({'api_id':r['api_id'],'arquivo':rel,'sha256':expected,'status':result.get('status','revisao'),'motivo':result.get('motivo',''),'parser':result.get('parser',''),'openapi_version':result.get('versao',''),'operations_count':result.get('operacoes','')})
    save()
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    from collections import Counter
    print('status:',dict(Counter(x['status'] for x in results)),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='--worker': print(json.dumps(inspect(Path(sys.argv[2]),sys.argv[3]),ensure_ascii=False))
    else: run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),int(sys.argv[4]) if len(sys.argv)>4 else 20)
