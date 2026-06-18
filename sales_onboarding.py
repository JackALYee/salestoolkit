"""Sales Onboarding tab for the Streamax Sales Toolkit.

Exports `content` — an HTML/JS string injected into app.py's components.html
iframe, same pattern as the other tabs (prospecting_flow, discovery_meeting…).

Renders the 5-phase new-rep onboarding path (Orient → Speak Streamax → Run the
Motion → Specialize → Live) as a vertical stepper. Each phase has:
  • Goal
  • Learn   — buttons that jump to the relevant toolkit tab (switchTab) or open Jerry GPT
  • Practice — copyable Jerry "mode" prompts (quiz / role-play / objection drill / pitch review)
  • Prove   — the gate, with a self-attested "mark complete" toggle

Progress + badges persist client-side in localStorage (v1). Server-side
scoring via the existing usage logs is the roadmap (see CLAUDE.md / Jerry logs).
"""
from __future__ import annotations

import base64
import html as _html


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# --- Phase data ------------------------------------------------------------
# action types for Learn links:
#   {"tab": "<content-section id>", "label": "..."}  -> switchTab in the iframe
#   {"jerry": True, "label": "..."}                  -> open Jerry GPT (parent frame)
PHASES = [
    {
        "id": "p0",
        "num": "0",
        "title": "Orient",
        "tagline": "Where am I, and what is this?",
        "time": "Days 1–3",
        "goal": "Navigate the toolkit and have one good conversation with Jerry.",
        "learn": [
            {"tab": "streamaxpedia", "label": "Tour Streamaxpedia"},
            {"jerry": True, "label": "Meet Jerry GPT"},
        ],
        "practice": [
            {"label": "Ask Jerry for the 2-minute company story",
             "prompt": "I just started as a Streamax sales rep. Explain the company, the Vision 2.0 story, and what makes us different in 2 minutes, like you're catching me up over coffee."},
        ],
        "prove": "Complete the Streamaxpedia tour and log your first Jerry chat. The win here is just showing up and coming back tomorrow.",
        "badge": "Oriented",
    },
    {
        "id": "p1",
        "num": "1",
        "title": "Speak Streamax",
        "tagline": "I can hold a product conversation.",
        "time": "Weeks 1–2",
        "goal": "Explain the portfolio + the SafeGPT thesis, and build a valid hardware config unaided.",
        "learn": [
            {"tab": "streamaxpedia", "label": "Search Engine + Product Matrix"},
            {"jerry": True, "label": "Ask Jerry about SafeGPT"},
        ],
        "practice": [
            {"label": "Jerry — Quiz mode (products & terms)",
             "prompt": "Quiz me on the Streamax product portfolio and terminology. Ask 8 questions one at a time, wait for my answer each time, tell me right/wrong with a one-line why, then give a final score out of 8. Start."},
            {"label": "Jerry — Score my SafeGPT pitch",
             "prompt": "Here is my 30-second SafeGPT pitch:\n\n[paste your pitch here]\n\nScore it 1-5 on each: (1) names the 'driver score, not raw events' idea, (2) cites a hard number, (3) says why competitors can't match it, (4) sounds like a human, not a brochure. Give the scores and the single most important fix."},
        ],
        "prove": "Deliver a 30-second SafeGPT pitch that scores ≥3/4 with Jerry, AND assemble a hardware config in the Product Matrix until the Solution Validator returns “Valid”.",
        "badge": "Streamax Speaker",
    },
    {
        "id": "p2",
        "num": "2",
        "title": "Run the Motion",
        "tagline": "I can take a deal from cold to discovery.",
        "time": "Weeks 3–6",
        "goal": "Prospect, open a call, run discovery, and survive the first wave of objections.",
        "learn": [
            {"tab": "prospecting-flow", "label": "Prospecting Flow (7-step + scripts)"},
            {"tab": "discovery", "label": "Discovery Meeting question bank"},
            {"tab": "presentation", "label": "Presentation (closed-loop journey)"},
        ],
        "practice": [
            {"label": "Jerry — Role-play a discovery call",
             "prompt": "Role-play as a skeptical fleet safety manager at a 200-truck long-haul carrier that currently uses Motive. I'm a new Streamax rep running a discovery call. Stay in character, give short realistic answers, and don't volunteer information — make me ask for it. When I end the call, score me on discovery (did I uncover the real pains?) and qualifying questions. Begin."},
            {"label": "Jerry — Objection drill",
             "prompt": "Run an objection drill. Give me one common objection a fleet operator raises, wait for my response, then score my response 1-5 and explain, then give the next one. Do 5 total, mixing pricing, incumbent-competitor, and 'just send me a deck'. Start with the pricing objection."},
            {"label": "Jerry — Cold email review",
             "prompt": "Here's a cold email I wrote to a prospect:\n\n[paste your email]\n\nCritique it in your voice — is it too much like a product manual? Does it lead with the customer's problem? Is the CTA low-friction? Rewrite the weakest part."},
        ],
        "prove": "Pass a simulated discovery call with Jerry (surface ≥3 of the 5 key pains, ask ≥4 qualifying questions) AND clear an objection volley (4/5). Then have your manager review one transcript.",
        "badge": "Motion Runner",
    },
    {
        "id": "p3",
        "num": "3",
        "title": "Specialize",
        "tagline": "I own one market and can beat the competition in it.",
        "time": "Weeks 6–10",
        "goal": "Deep fluency in your vertical + competitor battlecards + (if cleared) pricing.",
        "learn": [
            {"jerry": True, "label": "Deep-dive your vertical with Jerry"},
            {"tab": "value-calculator", "label": "Build a TCO case (Value Calculator)"},
            {"tab": "streamaxpedia", "label": "Confirm the config (Matrix)"},
        ],
        "practice": [
            {"label": "Jerry — Battlecard quiz",
             "prompt": "Quiz me with 10 'they say X, you say Y' battlecard questions for my vertical [school bus / transit / mining / trucking] against [Samsara / Motive / Lytx / Netradyne / MiTac / Hikvision]. One at a time, score each answer, give a final tally."},
            {"label": "Jerry — Win a mock deal",
             "prompt": "Run a mock deal. You are a buyer in my vertical [school bus / transit / mining / trucking] with a budget objection and a competitor incumbent. Make it multi-turn and realistic. At the end, tell me whether I earned a next step, and score me on discovery, value articulation, objection handling, and the close."},
        ],
        "prove": "Win a multi-turn mock deal vs Jerry-as-buyer in your vertical, build a real proposal (valid config + TCO case + one-page pitch) that passes Jerry's rubric, and score ≥8/10 on the battlecard quiz.",
        "badge": "Vertical Specialist",
    },
    {
        "id": "p4",
        "num": "4",
        "title": "Live with guardrails",
        "tagline": "I'm selling — Jerry is my copilot.",
        "time": "Week 10+",
        "goal": "Run real deals with the safety net still on.",
        "learn": [
            {"jerry": True, "label": "Use Jerry as your deal copilot"},
        ],
        "practice": [
            {"label": "Jerry — Draft a follow-up",
             "prompt": "Here's where my deal stands:\n\n[paste context — who, vertical, what was said, the objection]\n\nDraft my follow-up message, and tell me the single best next step to advance it."},
        ],
        "prove": "Advance a real qualified opportunity (or first close). Your manager reviews your logged Jerry interactions and real outcomes — this is where onboarding hands off to performance management.",
        "badge": "Certified",
    },
]


