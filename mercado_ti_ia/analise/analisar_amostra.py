"""Gera tabelas, gráficos e texto acadêmico para um lote reproduzível."""
import argparse
from datetime import date
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

if __package__:
    from .preparar_vagas import preparar
    from .relatorio import gerar_relatorio
else:
    from preparar_vagas import preparar
    from relatorio import gerar_relatorio

RAIZ = Path(__file__).resolve().parents[1]
CORES = ["#176b87", "#ab5427"]


def frequencia(valores, total, nome):
    contagem = valores.value_counts()
    tabela = contagem.rename_axis(nome).reset_index(name="vagas")
    tabela["percentual"] = (100 * tabela["vagas"] / total).round(2) if total else 0.0
    return tabela.sort_values(["vagas", nome], ascending=[False, True], ignore_index=True)


def salvar(tabela, pasta, nome):
    tabela.to_csv(pasta / f"{nome}.csv", index=False, encoding="utf-8-sig")


def marcar_barras(ax, serie, nomes, titulo, eixo="Número de vagas", sufixo=""):
    barras = ax.barh(nomes, serie, color=CORES[0])
    ax.bar_label(barras, labels=[f"{valor:g}{sufixo}" for valor in serie], padding=4)
    ax.set(xlabel=eixo, title=titulo, xlim=(0, max(max(serie, default=0) * 1.18, 1)))
    ax.invert_yaxis()


