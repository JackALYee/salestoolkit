import streamlit as st
import smtplib
import ssl
import time

# Cookie-based session persistence — keeps the user signed in across page
# refreshes and ?view=jerry_gpt navigations. Optional: if the module isn't
# available, login still works for the lifetime of this tab.
try:
    import auth as _auth
except Exception:  # noqa: BLE001
    _auth = None


def _persist(user_name: str) -> None:
    """Write the auth cookie after a successful sign-in."""
    if _auth is not None:
        _auth.persist_login(user_name)


# --- LEADERSHIP — Streamax executives cleared for sensitive pricing data ----
# Edit this set to grant/revoke clearance for Streamax product pricing,
# margin, and cost-basis information inside Jerry GPT.
# All comparisons are case-insensitive; values stored lowercase.
LEADERSHIP_EMAILS = frozenset({
    "jerry@streamax.com",
    "hekun@streamax.com",
    "jcyi@streamax.com",
    "liheng@streamax.com",
    "melanie@streamax.com",
    "alan@streamax.com",
    "xdwang@streamax.com",
    "zjzhao@streamax.com",
    "liulei@streamax.com",
    "xbhu@streamax.com",
    "sunyan@streamax.com",
    "johnz@streamax.com",
})

# --- VIP — power users who can use Opus 4.8 (the most expensive model) -------
# Everyone in LEADERSHIP is automatically VIP. Add additional emails to
# EXTRA_VIP_EMAILS to grant Opus access without giving them full leadership
# pricing clearance. Edit this set to grow the VIP roster.
EXTRA_VIP_EMAILS = frozenset({
    "jhsun@streamax.com",      # Emily — 西南欧客户经理
    "caojun@streamax.com",     # Cao Jun
    "wangrui@streamax.com",    # Wang Rui — Jerry's real-life good friend (SPECIAL)
})

# Computed at module load: every user with VIP privileges.
VIP_EMAILS = LEADERSHIP_EMAILS | EXTRA_VIP_EMAILS

# Easter-egg auth shortcuts (jerry_test, hekun_test, etc.) authenticate as a
# display name. Map the display name back to the canonical streamax.com email
# so the leadership check works for the bypass accounts too.
_EASTER_EGG_TO_EMAIL = {
    "jerry": "jerry@streamax.com",
    "hekun": "hekun@streamax.com",
    "zntang": "zntang@streamax.com",
    "jhsun": "jhsun@streamax.com",
}


def resolve_leadership(name_or_email: str) -> bool:
    """Return True if the given user is in the Streamax LEADERSHIP list.

    Accepts either a streamax.com email (regular accounts) or a display name
    (Jerry/Hekun/etc. — used by the easter-egg bypass logins). Case-insensitive.
    """
    if not name_or_email:
        return False
    val = name_or_email.strip().lower()
    # If it's a known display name, swap to canonical email
    val = _EASTER_EGG_TO_EMAIL.get(val, val)
    return val in LEADERSHIP_EMAILS


def resolve_vip(name_or_email: str) -> bool:
    """Return True if the user is in the VIP list (Opus 4.8 access).

    VIP = LEADERSHIP ∪ EXTRA_VIP_EMAILS. Accepts emails or easter-egg display
    names. Case-insensitive. Same resolution logic as resolve_leadership.
    """
    if not name_or_email:
        return False
    val = name_or_email.strip().lower()
    val = _EASTER_EGG_TO_EMAIL.get(val, val)
    return val in VIP_EMAILS


def resolve_user_email(name_or_email: str) -> str:
    """Return the canonical streamax.com email for a user identity.

    Handles three cases:
    - The input is already an email (contains '@') → returned lowercased.
    - The input is a known easter-egg display name (Jerry/Hekun/ZNTang/JHSun)
      → mapped via _EASTER_EGG_TO_EMAIL.
    - Anything else → empty string (caller should treat as "unknown").

    Used by auth.restore_session() so a cookie-restored user_name can
    re-derive user_email after a page reload — without that, jhsun-only
    customizations vanish whenever the tab is refreshed.
    """
    if not name_or_email:
        return ""
    val = name_or_email.strip().lower()
    if "@" in val:
        return val
    return _EASTER_EGG_TO_EMAIL.get(val, "")


