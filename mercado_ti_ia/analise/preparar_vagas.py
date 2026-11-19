"""Normaliza o recorte histórico e os registros públicos da Lever."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from bs4 import BeautifulSoup

if __package__:
    from .vocabulario import ALIASES, RE_RECRUTAMENTO, classificar_ia, tecnologias_texto
else:
    from vocabulario import ALIASES, RE_RECRUTAMENTO, classificar_ia, tecnologias_texto

BRASIL = re.compile(r"\b(?:brasil|brazil|s[ãa]o paulo|rio de janeiro|belo horizonte|curitiba|"
                   r"porto alegre|florian[oó]polis|recife|campinas|bras[ií]lia)\b", re.I)
CARGO_TEC = re.compile(
    r"\b(?:desenvolved\w*|developers?|programador\w*|full[ -]?stack|back[ -]?end|"
    r"front[ -]?end|devops|devsecops|sre|dataops|mlops|mobile engineer|"
    r"(?:software|data|platform|cloud|ai|machine learning|qa|quality assurance|"
    r"security|integration|site reliability|test|automation|analytics) (?:engineer\w*|architect\w*)|"
    r"(?:java|python|dotnet|net|kotlin|android|ios|golang) (?:engineer\w*|developer\w*)|"
    r"engenheir\w* (?:de|em) (?:software|dados|ia|machine learning|plataforma|qualidade)|"
    r"arquit\w* (?:de|em) (?:software|dados|solu[cç][oõ]es|nuvem)|"
    r"tech(?:nical)? lead|qa|quality assurance|software architect|systems? architect|"
    r"machine learning|cientista de dados|data scien(?:tist|ce))\b", re.I
)
NIVEIS = {
    "Júnior": r"\b(?:j[uú]nior|jr)\b",
    "Pleno": r"\b(?:pleno|mid(?:[- ]level)?|intermedi[aá]rio)\b",
    "Sênior": r"\b(?:s[eê]nior|sr)\b",
}
MODALIDADES = {
    "Remoto": r"\b(?:remot[oea]|home\s*office)\b",
    "Híbrido": r"\b(?:h[ií]brid[oa]|hybrid)\b",
    "Presencial": r"\b(?:presencial|on[ -]?site|office[ -]?based)\b",
}
TEXTOS_INSTITUCIONAIS = {
    "ciandt": re.compile(
        r"^\s*(?:At CI&T,\s*we help large enterprises|Na CI&T\s*,\s*ajudamos grandes empresas)",
        re.I,
    ),
    "Flex": re.compile(r"^\s*Flex is building AI.native financial services", re.I),
}


def metadado(texto, padroes):
    encontrados = [nome for nome, padrao in padroes.items() if re.search(padrao, texto, re.I)]
    return " / ".join(encontrados)


def descricao_lever(vaga, quadro=""):
    secoes = [vaga.get("descriptionPlain") or ""]
    for lista in vaga.get("lists") or []:
        soup = BeautifulSoup(lista.get("content") or "", "html.parser")
        secoes += [lista.get("text") or "", soup.get_text("\n", strip=True)]
    # Campos promocionais finais não entram. Remove avisos de IA no recrutamento
    # também quando aparecem no corpo incluído.
    institucional = TEXTOS_INSTITUCIONAIS.get(quadro)
    return "\n".join(linha for secao in secoes for linha in secao.splitlines()
                     if linha.strip() and not RE_RECRUTAMENTO.search(linha)
                     and not (institucional and institucional.search(linha)))


def registros_lever(pasta):
    for arquivo in sorted(pasta.glob("*.json")):
        lote = json.loads(arquivo.read_text(encoding="utf-8"))
        for vaga in lote["vagas"]:
            campos = vaga.get("categories") or {}
            locais = list(dict.fromkeys(filter(None, [campos.get("location"), *(campos.get("allLocations") or [])])))
            local = " | ".join(locais)
            cargo = (vaga.get("text") or "").strip()
            url = (vaga.get("hostedUrl") or "").strip()
            motivo = ""
            if not cargo or urlsplit(url).netloc != "jobs.lever.co":
                motivo = "Título ou URL inválidos"
            elif not BRASIL.search(local):
                motivo = "Localização brasileira não indicada"
            elif not CARGO_TEC.search(cargo):
                motivo = "Título fora do recorte técnico"
            plataforma = lote["empresa"]
            quadro = {"ciandt": "CI&T", "dlocal": "dLocal", "Flex": "Flex",
                      "britecore": "BriteCore", "jobgether": "Jobgether"}.get(plataforma, plataforma)
            empresa = "" if plataforma == "jobgether" else quadro
            descricao = descricao_lever(vaga, plataforma) if not motivo else ""
            codigo = re.search(r"\[\s*(?:job\s*[- ]?\s*)?(\d{4,})\s*\]", cargo, re.I)
            chave = f"{quadro}:{codigo.group(1)}" if codigo else url
            if not codigo and descricao:
                assinatura = " ".join((cargo + " " + descricao).casefold().split())
                chave = quadro + ":" + hashlib.sha256(assinatura.encode("utf-8")).hexdigest()
            yield dict(cargo=cargo, empresa=empresa, quadro=quadro, local=local, fonte="Lever", url=url,
                       pagina=lote["url"], coletado_em=lote["coletado_em"],
                       modalidade=metadado(vaga.get("workplaceType") or local, MODALIDADES)
                       or metadado(local, MODALIDADES),
                       senioridade=metadado(cargo, NIVEIS), etiquetas="", motivos=motivo,
                       descricao=descricao, chave=chave)


def registros_thor(arquivo):
    for vaga in pd.read_csv(arquivo, dtype=str, keep_default_na=False).to_dict("records"):
        yield dict(cargo=vaga["cargo"], empresa=vaga["empresa"], quadro="ProgramaThor", local=vaga["local"],
                   fonte="ProgramaThor", url=vaga["url"], pagina=vaga["pagina"],
                   coletado_em="2026-11-19", modalidade=metadado(vaga["local"], MODALIDADES),
                   senioridade=metadado(vaga["cargo"], NIVEIS), etiquetas=vaga["competencias"],
                   descricao="", motivos="", chave=vaga["url"])


def preparar(raiz: Path, lote: str, incluir_historico=True):
    historico = raiz / "dados" / "vagas_ti.csv"
    pasta = raiz / "dados" / "brutos" / "lever" / lote
    registros = list(registros_thor(historico)) if incluir_historico and historico.exists() else []
    registros.extend(registros_lever(pasta))
    if not registros:
        raise ValueError("Nenhum dado disponível para o lote solicitado.")
    chaves, urls = set(), set()
    for vaga in registros:
        if vaga["motivos"]:
            continue
        chave, url = vaga["chave"], vaga["url"]
        if chave in chaves or url in urls:
            vaga["motivos"] = "Duplicata"
            continue
        chaves.add(chave)
        urls.add(url)

    auditoria = pd.DataFrame(registros).drop(columns=["descricao", "chave"])
    validas = []
    for vaga in registros:
        if vaga["motivos"]:
            continue
        etiquetas = [tag.strip() for tag in vaga["etiquetas"].split(";") if tag.strip()]
        tecnologias = {ALIASES.get(tag.casefold(), tag) for tag in etiquetas}
        if vaga["fonte"] == "Lever":
            tecnologias |= tecnologias_texto(vaga["cargo"] + "\n" + vaga["descricao"])
        ia = classificar_ia(vaga["cargo"], etiquetas, vaga["descricao"])
        linha = {k: v for k, v in vaga.items() if k not in {"descricao", "motivos", "chave"}}
        linha.update(competencias="; ".join(sorted(tecnologias, key=str.casefold)),
                     tem_descricao=bool(vaga["descricao"]), mencao_ia=any(ia.values()))
        linha.update({f"ia_{campo}": "; ".join(termos) for campo, termos in ia.items()})
        validas.append(linha)
    return auditoria, pd.DataFrame(validas)

