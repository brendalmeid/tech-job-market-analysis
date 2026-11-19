"""Coleta títulos e tags dos cartões públicos da ProgramaThor."""
import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://programathor.com.br/jobs"
DADOS = Path(__file__).resolve().parents[1] / "dados"


def extrair_vagas(html, pagina):
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    for link in soup.select(".cell-list > a[href]"):
        url = urlsplit(urljoin(pagina, link["href"]))
        if url.netloc != urlsplit(BASE).netloc or not re.fullmatch(r"/jobs/\d+-[^/]+", url.path):
            continue
        titulo = link.select_one(".cell-list-content h3")
        empresa = link.select_one(".fa-briefcase")
        local = link.select_one(".fa-map-marker-alt")
        tags = [tag.get_text(" ", strip=True) for tag in link.select(".tag-list")]
        if not titulo or not empresa or not tags:
            continue
        if any(b.get_text(strip=True).casefold() == "vaga externa" for b in link.select("b")):
            continue
        for selo in titulo.select("span"):
            selo.decompose()
        yield {
            "cargo": titulo.get_text(" ", strip=True),
            "empresa": empresa.parent.get_text(" ", strip=True),
            "local": local.parent.get_text(" ", strip=True) if local else "",
            "competencias": "; ".join(dict.fromkeys(tags)),
            "url": url._replace(query="", fragment="").geturl(),
            "pagina": pagina,
        }


def executar_coleta(paginas, arquivos):
    registros = []
    with requests.Session() as sessao:
        sessao.headers["User-Agent"] = "EstudoAcademicoMercadoTI/1.0"
        for numero in range(1, paginas + 1):
            pagina = BASE if numero == 1 else f"{BASE}/page/{numero}"
            try:
                if arquivos:
                    html = arquivos[numero - 1].read_bytes()
                else:
                    if numero > 1:
                        time.sleep(1)
                    resposta = sessao.get(pagina, timeout=20)
                    resposta.raise_for_status()
                    html = resposta.content
            except (OSError, requests.RequestException) as erro:
                raise SystemExit(f"Falha na página {numero}: {erro}") from erro
            vagas = list(extrair_vagas(html, pagina))
            if not vagas:
                raise SystemExit(f"Nenhuma vaga válida na página {numero}. Confira a listagem.")
            print(f"Página {numero}: {len(vagas)} vagas antes da deduplicação")
            registros.extend(vagas)

    base = pd.DataFrame(registros).drop_duplicates(subset="url")
    DADOS.mkdir(exist_ok=True)
    destino = DADOS / "vagas_ti.csv"
    temporario = destino.with_suffix(".tmp")
    base.to_csv(temporario, index=False, encoding="utf-8-sig")
    temporario.replace(destino)
    print(f"{len(base)} vagas únicas salvas em {destino}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paginas", type=int, default=2)
    parser.add_argument("--html", nargs="+", type=Path, help="Cópias locais das páginas em ordem")
    args = parser.parse_args()
    if args.paginas < 1:
        parser.error("--paginas deve ser maior que zero")
    executar_coleta(len(args.html) if args.html else args.paginas, args.html)

