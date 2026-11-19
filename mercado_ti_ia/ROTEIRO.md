# Roteiro de apresentação — 10 a 12 minutos

Abra **apresentacao.pdf** em tela cheia. As seis páginas correspondem aos tópicos abaixo.

## 1. Contexto — 1 min

“Quando uma empresa anuncia uma vaga, ela dá pistas do perfil técnico que procura. O nosso recorte usa anúncios de desenvolvimento de software para observar quais competências aparecem e como a IA entra nessas vagas.”

## 2. Pergunta e fonte — 1 a 2 min

“Perguntamos quais etiquetas são mais frequentes e qual parcela das vagas menciona IA. Escolhemos a ProgramaThor por disponibilizar cartões de vagas com etiquetas técnicas e paginação pública. Trabalhamos com as duas primeiras páginas em 19 de novembro de 2026.”

## 3. Demonstração do pipeline — 2 a 3 min

Mostre o arquivo `dados/vagas_ti.csv`. Aponte cargo, empresa, local, competências, URL do anúncio e página de origem. Se quiser mostrar o código, abra `coleta/scraper.py` em `extrair_vagas` e `analise/analisar_vagas.py` em `analisar`.

“O BeautifulSoup extrai os cartões. Excluímos os marcados como externos e usamos URL para evitar contar o mesmo anúncio duas vezes. Foram 12 vagas elegíveis na primeira página e 7 na segunda. O Pandas conta cada etiqueta uma vez por vaga. Para IA, um anúncio vale um positivo quando encontramos pelo menos um termo explícito no título ou nas etiquetas.”

## 4. Gráfico — 2 min

“A barra mede número de anúncios. API, C# e MySQL aparecem em cinco dos 19, ou 26,32% cada. Git, JavaScript e Node.js estão entre as etiquetas com quatro ocorrências. Como uma vaga pode ter várias etiquetas, os percentuais podem somar mais de 100%. O gráfico mostra as primeiras oito etiquetas por frequência, com desempate alfabético.”

## 5. IA na amostra — 2 min

“Encontramos três anúncios com menções explícitas a IA, 15,79%. Dois casos aparecem no título, em vagas de AI Engineer e de engenharia de machine learning. No terceiro, uma vaga full stack traz a etiqueta AI Agents. Se tivéssemos olhado apenas os títulos, esse terceiro caso passaria despercebido.”

## 6. Conclusão e perguntas — 2 min

“Na amostra, as competências mais frequentes foram API, C# e MySQL. A presença de IA apareceu tanto em cargos especializados quanto como uma etiqueta em uma vaga de desenvolvimento. O recorte é pequeno e de uma única data e plataforma. Uma extensão seria analisar as descrições completas e comparar diferentes semanas.”

**Se perguntarem se 15,79% vale para o Brasil:** o percentual é 3 ÷ 19 na amostra observada. O estudo usou uma amostra de conveniência de um portal.

**Se perguntarem se as competências são requisitos:** medimos etiquetas e termos visíveis. Para classificar um termo como requisito, seria preciso ler a seção de requisitos do anúncio.

**Se perguntarem sobre o uso de IA no trabalho:** o Codex apoiou a implementação, a revisão e a produção dos materiais. Os números vêm do código executado sobre as páginas coletadas.

