function buildScenarios() {
  if (!product) {
    return [];
  }

  const built = product.solutions
    .map((solution, index) => ({
      scenarioId: `scenario-${index + 1}`,
      familyId: solution.id,
      familyLabel: {
        zh: `${t().familyPrefix} ${solution.id}`,
        en: `${UI.en.familyPrefix} ${solution.id}`,
      },
      title: bilingualCatalogText(solution.title || `${t().familyPrefix} ${index + 1}`),
      note: bilingualCatalogText(solution.note),
      image: pickPreviewAsset(solution.images),
      sourceIndex: index + 1,
    }))
    .filter((scenario) => (isAdplusProduct() ? KEPT_SCENARIO_POSITIONS.has(scenario.sourceIndex) : true));

  if (!isAdplusProduct()) return built;

  const customScenario = {
    scenarioId: CUSTOM_SCENARIO_ID,
    familyId: CUSTOM_FAMILY_ID,
    familyLabel: { zh: UI.zh.customScenario.familyLabel, en: UI.en.customScenario.familyLabel },
    title: { zh: UI.zh.customScenario.title, en: UI.en.customScenario.title },
    note: { zh: UI.zh.customScenario.note, en: UI.en.customScenario.note },
    image: "North America Sales List-FILE/AD Plus 2_0/Image/image.png",
    sourceIndex: 0,
  };

  return [customScenario, ...built];
}

let scenarios = buildScenarios();

state.scenarioId = scenarios[0]?.scenarioId || null;
state.familyId = scenarios[0]?.familyId || null;

function currentScenario() {
  return scenarios.find((item) => item.scenarioId === state.scenarioId) || null;
}

function isCustomFlow() {
  return isAdplusProduct() && state.familyId === CUSTOM_FAMILY_ID;
}

function currentSteps() {
  if (is960C53Product() && state.c53?.mode === "cascade") return L(C53_CASCADE_STEPS.zh, C53_CASCADE_STEPS.en) || C53_CASCADE_STEPS.en;
  if (isAvmProduct() && state.avm?.mode === "standalone") return L(AVM_STANDALONE_FLOW_STEPS.zh, AVM_STANDALONE_FLOW_STEPS.en) || AVM_STANDALONE_FLOW_STEPS.en;
  const steps = PRODUCT_META[state.productId]?.steps;
  if (steps) return L(steps.zh, steps.en) || steps.en;
  if (isStepperProduct()) return t().m1nSteps;
  return isCustomFlow() ? t().customSteps : t().presetSteps;
}

function currentPackageFamilyIds() {
  const pkg = product?.items?.find((item) => item.id === state.packageId);
  return new Set(pkg?.solutionRefs || []);
}

function itemsForFamily() {
  if (!product) return [];
  // AVM and C6 (now a free custom-style build) expose the whole item list, not a scenario subset.
  if (isAvmProduct() || isC6Product()) return product.items;
  if (!state.familyId || isCustomFlow()) return product.items;
  return product.items.filter((item) => !item.solutionRefs.length || item.solutionRefs.includes(state.familyId));
}

function packageCandidates() {
  if (is960C53Product()) {
    // Only no-logo C53-L/C53-R kits are selectable at entry. Rows 3 and 6
    // are Streamax-logo variants; rows 8–14 are included kit components.
    return product.items.filter((item) => [2, 4, 5, 7].includes(item.rowNumber));
  }
  if (isAvmProduct()) {
    return product.items.filter((item) => /kit/i.test(item.group) || /kit/i.test(item.name));
  }
  if (isC6Product()) {
    return product.items.filter((item) => /kit/i.test(item.group) || /kit/i.test(item.name));
  }
  return itemsForFamily().filter((item) => /kit/i.test(item.group) || /kit/i.test(item.name));
}

function accessoryCandidates() {
  return itemsForFamily().filter((item) => item.id !== state.packageId);
}

function groupedItems(items) {
  return items.reduce((map, item) => {
    const key = item.group || "Ungrouped";
    if (!map[key]) map[key] = [];
    map[key].push(item);
    return map;
  }, {});
}

