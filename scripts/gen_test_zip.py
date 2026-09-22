import os
import zipfile
import shutil
from docx import Document
from openpyxl import Workbook

DOWNLOADS = os.path.expanduser("~/Downloads")
TMP = os.path.join(os.path.dirname(__file__), "_tmp_gen")


def minimal_pptx(path):
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    presentation = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId1"/>
  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000"/>
</p:presentation>"""

    presentation_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>"""

    slide1 = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr/>
        <p:txBody><a:bodyPr/><a:p><a:r><a:t>Curso ESG</a:t></a:r></a:p></p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels)
        z.writestr("ppt/slides/slide1.xml", slide1)


def make_docx(path, texto):
    doc = Document()
    doc.add_paragraph(texto)
    doc.save(path)


def make_xlsx(path, valor_a1, valor_b2):
    wb = Workbook()
    ws = wb.active
    ws.title = "Plan1"
    ws["A1"] = valor_a1
    ws["B2"] = valor_b2
    wb.save(path)


def build_zip(out_name, docx_texto, xlsx_a1, xlsx_b2, include_all=True):
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    root = os.path.join(TMP, "pasta1")
    os.makedirs(os.path.join(root, "powerpoint"), exist_ok=True)
    os.makedirs(os.path.join(root, "docx"), exist_ok=True)
    os.makedirs(os.path.join(root, "excel"), exist_ok=True)

    minimal_pptx(os.path.join(root, "powerpoint", "apresentacao.pptx"))
    make_docx(os.path.join(root, "docx", "relatorio.docx"), docx_texto)
    make_xlsx(os.path.join(root, "excel", "planilha.xlsx"), xlsx_a1, xlsx_b2)

    out_path = os.path.join(DOWNLOADS, out_name)
    if os.path.exists(out_path):
        os.remove(out_path)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, filenames in os.walk(TMP):
            for f in filenames:
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, TMP)
                z.write(full, rel.replace(os.sep, "/"))

    shutil.rmtree(TMP)
    print("gerado:", out_path)


# 100 pontos: docx contém os dois termos esperados, excel com valores certos
build_zip(
    "teste-100.zip",
    docx_texto="Este documento fala sobre Fundamentos Digitais e sobre o Curso ESG da DITE.",
    xlsx_a1="Fundamentos Digitais",
    xlsx_b2="Aprovado",
)

# 90 pontos: docx só contém 1 dos 2 termos esperados (perde parte da pontuação do docx)
build_zip(
    "teste-90.zip",
    docx_texto="Este documento fala apenas sobre Fundamentos Digitais.",
    xlsx_a1="Fundamentos Digitais",
    xlsx_b2="Aprovado",
)
