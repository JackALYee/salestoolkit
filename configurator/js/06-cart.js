function selectedPresetItems() {
  if (isAvmProduct()) return selectedAvmItems();
  if (is960C53Product()) return selectedC53Items();
  const rows = itemsForFamily()
    .filter((item) => {
      // C6: AHD extension cables are chosen per-camera (nested); the AHD expansion cable (r15) is auto-added.
      // Device-extension and PBP cables are intentionally outside the guided C6 flow.
      if (isC6Product() && [9, 14, 15, 16, 17, 18, 19, 24].includes(item.rowNumber)) return false;
      // AVM: connection + B2 adapter cables are auto-added, not manually selected.
      if (isAvmProduct() && [7, 8, 19, 20].includes(item.rowNumber)) return false;
      return isMSeriesProduct() ? m3nPresetItemSelected(item) : state.selections[item.id]?.checked;
    })
    .map((item) => {
      const variantOptions = presetVariantOptions(item);
      const selectedVariantPart = state.selections[item.id]?.variantPartNumber;
      const selectedVariant = variantOptions?.find((entry) => entry.partNumber === selectedVariantPart) || variantOptions?.[0] || null;
      const avmQuantity =
        isAvmProduct() && item.rowNumber === 13
          ? "4"
          : state.selections[item.id]?.quantity || item.quantity || "1";
      return {
        product: product.title,
        scenario: localizedText(currentScenario()?.title || ""),
        family: state.familyId || "",
        group: displayCatalogText(item.group),
        name: variantOptions
          ? localizedText(selectedVariant.name)
          : (isZ5Product() && Z5_STEP_ROWS.storage.has(item.rowNumber))
            ? `Micro SD ${displayCatalogText(item.note || item.name)}`
          : (skuInfo(item.partNumber)?.title ? localizedText(skuInfo(item.partNumber).title) : displayCatalogText(item.name)),
        partNumber: variantOptions ? selectedVariant.partNumber : item.partNumber,
        quantity:
          isMSeriesProduct() && isM3nPresetCameraItem(item)
            ? String(Number(state.selections[item.id]?.quantity || 0))
            : avmQuantity,
        note: displayCatalogText(item.note),
        description: displayCatalogText(item.description),
      };
    });

  if (isC6Product()) {
    const c6Line = (it, qty = "1") => ({
      product: product.title,
      scenario: localizedText(currentScenario()?.title || ""),
      family: state.familyId || "",
      group: displayCatalogText(it.group),
      name: skuInfo(it.partNumber)?.title ? localizedText(skuInfo(it.partNumber).title) : displayCatalogText(it.name),
      partNumber: it.partNumber,
      quantity: qty,
      note: displayCatalogText(it.note),
      description: displayCatalogText(it.description),
    });
    const selectedCams = c6Items([20, 21, 22]).filter((cam) => state.selections[cam.id]?.checked);
    // Append each selected camera's chosen AHD extension cable.
    selectedCams.forEach((cam) => {
      const extRow = state.selections[cam.id]?.c6ExtRow;
      const ext = extRow ? findItemByRow(Number(extRow)) : null;
      if (ext) rows.push(c6Line(ext));
    });
    // Auto-add one AHD expansion cable (r15) whenever any camera is selected.
    if (selectedCams.length) {
      const exp = c6Items([15])[0];
      if (exp) rows.push(c6Line(exp));
    }
    const storage = c6Items([24])[0];
    const storageState = state.selections[storage?.id] || {};
    const storageQuantity = storageState.checked ? Math.max(1, Math.min(2, Number(storageState.quantity || 1))) : 0;
    const storageParts = Array.isArray(storageState.variantPartNumbers)
      ? storageState.variantPartNumbers
      : [storageState.variantPartNumber || SD_CARD_VARIANTS[0].partNumber];
    for (let index = 0; index < storageQuantity; index += 1) {
      const variant = SD_CARD_VARIANTS.find((item) => item.partNumber === storageParts[index]) || SD_CARD_VARIANTS[0];
      rows.push({
        product: product.title,
        scenario: localizedText(currentScenario()?.title || ""),
        family: state.familyId || "",
        group: "Storage",
        name: localizedText(variant.name),
        partNumber: variant.partNumber,
        quantity: "1",
        note: displayCatalogText(storage?.note || ""),
        description: displayCatalogText(storage?.description || ""),
      });
    }
  }

  if (isAvmProduct()) {
    // Auto-add the connection-mode adapter cable (standalone -> r7, cascade -> r8).
    const mode = avmCurrentMode();
    if (mode) {
      const adapter = findItemByRow(mode.adapterRow);
      if (adapter) {
        rows.push({
          product: product.title,
          scenario: localizedText(currentScenario()?.title || ""),
          family: state.familyId || "",
          group: displayCatalogText(adapter.group),
          name: skuInfo(adapter.partNumber)?.title ? localizedText(skuInfo(adapter.partNumber).title) : displayCatalogText(adapter.name),
          partNumber: adapter.partNumber,
          quantity: "1",
          note: displayCatalogText(adapter.note),
          description: displayCatalogText(adapter.description),
        });
      }
    }
    const b2Selections = itemsForFamily().filter(
      (item) => state.selections[item.id]?.checked && item.rowNumber !== undefined && [17, 18].includes(item.rowNumber)
    );
    if (b2Selections.length === 1) {
      const singleB2Adapter = findItemByRow(19);
      if (singleB2Adapter) {
        rows.push({
          product: product.title,
          scenario: localizedText(currentScenario()?.title || ""),
          family: state.familyId || "",
          group: displayCatalogText(singleB2Adapter.group),
          name: displayCatalogText(singleB2Adapter.name),
          partNumber: singleB2Adapter.partNumber,
          quantity: "1",
          note: displayCatalogText(singleB2Adapter.note),
          description: displayCatalogText(singleB2Adapter.description),
        });
      }
    }
    if (b2Selections.length >= 2) {
      const dualB2Adapter = findItemByRow(20);
      if (dualB2Adapter) {
        rows.push({
          product: product.title,
          scenario: localizedText(currentScenario()?.title || ""),
          family: state.familyId || "",
          group: displayCatalogText(dualB2Adapter.group),
          name: displayCatalogText(dualB2Adapter.name),
          partNumber: dualB2Adapter.partNumber,
          quantity: "1",
          note: displayCatalogText(dualB2Adapter.note),
          description: displayCatalogText(dualB2Adapter.description),
        });
      }
    }
    return rows;
  }

  if (!isMSeriesProduct()) return rows;

  const b2Selections = itemsForFamily().filter(
    (item) => m3nPresetItemSelected(item) && item.rowNumber !== undefined && [18, 19].includes(item.rowNumber)
  );

  if (b2Selections.length === 1) {
    const singleB2Adapter = findItemByRow(20);
    if (singleB2Adapter) {
      rows.push({
        product: product.title,
        scenario: localizedText(currentScenario()?.title || ""),
        family: state.familyId || "",
        group: displayCatalogText(singleB2Adapter.group),
        name: displayCatalogText(singleB2Adapter.name),
        partNumber: singleB2Adapter.partNumber,
        quantity: "1",
        note: displayCatalogText(singleB2Adapter.note),
        description: displayCatalogText(singleB2Adapter.description),
      });
    }
  }

  if (b2Selections.length >= 2) {
    const dualB2Adapter = findItemByRow(21);
    if (dualB2Adapter) {
      rows.push({
        product: product.title,
        scenario: localizedText(currentScenario()?.title || ""),
        family: state.familyId || "",
        group: displayCatalogText(dualB2Adapter.group),
        name: displayCatalogText(dualB2Adapter.name),
        partNumber: dualB2Adapter.partNumber,
        quantity: "1",
        note: displayCatalogText(dualB2Adapter.note),
        description: displayCatalogText(dualB2Adapter.description),
      });
    }
  }

  const extensionRows = [];
  for (const item of itemsForFamily().filter((entry) =>
    m3nPresetItemSelected(entry) && (isM3nPresetCameraItem(entry) || m3nOptionalExtensionRows(entry).length)
  )) {
    const block = state.selections[item.id] || {};
    const extensionIds =
      isM3nPresetCameraItem(item) && Array.isArray(block.extensions) && block.extensions.length
        ? block.extensions
        : block.extensionId
          ? [block.extensionId]
          : [];
    for (const extensionId of extensionIds) {
      if (!extensionId) continue;
      const extensionItem = product.items.find((entry) => entry.id === extensionId);
      if (!extensionItem) continue;
      extensionRows.push({
        product: product.title,
        scenario: localizedText(currentScenario()?.title || ""),
        family: state.familyId || "",
        group: displayCatalogText(extensionItem.group),
        name: displayCatalogText(extensionItem.name),
        partNumber: extensionItem.partNumber,
        quantity: "1",
        note: displayCatalogText(extensionItem.note),
        description: displayCatalogText(extensionItem.description),
      });
    }
  }

  return [...rows, ...extensionRows];
}

