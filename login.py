import streamlit as st
import smtplib
import ssl
import time
import base64
import os

def verify_streamax_credentials(email, password):
    # Master Override
    if email == "jackishandome" and password == "iagree":
        return True, "Master"
        
    # Test Easter Egg Overrides
    if email == "jerry_test" and password == "testme":
        return True, "Jerry"
    if email == "hekun_test" and password == "testme":
        return True, "Hekun"
        
    if not email.endswith("@streamax.com"):
        return False, "Please provide a valid @streamax.com email address."
    if not password:
        return False, "Password cannot be empty."
    
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL("mail.streamax.com", 465, timeout=10, context=context)
        server.login(email, password)
        server.quit()
        
        # Special Easter Egg Logins (Must pass real SMTP Auth first!)
        email_lower = email.lower()
        if email_lower == "jerry@streamax.com":
            return True, "Jerry"
        elif email_lower == "hekun@streamax.com":
            return True, "Hekun"
            
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
        
        /* Jumping Heart Animation for Master Login */
        @keyframes heartBounce { 0% { transform: translateY(0) scale(1); } 100% { transform: translateY(-20px) scale(1.15); } }
        .jumping-heart { 
            animation: heartBounce 0.4s infinite alternate cubic-bezier(0.5, 0.05, 1, 0.5); 
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 1. Master Override Animation
    if st.session_state.get('show_master_anim', False):
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src='data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23ff3366"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>' class='jumping-heart' style='width: 140px; height: 140px;'>
                <h2 style='color: #2AF598; margin-top: 30px; font-weight: 400; font-family: "Inter", sans-serif;'>Logging you in...</h2>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_master_anim'] = False
        st.session_state['authenticated'] = True
        st.rerun()
        
    # 2. Jerry Animation
    elif st.session_state.get('show_jerry_anim', False):
        img_src = "https://drive.google.com/thumbnail?id=15rtoKfYyO3Ep6VIlwPuwKOuJjFwsfvlT&sz=w800"
            
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <img src='{img_src}' class='login-mascot' style='max-width: 450px; width: 90%; height: auto; border-radius: 12px; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 15px 40px rgba(0,0,0,0.6);'>
                <h2 style='color: #2AF598; margin-top: 30px; font-weight: 600; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.3);'>欢迎老大检阅销售Toolkit</h2>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_jerry_anim'] = False
        st.session_state['authenticated'] = True
        st.rerun()

    # 3. Hekun Animation
    elif st.session_state.get('show_hekun_anim', False):
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                <div class='jumping-heart' style='font-size: 120px; line-height: 1; filter: drop-shadow(0 10px 25px rgba(42, 245, 152, 0.6)); text-shadow: 0 0 10px #2AF598;'>💰</div>
                <h2 style='color: #2AF598; margin-top: 40px; font-weight: 700; font-family: "Inter", sans-serif; text-shadow: 0 2px 10px rgba(42, 245, 152, 0.4);'>130,885万元，tmd干就完了</h2>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(8)
        st.session_state['show_hekun_anim'] = False
        st.session_state['authenticated'] = True
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
                        st.session_state['user_email'] = email_input
                        
                        # Trigger appropriate transition animation state
                        if message == "Master":
                            st.session_state['show_master_anim'] = True
                            st.rerun()
                        elif message == "Jerry":
                            st.session_state['show_jerry_anim'] = True
                            st.rerun()
                        elif message == "Hekun":
                            st.session_state['show_hekun_anim'] = True
                            st.rerun()
                        else:
                            st.session_state['authenticated'] = True
                            st.rerun()
                    else:
                        st.error(message)
