function renderReviewStep() {
  const rows = selectedItems();
  wizardStageEl.innerHTML = `
    <div class="review-card">
      <h3>${t().reviewTitle}</h3>
      <div class="review-meta">
        <p><strong>${t().summaryFields.product}:</strong> ${product.title}</p>
        <p><strong>${t().summaryFields.scenario}:</strong> ${localizedText(currentScenario()?.title || "") || "-"}</p>
        ${
          isCustomFlow()
            ? `
              <p><strong>${t().summaryFields.host}:</strong> ${selectedCustomHost() ? localizedText(selectedCustomHost().title) : "-"}</p>
              <p><strong>${t().summaryFields.powerBox}:</strong> ${selectedCustomPowerBox() ? localizedText(selectedCustomPowerBox().title) : "-"}</p>
              <p><strong>${t().summaryFields.wiring}:</strong> ${selectedCustomWirings().map((item) => localizedText(item.title)).join(" / ") || "-"}</p>
              <p><strong>${t().summaryFields.optionals}:</strong> ${selectedCustomOptionalDefs().map((item) => localizedText(item.title)).join(" / ") || t().noneSelected}</p>
            `
            : `
              <p><strong>${t().summaryFields.package}:</strong> ${currentPackage() ? displayCatalogText(currentPackage().name) : "-"}</p>
            `
        }
        <p><strong>${t().summaryFields.itemCount}:</strong> ${rows.length}</p>
      </div>
      <p class="hint">${t().reviewHint}</p>
    </div>
  `;
}

function kitLabel(kind) {
  if (kind === "base") return L("当前基础套装", "Current base kit");
  return L("当前核心套装", "Current core kit");
}

function renderStage() {
  if (isC6Product()) normalizeC6Selections();
  if (state.productPickerOpen) {
    renderScenarioStep();
    return;
  }
  if (state.step === 1) {
    if (isC6Product()) renderC6BaseStep();
    else if (isAvmProduct()) renderAvm2BaseStep();
    else if (is960C53Product()) renderC53BaseStep();
    else if (isMSeriesProduct()) renderM1nBaseStep();
    else if (isZ5Product()) renderZ5CoreStep();
    else if (isPresetPackageProduct()) renderPresetPackageStep();
    else renderScenarioStep();
    return;
  }
  if (!isCustomFlow()) {
    if (isMSeriesProduct()) {
      if (state.step === 2) renderM1nWiringStep();
      else if (state.step === 3) renderM1nCameraStep();
      else if (state.step === 4) renderM1nOptionalStep();
      else renderReviewStep();
      return;
    }
    // AVM bespoke steps: mandatory cameras, then host connection and screen.
    if (isAvmProduct()) {
      if (state.step === 2) { renderAvm2CameraStep(); return; }
      if (state.step === 3) { renderAvm2WiringStep(); return; }
      if (state.avm?.mode === "standalone") { renderReviewStep(); return; }
    }
    if (is960C53Product()) {
      if (state.step === 2) { renderC53SetupStep(); return; }
      if (state.step === 3) { renderC53DisplayStep(); return; }
      if (state.step === 4 && state.c53?.mode === "cascade") { renderC53HostStep(); return; }
      renderReviewStep();
      return;
    }
    // C6 Lite uses bespoke, AD-Plus-style step screens (built in stages).
    if (isC6Product()) {
      if (state.step === 2) {
        renderC6WiringStep();
        return;
      }
      if (state.step === 3) {
        renderC6CameraStep();
        return;
      }
      if (state.step === 4) {
        renderC6AccessoryStep();
        return;
      }
    }
    const meta = PRODUCT_META[state.productId];
    if (isZ5Product()) {
      if (state.step === 2) renderZ5StorageStep();
      else renderReviewStep();
      return;
    }
    if (meta?.selectable) {
      const rowKey = meta.selectable.map[state.step];
      if (rowKey) renderM1nSelectableStep(m1nItemsByRows(meta.selectable.rows[rowKey]), kitLabel(meta.kit));
      else renderReviewStep();
      return;
    }
    if (state.step === 2) renderPresetPackageStep();
    else if (state.step === 3) renderPresetAccessoryStep();
    else renderReviewStep();
    return;
  }
  if (state.step === 2) renderCustomHostStep();
  else if (state.step === 3) renderCustomPowerBoxStep();
  else if (state.step === 4) renderCustomWiringStep();
  else if (state.step === 5) renderCustomAccessoryStep();
  else if (state.step === 6) renderCustomOptionalStep();
  else renderReviewStep();
}

