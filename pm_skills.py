"""PM-skills catalog for Jerry GPT.

Bundles the 68-skill PM library (9 categories) under ./pm_skills/ as
`<category>/<skill>/SKILL.md`. This module reads each SKILL.md's YAML
frontmatter (name + description) and builds:

  - CATALOG_TEXT  — a compact, grouped catalog injected into Jerry's system
    prompt so he knows every skill that exists and can name / suggest / apply
    the right framework.
  - SKILLS_HINT   — the instruction telling Jerry how to use the catalog
    (suggest a skill, or apply it and announce which one he used).
  - load_skill_body(name) — returns the FULL SKILL.md body for one skill, for
    optional on-demand deep application (not loaded into the base prompt).

The catalog is static (derived from committed files), so it stays cache-stable
inside Jerry's cached system block.
"""
from __future__ import annotations

import re
from pathlib import Path

_SKILLS_DIR = Path(__file__).parent / "pm_skills"

# Human-readable category labels keyed by the bundled plugin-folder names.
_CATEGORY_LABELS = {
    "pm-product-strategy": "Product Strategy",
    "pm-product-discovery": "Product Discovery",
    "pm-market-research": "Market Research",
    "pm-go-to-market": "Go-To-Market",
    "pm-marketing-growth": "Marketing & Growth",
    "pm-execution": "Execution",
    "pm-data-analytics": "Data & Analytics",
    "pm-ai-shipping": "AI Shipping",
    "pm-toolkit": "PM Toolkit",
}


def _parse_frontmatter(text: str) -> dict:
    """Pull name + description out of a SKILL.md YAML frontmatter block."""
    out = {"name": "", "description": ""}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    block = m.group(1) if m else text[:600]
    nm = re.search(r'^\s*name:\s*"?([^"\n]+)"?\s*$', block, re.MULTILINE)
    dm = re.search(r'^\s*description:\s*"?(.+?)"?\s*$', block, re.MULTILINE | re.DOTALL)
    if nm:
        out["name"] = nm.group(1).strip()
    if dm:
        # description may span lines; collapse whitespace and strip a trailing quote
        desc = re.sub(r"\s+", " ", dm.group(1)).strip().rstrip('"').strip()
        out["description"] = desc
    return out


def load_catalog() -> list[dict]:
    """Return [{category, category_label, name, description, path}, ...] for
    every bundled skill, sorted by category then name. Empty if not bundled."""
    if not _SKILLS_DIR.is_dir():
        return []
    items: list[dict] = []
    for skill_md in sorted(_SKILLS_DIR.glob("*/*/SKILL.md")):
        category = skill_md.parts[-3]
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_frontmatter(text)
        name = fm["name"] or skill_md.parts[-2]
        items.append({
            "category": category,
            "category_label": _CATEGORY_LABELS.get(category, category),
            "name": name,
            "description": fm["description"],
            "path": str(skill_md),
        })
    items.sort(key=lambda d: (d["category_label"], d["name"]))
    return items


def _build_catalog_text() -> str:
    items = load_catalog()
    if not items:
        return ""
    lines: list[str] = []
    current_cat = None
    for it in items:
        if it["category_label"] != current_cat:
            current_cat = it["category_label"]
            lines.append(f"\n### {current_cat}")
        lines.append(f"- **{it['name']}** — {it['description']}")
    return "\n".join(lines).strip()


CATALOG_TEXT = _build_catalog_text()
_NAME_INDEX = {it["name"]: it["path"] for it in load_catalog()}


def load_skill_body(name: str) -> str | None:
    """Return the full SKILL.md body for one skill name, or None. For optional
    deep application — not part of the base prompt."""
    path = _NAME_INDEX.get(name)
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return None


# Injected into Jerry's system prompt alongside the catalog. Tells him to lean
# on these PM frameworks and to be transparent about which one he applied.
SKILLS_HINT = (
    "You have access to a PM SKILLS LIBRARY (catalogued below) — proven "
    "product-management frameworks covering strategy, discovery, market "
    "research, go-to-market, growth, execution, analytics, and AI shipping. "
    "Many sales questions map cleanly onto one of these frameworks.\n\n"
    "When a user's question fits a skill:\n"
    "1. APPLY the relevant skill's framework to structure your answer — don't "
    "just describe it, use it on their actual situation.\n"
    "2. TELL THE USER which skill you applied, naturally, e.g. "
    "\"I'm working through this with the **competitive-battlecard** framework…\" "
    "or \"This is a fit for the **ideal-customer-profile** skill — here's how it "
    "plays out for your case.\"\n"
    "3. If a skill would clearly help but you need more input from the user "
    "first, SUGGEST it by name and ask the one or two questions you need.\n"
    "Only invoke a skill when it genuinely fits — don't force one onto every "
    "question. Use the exact skill name from the catalog when you name it."
)
