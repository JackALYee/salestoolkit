import streamlit as st
import streamlit.components.v1 as components
import smtplib
import ssl
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid

# Import modular components
from login import render_login
from streamaxpedia_app import content as streamaxpedia_content
from prospecting_flow import content as prospecting_flow_content
from discovery_meeting import content as discovery_meeting_content
from presentation import content as presentation_content
from value_calculator import content as value_calculator_content
from dripmailer import content as dripmailer_content

# --- SMTP PYTHON HELPERS ---
def render_template(template_str, row):
    def replace_var(match):
        key = match.group(1).lower().strip()
        val = row.get(key, "")
        return str(val) if val else f"[{match.group(1)}]"
    return re.sub(r'\{([^}]+)\}', replace_var, template_str)

def create_message(subject, html_body, to_addr, from_name, from_email):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    return msg

# --- CONFIG & LAYOUT ---
st.set_page_config(
    page_title="Streamax Sales Toolkit | Aurora Flow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        margin: 0rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #050810;
        background-image: radial-gradient(circle at 50% -20%, #0B1221, #050810);
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- RENDER LOGIN OR TOOLKIT ---
if not st.session_state['authenticated']:
    render_login()
else:
    # 1. HTML Head & CSS (unchanged original layout + Streamlit JS Bridge added)
    html_head = r"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Streamax Sales Toolkit | Aurora Flow</title>
        
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
        <script src="https://unpkg.com/lucide@latest"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        
        <!-- IMPORT STREAMLIT COMPONENT LIB TO BRIDGE HTML TO PYTHON FOR EMAILS -->
        <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.3.0/dist/streamlit.js"></script>
        
        <script>
            window.MathJax = {
                loader: {load: ['[tex]/html']},
                tex: { packages: {'[+]': ['html']}, inlineMath: [['$', '$'], ['\\(', '\\)']], displayMath: [['$$', '$$'], ['\\[', '\\]']] },
                chtml: { scale: 0.9 }
            };
        </script>
        <script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

        <style>
            :root {
                --bg-deep: #050810;
                --bg-gradient: radial-gradient(circle at 50% -20%, #0B1221, #050810);
                --primary-green: #2AF598;
                --secondary-blue: #009EFD;
                --text-white: #FFFFFF;
                --text-grey: #A0AEC0;
                --glass-bg: rgba(255, 255, 255, 0.03);
                --glass-border: 1px solid rgba(255, 255, 255, 0.08);
                --card-radius: 16px;
                --font-main: 'Inter', 'Roboto', sans-serif;
                --glow-shadow: 0 0 20px rgba(42, 245, 152, 0.15);
                --gradient-text: linear-gradient(135deg, var(--primary-green) 0%, var(--secondary-blue) 100%);
                --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background-color: var(--bg-deep);
                background-image: var(--bg-gradient);
                font-family: var(--font-main);
                color: var(--text-white);
                line-height: 1.6;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }
            body::before {
                content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
                background-size: 50px 50px; opacity: 0.05; z-index: -1; pointer-events: none;
            }
            h1, h2, h3, h4, h5 { font-weight: 700; margin-bottom: 1rem; color: var(--text-white); }
            .gradient-text { background: var(--gradient-text); -webkit-background-clip: text; background-clip: text; color: transparent; display: inline-block; }
            p { color: var(--text-grey); margin-bottom: 1rem; }
            strong { color: var(--text-white); }
            ul, ol { color: var(--text-grey); padding-left: 20px; margin-bottom: 1rem; }
            li { margin-bottom: 8px; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; position: relative; }
            header { text-align: center; padding: 60px 0 40px; animation: fadeInDown 1s ease-out; }
            .header-subtitle { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; color: var(--primary-green); margin-bottom: 10px; }
            .header-meta { margin-top: 10px; font-size: 0.85rem; color: var(--text-grey); opacity: 0.7; }
            
            .nav-tabs { display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; flex-wrap: wrap; }
            .nav-btn { background: rgba(255, 255, 255, 0.05); border: var(--glass-border); color: var(--text-grey); padding: 12px 30px; border-radius: 30px; cursor: pointer; font-weight: 600; transition: var(--transition); backdrop-filter: blur(5px); font-family: var(--font-main); display: flex; align-items: center; gap: 8px; }
            .nav-btn:hover { background: rgba(255, 255, 255, 0.1); color: var(--text-white); transform: translateY(-2px); }
            .nav-btn.active { background: rgba(42, 245, 152, 0.1); border-color: var(--primary-green); color: var(--primary-green); box-shadow: var(--glow-shadow); }
            
            .card { background: var(--glass-bg); border: var(--glass-border); border-radius: var(--card-radius); padding: 30px; margin-bottom: 24px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); transition: var(--transition); position: relative; overflow: hidden; }
            .card:hover { border-color: rgba(42, 245, 152, 0.3); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); transform: translateY(-3px); }
            .section-header { margin-top: 40px; margin-bottom: 20px; border-left: 4px solid var(--primary-green); padding-left: 15px; font-size: 1.5rem; }
            .section-header.blue { border-color: var(--secondary-blue); }
            .fade-up { opacity: 0; transform: translateY(30px); transition: opacity 0.8s ease-out, transform 0.8s ease-out; }
            .fade-up.visible { opacity: 1; transform: translateY(0); }
            @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

            .script-box { background: rgba(0, 0, 0, 0.3); border-left: 3px solid var(--secondary-blue); padding: 20px; border-radius: 0 8px 8px 0; margin: 20px 0; position: relative; font-style: italic; }
            .script-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
            .script-tag { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--secondary-blue); font-weight: bold; }
            .copy-btn { background: transparent; border: 1px solid var(--text-grey); color: var(--text-grey); padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: var(--transition); display: flex; align-items: center; gap: 5px; }
            .copy-btn:hover { border-color: var(--primary-green); color: var(--primary-green); }
            .list-card-content { margin-left: 0; }
            .list-card-content li { margin-bottom: 12px; }
            .icp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .nested-list { margin-top: 5px; margin-left: 20px; margin-bottom: 15px; list-style-type: circle; }
            .category-title { color: var(--text-white); font-weight: 600; margin-top: 15px; margin-bottom: 5px; display: block; }
            .loop-step { margin-bottom: 20px; }
            .loop-step h5 { color: var(--secondary-blue); margin-bottom: 5px; font-size: 1.05rem; }
            .phase-title { color: var(--primary-green); text-transform: uppercase; font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 15px; border-bottom: 1px solid rgba(42, 245, 152, 0.3); padding-bottom: 8px; }

            .flow-container { border-left: 2px solid rgba(255, 255, 255, 0.1); margin-left: 10px; padding-left: 30px; position: relative; }
            .flow-step-block { position: relative; margin-bottom: 60px; }
            .flow-marker { position: absolute; left: -41px; top: 0; width: 20px; height: 20px; background: var(--bg-deep); border: 2px solid var(--primary-green); border-radius: 50%; box-shadow: 0 0 10px rgba(42, 245, 152, 0.3); display: flex; justify-content: center; align-items: center; font-size: 0.7rem; color: var(--primary-green); font-weight: bold; z-index: 2; }
            .flow-marker.blue { border-color: var(--secondary-blue); color: var(--secondary-blue); box-shadow: 0 0 10px rgba(0, 158, 253, 0.3); }
            .flow-title { font-size: 1.3rem; font-weight: 700; color: var(--text-white); margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
            .flow-subtitle { font-size: 0.9rem; color: var(--text-grey); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; display: block; }

            .sub-nav-tabs { display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
            .sub-nav-btn { background: transparent; border: none; color: var(--text-grey); font-size: 1rem; font-weight: 600; cursor: pointer; padding: 8px 16px; position: relative; transition: var(--transition); display: flex; align-items: center; gap: 8px;}
            .sub-nav-btn:hover { color: var(--text-white); }
            .sub-nav-btn.active { color: var(--primary-green); }
            .sub-nav-btn.active::after { content: ''; position: absolute; bottom: -11px; left: 0; width: 100%; height: 2px; background: var(--primary-green); box-shadow: 0 0 10px var(--primary-green); }
            .sub-content { display: none; }
            .sub-content.active { display: block; }

            #toast { visibility: hidden; min-width: 250px; background-color: var(--primary-green); color: #050810; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1000; left: 50%; bottom: 30px; transform: translateX(-50%); font-weight: bold; box-shadow: 0 0 20px rgba(42, 245, 152, 0.4); opacity: 0; transition: opacity 0.3s; }
            #toast.show { visibility: visible; opacity: 1; }
            .hidden { display: none !important; }
            
            /* Various Layout Classes (Calculators/Visuals) */
            .glass-panel { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; }
            .tooltip-bg { background: rgba(10, 15, 25, 0.95); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); }
            .tooltip-arrow-border { border-top-color: rgba(255, 255, 255, 0.1); }
            .highlighted-var { background-color: rgba(42, 245, 152, 0.15) !important; color: var(--primary-green) !important; border-radius: 4px; padding: 0.1rem 0.2rem; text-shadow: 0 0 8px var(--primary-green); border: 1px solid rgba(42, 245, 152, 0.4); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
            mjx-container { color: var(--text-white) !important; }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-subtitle fade-up">Streamax Sales Toolkit</div>
                <h1 class="fade-up" style="font-size: 3rem; line-height: 1.1;">
                    <span class="gradient-text">North America</span><br>
                    <span style="font-weight: 300;">Trucking Division</span>
                </h1>
                <div class="header-meta fade-up">Version 1.0 • Trucking BU • Jan 2026</div>
            </div>
        </header>

        <div class="container">
            <!-- Global HTML Navigation -->
            <nav class="nav-tabs fade-up">
                <button class="nav-btn" onclick="window.open('https://streamaxpedia.streamlit.app/?q=ad+plus', '_blank')">
                    <i data-lucide="book-open"></i> Streamaxpedia
                </button>
                <button class="nav-btn active" onclick="switchTab('prospecting-flow', this)">
                    <i data-lucide="git-merge"></i> Prospecting Flow
                </button>
                <button class="nav-btn" onclick="switchTab('discovery', this)">
                    <i data-lucide="search"></i> Discovery Meeting
                </button>
                <button class="nav-btn" onclick="switchTab('presentation', this)">
                    <i data-lucide="monitor-play"></i> Presentation
                </button>
                <button class="nav-btn" onclick="switchTab('value-calculator', this)">
                    <i data-lucide="calculator"></i> Value Calculator
                </button>
                <!-- Drip Mailer linked natively in the HTML -->
                <button class="nav-btn" onclick="switchTab('dripmailer', this)">
                    <i data-lucide="mail"></i> Email Tool
                </button>
            </nav>
    """

    # Base HTML closing tags + Original Logic
    html_tail = r"""
            <div style="height: 100px;"></div>
        </div>

        <div id="toast">Copied to Clipboard!</div>

        <script>
            // --- Initialize Streamlit Bridge ---
            function onRender(event) {
                Streamlit.setFrameHeight(1800);
            }
            Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
            Streamlit.setComponentReady();
            setInterval(() => { Streamlit.setFrameHeight(1800); }, 1000);

            // --- ICONS INITIALIZATION ---
            lucide.createIcons();

            function switchTab(tabId, btnElement) {
                document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
                if (btnElement) btnElement.classList.add('active');

                document.querySelectorAll('.content-section').forEach(section => section.classList.add('hidden'));
                const activeSection = document.getElementById(tabId);
                if (activeSection) {
                    activeSection.classList.remove('hidden');
                    const elements = activeSection.querySelectorAll('.fade-up');
                    elements.forEach(el => {
                        el.classList.remove('visible');
                        setTimeout(() => el.classList.add('visible'), 50);
                    });
                    observeElements(); 

                    if (tabId === 'value-calculator' && window.MathJax && MathJax.typesetPromise) {
                        MathJax.typesetPromise();
                    }
                }
            }

            function switchSubTab(tabId, element) {
                const subNavs = element.closest('.sub-nav-tabs').querySelectorAll('.sub-nav-btn');
                subNavs.forEach(btn => btn.classList.remove('active'));
                element.classList.add('active');

                const parentSection = element.closest('.content-section');
                parentSection.querySelectorAll('.sub-content').forEach(content => {
                    content.classList.remove('active');
                });
                const activeSub = document.getElementById(tabId);
                if(activeSub) {
                    activeSub.classList.add('active');
                    activeSub.querySelectorAll('.fade-up').forEach(el => {
                        el.classList.remove('visible');
                        setTimeout(() => el.classList.add('visible'), 50);
                    });
                    observeElements();

                    if ((tabId === 'tco-calc' || tabId === 'ifta-calc') && window.MathJax && MathJax.typesetPromise) {
                        MathJax.typesetPromise();
                    }
                }
            }

            function copyText(btnElement) {
                const textToCopy = btnElement.closest('.script-header').nextElementSibling.innerText;
                document.execCommand('copy'); // iFrame safety 
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const toast = document.getElementById("toast");
                    toast.className = "show";
                    setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
                }).catch(err => {
                    const textArea = document.createElement("textarea");
                    textArea.value = textToCopy;
                    document.body.appendChild(textArea);
                    textArea.select();
                    try { document.execCommand('copy'); const toast = document.getElementById("toast"); toast.className = "show"; setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000); } catch (err) {}
                    document.body.removeChild(textArea);
                });
            }

            function observeElements() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
                }, { threshold: 0.1 });
                document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));
            }

            document.addEventListener('DOMContentLoaded', () => {
                observeElements();
                setTimeout(() => { document.querySelectorAll('#prospecting-flow .fade-up').forEach(el => el.classList.add('visible')); }, 100);
                if (typeof initLoopVisual === 'function') initLoopVisual();
                if (typeof calculateROI === 'function') calculateROI();
                if (typeof initIfta === 'function') initIfta();
            });
        </script>
    </body>
    </html>
    """

    # Fetch variables to inject into the Drip Mailer Javascript
    current_email = st.session_state.get('user_email', 'your.email@streamax.com')
    auth_mode = st.session_state.get('auth_mode', 'Success')
    
    customized_dripmailer = dripmailer_content.replace("__USER_EMAIL__", current_email).replace("__AUTH_MODE__", auth_mode)

    # 2. ASSEMBLE HTML
    html_code = (
        html_head + "\n" +
        streamaxpedia_content + "\n" +
        prospecting_flow_content + "\n" +
        discovery_meeting_content + "\n" +
        presentation_content + "\n" +
        value_calculator_content + "\n" +
        customized_dripmailer + "\n" +
        html_tail
    )

    # 3. DECLARE AS CUSTOM COMPONENT 
    # This replaces components.html() and establishes a secure bridge.
    # The HTML 'Send' button now securely fires its payload back to this Python file!
    ToolkitComponent = components.declare_component("streamax_toolkit", html=html_code)
    
    # 4. RENDER & CAPTURE
    result = ToolkitComponent(key="main_toolkit")

    # 5. PYTHON SMTP PROCESSOR
    # When the Javascript sends back the 'send_batch' payload, Python catches it and handles the real sending.
    if result and isinstance(result, dict) and result.get("action") == "send_batch":
        csv_data = result.get("csvData", [])
        subj_tmpl = result.get("subjectTemplate", "")
        body_tmpl = result.get("bodyTemplate", "")
        sig_html = result.get("sigHtml", "")
        sig_name = result.get("sigName", "Streamax Sales")
        
        user_email = st.session_state.get('user_email')
        user_pass = st.session_state.get('user_password')
        
        if not user_email or not user_pass:
            st.error("Missing secure credentials. Please refresh the page and re-authenticate on the login screen.")
        else:
            with st.status(f"Transmitting {len(csv_data)} emails securely via mail.streamax.com...", expanded=True) as status:
                try:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL("mail.streamax.com", 465, timeout=30, context=context)
                    server.login(user_email, user_pass)
                    
                    success_count = 0
                    for index, row in enumerate(csv_data):
                        # Ensure keys are lowercase strings for matching
                        row_lower = {str(k).lower(): v for k, v in row.items()}
                        row_lower["your_name"] = sig_name
                        
                        target_email = row_lower.get('email', '')
                        if not target_email:
                            st.write(f"⚠️ Row {index+1}: Missing email address, skipping.")
                            continue
                            
                        rendered_subj = render_template(subj_tmpl, row_lower)
                        rendered_body = render_template(body_tmpl, row_lower).replace('\n', '<br>')
                        html_content = rendered_body + f"<br><br>{sig_html}"
                        
                        msg = create_message(rendered_subj, html_content, target_email, sig_name, user_email)
                        
                        try:
                            server.send_message(msg)
                            st.write(f"✅ Sent to **{target_email}**")
                            success_count += 1
                        except Exception as e:
                            st.write(f"❌ Failed to send to **{target_email}**: {str(e)}")
                            
                        time.sleep(0.5) # Prevent overloading the Streamax SMTP server
                        
                    server.quit()
                    status.update(label=f"Batch complete! Successfully dispatched {success_count} emails.", state="complete", expanded=False)
                    st.balloons()
                    
                except smtplib.SMTPAuthenticationError:
                    status.update(label="Authentication Failed.", state="error")
                    st.error("Email or password incorrect. Please refresh and re-authenticate.")
                except Exception as e:
                    status.update(label="SMTP Error", state="error")
                    st.error(f"SMTP Connection Error: {str(e)}")
