# Reuso em especificações OpenAPI

Este repositório contém os artefatos de um estudo empírico e descritivo sobre o uso de componentes e referências em especificações OpenAPI disponibilizadas pelo catálogo [APIs.guru](https://github.com/APIs-guru/openapi-directory).

A coleta e o processamento foram realizados entre 22 e 23 de novembro de 2026. O conjunto principal da análise contém 1.617 especificações OpenAPI 3.0.x.

## Fonte dos dados

As especificações foram obtidas a partir de uma cópia local do repositório:

https://github.com/APIs-guru/openapi-directory

A revisão exata utilizada foi:

```text
f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49
```

Esse identificador corresponde ao **commit Git** do repositório de origem. Para reproduzir o estudo, é necessário utilizar essa revisão, pois versões posteriores do catálogo podem conter documentos diferentes.

Os arquivos originais das especificações não estão incluídos neste repositório. Seus caminhos e hashes SHA-256 estão registrados no inventário em `execucao_final/selecao/`.

## Objetivo e definição de reuso

O estudo investiga a frequência de referências, as categorias de componentes definidos e a variação do reuso entre especificações OpenAPI.

Foram consideradas quatro categorias de componentes:

- `schemas`;
- `parameters`;
- `responses`;
- `requestBodies`.

A análise principal contabiliza referências internas diretas a componentes inteiros dessas categorias, quando o destino existe e é compatível com a posição da referência.

Neste estudo:

- **Componente definido:** uma entrada declarada em uma das quatro categorias.
- **Componente referenciado:** um componente com pelo menos uma referência direta válida.
- **Componente reutilizado:** um componente com referências diretas válidas em pelo menos duas posições distintas.

Referências em posições distintas não demonstram necessariamente o uso do componente por operações diferentes. A análise também não mede diretamente o reuso de código na implementação das APIs.

Após uma análise inicial dos dados, o procedimento foi aperfeiçoado e os critérios de seleção e análise foram definidos. Em seguida, as especificações foram processadas novamente com o procedimento estabelecido.

## Seleção das especificações

As versões foram agrupadas por identificação de API. Para cada grupo, foi selecionada a versão indicada como preferida. Quando havia apenas uma versão sem indicação de preferência, ela também era selecionada, desde que seus metadados pudessem ser lidos.

Foram considerados documentos que:

1. Declarassem uma versão OpenAPI 3.0.x.
2. Pudesse ser lidos pelo procedimento de análise.
3. Apresentassem pelo menos uma operação HTTP.
4. Fossem aprovados na verificação estrutural baseada no esquema OpenAPI 3.0.

A presença de componentes ou referências não foi exigida.

O processo resultou em:

| Etapa | Quantidade |
|---|---:|
| Versões identificadas no inventário | 4.138 |
| Grupos de APIs | 2.658 |
| Especificações candidatas | 2.654 |
| Documentos aprovados na triagem inicial | 1.619 |
| Documentos aprovados na verificação estrutural | 1.617 |

Os critérios completos e os registros de seleção estão disponíveis em `execucao_final/PROTOCOLO.md` e `execucao_final/selecao/`.

## Conteúdo do repositório

- `execucao_final/PROTOCOLO.md`: critérios, métricas, procedimentos e limitações.
- `execucao_final/RELATORIO.md`: resultados das análises realizadas.
- `execucao_final/CONGELAMENTO.json`: revisão da fonte, versões das dependências e hashes dos arquivos congelados.
- `execucao_final/CONTROLE_QUALIDADE.json`: registros das verificações realizadas.
- `execucao_final/requirements.txt`: dependências Python.
- `execucao_final/scripts/`: scripts de seleção, validação, extração e análise.
- `execucao_final/tests/`: testes automatizados.
- `execucao_final/selecao/`: inventário, triagem e verificação estrutural.
- `execucao_final/resultados/`: tabelas e gráficos gerados.
- `execucao_final/dados_auditaveis/`: dados detalhados do conjunto principal.
- `execucao_final/dados_triagem_minima/`: dados detalhados da análise de sensibilidade de seleção.
- `execucao_final/schemas/`: esquema informativo utilizado na validação.

## Ambiente utilizado

A execução registrada utilizou:

- **Python:** 3.11.0
- **PyYAML:** 6.0.3
- **jsonschema:** 4.26.0
- **matplotlib:** 3.11.0

A verificação estrutural utilizou o esquema informativo OpenAPI 3.0 publicado em 18 de outubro de 2024, com JSON Schema Draft 4 e sem verificação automática de formatos.

O arquivo do esquema está disponível em:

```text
execucao_final/schemas/openapi-3.0-2024-10-18.json
```

Seu hash SHA-256 é:

```text
2385f5bbb8c37878daae73baeabe7f34b2f022a4a8c049329ee61f71796f039c
```

A verificação estrutural não garante, por si só, a conformidade semântica integral dos documentos.

## Reprodução

Os comandos abaixo foram preparados para **PowerShell no Windows**. Eles devem ser executados a partir da raiz deste repositório.

A execução completa pode levar tempo, pois envolve a leitura e a análise de milhares de documentos. Utilize uma pasta nova para as saídas e não reaproveite arquivos intermediários de uma execução anterior.

### 1. Obter a fonte dos dados

```powershell
git clone https://github.com/APIs-guru/openapi-directory.git fonte-openapi
git -C fonte-openapi checkout f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49
git -C fonte-openapi rev-parse HEAD
```

O último comando deve apresentar:

```text
f04b8d0bcd39c52e1cf3ad7a5fe744709832ae49
```

### 2. Instalar as dependências

Com Python 3.11 disponível:

```powershell
python --version
python -m pip install -r execucao_final/requirements.txt
```

Para verificar a implementação antes de executar a análise:

```powershell
python -m unittest discover -s execucao_final/tests -v
```

A execução registrada passou em 36 testes automatizados.

### 3. Selecionar e validar as especificações

```powershell
$clone = 'fonte-openapi'

python execucao_final/scripts/selecionar.py $clone reproducao/selecao/inventario.csv

python execucao_final/scripts/elegibilidade.py $clone reproducao/selecao/inventario.csv reproducao/selecao/elegibilidade.csv 45

python execucao_final/scripts/validar_schema.py $clone reproducao/selecao/elegibilidade.csv execucao_final/schemas/openapi-3.0-2024-10-18.json reproducao/selecao/schema.csv 300
```

Esses comandos recriam o inventário, a triagem inicial e a verificação estrutural. Os valores `45` e `300` representam os limites de tempo, em segundos, usados nas etapas correspondentes.

### 4. Extrair e conferir os dados

```powershell
python execucao_final/scripts/extrair_amostra.py $clone reproducao/selecao/elegibilidade.csv reproducao/analise 120

python execucao_final/scripts/verificar_resultados.py reproducao/analise
```

A extração é realizada sobre os documentos aprovados na triagem inicial. O arquivo de verificação estrutural é aplicado nas etapas seguintes para gerar os resultados do conjunto principal.

O arquivo `reproducao/analise/verificacao.json` registra verificações de consistência dos dados extraídos. Consulte também `reproducao/analise/processamento.csv` para identificar eventuais falhas ou limites de tempo.

### 5. Gerar os resultados principais

```powershell
python execucao_final/scripts/analise_ampliada.py reproducao/analise reproducao/resultados/principal reproducao/selecao/schema.csv

python execucao_final/scripts/sensibilidade_definicao.py reproducao/analise reproducao/resultados/principal reproducao/selecao/schema.csv

python execucao_final/scripts/resumir.py reproducao/analise reproducao/resultados/principal reproducao/selecao/schema.csv

python execucao_final/scripts/graficos_exploratorios.py reproducao/resultados/principal
```

As tabelas e os gráficos serão gravados em:

```text
reproducao/resultados/principal/
```

### 6. Exportar os dados detalhados

```powershell
python execucao_final/scripts/exportar_detalhes.py reproducao/analise reproducao/dados_auditaveis reproducao/selecao/schema.csv
```

Essa etapa gera arquivos compactados com os componentes e as referências identificados no conjunto principal.

## Conferência dos resultados

Na execução registrada, os principais resultados foram:

| Indicador | Resultado |
|---|---:|
| Especificações analisadas | 1.617 |
| Documentos com pelo menos uma referência válida | 1.472 |
| Documentos sem referências válidas | 145 |
| Referências válidas | 782.302 |
| Componentes definidos | 168.421 |
| Componentes reutilizados em pelo menos duas posições | 59.781 |
| Documentos com componentes definidos | 1.489 |
| Mediana da proporção de componentes reutilizados | 37,5% |

Os resultados do conjunto principal podem ser consultados em `execucao_final/resultados/principal/`.

Caso uma nova execução apresente diferenças, verifique a revisão do repositório de origem, as versões das dependências, os registros de processamento, os limites de tempo e os arquivos gerados em cada etapa.

## Materiais de terceiros

As especificações de origem, o esquema OpenAPI e os dados derivados envolvem materiais de terceiros. Consulte as licenças e atribuições aplicáveis às fontes antes de redistribuir ou reutilizar esses materiais.
