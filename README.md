# Reuso em especificações OpenAPI

Este repositório reúne o material de reprodução de um estudo empírico e descritivo sobre componentes e referências em documentos OpenAPI do catálogo [APIs.guru](https://github.com/APIs-guru/openapi-directory).

O conjunto principal contém 1.617 especificações OpenAPI 3.0.x. A análise identifica componentes definidos nas categorias `schemas`, `parameters`, `responses` e `requestBodies` e suas referências internas diretas. Neste estudo, um componente é considerado reutilizado quando recebe referências em pelo menos duas posições distintas. Isso não implica necessariamente uso em operações distintas ou reuso de código.

Os critérios foram aperfeiçoados após uma exploração inicial dos dados. Os resultados são exploratórios e descrevem o conjunto estudado; não constituem um estudo confirmatório pré-registrado.

## Conteúdo

- `execucao_final/PROTOCOLO.md`: critérios, métricas e procedimentos.
- `execucao_final/RELATORIO.md`: resultados e limitações das análises.
- `execucao_final/scripts/` e `execucao_final/tests/`: código e testes.
- `execucao_final/selecao/`: inventário e registros de seleção.
- `execucao_final/resultados/`: tabelas e gráficos.
- `execucao_final/dados_auditaveis/`: dados detalhados do conjunto principal.
- `execucao_final/dados_triagem_minima/`: dados detalhados da análise de sensibilidade de seleção.
- `execucao_final/schemas/`: esquema informativo utilizado na validação.

As especificações originais e os arquivos intermediários de processamento não estão incluídos. Para executar novamente o estudo, obtenha o repositório de origem na revisão abaixo. Alguns resultados contêm análises adicionais que não necessariamente aparecem no artigo.

## Reprodução

Requisitos: Git, Python 3.11 e as dependências em `execucao_final/requirements.txt`. Execute os comandos abaixo no PowerShell, a partir da raiz deste repositório. Escolha uma pasta nova para as saídas.

```powershell
git clone https://github.com/APIs-guru/openapi-directory.git fonte-openapi
git -C fonte-openapi checkout f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49
python -m pip install -r execucao_final/requirements.txt
python -m unittest discover -s execucao_final/tests -v
$clone = 'fonte-openapi'
python execucao_final/scripts/selecionar.py $clone reproducao/selecao/inventario.csv
python execucao_final/scripts/elegibilidade.py $clone reproducao/selecao/inventario.csv reproducao/selecao/elegibilidade.csv 45
python execucao_final/scripts/validar_schema.py $clone reproducao/selecao/elegibilidade.csv execucao_final/schemas/openapi-3.0-2024-10-18.json reproducao/selecao/schema.csv 300
python execucao_final/scripts/extrair_amostra.py $clone reproducao/selecao/elegibilidade.csv reproducao/analise 120
python execucao_final/scripts/verificar_resultados.py reproducao/analise
python execucao_final/scripts/analise_ampliada.py reproducao/analise reproducao/resultados reproducao/selecao/schema.csv
python execucao_final/scripts/sensibilidade_definicao.py reproducao/analise reproducao/resultados reproducao/selecao/schema.csv
python execucao_final/scripts/resumir.py reproducao/analise reproducao/resultados reproducao/selecao/schema.csv
python execucao_final/scripts/graficos_exploratorios.py reproducao/resultados
python execucao_final/scripts/exportar_detalhes.py reproducao/analise reproducao/dados reproducao/selecao/schema.csv
```

Consulte o protocolo para detalhes dos filtros e limitações. Não reutilize caches de uma execução anterior com código diferente.

## Materiais de terceiros

O esquema OpenAPI e os dados derivados têm origem em materiais de terceiros. Antes de publicar, verifique as licenças e atribuições aplicáveis, inclusive aos dados derivados e ao esquema. Este repositório não concede direitos sobre os materiais de terceiros.
