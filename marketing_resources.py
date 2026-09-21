"""Marketing Resources tab — customer-facing collateral, in one place.

Two subsections:
  * Marketing Materials → Product Websites — the division's open pages, which a
    rep can paste straight into an email. `SITES` below. Gated resources (the
    Customer Onboarding Portal, this toolkit) are deliberately absent: they live
    on the hub, and a login wall is not collateral.
  * Marketing Materials → Downloadable Decks — the same files Jerry GPT
    surfaces (see downloads.py), served from /assets/downloads/ so a rep can
    grab them without having to coax Jerry into offering the download.

The deck list is generated from `downloads.ASSETS`, so this page and Jerry can
never disagree about what exists — add a file there and it appears here.

**The green badge is a promise to a customer.** It reads `customer_safe` from
the asset's own entry in `downloads.ASSETS` and treats a missing flag as unsafe.
It used to be inferred from the filename containing "Partner Enablement", which
badged both documents whose blurb says "INTERNAL — do not forward outside
Streamax" as cleared for external sharing.
"""
from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path

try:
    import downloads as _downloads
except Exception:                                                    # noqa: BLE001
    _downloads = None

_DOWNLOADS_DIR = Path(__file__).parent / "assets" / "downloads"

# Public product microsites. `public` drives the badge — be honest about what a
# rep may forward without checking first.
#
# Only genuinely open pages belong here. The division's other two web resources
# — the Customer Onboarding Portal and this toolkit — sit behind a sign-in and
# are listed on the hub instead; putting them on a tab headed "send as-is" would
# hand a customer a login wall.
SITES = [
    {
        "name": "Streamax Trucking",
        "url": "https://www.streamax-trucking.com",
        "tagline": "The division's main page — and the safety loop running on it "
                   "as a live 3D story.",
        "detail": "Eleven stops from the yard to the debrief, with the cameras "
                  "that watch each one, then the two open solution pages below "
                  "it. Public and indexed since 21 Sep 2026; it carries no "
                  "pricing and no credentials, so it forwards safely as an "
                  "opener when you do not yet know which product fits.",
        "public": True,
    },
    {
        "name": "eSIM",
        # Link the trailing slash. Without it the host answers a redirect first.
        "url": "https://www.streamax-trucking.com/esim/",
        "tagline": "Connectivity that ships inside the camera — eUICC, pooled "
                   "data, one contract instead of four.",
        "detail": "eUICC and both form factors, the spec and qualification "
                  "tables, a live data-pool calculator you can size a route on "
                  "in front of a customer, and the published coverage and rate "
                  "card: 189 countries, 388 networks, from $1.50/GB.",
        "public": True,
    },
    {
        "name": "Sentinel (S5)",
        # Quote this standalone domain outward, not the /sentinel/ path on the
        # hub — same site, but this is the address meant to be shared.
        "url": "https://streamax-sentinel.com",
        "tagline": "The 24/7 camera that never sleeps — the fuel- and cargo-theft "
                   "story for parked trucks.",
        "detail": "Interactive 0.02-lux night-vision comparison, a live 3D "
                  "posture-detection demo, the Tanzania and Kenya field results, "
                  "and the full document set (deck, spec, manual, install guide).",
        "public": True,
    },
]

# Files bundled with the app but NOT in downloads.ASSETS would be invisible to
# Jerry; nothing today, but keep the merge honest if that changes.
_EXTERNAL_ONLY: list[dict] = []


# Jerry's labels end in a parenthetical that says the format and sometimes how
# to open the thing: "(PPTX)", "(PDF, 7 pages)", "(ZIP, open 点击播放.html)".
_LABEL_TAIL = re.compile(r"\s*\(([^()]*)\)\s*$")


def _split_label(label: str) -> tuple[str, str]:
    """-> (title, note). The note is whatever the parenthetical says beyond the
    format token, because the format itself comes from the file on disk."""
    title = label.replace("Download · ", "")
    match = _LABEL_TAIL.search(title)
    if not match:
        return title.strip(), ""
    title = title[:match.start()].strip()
    _, _, note = match.group(1).partition(", ")
    return title, note.strip()


