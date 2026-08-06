const customCatalog = {
  hosts: [
    {
      id: "dual",
      short: { zh: "Dual-lens", en: "Dual-lens" },
      title: { zh: "Dual-lens host", en: "Dual-lens host" },
      detail: {
        zh: "Best for projects that need dual-path base video capability.", en: "Best for projects that need dual-path base video capability.",
      },
      image: "North America Sales List-FILE/AD Plus 2_0/Image/image.png",
      packageRows: { standard: 14, plus: 19, max: 17 },
    },
    {
      id: "single",
      short: { zh: "Single-lens", en: "Single-lens" },
      title: { zh: "Single-lens host", en: "Single-lens host" },
      detail: {
        zh: "Best for projects that only need a single-path host and may add accessories later.", en: "Best for projects that only need a single-path host and may add accessories later.",
      },
      image: "North America Sales List-FILE/AD Plus 2_0/Image/14-AD Plus 2.0-S Kit 套装-image.png",
      packageRows: { standard: 15, plus: 20, max: 18 },
    },
  ],
  powerBoxes: [
    {
      id: "standard",
      title: { zh: "Standard Power Box", en: "Standard Power Box" },
      badge: { zh: "Standard Power Box", en: "Standard Power Box" },
      detail: {
        zh: "Base solution for standard deployments.", en: "Base solution for standard deployments.",
      },
      note: {
        zh: "Start here when the customer only needs a basic project.", en: "Start here when the customer only needs a basic project.",
      },
    },
    {
      id: "plus",
      title: { zh: "Power Box Plus", en: "Power Box Plus" },
      badge: { zh: "Power Box Plus", en: "Power Box Plus" },
      detail: {
        zh: "With ECU parsing cability, suitable for mid-level projects.", en: "With ECU parsing cability, suitable for mid-level projects.",
      },
      note: {
        zh: "默认选择 16PIN 接线及其延长线，也可改选 9PIN 或散线。", en: "Defaults to 16PIN wiring and its extension cable; 9PIN or loose wire can also be selected.",
      },
    },
    {
      id: "max",
      title: { zh: "Power Box Max", en: "Power Box Max" },
      badge: { zh: "Power Box Max", en: "Power Box Max" },
      detail: {
        zh: "Extra 4 channels expansion. Highest expandability for more complex alarm and linkage setups.", en: "Extra 4 channels expansion. Highest expandability for more complex alarm and linkage setups.",
      },
      note: {
        zh: "Prefer this tier when future expansion is likely.", en: "Prefer this tier when future expansion is likely.",
      },
    },
  ],
  wiringModes: [
    {
      id: "loose",
      title: { zh: "散线方式", en: "Loose wire" },
      detail: {
        zh: "Best for testing or retrofit scenarios. Different power boxes use different loose-wire SKUs.", en: "Best for testing or retrofit scenarios. Different power boxes use different loose-wire SKUs.",
      },
      support: { standard: "builtin", plus: "item", max: "item" },
      rows: { plus: 26, max: 27 },
    },
    {
      id: "9pin",
      title: { zh: "9PIN J1939", en: "9PIN J1939" },
      detail: {
        zh: "Switch to 9PIN power access based on the vehicle model.", en: "Switch to 9PIN power access based on the vehicle model.",
      },
      support: { standard: "item", plus: "item", max: "item" },
      rows: { standard: 22, plus: 24, max: 24 },
    },
    {
      id: "16pin",
      title: { zh: "16PIN OBD", en: "16PIN OBD" },
      detail: {
        zh: "标准 OBD 接法。PBP / PBM 向导默认选择 16PIN 电源延长线（套装料号不含该线）。", en: "Standard OBD method. PBP / PBM builds default-select the 16PIN power extension cable; it is not included in the kit SKU.",
      },
      support: { standard: "item", plus: "item", max: "item" },
      rows: { standard: 23, plus: 25, max: 25 },
    },
  ],
  accessories: [
    {
      id: "ca46_adplus",
      ...skuInfo("5151053100007"),
      itemRow: 16,
      cameraType: "ahd",
      extensionRows: [31, 32, 33],
      extensionLabel: { zh: "AHD extension cable", en: "AHD extension cable" },
      allowedPowerBoxes: ["standard", "plus", "max"],
      maxQuantityByPowerBox: { standard: 1, plus: 1 },
      sortOrder: -10,
    },
    {
      id: "screen",
      ...skuInfo("5190012100075"),
      itemRow: 40,
      extensionRows: [41],
      extensionLabel: { zh: "Screen corrugated cable", en: "Screen corrugated cable" },
      lockExtension: true,
      secondaryExtensionRows: [31, 32, 33],
      secondaryExtensionLabel: { zh: "AHD 延长线", en: "AHD extension cable" },
    },
    {
      id: "c29n",
      ...skuInfo("5152119100007"),
      itemRow: 34,
      cameraType: "ipc",
      extensionRows: [28, 29, 30],
      extensionLabel: { zh: "IPC extension cable", en: "IPC extension cable" },
    },
    {
      id: "ca38",
      ...skuInfo("5051043100003"),
      itemRow: 35,
      cameraType: "ahd",
      extensionRows: [31, 32, 33],
      extensionLabel: { zh: "AHD extension cable", en: "AHD extension cable" },
    },
    {
      id: "ca42",
      ...skuInfo("5200027100004"),
      itemRow: 36,
      cameraType: "ahd",
      extensionRows: [37, 38, 39],
      extensionLabel: { zh: "Rear BSD extension cable", en: "Rear BSD extension cable" },
    },
    {
      id: "ca46_m1n",
      ...skuInfo("5151022100069"),
      sourceProductId: "m3n",
      itemRow: 23,
      cameraType: "ahd",
      extensionRows: [31, 32, 33],
      extensionLabel: { zh: "AHD 延长线", en: "AHD extension cable" },
      sortOrder: 10,
    },
    {
      id: "square_camera_m1n",
      ...skuInfo("5151003100126"),
      sourceProductId: "m1n20",
      itemRow: 22,
      cameraType: "ahd",
      extensionRows: [31, 32, 33],
      extensionLabel: { zh: "AHD extension cable", en: "AHD extension cable" },
    },
  ],
  optionals: [
    {
      id: "rwatch",
      title: { zh: "R-Watch", en: "R-Watch" },
      itemRow: 42,
      detail: UI.zh.optionalDetails.rwatch,
      detailEn: UI.en.optionalDetails.rwatch,
      allowedPowerBoxes: ["standard", "plus", "max"],
    },
    {
      // Keep the M3N-style independent B2 choices: each selected alarm owns one IPC extension cable.
      id: "b2_right",
      ...skuInfo("5090091100025"),
      itemRow: 43,
      b2Group: true,
      allowedPowerBoxes: ["max"],
      extensionRows: [28, 29, 30],
      extensionLabel: { zh: "6PIN IPC 延长线", en: "6PIN IPC extension cable" },
      requiredExtension: true,
    },
    {
      id: "b2_left",
      ...skuInfo("5090091100026"),
      sourceProductId: "m3n",
      itemRow: 19,
      b2Group: true,
      allowedPowerBoxes: ["max"],
      extensionRows: [28, 29, 30],
      extensionLabel: { zh: "6PIN IPC 延长线", en: "6PIN IPC extension cable" },
      requiredExtension: true,
    },
    {
      id: "b3",
      ...skuInfo("5190108100003"),
      itemRow: 47,
      allowedPowerBoxes: ["max"],
      extensionRows: [48, 49, 50],
      extensionLabel: { zh: "B3 extension cable", en: "B3 extension cable" },
      requiredExtension: true,
      maxQuantity: 2,
    },
    {
      id: "micro_sd",
      title: { zh: "Micro SD card", en: "Micro SD card" },
      image: "North America Sales List-FILE/AD Plus 2_0/Image/sd card.png",
      detail: { zh: "", en: UI.en.optionalDetails.microSd },
      detailEn: UI.en.optionalDetails.microSd,
      allowedPowerBoxes: ["standard", "plus", "max"],
      maxQuantity: 2,
    },
  ],
  helperRows: {
    videoOutputCable: 21,
    b2AdapterRowsByQuantity: { 1: 45, 2: 46 },
  },
};

const SD_CARD_VARIANTS = [
  { partNumber: "1610002100008", name: { zh: "Micro SD 128GB", en: "Micro SD 128GB" } },
  { partNumber: "1610002100007", name: { zh: "Micro SD 256GB", en: "Micro SD 256GB" } },
  { partNumber: "1610002100006", name: { zh: "Micro SD 512GB", en: "Micro SD 512GB" } },
  { partNumber: "1610002100005", name: { zh: "Micro SD 1TB", en: "Micro SD 1TB" } },
];


const M2_SSD_VARIANTS = [
  { partNumber: "1610004100014", name: { zh: "M.2 SSD 512GB", en: "M.2 SSD 512GB" } },
  { partNumber: "1610004100013", name: { zh: "M.2 SSD 1TB", en: "M.2 SSD 1TB" } },
  { partNumber: "1610004100012", name: { zh: "M.2 SSD 2TB", en: "M.2 SSD 2TB" } },
];
