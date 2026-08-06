function renderM3nCameraStep() {
  const items = m1nItemsByRows(currentMSeriesStepRows().cameras)
    .filter((item) => (isM1nProduct() ? ![15, 16].includes(item.rowNumber) : ![14, 15].includes(item.rowNumber)))
    .sort((left, right) => {
      const rank = (item) => {
        const text = `${item.name || ""} ${item.group || ""}`.toLowerCase();
        if (/c29n/.test(text)) return 1;
        if (/c46/.test(text)) return 2;
        if (/ca29m/.test(text)) return 3;
        if (/ca20s/.test(text)) return 4;
        if (/ad\s*kit/.test(text)) return 5;
        if (/ca46/.test(text)) return 6;
        return 10;
      };
      return rank(left) - rank(right);
    });
  const cameraStatus = m3nPresetCameraStatus();
  const channelRule = currentMSeriesChannelRule();
  const productTitle = currentProduct()?.title || "M-series";
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("当前基础套装", "Current base kit")}</strong>
        <p>${currentPackage() ? displayCatalogText(currentPackage().name) : "-"}</p>
      </div>
    </div>
    <section class="algorithm-plan-panel">
      <div class="algorithm-plan-head">
        <div>
          <strong>${L("算法与通道方案", "Algorithm & channel plan")}</strong>
          <span>${L("IPC、AHD 与录像通道均为硬限制。", "IPC, AHD, and recording channels are enforced.")}${hostCascadeActive() ? L(`（${hostCascadeName()} 级联已预占 ${avmCascadeReserved().ipc} IPC${avmCascadeReserved().ahd ? ` + ${avmCascadeReserved().ahd} AHD` : ""} / ${avmCascadeReserved().recording} 路录像，已计入额度）`, ` (${hostCascadeName()} cascade reserves ${avmCascadeReserved().ipc} IPC${avmCascadeReserved().ahd ? ` + ${avmCascadeReserved().ahd} AHD` : ""} / ${avmCascadeReserved().recording} recording, already counted.)`) : ""}</span>
        </div>
        <div class="resource-badge-list">
          <span>IPC ${cameraStatus.ipc}/${channelRule.ipc}</span>
          <span>AHD ${cameraStatus.ahd}/${channelRule.ahd}</span>
          <span>${L("录像", "Recording")} ${cameraStatus.recording}/${channelRule.recording}</span>
          <span>${L("内置算法", "Internal AI")} ${cameraStatus.internalAlgorithms}/2</span>
          <span>${L("外置算法", "External AI")} ${cameraStatus.externalAlgorithms}</span>
        </div>
      </div>
      <div class="algorithm-preset-grid">
        <button type="button" class="algorithm-preset-card" data-mseries-preset="adkit_ca46">
          <strong>4 AI · ADKIT + 2 × CA46</strong>
          <span>ADAS + DMS ${L("（外置）", "(external)")} · ${L("左 BSD + 右 BSD（MDVR）", "Left BSD + Right BSD (MDVR)")}</span>
          <small>IPC 1 · AHD 2 · ${L("录像通道", "Recording")} 4</small>
        </button>
        <button type="button" class="algorithm-preset-card" data-mseries-preset="c46_ca20s_ca29m">
          <strong>4 AI · 2 × C46 + CA20S + CA29M</strong>
          <span>${L("左 BSD + 右 BSD（外置）· ADAS + DMS（MDVR）", "Left BSD + Right BSD (external) · ADAS + DMS (MDVR)")}</span>
          <small>IPC 2 · AHD 2 · ${L("录像通道", "Recording")} 4</small>
        </button>
      </div>
    </section>
    <div class="capacity-note">
      <strong>${L("接口余量", "Interface remaining")}</strong>
      <p>${productTitle}: ${cameraStatus.ipcRemaining} IPC / ${cameraStatus.ahdRemaining} AHD / ${cameraStatus.recordingRemaining} ${L("路录像通道可用", "recording channels available")}.</p>
    </div>
    <div class="group-list accessory-vertical-list">
      ${items
        .map((item) => {
                    const block = ensurePresetSelectionState(item.id, item.quantity || "1");
                    const resource = mSeriesCameraResource(item);
                    const quantitySelectable = Boolean(resource && !resource.bundle);
                    const quantity = resource ? mSeriesSelectionQuantity(item) : (block.checked ? 1 : 0);
                    const maxQty = quantitySelectable ? Math.max(0, maxM3nPresetQuantity(item)) : 1;
                    const checked = block.checked ? "checked" : "";
                    const selected = (isM3nPresetCameraItem(item) ? quantity > 0 : block.checked) ? "selected" : "";
                    const info = skuInfo(item.partNumber);
                    const preview = info?.image || fallbackItemPreviewAsset(item);
                    const displayName = info?.title ? localizedText(info.title) : displayCatalogText(item.name);
                    const displayDetail = info?.detail !== undefined ? L(info.detail, info.detailEn) : displayCatalogText(item.note || item.description || "");
                    const cameraType = resource?.type || null;
                    const disabled =
                      !selected &&
                      Boolean(resource) &&
                      ((resource.ipc > cameraStatus.ipcRemaining) ||
                        (resource.ahd > cameraStatus.ahdRemaining) ||
                        (resource.recording > cameraStatus.recordingRemaining));
                    const extensionRows = m3nCameraExtensionRowsForMSeries(item);
                    const childRows = m3nAdkitChildRows(item);
                    const extensionTitle =
                      extensionRows === M3N_CAMERA_EXTENSION_ROWS.ipc
                        ? ("IPC extension cable")
                        : ("AHD extension cable");
                    return `
                      <section class="group-card accessory-row-group">
                        <label class="item-card accessory-row-card ${selected} ${disabled ? "disabled" : ""}">
                          <div class="accessory-row-media">
                            ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${displayCatalogText(item.name)}" />` : `<div class="thumb"></div>`}
                          </div>
                          <div class="accessory-row-copy">
                            <h4>${displayName}</h4>
                            <div class="sku">${item.partNumber || t().noPartNumber}</div>
                            <p>${displayDetail}</p>
                            ${
                              resource
                                ? `<div class="camera-resource-line">IPC ${resource.ipc} · AHD ${resource.ahd} · ${L("录像", "Recording")} ${resource.recording}${resource.externalAlgorithms.length ? ` · ${resource.externalAlgorithms.map(mSeriesAlgorithmLabel).join(" + ")} ${L("外置", "external")}` : ""}</div>`
                                : ""
                            }
                          </div>
                          <div class="accessory-row-control">
                            ${
                              quantitySelectable
                                ? `
                                  <div class="qty-stepper" data-m3n-camera-stepper="${item.id}">
                                    <button type="button" class="qty-btn" data-m3n-camera-step="${item.id}" data-direction="-1" ${quantity <= 0 ? "disabled" : ""}>-</button>
                                    <span class="qty-value">${quantity}</span>
                                    <button type="button" class="qty-btn" data-m3n-camera-step="${item.id}" data-direction="1" ${maxQty <= 0 || quantity >= maxQty ? "disabled" : ""}>+</button>
                                  </div>
                                `
                                : `<input type="checkbox" data-m3n-camera="${item.id}" ${checked} ${disabled ? "disabled" : ""} />`
                            }
                          </div>
                        </label>
                        ${
                          resource && quantity > 0 && extensionRows.length
                            ? Array.from({ length: quantity }, (_, index) => {
                                const selectedExtensionId = block.extensions?.[index] || block.extensionId || "";
                                return `
                                  <div class="extension-picker">
                                    <div class="extension-picker-head">
                                      <strong>${extensionTitle} ${index + 1}</strong>
                                      <span>${t().chooseLength}</span>
                                    </div>
                                    <label>
                                      <span>${t().lengthAndPart}</span>
                                      <select data-m3n-camera-extension="${item.id}" data-m3n-camera-extension-slot="${index}">
                                        ${extensionRows
                                          .map((rowNumber) => {
                                            const extensionItem = findItemByRow(rowNumber);
                                            const selectedOption = selectedExtensionId === extensionItem?.id ? "selected" : "";
                                            return `<option value="${rowNumber}" ${selectedOption}>${formatExtensionOptionLabel(extensionItem)}</option>`;
                                          })
                                          .join("")}
                                      </select>
                                    </label>
                                    <p class="hint">${t().installImpact}</p>
                                  </div>
                                `;
                              }).join("")
                            : ""
                        }
                        ${
                          resource?.ahd && quantity > 0
                            ? `
                              <div class="algorithm-assignment-grid">
                                ${Array.from({ length: quantity }, (_, index) => {
                                  const allowedAlgorithms = mSeriesAllowedInternalAlgorithms(item);
                                  const storedAlgorithm = block.algorithms?.[index] || "";
                                  const selectedAlgorithm = allowedAlgorithms.includes(storedAlgorithm) ? storedAlgorithm : "";
                                  const otherAlgorithms = cameraStatus.internalAlgorithms - (selectedAlgorithm ? 1 : 0);
                                  return `
                                    <label class="algorithm-assignment">
                                      <span>${L("MDVR 算法", "MDVR algorithm")} ${index + 1}</span>
                                      <select data-mseries-algorithm="${item.id}" data-mseries-algorithm-slot="${index}">
                                        <option value="" ${selectedAlgorithm ? "" : "selected"}>${L("仅录像，不启用算法", "Recording only")}</option>
                                        ${allowedAlgorithms.map((algorithm) => `<option value="${algorithm}" ${selectedAlgorithm === algorithm ? "selected" : ""} ${!selectedAlgorithm && otherAlgorithms >= 2 ? "disabled" : ""}>${mSeriesAlgorithmLabel(algorithm)}</option>`).join("")}
                                      </select>
                                    </label>
                                  `;
                                }).join("")}
                              </div>
                            `
                            : ""
                        }
                        ${
                          block.checked && childRows.length
                            ? `
                              <div class="extension-picker">
                                <div class="extension-picker-head">
                                  <strong>${L("AD Kit 配件", "AD Kit accessories")}</strong>
                                  <span>${L("按需勾选支架和螺丝", "Select bracket and screws if needed")}</span>
                                </div>
                                <div class="sub-option-list">
                                  ${childRows
                                    .map((rowNumber) => {
                                      const childItem = findItemByRow(rowNumber);
                                      if (!childItem) return "";
                                      const childChecked = state.selections[childItem.id]?.checked ? "checked" : "";
                                      const childPreview = fallbackItemPreviewAsset(childItem);
                                      return `
                                        <label class="sub-option-card">
                                          <div class="sub-option-media">
                                            ${childPreview ? `<img loading="lazy" decoding="async" class="thumb" src="./${childPreview}" alt="${displayCatalogText(childItem.name)}" />` : `<div class="thumb"></div>`}
                                          </div>
                                          <div class="sub-option-copy">
                                            <strong>${displayCatalogText(childItem.name)}</strong>
                                            <span>${childItem.partNumber || t().noPartNumber}</span>
                                          </div>
                                          <input type="checkbox" data-m3n-camera-child="${childItem.id}" ${childChecked} />
                                        </label>
                                      `;
                                    })
                                    .join("")}
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

  wizardStageEl.querySelectorAll("[data-m3n-camera]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setM3nPresetSelection(node.dataset.m3nCamera, event.target.checked);
    });
  });

  wizardStageEl.querySelectorAll("[data-m3n-camera-step]").forEach((node) => {
    node.addEventListener("click", () => {
      const itemId = node.dataset.m3nCameraStep;
      const block = ensurePresetSelectionState(itemId);
      const currentQty = block.checked ? Number(block.quantity || 0) : 0;
      const nextQty = currentQty + Number(node.dataset.direction || 0);
      setM3nPresetQuantity(itemId, nextQty);
    });
  });

  wizardStageEl.querySelectorAll("[data-m3n-camera-extension]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setM3nPresetCameraExtension(
        node.dataset.m3nCameraExtension,
        event.target.value,
        Number(node.dataset.m3nCameraExtensionSlot || 0)
      );
    });
  });

  wizardStageEl.querySelectorAll("[data-m3n-camera-child]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setM3nPresetChildSelection(node.dataset.m3nCameraChild, event.target.checked);
    });
  });
  wizardStageEl.querySelectorAll("[data-mseries-algorithm]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setMSeriesInternalAlgorithm(
        node.dataset.mseriesAlgorithm,
        Number(node.dataset.mseriesAlgorithmSlot || 0),
        event.target.value
      );
    });
  });
  wizardStageEl.querySelectorAll("[data-mseries-preset]").forEach((node) => {
    node.addEventListener("click", () => applyMSeriesAlgorithmPreset(node.dataset.mseriesPreset));
  });
}

function renderM1nBaseStep() {
  const pkg = currentPackage() || packageCandidates()[0];
  const preview = pkg ? pickPreviewAsset(pkg.images || []) : "";
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("流程说明", "Flow")}</strong>
        <p>${"Next, select wiring, then cameras, then accessories."}</p>
      </div>
    </div>
    <section class="group-card accessory-row-group">
      <div class="item-card accessory-row-card selected">
        <div class="accessory-row-media">
          ${preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${preview}" alt="${pkg ? displayCatalogText(pkg.name) : ""}" />` : `<div class="thumb"></div>`}
        </div>
        <div class="accessory-row-copy">
          <h4>${pkg ? displayCatalogText(pkg.name) : "M1N 2.0"}</h4>
          <div class="sku">${pkg?.partNumber || t().noPartNumber}</div>
          <p>${pkg ? displayCatalogText(pkg.note || pkg.description || "") : ""}</p>
        </div>
        <div class="accessory-row-control">
          <div class="tag">${L("基础套装", "Base kit")}</div>
        </div>
      </div>
    </section>
  `;
}

function renderM1nWiringStep() {
  renderM1nSelectableStep(
    m1nItemsByRows(currentMSeriesStepRows().wiring),
    L("当前基础套装", "Current base kit")
  );
}

function renderM1nCameraStep() {
  renderM3nCameraStep();
}

function renderM3nOptionalStep() {
  const items = m1nItemsByRows(currentMSeriesStepRows().optionals).filter((item) =>
    isM1nProduct() ? ![9, 32, 35].includes(item.rowNumber) : ![33, 35].includes(item.rowNumber)
  );
  const grouped = groupedItems(items);
  const itemCard = (item) => {
    const block = ensurePresetSelectionState(item.id, item.quantity || "1");
    const checked = block.checked ? "checked" : "";
    const selected = block.checked ? "selected" : "";
    const childRows = m3nOptionalChildRows(item);
    const extensionRows = m3nOptionalExtensionRows(item);
    const display = m3nOptionalDisplay(item);
    // Storage rows (SD / SSD) carry several part numbers by capacity; let the user pick one.
    const variantOptions = presetVariantOptions(item);
    const selectedVariant = variantOptions
      ? variantOptions.find((entry) => entry.partNumber === block.variantPartNumber) || variantOptions[0]
      : null;
    const headingName = variantOptions ? localizedText(selectedVariant.name) : display.name;
    const skuText = variantOptions ? selectedVariant.partNumber : item.partNumber || t().noPartNumber;
    return `
      <section class="group-card accessory-row-group">
        <label class="item-card accessory-row-card ${selected}">
          <div class="accessory-row-media">
            ${display.preview ? `<img loading="lazy" decoding="async" class="thumb" src="./${display.preview}" alt="${headingName}" />` : `<div class="thumb"></div>`}
          </div>
          <div class="accessory-row-copy">
            <h4>${headingName}</h4>
            <div class="sku">${skuText}</div>
            <p>${display.note}</p>
          </div>
          <div class="accessory-row-control">
            <input type="checkbox" data-m3n-optional="${item.id}" ${checked} />
          </div>
        </label>
        ${
          block.checked && variantOptions
            ? `
              <div class="extension-picker">
                <div class="extension-picker-head">
                  <strong>${L("容量 / 料号", "Capacity / part number")}</strong>
                  <span>${"Choose based on project requirements"}</span>
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
        ${
          block.checked && childRows.length
            ? `
              <div class="extension-picker">
                <div class="extension-picker-head">
                  <strong>${L("配套线材", "Included cable")}</strong>
                  <span>${"Included with this item"}</span>
                </div>
                <div class="sub-option-list">
                  ${childRows
                    .map((rowNumber) => {
                      const childItem = findItemByRow(rowNumber);
                      if (!childItem) return "";
                      const childPreview = fallbackItemPreviewAsset(childItem);
                      return `
                        <label class="sub-option-card locked">
                          <div class="sub-option-media">
                            ${childPreview ? `<img loading="lazy" decoding="async" class="thumb" src="./${childPreview}" alt="${displayCatalogText(childItem.name)}" />` : `<div class="thumb"></div>`}
                          </div>
                          <div class="sub-option-copy">
                            <strong>${displayCatalogText(childItem.name)}</strong>
                            <span>${childItem.partNumber || t().noPartNumber}</span>
                          </div>
                          <input type="checkbox" checked disabled />
                        </label>
                      `;
                    })
                    .join("")}
                </div>
              </div>
            `
            : ""
        }
        ${
          block.checked && extensionRows.length
            ? `
              <div class="extension-picker">
                <div class="extension-picker-head">
                  <strong>${item.rowNumber === 31 ? "AHD extension cable" : "IPC extension cable"}</strong>
                  <span>${t().chooseLength}</span>
                </div>
                <label>
                  <span>${t().lengthAndPart}</span>
                  <select data-m3n-optional-extension="${item.id}">
                    ${extensionRows
                      .map((rowNumber) => {
                        const extension = findItemByRow(rowNumber);
                        const selectedOption = block.extensionId === extension?.id ? "selected" : "";
                        return `<option value="${rowNumber}" ${selectedOption}>${formatExtensionOptionLabel(extension)}</option>`;
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
  };
  wizardStageEl.innerHTML = `
    <div class="focus-banner">
      <div>
        <strong>${t().summaryFields.product}</strong>
        <p>${currentProduct()?.title || "-"}</p>
      </div>
      <div>
        <strong>${L("当前基础套装", "Current base kit")}</strong>
        <p>${currentPackage() ? displayCatalogText(currentPackage().name) : "-"}</p>
      </div>
    </div>
    <div class="group-list accessory-vertical-list">
      ${Object.entries(grouped)
        .map(([groupName, groupItems]) => {
          // Singleton groups render flat; multi-item groups keep a header.
          if (groupItems.length < 2) return groupItems.map(itemCard).join("");
          const heading = groupItems.some((item) => item.rowNumber === 36 || item.rowNumber === 8)
            ? "Microphone"
            : groupItems.some((item) => item.rowNumber === 34)
              ? L("Speaker 喇叭", "Speaker")
              : displayCatalogText(groupName);
          return `
            <section class="group-card">
              <div class="group-meta">
                <h3>${heading}</h3>
                <div class="group-badge">${groupItems.length}</div>
              </div>
              <div class="group-list accessory-vertical-list">
                ${groupItems.map(itemCard).join("")}
              </div>
            </section>
          `;
        })
        .join("")}
    </div>
  `;

  wizardStageEl.querySelectorAll("[data-m3n-optional]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setM3nPresetSelection(node.dataset.m3nOptional, event.target.checked);
    });
  });
  wizardStageEl.querySelectorAll("[data-preset-variant]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setPresetVariant(node.dataset.presetVariant, event.target.value);
    });
  });
  wizardStageEl.querySelectorAll("[data-m3n-optional-extension]").forEach((node) => {
    node.addEventListener("change", (event) => {
      setM3nPresetCameraExtension(node.dataset.m3nOptionalExtension, event.target.value);
    });
  });
}

function renderM1nOptionalStep() {
  renderM3nOptionalStep();
}