function suggestAccessorySelection(item, groupItems) {
  if (item.id === state.packageId) return true;
  // C6 has only one included power lead, selected from the chosen kit; all
  // cameras, R-Watch and storage remain opt-in.
  if (isC6Product()) return false;
  if (isAvmProduct() && item.rowNumber !== undefined && [13, 14].includes(item.rowNumber)) return true;
  if (!item.solutionRefs.length) return false;
  if (/video output cable/i.test(item.group) || /video output cable/i.test(item.name)) return true;
  return groupItems.length === 1 && item.solutionRefs.includes(state.familyId);
}

function seedPresetSelections() {
  const accessoryGroups = groupedItems(accessoryCandidates());
  const packageIds = new Set(packageCandidates().map((item) => item.id));
  for (const item of itemsForFamily()) {
    if (!state.selections[item.id]) {
      const groupItems = accessoryGroups[item.group] || [];
      state.selections[item.id] = {
        checked: packageIds.has(item.id) ? item.id === state.packageId : suggestAccessorySelection(item, groupItems),
        quantity: item.quantity || "1",
      };
    }
  }
  if (state.packageId && state.selections[state.packageId]) {
    state.selections[state.packageId].checked = true;
  }
}

function resetCustomState() {
  state.custom = {
    host: null,
    powerBox: null,
    wiring: {},
    wiringExtras: {},
    accessoryEditor: null,
    accessories: {},
    optionals: {},
  };
}

function resetScenarioState() {
  state.packageId = null;
  state.selections = {};
  resetCustomState();
  if (isAvmProduct()) {
    state.avm = {
      mode: "standalone",
      cascadeHost: "adplus20",
      ahdRoute: "direct",
      cameraExtensions: [9, 9, 9, 9],
      storageQuantity: 0,
      storageVariants: [SD_CARD_VARIANTS[0].partNumber, SD_CARD_VARIANTS[0].partNumber],
    };
  }
  if (isMSeriesProduct()) {
    state.packageId = packageCandidates()[0]?.id || null;
    if (state.packageId) {
      const pkg = packageCandidates().find((item) => item.id === state.packageId);
      state.selections[state.packageId] = { checked: true, quantity: pkg?.quantity || "1" };
    }
    return;
  }
  if (!isCustomFlow()) {
    state.packageId = packageCandidates()[0]?.id || null;
    seedPresetSelections();
    if (isC6Product()) {
      const initialKit = currentPackage();
      const powerModel = /CAN/i.test(initialKit?.group || "") ? "can" : "rs232";
      const defaultPowerRow = powerModel === "can" ? 12 : 27;
      state.c6 = { powerModel };
      const defaultPower = product.items.find((item) => item.rowNumber === defaultPowerRow);
      if (defaultPower) state.selections[defaultPower.id] = { checked: true, quantity: "1" };
    }
  }
}

function chooseScenario(scenarioId) {
  const scenario = scenarios.find((item) => item.scenarioId === scenarioId);
  if (!scenario) return;
  state.productPickerOpen = isAdplusProduct();
  state.scenarioId = scenario.scenarioId;
  state.familyId = scenario.familyId;
  state.step = 1;
  resetScenarioState();
  render();
}

function chooseProduct(productId) {
  const nextProduct = catalog.productLines.find((item) => item.id === productId);
  if (!nextProduct) return;
  state.avmCascade = null;
  state.c53Cascade = null;
  state.productId = productId;
  state.productPickerOpen = true;
  product = nextProduct;
  scenarios = buildScenarios();
  if (productId === "adplus20") {
    const customScenario = scenarios.find((item) => item.scenarioId === CUSTOM_SCENARIO_ID);
    state.scenarioId = customScenario?.scenarioId || scenarios[0]?.scenarioId || null;
    state.familyId = customScenario?.familyId || scenarios[0]?.familyId || null;
  } else {
    state.scenarioId = scenarios[0]?.scenarioId || null;
    state.familyId = scenarios[0]?.familyId || null;
  }
  state.step = 1;
  resetScenarioState();
  render();
}

