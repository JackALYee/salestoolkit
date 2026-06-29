"""Sales & Marketing skills catalog for Jerry GPT.

Bundles the 45-skill marketing library (Corey Haines' marketingskills) under
./marketing_skills/ as `<skill>/SKILL.md` (flat layout — no category folders).
This module reads each SKILL.md's YAML frontmatter (name + description) and
builds:

  - CATALOG_TEXT  — a compact, grouped catalog injected into Jerry's system
    prompt so he knows every marketing/sales skill that exists and can name /
    suggest / apply the right one. Descriptions are trimmed to their first
    sentence (the long trigger-keyword lists in the source are dropped) to keep
    the cached prompt small.
  - SKILLS_HINT   — the instruction telling Jerry how to use the catalog
    (apply the skill and announce it, or suggest it by name).
  - load_skill_body(name) — returns the FULL SKILL.md body for one skill, for
    optional on-demand deep application (not loaded into the base prompt).

The catalog is static (derived from committed files), so it stays cache-stable
inside Jerry's cached system block. Mirrors pm_skills.py.
"""
from __future__ import annotations

import re
from pathlib import Path

_SKILLS_DIR = Path(__file__).parent / "marketing_skills"

# Curated grouping for the 45 skills so the catalog reads cleanly. Any skill
# not listed here falls into "Other Marketing Skills" — so newly-added skills
# still appear without a code change.
_CATEGORY_BY_SKILL = {
    # Research & Insight
    "competitor-profiling": "Research & Insight",
    "competitors": "Research & Insight",
    "customer-research": "Research & Insight",
    "marketing-psychology": "Research & Insight",
    "analytics": "Research & Insight",
    # Strategy & Positioning
    "product-marketing": "Strategy & Positioning",
    "marketing-plan": "Strategy & Positioning",
    "content-strategy": "Strategy & Positioning",
    "marketing-ideas": "Strategy & Positioning",
    "pricing": "Strategy & Positioning",
    "offers": "Strategy & Positioning",
    "launch": "Strategy & Positioning",
    # Sales & Outbound
    "cold-email": "Sales & Outbound",
    "prospecting": "Sales & Outbound",
    "sales-enablement": "Sales & Outbound",
    "revops": "Sales & Outbound",
    # Content & Creative
    "copywriting": "Content & Creative",
    "copy-editing": "Content & Creative",
    "emails": "Content & Creative",
    "sms": "Content & Creative",
    "ad-creative": "Content & Creative",
    "image": "Content & Creative",
    "video": "Content & Creative",
    "social": "Content & Creative",
    # SEO & Web
    "seo-audit": "SEO & Web",
    "ai-seo": "SEO & Web",
    "programmatic-seo": "SEO & Web",
    "schema": "SEO & Web",
    "site-architecture": "SEO & Web",
    "directory-submissions": "SEO & Web",
    # Acquisition & Conversion
    "ads": "Acquisition & Conversion",
    "cro": "Acquisition & Conversion",
    "ab-testing": "Acquisition & Conversion",
    "paywalls": "Acquisition & Conversion",
    "popups": "Acquisition & Conversion",
    "signup": "Acquisition & Conversion",
    "lead-magnets": "Acquisition & Conversion",
    "free-tools": "Acquisition & Conversion",
    # Growth & Retention
    "onboarding": "Growth & Retention",
    "churn-prevention": "Growth & Retention",
    "referrals": "Growth & Retention",
    "community-marketing": "Growth & Retention",
    "co-marketing": "Growth & Retention",
    "public-relations": "Growth & Retention",
    "aso": "Growth & Retention",
}

# Order categories appear in the catalog.
_CATEGORY_ORDER = [
    "Strategy & Positioning",
    "Research & Insight",
    "Sales & Outbound",
    "Content & Creative",
    "Acquisition & Conversion",
    "SEO & Web",
    "Growth & Retention",
    "Other Marketing Skills",
]


def _parse_frontmatter(text: str) -> dict:
    """Pull name + description out of a SKILL.md YAML frontmatter block."""
    out = {"name": "", "description": ""}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    block = m.group(1) if m else text[:800]
    nm = re.search(r'^\s*name:\s*"?([^"\n]+)"?\s*$', block, re.MULTILINE)
    dm = re.search(r'^\s*description:\s*"?(.+?)"?\s*$', block, re.MULTILINE | re.DOTALL)
    if nm:
        out["name"] = nm.group(1).strip()
    if dm:
        desc = re.sub(r"\s+", " ", dm.group(1)).strip().rstrip('"').strip()
        out["description"] = desc
    return out


def _trim_desc(desc: str, max_len: int = 220) -> str:
    """Keep the first sentence of a description (drops the long 'Also use when
    the user mentions …' keyword lists), capped at max_len."""
    if not desc:
        return ""
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0].strip()
    if len(first) > max_len:
        first = first[: max_len - 1].rstrip() + "…"
    return first


def _category_for(skill_name: str) -> str:
    return _CATEGORY_BY_SKILL.get(skill_name, "Other Marketing Skills")


def load_catalog() -> list[dict]:
    """Return [{category, name, description, path}, ...] for every bundled
    skill, sorted by category order then name. Empty if not bundled."""
    if not _SKILLS_DIR.is_dir():
        return []
    items: list[dict] = []
    for skill_md in sorted(_SKILLS_DIR.glob("*/SKILL.md")):
        folder = skill_md.parts[-2]
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _parse_frontmatter(text)
        name = fm["name"] or folder
        items.append({
            "category": _category_for(folder),
            "name": name,
            "description": _trim_desc(fm["description"]),
            "path": str(skill_md),
        })
    order = {c: i for i, c in enumerate(_CATEGORY_ORDER)}
    items.sort(key=lambda d: (order.get(d["category"], 99), d["name"]))
    return items


def _build_catalog_text() -> str:
    items = load_catalog()
    if not items:
        return ""
    lines: list[str] = []
    current_cat = None
    for it in items:
        if it["category"] != current_cat:
            current_cat = it["category"]
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
# on these marketing/sales frameworks and to be transparent about which one he
# applied. Mirrors pm_skills.SKILLS_HINT.
SKILLS_HINT = (
    "You also have a SALES & MARKETING SKILLS LIBRARY (catalogued below) — "
    "practical, expert playbooks covering positioning, pricing, cold email & "
    "prospecting, sales enablement, copywriting, SEO/AI-SEO, paid ads, "
    "conversion-rate optimization, launches, PR, retention, and more. Many "
    "sales and go-to-market questions map cleanly onto one of these.\n\n"
    "When a user's question fits a skill:\n"
    "1. APPLY the relevant skill's playbook to structure your answer — don't "
    "just describe it, use it on their actual situation (their product, "
    "audience, deal).\n"
    "2. TELL THE USER which skill you applied, naturally, e.g. "
    "\"I'm using the **cold-email** playbook here…\" or \"This is a fit for the "
    "**pricing** skill — here's how it plays out for your case.\"\n"
    "3. If a skill would clearly help but you need more input first, SUGGEST it "
    "by name and ask the one or two questions you need.\n"
    "These marketing skills sit alongside the PM SKILLS LIBRARY — pick whichever "
    "fits the question best, and you may combine them. Only invoke a skill when "
    "it genuinely fits — don't force one onto every question. Use the exact "
    "skill name from the catalog when you name it."
)
