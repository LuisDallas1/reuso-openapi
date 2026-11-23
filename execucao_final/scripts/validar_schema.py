"""Verificação exploratória contra JSON Schema informativo da OpenAPI 3.0."""
import csv,hashlib,json,os,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed

def worker(path,expected,schema_path):
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:return {'status':'revisao','motivo':'hash_divergente'}
 from yaml_aberto import load_document
 from jsonschema import Draft4Validator
 doc,parser=load_document(raw)
 schema=json.loads(Path(schema_path).read_text(encoding='utf8'))
 err=next(Draft4Validator(schema).iter_errors(doc),None)
 if err is None:return {'status':'conforme_schema','motivo':'','parser':parser}
 pointer=''.join('/'+str(x).replace('~','~0').replace('/','~1') for x in err.absolute_path)
 return {'status':'nao_conforme_schema','motivo':err.message[:600],'ponteiro':pointer,'palavra_chave':str(err.validator),'parser':parser}

def run(root,table,schema_path,out,timeout,limit):
 with Path(table).open(encoding='utf-8-sig',newline='') as f:rows=[r for r in csv.DictReader(f) if r['status']=='elegivel_preliminar']
 if limit:rows=rows[:limit]
 out.parent.mkdir(parents=True,exist_ok=True)
 cachefile=out.with_suffix('.checkpoint.json');cache=json.loads(cachefile.read_text(encoding='utf8')) if cachefile.exists() else {}
 schema_sha=hashlib.sha256(schema_path.read_bytes()).hexdigest()
 def key(r):return r['arquivo']+'|'+r['sha256']+'|'+schema_sha
 def save():
  tmp=cachefile.with_suffix('.tmp');tmp.write_text(json.dumps(cache,ensure_ascii=False),encoding='utf8');os.replace(tmp,cachefile)
 def task(r):
  try:
   proc=subprocess.run([sys.executable,__file__,'--worker',str(root/r['arquivo']),r['sha256'],str(schema_path)],capture_output=True,timeout=timeout)
   if proc.returncode:return key(r),{'status':'revisao','motivo':'processo_falhou: '+proc.stderr.decode('utf8',errors='replace')[-400:]}
   return key(r),json.loads(proc.stdout)
  except subprocess.TimeoutExpired:return key(r),{'status':'revisao','motivo':'tempo_limite_'+str(timeout)+'s'}
  except Exception as e:return key(r),{'status':'revisao','motivo':str(e)[:400]}
 pending=[r for r in rows if key(r) not in cache]
 print('total:',len(rows),'retomados:',len(rows)-len(pending),'pendentes:',len(pending),flush=True)
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(task,r) for r in pending]
  for i,f in enumerate(as_completed(futures),1):
   k,result=f.result();cache[k]=result
   if i%20==0:save()
   if i%100==0:print('novos avaliados:',i,flush=True)
 save();output=[]
 for r in rows:
  v=cache[key(r)];output.append({'api_id':r['api_id'],'arquivo':r['arquivo'],'sha256':r['sha256'],'status':v.get('status','revisao'),'ponteiro':v.get('ponteiro',''),'palavra_chave':v.get('palavra_chave',''),'motivo':v.get('motivo',''),'parser':v.get('parser','')})
 with out.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
 from collections import Counter
 print('status',dict(Counter(r['status'] for r in output)),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='--worker':
  try:print(json.dumps(worker(sys.argv[2],sys.argv[3],sys.argv[4]),ensure_ascii=True))
  except Exception as e:print(json.dumps({'status':'revisao','motivo':'erro: '+str(e)[:600]},ensure_ascii=True))
 else:run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]) if len(sys.argv)>6 else 0)
