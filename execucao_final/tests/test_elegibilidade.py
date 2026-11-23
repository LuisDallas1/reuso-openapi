import unittest,sys,tempfile,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from elegibilidade import inspect
class TestElegibilidade(unittest.TestCase):
 def check(self,data):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'doc.yaml'; b=data.encode();p.write_bytes(b);return inspect(p,hashlib.sha256(b).hexdigest())
 def test_sem_componentes_elegivel(self):
  self.assertEqual(self.check('openapi: 3.0.3\ninfo: {}\npaths:\n  /x:\n    get: {}\n')['status'],'elegivel_preliminar')
 def test_versao_fora(self):
  self.assertEqual(self.check('openapi: 3.1.0\ninfo: {}\npaths: {}\n')['motivo'],'versao_fora_escopo')
 def test_sem_operacoes(self):
  self.assertEqual(self.check('openapi: 3.0.3\ninfo: {}\npaths: {}\n')['motivo'],'sem_operacao')
 def test_valores_parecidos_com_data_e_igual(self):
  data='openapi: 3.0.3\ninfo: {title: example, version: 1}\npaths:\n  /x:\n    get:\n      x-example: 25:60:60\n      x-value: =\n'
  self.assertEqual(self.check(data)['status'],'elegivel_preliminar')
 def test_chaves_numericas_mantidas_como_texto(self):
  from yaml_aberto import load_document
  data=b'components:\n  schemas:\n    18_24: {}\n    123: {}\n'
  d,_=load_document(data);self.assertEqual(set(d['components']['schemas']),{'18_24','123'})
 def test_interpretacao_escalar_yaml(self):
  from yaml_aberto import load_document
  d,_=load_document(b'on_value: on\nleading: 012\nunderscores: 1_000\ntruth: true\ncount: 42\nscientific: 1e3\n')
  self.assertEqual((d['on_value'],d['leading'],d['underscores']),('on','012','1_000'))
  self.assertIs(d['truth'],True); self.assertEqual(d['count'],42); self.assertEqual(d['scientific'],1000.0)
 def test_chaves_duplicadas_registradas(self):
  data='openapi: 3.0.3\ninfo: {}\npaths:\n  /x: {get: {}}\n  /x: {post: {}}\n'
  self.assertEqual(self.check(data)['status'],'revisao')
 def test_merge_yaml_permite_sobrescrita_explicita(self):
  from yaml_aberto import load_document
  d,_=load_document(b'base: &b {name: old}\nobj: {<<: *b, name: new}\n')
  self.assertEqual(d['obj']['name'],'new')
 def test_hash_alterado(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'x';p.write_text('test');self.assertEqual(inspect(p,'outro')['motivo'],'hash_divergente')
if __name__=='__main__':unittest.main()