function choosePackage(packageId) {
  state.packageId = packageId;
  if (isC6Product()) {
    const pkg = product?.items?.find((item) => item.id === packageId);
    state.familyId = pkg?.solutionRefs?.[0] || null;
    state.c6 = state.c6 || {};
    state.c6.powerModel = /CAN/i.test(pkg?.group || "") ? "can" : "rs232";
    const powerRows = [10, 11, 12, 13, 27, 28];
    const defaultPowerRow = state.c6.powerModel === "can" ? 12 : 27;
    c6Items(powerRows).forEach((item) => {
      if (!state.selections[item.id]) state.selections[item.id] = { checked: false, quantity: "1" };
      state.selections[item.id].checked = item.rowNumber === defaultPowerRow;
    });
    // These catalog items are not part of the guided C6 flow. Clear any stale
    // selection left by an older session before rebuilding the BOM.
    c6Items([9, 14, 15]).forEach((item) => {
      if (state.selections[item.id]) state.selections[item.id].checked = false;
    });
  }
  for (const item of packageCandidates()) {
    if (!state.selections[item.id]) state.selections[item.id] = { checked: false, quantity: item.quantity || "1" };
    state.selections[item.id].checked = item.id === packageId;
  }
  render();
}

function currentPackage() {
  return packageCandidates().find((item) => item.id === state.packageId) || null;
}

function packagePreview(item) {
  const curated = skuInfo(item.partNumber)?.image;
  if (curated) return { src: curated, fallback: false };
  const ownImage = pickPreviewAsset(item.images);
  if (ownImage) return { src: ownImage, fallback: false };
  const scenarioImage = currentScenario()?.image || "";
  return scenarioImage ? { src: scenarioImage, fallback: true } : { src: "", fallback: false };
}

function selectedCustomHost() {
  return customCatalog.hosts.find((item) => item.id === state.custom.host) || null;
}

function selectedCustomPowerBox() {
  return customCatalog.powerBoxes.find((item) => item.id === state.custom.powerBox) || null;
}

function selectedCustomWirings() {
  return customCatalog.wiringModes.filter((item) => state.custom.wiring[item.id]);
}

function customPowerBoxPreview(powerBoxId) {
  const host = selectedCustomHost();
  if (!host) return "";
  if (powerBoxId === "standard") return host.image || "";
  const packageItem = findItemByRow(host.packageRows[powerBoxId]);
  return pickPreviewAsset(packageItem?.images || []) || host.image || "";
}

function customWiringPreview(modeId, powerBoxId) {
  if (!powerBoxId) return "";
  if (powerBoxId === "standard" && modeId === "loose") return "North America Sales List-FILE/AD Plus 2_0/Image/hard wire.png";
  if ((powerBoxId === "plus" || powerBoxId === "max") && modeId === "loose") return "North America Sales List-FILE/AD Plus 2_0/Image/hardwire pbm.png";
  if (powerBoxId === "standard" && modeId === "9pin") return pickPreviewAsset(findItemByRow(22)?.images || []);
  if (powerBoxId === "standard" && modeId === "16pin") return pickPreviewAsset(findItemByRow(23)?.images || []);
  if ((powerBoxId === "plus" || powerBoxId === "max") && modeId === "9pin") return pickPreviewAsset(findItemByRow(24)?.images || []);
  if ((powerBoxId === "plus" || powerBoxId === "max") && modeId === "16pin") return "North America Sales List-FILE/AD Plus 2_0/Image/16pinobd for pbm pbp.png";
  return "";
}

function customWiringSku(modeId, powerBoxId) {
  if (powerBoxId === "standard" && modeId === "loose") return "1261090100038";
  if ((powerBoxId === "plus" || powerBoxId === "max") && modeId === "16pin") return "1260040100242";
  const mode = customCatalog.wiringModes.find((item) => item.id === modeId);
  const rowNumber = mode?.rows?.[powerBoxId];
  return rowNumber ? findItemByRow(rowNumber)?.partNumber || "" : "";
}

function customPackageItem() {
  const host = selectedCustomHost();
  const powerBox = selectedCustomPowerBox();
  if (!host || !powerBox) return null;
  return findItemByRow(host.packageRows[powerBox.id]);
}