def _decks() -> list[dict]:
    """Decks from downloads.ASSETS that actually exist on disk."""
    out = []
    for asset in (getattr(_downloads, "ASSETS", []) if _downloads else []):
        path = _DOWNLOADS_DIR / asset["filename"]
        if not path.is_file():
            continue
        title, note = _split_label(asset["label"])
        out.append({
            "filename": asset["filename"],
            "title": title,
            "note": note,
            # The extension, not the label: the card used to print "PPTX" over
            # a ZIP and over a PDF, because the word was hardcoded.
            "fmt": path.suffix.lstrip(".").upper() or "FILE",
            "blurb": asset.get("blurb", ""),
            "size_mb": path.stat().st_size / 1048576,
            # The flag is declared beside the file in downloads.ASSETS. It used
            # to be inferred from "Partner Enablement" appearing in the
            # filename, which badged both INTERNAL GDPR documents as safe to
            # send to customers. Absent means NOT safe: on a tab that invites
            # forwarding, the quiet failure has to be the cautious one.
            "public": bool(asset.get("customer_safe", False)),
        })
    return out + _EXTERNAL_ONLY


def _badge(is_public: bool) -> str:
    if is_public:
        return ('<span class="mr-badge mr-badge-ok">'
                '<i data-lucide="globe"></i> Public — safe to send to customers</span>')
    return ('<span class="mr-badge mr-badge-warn">'
            '<i data-lucide="shield-alert"></i> '
            'Internal / partner only — not for customers</span>')


def _site_card(s: dict) -> str:
    parts = urllib.parse.urlparse(s["url"])
    # netloc alone collapsed /esim/ onto the hub's own address.
    host = parts.netloc + (parts.path if parts.path != "/" else "")
    return f"""
        <div class="mr-card">
            <div class="mr-card-head">
                <h4>{html.escape(s['name'])}</h4>
                <div class="mr-url">{html.escape(host)}</div>
                {_badge(s['public'])}
            </div>
            <p class="mr-tagline">{html.escape(s['tagline'])}</p>
            <p class="mr-detail">{html.escape(s['detail'])}</p>
            <div class="mr-actions">
                <a class="mr-btn mr-btn-primary" href="{html.escape(s['url'])}"
                   target="_blank" rel="noopener noreferrer">
                    <i data-lucide="external-link"></i> Open site
                </a>
                <button type="button" class="mr-btn"
                        onclick="mrCopy('{html.escape(s['url'])}', this)">
                    <i data-lucide="copy"></i> Copy link
                </button>
            </div>
        </div>"""


def _deck_card(d: dict) -> str:
    href = "/assets/downloads/" + urllib.parse.quote(d["filename"])
    # .get throughout: _EXTERNAL_ONLY entries are hand-written and need not
    # carry every key _decks() derives from a file on disk.
    meta = html.escape(" · ".join(
        x for x in (d.get("fmt", "FILE"), f"{d['size_mb']:.1f} MB",
                    d.get("note", "")) if x))
    return f"""
        <div class="mr-card">
            <div class="mr-card-head">
                <h4>{html.escape(d['title'])}</h4>
                <div class="mr-url">{meta}</div>
                {_badge(d['public'])}
            </div>
            <p class="mr-detail">{html.escape(d['blurb'])}</p>
            <div class="mr-actions">
                <a class="mr-btn mr-btn-primary" href="{href}" download>
                    <i data-lucide="download"></i> Download
                </a>
            </div>
        </div>"""