def _learn_button(item: dict) -> str:
    label = _html.escape(item["label"])
    if item.get("jerry"):
        return (
            f'<button class="ob-link ob-link-jerry" onclick="obOpenJerry(event);return false;">'
            f'<i data-lucide="message-circle"></i> {label}</button>'
        )
    tab = item["tab"]
    return (
        f'<button class="ob-link" onclick="obGoTab(\'{tab}\')">'
        f'<i data-lucide="arrow-right-circle"></i> {label}</button>'
    )


def _practice_card(item: dict) -> str:
    label = _html.escape(item["label"])
    b64 = _b64(item["prompt"])
    preview = _html.escape(item["prompt"][:140] + ("…" if len(item["prompt"]) > 140 else ""))
    return (
        '<div class="ob-prompt">'
        f'<div class="ob-prompt-head"><span class="ob-prompt-label">{label}</span></div>'
        f'<div class="ob-prompt-text">{preview}</div>'
        '<div class="ob-prompt-actions">'
        f'<button class="ob-btn-copy" onclick="obCopy(this,\'{b64}\')">'
        '<i data-lucide="copy"></i> Copy prompt</button>'
        '<button class="ob-btn-open" onclick="obOpenJerry(event);return false;">'
        '<i data-lucide="external-link"></i> Open Jerry GPT</button>'
        '</div></div>'
    )