function selectedCustomAccessoryDefs() {
  return customCatalog.accessories.filter((item) => {
    const stateBlock = state.custom.accessories[item.id];
    if (!stateBlock) return false;
    if (item.cameraType) return Number(stateBlock.quantity || 0) > 0;
    return Boolean(stateBlock.checked);
  });
}

function selectedCustomOptionalDefs() {
  const powerBox = selectedCustomPowerBox();
  return customCatalog.optionals.filter(
    (item) => state.custom.optionals[item.id]?.checked && (!powerBox || item.allowedPowerBoxes.includes(powerBox.id))
  );
}

function ca42TrailerAdapterEnabled() {
  const ca42State = ensureAccessoryState("ca42");
  return Number(ca42State.quantity || 0) > 0 && Boolean(ca42State.addonChecked);
}

function ca42TrailerAdapterBlocksRwatch() {
  const powerBox = selectedCustomPowerBox();
  return powerBox?.id === "standard" && ca42TrailerAdapterEnabled();
}

function visibleCustomOptionals() {
  const powerBox = selectedCustomPowerBox();
  if (!powerBox) return [];
  return customCatalog.optionals.filter((item) => item.allowedPowerBoxes.includes(powerBox.id));
}

function isOptionalDisabled(optionalDef) {
  return optionalDef.id === "rwatch" && ca42TrailerAdapterBlocksRwatch();
}

function avmCascadeActive() {
  return Boolean(state.avmCascade && state.productId === state.avmCascade.host);
}

function avmCascadeReserved() {
  if (avmCascadeActive()) return state.avmCascade.reserved || { ipc: 0, ahd: 0, recording: 0 };
  if (c53CascadeActive()) return state.c53Cascade.reserved || { ipc: 0, ahd: 0, recording: 0 };
  return { ipc: 0, ahd: 0, recording: 0 };
}

function hostCascadeActive() {
  return avmCascadeActive() || c53CascadeActive();
}

function hostCascadeName() {
  return avmCascadeActive() ? "AVM" : (c53CascadeActive() ? "C53" : "");
}

function selectedCameraCounts() {
  const reserved = avmCascadeReserved();
  return selectedCustomAccessoryDefs().reduce(
    (acc, item) => {
      const qty = Number(ensureAccessoryState(item.id).quantity || 0);
      if (item.cameraType === "ipc") acc.ipc += qty;
      if (item.cameraType === "ahd") acc.ahd += qty;
      return acc;
    },
    { ipc: reserved.ipc, ahd: reserved.ahd }
  );
}

function cameraCapacityRule() {
  const powerBox = selectedCustomPowerBox();
  if (!powerBox) return null;
  if (powerBox.id === "standard" || powerBox.id === "plus") {
    return {
      maxIpc: 1,
      maxAhd: 1,
      label: L("当前方案最多 1 路 IPC + 1 路 AHD", "This setup supports up to 1 IPC + 1 AHD"),
    };
  }
  if (powerBox.id === "max") {
    return {
      maxIpc: 1,
      maxAhdWithIpc: 3,
      maxAhdOnly: 4,
      label: L("PBM 最多 1 路 IPC + 3 路 AHD，或者 4 路 AHD", "PBM supports up to 1 IPC + 3 AHD, or 4 AHD"),
    };
  }
  return null;
}

function cameraCapacityWarning() {
  const rule = cameraCapacityRule();
  if (!rule) return "";
  const counts = selectedCameraCounts();
  const overText = "Selection exceeds the camera limit";
  if (rule.maxAhd !== undefined) {
    if (counts.ipc > rule.maxIpc || counts.ahd > rule.maxAhd) {
      return `${overText}: ${rule.label}`;
    }
    return "";
  }
  if (counts.ipc > rule.maxIpc) return `${overText}: ${rule.label}`;
  if (counts.ipc >= 1 && counts.ahd > rule.maxAhdWithIpc) return `${overText}: ${rule.label}`;
  if (counts.ipc === 0 && counts.ahd > rule.maxAhdOnly) return `${overText}: ${rule.label}`;
  return "";
}

