"""Conta competências por vaga e mede menções explícitas a IA."""
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PADRAO_IA = re.compile(
    r"\b(?:IA|AI|intelig[eê]ncia artificial|artificial intelligence|"
    r"machine learning|aprendizado de m[aá]quina|deep learning|LLMs?)\b",
    re.IGNORECASE,
)


def analisar():
    arquivo = RAIZ / "dados" / "vagas_ti.csv"
    if not arquivo.exists():
        raise SystemExit("Execute coleta/scraper.py para gerar dados/vagas_ti.csv.")
    base = pd.read_csv(arquivo, keep_default_na=False)
    colunas = {"url", "cargo", "competencias"}
    if not colunas.issubset(base.columns):
        raise SystemExit(f"Colunas ausentes: {', '.join(sorted(colunas - set(base.columns)))}")
    base = base.loc[base["cargo"].str.strip().ne("") & base["url"].str.strip().ne("")]
    base = base.drop_duplicates("url").copy()
    if base.empty:
        raise SystemExit("A base não contém vagas válidas.")

    # Cada habilidade conta no máximo uma vez para cada URL.
    tags = base["competencias"].str.split(";").explode().str.strip()
    tags = pd.DataFrame({"vaga": tags.index, "competencia": tags.values})
    tags = tags.loc[tags["competencia"].ne("")]
    tags["chave"] = tags["competencia"].str.casefold()
    tags = tags.drop_duplicates(["vaga", "chave"])
    frequencias = (
        tags.groupby("chave", as_index=False)
        .agg(competencia=("competencia", "first"), vagas=("vaga", "size"))
        .sort_values(["vagas", "competencia"], ascending=[False, True])
        .drop(columns="chave")
    )
    frequencias["percentual"] = (100 * frequencias["vagas"] / len(base)).round(2)
    menciona_ia = (base["cargo"] + " " + base["competencias"]).str.contains(PADRAO_IA)
    resumo = pd.DataFrame([{"total_vagas": len(base), "vagas_com_ia": int(menciona_ia.sum()),
                            "percentual_ia": round(100 * menciona_ia.mean(), 2)}])

    destino = RAIZ / "graficos"
    destino.mkdir(exist_ok=True)
    frequencias.to_csv(destino / "frequencias.csv", index=False, encoding="utf-8-sig")
    resumo.to_csv(destino / "resumo.csv", index=False)
    base.loc[menciona_ia].to_csv(destino / "vagas_com_ia.csv", index=False, encoding="utf-8-sig")
    topo = frequencias.head(8).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 4))
    barras = ax.barh(topo["competencia"], topo["vagas"], color="#176b87")
    ax.bar_label(barras, padding=4)
    ax.set_xlim(0, max(topo["vagas"], default=1) + 1)
    ax.set(xlabel="Número de vagas", title="Competências mais frequentes nos cartões")
    fig.tight_layout()
    fig.savefig(destino / "competencias.png", dpi=170)
    plt.close(fig)
    print(resumo.to_string(index=False))
    print(frequencias.head(8).to_string(index=False))


if __name__ == "__main__":
    analisar()