def _phase_block(p: dict) -> str:
    learn = "".join(_learn_button(i) for i in p["learn"])
    practice = "".join(_practice_card(i) for i in p["practice"])
    return f"""
      <div class="ob-phase fade-up" id="ob-phase-{p['id']}" data-phase="{p['id']}">
        <div class="ob-marker"><span class="ob-marker-num">{p['num']}</span></div>
        <div class="ob-phase-body card">
          <div class="ob-phase-head">
            <div>
              <h3 class="ob-phase-title">Phase {p['num']} · {_html.escape(p['title'])}
                <span class="ob-badge-pill" id="ob-badge-{p['id']}"><i data-lucide="award"></i> {_html.escape(p['badge'])}</span>
              </h3>
              <p class="ob-phase-tagline">{_html.escape(p['tagline'])} <span class="ob-time">{_html.escape(p['time'])}</span></p>
            </div>
          </div>
          <p class="ob-goal"><strong>Goal:</strong> {_html.escape(p['goal'])}</p>

          <div class="ob-col-label"><i data-lucide="book-open"></i> Learn</div>
          <div class="ob-links">{learn}</div>

          <div class="ob-col-label"><i data-lucide="dumbbell"></i> Practice with Jerry</div>
          <div class="ob-practice">{practice}</div>

          <div class="ob-col-label"><i data-lucide="flag"></i> Prove — the gate</div>
          <div class="ob-prove">{_html.escape(p['prove'])}</div>

          <button class="ob-complete" id="ob-complete-{p['id']}" onclick="obToggle('{p['id']}')">
            <span class="ob-complete-icon"><i data-lucide="circle"></i></span>
            <span class="ob-complete-text">Mark Phase {p['num']} complete</span>
          </button>
        </div>
      </div>
    """


_PHASES_HTML = "".join(_phase_block(p) for p in PHASES)
_PHASE_IDS = ",".join(f'"{p["id"]}"' for p in PHASES)
_TOTAL = len(PHASES)


