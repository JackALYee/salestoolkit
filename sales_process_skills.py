"""Solution Selling process skills catalog for Jerry GPT.

Bundles a small set of Streamax-adapted Solution Selling plays under
./sales_process_skills/ as `<skill>/SKILL.md` (flat layout). Same mechanism as
pm_skills.py / marketing_skills.py: this module reads each SKILL.md's YAML
frontmatter (name + description) and builds:

  - CATALOG_TEXT  — a compact catalog injected into Jerry's cached system prompt
    so he knows every play and can apply / name / suggest the right one.
  - SKILLS_HINT   — the instruction telling Jerry how to use the catalog.
  - load_skill_body(name) — the FULL SKILL.md body for one play (on demand).

Distilled methodology (frameworks/process) is documented in
jerry_gpt_knowledge/16_solution_selling_method.md; these skills are the
apply-on-demand plays. Static → cache-stable inside the cached system block.
"""
from __future__ import annotations

import re
from pathlib import Path

_SKILLS_DIR = Path(__file__).parent / "sales_process_skills"


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


def _trim_desc(desc: str, max_len: int = 240) -> str:
    """Keep the first sentence of a description, capped at max_len."""
    if not desc:
        return ""
    first = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0].strip()
    if len(first) > max_len:
        first = first[: max_len - 1].rstrip() + "…"
    return first


def load_catalog() -> list[dict]:
    """Return [{name, description, path}, ...] for every bundled play, sorted
    by name. Empty if not bundled."""
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
        items.append({
            "name": fm["name"] or folder,
            "description": _trim_desc(fm["description"]),
            "path": str(skill_md),
        })
    items.sort(key=lambda d: d["name"])
    return items


def _build_catalog_text() -> str:
    items = load_catalog()
    if not items:
        return ""
    return "\n".join(f"- **{it['name']}** — {it['description']}" for it in items).strip()


CATALOG_TEXT = _build_catalog_text()
_NAME_INDEX = {it["name"]: it["path"] for it in load_catalog()}


def load_skill_body(name: str) -> str | None:
    """Return the full SKILL.md body for one play name, or None."""
    path = _NAME_INDEX.get(name)
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return None


SKILLS_HINT = (
    "You also have a SOLUTION SELLING PROCESS toolkit (catalogued below) — the "
    "apply-on-demand plays from Streamax's core sales methodology (the full "
    "method is in your knowledge as '16_solution_selling_method'). These are the "
    "backbone under complex, competitive fleet/TSP deals.\n\n"
    "When a rep's question fits a play:\n"
    "1. APPLY it to their ACTUAL deal (their fleet, competitor, numbers) — don't "
    "just describe the framework, run it on their situation.\n"
    "2. NAME the play you're using, e.g. \"Let's run the **9-Block** on this…\" "
    "or \"This is a **competitive-strategy** call — you're not first, so…\".\n"
    "3. If a play would help but you need one or two inputs first, SUGGEST it by "
    "name and ask.\n"
    "Default to the method's instincts: diagnose before you prescribe, pain "
    "first, quantify value in the buyer's numbers, find who has the power to buy, "
    "and think Column A. Only invoke a play when it genuinely fits."
)
