import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from extrator import extract

def doc(components=None,refs=()):
    d={'openapi':'3.0.3','paths':{'/x':{'get':{'responses':{'200':{'content':{'application/json':{'schema':{'allOf':[{'$ref':r} for r in refs]}}}}}}}}}
    if components is not None: d['components']=components
    return d
class TestExtracao(unittest.TestCase):
    def test_sem_componentes(self):
        m,_,_=extract(doc(),'x'); self.assertEqual((m['defined_total'],m['refs_total'],m['reuse_percent']),(0,0,''))
    def test_sem_uso(self):
        m,_,_=extract(doc({'schemas':{'A':{},'B':{},'C':{}}}),'x'); self.assertEqual((m['defined_total'],m['reuse_percent']),(3,0))
    def test_uma_e_duas_refs(self):
        c={'schemas':{'A':{}}}; r='#/components/schemas/A'
        m,_,_=extract(doc(c,[r]),'x'); self.assertEqual((m['referenced_total'],m['reused_total']),(1,0))
        m,_,_=extract(doc(c,[r,r]),'x'); self.assertEqual((m['refs_total'],m['reused_total'],m['reuse_percent']),(2,1,100))
    def test_encadeada(self):
        c={'schemas':{'A':{'$ref':'#/components/schemas/B'},'B':{}}}; m,rows,_=extract(doc(c,['#/components/schemas/A']*3),'x'); self.assertEqual({x['nome']:x['refs_count'] for x in rows},{'A':3,'B':1})
    def test_escapes_e_invalidas(self):
        c={'schemas':{'a/b~c':{}}}; m,_,r=extract(doc(c,['#/components/schemas/a~1b~0c','#/components/schemas/ausente','https://example.org/spec','#/components/securitySchemes/X']),'x'); self.assertEqual((m['refs_total'],m['invalid_ref_count'],m['external_ref_count'],m['out_of_scope_ref_count']),(1,1,1,1))
    def test_tipo_incompativel(self):
        d=doc({'schemas':{'A':{}}}); d['paths']['/x']['get']['parameters']=[{'$ref':'#/components/schemas/A'}]
        m,_,r=extract(d,'x'); self.assertEqual((m['refs_total'],m['incompatible_ref_count'],r[0]['status']),(0,1,'tipo_incompativel'))
    def test_fragmento_percent_encoded(self):
        m,_,_=extract(doc({'schemas':{'com espaço':{}}},['#/components/schemas/com%20espa%C3%A7o']),'x'); self.assertEqual(m['refs_total'],1)
    def test_path_item_ref_externa(self):
        d=doc(); d['paths']['/x']['$ref']='other.yaml#/paths/~1x'
        m,_,_=extract(d,'x');self.assertEqual(m['external_ref_count'],1)
    def test_schema_ref_ignora_irmaos(self):
        d=doc({'schemas':{'A':{},'B':{}}})
        d['components']['schemas']['A']={'$ref':'#/components/schemas/B','properties':{'x':{'$ref':'#/components/schemas/B'}}}
        m,_,_=extract(d,'x');self.assertEqual(m['refs_total'],1)
    def test_paths_ignora_extensoes(self):
        d=doc({'schemas':{'A':{}}}); d['paths']['x-extra']={'get':{'responses':{'200':{'content':{'application/json':{'schema':{'$ref':'#/components/schemas/A'}}}}}}}
        m,_,_=extract(d,'x');self.assertEqual((m['operations_count'],m['refs_total']),(1,0))
    def test_operacoes(self):
        d=doc(); d['paths']['/x']['post']={}; d['paths']['/x']['parameters']=[]; m,_,_=extract(d,'x'); self.assertEqual(m['operations_count'],2)
    def test_exemplos_e_extensoes_nao_sao_refs(self):
        d=doc({'schemas':{'A':{}}}, ['#/components/schemas/A'])
        d['x-extension']={'$ref':'#/components/schemas/A'}
        d['components']['schemas']['A']['example']={'$ref':'#/components/schemas/A'}
        d['components']['schemas']['A']['properties']={'example':{'$ref':'#/components/schemas/A'}}
        m,_,_=extract(d,'x'); self.assertEqual(m['refs_total'],2)
    def test_examples_componente_referenciado(self):
        d=doc({'schemas':{'A':{}}, 'examples':{'demo':{'value':{'$ref':'#/components/schemas/A'}}}})
        m,_,_=extract(d,'x'); self.assertEqual(m['refs_total'],0)
if __name__=='__main__': unittest.main()
