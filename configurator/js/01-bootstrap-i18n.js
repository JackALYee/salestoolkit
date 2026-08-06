const catalog = window.CATALOG || { productLines: [] };
let product = catalog.productLines.find((item) => item.id === "adplus20");

const LANGS = ["zh", "en"];
const KEPT_SCENARIO_POSITIONS = new Set([1, 3, 9, 10, 11, 12]);
const CUSTOM_SCENARIO_ID = "scenario-custom";
const CUSTOM_FAMILY_ID = "custom";
// The only user-facing release version. Update it together with docs/release-notes.md.
const APP_VERSION = "B1.0.3";
const APP_RELEASE_NOTES = [
  {
    version: "B1.0.3",
    date: "2026-07-15",
    notes: ["Page updates."],
  },
  {
    version: "B1.0.2",
    date: "2026-07-15",
    notes: ["Page updates."],
  },
  {
    version: "B1.0.1",
    date: "2026-07-14",
    notes: [
      "First controlled beta release for the North America Sales Configurator.",
      "Selection flows are available for AD Plus 2.0, M1N 2.0, M3N, C6 Lite 2.0, AVM, Z5, and C53.",
      "Selected material lists export in the Opportunity Product Import Excel format.",
      "C53 cascade builds continue in the selected MDVR wizard, where the screen is configured.",
      "Beta feedback and exported-solution telemetry are collected when the companion server is deployed.",
    ],
  },
];

