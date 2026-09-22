// app.js — corretor automático de ZIP (DITE)
// Sem backend: tudo roda no navegador com JSZip + js-yaml.

(function () {
  "use strict";

  const CONFIG_PATHS = {
    rules: "config/rules.yaml",
    docxCsv: "config/docx-check.csv",
    excelYaml: "config/excel-check.yaml",
  };

  const fileInput = document.getElementById("file-input");
  const fileNameEl = document.getElementById("file-name");
  const loadingEl = document.getElementById("loading");
  const uploadCard = document.querySelector(".upload-card");
  const resultCard = document.getElementById("result");
  const errorCard = document.getElementById("error");
  const errorMessageEl = document.getElementById("error-message");
  const scoreValueEl = document.getElementById("score-value");
  const resultListEl = document.getElementById("result-list");
  const resetBtn = document.getElementById("reset-btn");
  const errorResetBtn = document.getElementById("error-reset-btn");

  fileInput.addEventListener("change", onFileSelected);
  resetBtn.addEventListener("click", resetUI);
  errorResetBtn.addEventListener("click", resetUI);

  function resetUI() {
    fileInput.value = "";
    fileNameEl.textContent = "";
    resultCard.hidden = true;
    errorCard.hidden = true;
    uploadCard.hidden = false;
    loadingEl.hidden = true;
  }

  async function onFileSelected(event) {
    const file = event.target.files[0];
    if (!file) return;

    fileNameEl.textContent = file.name;
    loadingEl.hidden = false;

    try {
      const result = await corrigirZip(file);
      showResult(result);
    } catch (err) {
      console.error(err);
      const fallback =
        configCache && configCache.rules && configCache.rules.textos
          ? configCache.rules.textos.erro_generico
          : "Não foi possível processar o arquivo.";
      showError(err.message || fallback);
    } finally {
      loadingEl.hidden = true;
    }
  }

  function showResult(result) {
    uploadCard.hidden = true;
    errorCard.hidden = true;
    resultCard.hidden = false;

    scoreValueEl.textContent = result.total;
    resultListEl.innerHTML = "";

    result.checks.forEach((check) => {
      const li = document.createElement("li");
      li.className = check.ok ? "ok" : "fail";
      const label = document.createElement("span");
      label.textContent = check.label;
      const points = document.createElement("span");
      points.className = "points";
      points.textContent = `${check.earned}/${check.max}`;
      li.appendChild(label);
      li.appendChild(points);
      resultListEl.appendChild(li);
    });
  }

  function showError(message) {
    uploadCard.hidden = true;
    resultCard.hidden = true;
    errorCard.hidden = false;
    errorMessageEl.textContent = message;
  }

  // ---------------------------------------------------------------------
  // Config loading
  // ---------------------------------------------------------------------

  let configCache = null;

  async function loadConfig() {
    if (configCache) return configCache;

    const [rulesText, csvText, excelYamlText] = await Promise.all([
      fetchText(CONFIG_PATHS.rules),
      fetchText(CONFIG_PATHS.docxCsv),
      fetchText(CONFIG_PATHS.excelYaml),
    ]);

    const rules = jsyaml.load(rulesText);
    const docxExpected = parseCsv(csvText);
    const excelChecks = jsyaml.load(excelYamlText);

    configCache = { rules, docxExpected, excelChecks };
    return configCache;
  }

  async function fetchText(path) {
    const res = await fetch(path);
    if (!res.ok) {
      const template =
        configCache && configCache.rules && configCache.rules.textos
          ? configCache.rules.textos.erro_config
          : "Não foi possível carregar o arquivo de configuração: {path}";
      throw new Error(format(template, { path }));
    }
    return res.text();
  }

  function format(template, values) {
    return template.replace(/\{(\w+)\}/g, (_, key) =>
      values[key] !== undefined ? values[key] : `{${key}}`
    );
  }

  function parseCsv(text) {
    const lines = text
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0);
    // primeira linha é cabeçalho ("conteudo_esperado")
    return lines.slice(1);
  }

  // ---------------------------------------------------------------------
  // Correção principal
  // ---------------------------------------------------------------------

  async function corrigirZip(file) {
    const { rules, docxExpected, excelChecks } = await loadConfig();
    const textos = rules.textos;

    const zip = await JSZip.loadAsync(file);
    const entries = Object.keys(zip.files);

    const checks = [];
    let total = 0;

    const rootFolder = rules.pasta_raiz;
    const hasRoot = entries.some((path) => normalizePath(path).startsWith(rootFolder + "/"));

    checks.push(
      pushCheck(
        format(textos.check_pasta_raiz, { pasta: rootFolder }),
        hasRoot,
        hasRoot ? rules.pontos_pasta_raiz : 0,
        rules.pontos_pasta_raiz
      )
    );

    const subfolders = rules.pastas;
    const foundFiles = {};

    for (const key of Object.keys(subfolders)) {
      const sub = subfolders[key];
      const folderPath = `${rootFolder}/${sub.nome}/`;
      const filesInFolder = entries.filter(
        (p) => normalizePath(p).startsWith(folderPath) && !p.endsWith("/")
      );

      const folderExists = entries.some((p) => normalizePath(p).startsWith(folderPath));
      checks.push(
        pushCheck(
          format(textos.check_pasta_existe, { pasta: sub.nome }),
          folderExists,
          folderExists ? sub.pontos_existencia : 0,
          sub.pontos_existencia
        )
      );

      const exts = Array.isArray(sub.extensao_esperada)
        ? sub.extensao_esperada
        : [sub.extensao_esperada];

      const matchFile = filesInFolder.find((p) =>
        exts.some((ext) => p.toLowerCase().endsWith(ext))
      );

      checks.push(
        pushCheck(
          format(textos.check_arquivo_correto, {
            extensoes: exts.join(", "),
            pasta: sub.nome,
          }),
          !!matchFile,
          matchFile ? sub.pontos_nome_correto : 0,
          sub.pontos_nome_correto
        )
      );

      foundFiles[key] = matchFile || null;
    }

    // Organização geral: as 3 pastas existem dentro da pasta raiz, nenhuma fora do lugar
    const allFoldersOk = Object.keys(subfolders).every((key) => {
      const sub = subfolders[key];
      return entries.some((p) => normalizePath(p).startsWith(`${rootFolder}/${sub.nome}/`));
    });
    checks.push(
      pushCheck(
        textos.check_organizacao,
        allFoldersOk,
        allFoldersOk ? rules.pontos_organizacao : 0,
        rules.pontos_organizacao
      )
    );

    // -------- PPTX: só verifica nome do arquivo (existência já conta) -----
    const pptxPoints = rules.verificacao_conteudo.powerpoint.pontos;
    const pptxOk = !!foundFiles.powerpoint;
    checks.push(pushCheck(textos.check_pptx, pptxOk, pptxOk ? pptxPoints : 0, pptxPoints));

    // -------- DOCX: conteúdo do CSV deve existir no texto do docx --------
    const docxPoints = rules.verificacao_conteudo.docx.pontos;
    let docxScore = 0;
    if (foundFiles.docx) {
      const docxText = await extractDocxText(zip.file(foundFiles.docx));
      const foundCount = docxExpected.filter((expected) =>
        docxText.toLowerCase().includes(expected.toLowerCase())
      ).length;
      const ratio = docxExpected.length ? foundCount / docxExpected.length : 0;
      docxScore = Math.round(ratio * docxPoints);
      checks.push(
        pushCheck(
          format(textos.check_docx_resultado, {
            encontrados: foundCount,
            total: docxExpected.length,
          }),
          foundCount === docxExpected.length,
          docxScore,
          docxPoints
        )
      );
    } else {
      checks.push(pushCheck(textos.check_docx_ausente, false, 0, docxPoints));
    }

    // -------- EXCEL: verificações de célula (página, coluna, linha) ------
    const excelPoints = rules.verificacao_conteudo.excel.pontos;
    let excelScore = 0;
    const verificacoesExcel = (excelChecks && excelChecks.verificacoes) || [];
    if (foundFiles.excel && verificacoesExcel.length) {
      const cellsOk = await checkExcelCells(zip.file(foundFiles.excel), verificacoesExcel);
      const ratio = cellsOk / verificacoesExcel.length;
      excelScore = Math.round(ratio * excelPoints);
      checks.push(
        pushCheck(
          format(textos.check_excel_resultado, {
            encontrados: cellsOk,
            total: verificacoesExcel.length,
          }),
          cellsOk === verificacoesExcel.length,
          excelScore,
          excelPoints
        )
      );
    } else {
      checks.push(pushCheck(textos.check_excel_ausente, false, 0, excelPoints));
    }

    total = checks.reduce((sum, c) => sum + c.earned, 0);
    const maxTotal = checks.reduce((sum, c) => sum + c.max, 0);
    const normalizedTotal = maxTotal ? Math.round((total / maxTotal) * 100) : 0;

    return { total: normalizedTotal, checks };
  }

  function pushCheck(label, ok, earned, max) {
    return { label, ok, earned, max };
  }

  function normalizePath(path) {
    return path.replace(/\\/g, "/");
  }

  // ---------------------------------------------------------------------
  // DOCX: é um zip com word/document.xml contendo o texto
  // ---------------------------------------------------------------------

  async function extractDocxText(docxZipEntry) {
    const docxBuffer = await docxZipEntry.async("arraybuffer");
    const innerZip = await JSZip.loadAsync(docxBuffer);
    const documentXml = innerZip.file("word/document.xml");
    if (!documentXml) return "";

    const xml = await documentXml.async("string");
    // remove tags, mantém texto
    return xml.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  }

  // ---------------------------------------------------------------------
  // XLSX: zip com xl/worksheets/sheetN.xml + xl/sharedStrings.xml + workbook.xml
  // ---------------------------------------------------------------------

  async function checkExcelCells(excelZipEntry, verificacoes) {
    const buffer = await excelZipEntry.async("arraybuffer");
    const innerZip = await JSZip.loadAsync(buffer);

    const sheetNameToPath = await mapSheetNames(innerZip);
    const sharedStrings = await loadSharedStrings(innerZip);

    let okCount = 0;

    for (const check of verificacoes) {
      const sheetPath = sheetNameToPath[check.pagina];
      if (!sheetPath) continue;

      const sheetFile = innerZip.file(sheetPath);
      if (!sheetFile) continue;

      const sheetXml = await sheetFile.async("string");
      const cellRef = `${check.coluna}${check.linha}`;
      const value = readCellValue(sheetXml, cellRef, sharedStrings);

      if (value !== null && String(value).trim() === String(check.conteudo_esperado).trim()) {
        okCount++;
      }
    }

    return okCount;
  }

  async function mapSheetNames(innerZip) {
    const workbookXml = await innerZip.file("xl/workbook.xml").async("string");
    const relsFile = innerZip.file("xl/_rels/workbook.xml.rels");
    const relsXml = relsFile ? await relsFile.async("string") : "";

    const sheetRegex = /<sheet[^>]*name="([^"]+)"[^>]*r:id="([^"]+)"/g;
    const relRegex = /<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"/g;

    const relMap = {};
    let relMatch;
    while ((relMatch = relRegex.exec(relsXml)) !== null) {
      relMap[relMatch[1]] = relMatch[2];
    }

    const nameToPath = {};
    let sheetMatch;
    while ((sheetMatch = sheetRegex.exec(workbookXml)) !== null) {
      const [, name, rId] = sheetMatch;
      const target = relMap[rId];
      if (target) {
        nameToPath[name] = target.startsWith("/") ? target.slice(1) : `xl/${target}`;
      }
    }

    return nameToPath;
  }

  async function loadSharedStrings(innerZip) {
    const file = innerZip.file("xl/sharedStrings.xml");
    if (!file) return [];

    const xml = await file.async("string");
    const strings = [];
    const regex = /<si>(.*?)<\/si>/gs;
    let match;
    while ((match = regex.exec(xml)) !== null) {
      const textMatch = match[1].match(/<t[^>]*>(.*?)<\/t>/gs);
      const text = textMatch
        ? textMatch.map((t) => t.replace(/<[^>]+>/g, "")).join("")
        : "";
      strings.push(decodeXmlEntities(text));
    }
    return strings;
  }

  function readCellValue(sheetXml, cellRef, sharedStrings) {
    const cellRegex = new RegExp(
      `<c[^>]*r="${cellRef}"[^>]*?(/>|>(.*?)</c>)`,
      "s"
    );
    const match = sheetXml.match(cellRegex);
    if (!match) return null;

    const fullTag = match[0];
    const isSharedString = /t="s"/.test(fullTag);

    const valueMatch = fullTag.match(/<v>(.*?)<\/v>/s);
    if (!valueMatch) {
      const inlineMatch = fullTag.match(/<is><t[^>]*>(.*?)<\/t><\/is>/s);
      return inlineMatch ? decodeXmlEntities(inlineMatch[1]) : null;
    }

    const rawValue = valueMatch[1];
    if (isSharedString) {
      const idx = parseInt(rawValue, 10);
      return sharedStrings[idx] !== undefined ? sharedStrings[idx] : null;
    }
    return decodeXmlEntities(rawValue);
  }

  function decodeXmlEntities(text) {
    return text
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'")
      .replace(/&amp;/g, "&");
  }
})();
