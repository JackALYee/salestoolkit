function c6Items(rows) {
  return (product?.items || []).filter((item) => rows.includes(item.rowNumber));
}

// AVM 2.0 flow. These helpers deliberately construct the fixed AVM BOM instead
// of relying on generic checkbox state: every AVM always has four cameras,
// four camera leads and one calibration-cloth set.
function avmState() {
  state.avm = state.avm || {};
  state.avm.mode = state.avm.mode || "standalone";
  state.avm.cascadeHost = state.avm.cascadeHost || "adplus20";
  state.avm.ahdRoute = state.avm.ahdRoute || "direct";
  const ahdExtensionRows = [31, 32, 33];
  state.avm.screenExtension = ahdExtensionRows.includes(Number(state.avm.screenExtension)) ? Number(state.avm.screenExtension) : 31;
  state.avm.mdvrExtension = ahdExtensionRows.includes(Number(state.avm.mdvrExtension)) ? Number(state.avm.mdvrExtension) : 31;
  state.avm.cameraExtensions = state.avm.cameraExtensions?.length === 4 ? state.avm.cameraExtensions : [9, 9, 9, 9];
  state.avm.storageVariants = state.avm.storageVariants?.length === 2 ? state.avm.storageVariants : [SD_CARD_VARIANTS[0].partNumber, SD_CARD_VARIANTS[0].partNumber];
  state.avm.storageQuantity = Math.max(0, Math.min(2, Number(state.avm.storageQuantity || 0)));
  return state.avm;
}

function avmItemByRow(row) {
  return c6Items([row])[0] || null;
}

// The DP7S path follows AD Plus 2.0: it uses the regular AHD extension cables,
// not the M12 audio-video leads used by the four AVM cameras.
function avmScreenAhdExtensions() {
  return [31, 32, 33].map((row) => findCatalogItem("adplus20", row)).filter(Boolean);
}

function avmDisplayName(item) {
  return skuInfo(item?.partNumber)?.title ? localizedText(skuInfo(item.partNumber).title) : displayCatalogText(item?.name || "");
}

function avmBomLine(item, quantity = "1") {
  return {
    product: product.title,
    scenario: "",
    family: "",
    group: displayCatalogText(item.group),
    name: avmDisplayName(item),
    partNumber: item.partNumber,
    quantity: String(quantity),
    note: displayCatalogText(item.note),
    description: displayCatalogText(item.description),
  };
}

