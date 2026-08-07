"""Marketing Resources tab — customer-facing collateral, in one place.

Two subsections:
  * Marketing Materials → Product Websites — public microsites a rep can paste
    straight into an email.
  * Marketing Materials → Downloadable Decks — the same PPTX files Jerry GPT
    surfaces (see downloads.py), served from /assets/downloads/ so a rep can
    grab them without having to coax Jerry into offering the download.

The deck list is generated from `downloads.ASSETS`, so this page and Jerry can
never disagree about what exists — add a file there and it appears here.
"""
from __future__ import annotations

import html
import urllib.parse
from pathlib import Path

try:
    import downloads as _downloads
except Exception:                                                    # noqa: BLE001
    _downloads = None

_DOWNLOADS_DIR = Path(__file__).parent / "assets" / "downloads"

# Public product microsites. `public` drives the badge — be honest about what a
# rep may forward without checking first.
SITES = [
    {
        "name": "Sentinel (S5)",
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


def _decks() -> list[dict]:
    """Decks from downloads.ASSETS that actually exist on disk."""
    out = []
    for asset in (getattr(_downloads, "ASSETS", []) if _downloads else []):
        path = _DOWNLOADS_DIR / asset["filename"]
        if not path.is_file():
            continue
        out.append({
            "filename": asset["filename"],
            "title": asset["label"].replace("Download · ", "").replace(" (PPTX)", ""),
            "blurb": asset.get("blurb", ""),
            "size_mb": path.stat().st_size / 1048576,
            # Partner-enablement material is not automatically customer-safe.
            "public": "Partner Enablement" not in asset["filename"],
        })
    return out + _EXTERNAL_ONLY


def _badge(is_public: bool) -> str:
    if is_public:
        return ('<span class="mr-badge mr-badge-ok">'
                '<i data-lucide="globe"></i> Public — safe to send to customers</span>')
    return ('<span class="mr-badge mr-badge-warn">'
            '<i data-lucide="shield-alert"></i> '
            'Partner enablement — check before forwarding externally</span>')


def _site_card(s: dict) -> str:
    host = urllib.parse.urlparse(s["url"]).netloc
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
    return f"""
        <div class="mr-card">
            <div class="mr-card-head">
                <h4>{html.escape(d['title'])}</h4>
                <div class="mr-url">PPTX · {d['size_mb']:.1f} MB</div>
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
            Customer-facing material you can send as-is. Everything here is cleared for external sharing.
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