function cameraCapacityStatus() {
  const rule = cameraCapacityRule();
  const counts = selectedCameraCounts();
  if (!rule) return { ipcRemaining: Infinity, ahdRemaining: Infinity, warning: "" };
  if (rule.maxAhd !== undefined) {
    return {
      ipcRemaining: Math.max(0, rule.maxIpc - counts.ipc),
      ahdRemaining: Math.max(0, rule.maxAhd - counts.ahd),
      warning: cameraCapacityWarning(),
    };
  }
  const ipcRemaining = counts.ahd >= rule.maxAhdOnly ? 0 : Math.max(0, rule.maxIpc - counts.ipc);
  const ahdLimit = counts.ipc >= 1 ? rule.maxAhdWithIpc : rule.maxAhdOnly;
  return {
    ipcRemaining,
    ahdRemaining: Math.max(0, ahdLimit - counts.ahd),
    warning: cameraCapacityWarning(),
  };
}

function isAccessoryChoiceDisabled(accessoryDef) {
  const accessoryState = ensureAccessoryState(accessoryDef.id);
  if (accessoryState.checked || !accessoryDef.cameraType) return false;
  const status = cameraCapacityStatus();
  if (accessoryDef.cameraType === "ipc") return status.ipcRemaining <= 0;
  if (accessoryDef.cameraType === "ahd") return status.ahdRemaining <= 0;
  return false;
}

function maxAccessoryQuantity(accessoryDef) {
  if (!accessoryDef.cameraType) return 1;
  const currentState = ensureAccessoryState(accessoryDef.id);
  const currentQty = Number(currentState.quantity || 0);
  const counts = selectedCameraCounts();
  const otherIpc = counts.ipc - (accessoryDef.cameraType === "ipc" ? currentQty : 0);
  const otherAhd = counts.ahd - (accessoryDef.cameraType === "ahd" ? currentQty : 0);
  const powerBox = selectedCustomPowerBox();
  if (!powerBox) return 1;
  const perAccessoryMax = Number(accessoryDef.maxQuantityByPowerBox?.[powerBox.id] ?? accessoryDef.maxQuantity ?? Infinity);
  if (powerBox.id === "standard" || powerBox.id === "plus") {
    if (accessoryDef.cameraType === "ipc") return Math.min(perAccessoryMax, Math.max(0, 1 - otherIpc));
    if (accessoryDef.cameraType === "ahd") return Math.min(perAccessoryMax, Math.max(0, 1 - otherAhd));
    return 1;
  }
  if (powerBox.id === "max") {
    if (accessoryDef.cameraType === "ipc") {
      if (otherAhd >= 4) return 0;
      return Math.min(perAccessoryMax, Math.max(0, 1 - otherIpc));
    }
    if (accessoryDef.cameraType === "ahd") {
      const limit = otherIpc >= 1 ? 3 : 4;
      return Math.min(perAccessoryMax, Math.max(0, limit - otherAhd));
    }
  }
  return 1;
}

function normalizeAccessorySelections() {
  for (const def of customCatalog.accessories) {
    const stateBlock = ensureAccessoryState(def.id);
    if (!def.cameraType) {
      stateBlock.checked = Boolean(stateBlock.checked);
      if (stateBlock.checked && !stateBlock.extension && def.extensionRows?.length) {
        stateBlock.extension = findItemByRow(def.extensionRows[0])?.id || "";
      }
      if (stateBlock.checked && !stateBlock.extraExtension && def.secondaryExtensionRows?.length) {
        stateBlock.extraExtension = findItemByRow(def.secondaryExtensionRows[0])?.id || "";
      }
      continue;
    }
    if (Number(stateBlock.quantity || 0) <= 0) {
      stateBlock.checked = false;
      stateBlock.quantity = 0;
      stateBlock.extension = "";
      stateBlock.extraExtension = "";
      stateBlock.addonChecked = false;
      stateBlock.extensions = [];
      continue;
    }
    const maxQty = Math.max(0, maxAccessoryQuantity(def));
    stateBlock.checked = true;
    stateBlock.quantity = Math.min(Math.max(1, Number(stateBlock.quantity || 1)), maxQty);
    const defaultExtensionId = def.extensionRows?.length ? findItemByRow(def.extensionRows[0])?.id || "" : "";
    stateBlock.extensions = Array.from(
      { length: Number(stateBlock.quantity || 0) },
      (_, index) => stateBlock.extensions?.[index] || defaultExtensionId
    );
    stateBlock.extension = stateBlock.extensions[0] || stateBlock.extension || "";
  }
}

