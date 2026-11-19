"""Baixa páginas da API pública Lever e registra cada resposta para retomada."""
import argparse
import json
import logging
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser

import requests

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = "https://api.lever.co"
AGENTE = "EstudoAcademicoMercadoTI"
EMPRESAS = {"ciandt": "CI&T", "dlocal": "dLocal", "Flex": "Flex", "britecore": "BriteCore", "jobgether": "Jobgether"}
TAMANHO = 50


def validar_robots(resposta, url):
    # Um 404 indica ausência do arquivo. Um bloqueio ou erro interrompe a coleta.
    if resposta.status_code == 404:
        return
    resposta.raise_for_status()
    regras = RobotFileParser()
    regras.parse(resposta.text.splitlines())
    if not regras.can_fetch(AGENTE, url):
        raise RuntimeError(f"Robots.txt não permite {url}")
    limites = [regras.crawl_delay(AGENTE) or 0]
    taxa = regras.request_rate(AGENTE)
    if taxa and taxa.requests:
        limites.append(taxa.seconds / taxa.requests)
    return max(limites)


def coletar(pasta, empresas, intervalo):
    pasta.mkdir(parents=True, exist_ok=True)
    with requests.Session() as sessao:
        sessao.headers["User-Agent"] = AGENTE + "/1.0"
        robots = None
        for empresa in empresas:
            endpoint = f"{ORIGEM}/v0/postings/{empresa}"
            for pagina in range(200):
                arquivo = pasta / f"{empresa}-{pagina:03}.json"
                if arquivo.exists():
                    dados = json.loads(arquivo.read_text(encoding="utf-8"))
                    logging.info("%s página %d reutilizada", empresa, pagina + 1)
                else:
                    if robots is None:
                        robots = sessao.get(f"{ORIGEM}/robots.txt", timeout=20)
                    limite = validar_robots(robots, endpoint) or 0
                    time.sleep(max(intervalo, limite))
                    parametros = {"mode": "json", "limit": TAMANHO, "skip": pagina * TAMANHO}
                    if empresa == "jobgether":
                        parametros["location"] = "Brazil"
                    resposta = sessao.get(endpoint, params=parametros, timeout=30)
                    resposta.raise_for_status()
                    vagas = resposta.json()
                    if not isinstance(vagas, list) or len(vagas) > TAMANHO:
                        raise ValueError(f"Resposta inesperada: {resposta.url}")
                    dados = {"empresa": empresa, "url": resposta.url,
                             "coletado_em": datetime.now(timezone.utc).isoformat(),
                             "vagas": vagas}
                    temp = arquivo.with_suffix(".tmp")
                    temp.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
                    temp.replace(arquivo)
                    logging.info("%s página %d: %d anúncios", empresa, pagina + 1, len(vagas))
                if len(dados["vagas"]) < TAMANHO:
                    break
            else:
                raise RuntimeError(f"Limite de páginas atingido em {empresa}; verifique a paginação.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lote", type=date.fromisoformat, required=True, help="Data do lote, AAAA-MM-DD")
    parser.add_argument("--empresa", choices=EMPRESAS, action="append")
    parser.add_argument("--intervalo", type=float, default=2)
    args = parser.parse_args()
    if not 1 <= args.intervalo <= 3600:
        parser.error("--intervalo deve estar entre 1 e 3600 segundos.")
    pasta = RAIZ / "dados" / "brutos" / "lever" / args.lote.isoformat()
    pasta.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(pasta / "coleta.log", encoding="utf-8")])
    try:
        coletar(pasta, args.empresa or EMPRESAS, args.intervalo)
    except (requests.RequestException, OSError, ValueError, RuntimeError) as erro:
        logging.error("Coleta interrompida. Para retomar, repita o comando: %s", erro)
        raise SystemExit(1) from erro

