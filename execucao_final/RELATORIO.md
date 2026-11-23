# Resultados finais da execução sobre o clone APIs.guru

Esta execução congelou fonte, esquema e scripts antes de reprocessar os arquivos. Ela contém sete análises observacionais complementares do **mesmo corpus**; não são sete amostras independentes nem experimentos controlados. Como as perguntas e regras foram consolidadas após uma exploração inicial, os resultados são finais para esta execução e **exploratórios**, não testes confirmatórios pré-registrados. Nenhuma medida demonstra qualidade ou causalidade.

## Base e seleção

O clone foi verificado sem alterações locais na revisão `f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49`. O inventário recomposto tem 4.138 versões em 2.658 grupos de API. Foram selecionadas 2.654 candidatas, com quatro grupos sem escolha automática. Na triagem mínima, 1.619 documentos passaram, 1.034 foram excluídos (1.030 por versão e quatro sem operação detectada) e um permaneceu com erro de leitura. Dos 1.619, dois não passaram no esquema estrutural OpenAPI; o corpus principal tem **1.617 documentos**. O conjunto de 1.619 é mantido para sensibilidade. A fonte é o clone, não todas as APIs REST.

O esquema informativo valida estrutura segundo o JSON Schema adotado, sem verificação automática de formatos nem garantia de validade semântica. As regras, status, versões, hashes e limitações estão no [protocolo](PROTOCOLO.md) e em `selecao/`.

## Experimento 1 — Frequência de referências

Dos 1.617 documentos, **1.472 (91,03%)** têm ao menos uma referência central direta válida. Foram 782.302 ocorrências no total. Por documento, a mediana foi 79, com quartis 16,0 e 376,0; a média foi 483,8, influenciada por documentos grandes. O denominador inclui documentos sem referências.

## Experimento 2 — Componentes definidos e uso por categoria

A tabela usa como denominador **componentes definidos dentro de cada categoria**, não documentos. Referenciado uma vez e reutilizado em pelo menos dois locais são grupos distintos.

| Categoria | Definidos | Sem referência | Uma referência | Duas ou mais | Percentual com duas ou mais |
|---|---:|---:|---:|---:|---:|
| schemas | 152.205 | 15.326 | 88.240 | 48.639 | 31,96% |
| parameters | 9.361 | 212 | 1.079 | 8.070 | 86,21% |
| responses | 6.091 | 1.412 | 2.197 | 2.482 | 40,75% |
| requestBodies | 764 | 38 | 136 | 590 | 77,23% |

No total há 168.421 definições: 16.988 sem referência, 91.652 com uma e 59.781 com duas ou mais. As medianas por documento, que têm outra ponderação, estão em `resultados/principal/categorias_por_documento.csv`.

## Experimento 3 — Variação entre documentos

Dos 1.617 documentos, 128 não têm componentes e possuem proporção de reuso não aplicável. Nos **1.489** restantes, a mediana do percentual foi **37,5%**, com quartis de 25,58% e 55,56% e intervalo observado de 0% a 100%. O documento mediano contém 14 operações. O valor de 100% pode se referir a um documento com poucos componentes.

## Experimento 4 — Sensibilidade da definição de reuso

Na regra principal, consideram-se posições estruturais em todo o documento. Se forem contadas apenas as referências no trecho `paths`, a mediana do percentual por documento muda de **37,5% para 20,0%**, e 1.027 documentos mudam o número de componentes classificados como reutilizados. Estar em `paths` não prova uso em operações distintas.

Foram identificadas 265 autorreferências diretas. Ao excluir somente essas ocorrências, o número agregado de componentes reutilizados passa de 59.781 para 59.692; 53 documentos mudam. Isso não detecta todos os ciclos.

## Experimento 5 — Concentração e extremos

A especificação com mais referências concentra 13,37% das ocorrências centrais. As **17** maiores, cerca de 1% do conjunto, concentram **32,27%**. Ao omiti-las apenas numa análise de sensibilidade, a mediana de referências muda de 79 para 77; a mediana de reuso passa de 37,5% para 37,5%. Esses documentos permanecem na análise principal.

## Experimento 6 — Associações descritivas

Coeficientes de Spearman com postos médios para empates: operacoes × referencias: 0,742; definidos × referencias: 0,952; operacoes × definidos: 0,710. Foram usados os 1.617 documentos; não foram aplicados testes de significância. As associações não demonstram causa, qualidade nem generalização a outras fontes.

## Experimento 7 — Sensibilidade de seleção e fonte

Com os **1.619** documentos da triagem mínima, o total com ao menos uma referência é 1.473 (90,98%); no subconjunto filtrado pelo esquema, é 1.472 (91,03%). A mediana de reuso aplicável foi 37,5% no subconjunto principal; consulte `resultados/triagem_minima/` para os demais indicadores.

A comparação abaixo usa o índice REST obtido depois do clone. Ela compara **nomes de versões**, não verifica se os arquivos das fontes são idênticos; diferenças de grupo ou versão não têm causa presumida. Os percentuais e medianas são descritivos dos subconjuntos.

| Comparação com o índice | Documentos | Com referências | Mediana de referências | Mediana de reuso aplicável |
|---|---:|---:|---:|---:|
| ausente no indice | 122 | 97,54% | 353,0 | 37,9% |
| mesma versao | 1.397 | 90,05% | 68,0 | 37,5% |
| versao diferente | 98 | 96,94% | 69,5 | 38,6% |

## Qualidade, reprodutibilidade e limites

A execução usou os scripts e o esquema identificados em `CONGELAMENTO.json`. A extração, a conferência de somas e a auditoria textual de sete arquivos estão em `analise/` e `selecao/`. Os testes sintéticos e as verificações reduzem riscos, mas não garantem cobertura integral da semântica OpenAPI. O estudo foi refinado após observar resultados prévios; não apresentar estes resultados como pré-registrados, experimentos causais ou uma amostra representativa de todas as APIs.

Os dados por documento, componentes e ocorrências de referências, tabelas e gráficos estão nas pastas do pacote. Os documentos originais devem ser obtidos novamente da revisão registrada; verificar direitos e licenças antes de redistribuir dados de origem ou derivados.