function selectedCustomItems() {
  const rows = [];
  const pkg = customPackageItem();
  if (pkg) rows.push(pkg);

  const powerBox = selectedCustomPowerBox();
  const hasReachedWiringStep = state.step >= 4;
  if (powerBox && hasReachedWiringStep) {
    for (const wiring of selectedCustomWirings()) {
      const supportType = wiring.support[powerBox.id];
      if (supportType === "item") {
        if (wiring.id === "16pin" && (powerBox.id === "plus" || powerBox.id === "max")) continue;
        const mapped = findItemByRow(wiring.rows[powerBox.id]);
        if (mapped) rows.push(mapped);
      }
    }
    if ((powerBox.id === "plus" || powerBox.id === "max") && state.custom.wiringExtras.power16Extension) {
      const extensionItem = findItemByRow(25);
      if (extensionItem) rows.push(extensionItem);
    }
  }

  const selectedAccessoryDefs = selectedCustomAccessoryDefs();
  const shouldAddVideoOutputCable = selectedAccessoryDefs.some((def) => {
    if (powerBox?.id === "max") return false;
    if (def.cameraType || def.id === "screen") return true;
    return false;
  });
  if (shouldAddVideoOutputCable) {
    const helper = findItemByRow(customCatalog.helperRows.videoOutputCable);
    if (helper) rows.push(helper);
  }

  for (const def of selectedAccessoryDefs) {
    const item = def.sourceProductId ? findCatalogItem(def.sourceProductId, def.itemRow) : findItemByRow(def.itemRow);
    const accessoryState = ensureAccessoryState(def.id);
    const quantity = Number(accessoryState.quantity || 0);
    if (def.cameraType && quantity <= 0) continue;
    if (item) rows.push({ ...item, quantity: String(quantity) });
    if (def.cameraType) {
      for (const extensionId of accessoryState.extensions || []) {
        if (!extensionId) continue;
        const extensionItem = product.items.find((entry) => entry.id === extensionId);
        if (extensionItem) rows.push({ ...extensionItem, quantity: "1" });
      }
    } else {
      const extensionId = accessoryState.extension;
      if (extensionId) {
        const extensionItem = product.items.find((entry) => entry.id === extensionId);
        if (extensionItem) rows.push({ ...extensionItem, quantity: String(quantity || 1) });
      }
      const extraExtensionId = accessoryState.extraExtension;
      if (extraExtensionId) {
        const extraExtensionItem = product.items.find((entry) => entry.id === extraExtensionId);
        if (extraExtensionItem) rows.push({ ...extraExtensionItem, quantity: String(quantity || 1) });
      }
    }
    if (def.id === "ca42" && accessoryState.addonChecked) {
      rows.push({
        id: "ca42_serial_adapter",
        rowNumber: 0,
        name: "Serial port adapter cable",
        group: "Reversing Monitoring, Rear BSD",
        note: "Optional. Used to enable trailer matching and available for all power-box builds. R-Watch is unavailable only when this is enabled on Standard Power Box.",
        description: "232 Signal Adapter Cable - C43 | One end small 5557-4P, other end SM-3Y female head + flying lead | 150mm | No label | C43 | 3036ML",
        partNumber: "1261050100291",
        quantity: "1",
      });
    }
  }

  for (const def of selectedCustomOptionalDefs()) {
    if (def.id === "micro_sd") {
      const stateBlock = ensureOptionalState(def.id);
      const qty = Math.min(2, Math.max(1, Number(stateBlock.quantity || 1)));
      const selectedParts = [stateBlock.variant1, stateBlock.variant2].slice(0, qty);
      for (const partNumber of selectedParts) {
        const variant = SD_CARD_VARIANTS.find((item) => item.partNumber === partNumber) || SD_CARD_VARIANTS[0];
        rows.push({
          id: `micro_sd_${variant.partNumber}`,
          group: "Storage",
          name: localizedText(variant.name),
          partNumber: variant.partNumber,
          quantity: "1",
          note: def.detailEn,
          description: def.detailEn,
        });
      }
      continue;
    }
    const stateBlock = ensureOptionalState(def.id);
    const quantity = Math.max(1, Number(stateBlock.quantity || 1));
    const item = def.sourceProductId ? findCatalogItem(def.sourceProductId, def.itemRow) : findItemByRow(def.itemRow);
    if (item) rows.push({ ...item, quantity: String(quantity) });
    const requiredRows = def.requiredRowsByQuantity?.[quantity] || def.requiredRows || [];
    for (const requiredRow of requiredRows) {
      const requiredItem = findItemByRow(requiredRow);
      if (requiredItem) rows.push({ ...requiredItem, quantity: def.requiredRowsByQuantity ? "1" : String(quantity) });
    }
    if (def.maxQuantity && def.extensionRows?.length) {
      for (const extensionId of stateBlock.extensions || []) {
        if (!extensionId) continue;
        const extensionItem = product.items.find((entry) => entry.id === extensionId);
        if (extensionItem) rows.push({ ...extensionItem, quantity: "1" });
      }
    } else {
      const extensionId = stateBlock.extension;
      if (extensionId) {
        const extensionItem = product.items.find((entry) => entry.id === extensionId);
        if (extensionItem) rows.push(extensionItem);
      }
    }
  }

  const selectedB2Defs = selectedCustomOptionalDefs().filter((def) => def.b2Group);
  const b2AdapterRow = customCatalog.helperRows.b2AdapterRowsByQuantity?.[selectedB2Defs.length];
  if (b2AdapterRow) {
    const b2Adapter = findItemByRow(b2AdapterRow);
    if (b2Adapter) rows.push({ ...b2Adapter, quantity: "1" });
  }

  const mergedRows = Array.from(
    rows.reduce((acc, item) => {
      const existing = acc.get(item.id);
      const qty = Number(item.quantity || "1");
      if (existing) {
        existing.quantity = String(Number(existing.quantity || "1") + qty);
      } else {
        acc.set(item.id, { ...item, quantity: String(qty) });
      }
      return acc;
    }, new Map()).values()
  );
  return mergedRows.map((item) => ({
    product: product.title,
    scenario: localizedText(currentScenario()?.title || ""),
    family: state.familyId || "",
    group: displayCatalogText(item.group),
    name: displayCatalogText(item.name),
    partNumber: item.partNumber,
    quantity: item.quantity || "1",
    note: displayCatalogText(item.note),
    description: displayCatalogText(item.description),
  }));
}

