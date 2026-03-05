import streamlit as st
import smtplib
import ssl
import time

def verify_streamax_credentials(email, password):
    email_lower = email.lower()
    
    # Test Easter Egg Overrides (including generic C-Suite tests)
    test_accounts = {
        "jerry_test": "Jerry",
        "hekun_test": "Hekun",
        "zntang_test": "ZNTang",
        "liheng_test": "C_Suite",
        "xdwang_test": "C_Suite",
        "alan_test": "C_Suite",
        "melanie_test": "C_Suite",
        "zjzhao_test": "C_Suite"
    }
    
    if email_lower in test_accounts and password == "testme":
        return True, test_accounts[email_lower]
        
    if not email_lower.endswith("@streamax.com"):
        return False, "Please provide a valid @streamax.com email address."
    if not password:
        return False, "Password cannot be empty."
    
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("mail.streamax.com", 465, timeout=10, context=context)
        server.login(email_lower, password)
        server.quit()
        
        # C-Suites Directory Mapping
        c_suites_directory = {
            "jerry@streamax.com": "Jerry",
            "hekun@streamax.com": "Hekun",
            "zntang@streamax.com": "ZNTang",
            "liheng@streamax.com": "C_Suite",
            "xdwang@streamax.com": "C_Suite",
            "alan@streamax.com": "C_Suite",
            "melanie@streamax.com": "C_Suite",
            "zjzhao@streamax.com": "C_Suite"
        }
        
        if email_lower in c_suites_directory:
            return True, c_suites_directory[email_lower]
            
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
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.05);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #2AF598;
            box-shadow: 0 0 0 1px #2AF598;
        }
        .stTextInput label {
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
        
    # --- C-SUITE ANIMATION HANDLER ---
    csuite_mode = st.session_state.get('show_csuite_anim', False)
    
    if csuite_mode:
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        
        # Reusable C-Suite Badge and Loading Text
        gaoguan_badge = "<div style='background: linear-gradient(135deg, #FFD700 0%, #F7971E 100%); color: #050810; padding: 6px 16px; border-radius: 30px; font-weight: 800; font-size: 0.9rem; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4); display: inline-flex; align-items: center; letter-spacing: 1px;'><span style='font-size: 1.1rem; margin-right: 6px;'></span> 高管权限登陆</div>"
        logging_in_text = "<p class='loading-text' style='color: #A0AEC0; font-size: 1rem; margin-top: 15px;'>Logging in...</p>"
        
        if csuite_mode == "Jerry":
            img_src = "https://drive.google.com/thumbnail?id=1yoXi043RnGn4ZDhtJGYXM3n2Z9tFiXMJ&sz=w800"
            content_html = f"""
                <img src='{img_src}' onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6); margin-bottom: 25px;'>
                <div class='loading-text' style='display: none; width: 90%; max-width: 450px; height: 300px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); color: #2AF598; font-size: 2rem; align-items: center; justify-content: center; font-weight: bold; font-family: "Inter", sans-serif; letter-spacing: 1px; margin-bottom: 25px;'>Drawing...</div>
                {gaoguan_badge}
                <h2 style='color: #2AF598; margin-top: 5px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>欢迎老大检阅销售Toolkit</h2>
            """
        elif csuite_mode == "Hekun":
            content_html = f"""
                <div class='jumping-heart' style='font-size: 120px; line-height: 1; filter: drop-shadow(0 10px 25px rgba(42, 245, 152, 0.6)); text-shadow: 0 0 10px #2AF598; margin-bottom: 35px;'>💰</div>
                {gaoguan_badge}
                <h2 style='color: #2AF598; margin-top: 5px; font-weight: 700; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.4);'>130,885万元，tmd干就完了</h2>
            """
        elif csuite_mode == "ZNTang":
            img_src = "https://drive.google.com/thumbnail?id=1yoXi043RnGn4ZDhtJGYXM3n2Z9tFiXMJ&sz=w800"
            content_html = f"""
                <img src='{img_src}' onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6); margin-bottom: 25px;'>
                <div class='loading-text' style='display: none; width: 90%; max-width: 450px; height: 300px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2); color: #2AF598; font-size: 2rem; align-items: center; justify-content: center; font-weight: bold; font-family: "Inter", sans-serif; letter-spacing: 1px; margin-bottom: 25px;'>Drawing...</div>
                {gaoguan_badge}
                <h2 style='color: #2AF598; margin-top: 5px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>今年一个亿，明年三个亿，后年上市</h2>
            """
        else:
            # Generic C-Suite Welcome
            content_html = f"""
                <div style='font-size: 80px; margin-bottom: 25px; filter: drop-shadow(0 10px 25px rgba(255, 215, 0, 0.3));'>🏢</div>
                {gaoguan_badge}
                <h2 style='color: #2AF598; margin-top: 5px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>欢迎高管检阅销售Toolkit</h2>
            """
            
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                {content_html}
                {logging_in_text}
            </div>
        """, unsafe_allow_html=True)
        
        # All C-Suite members get the 8-second animation
        time.sleep(8)
        st.session_state['show_csuite_anim'] = False
        st.session_state['authenticated'] = True
        st.rerun()

    # --- Standard Form View ---
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
                        st.session_state['user_email'] = email_input
                        st.session_state['user_password'] = pass_input
                        st.session_state['auth_mode'] = message
                        
                        # Check if returned message indicates any C-Suite role
                        if message in ["Jerry", "Hekun", "ZNTang", "C_Suite"]:
                            st.session_state['show_csuite_anim'] = message
                            st.rerun()
                        else:
                            st.session_state['authenticated'] = True
                            st.rerun()
                    else:
                        st.error(message)
