import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sensibilidade_definicao import target_key,is_self
class TestSensibilidade(unittest.TestCase):
 def test_target_com_escape(self):
  self.assertEqual(target_key('#/components/schemas/a~1b%20c'),('schemas','a/b c'))
 def test_autorreferencia(self):
  r={'source_pointer':'/components/schemas/a~1b/properties/x/$ref'}
  self.assertTrue(is_self(r,('schemas','a/b')))
  self.assertFalse(is_self(r,('schemas','outro')))
if __name__=='__main__':unittest.main()
