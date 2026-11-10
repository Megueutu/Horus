"""Validate the static site without executing the browser app or fixture generator."""

import csv
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

import yaml


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in ("script", "img", "link"):
            url = attrs.get("src") or attrs.get("href")
            if url and not url.startswith(("https://", "http://", "data:", "#")):
                self.references.append((url, attrs.get("onerror")))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root):
    page = Page()
    page.feed((root / "index.html").read_text(encoding="utf-8"))
    javascript = (root / "app.js").read_text(encoding="utf-8")
    for element_id in re.findall(r'getElementById\("([^"]+)"\)', javascript):
        require(element_id in page.ids, f"Missing HTML element: {element_id}")
    for url, fallback in page.references:
        if not (root / url).is_file():
            require(bool(fallback), f"Missing local asset: {url}")
            print(f"NOTE: optional asset {url} is absent; existing onerror fallback is preserved.")

    rules = yaml.safe_load((root / "config/rules.yaml").read_text(encoding="utf-8"))
    excel = yaml.safe_load((root / "config/excel-check.yaml").read_text(encoding="utf-8"))
    with (root / "config/docx-check.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    require(rows and rows[0] == ["conteudo_esperado"], "Invalid DOCX CSV header")
    require(len(rows) > 1 and all(len(row) == 1 and row[0].strip() for row in rows[1:]),
            "DOCX expectations must contain nonempty, single-column rows")

    require(isinstance(rules.get("pasta_raiz"), str) and rules["pasta_raiz"].strip(),
            "Missing ZIP root folder")
    require(set(rules["pastas"]) == {"powerpoint", "docx", "excel"}, "Invalid folder categories")
    weights = [rules["pontos_pasta_raiz"], rules["pontos_organizacao"]]
    for category, folder in rules["pastas"].items():
        require(isinstance(folder["nome"], str) and folder["nome"].strip(), "Empty folder name")
        extensions = folder["extensao_esperada"]
        extensions = extensions if isinstance(extensions, list) else [extensions]
        require(extensions and all(isinstance(ext, str) and ext.startswith(".") for ext in extensions),
                f"Invalid extensions: {category}")
        weights.extend([folder["pontos_existencia"], folder["pontos_nome_correto"],
                        rules["verificacao_conteudo"][category]["pontos"]])
    require(all(type(weight) is int and weight >= 0 for weight in weights), "Invalid score weights")
    require(sum(weights) == 100, f"Expected a 100-point rubric; got {sum(weights)}")
    required_texts = {
        "erro_config", "erro_generico", "check_pasta_raiz", "check_pasta_existe",
        "check_arquivo_correto", "check_organizacao", "check_pptx", "check_docx_resultado",
        "check_docx_ausente", "check_excel_resultado", "check_excel_ausente",
    }
    require(all(isinstance(rules["textos"].get(key), str) and rules["textos"][key].strip()
                for key in required_texts), "Missing application messages")
    require(excel.get("verificacoes"), "No Excel checks configured")
    for cell in excel["verificacoes"]:
        require(isinstance(cell["pagina"], str) and cell["pagina"].strip(), "Missing worksheet name")
        require(re.fullmatch(r"[A-Z]+", cell["coluna"]), "Invalid Excel column")
        require(type(cell["linha"]) is int and cell["linha"] > 0, "Invalid Excel row")
        require("conteudo_esperado" in cell, "Missing expected Excel value")
    print(f"PASS: HTML/JS references, YAML configurations, {len(rows) - 1} DOCX terms, "
          f"{len(excel['verificacoes'])} Excel cells, and 100-point rubric.")


if __name__ == "__main__":
    try:
        validate(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        sys.exit(f"FAIL: {error}")
