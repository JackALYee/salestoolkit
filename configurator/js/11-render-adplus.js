function renderCustomHostStep() {
  wizardStageEl.innerHTML = `
    <div class="option-grid two-col">
      ${customCatalog.hosts
        .map((host) => {
          const active = state.custom.host === host.id ? "active" : "";
          return `
            <button class="option-card ${active}" data-host="${host.id}">
              ${
                host.image
                  ? `<img loading="lazy" decoding="async" class="host-photo" src="./${host.image}" alt="${localizedText(host.title)}" />`
                  : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`
              }
              <div class="tag">${localizedText(host.short)}</div>
              <h3>${localizedText(host.title)}</h3>
              <p>${localizedText(host.detail)}</p>
            </button>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-host]").forEach((node) => {
    node.addEventListener("click", () => setCustomHost(node.dataset.host));
  });
}

function renderCustomPowerBoxStep() {
  const host = selectedCustomHost();
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.host}</strong>
        <p>${host ? localizedText(host.title) : t().noneSelected}</p>
      </div>
    </div>
    <div class="option-grid three-col">
      ${customCatalog.powerBoxes
        .map((powerBox) => {
          const active = state.custom.powerBox === powerBox.id ? "active" : "";
          const preview = customPowerBoxPreview(powerBox.id);
          return `
            <button class="option-card power-box-card ${active}" data-power-box="${powerBox.id}">
              ${
                preview
                  ? `<img loading="lazy" decoding="async" class="host-photo" src="./${preview}" alt="${localizedText(powerBox.title)}" />`
                  : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`
              }
              <div class="tag">${localizedText(powerBox.badge)}</div>
              <h3>${localizedText(powerBox.title)}</h3>
              <p>${localizedText(powerBox.detail)}</p>
            </button>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-power-box]").forEach((node) => {
    node.addEventListener("click", () => setCustomPowerBox(node.dataset.powerBox));
  });
}

function renderCustomWiringStep() {
  const powerBox = selectedCustomPowerBox();
  const power16ExtensionItem = findItemByRow(25);
  const showPower16ExtensionCard = powerBox && (powerBox.id === "plus" || powerBox.id === "max");
  const power16ExtensionPreview = pickPreviewAsset(power16ExtensionItem?.images || []);
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.powerBox}</strong>
        <p>${powerBox ? localizedText(powerBox.title) : t().noneSelected}</p>
      </div>
      <div>
        <strong>${t().summaryFields.host}</strong>
        <p>${selectedCustomHost() ? localizedText(selectedCustomHost().title) : t().noneSelected}</p>
      </div>
    </div>
    <div class="option-grid three-col">
      ${customCatalog.wiringModes
        .map((mode) => {
          const supported = isWiringSupported(mode);
          const wiringSku = customWiringSku(mode.id, powerBox?.id);
          const lockedDefault =
            powerBox && ((powerBox.id === "standard" && mode.id === "loose") || ((powerBox.id === "plus" || powerBox.id === "max") && mode.id === "16pin"));
          const preview = customWiringPreview(mode.id, powerBox?.id);
          return `
            <label class="option-card wiring-card ${state.custom.wiring[mode.id] ? "active" : ""} ${supported ? "" : "disabled"} ${lockedDefault ? "locked-option" : ""}">
              ${
                preview
                  ? `<img loading="lazy" decoding="async" class="host-photo" src="./${preview}" alt="${localizedText(mode.title)}" />`
                  : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`
              }
              <input type="checkbox" data-wiring="${mode.id}" ${state.custom.wiring[mode.id] ? "checked" : ""} ${supported && !lockedDefault ? "" : "disabled"} />
              <div class="tag">${localizedText(mode.title)}</div>
              <h3>${localizedText(mode.title)}</h3>
              <div class="sku">${wiringSku || t().noPartNumber}</div>
              <p>${localizedText(mode.detail)}</p>
            </label>
          `;
        })
        .join("")}
      ${
        showPower16ExtensionCard
          ? `
            <label class="option-card wiring-card wiring-extra-card ${state.custom.wiringExtras.power16Extension ? "active" : ""}">
              ${
                power16ExtensionPreview
                  ? `<img loading="lazy" decoding="async" class="host-photo" src="./${power16ExtensionPreview}" alt="${t().labels.power16ExtTitle}" />`
                  : `<div class="host-photo host-photo-empty">${t().emptyPreview}</div>`
              }
              <input type="checkbox" data-wiring-extra="power16Extension" ${state.custom.wiringExtras.power16Extension ? "checked" : ""} />
              <div class="tag">${t().labels.power16ExtTitle}</div>
              <h3>${t().labels.power16ExtTitle}</h3>
              <div class="sku">${power16ExtensionItem?.partNumber || "1260040100236"}</div>
              <p>${t().labels.power16ExtDetail}</p>
            </label>
          `
          : ""
      }
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-wiring]").forEach((node) => {
    node.addEventListener("change", (event) => {
      toggleCustomWiring(node.dataset.wiring, event.target.checked);
    });
  });
  wizardStageEl.querySelectorAll("[data-wiring-extra]").forEach((node) => {
    node.addEventListener("change", (event) => {
      toggleCustomWiringExtra(node.dataset.wiringExtra, event.target.checked);
    });
  });
}

