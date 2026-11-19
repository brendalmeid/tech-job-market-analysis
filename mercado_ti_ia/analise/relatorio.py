"""Gera texto e tabelas do artigo usando somente os resultados processados."""
import pandas as pd


def percentual(x):
    return f"{x:.2f}".replace(".", ",") + "%" if pd.notna(x) else "—"


def tabela(df, colunas, titulos):
    linhas = ["| " + " | ".join(titulos) + " |", "| " + " | ".join(["---"] * len(colunas)) + " |"]
    for valores in df[colunas].itertuples(index=False, name=None):
        celulas = [percentual(v) if "percentual" in c else str(v).replace("|", r"\|")
                   for c, v in zip(colunas, valores)]
        linhas.append("| " + " | ".join(celulas) + " |")
    return "\n".join(linhas)


def destaque(df, campo):
    if df.empty:
        return "Não houve registros suficientes para interpretar esta distribuição."
    linha = df.iloc[0]
    return f"{linha[campo]} ({linha['vagas']} vagas, {percentual(linha['percentual'])})"


def gerar_relatorio(base, auditoria, t, lote):
    n = len(base)
    positivos = int(base["mencao_ia"].sum())
    total = len(auditoria)
    tecn = t["frequencias"].head(10)
    datas = sorted(set(pd.to_datetime(auditoria["coletado_em"], format="ISO8601", utc=True)
                       .dt.tz_convert("America/Sao_Paulo")
                       .where(auditoria["coletado_em"].str.contains("T"))
                       .dt.strftime("%d/%m/%Y").dropna()))
    if auditoria["fonte"].eq("ProgramaThor").any():
        datas = sorted(set(datas + ["19/11/2026"]))
    origens = ", ".join(t["por_fonte"]["fonte"])
    por_empresa = t["por_quadro"]
    lever = por_empresa.loc[por_empresa["fonte"].eq("Lever")].sort_values("vagas", ascending=False)
    concentracao = ""
    if not lever.empty:
        maior = lever.iloc[0]
        concentracao = f" Na Lever, {maior['quadro']} respondeu por {maior['vagas']} de {lever['vagas'].sum()} anúncios válidos."
    comparacao = "\n\n".join(
        "**" + grupo + "** (n = " + str(df.iloc[0]["denominador"]) + ")\n\n"
        + tabela(df.head(5), ["competencia", "vagas", "percentual"], ["Tecnologia", "Vagas", "% no grupo"])
        for grupo, df in t["tecnologias_por_grupo_ia"].groupby("grupo")
    )
    ranking_fonte = "\n\n".join(
        f"**{fonte}**\n\n" + tabela(df.head(5), ["competencia", "vagas", "percentual"],
                                   ["Tecnologia", "Vagas", "% na fonte"])
        for fonte, df in t["tecnologias_por_fonte"].groupby("fonte")
    )
    meta = "A meta exploratória de 100 anúncios válidos foi atingida." if n >= 100 else "A meta exploratória de 100 anúncios válidos não foi atingida."
    return f"""# Competências técnicas e menções à inteligência artificial em anúncios de desenvolvimento de software

## Objetivo

Investigar quais tecnologias são mencionadas em anúncios de desenvolvimento de software e áreas técnicas adjacentes e medir a proporção de anúncios com menção explícita a inteligência artificial (IA).

## Metodologia

A análise é exploratória e utiliza amostras de conveniência. Fontes efetivamente analisadas: {origens}. Data(s) observada(s) da coleta, no horário de Brasília: {', '.join(datas)}. O identificador do lote é `{lote}`.

O recorte histórico da ProgramaThor foi obtido por scraping HTML das duas primeiras páginas públicas. Foram mantidos os anúncios com cargo, empresa e etiquetas, sem selo de vaga externa e com URL única. A base legada fornecida ao novo pipeline contém apenas os 19 anúncios que passaram pela triagem original. O total de entradas analisadas neste lote contabiliza a base legada já filtrada e as respostas brutas da Lever.

A ampliação usa requisições paginadas à API pública Lever Postings, com verificação de robots.txt, intervalo entre chamadas e registro das respostas em JSON. Foram incluídos anúncios com título técnico e localização brasileira explícita no metadado de localização. O recorte técnico abrange desenvolvimento, engenharia de dados e IA, QA, arquitetura de software e DevOps. O quadro Jobgether foi consultado com o filtro de localização Brazil. A Jobgether intermedeia oportunidades, e o empregador final pode não ser identificado em seus anúncios. URLs, códigos de vaga e repetições exatas de título e descrição dentro do mesmo quadro foram usados para deduplicação. Repostagens entre quadros sem identificador comum podem permanecer.

No Pandas, cada tecnologia conta no máximo uma vez por anúncio. As etiquetas da ProgramaThor foram normalizadas com equivalências explícitas. Na Lever, um vocabulário fixo identifica tecnologias pelo título e pelo texto da descrição e das seções de requisitos. A identificação de IA registra separadamente evidências em título, etiquetas e descrição, quando disponíveis. Siglas curtas recebem tratamento contextual. Avisos conhecidos sobre IA no recrutamento e introduções institucionais recorrentes identificadas na CI&T e na Flex são removidos do texto analisado. Senioridade vem do título e modalidade vem dos metadados ou da indicação explícita na localização. Valores ausentes são registrados como não informados.

## Resultados

Foram recebidas **{total} entradas** neste pipeline. **{total - n}** foram excluídas, restando **{n} anúncios válidos**. {meta} O recorte anterior continha 19 anúncios válidos.

### Triagem e comparação entre fontes

{tabela(t["por_fonte"], ["fonte", "coletadas", "excluidas", "validas", "com_ia", "percentual_ia"], ["Fonte", "Entradas", "Excluídas", "Válidas", "Com menção a IA", "% com menção"])}

{tabela(t["exclusoes"], ["fonte", "motivos", "vagas"], ["Fonte", "Motivo de exclusão", "Entradas"])}

As taxas por fonte são descritivas. A base histórica utiliza títulos e etiquetas, enquanto a Lever fornece títulos e descrições. A diferença de cobertura pode afetar a probabilidade de detectar cada termo.{concentracao}

### Competências mais frequentes

{tabela(tecn, ["competencia", "vagas", "percentual"], ["Competência", "Vagas", "% da amostra"])}

A etiqueta ou tecnologia com maior contagem foi {destaque(tecn, 'competencia')}. O gráfico `competencias.png` ordena as dez maiores frequências e usa ordem alfabética em caso de empate. Os percentuais podem somar mais de 100%, pois cada anúncio pode mencionar várias tecnologias.

{ranking_fonte}

### Menções à IA

**{positivos} de {n} anúncios ({percentual(100 * positivos / n)})** tiveram pelo menos uma menção explícita. A categoria «sem menção explícita» indica que o vocabulário não encontrou evidência nos campos disponíveis. A ausência de evidência textual não informa se o trabalho utiliza IA.

{tabela(t["campos_ia"], ["campo", "disponiveis", "com_mencao"], ["Campo", "Anúncios com campo disponível", "Anúncios com menção no campo"])}

Uma mesma vaga pode contribuir em mais de um campo. O gráfico `mencoes_ia.png` mostra as duas categorias. O gráfico `tecnologias_por_grupo_ia.png`, quando há dois grupos, compara percentuais dentro de cada grupo para as dez tecnologias mais frequentes no total.

{comparacao}

### Perfil das vagas e tecnologias que aparecem juntas

{tabela(t["senioridade"], ["senioridade", "vagas", "percentual"], ["Senioridade", "Vagas", "% da amostra"])}

{tabela(t["modalidade"], ["modalidade", "vagas", "percentual"], ["Modalidade", "Vagas", "% da amostra"])}

{tabela(t["coocorrencias"].head(10), ["par", "vagas", "percentual"], ["Par de tecnologias", "Vagas", "% da amostra"])}

A coocorrência mais frequente foi {destaque(t["coocorrencias"], 'par')}. Cada par conta no máximo uma vez por anúncio. A presença simultânea de duas tecnologias descreve o texto do anúncio e pode incluir alternativas de ferramentas ou experiências desejáveis.

## Limitações e trabalhos futuros

As fontes e empresas foram escolhidas por conveniência. A concentração em alguns quadros de carreira, as diferenças entre etiquetas e descrições e a localização declarada limitam comparações e generalizações para o mercado brasileiro. Menções podem surgir no contexto da empresa, de responsabilidades ou de competências desejáveis. O vocabulário e o filtro por cargo podem deixar de detectar variações, e a deduplicação pode perder republicações com texto alterado. Não foi estimada precisão ou sensibilidade em uma amostra rotulada manualmente.

Trabalhos futuros podem ampliar o número de empregadores, acompanhar lotes ao longo do tempo, validar uma amostra manualmente e diferenciar requisitos obrigatórios, desejáveis e menções contextuais.

## Fontes e documentação

- [ProgramaThor — primeira página](https://programathor.com.br/jobs) e [segunda página](https://programathor.com.br/jobs/page/2).
- [Lever Postings API](https://github.com/lever/postings-api).
- A origem de cada resposta e sua data constam nos JSONs brutos. A coluna `pagina` permite rastrear cada anúncio.

## Uso de IA

O Codex auxiliou na revisão, implementação, testes e documentação do código. Os resultados quantitativos foram obtidos pela execução do pipeline sobre os anúncios reais.
"""