def salvar_figura(fig, pasta, nome):
    fig.tight_layout()
    fig.savefig(pasta / f"{nome}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def barras(tabela, chave, titulo, pasta, nome, limite=10):
    if tabela.empty:
        return
    topo = tabela.head(limite)
    fig, ax = plt.subplots(figsize=(8, max(3, 1.5 + len(topo) * 0.35)))
    marcar_barras(ax, topo["vagas"], topo[chave], titulo)
    salvar_figura(fig, pasta, nome)


def calcular(auditoria, base, pasta):
    n = len(base)
    validas = auditoria["motivos"].eq("")
    fontes = auditoria.assign(validas=validas.astype(int)).groupby("fonte").agg(
        coletadas=("url", "size"), validas=("validas", "sum")).reset_index()
    fontes["excluidas"] = fontes["coletadas"] - fontes["validas"]
    ia_fontes = base.groupby("fonte")["mencao_ia"].sum()
    fontes["com_ia"] = fontes["fonte"].map(ia_fontes).fillna(0).astype(int)
    fontes["percentual_ia"] = (100 * fontes["com_ia"] / fontes["validas"].where(fontes["validas"].ne(0))).round(2)
    exclusoes = (auditoria.loc[~validas].groupby(["fonte", "motivos"]).size()
                 .rename("vagas").reset_index())
    empresas = (base.assign(empresa=base["empresa"].replace("", "Não informado"))
                .groupby(["fonte", "empresa"]).size().rename("vagas").reset_index())
    quadros = base.groupby(["fonte", "quadro"]).size().rename("vagas").reset_index()
    grupos = base["mencao_ia"].map({True: "Com menção", False: "Sem menção explícita"})
    ia = frequencia(grupos, n, "grupo")
    campos = pd.DataFrame({"campo": ["Título", "Etiquetas", "Descrição"],
                           "disponiveis": [n, int(base["etiquetas"].ne("").sum()), int(base["tem_descricao"].sum())],
                           "com_mencao": [int(base[col].ne("").sum()) for col in ("ia_titulo", "ia_etiquetas", "ia_descricao")]})
    listas = base["competencias"].map(lambda texto: texto.split("; ") if texto else [])
    tags = listas.explode().dropna()
    tecn = frequencia(tags, n, "competencia")
    por_fonte = []
    for fonte, vagas in base.groupby("fonte"):
        tabela = frequencia(tags[tags.index.isin(vagas.index)], len(vagas), "competencia")
        por_fonte.append(tabela.assign(fonte=fonte))
    grupos_tec = []
    for grupo, linhas in grupos.groupby(grupos):
        frequencias = frequencia(tags[tags.index.isin(linhas.index)], len(linhas), "competencia")
        grupos_tec.append(frequencias.assign(grupo=grupo, denominador=len(linhas)))
    comparacao = pd.concat(grupos_tec, ignore_index=True)
    pares = pd.Series([" + ".join(par) for tags_vaga in listas
                       for par in combinations(sorted(tags_vaga, key=str.casefold), 2)], dtype=str)
    cooc = frequencia(pares, n, "par")
    cooc = cooc.loc[cooc["vagas"].ge(2)]
    nivel = frequencia(base["senioridade"].replace("", "Não informado"), n, "senioridade")
    modalidade = frequencia(base["modalidade"].replace("", "Não informado"), n, "modalidade")
    tabelas = {"por_fonte": fontes, "por_empresa": empresas, "por_quadro": quadros, "exclusoes": exclusoes,
               "frequencias": tecn, "tecnologias_por_fonte": pd.concat(por_fonte, ignore_index=True),
               "mencoes_ia": ia, "campos_ia": campos, "tecnologias_por_grupo_ia": comparacao,
               "senioridade": nivel, "modalidade": modalidade, "coocorrencias": cooc}
    for nome, tabela in tabelas.items():
        salvar(tabela, pasta, nome)

    barras(tecn, "competencia", "Dez competências mais mencionadas", pasta, "competencias")
    fig, ax = plt.subplots(figsize=(8, 3))
    marcar_barras(ax, ia["percentual"], ia["grupo"], "Menção explícita à inteligência artificial",
                  "Percentual das vagas válidas", "%")
    salvar_figura(fig, pasta, "mencoes_ia")
    if base["senioridade"].ne("").any():
        barras(nivel, "senioridade", "Senioridade indicada no título", pasta, "senioridade")
    if base["modalidade"].ne("").any():
        barras(modalidade, "modalidade", "Modalidade indicada no anúncio", pasta, "modalidade")
    barras(cooc, "par", "Pares de tecnologias que aparecem juntos", pasta, "coocorrencias")
    if grupos.nunique() == 2 and not comparacao.empty:
        ordem = tecn.head(10)["competencia"]
        pivot = comparacao.pivot(index="competencia", columns="grupo", values="percentual")
        pivot = pivot.reindex(ordem).fillna(0).iloc[::-1]
        fig, ax = plt.subplots(figsize=(9, 6))
        pivot.plot.barh(ax=ax, color=CORES, width=0.75)
        for barras_ax in ax.containers:
            ax.bar_label(barras_ax, labels=[f"{valor:.1f}%" if valor else "" for valor in barras_ax.datavalues],
                         fontsize=7, padding=3)
        rotulos = [f"{grupo} (n={int(grupos.eq(grupo).sum())})" for grupo in pivot.columns]
        ax.legend(rotulos, loc="lower right")
        ax.set(xlabel="Percentual dentro de cada grupo", ylabel="", xlim=(0, 115),
               title="Competências por presença de menção explícita a IA")
        salvar_figura(fig, pasta, "tecnologias_por_grupo_ia")
    return tabelas


def executar(lote, incluir_historico):
    auditoria, base = preparar(RAIZ, lote, incluir_historico)
    if base.empty:
        raise ValueError("Não há anúncios válidos para análise.")
    identificador = lote if incluir_historico else f"{lote}-lever"
    dados = RAIZ / "dados" / "tratados" / identificador
    graficos = RAIZ / "graficos" / f"ampliada-{identificador}"
    dados.mkdir(parents=True, exist_ok=True)
    graficos.mkdir(parents=True, exist_ok=True)
    salvar(auditoria, dados, "auditoria")
    salvar(base, dados, "vagas_ti")
    salvar(base.loc[base["mencao_ia"]], dados, "vagas_com_ia")
    tabelas = calcular(auditoria, base, graficos)
    texto = gerar_relatorio(base, auditoria, tabelas, lote)
    relatorio = RAIZ / "resultados_artigo.md" if incluir_historico else graficos / "resultados_artigo.md"
    relatorio.write_text(texto, encoding="utf-8")
    print(tabelas["por_fonte"].to_string(index=False))
    print(tabelas["mencoes_ia"].to_string(index=False))
    print(f"Saídas: {dados} | {graficos}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lote", type=date.fromisoformat, required=True)
    parser.add_argument("--sem-historico", action="store_true")
    args = parser.parse_args()
    executar(args.lote.isoformat(), not args.sem_historico)