function renderExtensionBlock(def, stateBlock, extensionSetter, allowNone = true, slot = 0, heading = "", options = {}) {
  const extensionRows = options.extensionRows || def.extensionRows || [];
  const title = options.label || localizedText(def.extensionLabel);
  const stateField = options.stateField || (extensionSetter === "accessory" && def.cameraType ? "extensions" : "extension");
  const lockExtension = options.lockExtension ?? def.lockExtension;
  const selectedExtensionId = stateField === "extensions" ? stateBlock.extensions?.[slot] || "" : stateBlock[stateField] || "";
  const sortedExtensionRows = [...extensionRows].sort((leftRow, rightRow) => {
    const leftItem = findItemByRow(leftRow);
    const rightItem = findItemByRow(rightRow);
    return extensionLengthValue(leftItem) - extensionLengthValue(rightItem);
  });
  return `
    <div class="extension-picker">
      <div class="extension-picker-head">
        <strong>${heading || title}</strong>
        <span>${lockExtension ? t().locked : t().chooseLength}</span>
      </div>
      <label>
        <span>${t().lengthAndPart}</span>
        <select data-extension-kind="${extensionSetter}" data-extension-id="${def.id}" data-extension-slot="${slot}" data-extension-field="${stateField}" ${lockExtension ? "disabled" : ""}>
          ${sortedExtensionRows
            .map((rowNumber) => {
              const extensionItem = findItemByRow(rowNumber);
              const selectedOption = selectedExtensionId === extensionItem?.id ? "selected" : "";
              return `<option value="${rowNumber}" ${selectedOption}>${formatExtensionOptionLabel(extensionItem)}</option>`;
            })
            .join("")}
          ${lockExtension || !allowNone ? "" : `<option value="none" ${selectedExtensionId ? "" : "selected"}>${t().notNeeded}</option>`}
        </select>
      </label>
      <p class="hint">${lockExtension ? t().lockedCable : t().installImpact}</p>
    </div>
  `;
}

function renderAccessoryEditor() {
  const accessoryId = state.custom.accessoryEditor;
  if (!accessoryId) return "";
  const def = customCatalog.accessories.find((item) => item.id === accessoryId);
  if (!def || !def.cameraType) return "";
  const stateBlock = ensureAccessoryState(accessoryId);
  const quantity = Number(stateBlock.quantity || 0);
  if (quantity <= 0) return "";
  return `
    <div class="accessory-editor-backdrop" data-close-accessory-editor="true"></div>
    <div class="accessory-editor-panel">
      <div class="accessory-editor-head">
        <div>
          <strong>${localizedText(def.title)}</strong>
          <p>${quantity} ${localizedText(def.extensionLabel)}</p>
        </div>
        <button type="button" class="accessory-editor-close" data-close-accessory-editor="true">脳</button>
      </div>
      <div class="accessory-editor-body">
        ${Array.from({ length: quantity }, (_, index) =>
          renderExtensionBlock(
            def,
            stateBlock,
            "accessory",
            true,
            index,
            `${localizedText(def.extensionLabel)} ${index + 1}`
          )
        ).join("")}
      </div>
    </div>
  `;
}

