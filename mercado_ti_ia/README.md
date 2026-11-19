# Competências técnicas e IA em anúncios de desenvolvimento de software

Trabalho da optativa Mineração e Análise de Dados, Engenharia da Computação, UEMG. O projeto contém um recorte histórico levantado por scraping HTML da ProgramaThor e uma ampliação a partir de anúncios públicos da Lever.

## Instalação no Windows

Abra o PowerShell dentro da pasta interna `mercado_ti_ia` (onde está este README). Se a `.venv` já está pronta, use os comandos da próxima seção. Para criar um ambiente novo com Python funcional, use:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Versões testadas estão no `requirements.txt`. A execução deste lote usou CPython 3.15.2. No VS Code, selecione `.venv\Scripts\python.exe` como interpretador.

## Reproduzir a análise e rodar os testes

A análise usa as respostas já salvas e funciona sem internet:

```powershell
.\.venv\Scripts\python.exe -m analise.analisar_amostra --lote 2026-11-19
.\.venv\Scripts\python.exe -m unittest discover -s testes -v
```

Use `--sem-historico` para analisar apenas a Lever. Uma execução atualiza os resultados do lote escolhido e o `resultados_artigo.md` da raiz. O relatório desse lote é a fonte de tabelas e texto para o artigo no modelo SBC. As imagens PNG em 300 dpi estão em `graficos/ampliada-2026-11-19/`.

## Atualizar ou retomar a coleta

```powershell
.\.venv\Scripts\python.exe -m coleta.coletar_lever --lote 2026-11-19
.\.venv\Scripts\python.exe -m analise.analisar_amostra --lote 2026-11-19
```

Com o mesmo lote, o coletor reutiliza páginas registradas e continua na primeira página ausente de cada quadro. Para uma coleta em outra data, use um novo identificador AAAA-MM-DD nos dois comandos. A data de cada resposta é gravada no JSON. Um lote parcialmente retomado pode abranger mais de uma data e a API não fornece um snapshot transacional entre páginas. O parâmetro `--empresa` pode ser repetido para selecionar quadros específicos. O intervalo padrão é de dois segundos e pode ser aumentado com `--intervalo`.

O coletor verifica as regras de robots da API antes de buscar páginas novas, usa a paginação oficial e interrompe a execução ao receber HTTP 403, 429 ou outra falha HTTP. Consulte o `coleta.log` do lote e, se for apropriado, retome depois da resolução do erro ou do prazo indicado pela fonte. A coleta usa somente anúncios públicos. A opção `--html` do coletor histórico permite examinar cópias locais, mas o CSV original já está pronto e deve ser mantido como referência.

## Dados e rastreabilidade

| Caminho | Conteúdo |
| --- | --- |
| `dados/vagas_ti.csv` | Base histórica filtrada com 19 anúncios da ProgramaThor |
| `dados/brutos/lever/<lote>/` | Respostas originais da API, URL e horário UTC por página e log da execução |
| `dados/tratados/<lote>/auditoria.csv` | Uma linha por entrada reprocessada, com motivo de exclusão |
| `dados/tratados/<lote>/vagas_ti.csv` | Anúncios válidos com evidências de IA em campos separados |
| `graficos/ampliada-<lote>/` | Tabelas e PNGs do lote ampliado |
| `resultados_artigo.md` | Metodologia, tabelas, resultados, discussão e limitações do último lote analisado |

Os arquivos anteriores de `graficos/`, o artigo e os slides da primeira entrega correspondem ao recorte de 19 vagas e foram preservados. A base antiga já chegou filtrada ao novo pipeline. Por isso, a tabela de auditoria da ampliação não reconta os descartes da triagem original. Na Lever, a borda de coleta registra o quadro de publicação e deixa o nome do empregador ausente quando o anúncio intermediado não o identifica de forma estruturada.

## Fontes investigadas e decisões

- **ProgramaThor.** A pesquisa inicial percorreu duas páginas da listagem geral. Existem páginas por tecnologia e listagens com vagas vencidas, que mudariam o recorte. Os termos da plataforma restringem o uso dos dados para finalidades fora do serviço. Sem autorização específica, a ampliação não fez novas requisições a esse portal. Foi reutilizada somente a base histórica fornecida. [Listagem](https://programathor.com.br/jobs) · [FAQ](https://programathor.com.br/faq) · [Termos de serviço](https://programathor.com.br/terms/)
- **Lever.** A documentação pública permite coleta de anúncios publicados por terceiros. Os quadros consultados foram CI&T, dLocal, Flex, BriteCore e Jobgether. O quadro dLocal retornou uma lista vazia nesta consulta e não contribuiu com dados. A busca da Jobgether foi filtrada por localização Brazil. [Documentação Lever](https://github.com/lever/postings-api)
- **Outras bases comerciais.** A base comercial de anúncios brasileiros consultada exige contratação para obter o histórico. Ela não foi utilizada. [Techmap Brasil](https://jobdatafeeds.com/data/countries/br)

## Decisões de análise

A ampliação inclui títulos técnicos de software, QA, engenharia de dados, IA, arquitetura e infraestrutura de software com local brasileiro explícito. Modalidade e senioridade ausentes ficam em branco na base tratada e aparecem como “Não informado” nos agregados. A análise mede menções em títulos, etiquetas e descrições. Como a cobertura dos campos e os critérios de entrada variam entre as fontes, compare os resultados em caráter descritivo. As frequências por fonte ajudam a contextualizar os números agregados.

O comando `python` do sistema apontava para o atalho da Microsoft Store neste ambiente. As execuções foram verificadas com o executável explícito da `.venv`. O coletor salva as páginas incrementalmente para que uma falha de rede não obrigue a baixar aquelas já registradas. Os testes cobrem a retomada local, robots.txt, exclusões, normalização, detecção de siglas ambíguas e geração de resultados.

## Uso de IA

O Codex apoiou a revisão, implementação, testes e documentação do código. Os resultados quantitativos foram calculados pelo pipeline a partir dos dados reais registrados.

