function m1nItemsByRows(rowSet) {
  return (product?.items || []).filter((item) => rowSet.has(item.rowNumber));
}

function currentMSeriesStepRows() {
  if (isAvmProduct()) return AVM_STEP_ROWS;
  if (isM3nProduct()) return M3N_STEP_ROWS;
  if (isC6Product()) return C6_STEP_ROWS;
  return M1N_STEP_ROWS;
}

function currentMSeriesChannelRule() {
  return M_SERIES_CHANNEL_RULES[state.productId] || { ipc: 1, ahd: 1, recording: 1 };
}

const M_SERIES_INTERNAL_ALGORITHMS = ["adas", "dms", "left_bsd", "right_bsd", "rear_bsd"];

function mSeriesCameraResource(item) {
  const text = `${item?.name || ""} ${item?.group || ""}`.toLowerCase();
  // AD Kit 的随附支架/螺丝同属 "AD Kit" 分组；只有套装主件才占用接口和录像通道。
  const isAdkit = (isM1nProduct() && item?.rowNumber === 14) || (isM3nProduct() && item?.rowNumber === 13);
  if (isAdkit) return { type: "ipc", ipc: 1, ahd: 0, recording: 2, bundle: true, externalAlgorithms: ["adas", "dms"] };
  if (/c46/.test(text)) return { type: "ipc", ipc: 1, ahd: 0, recording: 1, bundle: false, externalAlgorithms: ["bsd"] };
  if (/ca20s|ca29m|ca46|square camera|方型机|metal conch|金属海螺|bsd|surveillance/.test(text)) {
    return { type: "ahd", ipc: 0, ahd: 1, recording: 1, bundle: false, externalAlgorithms: [] };
  }
  if (/c29n/.test(text)) return { type: "ipc", ipc: 1, ahd: 0, recording: 1, bundle: false, externalAlgorithms: [] };
  return null;
}

function mSeriesSelectionQuantity(item) {
  const resource = mSeriesCameraResource(item);
  const block = state.selections[item?.id];
  if (!resource || !block?.checked) return 0;
  return resource.bundle ? 1 : Number(block.quantity || 0);
}

function mSeriesAlgorithmLabel(id) {
  return {
    adas: "ADAS",
    dms: "DMS",
    left_bsd: "Left BSD",
    right_bsd: "Right BSD",
    rear_bsd: "Rear BSD",
  }[id] || id;
}

// AHD algorithms run in the MDVR, but their available functions still depend
// on the camera model. An empty list intentionally leaves the camera as
// recording-only (for example the New Metal Conch surveillance camera).
function mSeriesAllowedInternalAlgorithms(item) {
  const text = `${item?.name || ""} ${item?.group || ""}`.toLowerCase();
  if (/ca20s/.test(text)) return ["adas"];
  if (/ca29m/.test(text)) return ["dms"];
  if (/ca46/.test(text)) return ["left_bsd", "right_bsd", "rear_bsd"];
  if (/square camera|方型机/.test(text)) return ["rear_bsd"];
  return [];
}