def _build() -> str:
    site_cards = "\n".join(_site_card(s) for s in SITES)
    decks = _decks()
    deck_cards = ("\n".join(_deck_card(d) for d in decks) if decks else
                  '<p class="mr-empty">No decks are bundled with this build.</p>')

    return f"""
<div id="marketing-resources" class="content-section hidden tex2jax_ignore">
    <style>
        .mr-wrap{{max-width:1180px;margin:0 auto}}
        .mr-sub{{margin:34px 0 6px;font-size:1.05rem;font-weight:700;color:var(--text-white);
            display:flex;align-items:center;gap:9px}}
        .mr-sub i{{width:17px;height:17px;color:var(--primary-green)}}
        .mr-sub-note{{color:var(--text-grey);font-size:.82rem;margin:0 0 18px}}
        .mr-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}}
        .mr-card{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.09);
            border-radius:14px;padding:20px;transition:.25s;display:flex;flex-direction:column}}
        .mr-card:hover{{border-color:rgba(42,245,152,.4);transform:translateY(-3px);
            box-shadow:0 12px 28px rgba(0,0,0,.32)}}
        .mr-card-head{{margin-bottom:12px}}
        .mr-card h4{{margin:0;font-size:1.02rem;color:var(--text-white);font-weight:700}}
        .mr-url{{font-size:.74rem;color:var(--secondary-blue);margin-top:3px;
            font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
        .mr-badge{{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:999px;
            font-size:.66rem;font-weight:700;line-height:1.3;margin-top:9px}}
        .mr-badge i{{width:11px;height:11px;flex:none}}
        .mr-badge-ok{{background:rgba(42,245,152,.11);color:#2AF598;border:1px solid rgba(42,245,152,.3)}}
        .mr-badge-warn{{background:rgba(255,184,0,.11);color:#FFB800;border:1px solid rgba(255,184,0,.3)}}
        .mr-tagline{{color:var(--text-white);font-size:.9rem;margin:0 0 8px;line-height:1.5}}
        .mr-detail{{color:var(--text-grey);font-size:.84rem;margin:0 0 16px;line-height:1.6;flex:1}}
        .mr-actions{{display:flex;gap:9px;flex-wrap:wrap;margin-top:auto}}
        .mr-btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:8px;
            font-size:.8rem;font-weight:600;cursor:pointer;text-decoration:none;font-family:inherit;
            background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);
            color:var(--text-white);transition:.2s}}
        .mr-btn:hover{{background:rgba(255,255,255,.12);border-color:rgba(255,255,255,.3)}}
        .mr-btn i{{width:14px;height:14px}}
        .mr-btn-primary{{background:linear-gradient(135deg,var(--primary-green),var(--secondary-blue));
            color:#050810;border:none;font-weight:700}}
        .mr-btn-primary:hover{{transform:translateY(-2px);box-shadow:0 5px 16px rgba(42,245,152,.35)}}
        .mr-empty{{color:var(--text-grey);font-size:.86rem}}
    </style>

    <div class="mr-wrap">
        <h2 class="section-title">Marketing Resources</h2>
        <p class="section-subtitle">
            Customer-facing material you can send as-is — plus a few partner and internal files.
            Read the badge on a card before you forward it.
        </p>

        <h3 class="mr-sub"><i data-lucide="megaphone"></i> Marketing Materials</h3>
        <p class="mr-sub-note">
            Product websites and decks, ready to paste into an email or forward to a prospect.
        </p>

        <h3 class="mr-sub"><i data-lucide="globe"></i> Product Websites</h3>
        <div class="mr-grid">
{site_cards}
        </div>

        <h3 class="mr-sub"><i data-lucide="presentation"></i> Downloadable Decks</h3>
        <div class="mr-grid">
{deck_cards}
        </div>
    </div>

    <script>
        function mrCopy(text, btn) {{
            var done = function () {{
                var old = btn.innerHTML;
                btn.innerHTML = '<i data-lucide="check"></i> Copied';
                if (window.lucide) lucide.createIcons();
                setTimeout(function () {{
                    btn.innerHTML = old;
                    if (window.lucide) lucide.createIcons();
                }}, 1600);
            }};
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(done, done);
            }} else {{
                var ta = document.createElement('textarea');
                ta.value = text; document.body.appendChild(ta); ta.select();
                try {{ document.execCommand('copy'); }} catch (e) {{}}
                document.body.removeChild(ta); done();
            }}
        }}
    </script>
</div>
"""


content = _build()
