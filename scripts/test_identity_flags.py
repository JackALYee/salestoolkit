"""Identity flags on the HTML site: easter eggs, LEADERSHIP, SPECIAL_RELATIONSHIPS.

The Streamlit path set these into st.session_state at login; the FastAPI path
has to re-derive them per request. This checks it actually does.

    python3 scripts/test_identity_flags.py
"""
import pathlib, sys, types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
st = types.ModuleType("streamlit"); st.session_state = {}
class _S:
    def get(self, k, d=None): return None
st.secrets = _S()
def _d(*a, **k):
    def w(f): return f
    return w
st.cache_resource = _d; st.cache_data = _d
for n in ("markdown", "error", "stop", "rerun"): setattr(st, n, lambda *a, **k: None)
sys.modules["streamlit"] = st
c = types.ModuleType("streamlit.components"); v = types.ModuleType("streamlit.components.v1")
v.html = lambda *a, **k: None; c.v1 = v
sys.modules["streamlit.components"] = c; sys.modules["streamlit.components.v1"] = v

import login, jerry_gpt

fails = 0
def check(label, cond, detail=""):
    global fails
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + ("" if cond else f"   {detail}"))
    if not cond: fails += 1

def clearance(user, first_turn=True):
    """Exactly what server.py /api/chat builds for this user."""
    return jerry_gpt._build_clearance_block(
        user if "@" in user else "", user,
        bool(login.resolve_leadership(user)),
        is_first_turn=first_turn,
        special_relationship=login.resolve_special_relationship(user),
    )["text"]

print("=== login easter eggs still authenticate ===")
for creds, want in [(("jerry_test", "testme"), "Jerry"),
                    (("hekun_test", "testme"), "Hekun"),
                    (("zntang_test", "testme"), "ZNTang"),
                    (("test_account", "testme"), "Success")]:
    ok, msg = login.verify_streamax_credentials(*creds)
    check(f"{creds[0]:14s} -> {want}", ok and msg == want, f"got ({ok}, {msg!r})")
ok, _ = login.verify_streamax_credentials("jerry_test", "wrongpass")
check("wrong easter-egg password rejected", not ok)

print("\n=== LEADERSHIP resolves for display names and emails ===")
for who in ["Jerry", "Hekun", "jcyi@streamax.com", "johnz@streamax.com"]:
    check(f"{who:20s} is leadership", bool(login.resolve_leadership(who)))
for who in ["test_account", "nobody@streamax.com"]:
    check(f"{who:20s} is NOT leadership", not login.resolve_leadership(who))
# ZNTang has an easter-egg login and an entry in _EASTER_EGG_TO_EMAIL, but
# zntang@streamax.com is deliberately NOT in LEADERSHIP_EMAILS. Asserted so the
# distinction is explicit rather than looking like an oversight.
check("ZNTang authenticates but is NOT leadership",
      not login.resolve_leadership("ZNTang"))
check("jhsun no longer leadership", not login.resolve_leadership("jhsun@streamax.com"))

print("\n=== SPECIAL_RELATIONSHIPS reach the prompt (was hardcoded None) ===")
t = clearance("Jerry")
check("Jerry himself: relationship section present", "SPECIAL" in t.upper())
check("Jerry himself: informal 你 override", "你" in t and "special-relationship override" in t)
t = clearance("hekun@streamax.com")
check("Kun He: recognised as best buddy", "Kun He" in t)
t = clearance("wangrui@streamax.com")
check("Rui Wang: recognised as best buddy", "Rui Wang" in t)
t = clearance("nobody@streamax.com")
check("ordinary user: no special section", "special-relationship override" not in t)

print("\n=== greeting fires only on the first turn ===")
first = clearance("Jerry", first_turn=True)
later = clearance("Jerry", first_turn=False)
check("first turn is longer (greeting attached)", len(first) > len(later))
check("later turns still keep the informal register", "你" in later)

print("\n=== VIP grants Claude models (but not pricing clearance) ===")
LEAD, VIP_ONLY, PLAIN = "jcyi@streamax.com", "caojun@streamax.com", "nobody@streamax.com"
check("caojun is VIP", login.resolve_vip(VIP_ONLY))
check("caojun is NOT leadership", not login.resolve_leadership(VIP_ONLY))
check("leadership is implicitly VIP", login.resolve_vip(LEAD))
check("ordinary user is not VIP", not login.resolve_vip(PLAIN))

def models(who):
    return jerry_gpt._allowed_models(bool(login.resolve_leadership(who)),
                                     bool(login.resolve_vip(who)))
vip_models, plain_models = models(VIP_ONLY), models(PLAIN)
check("VIP can select Opus 5", "claude-opus-5" in vip_models.values(), str(vip_models))
check("VIP can select every model", len(vip_models) == len(jerry_gpt.MODEL_OPTIONS))
check("non-VIP gets DeepSeek only", set(plain_models.values()) == {jerry_gpt._deepseek_model()},
      str(plain_models))

# A menu entry without a key would just fail at request time.
def key_for(who):
    return jerry_gpt._resolve_provider_key(
        "anthropic", bool(login.resolve_leadership(who)), bool(login.resolve_vip(who)))[1]
jerry_gpt._get_api_key = lambda: "sk-test"
check("VIP actually resolves an org Anthropic key", key_for(VIP_ONLY) == "org")
check("leadership resolves an org key", key_for(LEAD) == "org")
check("non-VIP resolves NO Anthropic key", key_for(PLAIN) == "")

# The block embeds the user's own identifier, so normalise that out before
# comparing — what must match is the *clearance branch*, not the literal text.
check("VIP does NOT get leadership pricing clearance",
      clearance(VIP_ONLY).replace(VIP_ONLY, "U") == clearance(PLAIN).replace(PLAIN, "U"))
check("...and leadership's block genuinely differs from VIP's",
      clearance(LEAD).replace(LEAD, "U") != clearance(VIP_ONLY).replace(VIP_ONLY, "U"))

print("\n=== pricing clearance still gated by LEADERSHIP ===")
lead = clearance("jcyi@streamax.com")
plain = clearance("nobody@streamax.com")
check("leadership block differs from non-leadership", lead != plain)
check("non-leadership is told not to disclose pricing",
      "not" in plain.lower() and "pric" in plain.lower())

print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
