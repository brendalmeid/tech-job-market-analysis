# Competências técnicas e menções à inteligência artificial em anúncios de desenvolvimento de software

## Objetivo

Investigar quais tecnologias são mencionadas em anúncios de desenvolvimento de software e áreas técnicas adjacentes e medir a proporção de anúncios com menção explícita a inteligência artificial (IA).

## Metodologia

A análise é exploratória e utiliza amostras de conveniência. Fontes efetivamente analisadas: Lever, ProgramaThor. Data(s) observada(s) da coleta, no horário de Brasília: 19/11/2026. O identificador do lote é `2026-11-19`.

O recorte histórico da ProgramaThor foi obtido por scraping HTML das duas primeiras páginas públicas. Foram mantidos os anúncios com cargo, empresa e etiquetas, sem selo de vaga externa e com URL única. A base legada fornecida ao novo pipeline contém apenas os 19 anúncios que passaram pela triagem original. O total de entradas analisadas neste lote contabiliza a base legada já filtrada e as respostas brutas da Lever.

A ampliação usa requisições paginadas à API pública Lever Postings, com verificação de robots.txt, intervalo entre chamadas e registro das respostas em JSON. Foram incluídos anúncios com título técnico e localização brasileira explícita no metadado de localização. O recorte técnico abrange desenvolvimento, engenharia de dados e IA, QA, arquitetura de software e DevOps. O quadro Jobgether foi consultado com o filtro de localização Brazil. A Jobgether intermedeia oportunidades, e o empregador final pode não ser identificado em seus anúncios. URLs, códigos de vaga e repetições exatas de título e descrição dentro do mesmo quadro foram usados para deduplicação. Repostagens entre quadros sem identificador comum podem permanecer.

No Pandas, cada tecnologia conta no máximo uma vez por anúncio. As etiquetas da ProgramaThor foram normalizadas com equivalências explícitas. Na Lever, um vocabulário fixo identifica tecnologias pelo título e pelo texto da descrição e das seções de requisitos. A identificação de IA registra separadamente evidências em título, etiquetas e descrição, quando disponíveis. Siglas curtas recebem tratamento contextual. Avisos conhecidos sobre IA no recrutamento e introduções institucionais recorrentes identificadas na CI&T e na Flex são removidos do texto analisado. Senioridade vem do título e modalidade vem dos metadados ou da indicação explícita na localização. Valores ausentes são registrados como não informados.

## Resultados

Foram recebidas **563 entradas** neste pipeline. **364** foram excluídas, restando **199 anúncios válidos**. A meta exploratória de 100 anúncios válidos foi atingida. O recorte anterior continha 19 anúncios válidos.

### Triagem e comparação entre fontes

| Fonte | Entradas | Excluídas | Válidas | Com menção a IA | % com menção |
| --- | --- | --- | --- | --- | --- |
| Lever | 544 | 364 | 180 | 97 | 53,89% |
| ProgramaThor | 19 | 0 | 19 | 3 | 15,79% |

| Fonte | Motivo de exclusão | Entradas |
| --- | --- | --- |
| Lever | Localização brasileira não indicada | 57 |
| Lever | Título fora do recorte técnico | 307 |

As taxas por fonte são descritivas. A base histórica utiliza títulos e etiquetas, enquanto a Lever fornece títulos e descrições. A diferença de cobertura pode afetar a probabilidade de detectar cada termo. Na Lever, Jobgether respondeu por 115 de 180 anúncios válidos.

### Competências mais frequentes

| Competência | Vagas | % da amostra |
| --- | --- | --- |
| API | 114 | 57,29% |
| CI/CD | 76 | 38,19% |
| AWS | 67 | 33,67% |
| Python | 67 | 33,67% |
| Azure | 64 | 32,16% |
| SQL | 60 | 30,15% |
| Java | 50 | 25,13% |
| Git | 46 | 23,12% |
| REST | 40 | 20,10% |
| Docker | 35 | 17,59% |

A etiqueta ou tecnologia com maior contagem foi API (114 vagas, 57,29%). O gráfico `competencias.png` ordena as dez maiores frequências e usa ordem alfabética em caso de empate. Os percentuais podem somar mais de 100%, pois cada anúncio pode mencionar várias tecnologias.

**Lever**

| Tecnologia | Vagas | % na fonte |
| --- | --- | --- |
| API | 109 | 60,56% |
| CI/CD | 75 | 41,67% |
| AWS | 67 | 37,22% |
| Python | 64 | 35,56% |
| Azure | 63 | 35,00% |

