"""Extração preliminar de candidatos da triagem, isolada por processo."""
import csv, hashlib, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def worker(path, rel, sha):
 from yaml_aberto import load_document
 from extrator import extract
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=sha: raise ValueError('hash divergente')
 doc,parser=load_document(raw); metrics,components,refs=extract(doc,rel)
 metrics['sha256']=sha; metrics['parser']=parser
 return {'metrics':metrics,'components':components,'refs':refs}

def run(root,table,out,timeout):
 with Path(table).open(encoding='utf-8-sig',newline='') as f:
  rows=[r for r in csv.DictReader(f) if r['status']=='elegivel_preliminar']
 store=out/'por_documento';store.mkdir(parents=True,exist_ok=True)
 def task(row):
  rel=row['arquivo'];sha=row['sha256'];dest=store/(hashlib.sha256((rel+'|'+sha).encode()).hexdigest()+'.json')
  if dest.exists(): return rel,'armazenado',''
  try:
   proc=subprocess.run([sys.executable,__file__,'--worker',str(root/rel),rel,sha],capture_output=True,timeout=timeout)
   if proc.returncode: return rel,'revisao',proc.stderr.decode('utf8',errors='replace')[-400:]
   data=json.loads(proc.stdout);tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8');os.replace(tmp,dest)
   return rel,'extraido',''
  except subprocess.TimeoutExpired: return rel,'revisao','tempo_limite_'+str(timeout)+'s'
  except Exception as exc: return rel,'revisao',str(exc)[:400]
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(task,r) for r in rows]
  log=[]
  for i,f in enumerate(as_completed(futures),1):
   rel,status,error=f.result();log.append({'arquivo':rel,'status':status,'motivo':error})
   if i%200==0: print('processados:',i,flush=True)
 with (out/'processamento.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['arquivo','status','motivo']);w.writeheader();w.writerows(sorted(log,key=lambda x:x['arquivo']))
 print('sucesso:',sum(x['status']!='revisao' for x in log),'revisao:',sum(x['status']=='revisao' for x in log),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='--worker': print(json.dumps(worker(sys.argv[2],sys.argv[3],sys.argv[4]),ensure_ascii=True))
 else: run(Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3]),int(sys.argv[4]))