function selectedItems() {
  const rows = isCustomFlow() ? selectedCustomItems() : selectedPresetItems();
  if (avmCascadeActive() && state.avmCascade.items?.length) return [...state.avmCascade.items, ...rows];
  if (c53CascadeActive() && state.c53Cascade.items?.length) return [...state.c53Cascade.items, ...rows];
  return rows;
}

function updateStepControls() {
  const steps = currentSteps();
  const enteringC53HostWizard = is960C53Product() && state.c53?.mode === "cascade" && state.step === 4;
  prevStepBtn.disabled = state.productPickerOpen;
  nextStepBtn.textContent = enteringC53HostWizard
    ? L("进入 MDVR 向导", "Enter MDVR Wizard")
    : state.step === steps.length
      ? t().stay
      : t().next;
  nextStepBtn.disabled = state.productPickerOpen
    ? !Boolean(state.productId)
    : (state.step === steps.length && !enteringC53HostWizard) || !validateCurrentStep();
}

function validateCurrentStep() {
  if (state.productPickerOpen) return Boolean(state.productId);
  if (!isCustomFlow()) {
    if (is960C53Product() && state.c53?.mode === "cascade" && state.step === 4) {
      return Boolean(state.c53.cascadeHost);
    }
    if (state.step === 1) {
      if (isAvmProduct()) return Boolean(state.packageId) && Boolean(state.avm?.mode);
      return isC6Product() ? Boolean(state.packageId) : Boolean(state.scenarioId);
    }
    if (state.step === 2) {
      // A matching default is selected on kit selection: loose cable for RS232,
      // 16PIN OBD for CAN. The user can switch it to another matching connector.
      if (isC6Product()) {
        const requiredRow = c6CurrentPowerModel() === "can" ? 12 : 27;
        const requiredPower = c6Items([requiredRow])[0];
        return Boolean(requiredPower && state.selections[requiredPower.id]?.checked);
      }
      return Boolean(state.packageId);
    }
    return true;
  }
  if (state.step === 1) return Boolean(state.scenarioId);
  if (state.step === 2) return Boolean(state.custom.host);
  if (state.step === 3) return Boolean(state.custom.powerBox);
  if (state.step === 4) return selectedCustomWirings().length > 0;
  return true;
}