_STYLE = """
<style>
  #onboarding .ob-hero { text-align:center; }
  #onboarding .ob-progress-wrap { max-width:760px; margin:18px auto 6px; }
  #onboarding .ob-progress-track { height:10px; background:rgba(255,255,255,0.06); border:var(--glass-border); border-radius:20px; overflow:hidden; }
  #onboarding .ob-progress-fill { height:100%; width:0%; background:var(--gradient-text); border-radius:20px; transition:width .5s cubic-bezier(.4,0,.2,1); box-shadow:0 0 12px rgba(42,245,152,.4); }
  #onboarding .ob-progress-label { margin-top:8px; font-size:.85rem; color:var(--text-grey); }
  #onboarding .ob-progress-label b { color:var(--primary-green); }
  #onboarding .ob-reset { background:none; border:none; color:var(--text-grey); font-size:.72rem; text-decoration:underline; cursor:pointer; opacity:.6; margin-top:4px; }
  #onboarding .ob-reset:hover { opacity:1; color:#fca5a5; }

  #onboarding .ob-timeline { position:relative; max-width:920px; margin:30px auto 0; padding-left:8px; }
  #onboarding .ob-timeline::before { content:''; position:absolute; left:27px; top:20px; bottom:40px; width:2px; background:linear-gradient(to bottom, var(--primary-green), rgba(255,255,255,0.08)); }
  #onboarding .ob-phase { position:relative; padding-left:64px; margin-bottom:26px; }
  #onboarding .ob-marker { position:absolute; left:0; top:6px; width:54px; height:54px; border-radius:50%; background:var(--bg-deep); border:2px solid rgba(255,255,255,0.12); display:flex; align-items:center; justify-content:center; z-index:2; transition:all .3s; }
  #onboarding .ob-marker-num { font-size:1.4rem; font-weight:800; color:var(--text-grey); }
  #onboarding .ob-phase.ob-done .ob-marker { border-color:var(--primary-green); background:rgba(42,245,152,.1); box-shadow:0 0 18px rgba(42,245,152,.35); }
  #onboarding .ob-phase.ob-done .ob-marker-num { color:var(--primary-green); }

  #onboarding .ob-phase-body { margin-bottom:0; }
  #onboarding .ob-phase-title { font-size:1.25rem; margin-bottom:4px; display:flex; align-items:center; flex-wrap:wrap; gap:10px; }
  #onboarding .ob-phase-tagline { color:var(--text-grey); font-style:italic; margin-bottom:14px; font-size:.92rem; }
  #onboarding .ob-time { font-style:normal; font-size:.72rem; color:var(--secondary-blue); border:1px solid rgba(0,158,253,.3); border-radius:20px; padding:2px 10px; margin-left:8px; white-space:nowrap; }
  #onboarding .ob-goal { color:var(--text-white); border-left:3px solid var(--primary-green); padding-left:12px; margin-bottom:18px; font-size:.95rem; }

  #onboarding .ob-badge-pill { font-size:.62rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--text-dim,#6b7689); border:1px solid rgba(255,255,255,0.12); border-radius:20px; padding:3px 10px; display:inline-flex; align-items:center; gap:5px; opacity:.5; }
  #onboarding .ob-badge-pill svg { width:12px; height:12px; }
  #onboarding .ob-phase.ob-done .ob-badge-pill { color:var(--primary-green); border-color:var(--primary-green); background:rgba(42,245,152,.08); opacity:1; }

  #onboarding .ob-col-label { font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:var(--primary-green); margin:18px 0 10px; display:flex; align-items:center; gap:7px; }
  #onboarding .ob-col-label svg { width:14px; height:14px; }

  #onboarding .ob-links { display:flex; flex-wrap:wrap; gap:10px; }
  #onboarding .ob-link { display:inline-flex; align-items:center; gap:7px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); color:var(--text-white); padding:8px 14px; border-radius:10px; font-size:.85rem; font-weight:500; cursor:pointer; transition:all .2s; font-family:inherit; }
  #onboarding .ob-link svg { width:15px; height:15px; }
  #onboarding .ob-link:hover { border-color:var(--secondary-blue); background:rgba(0,158,253,.08); transform:translateY(-1px); }
  #onboarding .ob-link-jerry { border-color:rgba(42,245,152,.35); color:var(--primary-green); }
  #onboarding .ob-link-jerry:hover { border-color:var(--primary-green); background:rgba(42,245,152,.08); }

  #onboarding .ob-practice { display:flex; flex-direction:column; gap:12px; }
  #onboarding .ob-prompt { background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:14px 16px; }
  #onboarding .ob-prompt-label { font-weight:600; color:var(--text-white); font-size:.9rem; }
  #onboarding .ob-prompt-text { color:var(--text-grey); font-size:.82rem; margin:8px 0 12px; line-height:1.5; font-family:'Roboto Mono','SF Mono',Menlo,monospace; }
  #onboarding .ob-prompt-actions { display:flex; gap:10px; flex-wrap:wrap; }
  #onboarding .ob-btn-copy, #onboarding .ob-btn-open { display:inline-flex; align-items:center; gap:6px; padding:6px 13px; border-radius:8px; font-size:.78rem; font-weight:600; cursor:pointer; transition:all .2s; font-family:inherit; }
  #onboarding .ob-btn-copy svg, #onboarding .ob-btn-open svg { width:13px; height:13px; }
  #onboarding .ob-btn-copy { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.15); color:var(--text-grey); }
  #onboarding .ob-btn-copy:hover { border-color:var(--primary-green); color:var(--primary-green); }
  #onboarding .ob-btn-copy.ob-copied { border-color:var(--primary-green); color:var(--primary-green); background:rgba(42,245,152,.12); }
  #onboarding .ob-btn-open { background:linear-gradient(135deg,#2AF598 0%,#009EFD 100%); border:none; color:#050810; }
  #onboarding .ob-btn-open:hover { box-shadow:0 6px 14px rgba(42,245,152,.25); transform:translateY(-1px); }

  #onboarding .ob-prove { background:rgba(0,158,253,0.05); border-left:3px solid var(--secondary-blue); border-radius:0 8px 8px 0; padding:12px 16px; color:var(--text-grey); font-size:.88rem; line-height:1.55; }

  #onboarding .ob-complete { margin-top:18px; width:100%; display:flex; align-items:center; justify-content:center; gap:9px; padding:11px; border-radius:10px; background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.18); color:var(--text-grey); font-size:.88rem; font-weight:600; cursor:pointer; transition:all .2s; font-family:inherit; }
  #onboarding .ob-complete svg { width:17px; height:17px; }
  #onboarding .ob-complete:hover { border-color:var(--primary-green); color:var(--text-white); }
  #onboarding .ob-phase.ob-done .ob-complete { border-style:solid; border-color:var(--primary-green); background:rgba(42,245,152,.1); color:var(--primary-green); }

  @media (max-width:640px){
    #onboarding .ob-phase { padding-left:54px; }
    #onboarding .ob-timeline::before { left:22px; }
    #onboarding .ob-marker { width:44px; height:44px; }
    #onboarding .ob-marker-num { font-size:1.15rem; }
  }
</style>
"""


