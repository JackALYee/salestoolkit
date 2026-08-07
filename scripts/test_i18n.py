"""Browser test for the page-wide language switcher + Marketing Resources.

Needs the scraper venv (playwright) and a built page:
    python3 build_static.py && .scrape_venv/bin/python scripts/test_i18n.py
"""
from playwright.sync_api import sync_playwright
import pathlib, sys

URL = "file://" + str(pathlib.Path(__file__).resolve().parent.parent / "site" / "index.html")
fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

EXPECT = {
    "zh": {"nav": "客户开发流程", "hdr": "全球",      "guide": "锐明销售工具箱使用指南"},
    "ja": {"nav": "見込み客開拓フロー", "hdr": "グローバル", "guide": "Streamax セールスツールキット利用ガイド"},
    "es": {"nav": "Flujo de Prospección", "hdr": "Global", "guide": "Guía de Uso del Kit de Ventas Streamax"},
    "pt": {"nav": "Fluxo de Prospecção", "hdr": "Global", "guide": "Guia de Uso do Kit de Vendas Streamax"},
    "fr": {"nav": "Parcours de Prospection", "hdr": "Mondiale", "guide": "Guide d'Utilisation de la Boîte à Outils Commerciale Streamax"},
    "it": {"nav": "Flusso di Prospezione", "hdr": "Globale", "guide": "Guida all'Uso del Toolkit Commerciale Streamax"},
}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(1200)

    print("=== default state ===")
    check("loads in English", "Prospecting Flow" in pg.inner_text("nav.nav-tabs"))
    check("switcher visible", pg.is_visible("#stmx-lang"))
    check("switcher is in the top-right", pg.evaluate("""() => {
        const r = document.querySelector('#stmx-lang').getBoundingClientRect();
        return r.top < 80 && (window.innerWidth - r.right) < 320;
    }"""))
    check("does not overlap the user pill", pg.evaluate("""() => {
        const a = document.querySelector('#stmx-lang').getBoundingClientRect();
        const b = document.querySelector('.user-pill').getBoundingClientRect();
        return a.right <= b.left + 1 || b.right <= a.left + 1;
    }"""))
    check("no JS errors on load", not errors, str(errors[:2]))

    print("\n=== switching languages ===")
    for code, want in EXPECT.items():
        pg.evaluate(f"stmxSetLang('{code}')")
        pg.wait_for_timeout(320)
        nav = pg.inner_text("nav.nav-tabs")
        hdr = pg.inner_text("header h1")
        guide = pg.inner_text("#app-intro-title")
        ok = want["nav"] in nav and want["hdr"] in hdr and want["guide"] in guide
        check(f"{code}: nav + header + guide translated", ok,
              f"nav={nav[:40]!r} hdr={hdr[:24]!r}")

    print("\n=== round trip back to English ===")
    pg.evaluate("stmxSetLang('en')")
    pg.wait_for_timeout(320)
    check("nav restored", "Prospecting Flow" in pg.inner_text("nav.nav-tabs"))
    check("header restored", "Global" in pg.inner_text("header h1"))
    check("guide restored", "Streamax Sales Toolkit User Guide" in pg.inner_text("#app-intro-title"))
    check("no duplicated text after round trip",
          pg.inner_text("nav.nav-tabs").count("Prospecting Flow") == 1)

    print("\n=== persistence ===")
    pg.evaluate("stmxSetLang('ja')")
    pg.wait_for_timeout(250)
    pg.reload(wait_until="load"); pg.wait_for_timeout(1200)
    check("language survives reload (localStorage)",
          "見込み客開拓フロー" in pg.inner_text("nav.nav-tabs"))
    pg.evaluate("stmxSetLang('en')")

    print("\n=== Marketing Resources tab ===")
    pg.evaluate("""() => {
        const b = [...document.querySelectorAll('.nav-btn')]
            .find(x => x.textContent.includes('Marketing Resources'));
        b.click();
    }""")
    pg.wait_for_timeout(500)
    sec = pg.inner_text("#marketing-resources")
    check("section renders", pg.is_visible("#marketing-resources"))
    check("Marketing Materials subsection", "Marketing Materials" in sec)
    check("sentinel site card", "streamax-sentinel.com" in sec)
    check("two decks listed", sec.count("Download") >= 2, f"count={sec.count('Download')}")
    hrefs = pg.eval_on_selector_all("#marketing-resources a[download]", "els => els.map(e => e.getAttribute('href'))")
    check("deck hrefs point at /assets/downloads/", all(h.startswith("/assets/downloads/") for h in hrefs), str(hrefs))

    print("\n=== dynamic content re-translation (MutationObserver) ===")
    pg.evaluate("stmxSetLang('fr')")
    pg.wait_for_timeout(300)
    pg.evaluate("""() => {
        const d = document.createElement('div');
        d.id = 'late'; d.textContent = 'Value Calculator';
        document.querySelector('#marketing-resources').appendChild(d);
    }""")
    pg.wait_for_timeout(700)
    check("late-injected node gets translated",
          pg.inner_text("#late") == "Calculateur de Valeur", pg.inner_text("#late"))
    pg.evaluate("stmxSetLang('en')")

    check("still no JS errors", not errors, str(errors[:3]))
    b.close()

print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