function renderSummary() {
  if (state.productPickerOpen) {
    summaryMetaEl.innerHTML = `
      <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
      <p><strong>${t().summaryFields.scenario}:</strong> ${localizedText(currentScenario()?.title || "") || t().noneSelected}</p>
    `;
    cartListEl.innerHTML = `<p class="empty">${t().rightBlank}</p>`;
    return;
  }
  if (state.step === 1 && !isZ5Product()) {
    if (isPresetPackageProduct()) {
      summaryMetaEl.innerHTML = `
        <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
        <p><strong>${t().summaryFields.package}:</strong> ${currentPackage() ? displayCatalogText(currentPackage().name) : t().noneSelected}</p>
      `;
    } else {
      summaryMetaEl.innerHTML = `
        <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
        <p><strong>${t().summaryFields.scenario}:</strong> ${localizedText(currentScenario()?.title || "") || t().noneSelected}</p>
      `;
    }
    cartListEl.innerHTML = `<p class="empty">${t().rightBlank}</p>`;
    return;
  }

  const rows = selectedItems();
  if (isCustomFlow()) {
    summaryMetaEl.innerHTML = `
      <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
      <p><strong>${t().summaryFields.host}:</strong> ${selectedCustomHost() ? localizedText(selectedCustomHost().title) : t().noneSelected}</p>
      <p><strong>${t().summaryFields.powerBox}:</strong> ${selectedCustomPowerBox() ? localizedText(selectedCustomPowerBox().title) : t().noneSelected}</p>
      <p><strong>${t().summaryFields.wiring}:</strong> ${selectedCustomWirings().map((item) => localizedText(item.title)).join(" / ") || t().noneSelected}</p>
      <p><strong>${t().summaryFields.wiringNote}:</strong> ${wiringSummaryText() || t().noneSelected}</p>
      <p><strong>${t().summaryFields.optionals}:</strong> ${selectedCustomOptionalDefs().map((item) => localizedText(item.title)).join(" / ") || t().noneSelected}</p>
    `;
    if (!rows.length) {
      cartListEl.innerHTML = `<p class="empty">${t().rightBlank}</p>`;
      return;
    }
  } else {
    const scenario = currentScenario();
    const pkg = currentPackage();
    summaryMetaEl.innerHTML = isZ5Product()
      ? `
        <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
        <p><strong>${L("Core kit", "Core kit")}:</strong> ${pkg ? displayCatalogText(pkg.name) : t().noneSelected}</p>
        <p><strong>SKU:</strong> ${pkg?.partNumber || t().noneSelected}</p>
        <p><strong>${t().summaryFields.itemCount}:</strong> ${rows.length}</p>
      `
      : isPresetPackageProduct()
      ? `
        <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
        <p><strong>${L("基础套装", "Base kit")}:</strong> ${pkg ? displayCatalogText(pkg.name) : t().noneSelected}</p>
        <p><strong>${t().summaryFields.package}:</strong> ${pkg?.partNumber || t().noneSelected}</p>
        <p><strong>${t().summaryFields.itemCount}:</strong> ${rows.length}</p>
      `
      : `
        <p><strong>${t().summaryFields.product}:</strong> ${product?.title || "-"}</p>
        <p><strong>${t().summaryFields.solution}:</strong> ${localizedText(scenario?.title || "") || "-"}</p>
        <p><strong>${t().summaryFields.package}:</strong> ${pkg?.partNumber || t().noneSelected}</p>
        <p><strong>${t().summaryFields.itemCount}:</strong> ${rows.length}</p>
      `;
    if (!rows.length) {
      cartListEl.innerHTML = `<p class="empty">${t().noItems}</p>`;
      return;
    }
  }

  const selectedAccessoryDefs = selectedCustomAccessoryDefs();
  const shouldShowVideoNote =
    isCustomFlow() &&
    selectedAccessoryDefs.some((def) => {
      if (def.cameraType) return true;
      if (def.id === "screen") return selectedCustomPowerBox()?.id !== "max";
      return false;
    });
  const summaryNote = shouldShowVideoNote ? `<div class="helper-note">${t().summaryNoteVideo}</div>` : "";

  cartListEl.innerHTML =
    summaryNote +
    rows
      .map(
        (row) => `
          <div class="cart-row">
            <div>
            <strong>${displayCatalogText(row.name || row.group)}</strong>
            <div class="sku">${row.partNumber || t().noPartNumber}</div>
            <div class="hint">${displayCatalogText(row.group)}</div>
          </div>
            <div>x ${row.quantity}</div>
          </div>
        `
      )
      .join("");
}