function avmSelectableCard(item, key, checked, detailOverride = "") {
  const preview = skuInfo(item.partNumber)?.image || fallbackItemPreviewAsset(item);
  return `
    <section class="group-card accessory-row-group">
      <label class="item-card accessory-row-card ${checked ? "selected" : ""}">
        <div class="accessory-row-media">${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${avmDisplayName(item)}" />` : `<div class="thumb"></div>`}</div>
        <div class="accessory-row-copy"><h4>${avmDisplayName(item)}</h4><div class="sku">${item.partNumber}</div><p>${detailOverride || displayCatalogText(item.note || item.description || "")}</p></div>
        <div class="accessory-row-control"><input type="checkbox" ${key} ${checked ? "checked" : ""} /></div>
      </label>
    </section>`;
}

function avmB2Section() {
  const b2s = [avmItemByRow(17), avmItemByRow(18)];
  const b2Extensions = [28, 29, 30].map((row) => findCatalogItem("m3n", row)).filter(Boolean);
  return `<div class="c6-section"><h3 class="c6-section-title">${L("B2 声光报警器", "B2 sound and light alarms")}</h3><p class="c6-section-hint">${L("左右独立选择。每个 B2 默认带 6PIN IPC 延长线；转接线按数量自动匹配。", "Choose left/right independently. Each B2 includes a default 6PIN IPC extension; the adapter is matched by quantity.")}</p>
    <div class="group-list accessory-vertical-list">${b2s.map((item) => { const block = state.selections[item.id] || {}; const selected = Boolean(block.checked); const ext = Number(block.b2ExtensionRow || 28); return `${avmSelectableCard(item, `data-avm2-b2="${item.id}"`, selected)}${selected ? `<div class="extension-picker"><label><span>${L("B2 IPC 延长线", "B2 IPC extension cable")}</span><select data-avm2-b2-extension="${item.id}">${b2Extensions.map((cable) => `<option value="${cable.rowNumber}" ${ext === cable.rowNumber ? "selected" : ""}>${formatExtensionOptionLabel(cable)}</option>`).join("")}</select></label></div>` : ""}`; }).join("")}</div>
  </div>`;
}

function attachAvmB2Handlers() {
  wizardStageEl.querySelectorAll("[data-avm2-b2]").forEach((node) => node.addEventListener("change", (event) => { const block = state.selections[node.dataset.avm2B2] || { quantity: "1" }; block.checked = event.target.checked; block.b2ExtensionRow = block.b2ExtensionRow || 28; state.selections[node.dataset.avm2B2] = block; render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-b2-extension]").forEach((node) => node.addEventListener("change", () => { state.selections[node.dataset.avm2B2Extension].b2ExtensionRow = Number(node.value); render(); }));
}

function avmStorageSection() {
  const avm = avmState();
  const storagePreview = "North America Sales List-FILE/AD Plus 2_0/Image/sd card.png";
  return `<div class="c6-section"><h3 class="c6-section-title">${L("Micro SD 卡", "Micro SD cards")}</h3><section class="group-card accessory-row-group"><div class="item-card accessory-row-card ${avm.storageQuantity > 0 ? "selected" : ""}"><div class="accessory-row-media"><img class="thumb" src="./${storagePreview}" alt="Micro SD card" /></div><div class="accessory-row-copy"><h4>Micro SD card</h4><div class="sku">${L("多种容量可选", "Multiple capacity options")}</div><p>${L("AVM 最多支持 2 张存储卡。", "AVM supports up to 2 cards.")}</p></div><div class="accessory-row-control"><div class="qty-stepper"><button type="button" class="qty-btn" data-avm2-storage-step="-1" ${avm.storageQuantity === 0 ? "disabled" : ""}>-</button><span class="qty-value">${avm.storageQuantity}</span><button type="button" class="qty-btn" data-avm2-storage-step="1" ${avm.storageQuantity >= 2 ? "disabled" : ""}>+</button></div></div></div></section>${avm.storageQuantity > 0 ? `<div class="extension-picker accessory-qty-picker storage-picker"><div class="extension-picker-head"><strong>${L("选择 Micro SD 卡", "Choose Micro SD cards")}</strong><span>${L("最多 2 张", "Up to 2 cards")}</span></div><div class="storage-card-grid">${Array.from({ length: avm.storageQuantity }, (_, index) => `<label class="storage-card"><span class="storage-card-label">${index === 0 ? L("第一张卡", "First card") : L("第二张卡", "Second card")}</span><select data-avm2-storage-variant="${index}">${SD_CARD_VARIANTS.map((variant) => `<option value="${variant.partNumber}" ${avm.storageVariants[index] === variant.partNumber ? "selected" : ""}>${localizedText(variant.name)}</option>`).join("")}</select><span class="storage-card-sku">SKU ${avm.storageVariants[index]}</span></label>`).join("")}</div></div>` : ""}</div>`;
}

function attachAvmStorageHandlers() {
  wizardStageEl.querySelectorAll("[data-avm2-storage-step]").forEach((node) => node.addEventListener("click", () => { const avm = avmState(); avm.storageQuantity = Math.max(0, Math.min(2, avm.storageQuantity + Number(node.dataset.avm2StorageStep))); render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-storage-variant]").forEach((node) => node.addEventListener("change", () => { avmState().storageVariants[Number(node.dataset.avm2StorageVariant)] = node.value; render(); }));
}

function avmModeVisual(modeId, avmPreview) {
  const avmNode = `<div class="avm-mode-device"><img loading="lazy" decoding="async" src="./${avmPreview}" alt="AVM" /><span>AVM</span></div>`;
  if (modeId === "standalone") return `<div class="avm-mode-visual standalone">${avmNode}</div>`;
  return `<div class="avm-mode-visual cascade">${avmNode}<span class="avm-mode-plus">+</span><div class="avm-mode-device"><img loading="lazy" decoding="async" src="./North America Sales List-FILE/AD Plus 2_0/Image/image.png" alt="AD Plus 2.0" /><span>AD Plus 2.0</span></div><div class="avm-mode-device"><img loading="lazy" decoding="async" src="./North America Sales List-FILE/M1N 2_0/Image/3-M1N 2.0 -image.png" alt="MDVR" /><span>MDVR</span></div></div>`;
}

function renderAvm2BaseStep() {
  const avm = avmState();
  const kit = avmItemByRow(6);
  const kitPreview = skuInfo(kit?.partNumber)?.image || fallbackItemPreviewAsset(kit);
  wizardStageEl.innerHTML = `
    <div class="c6-section">
      <h3 class="c6-section-title">${L("方案模式", "Solution mode")}</h3>
      <div class="option-grid two-col">
        <button type="button" class="option-card avm-mode-card ${avm.mode === "standalone" ? "active" : ""}" data-avm2-mode="standalone">${kitPreview ? avmModeVisual("standalone", kitPreview) : ""}<div class="tag">${L("单机", "Standalone")}</div><h3>${L("独立单机", "Standalone AVM")}</h3><p>${L("AVM 独立工作，直接向 DP7S 输出鸟瞰图。", "AVM operates independently and sends its bird's-eye AHD output directly to DP7S.")}</p></button>
        <button type="button" class="option-card avm-mode-card ${avm.mode === "cascade" ? "active" : ""}" data-avm2-mode="cascade">${kitPreview ? avmModeVisual("cascade", kitPreview) : ""}<div class="tag">${L("级联", "Cascade")}</div><h3>${L("级联从机", "Cascade slave")}</h3><p>${L("AVM 作为从机接入上级 MDVR；图中展示 AD Plus 2.0 与通用 MDVR 参考形态。", "AVM connects as a slave to an upstream MDVR; AD Plus 2.0 and a generic MDVR are shown as reference hosts.")}</p></button>
      </div>
    </div>`;
  wizardStageEl.querySelectorAll("[data-avm2-mode]").forEach((node) => node.addEventListener("click", () => { avm.mode = node.dataset.avm2Mode; render(); }));
}

function renderAvm2CameraStep() {
  const avm = avmState();
  const camera = avmItemByRow(13);
  const calibration = avmItemByRow(14);
  const extensions = [9, 10, 11, 12].map(avmItemByRow).filter(Boolean);
  const cameraPreview = skuInfo(camera?.partNumber)?.image || fallbackItemPreviewAsset(camera);
  const calibrationPreview = skuInfo(calibration?.partNumber)?.image || fallbackItemPreviewAsset(calibration);
  wizardStageEl.innerHTML = `
    <div class="focus-banner"><div><strong>${L("固定配置", "Fixed configuration")}</strong><p>${L("4 个环视摄像机 + 4 条独立延长线 + 标定布", "4 surround cameras + 4 individual extension cables + calibration cloth")}</p></div></div>
    <section class="group-card accessory-row-group"><div class="item-card accessory-row-card selected"><div class="accessory-row-media">${cameraPreview ? `<img class="thumb" src="./${cameraPreview}" alt="${avmDisplayName(camera)}" />` : ""}</div><div class="accessory-row-copy"><h4>${avmDisplayName(camera)} × 4</h4><div class="sku">${camera?.partNumber || ""}</div><p>${L("每套 AVM 必带四个同制式 CA51D 摄像机。", "Every AVM requires four CA51D cameras of the same standard.")}</p></div><div class="accessory-row-control"><span class="tag">${L("必选", "Required")}</span></div></div></section>
    <div class="extension-picker"><div class="extension-picker-head"><strong>${L("四条摄像机延长线", "Four camera extension cables")}</strong><span>${L("分别按安装距离选择", "Choose each by installation distance")}</span></div>${[0, 1, 2, 3].map((slot) => `<label><span>${L("摄像机", "Camera")} ${slot + 1}</span><select data-avm2-camera-extension="${slot}">${extensions.map((item) => `<option value="${item.rowNumber}" ${Number(avm.cameraExtensions[slot]) === item.rowNumber ? "selected" : ""}>${formatExtensionOptionLabel(item)}</option>`).join("")}</select></label>`).join("")}</div>
    <section class="group-card accessory-row-group"><div class="item-card accessory-row-card selected"><div class="accessory-row-media">${calibrationPreview ? `<img class="thumb" src="./${calibrationPreview}" alt="${avmDisplayName(calibration)}" />` : ""}</div><div class="accessory-row-copy"><h4>${avmDisplayName(calibration)}</h4><div class="sku">${calibration?.partNumber || ""}</div><p>${L("一套 4 块，默认带出。", "One set of four, included by default.")}</p></div><div class="accessory-row-control"><span class="tag">${L("必选", "Required")}</span></div></div></section>`;
  wizardStageEl.querySelectorAll("[data-avm2-camera-extension]").forEach((node) => node.addEventListener("change", () => { avm.cameraExtensions[Number(node.dataset.avm2CameraExtension)] = Number(node.value); render(); }));
}

function renderAvm2WiringStep() {
  const avm = avmState();
  const screen = avmItemByRow(15);
  const screenChecked = Boolean(state.selections[screen?.id]?.checked);
  const screenExtensions = avmScreenAhdExtensions();
  const hostNames = { adplus20: "AD Plus 2.0", m1n20: "M1N 2.0", m3n: "M3N" };
  const ahdExtensionPicker = (label, dataAttribute, selectedRow) => `<label><span>${label}</span><select ${dataAttribute}>${screenExtensions.map((item) => `<option value="${item.rowNumber}" ${Number(selectedRow) === item.rowNumber ? "selected" : ""}>${formatExtensionOptionLabel(item)}</option>`).join("")}</select></label>`;
  wizardStageEl.innerHTML = `
    <div class="c6-section">
      <h3 class="c6-section-title">${L("上级主机连接", "Host connection")}</h3>
      ${avm.mode === "cascade" ? `<p class="c6-section-hint">${L("级联线会自动加入。选择一台上级主机后，主机本体会加入组合清单；完成 AVM 配置后将进入所选主机原有的选型向导。Direct to screen 预占主机 1 路 IPC / 1 路录像；屏幕 + MDVR 录制再预占 1 路 AHD / 1 路录像。", "The cascade IPC cable is included automatically. Choose one host: it joins the combined list and its own wizard follows the AVM pages. Direct to screen reserves 1 IPC / 1 recording channel; Screen + MDVR recording additionally reserves 1 AHD / 1 recording channel.")}</p><div class="option-grid three-col">${Object.entries(hostNames).map(([id, name]) => `<button type="button" class="option-card avm-host-card ${avm.cascadeHost === id ? "active" : ""}" data-avm2-host="${id}"><div class="avm-host-media"><img loading="lazy" decoding="async" src="./${PRODUCT_META[id]?.entryImage || ""}" alt="${name}" /></div><h3>${name}</h3><p>${L("加入组合清单，随后按其向导完成主机选型。", "Joins the combined list; host setup continues in its own wizard.")}</p></button>`).join("")}</div>` : `<p class="c6-section-hint">${L("单机模式不接上级 MDVR。", "Standalone mode does not connect to an upstream MDVR.")}</p>`}
    </div>
    <div class="c6-section"><h3 class="c6-section-title">${L("司机屏幕与俯瞰图输出", "Driver screen & bird's-eye output")}</h3>${avmSelectableCard(screen, `data-avm2-screen="${screen.id}"`, screenChecked)}
      ${screenChecked ? `<div class="option-grid two-col"><button type="button" class="option-card ${avm.ahdRoute === "direct" ? "active" : ""}" data-avm2-route="direct"><h3>${L("直接到屏幕", "Direct to screen")}</h3><p>${L("自动带 AHD 信号转接线，仅供司机查看。", "Automatically includes the AHD signal adapter; for driver viewing only.")}</p></button>${avm.mode === "cascade" ? `<button type="button" class="option-card ${avm.ahdRoute === "split" ? "active" : ""}" data-avm2-route="split"><h3>${L("屏幕 + MDVR 录制", "Screen + MDVR recording")}</h3><p>${L("自动带 AHD 信号转接线与一拖二线，同时接屏幕和主机 AHD 输入。", "Automatically includes the AHD signal adapter and splitter to feed both screen and host AHD input.")}</p></button>` : ""}</div><div class="extension-picker"><div class="extension-picker-head"><strong>${L("AHD 延长线", "AHD extension cable")}</strong><span>${L("必选，复用 AD Plus 2.0 线材，按安装距离选择", "Required — uses AD Plus 2.0 cables; choose by installation distance")}</span></div>${ahdExtensionPicker(L("屏幕端", "Screen end"), "data-avm2-screen-extension", avm.screenExtension)}${avm.mode === "cascade" && avm.ahdRoute === "split" ? ahdExtensionPicker(L("MDVR 端", "MDVR end"), "data-avm2-mdvr-extension", avm.mdvrExtension) : ""}</div>` : ""}
    </div>
    ${avm.mode === "standalone" ? `${avmB2Section()}${avmStorageSection()}` : ""}`;
  wizardStageEl.querySelectorAll("[data-avm2-host]").forEach((node) => node.addEventListener("click", () => { avm.cascadeHost = node.dataset.avm2Host; render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-screen]").forEach((node) => node.addEventListener("change", (event) => { state.selections[screen.id] = { checked: event.target.checked, quantity: "1" }; render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-route]").forEach((node) => node.addEventListener("click", () => { avm.ahdRoute = node.dataset.avm2Route; render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-screen-extension]").forEach((node) => node.addEventListener("change", () => { avm.screenExtension = Number(node.value); render(); }));
  wizardStageEl.querySelectorAll("[data-avm2-mdvr-extension]").forEach((node) => node.addEventListener("change", () => { avm.mdvrExtension = Number(node.value); render(); }));
  if (avm.mode === "standalone") { attachAvmB2Handlers(); attachAvmStorageHandlers(); }
}

function renderAvm2AccessoriesStep() {
  const avm = avmState();
  wizardStageEl.innerHTML = `
    ${avm.mode === "cascade" ? avmB2Section() : ""}
    ${avmStorageSection()}`;
  if (avm.mode === "cascade") attachAvmB2Handlers();
  attachAvmStorageHandlers();
}

function selectedAvmItems() {
  const avm = avmState();
  const rows = [avmBomLine(avmItemByRow(6)), avmBomLine(avmItemByRow(13), 4), avmBomLine(avmItemByRow(14))];
  avm.cameraExtensions.forEach((row) => { const item = avmItemByRow(Number(row)); if (item) rows.push(avmBomLine(item)); });
  if (avm.mode === "cascade") { const cascadeCable = avmItemByRow(8); if (cascadeCable) rows.push(avmBomLine(cascadeCable)); }
  const screen = avmItemByRow(15);
  if (state.selections[screen?.id]?.checked) {
    rows.push(avmBomLine(screen));
    const signalAdapter = avmItemByRow(16);
    if (signalAdapter) rows.push(avmBomLine(signalAdapter));
    if (avm.mode === "cascade" && avm.ahdRoute === "split") {
      const splitter = avmItemByRow(7);
      if (splitter) rows.push(avmBomLine(splitter));
    }
    const screenExtension = findCatalogItem("adplus20", Number(avm.screenExtension));
    if (screenExtension) rows.push(avmBomLine(screenExtension));
    if (avm.mode === "cascade" && avm.ahdRoute === "split") {
      const mdvrExtension = findCatalogItem("adplus20", Number(avm.mdvrExtension));
      if (mdvrExtension) rows.push(avmBomLine(mdvrExtension));
    }
  }
  if (avm.mode === "standalone") {
    const selectedB2 = [avmItemByRow(17), avmItemByRow(18)].filter((item) => state.selections[item?.id]?.checked);
    selectedB2.forEach((item) => { rows.push(avmBomLine(item)); const extension = findCatalogItem("m3n", Number(state.selections[item.id]?.b2ExtensionRow || 28)); if (extension) rows.push(avmBomLine(extension)); });
    if (selectedB2.length) { const adapter = avmItemByRow(selectedB2.length === 1 ? 19 : 20); if (adapter) rows.push(avmBomLine(adapter)); }
    for (let index = 0; index < avm.storageQuantity; index += 1) { const variant = SD_CARD_VARIANTS.find((item) => item.partNumber === avm.storageVariants[index]) || SD_CARD_VARIANTS[0]; rows.push({ product: product.title, scenario: "", family: "", group: "Storage", name: localizedText(variant.name), partNumber: variant.partNumber, quantity: "1", note: "AVM storage", description: "AVM Micro SD card" }); }
  }
  return rows;
}

function avmEnterHostFlow() {
  const avm = avmState();
  const cascade = {
    host: avm.cascadeHost,
    route: avm.ahdRoute,
    reserved: { ipc: 1, ahd: avm.ahdRoute === "split" ? 1 : 0, recording: avm.ahdRoute === "split" ? 2 : 1 },
    items: selectedAvmItems(),
    snapshot: {
      avm: JSON.parse(JSON.stringify(state.avm)),
      selections: JSON.parse(JSON.stringify(state.selections)),
      packageId: state.packageId,
    },
  };
  chooseProduct(cascade.host);
  state.avmCascade = cascade;
  state.productPickerOpen = false;
  state.step = isAdplusProduct() ? 2 : 1;
  render();
}

function avmReturnFromHostFlow() {
  const cascade = state.avmCascade;
  if (!cascade) return;
  chooseProduct("avm");
  state.avmCascade = null;
  state.avm = cascade.snapshot.avm;
  state.selections = cascade.snapshot.selections;
  state.packageId = cascade.snapshot.packageId;
  state.productPickerOpen = false;
  state.step = 3;
  render();
}
function c6PowerModelOf(item) {
  return /CAN/i.test(item.group?.en || item.group || "") ? "can" : "rs232";
}

const C6_POWER_ROWS = [10, 11, 12, 13, 27, 28];

function c6KitModelOf(item) {
  return /CAN/i.test(item?.group?.en || item?.group || "") ? "can" : "rs232";
}

function c6RequiredPowerRow(model) {
  return model === "can" ? 12 : 27;
}

function c6SharedKitPreview(item) {
  const single = /single-lens/i.test(item?.group?.en || item?.group || "");
  return single
    ? "North America Sales List-FILE/C6 Lite 2_0/Image/C6-2.0-S-kit.png"
    : "North America Sales List-FILE/C6 Lite 2_0/Image/C6-kit-dual.png";
}

function c6SelectedKitIsSingle() {
  const pkg = currentPackage();
  return /single-lens/i.test(pkg?.group?.en || pkg?.group || "");
}
function c6CurrentPowerModel() {
  return c6KitModelOf(currentPackage()) || state.c6?.powerModel || null;
}
// Business rules from the spec:
//  - Extra cameras / AHD expansion are only for the single-lens (2.0-S) kit; the dual-lens uses both channels.
//  - R-Watch only works on the RS232 model.
function normalizeC6Selections() {
  const single = c6SelectedKitIsSingle();
  if (!single) {
    c6Items([20, 21, 22]).forEach((cam) => {
      if (state.selections[cam.id]) {
        state.selections[cam.id].checked = false;
        state.selections[cam.id].c6ExtRow = "";
      }
    });
  } else {
    // Single-lens expands only one AHD channel -> keep at most one camera.
    let seenCam = false;
    c6Items([20, 21, 22]).forEach((cam) => {
      if (state.selections[cam.id]?.checked) {
        if (seenCam) {
          state.selections[cam.id].checked = false;
          state.selections[cam.id].c6ExtRow = "";
        } else seenCam = true;
      }
    });
  }
  // AHD Expansion (r15) is auto-added with cameras, never selected manually.
  const exp = c6Items([15])[0];
  if (exp && state.selections[exp.id]) state.selections[exp.id].checked = false;
  c6Items([9, 14]).forEach((item) => {
    if (state.selections[item.id]) state.selections[item.id].checked = false;
  });
  const requiredRow = c6RequiredPowerRow(c6CurrentPowerModel());
  const requiredPower = c6Items([requiredRow])[0];
  if (requiredPower) {
    state.selections[requiredPower.id] = { ...(state.selections[requiredPower.id] || {}), checked: true, quantity: "1" };
  }
  if (c6CurrentPowerModel() === "can") {
    const rwatch = c6Items([23])[0];
    if (rwatch && state.selections[rwatch.id]) state.selections[rwatch.id].checked = false;
  }
}

// AVM base: the AVM 360 kit (surround cameras + calibration are part of the core system).
function renderAvmBaseStep() {
  const kit = c6Items([6])[0];
  const included = c6Items([13, 14]); // CA51D ×4, calibration cloth
  const active = kit && kit.id === state.packageId ? "active" : "";
  const kitImg = (kit && (skuInfo(kit.partNumber)?.image || fallbackItemPreviewAsset(kit) || pickPreviewAsset(kit.images))) || "";
  wizardStageEl.innerHTML = `
    <button class="option-card avm-kit-card ${active}" data-package="${kit?.id || ""}">
      ${kitImg ? `<img loading="lazy" decoding="async" class="host-photo" src="./${kitImg}" alt="AVM" />` : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`}
      <div class="tag">${L("360° 环视系统", "360° surround-view system")}</div>
      <h3>${displayCatalogText(kit?.name) || "AVM"}</h3>
      <div class="sku">${kit?.partNumber || t().noPartNumber}</div>
      <p>${displayCatalogText(kit?.note || "")}</p>
    </button>
    <div class="c6-section">
      <h3 class="c6-section-title">${L("套装已包含", "Included in this kit")}</h3>
      <div class="group-list accessory-vertical-list">
        ${included
          .map((it) => {
            const info = skuInfo(it.partNumber);
            const preview = info?.image || fallbackItemPreviewAsset(it);
            const qty = it.rowNumber === 13 ? " × 4" : "";
            const name = (info?.title ? localizedText(info.title) : displayCatalogText(it.name)) + qty;
            return `
              <section class="group-card accessory-row-group">
                <label class="item-card accessory-row-card selected">
                  <div class="accessory-row-media">${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${name}" />` : `<div class="thumb"></div>`}</div>
                  <div class="accessory-row-copy">
                    <h4>${name}</h4>
                    <div class="sku">${it.partNumber || t().noPartNumber}</div>
                    <p>${displayCatalogText(it.note || "")}</p>
                  </div>
                  <div class="accessory-row-control"><span class="tag">${L("必带", "Included")}</span></div>
                </label>
              </section>
            `;
          })
          .join("")}
      </div>
    </div>
  `;
  wizardStageEl.querySelectorAll("[data-package]").forEach((node) => {
    node.addEventListener("click", () => choosePackage(node.dataset.package));
  });
}

// AVM connection modes: which adapter cable + reference diagram.
const AVM_MODES = [
  { id: "standalone", adapterRow: 7, diagram: "North America Sales List-FILE/AVM/Image/1--image.png",
    title: { zh: "单机录屏", en: "Standalone (record on screen)" },
    detail: { zh: "AVM 直连 DP7S 屏幕录制。", en: "AVM records directly to the DP7S screen." } },
  { id: "cascade", adapterRow: 8, diagram: "North America Sales List-FILE/AVM/Image/2--image.png",
    title: { zh: "级联录像机", en: "Cascade to a recorder" },
    detail: { zh: "AVM 作为从机接入 AD Plus / MDVR 录像机。", en: "AVM connects as a slave to an AD Plus / MDVR recorder." } },
];
function avmCurrentMode() {
  return AVM_MODES.find((m) => m.id === state.avm?.mode) || null;
}
// A selectable AVM item card (checkbox), curated via the SKU library.
function avmItemCard(item) {
  const block = state.selections[item.id] || {};
  const checked = block.checked ? "checked" : "";
  const selected = block.checked ? "selected" : "";
  const info = skuInfo(item.partNumber);
  const preview = info?.image || fallbackItemPreviewAsset(item);
  const name = info?.title ? localizedText(info.title) : displayCatalogText(item.name);
  const detail = info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(item.note || item.description || "");
  return `
    <section class="group-card accessory-row-group">
      <label class="item-card accessory-row-card ${selected}">
        <div class="accessory-row-media">${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${name}" />` : `<div class="thumb"></div>`}</div>
        <div class="accessory-row-copy">
          <h4>${name}</h4>
          <div class="sku">${item.partNumber || t().noPartNumber}</div>
          <p>${detail}</p>
        </div>
        <div class="accessory-row-control"><input type="checkbox" data-avm-item="${item.id}" ${checked} /></div>
      </label>
    </section>
  `;
}
function attachAvmHandlers() {
  wizardStageEl.querySelectorAll("[data-avm-item]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.avmItem;
      if (!state.selections[id]) state.selections[id] = { checked: false, quantity: "1" };
      state.selections[id].checked = event.target.checked;
      render();
    });
  });
  wizardStageEl.querySelectorAll("[data-avm-mode]").forEach((node) => {
    node.addEventListener("click", () => {
      state.avm = state.avm || {};
      state.avm.mode = node.dataset.avmMode;
      render();
    });
  });
}
function avmFocusBanner() {
  const mode = avmCurrentMode();
  return `
    <div class="focus-banner">
      <div><strong>${t().summaryFields.product}</strong><p>${currentProduct()?.title || "-"}</p></div>
      <div><strong>${L("连接方式", "Connection mode")}</strong><p>${mode ? localizedText(mode.title) : t().noneSelected}</p></div>
    </div>
  `;
}

// AVM step 2 — connection mode (picks the adapter cable) + video extension cables.
function renderAvmWiringStep() {
  const mode = avmCurrentMode();
  const extensions = c6Items([9, 10, 11, 12]);
  wizardStageEl.innerHTML = `
    ${avmFocusBanner()}
    <div class="c6-section">
      <h3 class="c6-section-title">${L("连接方式", "Connection mode")}</h3>
      <p class="c6-section-hint">${L("选择 AVM 如何接入——决定所需的转接线。", "Choose how the AVM connects — this sets the required adapter cable.")}</p>
      <div class="option-grid two-col">
        ${AVM_MODES.map((m) => `
          <button class="option-card ${state.avm?.mode === m.id ? "active" : ""}" data-avm-mode="${m.id}">
            <div class="tag">${localizedText(m.title)}</div>
            <h3>${localizedText(m.title)}</h3>
            <p>${localizedText(m.detail)}</p>
          </button>
        `).join("")}
      </div>
      ${
        mode
          ? `<div class="c6-section">
              <img loading="lazy" decoding="async" class="avm-diagram" src="./${mode.diagram}" alt="diagram" />
              <p class="c6-section-hint">${L("已自动加入转接线：", "Adapter cable auto-added:")} ${(() => { const a = findItemByRow(mode.adapterRow); return a ? (skuInfo(a.partNumber)?.title ? localizedText(skuInfo(a.partNumber).title) : displayCatalogText(a.name)) : ""; })()}</p>
            </div>`
          : `<p class="c6-section-hint">${L("请先选择连接方式。", "Choose a connection mode first.")}</p>`
      }
    </div>
    <div class="c6-section">
      <h3 class="c6-section-title">${L("视频延长线（按需）", "Video extension cable (optional)")}</h3>
      <div class="group-list accessory-vertical-list">${extensions.map(avmItemCard).join("")}</div>
    </div>
  `;
  attachAvmHandlers();
}

// AVM step 3 — screen (DP7S) + AHD signal adapter.
function renderAvmScreenStep() {
  const items = c6Items([15, 16]);
  wizardStageEl.innerHTML = `
    ${avmFocusBanner()}
    <div class="c6-section">
      <h3 class="c6-section-title">${L("屏幕", "Screen")}</h3>
      <div class="group-list accessory-vertical-list">${items.map(avmItemCard).join("")}</div>
    </div>
  `;
  attachAvmHandlers();
}

// AVM step 4 — exterior alarm (B2 left/right) + adapter cables.
function renderAvmAlarmStep() {
  const items = c6Items([17, 18]); // B2 right / left — adapter cable is auto-added by count
  wizardStageEl.innerHTML = `
    ${avmFocusBanner()}
    <div class="c6-section">
      <h3 class="c6-section-title">${L("外部报警", "Exterior alarm")}</h3>
      <p class="c6-section-hint">${L("B2 分左/右两只，可选装；转接线会按所选数量自动加入。", "B2 comes as left/right units (optional); the matching adapter cable is added automatically.")}</p>
      <div class="group-list accessory-vertical-list">${items.map(avmItemCard).join("")}</div>
    </div>
  `;
  attachAvmHandlers();
}

// C6 Lite base kit: four explicit combinations of lens count and vehicle interface.
function renderC6BaseStep() {
  const kits = c6Items([7, 8, 25, 26]);
  wizardStageEl.innerHTML = `
    <div class="option-grid c6-kit-grid">
      ${kits
        .map((kit) => {
          const active = kit.id === state.packageId ? "active" : "";
          const single = /single-lens/i.test(kit.group?.en || kit.group || "");
          const model = c6KitModelOf(kit);
          const lens = single ? L("单镜头", "Single-lens") : L("双镜头", "Dual-lens");
          const modelLabel = model === "can" ? "CAN" : "RS232";
          const preview = c6SharedKitPreview(kit);
          const detail = L(
            `${lens} · ${modelLabel} 版本`,
            `${single ? "Single-lens" : "Dual-lens"} · ${modelLabel} vehicle interface`
          );
          return `
            <button class="option-card ${active}" data-package="${kit.id}">
              ${preview ? `<img loading="lazy" decoding="async" class="host-photo" src="./${preview}" alt="${displayCatalogText(kit.name)}" />` : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`}
              <div class="tag">${lens} · ${modelLabel}</div>
              <h3>${single ? "C6 Lite 2.0-S" : "C6 Lite 2.0"} · ${modelLabel}</h3>
              <div class="sku">${kit.partNumber || t().noPartNumber}</div>
              <p>${detail}</p>
            </button>
          `;
        })
        .join("")}
    </div>
  `;
  wizardStageEl.querySelectorAll("[data-package]").forEach((node) => {
    node.addEventListener("click", () => choosePackage(node.dataset.package));
  });
}

// C6 Lite power: the selected kit determines the compatible cable list and its default.
function renderC6WiringStep() {
  state.c6 = state.c6 || {};
  const powerCables = c6Items(C6_POWER_ROWS);
  const kit = currentPackage();
  const kitModel = c6KitModelOf(kit);
  const compatibleCables = powerCables.filter((it) => c6PowerModelOf(it) === kitModel);
  const requiredRow = c6RequiredPowerRow(kitModel);
  const requiredPower = compatibleCables.find((it) => it.rowNumber === requiredRow);
  if (requiredPower) state.selections[requiredPower.id] = { ...(state.selections[requiredPower.id] || {}), checked: true, quantity: "1" };
  const optionalCables = compatibleCables.filter((it) => it.rowNumber !== requiredRow);
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("当前核心套装", "Current core kit")}</strong>
        <p>${kit ? displayCatalogText(kit.name) : "-"}</p>
      </div>
    </div>
    <div class="c6-section">
      <h3 class="c6-section-title">${L("电源线", "Power cable")}</h3>
      <p class="c6-section-hint">${kitModel === "can" ? L("16PIN OBD 是 CAN 套装的强制线材；9PIN OBD 与 CAN 散线可按项目额外选择。", "16PIN OBD is required for CAN kits; add 9PIN OBD or the CAN loose power cable only when needed.") : L("电源散线是 RS232 套装的强制线材；16PIN 与 9PIN OBD 可按项目额外选择。", "The loose power cable is required for RS232 kits; add 16PIN or 9PIN OBD only when needed.")}</p>
      <div class="group-list accessory-vertical-list">
        ${[requiredPower, ...optionalCables].filter(Boolean).map((it) => {
          const required = it.rowNumber === requiredRow;
          const checked = Boolean(state.selections[it.id]?.checked);
          const preview = skuInfo(it.partNumber)?.image || fallbackItemPreviewAsset(it);
          const name = skuInfo(it.partNumber)?.title ? localizedText(skuInfo(it.partNumber).title) : displayCatalogText(it.name);
          return `
            <section class="group-card accessory-row-group">
              <label class="item-card accessory-row-card ${checked ? "selected" : ""}">
                <div class="accessory-row-media">${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${name}" />` : `<div class="thumb"></div>`}</div>
                <div class="accessory-row-copy"><h4>${name}</h4><div class="sku">${it.partNumber || t().noPartNumber}</div><p>${displayCatalogText(it.note || it.description || "")}</p></div>
                <div class="accessory-row-control">${required ? `<span class="tag">${L("强制包含", "Required")}</span>` : `<input type="checkbox" data-c6-optional-power="${it.id}" ${checked ? "checked" : ""} />`}</div>
              </label>
            </section>`;
        }).join("")}
      </div>
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-c6-optional-power]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.c6OptionalPower;
      if (!state.selections[id]) state.selections[id] = { checked: false, quantity: "1" };
      state.selections[id].checked = event.target.checked;
      render();
    });
  });
}

// C6 Lite cameras: each camera is a card; selecting it reveals a nested AHD extension-cable picker.
function renderC6CameraStep() {
  const cameras = c6Items([20, 21, 22]);
  const extCables = c6Items([16, 17, 18, 19]);
  const kit = currentPackage();
  const single = c6SelectedKitIsSingle();
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("当前核心套装", "Current core kit")}</strong>
        <p>${kit ? displayCatalogText(kit.name) : "-"}</p>
      </div>
    </div>
    ${
      !single
        ? `<div class="capacity-note warning">
            <strong>${L("双镜头无法额外加装摄像头", "No extra cameras on the dual-lens kit")}</strong>
            <p>${L("双镜头套装已占用两路 AHD 通道。若需加装摄像头，请在第 1 步改选单镜头（C6 Lite 2.0-S）。", "The dual-lens kit already uses both AHD channels. To add a camera, switch to the single-lens (C6 Lite 2.0-S) kit in step 1.")}</p>
          </div>`
        : `<div class="capacity-note">
            <strong>${L("最多加装 1 个摄像头", "Add at most one camera")}</strong>
            <p>${L("单镜头仅可扩展一路 AHD 通道，因此摄像头只能选择一个。", "The single-lens kit can expand only one AHD channel, so you can add at most one camera.")}</p>
          </div>`
    }
    <div class="group-list accessory-vertical-list">
      ${(single ? cameras : [])
        .map((cam) => {
          const block = state.selections[cam.id] || {};
          const checked = block.checked ? "checked" : "";
          const selected = block.checked ? "selected" : "";
          const info = skuInfo(cam.partNumber);
          const preview = info?.image || fallbackItemPreviewAsset(cam);
          const name = info?.title ? localizedText(info.title) : displayCatalogText(cam.name);
          const detail = info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(cam.note || cam.description || "");
          const extRow = block.c6ExtRow || "";
          return `
            <section class="group-card accessory-row-group">
              <label class="item-card accessory-row-card ${selected}">
                <div class="accessory-row-media">
                  ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${name}" />` : `<div class="thumb"></div>`}
                </div>
                <div class="accessory-row-copy">
                  <h4>${name}</h4>
                  <div class="sku">${cam.partNumber || t().noPartNumber}</div>
                  <p>${detail}</p>
                </div>
                <div class="accessory-row-control">
                  <input type="checkbox" data-c6-camera="${cam.id}" ${checked} />
                </div>
              </label>
              ${
                block.checked
                  ? `
                    <div class="extension-picker">
                      <div class="extension-picker-head">
                        <strong>${L("AHD 延长线", "AHD extension cable")}</strong>
                        <span>${L("按安装距离选择，可不选", "Optional — choose by install distance")}</span>
                      </div>
                      <label>
                        <span>${t().lengthAndPart}</span>
                        <select data-c6-cam-ext="${cam.id}">
                          <option value="" ${extRow === "" ? "selected" : ""}>${t().notNeeded}</option>
                          ${extCables
                            .map((ext) => {
                              const et = skuInfo(ext.partNumber)?.title;
                              const label = et ? localizedText(et) : displayCatalogText(ext.name);
                              return `<option value="${ext.rowNumber}" ${String(extRow) === String(ext.rowNumber) ? "selected" : ""}>${label} | ${ext.partNumber}</option>`;
                            })
                            .join("")}
                        </select>
                      </label>
                    </div>
                  `
                  : ""
              }
            </section>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-c6-camera]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.c6Camera;
      if (!state.selections[id]) state.selections[id] = { checked: false, quantity: "1" };
      state.selections[id].checked = event.target.checked;
      // Single-lens can expand only one AHD channel -> at most one camera.
      if (event.target.checked) {
        c6Items([20, 21, 22]).forEach((other) => {
          if (other.id !== id && state.selections[other.id]) {
            state.selections[other.id].checked = false;
            state.selections[other.id].c6ExtRow = "";
          }
        });
      }
      render();
    });
  });
  wizardStageEl.querySelectorAll("[data-c6-cam-ext]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.c6CamExt;
      if (!state.selections[id]) state.selections[id] = { checked: true, quantity: "1" };
      state.selections[id].c6ExtRow = event.target.value;
      render();
    });
  });
}