function renderSelectedCameraConfigs() {
  const selectedCameras = selectedCameraAccessoryDefs();
  if (!selectedCameras.length) return "";
  return `
    <section class="camera-config-panel">
      <div class="camera-config-panel-head">
        <strong>${L("已选摄像头线材配置", "Selected camera cable setup")}</strong>
        <span>${L("下方卡片只选数量，这里统一设置每一路延长线长度", "Use the cards below for quantity only. Set each extension length here.")}</span>
      </div>
      <div class="camera-config-list">
        ${selectedCameras
          .map((def) => {
            const stateBlock = ensureAccessoryState(def.id);
            const quantity = Number(stateBlock.quantity || 0);
            return `
              <article class="camera-config-item">
                <div class="camera-config-item-head">
                  <strong>${localizedText(def.title)}</strong>
                  <span>${quantity} x ${localizedText(def.extensionLabel)}</span>
                </div>
                <div class="camera-config-item-grid">
                  ${Array.from({ length: quantity }, (_, index) =>
                    renderExtensionBlock(
                      def,
                      stateBlock,
                      "accessory",
                      true,
                      index,
                      `${localizedText(def.extensionLabel)} ${index + 1}`
                    )
                  ).join("")}
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function renderCustomAccessoryStep() {
  const capacityRule = cameraCapacityRule();
  const capacityWarning = cameraCapacityWarning();
  const capacityStatus = cameraCapacityStatus();
  const accessories = orderedCustomAccessories();
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().labels.currentMain}</strong>
        <p>${selectedCustomHost() ? localizedText(selectedCustomHost().title) : "-"} + ${selectedCustomPowerBox() ? localizedText(selectedCustomPowerBox().title) : "-"}</p>
      </div>
      <div>
        <strong>${t().labels.currentWiring}</strong>
        <p>${selectedCustomWirings().map((item) => localizedText(item.title)).join(" / ") || "-"}</p>
      </div>
    </div>
    ${hostCascadeActive() ? `<p class="c6-section-hint">${L(`${hostCascadeName()} 级联已预占 ${avmCascadeReserved().ipc} 路 IPC${avmCascadeReserved().ahd ? ` + ${avmCascadeReserved().ahd} 路 AHD` : ""}，已计入摄像头路数额度。`, `${hostCascadeName()} cascade reserves ${avmCascadeReserved().ipc} IPC${avmCascadeReserved().ahd ? ` + ${avmCascadeReserved().ahd} AHD` : ""} on this host, already counted toward the camera limits.`)}</p>` : ""}
    ${
      capacityRule
        ? `<div class="capacity-note ${capacityWarning ? "warning" : ""}">
            <strong>${t().cameraRuleTitle}</strong>
            <p>${capacityWarning || `${capacityRule.label}. ${"Remaining"} ${capacityStatus.ipcRemaining} IPC / ${capacityStatus.ahdRemaining} AHD.`}</p>
          </div>`
        : ""
    }
    <div class="group-list accessory-vertical-list">
      ${accessories
        .map((def) => {
          const item = def.sourceProductId ? findCatalogItem(def.sourceProductId, def.itemRow) : findItemByRow(def.itemRow);
          const blockState = ensureAccessoryState(def.id);
          const maxQty = Math.max(1, maxAccessoryQuantity(def));
          const quantity = Number(blockState.quantity || 0);
          const selected = (def.cameraType ? quantity > 0 : blockState.checked) ? "selected" : "";
          const disabled = isAccessoryChoiceDisabled(def) ? "disabled" : "";
          const preview = def.image || pickPreviewAsset(item?.images || []);
          return `
            <section class="group-card accessory-row-group">
              <label class="item-card accessory-row-card ${selected} ${disabled}">
                <div class="accessory-row-media">
                  ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${localizedText(def.title)}" />` : `<div class="thumb"></div>`}
                </div>
                <div class="accessory-row-copy">
                  <h4>${localizedText(def.title)}</h4>
                  <div class="sku">${item?.partNumber || t().noPartNumber}</div>
                  <p>${accessoryDetailText(def)}</p>
                </div>
                <div class="accessory-row-control">
                  ${
                    def.cameraType
                      ? `
                        <div class="qty-stepper" data-accessory-stepper="${def.id}">
                          <button type="button" class="qty-btn" data-accessory-step="${def.id}" data-direction="-1" ${quantity <= 0 ? "disabled" : ""}>-</button>
                          <span class="qty-value">${quantity}</span>
                          <button type="button" class="qty-btn" data-accessory-step="${def.id}" data-direction="1" ${quantity >= maxQty ? "disabled" : ""}>+</button>
                        </div>
                      `
                      : `<input type="checkbox" data-accessory="${def.id}" ${blockState.checked ? "checked" : ""} ${disabled ? "disabled" : ""} />`
                  }
                </div>
              </label>
              ${
                def.cameraType && quantity > 0
                  ? `
                    ${Array.from({ length: quantity }, (_, index) =>
                      renderExtensionBlock(
                        def,
                        blockState,
                        "accessory",
                        true,
                        index,
                        `${localizedText(def.extensionLabel)} ${index + 1}`
                      )
                    ).join("")}
                    ${
                      def.id === "ca42"
                        ? `
                          <div class="extension-picker">
                            <div class="extension-picker-head">
                              <strong>${"Serial port adapter cable"}</strong>
                              <span>${"Optional feature cable"}</span>
                            </div>
                            <div class="sku">1261050100291</div>
                            <label class="inline-check">
                              <input type="checkbox" data-accessory-addon="${def.id}" ${blockState.addonChecked ? "checked" : ""} />
                              <span>Enable trailer matching cable set</span>
                            </label>
                            <p class="hint">Available for all power-box builds to enable trailer matching. Limitation: R-Watch is unavailable only when this is enabled on Standard Power Box.</p>
                          </div>
                        `
                        : ""
                    }
                  `
                  : !def.cameraType && blockState.checked
                    ? `
                      ${renderExtensionBlock(def, blockState, "accessory")}
                      ${
                        def.secondaryExtensionRows?.length
                          ? renderExtensionBlock(def, blockState, "accessory", true, 0, "", {
                              extensionRows: def.secondaryExtensionRows,
                              label: localizedText(def.secondaryExtensionLabel),
                              stateField: "extraExtension",
                              lockExtension: false,
                            })
                          : ""
                      }
                    `
                    : ""
              }
            </section>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-accessory]").forEach((node) => {
    node.addEventListener("change", (event) => {
      toggleCustomAccessory(node.dataset.accessory, event.target.checked);
    });
  });
  wizardStageEl.querySelectorAll("[data-accessory-step]").forEach((node) => {
    node.addEventListener("click", () => {
      const accessoryId = node.dataset.accessoryStep;
      const currentQty = Number(ensureAccessoryState(accessoryId).quantity || 0);
      const nextQty = currentQty + Number(node.dataset.direction || 0);
      setCustomAccessoryQuantity(accessoryId, nextQty);
    });
  });
  wizardStageEl.querySelectorAll("[data-accessory-addon]").forEach((node) => {
    node.addEventListener("change", (event) => {
      toggleAccessoryAddon(node.dataset.accessoryAddon, event.target.checked);
    });
  });
}