function renderStaticContent() {
  document.documentElement.lang = L("zh-CN", "en");
  document.body.classList.toggle("compact-flow", state.step > 1);
  document.title = t().docTitle;
  const activeProductTitle = String(product?.title || "").replace(/_/g, ".");
  document.getElementById("hero-eyebrow").textContent = state.productPickerOpen
    ? t().heroEyebrow
    : (activeProductTitle || t().heroEyebrow);
  document.getElementById("hero-title").textContent = t().heroTitle;
  document.getElementById("hero-intro").textContent = t().heroIntro;
  document.getElementById("highlight-1").textContent = t().heroHighlights[0];
  document.getElementById("highlight-2").textContent = t().heroHighlights[1];
  document.getElementById("highlight-3").textContent = t().heroHighlights[2];
  document.getElementById("hero-note-label").textContent = t().heroNoteLabel;
  document.getElementById("hero-note-title").textContent = t().heroNoteTitle;
  document.getElementById("hero-note-body").textContent = t().heroNoteBody;
  document.getElementById("summary-step").textContent = t().summaryStep;
  document.getElementById("summary-title").textContent = t().summaryTitle;
  prevStepBtn.textContent = t().prev;
  exportExcelBtn.textContent = t().exportExcel;
}

function render() {
  renderStaticContent();
  renderStepPills();
  renderStage();
  renderSummary();
  updateStepControls();

  wizardStageEl.querySelectorAll("[data-extension-kind]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const kind = node.dataset.extensionKind;
      const id = node.dataset.extensionId;
      const slot = Number(node.dataset.extensionSlot || 0);
      const field = node.dataset.extensionField || "extension";
      if (kind === "accessory") setAccessoryExtension(id, event.target.value, slot, field);
      if (kind === "optional") setOptionalExtension(id, event.target.value, slot);
    });
  });
}