// C6 Lite accessories: R-Watch + Micro SD (with nested capacity picker), AD-Plus-style cards.
function renderC6AccessoryStep() {
  const items = c6Items([23, 24]);
  const kit = currentPackage();
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("当前核心套装", "Current core kit")}</strong>
        <p>${kit ? displayCatalogText(kit.name) : "-"}</p>
      </div>
    </div>
    <div class="group-list accessory-vertical-list">
      ${items
        .map((it) => {
          const block = state.selections[it.id] || {};
          const isStorage = it.rowNumber === 24;
          const quantity = isStorage ? (block.checked ? Math.max(1, Math.min(2, Number(block.quantity || 0))) : 0) : (block.checked ? 1 : 0);
          const checked = quantity > 0 ? "checked" : "";
          const selected = quantity > 0 ? "selected" : "";
          const variantOptions = presetVariantOptions(it);
          const selectedPartNumbers = isStorage
            ? (Array.isArray(block.variantPartNumbers) ? block.variantPartNumbers : [block.variantPartNumber || SD_CARD_VARIANTS[0].partNumber])
            : [block.variantPartNumber];
          const selectedVariant = variantOptions
            ? variantOptions.find((v) => v.partNumber === selectedPartNumbers[0]) || variantOptions[0]
            : null;
          const info = variantOptions ? null : skuInfo(it.partNumber);
          const preview = info?.image || fallbackItemPreviewAsset(it);
          const name = variantOptions ? localizedText(selectedVariant.name) : (info?.title ? localizedText(info.title) : displayCatalogText(it.name));
          // R-Watch (row 23) only supports the RS232 model.
          const disabled = it.rowNumber === 23 && c6CurrentPowerModel() === "can";
          const detail = disabled
            ? L("R-Watch 仅支持 RS232 机型。当前接线为 CAN，请改用 RS232 机型。", "R-Watch only supports the RS232 model. Current wiring is CAN — switch to an RS232 power cable to use it.")
            : (info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(it.note || it.description || ""));
          const skuText = variantOptions ? selectedVariant.partNumber : it.partNumber || t().noPartNumber;
          return `
            <section class="group-card accessory-row-group">
              <label class="item-card accessory-row-card ${selected} ${disabled ? "disabled" : ""}">
                <div class="accessory-row-media">
                  ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${name}" />` : `<div class="thumb"></div>`}
                </div>
                <div class="accessory-row-copy">
                  <h4>${name}</h4>
                  <div class="sku">${skuText}</div>
                  <p>${detail}</p>
                </div>
                <div class="accessory-row-control">
                  ${
                    isStorage
                      ? `<div class="qty-stepper" data-c6-storage-stepper="${it.id}">
                          <button type="button" class="qty-btn" data-c6-storage-step="${it.id}" data-direction="-1" ${quantity <= 0 ? "disabled" : ""}>-</button>
                          <span class="qty-value">${quantity}</span>
                          <button type="button" class="qty-btn" data-c6-storage-step="${it.id}" data-direction="1" ${quantity >= 2 ? "disabled" : ""}>+</button>
                        </div>`
                      : `<input type="checkbox" data-c6-extra="${it.id}" ${checked} ${disabled ? "disabled" : ""} />`
                  }
                </div>
              </label>
              ${
                quantity > 0 && variantOptions
                  ? `
                    <div class="extension-picker accessory-qty-picker storage-picker">
                      <div class="extension-picker-head">
                        <strong>${L("选择 Micro SD 卡", "Choose Micro SD card")}</strong>
                        <span>${L("最多 2 张", "Up to 2 cards")}</span>
                      </div>
                      <div class="storage-card-grid">
                        ${Array.from({ length: quantity }, (_, index) => {
                          const selectedPart = selectedPartNumbers[index] || selectedVariant.partNumber;
                          return `<label class="storage-card">
                            <span class="storage-card-label">${index === 0 ? L("第一张卡", "First card") : L("第二张卡", "Second card")}</span>
                            <select data-c6-storage-variant="${it.id}" data-slot="${index}">
                              ${variantOptions.map((v) => `<option value="${v.partNumber}" ${selectedPart === v.partNumber ? "selected" : ""}>${localizedText(v.name)}</option>`).join("")}
                            </select>
                            <span class="storage-card-sku">SKU ${selectedPart}</span>
                          </label>`;
                        }).join("")}
                      </div>
                    </div>
                  `
                  : ""
              }
            </section>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-c6-extra]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.c6Extra;
      if (!state.selections[id]) state.selections[id] = { checked: false, quantity: "1" };
      state.selections[id].checked = event.target.checked;
      render();
    });
  });
  wizardStageEl.querySelectorAll("[data-c6-storage-step]").forEach((node) => {
    node.addEventListener("click", () => {
      const id = node.dataset.c6StorageStep;
      const block = state.selections[id] || { checked: false, quantity: "0" };
      const currentQuantity = block.checked ? Math.max(1, Number(block.quantity || 0)) : 0;
      const quantity = Math.max(0, Math.min(2, currentQuantity + Number(node.dataset.direction || 0)));
      block.checked = quantity > 0;
      block.quantity = String(quantity);
      const variants = Array.isArray(block.variantPartNumbers) ? block.variantPartNumbers : [block.variantPartNumber || SD_CARD_VARIANTS[0].partNumber];
      block.variantPartNumbers = variants.slice(0, quantity);
      while (block.variantPartNumbers.length < quantity) block.variantPartNumbers.push(SD_CARD_VARIANTS[0].partNumber);
      block.variantPartNumber = block.variantPartNumbers[0] || SD_CARD_VARIANTS[0].partNumber;
      state.selections[id] = block;
      render();
    });
  });
  wizardStageEl.querySelectorAll("[data-c6-storage-variant]").forEach((node) => {
    node.addEventListener("change", (event) => {
      const id = node.dataset.c6StorageVariant;
      const block = state.selections[id] || { checked: true, quantity: "1" };
      const slot = Number(node.dataset.slot || 0);
      const variants = Array.isArray(block.variantPartNumbers) ? block.variantPartNumbers : [block.variantPartNumber || SD_CARD_VARIANTS[0].partNumber];
      variants[slot] = event.target.value;
      block.variantPartNumbers = variants;
      block.variantPartNumber = variants[0];
      state.selections[id] = block;
      render();
    });
  });
}