function m3nCameraExtensionRows(item) {
  if (isM1nProduct()) {
    const text = `${item?.name || ""} ${item?.group || ""}`.toLowerCase();
    if (/c29n|ca20s|dms|adas/.test(text)) return [28, 29, 30];
    if (/ca29m|ca46|square camera|方型机|metal conch|金属海螺|bsd|surveillance/.test(text)) return [24, 25, 26, 27];
    return [];
  }
  const text = `${item?.name || ""} ${item?.group || ""}`.toLowerCase();
  if (/c29n|ca20s|dms|adas/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ipc;
  if (/ca29m/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ahd;
  if (/ca46|square camera|方型机|metal conch|金属海螺|bsd|surveillance/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ahd;
  return [];
}

function isM3nPresetCameraItem(item) {
  return Boolean(m3nPresetCameraType(item));
}

function m3nCameraExtensionRowsForMSeries(item) {
  const text = `${item?.name || ""} ${item?.group || ""}`.toLowerCase();
  if (/c29n/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ipc;
  if (/ca29m|ca20s/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ahd;
  if (/ca46|square camera|metal conch|bsd|surveillance/.test(text)) return M3N_CAMERA_EXTENSION_ROWS.ahd;
  return [];
}

function m3nPresetItemSelected(item) {
  if (!item) return false;
  if (isMSeriesProduct() && isM3nPresetCameraItem(item)) {
    const block = state.selections[item.id];
    return Boolean(block?.checked) && Number(block?.quantity || 0) > 0;
  }
  return Boolean(state.selections[item.id]?.checked);
}

function ensurePresetSelectionState(itemId, fallbackQuantity = "1") {
  if (!state.selections[itemId]) {
    state.selections[itemId] = { checked: false, quantity: fallbackQuantity };
  }
  return state.selections[itemId];
}

function isLockedPresetItem(item) {
  return isAvmProduct() && item?.rowNumber !== undefined && [13, 14].includes(item.rowNumber);
}

function maxM3nPresetQuantity(item) {
  const resource = mSeriesCameraResource(item);
  if (!resource || resource.bundle) return 1;
  const block = state.selections[item.id];
  const currentQty = block?.checked ? Number(block.quantity || 0) : 0;
  const status = m3nPresetCameraStatus();
  const interfaceRemaining = resource.type === "ipc" ? status.ipcRemaining : status.ahdRemaining;
  const recordingRemaining = Math.floor(status.recordingRemaining / resource.recording);
  return currentQty + Math.min(interfaceRemaining, recordingRemaining);
}

function presetVariantOptions(item) {
  if (!item) return null;
  if (isC6Product() && item.rowNumber === 24) return SD_CARD_VARIANTS;
  if (item.rowNumber === 37) return SD_CARD_VARIANTS;
  if (item.rowNumber === 38) return M2_SSD_VARIANTS;
  return null;
}

function setPresetVariant(itemId, partNumber) {
  const item = product?.items?.find((entry) => entry.id === itemId);
  const block = ensurePresetSelectionState(itemId, item?.quantity || "1");
  block.variantPartNumber = partNumber;
  render();
}

function setM3nPresetSelection(itemId, checked) {
  const item = product?.items?.find((entry) => entry.id === itemId);
  const block = ensurePresetSelectionState(itemId, item?.quantity || "1");
  const resource = mSeriesCameraResource(item);
  // Keep the channel reservation enforceable even if this setter is reached
  // without the disabled checkbox state (for example through restored state).
  if (checked && !block.checked && resource) {
    const status = m3nPresetCameraStatus();
    if (
      resource.ipc > status.ipcRemaining ||
      resource.ahd > status.ahdRemaining ||
      resource.recording > status.recordingRemaining
    ) return;
  }
  block.checked = checked;
  if (isM3nPresetCameraItem(item) && !resource?.bundle) {
    block.quantity = checked ? "1" : "0";
  }
  if (checked) {
    const extensionRows = m3nCameraExtensionRowsForMSeries(item).length
      ? m3nCameraExtensionRowsForMSeries(item)
      : m3nOptionalExtensionRows(item);
    if (extensionRows.length && !block.extensionId) {
      block.extensionId = findItemByRow(extensionRows[0])?.id || "";
    }
    for (const childRow of [...m3nAdkitChildRows(item), ...m3nOptionalChildRows(item)]) {
      const childItem = findItemByRow(childRow);
      if (childItem) ensurePresetSelectionState(childItem.id, childItem.quantity || "1").checked = true;
    }
  } else {
    block.extensionId = "";
    for (const childRow of [...m3nAdkitChildRows(item), ...m3nOptionalChildRows(item)]) {
      const childItem = findItemByRow(childRow);
      if (childItem) ensurePresetSelectionState(childItem.id, childItem.quantity || "1").checked = false;
    }
  }
  render();
}

function setMSeriesInternalAlgorithm(itemId, slot, algorithm) {
  const item = product?.items?.find((entry) => entry.id === itemId);
  const resource = mSeriesCameraResource(item);
  if (!resource?.ahd) return;
  const allowedAlgorithms = mSeriesAllowedInternalAlgorithms(item);
  if (algorithm && !allowedAlgorithms.includes(algorithm)) return;
  const block = ensurePresetSelectionState(itemId, item?.quantity || "1");
  const currentAlgorithms = [...(block.algorithms || [])];
  const usedElsewhere = m3nPresetCameraStatus().internalAlgorithms - (currentAlgorithms[slot] ? 1 : 0);
  if (algorithm && usedElsewhere >= 2) return;
  currentAlgorithms[slot] = algorithm;
  block.algorithms = currentAlgorithms;
  render();
}

function applyMSeriesAlgorithmPreset(presetId) {
  const cameraItems = m1nItemsByRows(currentMSeriesStepRows().cameras);
  const findCamera = (pattern) => cameraItems.find((item) => pattern.test(`${item.name || ""} ${item.group || ""}`));
  for (const item of cameraItems) {
    if (!mSeriesCameraResource(item)) continue;
    const block = ensurePresetSelectionState(item.id, item.quantity || "1");
    block.checked = false;
    block.quantity = 0;
    block.extensionId = "";
    block.extensions = [];
    block.algorithms = [];
  }
  if (presetId === "adkit_ca46") {
    const adkit = cameraItems.find((item) => mSeriesCameraResource(item)?.bundle);
    const ca46 = findCamera(/ca46/i);
    if (!adkit || !ca46) return;
    const adkitBlock = ensurePresetSelectionState(adkit.id, adkit.quantity || "1");
    adkitBlock.checked = true;
    adkitBlock.quantity = 1;
    for (const childRow of m3nAdkitChildRows(adkit)) {
      const childItem = findItemByRow(childRow);
      if (childItem) ensurePresetSelectionState(childItem.id, childItem.quantity || "1").checked = true;
    }
    const ca46Block = ensurePresetSelectionState(ca46.id, ca46.quantity || "1");
    const extensionId = findItemByRow(M3N_CAMERA_EXTENSION_ROWS.ahd[0])?.id || "";
    ca46Block.checked = true;
    ca46Block.quantity = 2;
    ca46Block.extensions = [extensionId, extensionId];
    ca46Block.extensionId = extensionId;
    ca46Block.algorithms = ["left_bsd", "right_bsd"];
  } else if (presetId === "c46_ca20s_ca29m") {
    const c46 = findCamera(/c46(?!.*ca46)/i);
    const ca20s = findCamera(/ca20s/i);
    const ca29m = findCamera(/ca29m/i);
    if (!c46 || !ca20s || !ca29m) return;
    const c46Block = ensurePresetSelectionState(c46.id, c46.quantity || "1");
    c46Block.checked = true;
    c46Block.quantity = 2;
    const extensionId = findItemByRow(M3N_CAMERA_EXTENSION_ROWS.ahd[0])?.id || "";
    for (const [item, algorithm] of [[ca20s, "adas"], [ca29m, "dms"]]) {
      const block = ensurePresetSelectionState(item.id, item.quantity || "1");
      block.checked = true;
      block.quantity = 1;
      block.extensionId = extensionId;
      block.extensions = [extensionId];
      block.algorithms = [algorithm];
    }
  } else {
    return;
  }
  render();
}

function setM3nPresetQuantity(itemId, nextQuantity) {
  const item = product?.items?.find((entry) => entry.id === itemId);
  if (!item) return;
  const block = ensurePresetSelectionState(itemId, item.quantity || "1");
  const maxQty = Math.max(0, maxM3nPresetQuantity(item));
  const quantity = Math.max(0, Math.min(maxQty, Number(nextQuantity || 0)));
  const defaultExtensionRows = m3nCameraExtensionRowsForMSeries(item);
  const defaultExtensionId = defaultExtensionRows.length ? findItemByRow(defaultExtensionRows[0])?.id || "" : "";
  block.quantity = quantity;
  block.checked = quantity > 0;
  block.extensions = Array.from({ length: quantity }, (_, index) => block.extensions?.[index] || defaultExtensionId);
  block.extensionId = block.extensions[0] || "";
  render();
}

function setM3nPresetChildSelection(itemId, checked) {
  const item = product?.items?.find((entry) => entry.id === itemId);
  const block = ensurePresetSelectionState(itemId, item?.quantity || "1");
  block.checked = checked;
  render();
}

function setM3nPresetCameraExtension(itemId, rowNumber, slot = 0) {
  const block = ensurePresetSelectionState(itemId);
  if (rowNumber === "none") {
    block.extensionId = "";
    if (Array.isArray(block.extensions)) block.extensions[slot] = "";
    render();
    return;
  }
  const extensionId = findItemByRow(Number(rowNumber))?.id || "";
  block.extensionId = extensionId;
  if (!Array.isArray(block.extensions)) block.extensions = [];
  block.extensions[slot] = extensionId;
  render();
}

function m3nPresetCameraType(item) {
  return mSeriesCameraResource(item)?.type || null;
}

function m3nAdkitChildRows(item) {
  if (!item) return [];
  if (isM1nProduct() && item.rowNumber === 14) return [15, 16];
  if (isM3nProduct() && item.rowNumber === 13) return [14, 15];
  return [];
}

function m3nOptionalChildRows(item) {
  if (!item) return [];
  if (isM1nProduct()) {
    if (item.rowNumber === 8) return [9];
    if (item.rowNumber === 31) return [32];
    if (item.rowNumber === 34) return [35];
    return [];
  }
  if (isM3nProduct()) {
    if (item.rowNumber === 8) return [9];
    if (item.rowNumber === 31) return [32];
    if (item.rowNumber === 34) return [35];
    return [];
  }
  if (item.rowNumber === 34) return [35];
  if (item.rowNumber === 36) return [33];
  return [];
}

function m3nOptionalExtensionRows(item) {
  if (!item) return [];
  if ([18, 19].includes(item.rowNumber)) return M3N_CAMERA_EXTENSION_ROWS.ipc;
  if (item.rowNumber === 31) return M3N_CAMERA_EXTENSION_ROWS.ahd;
  return [];
}

function m3nOptionalDisplay(item) {
  if (!item) return { name: "", note: "", preview: "" };
  if (item.rowNumber === 8) {
    return {
      name: "Microphone",
      note: "Choose when audio pickup is needed. The adapter cable is included below.",
      preview: fallbackItemPreviewAsset(item),
    };
  }
  const info = skuInfo(item.partNumber);
  return {
    name: info?.title ? localizedText(info.title) : displayCatalogText(item.name),
    note: info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(item.note || item.description || ""),
    preview: info?.image || fallbackItemPreviewAsset(item),
  };
}

function m3nPresetCameraStatus() {
  const channelRule = currentMSeriesChannelRule();
  const selectedItems = m1nItemsByRows(currentMSeriesStepRows().cameras).filter((item) => mSeriesSelectionQuantity(item) > 0);
  const reserved = avmCascadeReserved();
  const totals = selectedItems.reduce(
    (sum, item) => {
      const resource = mSeriesCameraResource(item);
      const quantity = mSeriesSelectionQuantity(item);
      const block = state.selections[item.id] || {};
      sum.ipc += resource.ipc * quantity;
      sum.ahd += resource.ahd * quantity;
      sum.recording += resource.recording * quantity;
      const allowedAlgorithms = mSeriesAllowedInternalAlgorithms(item);
      sum.internalAlgorithms += (block.algorithms || []).filter((algorithm) => allowedAlgorithms.includes(algorithm)).length;
      sum.externalAlgorithms += resource.externalAlgorithms.length * quantity;
      return sum;
    },
    { ipc: reserved.ipc, ahd: reserved.ahd, recording: reserved.recording, internalAlgorithms: 0, externalAlgorithms: 0 }
  );
  return {
    ...totals,
    ipcRemaining: Math.max(0, channelRule.ipc - totals.ipc),
    ahdRemaining: Math.max(0, channelRule.ahd - totals.ahd),
    recordingRemaining: Math.max(0, channelRule.recording - totals.recording),
    internalAlgorithmsRemaining: Math.max(0, 2 - totals.internalAlgorithms),
  };
}

function renderM1nSelectableStep(items, summaryLabel) {
  const grouped = groupedItems(items);
  const itemCard = (item) => {
    const locked = isLockedPresetItem(item);
    const checked = (locked || state.selections[item.id]?.checked) ? "checked" : "";
    const selected = checked ? "selected" : "";
    const variantOptions = presetVariantOptions(item);
    const selectedVariantPart = state.selections[item.id]?.variantPartNumber;
    const selectedVariant = variantOptions?.find((entry) => entry.partNumber === selectedVariantPart) || variantOptions?.[0] || null;
    // Variant items (storage) keep their per-variant name; everything else can use the shared SKU library.
    const info = variantOptions ? null : skuInfo(item.partNumber);
    const preview = info?.image || fallbackItemPreviewAsset(item);
    const headingName = variantOptions ? localizedText(selectedVariant.name) : (info?.title ? localizedText(info.title) : displayCatalogText(item.name));
    const detailText = info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(item.note || item.description || "");
    return `
      <section class="group-card accessory-row-group">
        <label class="item-card accessory-row-card ${selected}">
          <div class="accessory-row-media">
            ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${headingName}" />` : `<div class="thumb"></div>`}
          </div>
          <div class="accessory-row-copy">
            <h4>${headingName}</h4>
            <div class="sku">${variantOptions ? selectedVariant.partNumber : item.partNumber || t().noPartNumber}</div>
            <p>${detailText}</p>
          </div>
          <div class="accessory-row-control">
            <input type="checkbox" data-selection="${item.id}" ${checked} ${locked ? "disabled" : ""} />
          </div>
        </label>
        ${
          checked && variantOptions
            ? `
              <div class="extension-picker">
                <div class="extension-picker-head">
                  <strong>${L("容量 / 料号", "Capacity / part number")}</strong>
                  <span>${"Maximum 1 unit"}</span>
                </div>
                <label>
                  <span>${L("选择规格", "Choose variant")}</span>
                  <select data-preset-variant="${item.id}">
                    ${variantOptions
                      .map((variant) => `<option value="${variant.partNumber}" ${selectedVariant.partNumber === variant.partNumber ? "selected" : ""}>${localizedText(variant.name)} | ${variant.partNumber}</option>`)
                      .join("")}
                  </select>
                </label>
              </div>
            `
            : ""
        }
      </section>
    `;
  };
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${summaryLabel}</strong>
        <p>${currentPackage() ? displayCatalogText(currentPackage().name) : "-"}</p>
      </div>
    </div>
    <div class="group-list accessory-vertical-list">
      ${Object.entries(grouped)
        .map(([groupName, groupItems]) =>
          // Only keep a group header when it actually groups several parts; singletons render flat.
          groupItems.length >= 2
            ? `
              <section class="group-card">
                <div class="group-meta">
                  <h3>${displayCatalogText(groupName)}</h3>
                  <div class="group-badge">${groupItems.length}</div>
                </div>
                <div class="group-list accessory-vertical-list">
                  ${groupItems.map(itemCard).join("")}
                </div>
              </section>
            `
            : groupItems.map(itemCard).join("")
        )
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-selection]").forEach((node) => {
    node.addEventListener("change", (event) => {
      if (!state.selections[node.dataset.selection]) {
        state.selections[node.dataset.selection] = { checked: false, quantity: "1" };
      }
      state.selections[node.dataset.selection].checked = event.target.checked;
      render();
    });
  });
  wizardStageEl.querySelectorAll("[data-preset-variant]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setPresetVariant(node.dataset.presetVariant, event.target.value);
    });
  });
}