# --- SPECIAL RELATIONSHIPS — Jerry's self + inner circle ---------------------
# These accounts receive a personalized first-message greeting and are
# addressed as 你 (informal) instead of 您, regardless of LEADERSHIP status.
# `kind` is the relationship type the prompt switches on; `name` is the
# real-life name surfaced inside the prompt so Jerry knows WHO he's seeing.
SPECIAL_RELATIONSHIPS = {
    "jerry@streamax.com":  {"kind": "self",       "name": "Jerry himself (the human you are based on)"},
    "hekun@streamax.com":  {"kind": "best_buddy", "name": "Kun He (real-life best buddy)"},
    "wangrui@streamax.com": {"kind": "best_buddy", "name": "Rui Wang (real-life good friend)"},
}


def resolve_special_relationship(name_or_email: str) -> dict | None:
    """Return the SPECIAL_RELATIONSHIPS entry if the user matches, else None.

    Accepts emails or easter-egg display names (Jerry/Hekun) — same
    resolution logic as `resolve_leadership`. Case-insensitive.
    """
    if not name_or_email:
        return None
    val = name_or_email.strip().lower()
    val = _EASTER_EGG_TO_EMAIL.get(val, val)
    return SPECIAL_RELATIONSHIPS.get(val)


def _grant_leadership(name_or_email: str) -> None:
    """Set session_state['is_leadership'] for the just-authenticated user."""
    st.session_state["is_leadership"] = resolve_leadership(name_or_email)


def _grant_vip(name_or_email: str) -> None:
    """Set session_state['is_vip'] for the just-authenticated user.

    Called from every login branch alongside _grant_leadership so VIP status
    is available immediately on first render. VIP = LEADERSHIP ∪ EXTRA_VIP.
    """
    st.session_state["is_vip"] = resolve_vip(name_or_email)

def verify_streamax_credentials(email, password):
    # 1. 自动清除首尾的隐藏空格，并转为小写用于校验
    clean_email = email.strip()
    email_lower = clean_email.lower()
    
    # Test Easter Egg Overrides and Bypass
    if email_lower == "jerry_test" and password == "testme":
        return True, "Jerry"
    if email_lower == "hekun_test" and password == "testme":
        return True, "Hekun"
    if email_lower == "zntang_test" and password == "testme":
        return True, "ZNTang"
    if email_lower == "jhsun_test" and password == "testme":
        return True, "JHSun"
    if email_lower == "test_account" and password == "testme":
        return True, "Success"
        
    # 2. 使用全小写的 email_lower 来做后缀检查，避免大小写导致报错
    if not email_lower.endswith("@streamax.com"):
        return False, "Please provide a valid @streamax.com email address."
    if not password:
        return False, "Password cannot be empty."
    
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("mail.streamax.com", 465, timeout=10, context=context)
        # 3. 使用清除过空格的 clean_email 发送给服务器进行验证
        server.login(clean_email, password)
        server.quit()
        
        # Special Easter Egg Logins (Must pass real SMTP Auth first!)
        if email_lower == "jerry@streamax.com":
            return True, "Jerry"
        elif email_lower == "hekun@streamax.com":
            return True, "Hekun"
        elif email_lower == "zntang@streamax.com":
            return True, "ZNTang"
        elif email_lower == "jhsun@streamax.com":
            return True, "JHSun"
            
        return True, "Success"
    except smtplib.SMTPAuthenticationError:
        return False, "Email or password incorrect."
    except Exception as e:
        if '535' in str(e) or 'authentication failed' in str(e).lower():
            return False, "Email or password incorrect."
        else:
            return False, f"Could not connect to the mail server: {str(e)}"