**ProgramaThor**

| Tecnologia | Vagas | % na fonte |
| --- | --- | --- |
| API | 5 | 26,32% |
| C# | 5 | 26,32% |
| MySQL | 5 | 26,32% |
| .NET | 4 | 21,05% |
| Git | 4 | 21,05% |

### Menções à IA

**100 de 199 anúncios (50,25%)** tiveram pelo menos uma menção explícita. A categoria «sem menção explícita» indica que o vocabulário não encontrou evidência nos campos disponíveis. A ausência de evidência textual não informa se o trabalho utiliza IA.

| Campo | Anúncios com campo disponível | Anúncios com menção no campo |
| --- | --- | --- |
| Título | 199 | 31 |
| Etiquetas | 19 | 1 |
| Descrição | 180 | 94 |

Uma mesma vaga pode contribuir em mais de um campo. O gráfico `mencoes_ia.png` mostra as duas categorias. O gráfico `tecnologias_por_grupo_ia.png`, quando há dois grupos, compara percentuais dentro de cada grupo para as dez tecnologias mais frequentes no total.

**Com menção** (n = 100)

| Tecnologia | Vagas | % no grupo |
| --- | --- | --- |
| API | 65 | 65,00% |
| Python | 46 | 46,00% |
| AWS | 43 | 43,00% |
| CI/CD | 40 | 40,00% |
| Azure | 30 | 30,00% |

**Sem menção explícita** (n = 99)

| Tecnologia | Vagas | % no grupo |
| --- | --- | --- |
| API | 49 | 49,49% |
| CI/CD | 36 | 36,36% |
| Azure | 34 | 34,34% |
| SQL | 30 | 30,30% |
| JavaScript | 26 | 26,26% |

### Perfil das vagas e tecnologias que aparecem juntas

| Senioridade | Vagas | % da amostra |
| --- | --- | --- |
| Sênior | 102 | 51,26% |
| Não informado | 74 | 37,19% |
| Pleno | 17 | 8,54% |
| Júnior | 4 | 2,01% |
| Pleno / Sênior | 2 | 1,01% |

| Modalidade | Vagas | % da amostra |
| --- | --- | --- |
| Remoto | 189 | 94,97% |
| Híbrido | 7 | 3,52% |
| Presencial | 3 | 1,51% |

| Par de tecnologias | Vagas | % da amostra |
| --- | --- | --- |
| API + CI/CD | 48 | 24,12% |
| Azure + CI/CD | 44 | 22,11% |
| API + Azure | 41 | 20,60% |
| API + REST | 40 | 20,10% |
| API + Java | 38 | 19,10% |
| API + SQL | 38 | 19,10% |
| API + AWS | 37 | 18,59% |
| API + Python | 37 | 18,59% |
| API + Git | 35 | 17,59% |
| AWS + Python | 32 | 16,08% |

A coocorrência mais frequente foi API + CI/CD (48 vagas, 24,12%). Cada par conta no máximo uma vez por anúncio. A presença simultânea de duas tecnologias descreve o texto do anúncio e pode incluir alternativas de ferramentas ou experiências desejáveis.

## Limitações e trabalhos futuros

As fontes e empresas foram escolhidas por conveniência. A concentração em alguns quadros de carreira, as diferenças entre etiquetas e descrições e a localização declarada limitam comparações e generalizações para o mercado brasileiro. Menções podem surgir no contexto da empresa, de responsabilidades ou de competências desejáveis. O vocabulário e o filtro por cargo podem deixar de detectar variações, e a deduplicação pode perder republicações com texto alterado. Não foi estimada precisão ou sensibilidade em uma amostra rotulada manualmente.

Trabalhos futuros podem ampliar o número de empregadores, acompanhar lotes ao longo do tempo, validar uma amostra manualmente e diferenciar requisitos obrigatórios, desejáveis e menções contextuais.

## Fontes e documentação

- [ProgramaThor — primeira página](https://programathor.com.br/jobs) e [segunda página](https://programathor.com.br/jobs/page/2).
- [Lever Postings API](https://github.com/lever/postings-api).
- A origem de cada resposta e sua data constam nos JSONs brutos. A coluna `pagina` permite rastrear cada anúncio.

## Uso de IA

O Codex auxiliou na revisão, implementação, testes e documentação do código. Os resultados quantitativos foram obtidos pela execução do pipeline sobre os anúncios reais.
