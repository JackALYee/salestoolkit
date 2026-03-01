import streamlit as st
import streamlit.components.v1 as components

# Import modular components
from login import render_login
from streamaxpedia_app import content as streamaxpedia_content
from prospecting_flow import content as prospecting_flow_content
from discovery_meeting import content as discovery_meeting_content
from presentation import content as presentation_content
from value_calculator import content as value_calculator_content

# Configure the Streamlit page settings
st.set_page_config(
    page_title="Streamax Sales Toolkit | Aurora Flow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default UI elements, set background, and create custom CSS for the Native Streamlit Navigation Bar
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
    
    /* Set dark background globally so it blends smoothly */
    .stApp {
        background-color: #050810;
        background-image: radial-gradient(circle at 50% -20%, #0B1221, #050810);
    }

    /* ---- STREAMLIT RADIO BUTTONS STYLED AS THE UNIFIED NAV BAR ---- */
    /* Hide the circular radio input entirely */
    div[role="radiogroup"] > label > div:first-child { 
        display: none !important; 
    }
    
    /* Style the container holding the radio buttons */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 15px !important;
        margin-bottom: 20px !important;
        flex-wrap: wrap !important;
    }
    
    /* Style the radio labels to match the HTML glassmorphism buttons */
    div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 30px !important;
        padding: 10px 24px !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
    }
    
    /* Style the text inside the radio labels */
    div[role="radiogroup"] > label p {
        color: #A0AEC0 !important;
        font-weight: 600 !important;
        margin: 0 !important;
        font-size: 0.95rem !important;
    }
    
    /* Hover effects */
    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateY(-2px);
    }
    div[role="radiogroup"] > label:hover p {
        color: #FFFFFF !important;
    }
    
    /* Checked/Active state */
    div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(42, 245, 152, 0.1) !important;
        border-color: #2AF598 !important;
        box-shadow: 0 0 20px rgba(42, 245, 152, 0.15) !important;
        transform: translateY(-2px);
    }
    div[role="radiogroup"] > label[data-checked="true"] p {
        color: #2AF598 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Check authentication state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Render the specific view based on authentication state
if not st.session_state['authenticated']:
    render_login()
else:
    # 1. Render the Toolkit Header Natively in Streamlit (Removed from HTML iframe to prevent duplication)
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 20px 0; animation: fadeInDown 1s ease-out;">
            <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; color: #2AF598; margin-bottom: 10px; font-family: 'Inter', sans-serif; font-weight: bold;">Streamax Sales Toolkit</div>
            <h1 style="font-size: 3.5rem; line-height: 1.1; margin-bottom: 0; color: white; font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -1px;">
                <span style="background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%); -webkit-background-clip: text; color: transparent;">North America</span><br>
                <span style="font-weight: 300;">Trucking Division</span>
            </h1>
            <div style="margin-top: 10px; font-size: 0.85rem; color: #A0AEC0; opacity: 0.7; font-family: 'Inter', sans-serif;">Version 1.0 • Trucking BU • Jan 2026</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Render the Unified Global Navigation Bar natively in Streamlit!
    tabs = {
        "📖 Streamaxpedia": "streamaxpedia",
        "🛣️ Prospecting Flow": "prospecting-flow",
        "🔍 Discovery Meeting": "discovery",
        "🖥️ Presentation": "presentation",
        "🧮 Value Calculator": "value-calculator",
        "📧 Email Tool": "dripmailer"
    }
    selected_label = st.radio("Navigation", list(tabs.keys()), horizontal=True, label_visibility="collapsed")
    active_id = tabs[selected_label]

    # 3. Route to the correct view (Python vs HTML)
    if active_id == "dripmailer":
        # Render the pure Python module
        from dripmailer import render_dripmailer
        st.write("<br>", unsafe_allow_html=True)
        render_dripmailer()
    else:
        # The HTML head, styling, and structural shell (Note: Header and <nav> have been removed!)
        html_head = r"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Streamax Sales Toolkit</title>
            
            <script src="https://cdn.tailwindcss.com"></script>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
            <script src="https://unpkg.com/lucide@latest"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            
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
                    --bg-deep: transparent; /* Changed to transparent so Streamlit BG bleeds through nicely */
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
                    font-family: var(--font-main);
                    color: var(--text-white);
                    line-height: 1.6;
                    overflow-x: hidden;
                }
                h1, h2, h3, h4, h5 { font-weight: 700; margin-bottom: 1rem; color: var(--text-white); }
                .gradient-text { background: var(--gradient-text); -webkit-background-clip: text; background-clip: text; color: transparent; display: inline-block; }
                p { color: var(--text-grey); margin-bottom: 1rem; }
                strong { color: var(--text-white); }
                ul, ol { color: var(--text-grey); padding-left: 20px; margin-bottom: 1rem; }
                li { margin-bottom: 8px; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; position: relative; }
                
                .card { background: var(--glass-bg); border: var(--glass-border); border-radius: var(--card-radius); padding: 30px; margin-bottom: 24px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); transition: var(--transition); position: relative; overflow: hidden; }
                .card:hover { border-color: rgba(42, 245, 152, 0.3); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); transform: translateY(-3px); }
                .section-header { margin-top: 40px; margin-bottom: 20px; border-left: 4px solid var(--primary-green); padding-left: 15px; font-size: 1.5rem; }
                .section-header.blue { border-color: var(--secondary-blue); }
                
                .fade-up { opacity: 0; transform: translateY(30px); transition: opacity 0.8s ease-out, transform 0.8s ease-out; }
                .fade-up.visible { opacity: 1; transform: translateY(0); }
                @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

                /* Section Styles */
                .script-box { background: rgba(0, 0, 0, 0.3); border-left: 3px solid var(--secondary-blue); padding: 20px; border-radius: 0 8px 8px 0; margin: 20px 0; position: relative; font-style: italic; }
                .script-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
                .script-tag { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: var(--secondary-blue); font-weight: bold; }
                .copy-btn { background: transparent; border: 1px solid var(--text-grey); color: var(--text-grey); padding: 4px 12px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: var(--transition); display: flex; align-items: center; gap: 5px; }
                .copy-btn:hover { border-color: var(--primary-green); color: var(--primary-green); }
                .list-card-content { margin-left: 0; }
                .list-card-content li { margin-bottom: 12px; }
                
                /* Sub-Navigation for inner tools */
                .sub-nav-tabs { display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
                .sub-nav-btn { background: transparent; border: none; color: var(--text-grey); font-size: 1rem; font-weight: 600; cursor: pointer; padding: 8px 16px; position: relative; transition: var(--transition); display: flex; align-items: center; gap: 8px;}
                .sub-nav-btn:hover { color: var(--text-white); }
                .sub-nav-btn.active { color: var(--primary-green); }
                .sub-nav-btn.active::after { content: ''; position: absolute; bottom: -11px; left: 0; width: 100%; height: 2px; background: var(--primary-green); box-shadow: 0 0 10px var(--primary-green); }
                .sub-content { display: none; }
                .sub-content.active { display: block; }
                
                /* Toast Notification */
                #toast { visibility: hidden; min-width: 250px; background-color: var(--primary-green); color: #050810; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1000; left: 50%; bottom: 30px; transform: translateX(-50%); font-weight: bold; box-shadow: 0 0 20px rgba(42, 245, 152, 0.4); opacity: 0; transition: opacity 0.3s; }
                #toast.show { visibility: visible; opacity: 1; }
                .hidden { display: none !important; }
            </style>
        </head>
        <body>
            <div class="container" id="content-container">
        """

        # The HTML scripts and closing tags. Contains the auto-initializer to show the active tab!
        html_tail = f"""
                <div style="height: 100px;"></div>
            </div>
            
            <div id="toast" style="visibility: hidden; min-width: 250px; background-color: var(--primary-green); color: #050810; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1000; left: 50%; bottom: 30px; transform: translateX(-50%); font-weight: bold; box-shadow: 0 0 20px rgba(42, 245, 152, 0.4); opacity: 0; transition: opacity 0.3s;">Copied to Clipboard!</div>

            <script>
                lucide.createIcons();

                // Observe Elements for Fade Up
                function observeElements() {{
                    const observer = new IntersectionObserver((entries) => {{
                        entries.forEach(entry => {{
                            if (entry.isIntersecting) entry.target.classList.add('visible');
                        }});
                    }}, {{ threshold: 0.1 }});
                    document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));
                }}

                // Init script triggered safely on load
                document.addEventListener('DOMContentLoaded', () => {{
                    // Force hide all sections, then show the active one passed dynamically from Python!
                    document.querySelectorAll('.content-section').forEach(section => section.classList.add('hidden'));
                    
                    const activeSection = document.getElementById('{active_id}');
                    if (activeSection) {{
                        activeSection.classList.remove('hidden');
                        
                        // Trigger fade animations immediately
                        const elements = activeSection.querySelectorAll('.fade-up');
                        elements.forEach(el => {{
                            el.classList.remove('visible');
                            setTimeout(() => el.classList.add('visible'), 50);
                        }});
                        
                        // Triggers specific to sections
                        if ('{active_id}' === 'value-calculator' && window.MathJax && MathJax.typesetPromise) {{
                            MathJax.typesetPromise();
                        }}
                        
                        if ('{active_id}' === 'presentation' && typeof initLoopVisual === 'function') {{
                            initLoopVisual();
                        }}
                    }}
                    
                    observeElements();
                    
                    if (typeof calculateROI === 'function') calculateROI();
                    if (typeof initIfta === 'function') initIfta();
                }});

                // Local HTML Sub-Tab switching logic (unchanged)
                function switchSubTab(tabId, element) {{
                    const subNavs = element.closest('.sub-nav-tabs').querySelectorAll('.sub-nav-btn');
                    subNavs.forEach(btn => btn.classList.remove('active'));
                    element.classList.add('active');

                    const parentSection = element.closest('.content-section');
                    parentSection.querySelectorAll('.sub-content').forEach(content => {{
                        content.classList.remove('active');
                    }});
                    const activeSub = document.getElementById(tabId);
                    if(activeSub) {{
                        activeSub.classList.add('active');
                        activeSub.querySelectorAll('.fade-up').forEach(el => {{
                            el.classList.remove('visible');
                            setTimeout(() => el.classList.add('visible'), 50);
                        }});
                        observeElements();

                        if ((tabId === 'tco-calc' || tabId === 'ifta-calc') && window.MathJax && MathJax.typesetPromise) {{
                            MathJax.typesetPromise();
                        }}
                    }}
                }}

                // Copy functionality
                function copyText(btnElement) {{
                    const textToCopy = btnElement.closest('.script-header').nextElementSibling.innerText;
                    document.execCommand('copy'); 
                    navigator.clipboard.writeText(textToCopy).then(() => {{
                        const toast = document.getElementById("toast");
                        toast.style.visibility = "visible";
                        toast.style.opacity = "1";
                        setTimeout(function(){{ toast.style.opacity = "0"; toast.style.visibility = "hidden"; }}, 3000);
                    }}).catch(err => {{
                        const textArea = document.createElement("textarea");
                        textArea.value = textToCopy;
                        document.body.appendChild(textArea);
                        textArea.select();
                        try {{
                            document.execCommand('copy');
                            const toast = document.getElementById("toast");
                            toast.style.visibility = "visible";
                            toast.style.opacity = "1";
                            setTimeout(function(){{ toast.style.opacity = "0"; toast.style.visibility = "hidden"; }}, 3000);
                        }} catch (err) {{}}
                        document.body.removeChild(textArea);
                    }});
                }}
            </script>
        </body>
        </html>
        """

        # Reconstruct HTML by appending the specific active module. 
        # (This makes the iframe incredibly fast to load since it doesn't render inactive HTML content)
        html_code = html_head + "\n"
        
        if active_id == "streamaxpedia": html_code += streamaxpedia_content
        elif active_id == "prospecting-flow": html_code += prospecting_flow_content
        elif active_id == "discovery": html_code += discovery_meeting_content
        elif active_id == "presentation": html_code += presentation_content
        elif active_id == "value-calculator": html_code += value_calculator_content
        
        html_code += "\n" + html_tail

        components.html(html_code, height=1800, scrolling=True)