function renderCustomOptionalStep() {
  const optionals = visibleCustomOptionals();
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().labels.currentMain}</strong>
        <p>${selectedCustomHost() ? localizedText(selectedCustomHost().title) : "-"} + ${selectedCustomPowerBox() ? localizedText(selectedCustomPowerBox().title) : "-"}</p>
      </div>
      <div>
        <strong>${t().labels.currentVideoCombo}</strong>
        <p>${selectedCustomAccessoryDefs().map((item) => localizedText(item.title)).join(" / ") || t().noneSelected}</p>
      </div>
    </div>
    <div class="group-list accessory-vertical-list">
      ${optionals
        .map((def) => {
          const item = def.sourceProductId ? findCatalogItem(def.sourceProductId, def.itemRow) : findItemByRow(def.itemRow);
          const blockState = ensureOptionalState(def.id);
          const quantity = Number(blockState.quantity || 0);
          const isMultiQty = Number(def.maxQuantity || 0) > 1;
          const disabled = isOptionalDisabled(def);
          const selected = (isMultiQty ? quantity > 0 : blockState.checked) ? "selected" : "";
          const preview = def.image || pickPreviewAsset(item?.images || []);
          return `
            <section class="group-card accessory-row-group">
              <label class="item-card accessory-row-card ${selected} ${disabled ? "disabled" : ""}">
                <div class="accessory-row-media">
                  ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${localizedText(def.title)}" />` : `<div class="thumb"></div>`}
                </div>
                <div class="accessory-row-copy">
                  <h4>${localizedText(def.title)}</h4>
                  <div class="sku">${item?.partNumber || (def.id === "micro_sd" ? "Multiple storage options" : t().noPartNumber)}</div>
                  <p>${optionalDetailText(def)}</p>
                </div>
                <div class="accessory-row-control">
                  ${
                    isMultiQty
                      ? `
                        <div class="qty-stepper" data-optional-stepper="${def.id}">
                          <button type="button" class="qty-btn" data-optional-step="${def.id}" data-direction="-1" ${quantity <= 0 || disabled ? "disabled" : ""}>-</button>
                          <span class="qty-value">${quantity}</span>
                          <button type="button" class="qty-btn" data-optional-step="${def.id}" data-direction="1" ${quantity >= Number(def.maxQuantity || 1) || disabled ? "disabled" : ""}>+</button>
                        </div>
                      `
                      : `<input type="checkbox" data-optional="${def.id}" ${blockState.checked ? "checked" : ""} ${disabled ? "disabled" : ""} />`
                  }
                </div>
              </label>
              ${
                quantity > 0 && def.id === "micro_sd"
                  ? `
                    <div class="extension-picker accessory-qty-picker storage-picker">
                      <div class="extension-picker-head">
                        <strong>Choose Micro SD cards</strong>
                        <span>Up to ${Number(def.maxQuantity || 2)} cards</span>
                      </div>
                      <div class="storage-card-grid">
                        <label class="storage-card">
                          <span class="storage-card-label">First card</span>
                          <select data-optional-variant="${def.id}" data-slot="1">
                            ${SD_CARD_VARIANTS.map((variant) => `<option value="${variant.partNumber}" ${blockState.variant1 === variant.partNumber ? "selected" : ""}>${localizedText(variant.name)}</option>`).join("")}
                          </select>
                          <span class="storage-card-sku">SKU ${blockState.variant1}</span>
                        </label>
                        ${
                          Number(blockState.quantity || 1) === 2
                            ? `
                              <label class="storage-card">
                                <span class="storage-card-label">Second card</span>
                                <select data-optional-variant="${def.id}" data-slot="2">
                                  ${SD_CARD_VARIANTS.map((variant) => `<option value="${variant.partNumber}" ${blockState.variant2 === variant.partNumber ? "selected" : ""}>${localizedText(variant.name)}</option>`).join("")}
                                </select>
                                <span class="storage-card-sku">SKU ${blockState.variant2}</span>
                              </label>
                            `
                            : ""
                        }
                      </div>
                    </div>
                  `
                  : ""
              }
              ${
                quantity > 0 && def.maxQuantity && def.extensionRows?.length
                  ? Array.from({ length: quantity }, (_, index) =>
                      renderExtensionBlock(
                        def,
                        blockState,
                        "optional",
                        !def.requiredExtension,
                        index,
                        `${localizedText(def.extensionLabel)} ${index + 1}`
                      ).replace(t().lockedCable, t().labels.b3Hint)
                    ).join("")
                  : blockState.checked && def.extensionRows?.length
                    ? renderExtensionBlock(def, blockState, "optional", !def.requiredExtension).replace(t().lockedCable, t().labels.b3Hint)
                    : ""
              }
            </section>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-optional]").forEach((node) => {
    node.addEventListener("change", (event) => {
      toggleCustomOptional(node.dataset.optional, event.target.checked);
    });
  });
  wizardStageEl.querySelectorAll("[data-optional-step]").forEach((node) => {
    node.addEventListener("click", () => {
      const optionalId = node.dataset.optionalStep;
      const currentQty = Number(ensureOptionalState(optionalId).quantity || 0);
      const nextQty = currentQty + Number(node.dataset.direction || 0);
      setOptionalQuantity(optionalId, nextQty);
    });
  });
  wizardStageEl.querySelectorAll("[data-optional-variant]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setOptionalVariant(node.dataset.optionalVariant, Number(node.dataset.slot), event.target.value);
    });
  });
}
