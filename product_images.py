"""Product image library for Jerry GPT.

When Jerry mentions a Streamax product by name in his answer, the chat UI
surfaces a picture of it so the user can see what's being discussed. Images
were rendered from the official School Bus + Public Transport solution decks
and live in assets/products/*.jpg.

Two public helpers:
  - find_product_images(text) -> ordered, de-duped list of (image_path, caption)
    for every product mentioned in `text`.
  - PRODUCT_NAME_HINT -> a short string listing the products that have images,
    injected into Jerry's system prompt so he refers to them by exact name.

Matching is case-insensitive with alphanumeric boundary guards, so "C20D"
doesn't match inside "CA20D" and "P3" doesn't match inside "P3D".
"""
from __future__ import annotations

import re
from pathlib import Path

_ASSETS = Path(__file__).parent / "assets" / "products"

# image filename (without .jpg) -> human caption shown under the picture
_IMAGE_CAPTIONS = {
    "palm_vein_reader":        "Palm Vein Recognition reader — School Bus attendance",
    "stoparm_c28_c27_b2":      "Stop-Arm capture hardware — C28 AI camera · C27 plate camera · B2 alarm",
    "child_check_c34":         "C34 / CA34 AI Child-Check camera (92% accuracy)",
    "motion_sensor_dp7s":      "DP7S motion sensor — Child Check (99.9% accuracy)",
    "child_check_layers":      "Child Check — 3-layer solution (button · AI camera · motion sensor)",
    "m1n_2_0":                 "M1N 2.0 — entry tier MDVR",
    "x3n":                     "X3N — MDVR (2–4 lane stop-arm capture)",
    "x5n_pro":                 "X5N Pro — MDVR (5–8 lane capture / regional regulatory)",
    "ibcu_schoolbus":          "IBCU — Intelligent Bus Central Unit (School Bus flagship)",
    "ibcu":                    "IBCU (A16Max) — all-in-one Intelligent Bus Central Unit",
    "c29n":                    "C29N — DMS driver-monitoring camera (face-tracing IR)",
    "adkit_3_0":               "ADKIT3.0 — expandable DMS camera (ADAS-ready)",
    "ca20s":                   "CA20S — single-lens ADAS camera",
    "c20d":                    "C20D — dual-lens ADAS camera",
    "ca20d":                   "CA20D — triple-lens ADAS camera (+ANPR)",
    "bsd_family":              "Blind-Spot Detection family — CA24S · C46 · C53 · AVM",
    "c46":                     "C46 — top-down BSD camera (16m both sides)",
    "c53":                     "C53 — flagship long-range black-light BSD (50m lateral)",
    "cms20":                   "CMS20 — digital rear-view mirror (Blacklight 1.8T)",
    "ai_avm":                  "AI-AVM — 360° around-view monitor",
    "apc_p3_p3d":              "P3 / P3D — Automatic Passenger Counting (99% / 85% OD)",
    "pis_displays":            "L16MAX-286 / L16MAX-215 — passenger info displays",
    "pis_box_ims100":          "PIS Box (IMS 100) — onboard media player",
    "mdvr_tiers":              "MDVR tiers — M1N2.0 · X3NPro · A8Pro2.0 · A16Max",
    "bus_operation_portfolio": "Bus operation portfolio — XPAD · X3NPro · A8Pro · A16Max",
    # Mining solution
    "mining_product_store":    "Mining product store — M10 / M10 PRO / M1N 2.0 tiers + IPC line",
    "mining_system_schematic": "Mining safety system — M10 MDVR + DMS + BSD + radar",
    "mining_bsd":              "Mining BSD — dual-lens blacklight, 270° dead-zone-free",
    "mining_fcw":              "Mining ADAS — Forward Collision Warning IPC",
    "mining_dms_edge":         "Mining Driver Behavior IPC — edge DMS (gas-mask fatigue)",
    "mining_blacklight_cam":   "Mining blacklight smart camera (0.01–0.03 lux)",
    "mining_radar_vision":     "Radar-vision fusion — dust-penetrating mmWave + camera",
    "mining_v2v":              "V2V — vehicle-to-vehicle beyond-visual-range alerts",
    "mining_reverse_radar":    "Reverse radar-vision fusion warning",
    "mining_reversing_cam":    "Intelligent reversing camera (tire-to-wall distance)",
    "mining_bucket_tooth":     "Excavator bucket-tooth detachment detection",
    "mining_large_block":      "Large-block detection system",
    "mining_minesync_cloud":   "MineSync-Cloud + SafeGPT mining platform",
    "mining_scenario_overview":"Mining solution — full scenario coverage",
    # Vision 2.0 / new products
    "dcmax_gt1":               "DC MAX AI dashcam + GT1 telematics gateway",
    "dcmax_6ch_architecture":  "DC MAX — 6-channel video-telematics architecture",
    "fms_tracker":             "FMS Tracker — dead-reckoning asset tracker",
    "safegpt_dashboard":       "SafeGPT — real-time risk dashboard",
    "safegpt_driver_eval":     "SafeGPT — driver evaluation & coaching",
    "trailer_4k_blacklight":   "In-cargo 4K + 1080P blacklight cameras",
    "trailer_volume_ai":       "AI cargo-volume detection (95% accuracy)",
    "cargo_security_device":   "All-in-one cargo-security device (Q4 2025)",
    "cargo_device_allinone":   "Cargo-security device — all-in-one interfaces",
    "blacklight_ultra":        "Blacklight Ultra — 0.02-lux night vision",
}