_SCRIPT = r"""
<script>
  (function(){
    var OB_KEY = 'streamax_onboarding_v1';
    var OB_PHASES = [__PHASE_IDS__];
    var OB_TOTAL = __TOTAL__;

    function obLoad(){ try { return JSON.parse(localStorage.getItem(OB_KEY) || '{}'); } catch(e){ return {}; } }
    function obSave(s){ try { localStorage.setItem(OB_KEY, JSON.stringify(s)); } catch(e){} }

    function obRefresh(){
      var s = obLoad(); var done = 0;
      OB_PHASES.forEach(function(pid){
        var phase = document.getElementById('ob-phase-'+pid);
        var btn = document.getElementById('ob-complete-'+pid);
        var on = !!s[pid];
        if (on) done++;
        if (phase) phase.classList.toggle('ob-done', on);
        if (btn){
          var icon = btn.querySelector('.ob-complete-icon');
          var txt = btn.querySelector('.ob-complete-text');
          var num = pid.replace('p','');
          if (icon) icon.innerHTML = on ? '<i data-lucide="check-circle-2"></i>' : '<i data-lucide="circle"></i>';
          if (txt) txt.textContent = on ? ('Phase '+num+' complete') : ('Mark Phase '+num+' complete');
        }
      });
      var pct = OB_TOTAL ? Math.round(done/OB_TOTAL*100) : 0;
      var fill = document.getElementById('ob-progress-fill');
      var lbl = document.getElementById('ob-progress-label');
      if (fill) fill.style.width = pct + '%';
      if (lbl) lbl.innerHTML = '<b>'+done+'</b> of '+OB_TOTAL+' phases complete · <b>'+pct+'%</b>';
      if (window.lucide && lucide.createIcons) { try { lucide.createIcons(); } catch(e){} }
    }

    window.obToggle = function(pid){
      var s = obLoad(); s[pid] = !s[pid]; obSave(s); obRefresh();
    };
    window.obResetOnboarding = function(){
      if (confirm('Reset all onboarding progress on this browser?')) { obSave({}); obRefresh(); }
    };
    window.obGoTab = function(tabId){
      try {
        if (typeof switchTab !== 'function') return;
        // Find the top-nav button that drives this tab so it highlights correctly.
        var match = null;
        document.querySelectorAll('.nav-btn').forEach(function(b){
          var oc = b.getAttribute('onclick') || '';
          if (oc.indexOf("switchTab('" + tabId + "'") !== -1) match = b;
        });
        switchTab(tabId, match);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch(e){}
    };
    window.obOpenJerry = function(evt){
      if (evt && evt.preventDefault) evt.preventDefault();
      var base = '';
      try { if (document.referrer) base = document.referrer; } catch(e){}
      if (!base) { try { base = window.parent.location.href; } catch(e){ base=''; } }
      if (!base) base = window.location.href;
      var url = base.split('?')[0].split('#')[0] + '?view=jerry_gpt';
      window.open(url, '_blank', 'noopener');
      return false;
    };
    window.obCopy = function(btn, b64){
      var text = '';
      try { text = decodeURIComponent(escape(atob(b64))); } catch(e){ text = atob(b64); }
      function flash(){
        btn.classList.add('ob-copied');
        var orig = btn.innerHTML;
        btn.innerHTML = '<i data-lucide="check"></i> Copied';
        if (window.lucide && lucide.createIcons) { try{ lucide.createIcons(); }catch(e){} }
        setTimeout(function(){ btn.classList.remove('ob-copied'); btn.innerHTML = orig; if(window.lucide&&lucide.createIcons){try{lucide.createIcons();}catch(e){}} }, 1600);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(flash).catch(function(){ obCopyFallback(text, flash); });
      } else { obCopyFallback(text, flash); }
    };
    function obCopyFallback(text, cb){
      var ta = document.createElement('textarea'); ta.value = text;
      ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.focus(); ta.select();
      try { document.execCommand('copy'); } catch(e){}
      document.body.removeChild(ta); if (cb) cb();
    }

    // Restore state on load (and shortly after, once lucide/icons are ready)
    obRefresh();
    setTimeout(obRefresh, 400);
    setTimeout(obRefresh, 1200);
  })();
</script>
"""