def render_login():
    # Inject Login Screen Specific CSS
    st.markdown(
        """
        <style>
        /* Login Screen Specific CSS (matches the toolkit theme) */
        .stApp {
            background-color: #050810;
            background-image: radial-gradient(circle at 50% -20%, #0B1221, #050810);
        }
        /* --- Bulletproof input dark mode --------------------------------------
           Paints EVERY wrapper layer dark (Streamlit + BaseWeb add several),
           defeats Windows Forced Colors / High Contrast mode via
           `forced-color-adjust: none`, and uses `color-scheme: dark` so
           browsers don't apply light-mode UA defaults. Autofill is overridden
           via `-webkit-text-fill-color` + a massive inset box-shadow. */
        [data-testid="stTextInput"],
        [data-testid="stTextInput"] > div,
        [data-testid="stTextInput"] > div > div,
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="base-input"] {
            background: rgba(20, 25, 40, 0.85) !important;
            background-color: rgba(20, 25, 40, 0.85) !important;
            background-image: none !important;
            color-scheme: dark !important;
            forced-color-adjust: none !important;
            border-radius: 8px !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"],
        [data-testid="stTextInput"] [data-baseweb="base-input"] {
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        [data-testid="stTextInput"] input {
            background: transparent !important;
            background-color: transparent !important;
            background-image: none !important;
            color: #2AF598 !important;
            -webkit-text-fill-color: #2AF598 !important;
            caret-color: #2AF598 !important;
            color-scheme: dark !important;
            forced-color-adjust: none !important;
        }
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
            border-color: #2AF598 !important;
            box-shadow: 0 0 0 1px #2AF598 !important;
            outline: none !important;
        }
        [data-testid="stTextInput"] input::placeholder {
            color: rgba(160, 174, 192, 0.55) !important;
            -webkit-text-fill-color: rgba(160, 174, 192, 0.55) !important;
            opacity: 1 !important;
        }
        /* Defeat Chrome/Safari/Edge autofill repaint */
        [data-testid="stTextInput"] input:-webkit-autofill,
        [data-testid="stTextInput"] input:-webkit-autofill:hover,
        [data-testid="stTextInput"] input:-webkit-autofill:focus,
        [data-testid="stTextInput"] input:-webkit-autofill:active {
            -webkit-text-fill-color: #2AF598 !important;
            -webkit-box-shadow: 0 0 0 1000px rgba(20, 25, 40, 0.95) inset !important;
            caret-color: #2AF598 !important;
            transition: background-color 5000s ease-in-out 0s;
        }
        .stTextInput label,
        [data-testid="stTextInput"] label {
            color: #A0AEC0 !important;
        }
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 30px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .stButton>button {
            background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%) !important;
            color: #050810 !important;
            font-weight: 700 !important;
            border: none;
            border-radius: 8px;
            width: 100%;
            padding: 0.6rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 4px 15px rgba(42, 245, 152, 0.4);
            transform: translateY(-2px);
        }
        
        /* Mascot Animation for Login Screen */
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-12px); } }
        .login-mascot { 
            animation: float 4s ease-in-out infinite; 
            filter: drop-shadow(0 15px 20px rgba(42, 245, 152, 0.15)); 
        }
        
        /* Jumping Heart Animation */
        @keyframes heartBounce { 0% { transform: translateY(0) scale(1); } 100% { transform: translateY(-20px) scale(1.15); } }
        .jumping-heart { 
            animation: heartBounce 0.4s infinite alternate cubic-bezier(0.5, 0.05, 1, 0.5); 
        }
        
        /* Pulsing Text Animation for Loading */
        @keyframes pulseText {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .loading-text {
            animation: pulseText 1.5s infinite ease-in-out;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    # 1. Jerry Animation
    if st.session_state.get('show_jerry_anim', False):
        img_src = "https://drive.google.com/thumbnail?id=1yoXi043RnGn4ZDhtJGYXM3n2Z9tFiXMJ&sz=w800"
            
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src='{img_src}' onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6);'>
                <div class='loading-text' style='display: none; width: 90%; max-width: 450px; height: 300px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); color: #2AF598; font-size: 2rem; align-items: center; justify-content: center; font-weight: bold; font-family: "Inter", sans-serif; letter-spacing: 1px;'>Drawing...</div>
                <h2 style='color: #2AF598; margin-top: 30px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>你的数字分身已上线！</h2>
                <p class='loading-text' style='color: #A0AEC0; font-size: 1rem; margin-top: 10px;'>Logging in...</p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_jerry_anim'] = False
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = 'Jerry'
        _grant_leadership('Jerry')
        _grant_vip('Jerry')
        _persist('Jerry')
        st.rerun()

    # 2. Hekun Animation
    elif st.session_state.get('show_hekun_anim', False):
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <div class='jumping-heart' style='font-size: 120px; line-height: 1; filter: drop-shadow(0 10px 25px rgba(42, 245, 152, 0.6)); text-shadow: 0 0 10px #2AF598;'>💰</div>
                <h2 style='color: #2AF598; margin-top: 40px; font-weight: 700; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.4);'>130,885万元，tmd干就完了</h2>
                <p class='loading-text' style='color: #A0AEC0; font-size: 1rem; margin-top: 10px;'>Logging in...</p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_hekun_anim'] = False
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = 'Hekun'
        _grant_leadership('Hekun')
        _grant_vip('Hekun')
        _persist('Hekun')
        st.rerun()

    # 3. ZNTang Animation (Easter Egg)
    elif st.session_state.get('show_zntang_anim', False):
        img_src = "https://drive.google.com/thumbnail?id=1yoXi043RnGn4ZDhtJGYXM3n2Z9tFiXMJ&sz=w800"
            
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src='{img_src}' onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6);'>
                <div class='loading-text' style='display: none; width: 90%; max-width: 450px; height: 300px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); color: #2AF598; font-size: 2rem; align-items: center; justify-content: center; font-weight: bold; font-family: "Inter", sans-serif; letter-spacing: 1px;'>Drawing...</div>
                <h2 style='color: #2AF598; margin-top: 30px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>今年一个亿，明年三个亿，后年上市</h2>
                <p class='loading-text' style='color: #A0AEC0; font-size: 1rem; margin-top: 10px;'>Logging in...</p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_zntang_anim'] = False
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = 'ZNTang'
        _grant_leadership('ZNTang')
        _grant_vip('ZNTang')
        _persist('ZNTang')
        st.rerun()

    # 4. JHSun Animation (Easter Egg)
    elif st.session_state.get('show_jhsun_anim', False):
        img_src = "https://drive.google.com/thumbnail?id=1MbhoRTe86qcO9Q0GNeJ9DPPYeuYLn4DG&sz=w800"
            
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src='{img_src}' onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6);'>
                <div class='loading-text' style='display: none; width: 90%; max-width: 450px; height: 300px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); color: #2AF598; font-size: 2rem; align-items: center; justify-content: center; font-weight: bold; font-family: "Inter", sans-serif; letter-spacing: 1px;'>Drawing...</div>
                <h2 style='color: #2AF598; margin-top: 30px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3); text-align: center; max-width: 700px; line-height: 1.4;'>Congratulations to your new position! 🎉<br><span style='font-size: 1.1rem; font-weight: 500; color: #E0E6ED;'>As promised, no matter which sales market you are fighting for, we will support and empower you.</span></h2>
                <p class='loading-text' style='color: #A0AEC0; font-size: 1rem; margin-top: 10px;'>Logging in...</p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(12)
        st.session_state['show_jhsun_anim'] = False
        st.session_state['authenticated'] = True
        st.session_state['user_name'] = 'JHSun'
        # Normalize user_email so downstream jhsun-only customizations
        # (Global Trucking title, Emily entry, Jack GPT route) work even
        # when the user authenticated via the jhsun_test shortcut.
        st.session_state['user_email'] = 'jhsun@streamax.com'
        _grant_leadership('JHSun')
        _grant_vip('JHSun')
        _persist('JHSun')
        st.rerun()

    # Show Standard Form View
    else:
        st.write("<br><br>", unsafe_allow_html=True) # Vertical spacing
        
        st.markdown("""
            <div style='display: flex; justify-content: center; margin-bottom: 10px;'>
                <img src='https://drive.google.com/thumbnail?id=1bXf5psHrw4LOk0oMAkTJRL15_mLCabad&sz=w500' alt='Streamax Mascot' class='login-mascot' style='width: 150px; height: 150px; object-fit: contain;'>
            </div>
            <h1 style='text-align: center; color: white; font-size: 3rem; margin-bottom: 0; line-height: 1.2;'>
                <span style='background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Streamax</span> Sales Toolkit
            </h1>
            <p style='text-align: center; color: #A0AEC0; font-size: 1.1rem; margin-bottom: 40px;'>
                Secure Access • Trucking Division
            </p>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            with st.form("login_form"):
                email_input = st.text_input("Streamax Email", placeholder="name@streamax.com")
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                st.write("<br>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("Authenticate")
                
                if submit_btn:
                    with st.spinner("Connecting to Streamax secure server..."):
                        is_valid, message = verify_streamax_credentials(email_input, pass_input)
                        
                    if is_valid:
                        # SAVING CREDENTIALS TO BE USED LATER IN THE DRIP MAILER!
                        st.session_state['user_email'] = email_input
                        st.session_state['user_password'] = pass_input
                        st.session_state['auth_mode'] = message
                        
                        # Trigger appropriate transition animation state
                        if message == "Jerry":
                            st.session_state['show_jerry_anim'] = True
                            st.rerun()
                        elif message == "Hekun":
                            st.session_state['show_hekun_anim'] = True
                            st.rerun()
                        elif message == "ZNTang":
                            st.session_state['show_zntang_anim'] = True
                            st.rerun()
                        elif message == "JHSun":
                            st.session_state['show_jhsun_anim'] = True
                            st.rerun()
                        else:
                            st.session_state['authenticated'] = True
                            st.session_state['user_name'] = email_input
                            _grant_leadership(email_input)
                            _grant_vip(email_input)
                            _persist(email_input)
                            st.rerun()
                    else:
                        st.error(message)
