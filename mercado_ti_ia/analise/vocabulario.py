"""Vocabulários explícitos para classificar anúncios sem inferir requisitos."""
import re

TERMOS_IA = {
    "Inteligência artificial": r"intelig[eê]ncia artificial|artificial intelligence",
    "Machine learning": r"machine learning|aprendizado de m[aá]quina",
    "Deep learning": r"deep learning|aprendizado profundo",
    "IA generativa": r"generative ai|ai generative|gen[ -]?ai|ia generativa",
    "LLM": r"llms?|large language models?|modelos? de linguagem de grande porte",
    "Agentes de IA": r"ai agents?|agentes? de ia|agentic ai",
    "NLP": r"NLP|natural language processing|processamento de linguagem natural",
    "Visão computacional": r"computer vision|vis[aã]o computacional",
    "RAG": r"RAG|retrieval[ -]augmented generation",
}
SIGLAS = {"IA", "AI", "NLP", "RAG"}
PADROES_IA = {
    nome: re.compile(rf"(?<!\w)(?:{padrao})(?!\w)", re.IGNORECASE)
    for nome, padrao in TERMOS_IA.items()
}
RE_SIGLA = re.compile(r"\b(?:IA|AI)\b")
RE_IA_CONTEXTUAL = re.compile(
    r"\b(?:AI|IA)[ -](?:engineer\w*|engineering|developer\w*|architect\w*|"
    r"platform\w*|tools?|powered|driven|assisted|first|native|models?|solutions?|systems?|generativa|aplicada)\b"
    r"|\b(?:engenheir[oa]|desenvolvedor[ae]?|especialista|solu[cç][oõ]es|ferramentas?|modelos?)"
    r" (?:em|de|com) (?:IA|AI)\b", re.IGNORECASE
)
RE_ESTADO_IOWA = re.compile(r",\s*IA(?=\s*(?:\d{5}\b|[.;)]|$))")
RE_RECRUTAMENTO = re.compile(
    r"we may use artificial intelligence|we use (?:artificial intelligence|ai) tools in our hiring"
    r"|ferramentas? de (?:ia|intelig[eê]ncia artificial).*processo seletivo",
    re.IGNORECASE,
)

TECNOLOGIAS = {
    "Python": r"python", "Java": r"java(?![ .-]script\b)",
    "JavaScript": r"java[ .-]?script|(?-i:JS)",
    "TypeScript": r"type[ .-]?script|(?-i:TS)", "C#": r"c ?\#|c[ -]?sharp", "C++": r"c\+\+",
    ".NET": r"\.net|dotnet", "Node.js": r"node[ .-]?js",
    "React": r"react(?:[ .-]?js)?", "React Native": r"react native",
    "Angular": r"angular", "Vue.js": r"vue(?:[ .-]?js)?",
    "SQL": r"sql", "SQL Server": r"sql server", "PostgreSQL": r"postgres(?:ql)?",
    "MySQL": r"mysql", "MongoDB": r"mongodb", "Redis": r"redis",
    "Docker": r"docker", "Kubernetes": r"kubernetes|k8s", "Terraform": r"terraform",
    "AWS": r"aws|amazon web services", "Azure": r"azure",
    "GCP": r"gcp|google cloud platform", "Git": r"git", "CI/CD": r"ci\s*/\s*cd",
    "Kafka": r"kafka", "RabbitMQ": r"rabbitmq", "Databricks": r"databricks",
    "Spark": r"apache spark|pyspark", "FastAPI": r"fastapi",
    "Spring Boot": r"spring boot", "Flutter": r"flutter", "Kotlin": r"kotlin",
    "API": r"apis?", "REST": r"restful|rest apis?|apis? rest", "PHP": r"php",
    "Ruby": r"ruby", "Rust": r"rust", "Go": r"golang|go lang", "Swift": r"swift",
    "LangChain": r"langchain", "LangGraph": r"langgraph", "PyTorch": r"pytorch",
    "TensorFlow": r"tensorflow", "Pandas": r"pandas", "Snowflake": r"snowflake",
    "Power BI": r"power\s*bi", "Cypress": r"cypress", "Playwright": r"playwright",
    "Selenium": r"selenium", "GraphQL": r"graphql", "SASS": r"sass|scss",
}
PADROES_TEC = {
    nome: re.compile(rf"(?<![\w+#])(?:{termos})(?![\w+#])", re.IGNORECASE)
    for nome, termos in TECNOLOGIAS.items()
}
ALIASES = {
    "javascript": "JavaScript", "java script": "JavaScript", "js": "JavaScript",
    "typescript": "TypeScript", "type script": "TypeScript", "ts": "TypeScript",
    "node.js": "Node.js", "node js": "Node.js", "nodejs": "Node.js",
    "c#": "C#", "c #": "C#", "csharp": "C#", "c sharp": "C#",
    "reactjs": "React", "react.js": "React", "react": "React",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "dotnet": ".NET",
}


def termos_ia(texto, campo):
    """Aceita siglas isoladas como etiquetas e exige contexto para AI/IA em prosa."""
    texto = RE_ESTADO_IOWA.sub("", texto or "")
    encontrados = set()
    for nome, padrao in PADROES_IA.items():
        for match in padrao.finditer(texto):
            termo = match.group()
            if termo.upper() in SIGLAS and campo != "etiqueta" and termo != termo.upper():
                continue
            encontrados.add(nome)
    etiqueta_curta = campo == "etiqueta" and texto.strip().upper() in {"AI", "IA"}
    sigla_titulo = campo == "titulo" and RE_SIGLA.search(texto)
    if etiqueta_curta or sigla_titulo or RE_IA_CONTEXTUAL.search(texto):
        if not encontrados:
            encontrados.add("IA/AI")
    return encontrados


def classificar_ia(titulo, etiquetas=(), descricao=""):
    """Retorna a evidência observada em cada campo."""
    return {
        "titulo": sorted(termos_ia(titulo, "titulo")),
        "etiquetas": sorted(set().union(*(termos_ia(tag, "etiqueta") for tag in etiquetas))),
        "descricao": sorted(termos_ia(descricao, "descricao")),
    }


def tecnologias_texto(texto):
    texto = re.sub(r"\breact native\b", "ReactNative", texto, flags=re.IGNORECASE)
    encontrados = {nome for nome, padrao in PADROES_TEC.items() if padrao.search(texto)}
    if "ReactNative" in texto:
        encontrados.add("React Native")
    return encontrados