function orderedCustomAccessories() {
  const powerBox = selectedCustomPowerBox();
  return customCatalog.accessories
    .filter((item) => !item.allowedPowerBoxes || (powerBox && item.allowedPowerBoxes.includes(powerBox.id)))
    .sort((left, right) => {
      const leftRank = left.cameraType ? 0 : 1;
      const rightRank = right.cameraType ? 0 : 1;
      if (leftRank !== rightRank) return leftRank - rightRank;
      return (left.sortOrder || 0) - (right.sortOrder || 0);
    });
}

function extractCableLength(item) {
  const text = [item?.note, item?.description, item?.name].filter(Boolean).join(" ");
  const match = text.match(/(\d+(?:\.\d+)?)\s*(M|CM|MM)\b/i);
  return match ? `${match[1]}${match[2].toUpperCase()}` : "";
}

function formatExtensionOptionLabel(item) {
  const length = extractCableLength(item);
  const rawName = typeof item?.name === "string" ? item.name : displayCatalogText(item?.name || "");
  const name = normalizeWhitespace((rawName || "").split(/\r?\n/)[0]);
  const partNumber = item?.partNumber || t().noPartNumber;
  return [length, name, partNumber].filter(Boolean).join(" | ");
}

function extensionLengthValue(item) {
  const text = [item?.note, item?.description, item?.name].filter(Boolean).join(" ");
  const match = text.match(/(\d+(?:\.\d+)?)\s*(M|CM|MM)\b/i);
  if (!match) return Number.POSITIVE_INFINITY;
  const value = Number(match[1]);
  const unit = match[2].toUpperCase();
  if (unit === "MM") return value / 1000;
  if (unit === "CM") return value / 100;
  return value;
}

function accessoryDetailText(def) {
  if (def.id === "screen") return state.language === "zh" ? UI.zh.accessoryDetails.screen : UI.en.accessoryDetails.screen;
  return state.language === "zh" ? def.detail : def.detailEn;
}

function optionalDetailText(def) {
  return state.language === "zh" ? def.detail : def.detailEn;
}

function ensureAccessoryState(accessoryId) {
  if (!state.custom.accessories[accessoryId]) {
    state.custom.accessories[accessoryId] = { checked: false, extension: "", extraExtension: "", addonChecked: false, extensions: [], quantity: 0 };
  }
  return state.custom.accessories[accessoryId];
}

function ensureOptionalState(optionalId) {
  if (!state.custom.optionals[optionalId]) {
    state.custom.optionals[optionalId] = {
      checked: false,
      extension: "",
      extensions: [],
      quantity: 0,
      variant1: SD_CARD_VARIANTS[0].partNumber,
      variant2: SD_CARD_VARIANTS[0].partNumber,
    };
  }
  return state.custom.optionals[optionalId];
}

function setCustomHost(hostId) {
  state.custom.host = hostId;
  render();
}

function setCustomPowerBox(powerBoxId) {
  const changed = state.custom.powerBox !== powerBoxId;
  state.custom.powerBox = powerBoxId;
  if (changed) {
    applyDefaultWiring();
    state.custom.optionals = {};
    normalizeAccessorySelections();
  }
  render();
}

function isWiringSupported(mode) {
  const powerBoxId = state.custom.powerBox;
  return powerBoxId ? Boolean(mode.support[powerBoxId]) : false;
}

function applyDefaultWiring() {
  state.custom.wiring = {};
  state.custom.wiringExtras = {};
  if (state.custom.powerBox === "standard") state.custom.wiring.loose = true;
  if (state.custom.powerBox === "plus" || state.custom.powerBox === "max") {
    state.custom.wiring["16pin"] = true;
    state.custom.wiringExtras.power16Extension = true;
  }
}

