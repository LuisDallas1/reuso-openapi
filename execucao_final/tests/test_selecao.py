import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from selecionar import select,read_preferred

def row(p=None,status='ok'): return {'preferred':p,'metadata_status':status}
class TestSelecao(unittest.TestCase):
 def test_metadados_com_info_aninhado(self):
  b=b'openapi: 3.0.0\nservers:\n  - url: https://example.org\ninfo:\n  title: Test\n  contact:\n    name: X\n  x-preferred: true\npaths: {}\n'
  self.assertIs(read_preferred(b),True)
 def test_preferred(self):
  a,b=row(False),row(True); self.assertIs(select([a,b])[0],b)
 def test_unica(self): self.assertEqual(select([row()])[1],'unica_versao_sem_marcador')
 def test_multiplas_sem_preferred(self): self.assertIsNone(select([row(),row()])[0])
 def test_ambiguo(self): self.assertIsNone(select([row(True),row(True)])[0])
 def test_falha_impede_escolha(self): self.assertIsNone(select([row(True),row(None,'erro')])[0])
if __name__=='__main__': unittest.main()
