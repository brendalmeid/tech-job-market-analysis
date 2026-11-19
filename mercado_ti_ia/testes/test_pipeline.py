import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analise.analisar_amostra import calcular
from analise.preparar_vagas import descricao_lever, preparar
from analise.vocabulario import classificar_ia, tecnologias_texto
from coleta.coletar_lever import coletar, validar_robots


class Identificacao(unittest.TestCase):
    def test_evidencia_por_campo(self):
        evidencia = classificar_ia("AI Engineer", ["AI Agents", "NLP"], "RAG e modelos LLM.")
        self.assertEqual(evidencia["titulo"], ["IA/AI"])
        self.assertEqual(evidencia["etiquetas"], ["Agentes de IA", "NLP"])
        self.assertEqual(evidencia["descricao"], ["LLM", "RAG"])

    def test_siglas_ambiguas(self):
        resultado = classificar_ia("Dev em Cedar Rapids, IA", ["API"], "Use a rag to clean.")
        self.assertFalse(any(resultado.values()))

    def test_termos_contextuais(self):
        for texto in ("AI-powered", "ferramentas de IA", "NLP engineer", "GenAI",
                      "Visão computacional", "Deep Learning", "Natural Language Processing"):
            with self.subTest(texto=texto):
                self.assertTrue(classificar_ia("", [], texto)["descricao"])

    def test_aviso_de_recrutamento(self):
        vaga = {"descriptionPlain": "Software role.\nWe may use artificial intelligence in hiring.",
                "lists": [{"text": "Requirements", "content": "<ul><li>Python</li><li>SQL</li></ul>"}]}
        descricao = descricao_lever(vaga)
        self.assertFalse(classificar_ia("", [], descricao)["descricao"])
        self.assertEqual(tecnologias_texto(descricao), {"Python", "SQL"})

    def test_normalizacao(self):
        self.assertEqual(tecnologias_texto("C Sharp e C#; Java Script; NodeJS; React Native."),
                         {"C#", "JavaScript", "Node.js", "React Native"})

    def test_remove_apresentacao_institucional(self):
        vaga = {"descriptionPlain": "At CI&T, we help large enterprises use AI tools.\nBuild Java APIs."}
        self.assertEqual(descricao_lever(vaga, "ciandt"), "Build Java APIs.")
        self.assertFalse(classificar_ia("", [], descricao_lever(vaga, "ciandt"))["descricao"])


class Pipeline(unittest.TestCase):
    def test_triagem_deduplicacao_e_resultados(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            pasta = raiz / "dados" / "brutos" / "lever" / "2026-11-19"
            pasta.mkdir(parents=True)
            casos = [
                ("[Job-12345] Senior Python Developer", "Brazil"),
                ("[Job-12345] Senior Python Developer", "Brazil"),
                ("Python Developer", "Colombia"),
                ("Sales Manager", "Brazil"),
            ]
            vagas = [
                {"text": cargo, "hostedUrl": f"https://jobs.lever.co/ciandt/{i}",
                 "categories": {"location": local}, "workplaceType": "remote",
                 "descriptionPlain": "Python, Docker, Machine Learning"}
                for i, (cargo, local) in enumerate(casos)
            ]
            (pasta / "ciandt-000.json").write_text(json.dumps({
                "empresa": "ciandt", "coletado_em": "2026-11-19T15:00:00+00:00",
                "url": "https://api.lever.co/v0/postings/ciandt", "vagas": vagas,
            }), encoding="utf-8")
            auditoria, base = preparar(raiz, "2026-11-19")
            self.assertEqual(len(base), 1)
            self.assertEqual(set(auditoria["motivos"]), {
                "", "Duplicata", "Localização brasileira não indicada", "Título fora do recorte técnico"
            })
            linha = base.iloc[0]
            self.assertTrue(linha["mencao_ia"])
            self.assertEqual(linha["senioridade"], "Sênior")
            self.assertEqual(linha["modalidade"], "Remoto")
            self.assertEqual(linha["competencias"], "Docker; Python")
            tabelas = calcular(auditoria, base, raiz)
            self.assertEqual(tabelas["por_fonte"].iloc[0]["excluidas"], 3)
            self.assertEqual(tabelas["mencoes_ia"].iloc[0]["percentual"], 100)
            self.assertTrue((raiz / "competencias.png").exists())

    def test_base_historica_preservada(self):
        raiz = Path(__file__).resolve().parents[1]
        _, base = preparar(raiz, "sem-cache")
        self.assertEqual(len(base), 19)
        self.assertFalse(base["tem_descricao"].any())

    def test_retomada_sem_requisicao(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            (pasta / "ciandt-000.json").write_text('{"vagas": []}', encoding="utf-8")
            with patch("requests.Session.get", side_effect=AssertionError("rede em cache completo")):
                coletar(pasta, ["ciandt"], 2)

    def test_robots(self):
        class Resposta:
            status_code = 200
            text = "User-agent: *\nDisallow: /privado/\nCrawl-delay: 5\n"

            def raise_for_status(self):
                pass

        self.assertEqual(validar_robots(Resposta(), "https://api.lever.co/v0/postings"), 5)
        with self.assertRaises(RuntimeError):
            validar_robots(Resposta(), "https://api.lever.co/privado/teste")
