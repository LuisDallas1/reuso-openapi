"""Empacota resultados locais e registra hashes; não publica conteúdo."""
import csv,hashlib,io,json,platform,sys,zipfile
from datetime import datetime,timezone
from importlib.metadata import version
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def run(dest):
 fixed=['README.md','requirements.txt','artigo_rascunho_preliminar.zip','artigo_rascunho_preliminar.pdf','selecao/inventario.csv','selecao/elegibilidade_v4.csv','selecao/schema_v4.csv','selecao/pendencias_politica.csv','selecao/auditoria_textual.csv','catalogo/lista.json','catalogo/metadados.json','catalogo/comparacao_indice_clone.csv','catalogo/sensibilidade_fontes_schema.csv','catalogo/sensibilidade_fontes.csv','selecao/arquivos_alternativos.txt','analise_preliminar_v4/spec_metrics.csv','analise_preliminar_v4/processamento.csv','analise_preliminar_v4/verificacao.json']
 files=[Path(x) for x in fixed]
 for directory,glob in [('scripts','*.py'),('tests','*.py'),('schemas','*.json'),('resultados_schema','*'),('resultados_exploratorios','*'),('dados_auditaveis_schema','*.gz'),('dados_auditaveis','*.gz'),('analise_preliminar_v4/por_documento','*.json')]:
  files.extend(p for p in Path(directory).glob(glob) if p.is_file())
 files=sorted(set(files),key=lambda p:p.as_posix())
 missing=[str(p) for p in files if not p.exists()]
 if missing:raise FileNotFoundError(str(missing))
 manifest=[]
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for i,p in enumerate(files,1):
   z.write(p,p.as_posix());manifest.append({'arquivo':p.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
   if i%400==0:print('arquivos empacotados:',i,flush=True)
  buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=['arquivo','bytes','sha256']);w.writeheader();w.writerows(manifest);z.writestr('MANIFESTO_SHA256.csv',buf.getvalue().encode('utf-8-sig'))
  meta={'criado_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'PyYAML':version('PyYAML'),'jsonschema':version('jsonschema'),'matplotlib':version('matplotlib'),'revisao_clone':'f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49','schema_sha256':sha(Path('schemas/openapi-3.0-2024-10-18.json')),'dados_origem_no_pacote':False,'aviso':'Resultados exploratórios. O pacote contém dados derivados, índices públicos, scripts e hashes, não os arquivos de origem completos. Revisar licenças antes de divulgar.'}
  z.writestr('METADADOS_PACOTE.json',json.dumps(meta,ensure_ascii=False,indent=2).encode('utf8'))
 print('arquivos:',len(files),'zip_bytes:',dest.stat().st_size,'sha256:',sha(dest),flush=True)
if __name__=='__main__':run(Path(sys.argv[1]))
