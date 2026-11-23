import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analise_ampliada import q,rank,spearman,frac
class TesteAnalise(unittest.TestCase):
 def test_quartis_inclusivos(self):
  self.assertEqual(q([10,0,20,30],.25),7.5)
 def test_empates_e_associacao(self):
  self.assertEqual(rank([10,10,20]),[1.5,1.5,3.0])
  self.assertAlmostEqual(spearman([1,2,3],[9,5,1]),-1.0)
  self.assertIsNone(spearman([1,1],[2,3]))
 def test_denominador_zero(self):self.assertIsNone(frac(0,0))
if __name__=='__main__':unittest.main()