function downloadFile(filename, content, type) {
  const blob = content instanceof Blob ? content : new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function xmlEscape(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function zipCrc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function zipStore(entries) {
  const encoder = new TextEncoder();
  const chunks = [];
  const directory = [];
  let offset = 0;
  const write = (size, callback) => {
    const output = new Uint8Array(size);
    callback(new DataView(output.buffer));
    return output;
  };

  entries.forEach(({ name, content }) => {
    const nameBytes = encoder.encode(name);
    const body = encoder.encode(content);
    const crc = zipCrc32(body);
    const header = write(30 + nameBytes.length, (view) => {
      view.setUint32(0, 0x04034b50, true);
      view.setUint16(4, 20, true);
      view.setUint16(6, 0x0800, true);
      view.setUint32(14, crc, true);
      view.setUint32(18, body.length, true);
      view.setUint32(22, body.length, true);
      view.setUint16(26, nameBytes.length, true);
    });
    header.set(nameBytes, 30);
    chunks.push(header, body);
    directory.push({ nameBytes, crc, size: body.length, offset });
    offset += header.length + body.length;
  });

  const directoryOffset = offset;
  directory.forEach((entry) => {
    const header = write(46 + entry.nameBytes.length, (view) => {
      view.setUint32(0, 0x02014b50, true);
      view.setUint16(4, 20, true);
      view.setUint16(6, 20, true);
      view.setUint16(8, 0x0800, true);
      view.setUint32(16, entry.crc, true);
      view.setUint32(20, entry.size, true);
      view.setUint32(24, entry.size, true);
      view.setUint16(28, entry.nameBytes.length, true);
      view.setUint32(42, entry.offset, true);
    });
    header.set(entry.nameBytes, 46);
    chunks.push(header);
    offset += header.length;
  });

  chunks.push(
    write(22, (view) => {
      view.setUint32(0, 0x06054b50, true);
      view.setUint16(8, directory.length, true);
      view.setUint16(10, directory.length, true);
      view.setUint32(12, offset - directoryOffset, true);
      view.setUint32(16, directoryOffset, true);
    })
  );
  return new Blob(chunks, { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
}

function createOpportunityImportWorkbook(rows) {
  const importNotes = [
    "Sort by Arabic numerals in order,\neg:1",
    "Required, Product Number, \neg:3390001100003",
    "Required",
    "Optional,integer",
    "Required, Dongguan factory/Vitnam Factory",
    "Optional, True/False",
    "Optional",
  ];
  const headers = ["SortOrder", "Product Code*", "Quantity*", "Sales Price", "Factory*", "Is Substitute Material", "Description"];
  const inlineCell = (reference, value, style = "") =>
    `<c r="${reference}" t="inlineStr"${style}><is><t>${xmlEscape(value)}</t></is></c>`;
  const numberCell = (reference, value, style = "") => `<c r="${reference}"${style}><v>${value}</v></c>`;
  const sheetRows = [
    `<row r="1" ht="72" customHeight="1">${importNotes.map((note, index) => inlineCell(`${String.fromCharCode(65 + index)}1`, note, ' s="3"')).join("")}</row>`,
    `<row r="2">${headers.map((header, index) => inlineCell(`${String.fromCharCode(65 + index)}2`, header)).join("")}</row>`,
    ...rows.map((row, index) => {
      const rowNumber = index + 3;
      const material = String(row.partNumber || "").trim();
      const quantity = Math.max(1, Number.parseInt(String(row.quantity || "1"), 10) || 1);
      return `<row r="${rowNumber}">${numberCell(`A${rowNumber}`, index + 1)}${inlineCell(`B${rowNumber}`, material, ' s="2"')}${numberCell(`C${rowNumber}`, quantity, ' s="1"')}${numberCell(`D${rowNumber}`, 1, ' s="1"')}${inlineCell(`E${rowNumber}`, "Vietnam factory")}</row>`;
    }),
  ].join("");
  const lastRow = Math.max(2, rows.length + 2);
  const worksheet = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:G${lastRow}"/><sheetFormatPr defaultRowHeight="15"/><cols><col min="2" max="2" width="20.7230769230769" customWidth="1"/><col min="3" max="3" width="10.6307692307692" customWidth="1"/><col min="4" max="4" width="15.0923076923077" customWidth="1"/><col min="5" max="5" width="18.1769230769231" customWidth="1"/><col min="6" max="6" width="25" customWidth="1"/><col min="7" max="7" width="13.0923076923077" customWidth="1"/></cols><sheetData>${sheetRows}</sheetData></worksheet>`;
  const styles = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="0_ "/></numFmts><fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/><scheme val="minor"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"><alignment vertical="center"/></xf></cellStyleXfs><cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"><alignment vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles><tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/></styleSheet>`;
  return zipStore([
    { name: "[Content_Types].xml", content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>` },
    { name: "_rels/.rels", content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>` },
    { name: "xl/workbook.xml", content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Dates" sheetId="1" r:id="rId1"/></sheets></workbook>` },
    { name: "xl/_rels/workbook.xml.rels", content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>` },
    { name: "xl/worksheets/sheet1.xml", content: worksheet },
    { name: "xl/styles.xml", content: styles },
  ]);
}

function exportExcel() {
  const rows = selectedItems().filter((row) => String(row.partNumber || "").trim());
  const workbook = createOpportunityImportWorkbook(rows);
  downloadFile(
    `opportunity-product-import-${state.productId || "product"}.xlsx`,
    workbook,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
  reportSolutionExport(rows);
}

function analyticsSessionId() {
  const key = "sales-configurator-session-id";
  let sessionId = localStorage.getItem(key);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(key, sessionId);
  }
  return sessionId;
}

function activeBuildContext() {
  return {
    version: APP_VERSION,
    sessionId: analyticsSessionId(),
    productId: state.productId,
    productName: product?.title || state.productId,
    step: state.step,
    items: selectedItems().filter((item) => String(item.partNumber || "").trim()).map((item) => ({
      partNumber: String(item.partNumber || "").trim(),
      name: String(item.name || "").trim(),
      quantity: String(item.quantity || "1"),
    })),
  };
}

function postToServer(path, payload) {
  if (window.location.protocol === "file:") return Promise.reject(new Error("The feedback server is unavailable when opening the HTML file directly."));
  return fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then((response) => {
    if (!response.ok) throw new Error("The server could not save this request.");
    return response.json();
  });
}

function reportSolutionExport(rows) {
  const context = activeBuildContext();
  context.items = rows.map((item) => ({
    partNumber: String(item.partNumber || "").trim(),
    name: String(item.name || "").trim(),
    quantity: String(item.quantity || "1"),
  }));
  postToServer("/api/solutions", context).catch(() => {
    // Export remains available when the site is opened locally or telemetry is temporarily offline.
  });
}

function openFeedbackDialog() {
  feedbackStatus.textContent = "";
  feedbackForm.reset();
  if (typeof feedbackDialog.showModal === "function") feedbackDialog.showModal();
  else feedbackStatus.textContent = "Feedback requires a modern browser.";
}

function closeFeedbackDialog() {
  if (feedbackDialog.open) feedbackDialog.close();
}

let annotationModeActive = false;
let annotationContext = null;
let annotationSelectedElement = null;

function annotationLabel(element) {
  const explicitLabel = element.getAttribute("data-comment-label");
  if (explicitLabel) return explicitLabel.trim().slice(0, 240);
  const text = (element.getAttribute("aria-label") || element.innerText || element.alt || "").replace(/\s+/g, " ").trim();
  if (text) return text.slice(0, 240);
  return element.id || element.getAttribute("data-comment-id") || element.tagName.toLowerCase();
}

function annotationSelector(element) {
  if (element.id) return `#${element.id}`;
  const commentId = element.getAttribute("data-comment-id");
  if (commentId) return `[data-comment-id="${commentId.replace(/"/g, "\\\"")}"]`;
  const classes = [...element.classList].filter((name) => !name.startsWith("annotation-")).slice(0, 3);
  return `${element.tagName.toLowerCase()}${classes.map((name) => `.${name}`).join("")}` || element.tagName.toLowerCase();
}

function getAnnotationTarget(node) {
  if (!(node instanceof Element)) return null;
  if (node.closest(".topbar")) return null;
  const target = node.closest("[data-comment-id], button, label, .scenario-card, .package-card, .item-card, .option-card, .group-card, .storage-card, .wiring-card, .review-card, .summary, .wizard-stage, .wizard-actions, .cart-actions, img, h1, h2, h3, h4, p");
  if (!target || !document.querySelector(".shell")?.contains(target)) return null;
  return target;
}

function setAnnotationMode(active) {
  annotationModeActive = active;
  document.body.classList.toggle("annotation-mode", active);
  annotationButton.setAttribute("aria-pressed", String(active));
  annotationButton.textContent = active ? "Click an element" : "Annotate";
}

function clearAnnotationSelection() {
  annotationSelectedElement?.classList.remove("annotation-selected");
  annotationSelectedElement = null;
  annotationContext = null;
}

async function openAnnotationDialog(element) {
  clearAnnotationSelection();
  annotationSelectedElement = element;
  annotationSelectedElement.classList.add("annotation-selected");
  const rect = element.getBoundingClientRect();
  annotationContext = {
    targetLabel: annotationLabel(element),
    targetSelector: annotationSelector(element),
    targetText: (element.innerText || element.alt || "").replace(/\s+/g, " ").trim().slice(0, 1000),
    targetBounds: {
      x: Math.round(rect.left + window.scrollX), y: Math.round(rect.top + window.scrollY),
      width: Math.round(rect.width), height: Math.round(rect.height),
    },
    reviewState: JSON.parse(JSON.stringify(state)),
  };
  annotationForm.reset();
  annotationStatus.textContent = "The review team will see this element highlighted in its page view.";
  annotationTarget.textContent = `Selected element: ${annotationContext.targetLabel}`;
  if (typeof annotationDialog.showModal === "function") annotationDialog.showModal();
}

function closeAnnotationDialog() {
  if (annotationDialog.open) annotationDialog.close();
  clearAnnotationSelection();
}

function submitAnnotation(event) {
  event.preventDefault();
  const message = annotationMessage.value.trim();
  if (!message || !annotationContext) return;
  annotationStatus.textContent = "Sending…";
  const submitButton = annotationForm.querySelector("button[type=submit]");
  submitButton.disabled = true;
  postToServer("/api/annotations", {
    ...activeBuildContext(),
    ...annotationContext,
    message,
    contact: annotationContact.value.trim(),
    pageUrl: window.location.href,
  }).then(() => {
    annotationStatus.textContent = "Thank you. Your annotation has been sent.";
    annotationForm.reset();
  }).catch((error) => {
    annotationStatus.textContent = error.message || "Annotation could not be sent. Please try again later.";
  }).finally(() => {
    submitButton.disabled = false;
  });
}

function openReleaseDialog() {
  releaseContent.replaceChildren(...APP_RELEASE_NOTES.map((release) => {
    const entry = document.createElement("article");
    entry.className = "release-history-entry";

    const heading = document.createElement("h3");
    heading.textContent = `${release.version} — ${release.date}`;

    const notes = document.createElement("ul");
    notes.replaceChildren(...release.notes.map((note) => {
      const item = document.createElement("li");
      item.textContent = note;
      return item;
    }));

    entry.append(heading, notes);
    return entry;
  }));
  if (typeof releaseDialog.showModal === "function") releaseDialog.showModal();
}

function closeReleaseDialog() {
  if (releaseDialog.open) releaseDialog.close();
}

function submitFeedback(event) {
  event.preventDefault();
  const message = feedbackMessage.value.trim();
  if (!message) return;
  feedbackStatus.textContent = "Sending…";
  const submitButton = feedbackForm.querySelector("button[type=submit]");
  submitButton.disabled = true;
  postToServer("/api/feedback", {
    ...activeBuildContext(),
    message,
    contact: feedbackContact.value.trim(),
    pageUrl: window.location.href,
  }).then(() => {
    feedbackStatus.textContent = "Thank you. Your feedback has been sent.";
    feedbackForm.reset();
  }).catch((error) => {
    feedbackStatus.textContent = error.message || "Feedback could not be sent. Please try again later.";
  }).finally(() => {
    submitButton.disabled = false;
  });
}

function setLanguage(language) {
  if (!LANGS.includes(language)) return;
  state.language = language;
  render();
}

prevStepBtn.addEventListener("click", () => {
  if (avmCascadeActive() && !state.productPickerOpen && state.step === (isAdplusProduct() ? 2 : 1)) {
    avmReturnFromHostFlow();
    return;
  }
  if (c53CascadeActive() && !state.productPickerOpen && state.step === (isAdplusProduct() ? 2 : 1)) {
    c53ReturnFromHostFlow();
    return;
  }
  if (isAdplusProduct() && !state.productPickerOpen && state.step === 2) {
    state.productPickerOpen = true;
    state.step = 1;
    render();
    return;
  }
  if (state.step > 1) {
    state.step -= 1;
    render();
    return;
  }
  if (!state.productPickerOpen && state.step === 1) {
    state.productPickerOpen = true;
    render();
  }
});

nextStepBtn.addEventListener("click", () => {
  if (!validateCurrentStep()) return;
  if (is960C53Product() && state.c53?.mode === "standalone" && state.step === 2) {
    const gpsItems = (product?.items || []).filter((item) => [19, 20, 21].includes(item.rowNumber));
    const gps = gpsItems.find((item) => state.selections[item.id]?.checked) || gpsItems[0];
    if (gps) {
      gpsItems.forEach((item) => {
        const block = ensurePresetSelectionState(item.id, item.quantity || "1");
        block.checked = item.id === gps.id;
        block.quantity = item.id === gps.id ? "1" : "0";
      });
    }
  }
  if (state.productPickerOpen) {
    state.productPickerOpen = false;
    state.step = isAdplusProduct() ? 2 : 1;
    render();
    return;
  }
  if (isAvmProduct() && state.avm?.mode === "cascade" && state.step === 3) {
    avmEnterHostFlow();
    return;
  }
  if (is960C53Product() && state.c53?.mode === "cascade" && state.step === 4) {
    c53EnterHostFlow();
    return;
  }
  if (state.step < currentSteps().length) {
    state.step += 1;
    render();
  }
});

exportExcelBtn.addEventListener("click", exportExcel);
feedbackButton.addEventListener("click", openFeedbackDialog);
feedbackForm.addEventListener("submit", submitFeedback);
document.querySelectorAll("[data-feedback-close]").forEach((button) => button.addEventListener("click", closeFeedbackDialog));
annotationButton.addEventListener("click", () => setAnnotationMode(!annotationModeActive));
annotationForm.addEventListener("submit", submitAnnotation);
document.querySelectorAll("[data-annotation-close]").forEach((button) => button.addEventListener("click", closeAnnotationDialog));
document.querySelector(".shell").addEventListener("click", (event) => {
  if (!annotationModeActive) return;
  const target = getAnnotationTarget(event.target);
  if (!target) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  setAnnotationMode(false);
  void openAnnotationDialog(target);
}, true);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && annotationModeActive) setAnnotationMode(false);
});
window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin || event.data?.type !== "annotation-review-state") return;
  const reviewState = event.data.state;
  if (!reviewState || typeof reviewState !== "object") return;
  const safeState = JSON.parse(JSON.stringify(reviewState));
  Object.assign(state, safeState, { language: "en" });
  render();
});
document.getElementById("app-version").addEventListener("click", openReleaseDialog);
document.querySelectorAll("[data-release-close]").forEach((button) => button.addEventListener("click", closeReleaseDialog));

document.getElementById("app-version").textContent = `Beta ${APP_VERSION}`;

if (product) {
  resetScenarioState();
}

render();
document.documentElement.classList.remove("app-loading");