const UI = {
  zh: null,
  en: {
    docTitle: "Streamax Sales Configurator",
    heroEyebrow: "Streamax Sales Configurator",
    heroTitle: "Configure complete vehicle video solutions",
    heroIntro: "Choose a product line, configure the required components, and export a ready-to-quote material list.",
    heroHighlights: [
      "Explore available product solutions",
      "Automatically match required components and cables",
      "Export a ready-to-quote material list",
    ],
    homeCompareTitle: "Exploded Solution Preview",
    homeCompareIntro: "Below are two sample approaches based on the first home-page solution: a fully rebuilt modular version on the left and an original-image overlay version on the right.",
    homeCompareRebuild: "Option A: rebuilt modular version",
    homeCompareOverlay: "Option B: original image overlay",
    homeCompareRebuildNote: "Each module is independent, so it can be added, replaced, or reconnected later.",
    homeCompareOverlayNote: "Keeps the original visual style and highlights key modules with overlays.",
    heroNoteLabel: "What This Does",
    heroNoteTitle: "A customer-facing Streamax configurator",
    heroNoteBody: "This is not an internal material spreadsheet. It turns a complex sellable list into a guided selection flow.",
    prev: "Previous",
    next: "Next",
    stay: "Stay on summary",
    exportExcel: "Export Excel",
    summaryStep: "Summary",
    summaryTitle: "Current Build List",
    stepLabel: "STEP",
    emptyPreview: "No preview available",
    noPartNumber: "No part number",
    noneSelected: "Not selected",
    notNeeded: "No extension cable",
    installImpact: "The system matches one extension cable by default. Removing it may affect installation.",
    lockedCable: "This item requires the cable and it has been locked automatically.",
    chooseLength: "Choose based on installation distance",
    locked: "Locked automatically",
    lengthAndPart: "Cable length / part number",
    cameraRuleTitle: "Camera quantity rule",
    summaryNoteVideo: "Note: when an external camera or screen is selected, one video output cable is mandatory and will be added automatically.",
    rightBlank: "The complete list will build itself on the right as selections are made.",
    noItems: "No items selected yet.",
    reviewTitle: "Build Summary",
    reviewHint: "The list on the right is ready to export. It can also be extended later for quotation or ordering templates.",
    confirmRemoveCable: "Are you sure you want to remove the extension cable? This may affect installation.",
    summaryFields: {
      product: "Product",
      scenario: "Entry",
      solution: "Solution",
      package: "Core kit",
      host: "Host",
      powerBox: "Power box",
      wiring: "Wiring",
      wiringNote: "Wiring note",
      videoCombo: "Video combo",
      optionals: "Optional items",
      itemCount: "Selected items",
    },
    presetSteps: [
      { id: 1, title: "Choose Entry", description: "Start from an existing solution or build from scratch." },
      { id: 2, title: "Choose Core Kit", description: "Pick one core kit from the current solution as the main SKU." },
      { id: 3, title: "Add Cables & Extras", description: "Add accessories based on installation, vehicle type, and function." },
      { id: 4, title: "Review & Export", description: "Check the final combination and export the selected SKU list." },
    ],
    m1nSteps: [
      { id: 1, title: "Confirm Base Kit", description: "Start with the fixed M1N 2.0 base kit before selecting additional items." },
      { id: 2, title: "Choose Wiring", description: "Select the required signal cables, adapter cables, and base access wiring first." },
      { id: 3, title: "Choose Cameras", description: "Select the cameras for DMS, ADAS, BSD, or rear-view scenarios, together with their matching extension cables." },
      { id: 4, title: "Choose Accessories", description: "Add screen, speaker, storage, alarm, and other accessories." },
      { id: 5, title: "Review & Export", description: "Check the full M1N 2.0 list and export the selected SKU list." },
    ],
    customSteps: [
      { id: 1, title: "Choose Entry", description: "Start from an existing solution or build from scratch." },
      { id: 2, title: "Choose Host", description: "Decide whether the customer needs a single-lens or dual-lens host." },
      { id: 3, title: "Choose Power Box", description: "Select Standard Power Box, Power Box Plus, or Power Box Max." },
      { id: 4, title: "Choose Wiring", description: "Choose loose wire, 9PIN, or 16PIN based on vehicle and installation." },
      { id: 5, title: "Choose Video Combo", description: "Select the required cameras and screen. Matching cables are added automatically." },
      { id: 6, title: "Choose Optional Items", description: "Add R-Watch, B2, B3, and other optional items based on the power box." },
      { id: 7, title: "Review & Export", description: "Check the final combination and export the selected SKU list." },
    ],
    customScenario: {
      familyLabel: "Custom",
      title: "Not sure, build from scratch",
      note: "Skip preset system combinations and build step by step from host, power box, and wiring.",
    },
    familyPrefix: "Plan",
    resourceLabels: { spec: "Spec", manual: "Manual" },
    hosts: {
      dual: {
        short: "Dual-lens",
        title: "Dual-lens host",
        detail: "Best for projects that need dual-path base video capability.",
      },
      single: {
        short: "Single-lens",
        title: "Single-lens host",
        detail: "Best for projects that only need a single-path host and may add accessories later.",
      },
    },
    powerBoxes: {
      standard: {
        title: "Standard Power Box",
        badge: "Standard Power Box",
        detail: "Base solution for standard deployments.",
        note: "Start here when the customer only needs a basic project.",
      },
      plus: {
        title: "Power Box Plus",
        badge: "Power Box Plus",
        detail: "With ECU parsing cability, suitable for mid-level projects.",
        note: "Includes 16PIN by default and can also add 9PIN or loose wire.",
      },
      max: {
        title: "Power Box Max",
        badge: "Power Box Max",
        detail: "Extra 4 channels expansion. Highest expandability for more complex alarm and linkage setups.",
        note: "Prefer this tier when future expansion is likely.",
      },
    },
    wiringModes: {
      loose: {
        title: "Loose wire",
        detail: "Best for testing or special retrofit scenarios. Different power boxes use different loose-wire SKUs.",
      },
      "9pin": {
        title: "9PIN J1939",
        detail: "Switch to 9PIN power access based on the vehicle model.",
      },
      "16pin": {
        title: "16PIN OBD",
        detail: "Standard OBD method. PBP / PBM builds include the 16PIN power extension cable by default.",
      },
    },
    accessoryDetails: {
      screen: "Image display for driver assist",
      c29n: "Driver monitoring IPC camera for DMS-related scenarios.",
      ca46_adplus: "BSD camera for PBM scenarios.",
      ca38: "Basic reverse camera for rear-view and reverse use.",
      ca42: "For trailers",
      ca46_m1n: "Interior Monitoring",
      square_camera_m1n: "Square camera for outdoor waterproof reverse or rear-view scenarios.",
    },
    optionalDetails: {
      rwatch: "Useful for driver behavior reminder and linkage reminder projects. Available on Standard, PBP, and PBM.",
      b2: "External BSD sound-and-light alarm. Available on PBM. The matching adapter cable is selected automatically for one or two alarms.",
      b3: "Internal sound-and-light alarm. Available on PBM and requires a B3 extension cable length choice.",
      microSd: "Optional storage card. AD Plus 2.0 supports up to 2 cards.",
    },
    labels: {
      screenCable: "Screen corrugated cable",
      ipcCable: "IPC extension cable",
      ahdCable: "AHD extension cable",
      rearBsdCable: "Rear BSD extension cable",
      b3Cable: "B3 extension cable",
      currentMain: "Current main combo",
      currentWiring: "Wiring",
      currentVideoCombo: "Current video combo",
      optionalsTitle: "Optional items",
      videoComboTitle: "Video combo",
      specsManual: "Product resources",
      builtIn: "This cable path is already included by default",
      needsExtra: "An extra cable SKU is required",
      unsupported: "This method is not supported with the current power box",
      choosePowerBoxFirst: "Choose a power box first",
      b3Hint: "B3 requires one extension cable. Choose the length based on installation distance.",
      power16ExtTitle: "16PIN power extension cable",
      power16ExtDetail: "Makes power access easier during installation.",
      quantity: "Qty",
      card1: "Card 1",
      card2: "Card 2",
      capacity: "Capacity",
    },
  },
};

UI.zh = UI.en;