function toggleCustomWiring(wiringId, checked) {
  const powerBoxId = state.custom.powerBox;
  if ((powerBoxId === "standard" && wiringId === "loose") || ((powerBoxId === "plus" || powerBoxId === "max") && wiringId === "16pin")) {
    state.custom.wiring[wiringId] = true;
    render();
    return;
  }
  state.custom.wiring[wiringId] = checked;
  render();
}

function toggleCustomWiringExtra(extraId, checked) {
  state.custom.wiringExtras[extraId] = checked;
  render();
}

function toggleCustomAccessory(accessoryId, checked) {
  const accessoryDef = customCatalog.accessories.find((item) => item.id === accessoryId);
  if (!accessoryDef) return;
  const accessoryState = ensureAccessoryState(accessoryId);
  if (accessoryDef.cameraType) {
    accessoryState.quantity = checked ? Math.max(1, Number(accessoryState.quantity || 1)) : 0;
    accessoryState.checked = accessoryState.quantity > 0;
    if (!accessoryState.checked) accessoryState.addonChecked = false;
    normalizeAccessorySelections();
    render();
    return;
  }
  accessoryState.checked = checked;
  accessoryState.quantity = checked ? 1 : 0;
  if (checked && !accessoryState.extension && accessoryDef.extensionRows?.length) {
    const defaultExtension = findItemByRow(accessoryDef.extensionRows[0]);
    accessoryState.extension = defaultExtension?.id || "";
  }
  if (checked && !accessoryState.extraExtension && accessoryDef.secondaryExtensionRows?.length) {
    const defaultExtraExtension = findItemByRow(accessoryDef.secondaryExtensionRows[0]);
    accessoryState.extraExtension = defaultExtraExtension?.id || "";
  }
  if (!checked) {
    accessoryState.extension = accessoryDef.lockExtension && accessoryDef.extensionRows?.length
      ? findItemByRow(accessoryDef.extensionRows[0])?.id || ""
      : "";
    accessoryState.extraExtension = "";
  }
  normalizeAccessorySelections();
  render();
}

function setCustomAccessoryQuantity(accessoryId, quantity) {
  const accessoryDef = customCatalog.accessories.find((item) => item.id === accessoryId);
  if (!accessoryDef) return;
  const accessoryState = ensureAccessoryState(accessoryId);
  const maxQty = Math.max(0, maxAccessoryQuantity(accessoryDef));
  accessoryState.quantity = Math.min(Math.max(0, Number(quantity || 0)), maxQty);
  accessoryState.checked = accessoryState.quantity > 0;
  normalizeAccessorySelections();
  if (accessoryDef.cameraType) {
    if (accessoryState.quantity > 0) {
      state.custom.accessoryEditor = accessoryId;
    } else if (state.custom.accessoryEditor === accessoryId) {
      state.custom.accessoryEditor = null;
    }
  }
  render();
}

function openAccessoryEditor(accessoryId) {
  state.custom.accessoryEditor = accessoryId;
  render();
}

function closeAccessoryEditor() {
  state.custom.accessoryEditor = null;
  render();
}

function toggleCustomOptional(optionalId, checked) {
  const optionalDef = customCatalog.optionals.find((item) => item.id === optionalId);
  if (!optionalDef) return;
  if (isOptionalDisabled(optionalDef)) return;
  const optionalState = ensureOptionalState(optionalId);
  if (optionalDef.maxQuantity) {
    optionalState.quantity = checked ? Math.max(1, Number(optionalState.quantity || 1)) : 0;
    optionalState.checked = optionalState.quantity > 0;
    if (optionalDef.extensionRows?.length) {
      const defaultExtension = findItemByRow(optionalDef.extensionRows[0])?.id || "";
      optionalState.extensions = Array.from(
        { length: Number(optionalState.quantity || 0) },
        (_, index) => optionalState.extensions?.[index] || defaultExtension
      );
      optionalState.extension = optionalState.extensions[0] || "";
    }
    render();
    return;
  }
  optionalState.checked = checked;
  if (checked && !optionalState.extension && optionalDef.extensionRows?.length) {
    const defaultExtension = findItemByRow(optionalDef.extensionRows[0]);
    optionalState.extension = defaultExtension?.id || "";
  }
  if (!checked) {
    optionalState.extension = optionalDef.lockExtension && optionalDef.extensionRows?.length
      ? findItemByRow(optionalDef.extensionRows[0])?.id || ""
      : "";
  }
  render();
}

