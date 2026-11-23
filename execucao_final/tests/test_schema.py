import tempfile,unittest,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validar_schema import worker
SCHEMA=Path(__file__).resolve().parents[1]/'schemas'/'openapi-3.0-2024-10-18.json'
class TestSchema(unittest.TestCase):
 def check(self,content):
  b=content.encode('utf8')
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'doc.yaml';p.write_bytes(b);return worker(str(p),hashlib.sha256(b).hexdigest(),str(SCHEMA))
 def test_minimo_valido(self):
  d='openapi: 3.0.3\ninfo: {title: Test, version: "1"}\npaths: {}\n';self.assertEqual(self.check(d)['status'],'conforme_schema')
 def test_falta_info_title(self):
  d='openapi: 3.0.3\ninfo: {version: "1"}\npaths: {}\n';self.assertEqual(self.check(d)['status'],'nao_conforme_schema')
 def test_operacao_sem_respostas(self):
  d='openapi: 3.0.3\ninfo: {title: Test, version: "1"}\npaths:\n  /x:\n    get: {}\n';self.assertEqual(self.check(d)['status'],'nao_conforme_schema')
if __name__=='__main__':unittest.main()