content = (
    _STYLE
    + """
        <!-- SECTION: SALES ONBOARDING -->
        <div id="onboarding" class="content-section hidden">
            <div class="card fade-up ob-hero">
                <h2 class="gradient-text">Sales Onboarding Path</h2>
                <p>Your ramp from day one to your first real deal — five phases, each with something to <strong>learn</strong>, something to <strong>practice with Jerry</strong>, and a <strong>gate to prove you're ready</strong> before moving on.</p>
                <div class="ob-progress-wrap">
                    <div class="ob-progress-track"><div class="ob-progress-fill" id="ob-progress-fill"></div></div>
                    <div class="ob-progress-label" id="ob-progress-label"><b>0</b> of __TOTAL__ phases complete · <b>0%</b></div>
                    <button class="ob-reset" onclick="obResetOnboarding()">Reset my progress</button>
                </div>
            </div>

            <div class="ob-timeline">
                __PHASES__
            </div>
        </div>
    """
    + _SCRIPT
)

# Substitute the generated pieces (kept out of the f-string to avoid brace clashes with the JS/CSS).
content = (
    content
    .replace("__PHASES__", _PHASES_HTML)
    .replace("__PHASE_IDS__", _PHASE_IDS)
    .replace("__TOTAL__", str(_TOTAL))
)