function setAccessoryExtension(accessoryId, nextValue, slot = 0, stateField = "extension") {
  const accessoryDef = customCatalog.accessories.find((item) => item.id === accessoryId);
  const accessoryState = ensureAccessoryState(accessoryId);
  if (!accessoryDef) return;
  if (nextValue === "none") {
    if (!window.confirm(t().confirmRemoveCable)) {
      render();
      return;
    }
    if (stateField === "extensions") {
      accessoryState.extensions[slot] = "";
      if (slot === 0) accessoryState.extension = "";
    } else {
      accessoryState[stateField] = "";
    }
    render();
    return;
  }
  const matchedItem = findItemByRow(Number(nextValue));
  const matchedId = matchedItem?.id || "";
  if (accessoryDef.cameraType && stateField === "extensions") {
    accessoryState.extensions[slot] = matchedId;
    if (slot === 0) accessoryState.extension = matchedId;
  } else {
    accessoryState[stateField] = matchedId;
  }
  render();
}

function toggleAccessoryAddon(accessoryId, checked) {
  const accessoryState = ensureAccessoryState(accessoryId);
  accessoryState.addonChecked = checked;
  if (accessoryId === "ca42" && checked && selectedCustomPowerBox()?.id === "standard") {
    const rwatchState = ensureOptionalState("rwatch");
    rwatchState.checked = false;
    rwatchState.quantity = 0;
  }
  render();
}

function setOptionalExtension(optionalId, nextValue, slot = 0) {
  const optionalDef = customCatalog.optionals.find((item) => item.id === optionalId);
  const optionalState = ensureOptionalState(optionalId);
  const matchedItem = findItemByRow(Number(nextValue));
  const matchedId = matchedItem?.id || (optionalDef?.requiredExtension
    ? findItemByRow(optionalDef.extensionRows?.[0])?.id || ""
    : "");
  if (optionalDef?.maxQuantity && optionalDef.extensionRows?.length) {
    optionalState.extensions[slot] = matchedId;
    if (slot === 0) optionalState.extension = matchedId;
  } else {
    optionalState.extension = matchedId;
  }
  render();
}

function setOptionalQuantity(optionalId, quantity) {
  const optionalDef = customCatalog.optionals.find((item) => item.id === optionalId);
  const optionalState = ensureOptionalState(optionalId);
  const maxQty = Math.max(1, Number(optionalDef?.maxQuantity || 2));
  optionalState.quantity = Math.min(maxQty, Math.max(0, Number(quantity || 0)));
  optionalState.checked = optionalState.quantity > 0;
  if (optionalDef?.extensionRows?.length) {
    const defaultExtension = findItemByRow(optionalDef.extensionRows[0])?.id || "";
    optionalState.extensions = Array.from(
      { length: Number(optionalState.quantity || 0) },
      (_, index) => optionalState.extensions?.[index] || defaultExtension
    );
    optionalState.extension = optionalState.extensions[0] || "";
  }
  render();
}

function setOptionalVariant(optionalId, slot, partNumber) {
  const optionalState = ensureOptionalState(optionalId);
  if (slot === 1) optionalState.variant1 = partNumber;
  if (slot === 2) optionalState.variant2 = partNumber;
  render();
}

function wiringSummaryText() {
  const powerBox = selectedCustomPowerBox();
  const modes = selectedCustomWirings();
  if (!modes.length || !powerBox) return "";
  return modes
    .map((mode) => {
      const supportType = mode.support[powerBox.id];
      if (supportType === "builtin") return `${localizedText(mode.title)} (${"included"})`;
      if (supportType === false) return "";
      if (mode.id === "16pin" && (powerBox.id === "plus" || powerBox.id === "max")) return localizedText(mode.title);
      const item = findItemByRow(mode.rows[powerBox.id]);
      return normalizeWhitespace(item?.name || localizedText(mode.title));
    })
    .filter(Boolean)
    .join(" / ");
}