# product alias -> image filename. Aliases are matched case-insensitively with
# alphanumeric boundary guards. List longer/more-specific aliases too; the
# scanner resolves each match to its image and de-dupes by image afterward.
_ALIAS_TO_IMAGE = {
    # School Bus
    "palm vein": "palm_vein_reader",
    "palm-vein": "palm_vein_reader",
    "C28": "stoparm_c28_c27_b2",
    "C27": "stoparm_c28_c27_b2",
    "B2": "stoparm_c28_c27_b2",
    "C34": "child_check_c34",
    "CA34": "child_check_c34",
    "DP7S": "motion_sensor_dp7s",
    "child check": "child_check_layers",
    "child-check": "child_check_layers",
    "M1N 2.0": "m1n_2_0",
    "M1N2.0": "m1n_2_0",
    "X3N": "x3n",
    "X5N Pro": "x5n_pro",
    "X5NPro": "x5n_pro",
    # Public Transport
    "IBCU": "ibcu",
    "A16Max": "ibcu",
    "A16 Max": "ibcu",
    "A16MAX": "ibcu",
    "C29N": "c29n",
    "ADKIT3.0": "adkit_3_0",
    "ADKIT 3.0": "adkit_3_0",
    "ADKIT": "adkit_3_0",
    "CA20S": "ca20s",
    "C20D": "c20d",
    "CA20D": "ca20d",
    "CA24S": "bsd_family",
    "C46": "c46",
    "C53": "c53",
    "CMS20": "cms20",
    "AI-AVM": "ai_avm",
    "AVM": "ai_avm",
    "P3D": "apc_p3_p3d",
    "P3": "apc_p3_p3d",
    "L16MAX-286": "pis_displays",
    "L16MAX-215": "pis_displays",
    "L16MAX": "pis_displays",
    "PIS Box": "pis_box_ims100",
    "IMS 100": "pis_box_ims100",
    "IMS100": "pis_box_ims100",
    "X3NPro": "mdvr_tiers",
    "X3N Pro": "mdvr_tiers",
    "A8Pro2.0": "mdvr_tiers",
    "A8Pro": "mdvr_tiers",
    "A8PRO": "mdvr_tiers",
    "XPAD": "bus_operation_portfolio",
    # Mining solution
    "M10 PRO": "mining_product_store",
    "M10PRO": "mining_product_store",
    "M10": "mining_product_store",
    "Mining BSD": "mining_bsd",
    "Mining ADAS": "mining_fcw",
    "Mining Driver Behavior": "mining_dms_edge",
    "Thermal Smart CAM": "mining_product_store",
    "bucket tooth": "mining_bucket_tooth",
    "bucket teeth": "mining_bucket_tooth",
    "large block": "mining_large_block",
    "V2V": "mining_v2v",
    "V2X": "mining_v2v",
    "MineSync-Cloud": "mining_minesync_cloud",
    "MineSync": "mining_minesync_cloud",
    "reversing camera": "mining_reversing_cam",
    "smart reversing": "mining_reversing_cam",
    "radar-vision": "mining_radar_vision",
    "radar vision": "mining_radar_vision",
    "millimeter-wave radar": "mining_product_store",
    "blacklight smart camera": "mining_blacklight_cam",
    # Vision 2.0 / new products
    "DC MAX": "dcmax_gt1",
    "DC-MAX": "dcmax_gt1",
    "DCMAX": "dcmax_gt1",
    "GT1": "dcmax_gt1",
    "FMS Tracker": "fms_tracker",
    "Blacklight Ultra": "blacklight_ultra",
    "cargo security": "cargo_security_device",
}

# Pre-compile one regex per alias with alphanumeric boundary guards.
# (?<![A-Za-z0-9]) ... (?![A-Za-z0-9]) so "C20D" won't fire inside "CA20D"
# and "P3" won't fire inside "P3D".
_COMPILED = [
    (re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", re.IGNORECASE), image)
    for alias, image in _ALIAS_TO_IMAGE.items()
]

# Cap how many images we surface per answer so a product-heavy response
# doesn't bury the text under a wall of pictures.
MAX_IMAGES = 4


def find_product_images(text: str) -> list[tuple[str, str]]:
    """Scan `text` for product mentions; return ordered, de-duped
    [(image_path, caption), ...] for products that have a picture on disk.

    Order = first appearance in the text. De-duped by image file (so a stop-arm
    answer mentioning C28, C27 and B2 shows the one capture-hardware slide once).
    Capped at MAX_IMAGES.
    """
    if not text:
        return []

    # Find earliest match position for each image file
    first_pos: dict[str, int] = {}
    for pattern, image in _COMPILED:
        m = pattern.search(text)
        if m is None:
            continue
        pos = m.start()
        if image not in first_pos or pos < first_pos[image]:
            first_pos[image] = pos

    if not first_pos:
        return []

    ordered = sorted(first_pos.items(), key=lambda kv: kv[1])
    out: list[tuple[str, str]] = []
    for image, _pos in ordered:
        path = _ASSETS / f"{image}.jpg"
        if path.is_file():
            out.append((str(path), _IMAGE_CAPTIONS.get(image, image)))
        if len(out) >= MAX_IMAGES:
            break
    return out


# Injected into Jerry's system prompt so he names products precisely (which is
# what lets the scanner surface the right picture). Kept short to stay cheap.
PRODUCT_NAME_HINT = (
    "When you discuss a specific Streamax product, refer to it by its exact "
    "model name (e.g. C29N, CA20D, C53, IBCU, P3D, M1N 2.0, C34, DP7S, CMS20, "
    "L16MAX-286; mining: M10, M10 PRO, Mining BSD, Mining ADAS, V2V, MineSync-Cloud; "
    "new products: DC MAX, GT1, FMS Tracker, Blacklight Ultra). The interface "
    "automatically shows the user a product photo for the models you name, so "
    "precise naming helps them see what you mean. Do not invent image links or "
    "markdown images — just name the product."
)
