const stepPillsEl = document.getElementById("step-pills");
const stepCopyEl = document.getElementById("step-copy");
const wizardTopEl = document.querySelector(".wizard-top");
const wizardStageEl = document.getElementById("wizard-stage");
const summaryMetaEl = document.getElementById("summary-meta");
const cartListEl = document.getElementById("cart-list");
const prevStepBtn = document.getElementById("prev-step");
const nextStepBtn = document.getElementById("next-step");
const exportExcelBtn = document.getElementById("export-excel");
const feedbackButton = document.getElementById("feedback-button");
const annotationButton = document.getElementById("annotation-button");
const feedbackDialog = document.getElementById("feedback-dialog");
const feedbackForm = document.getElementById("feedback-form");
const feedbackMessage = document.getElementById("feedback-message");
const feedbackContact = document.getElementById("feedback-contact");
const feedbackStatus = document.getElementById("feedback-status");
const releaseDialog = document.getElementById("release-dialog");
const releaseContent = document.getElementById("release-content");
const annotationDialog = document.getElementById("annotation-dialog");
const annotationForm = document.getElementById("annotation-form");
const annotationTarget = document.getElementById("annotation-target");
const annotationMessage = document.getElementById("annotation-message");
const annotationContact = document.getElementById("annotation-contact");
const annotationStatus = document.getElementById("annotation-status");

const state = {
  productId: "adplus20",
  language: "en",
  step: 1,
  productPickerOpen: true,
  scenarioId: null,
  familyId: null,
  packageId: null,
  selections: {},
  custom: {
    host: null,
    powerBox: null,
    wiring: {},
    wiringExtras: {},
    accessoryEditor: null,
    accessories: {},
    optionals: {},
  },
  c6: { powerModel: null },
  avm: { mode: null },
  avmCascade: null,
  c53: { mode: null, cascadeHost: null },
  c53Cascade: null,
};

function t() {
  return UI[state.language] || UI.en;
}

// Pick the Chinese or English variant based on the active language.
function L(zh, en) {
  return state.language === "zh" ? zh : en;
}

function localizedText(value) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value[state.language] || value.zh || value.en || "";
  }
  return String(value || "");
}

function pickPreviewAsset(assets = []) {
  return assets.find((asset) => /\.(png|jpe?g|gif|webp|bmp)$/i.test(asset)) || "";
}

const SUPPLEMENTAL_PREVIEW_BY_PART = {
  "5154022100006": "North America Sales List-FILE/C6 Lite 2_0/Image/C6lite2.0dual.png",
  "5154022100020": "North America Sales List-FILE/C6 Lite 2_0/Image/C6lite2.0single.png",
  "5152119100007": "North America Sales List-FILE/AD Plus 2_0/Image/33-C29N-image.png",
  "5151003100126": "North America Sales List-FILE/C6 Lite 2_0/Image/21-Square Camera-image.png",
  "5151022100069": "assets/shared-media/camera-metal-snail.png",
  "5190012100075": "North America Sales List-FILE/960C53/图片/25-7-inch Screen-图片4.png",
  "5090091100025": "North America Sales List-FILE/960C53/图片/34-B2-R-image.png",
  "5090091100026": "North America Sales List-FILE/960C53/图片/35-B2-L-image.png",
  "5190067100044": "North America Sales List-FILE/M3N/Image/5-R-Watch-image.png",
  "5151036100003": "North America Sales List-FILE/M3N/Image/10-CA29M-image.png",
  "5151019100038": "North America Sales List-FILE/M3N/Image/11-CA20S-image.png",
  "5200007100101": "North America Sales List-FILE/M3N/Image/12-AD Kit 3.0-image.gif",
  "5151053100007": "North America Sales List-FILE/M3N/Image/16-CA46-image.png",
  "5190076100018": "North America Sales List-FILE/M3N/Image/2-惯导模块-image.png",
  "1261050100409": "North America Sales List-FILE/M3N/Image/4-20PIN Plug Signal Cable-image.png",
  "1210040000008": "North America Sales List-FILE/M3N/Image/6-Alarm Serial Port Connection Cable-image.png",
  "1610002100008": "North America Sales List-FILE/M1N 2_0/Image/36-Micro SD Card-image.png",
  "1610002100007": "North America Sales List-FILE/M1N 2_0/Image/36-Micro SD Card-image.png",
  "1610002100006": "North America Sales List-FILE/M1N 2_0/Image/36-Micro SD Card-image.png",
  "1610002100005": "North America Sales List-FILE/M1N 2_0/Image/36-Micro SD Card-image.png",
  "1610004100014": "North America Sales List-FILE/M3N/Image/37-M.2 SSD-image.png",
  "1610004100013": "North America Sales List-FILE/M3N/Image/37-M.2 SSD-image.png",
  "1610004100012": "North America Sales List-FILE/M3N/Image/37-M.2 SSD-image.png",
};

SUPPLEMENTAL_PREVIEW_BY_PART["1262010000025"] = "assets/shared-media/m3n-b2-cable-single.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1262010100031"] = "assets/shared-media/m3n-b2-cable-dual.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1120041000455"] = "assets/shared-media/m3n-adkit-bracket.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1160010100023"] = "assets/shared-media/m3n-adkit-bracket-screw.png";
SUPPLEMENTAL_PREVIEW_BY_PART["5190015100004"] = "assets/shared-media/m3n-speaker-a.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1260011000026"] = "assets/shared-media/m3n-speaker-adapter-cable.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1261050000056"] = "assets/shared-media/m3n-microphone-cable.png";
SUPPLEMENTAL_PREVIEW_BY_PART["5190015100021"] = "assets/shared-media/m3n-microphone-alt.png";
SUPPLEMENTAL_PREVIEW_BY_PART["5190021100004"] = "assets/shared-media/m3n-microphone-alt.png";
SUPPLEMENTAL_PREVIEW_BY_PART["1260040100057"] = "assets/shared-media/m3n-microphone-cable.png";

function fallbackItemPreviewAsset(item) {
  if (!item) return "";
  const direct = pickPreviewAsset(item.images || []);
  if (direct) return direct;
  const normalizedPart = normalizeWhitespace(item.partNumber);
  if (normalizedPart && SUPPLEMENTAL_PREVIEW_BY_PART[normalizedPart]) {
    return SUPPLEMENTAL_PREVIEW_BY_PART[normalizedPart];
  }
  if (!normalizedPart) return "";
  const productPriority = ["adplus20", "m1n20", "m3n", "c6lite20", "avm", "z5", "960c53", "966c46ipc"];
  for (const productId of productPriority) {
    const line = catalog.productLines.find((entry) => entry.id === productId);
    const match = line?.items?.find(
      (entry) => normalizeWhitespace(entry.partNumber) === normalizedPart && pickPreviewAsset(entry.images || [])
    );
    const preview = pickPreviewAsset(match?.images || []);
    if (preview) return preview;
  }
  return "";
}

function normalizeWhitespace(value) {
  return String(value || "").replace(/\s+/g, " ").trim();
}

function englishCatalogText(value) {
  const lines = String(value || "")
    .split(/\n+/)
    .map((line) => normalizeWhitespace(line))
    .filter(Boolean);
  if (lines.length > 1) {
    return lines.find((line) => /[A-Za-z]/.test(line)) || lines[0];
  }
  const compact = normalizeWhitespace(value);
  const stripped = compact.replace(/[\u4e00-\u9fff()]/g, "").replace(/\s+/g, " ").trim();
  return stripped || compact;
}

function chineseCatalogText(value) {
  const lines = String(value || "")
    .split(/\n+/)
    .map((line) => normalizeWhitespace(line))
    .filter(Boolean);
  const zhLine = lines.find((line) => /[\u4e00-\u9fff]/.test(line));
  return zhLine || normalizeWhitespace(value);
}

function bilingualCatalogText(value) {
  return {
    zh: chineseCatalogText(value),
    en: englishCatalogText(value),
  };
}

function displayCatalogText(value) {
  return state.language === "zh" ? chineseCatalogText(value) : englishCatalogText(value);
}

function findItemByRow(rowNumber) {
  return product?.items.find((item) => item.rowNumber === rowNumber) || null;
}

function findCatalogItem(productId, rowNumber) {
  const line = catalog.productLines.find((item) => item.id === productId);
  return line?.items.find((item) => item.rowNumber === rowNumber) || null;
}

// Shared component library keyed by part number (SKU).
// Holds the *presentation* of a physical part (curated title / image / description) so the
// same camera looks identical in every product instead of being re-described per flow.
// Flow-specific behaviour (cameraType, extension rows, power-box rules) stays with each consumer.
const SKU_LIBRARY = {
  // --- cameras already curated for the AD Plus flow ---
  "5152119100007": { title: { zh: "C29N DMS camera", en: "C29N DMS camera" },
    detail: UI.zh.accessoryDetails.c29n, detailEn: UI.en.accessoryDetails.c29n },
  "5151053100007": { title: { zh: "CA46 BSD camera", en: "CA46 BSD camera" },
    image: "North America Sales List-FILE/AD Plus 2_0/Image/15-CA46-image.png",
    detail: UI.zh.accessoryDetails.ca46_adplus, detailEn: UI.en.accessoryDetails.ca46_adplus },
  "5051043100003": { title: { zh: "CA38 reverse camera", en: "CA38 reverse camera" },
    image: "assets/shared-media/camera-ca38.png",
    detail: UI.zh.accessoryDetails.ca38, detailEn: UI.en.accessoryDetails.ca38 },
  "5200027100004": { title: { zh: "CA42 wireless camera", en: "CA42 wireless camera" },
    detail: UI.zh.accessoryDetails.ca42, detailEn: UI.en.accessoryDetails.ca42 },
  "5151022100069": { title: { zh: "CA46 金属海螺", en: "Metal snail camera" },
    image: "assets/shared-media/camera-metal-snail.png",
    detail: UI.zh.accessoryDetails.ca46_m1n, detailEn: UI.en.accessoryDetails.ca46_m1n },
  "5151003100126": { title: { zh: "Square camera", en: "Square camera" },
    image: "North America Sales List-FILE/C6 Lite 2_0/Image/21-Square Camera-image.png",
    detail: UI.zh.accessoryDetails.square_camera_m1n, detailEn: UI.en.accessoryDetails.square_camera_m1n },
  // --- cameras that only existed as raw catalog rows (no AD Plus curation) ---
  "5151036100003": { title: { zh: "CA29M DMS camera", en: "CA29M DMS camera" },
    image: "North America Sales List-FILE/M3N/Image/10-CA29M-image.png" },
  "5151019100038": { title: { zh: "CA20S ADAS camera", en: "CA20S ADAS camera" },
    image: "North America Sales List-FILE/M3N/Image/11-CA20S-image.png" },
  "5200007100101": { title: { zh: "AD Kit 3.0 (DMS + ADAS)", en: "AD Kit 3.0 (DMS + ADAS)" },
    image: "North America Sales List-FILE/M3N/Image/12-AD Kit 3.0-image.gif" },
  // --- optionals shared with the AD Plus flow (screen / alarms) ---
  "5190012100075": { title: { zh: "DP7S 屏幕", en: "DP7S screen" },
    image: "assets/shared-media/screen-dp7s.png",
    detail: UI.zh.accessoryDetails.screen, detailEn: UI.en.accessoryDetails.screen },
  "5090091100025": { title: { zh: "B2 sound and light alarm", en: "B2 sound and light alarm" },
    image: "North America Sales List-FILE/AD Plus 2_0/Image/b2.png",
    detail: UI.zh.optionalDetails.b2, detailEn: UI.en.optionalDetails.b2 },
  "5090091100026": { title: { zh: "B2 sound and light alarm", en: "B2 sound and light alarm" },
    image: "North America Sales List-FILE/AD Plus 2_0/Image/b2.png",
    detail: UI.zh.optionalDetails.b2, detailEn: UI.en.optionalDetails.b2 },
  "5190108100003": { title: { zh: "B3 sound and light alarm", en: "B3 sound and light alarm" },
    detail: UI.zh.optionalDetails.b3, detailEn: UI.en.optionalDetails.b3 },
  // --- C6 Lite 2.0 parts (title-only: distinguish otherwise-identical cable names) ---
  "1261090100095": { title: { zh: "16PIN OBD Power Cable (RS232)", en: "16PIN OBD Power Cable (RS232)" } },
  "1261090100117": { title: { zh: "9PIN OBD Power Cable (RS232)", en: "9PIN OBD Power Cable (RS232)" } },
  "1261090100120": { title: { zh: "16PIN OBD Power Cable (CAN)", en: "16PIN OBD Power Cable (CAN)" } },
  "1261090100121": { title: { zh: "9PIN OBD Power Cable (CAN)", en: "9PIN OBD Power Cable (CAN)" } },
  "1260010100356": { title: { zh: "AHD Extension Cable 3M", en: "AHD Extension Cable 3M" }, image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-AHD-Extension-Cable.png" },
  "1260010100357": { title: { zh: "AHD Extension Cable 5M", en: "AHD Extension Cable 5M" }, image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-AHD-Extension-Cable.png" },
  "1260010100358": { title: { zh: "AHD Extension Cable 7M", en: "AHD Extension Cable 7M" }, image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-AHD-Extension-Cable.png" },
  "1260010100359": { title: { zh: "AHD Extension Cable 9M", en: "AHD Extension Cable 9M" }, image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-AHD-Extension-Cable.png" },
  // C6 cables whose photos were embedded in the workbook (extracted here) rather than the shared image folder.
  "1260040100326": { image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-Device-Extension-Cable.png" },
  "1260011100208": { image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-AHD-Expansion-Cable.png" },
  "5151047100028": { title: { zh: "CA29P DMS camera", en: "CA29P DMS camera" } },
  // C6 Lite base kits — real dual/single product photos (catalog only had a shared wiring diagram)
  "5154022100006": { image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6lite2.0dual.png" },
  "5154022100020": { image: "North America Sales List-FILE/C6 Lite 2_0/Image/C6-2.0-S-kit.png" },
  // AVM parts — images extracted from the workbook (were missing on disk)
  "1261020100108": { title: { zh: "音视频转接线", en: "Audio-Video Adapter Cable" }, image: "North America Sales List-FILE/AVM/Image/AVM-AV-Adapter-Cable.png" },
  "1260010000130": { title: { zh: "级联转接线", en: "Cascading Mode Adapter Cable" }, image: "North America Sales List-FILE/AVM/Image/AVM-Cascading-Adapter-Cable.png" },
  "1260011100152": { title: { zh: "音视频延长线 5M", en: "Audio-Video Extension Cable 5M" }, image: "North America Sales List-FILE/AVM/Image/AVM-AV-Extension-Cable.png" },
  "1260011100153": { title: { zh: "音视频延长线 11M", en: "Audio-Video Extension Cable 11M" }, image: "North America Sales List-FILE/AVM/Image/AVM-AV-Extension-Cable.png" },
  "1260011100154": { title: { zh: "音视频延长线 15M", en: "Audio-Video Extension Cable 15M" }, image: "North America Sales List-FILE/AVM/Image/AVM-AV-Extension-Cable.png" },
  "1260011100155": { title: { zh: "音视频延长线 23M", en: "Audio-Video Extension Cable 23M" }, image: "North America Sales List-FILE/AVM/Image/AVM-AV-Extension-Cable.png" },
  "5190074100007": { image: "North America Sales List-FILE/AVM/Image/AVM-Calibration-Cloth.png" },
  "1210010100059": { title: { zh: "AHD 信号转接线", en: "AHD Signal Adapter Cable" }, image: "North America Sales List-FILE/AVM/Image/AVM-AHD-Signal-Adapter.png" },
  "1262010000025": { title: { zh: "B2 转接线（接 1 个）", en: "B2 Adapter Cable (1 alarm)" }, image: "North America Sales List-FILE/AVM/Image/AVM-B2-Adapter-1.png" },
  "1262010100031": { title: { zh: "B2 转接线（接 2 个）", en: "B2 Adapter Cable (2 alarms)" }, image: "North America Sales List-FILE/AVM/Image/AVM-B2-Adapter-2.png" },
};

function skuInfo(partNumber) {
  return SKU_LIBRARY[partNumber] || null;
}

