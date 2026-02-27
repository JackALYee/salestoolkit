import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page settings
st.set_page_config(
    page_title="Streamax Sales Toolkit | Aurora Flow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit's default UI elements to provide an immersive, full-screen experience
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
    </style>
    """,
    unsafe_allow_html=True
)

# The exact, unmodified HTML/CSS/JS content of your toolkit
# We use a raw string (r"") so the LaTeX equations in the Value Calculator aren't treated as escape characters.
html_code = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streamax Sales Toolkit | Aurora Flow</title>
    
    <!-- Tailwind CSS (for TCO Calculator) -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    
    <!-- Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- MathJax for LaTeX Rendering (TCO Calculator) -->
    <script>
        window.MathJax = {
            loader: {load: ['[tex]/html']},
            tex: {
                packages: {'[+]': ['html']},
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']]
            },
            chtml: {
                scale: 0.9
            }
        };
    </script>
    <script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

    <style>
        /* --- 2. GLOBAL CSS VARIABLES --- */
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
            
            /* Additional Utilities */
            --gradient-text: linear-gradient(135deg, var(--primary-green) 0%, var(--secondary-blue) 100%);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* --- RESET & BASE --- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

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

        /* Grid Overlay Effect */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            opacity: 0.05;
            z-index: -1;
            pointer-events: none;
        }

        /* --- TYPOGRAPHY --- */
        h1, h2, h3, h4, h5 {
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--text-white);
        }

        .gradient-text {
            background: var(--gradient-text);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            display: inline-block;
        }

        p {
            color: var(--text-grey);
            margin-bottom: 1rem;
        }

        strong {
            color: var(--text-white);
        }
        
        ul, ol {
            color: var(--text-grey);
            padding-left: 20px;
            margin-bottom: 1rem;
        }
        
        li {
            margin-bottom: 8px;
        }

        /* --- LAYOUT --- */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
        }

        header {
            text-align: center;
            padding: 60px 0 40px;
            animation: fadeInDown 1s ease-out;
        }

        .header-subtitle {
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--primary-green);
            margin-bottom: 10px;
        }

        .header-meta {
            margin-top: 10px;
            font-size: 0.85rem;
            color: var(--text-grey);
            opacity: 0.7;
        }

        /* --- NAVIGATION --- */
        .nav-tabs {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }

        .nav-btn {
            background: rgba(255, 255, 255, 0.05);
            border: var(--glass-border);
            color: var(--text-grey);
            padding: 12px 30px;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 600;
            transition: var(--transition);
            backdrop-filter: blur(5px);
            font-family: var(--font-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-white);
            transform: translateY(-2px);
        }

        .nav-btn.active {
            background: rgba(42, 245, 152, 0.1);
            border-color: var(--primary-green);
            color: var(--primary-green);
            box-shadow: var(--glow-shadow);
        }

        /* --- GLASS CARDS --- */
        .card {
            background: var(--glass-bg);
            border: var(--glass-border);
            border-radius: var(--card-radius);
            padding: 30px;
            margin-bottom: 24px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            border-color: rgba(42, 245, 152, 0.3);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transform: translateY(-3px);
        }
        
        .section-header {
             margin-top: 40px; 
             margin-bottom: 20px;
             border-left: 4px solid var(--primary-green); 
             padding-left: 15px;
             font-size: 1.5rem;
        }
        
        .section-header.blue {
            border-color: var(--secondary-blue);
        }

        /* --- ANIMATIONS --- */
        .fade-up {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s ease-out, transform 0.8s ease-out;
        }

        .fade-up.visible {
            opacity: 1;
            transform: translateY(0);
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* --- SECTION 2: PROSPECTING STYLES --- */
        .script-box {
            background: rgba(0, 0, 0, 0.3);
            border-left: 3px solid var(--secondary-blue);
            padding: 20px;
            border-radius: 0 8px 8px 0;
            margin: 20px 0;
            position: relative;
            font-style: italic;
        }
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

        /* --- PROSPECTING FLOW STYLES --- */
        .flow-container {
            border-left: 2px solid rgba(255, 255, 255, 0.1);
            margin-left: 10px;
            padding-left: 30px;
            position: relative;
        }
        
        .flow-step-block {
            position: relative;
            margin-bottom: 60px;
        }

        .flow-marker {
            position: absolute;
            left: -41px;
            top: 0;
            width: 20px;
            height: 20px;
            background: var(--bg-deep);
            border: 2px solid var(--primary-green);
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(42, 245, 152, 0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 0.7rem;
            color: var(--primary-green);
            font-weight: bold;
            z-index: 2;
        }

        .flow-marker.blue {
            border-color: var(--secondary-blue);
            color: var(--secondary-blue);
            box-shadow: 0 0 10px rgba(0, 158, 253, 0.3);
        }

        .flow-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-white);
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .flow-subtitle {
            font-size: 0.9rem;
            color: var(--text-grey);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
            display: block;
        }

        /* --- VISUAL LOOP STYLES --- */
        .loop-visual-wrapper {
            position: relative;
            width: 100%;
            height: 600px;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
        }

        .scene-container {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .orbit-svg {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .road-base { fill: none; stroke: rgba(255, 255, 255, 0.08); stroke-width: 2px; }
        .road-edge { display: none; }
        .road-lane {
            fill: none;
            stroke: var(--primary-green);
            stroke-width: 1px;
            stroke-dasharray: none;
            stroke-linecap: round;
            animation: roadFlow 40s linear infinite;
            filter: drop-shadow(0 0 4px var(--primary-green));
            opacity: 0.6;
        }

        @keyframes roadFlow { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -1000; } }

        .center-logo-area { position: absolute; z-index: 5; text-align: center; width: 300px; pointer-events: none; }
        .center-logo-area h1 {
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, var(--text-white) 0%, var(--secondary-blue) 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 30px rgba(0, 158, 253, 0.3);
        }
        .center-logo-area p { color: var(--primary-green); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }

        .node-container {
            position: absolute;
            width: 70px;
            height: 70px;
            transform: translate(-50%, -50%);
            z-index: 10;
            cursor: pointer;
            transition: z-index 0.2s;
        }
        .node-container:hover { z-index: 50; }

        .node-visual {
            width: 100%; height: 100%;
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02));
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            border-top: 1px solid rgba(255, 255, 255, 0.4);
            border-left: 1px solid rgba(255, 255, 255, 0.4);
            border-bottom: 1px solid rgba(0, 0, 0, 0.4);
            border-right: 1px solid rgba(0, 0, 0, 0.4);
            box-shadow: inset 2px 2px 4px rgba(255, 255, 255, 0.1), inset -2px -2px 4px rgba(0, 0, 0, 0.4), 0 15px 25px rgba(0,0,0,0.6);
            display: flex; justify-content: center; align-items: center;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
        }
        .node-visual i { font-size: 1.5rem; color: var(--text-grey); transition: all 0.3s ease; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); }

        .node-container:hover .node-visual {
            transform: scale(1.15) translateY(-5px);
            background: linear-gradient(145deg, rgba(42, 245, 152, 0.15), rgba(42, 245, 152, 0.05));
            border-color: rgba(42, 245, 152, 0.5);
            box-shadow: inset 2px 2px 6px rgba(42, 245, 152, 0.2), inset -2px -2px 6px rgba(0, 0, 0, 0.5), 0 0 30px rgba(42, 245, 152, 0.3);
        }
        .node-container:hover .node-visual i { color: var(--text-white); transform: scale(1.1); filter: drop-shadow(0 0 8px var(--primary-green)); }

        .node-static-label {
            position: absolute; top: 80px; left: 50%; transform: translateX(-50%); width: 140px; text-align: center;
            font-size: 0.8rem; font-weight: 600; color: var(--text-white); text-shadow: 0 2px 4px rgba(0,0,0,0.8);
            pointer-events: none; transition: opacity 0.3s;
        }
        .node-container:hover .node-static-label { opacity: 0; }

        .phase-label {
            position: absolute; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
            color: var(--secondary-blue); padding: 5px 12px; border-radius: 20px; background: rgba(0, 158, 253, 0.1);
            border: 1px solid rgba(0, 158, 253, 0.3); transform: translate(-50%, -50%); z-index: 4; pointer-events: none; white-space: nowrap;
        }

        .popup-card {
            position: absolute; top: 50%; left: 50%; width: 240px;
            background: rgba(11, 18, 33, 0.95); border: 1px solid var(--primary-green); border-radius: 12px;
            padding: 15px; opacity: 0; visibility: hidden; transform: translate(-50%, 10px) scale(0.9);
            transition: all 0.3s ease; pointer-events: none; box-shadow: 0 20px 50px rgba(0,0,0,0.6); z-index: 100;
        }
        .node-container:hover .popup-card { opacity: 1; visibility: visible; transform: translate(-50%, -135%) scale(1); }
        .pop-down .popup-card { transform: translate(-50%, -10px) scale(0.9); }
        .pop-down:hover .popup-card { transform: translate(-50%, 65%) scale(1); }

        .popup-header { color: var(--primary-green); font-size: 0.9rem; font-weight: 700; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; display: flex; align-items: center; gap: 8px; }
        .popup-list { list-style: none; font-size: 0.8rem; color: var(--text-grey); line-height: 1.4; padding: 0; margin: 0; }
        .popup-list li { position: relative; padding-left: 12px; margin-bottom: 4px; }
        .popup-list li::before { content: ''; position: absolute; left: 0; top: 6px; width: 4px; height: 4px; background: var(--secondary-blue); border-radius: 50%; }

        /* --- SUB-NAVIGATION --- */
        .sub-nav-tabs { display: flex; gap: 20px; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        .sub-nav-btn { background: transparent; border: none; color: var(--text-grey); font-size: 1rem; font-weight: 600; cursor: pointer; padding: 8px 16px; position: relative; transition: var(--transition); display: flex; align-items: center; gap: 8px;}
        .sub-nav-btn:hover { color: var(--text-white); }
        .sub-nav-btn.active { color: var(--primary-green); }
        .sub-nav-btn.active::after { content: ''; position: absolute; bottom: -11px; left: 0; width: 100%; height: 2px; background: var(--primary-green); box-shadow: 0 0 10px var(--primary-green); }
        .sub-content { display: none; }
        .sub-content.active { display: block; }

        #running-element {
            position: absolute; width: 40px; height: 30px; color: var(--primary-green); font-size: 20px;
            z-index: 20; pointer-events: none; filter: drop-shadow(0 0 10px var(--primary-green));
            transition: transform 0.05s linear; display: flex; justify-content: center; align-items: center;
        }
        #running-element i.fa-person-walking { font-size: 24px; color: var(--secondary-blue); filter: drop-shadow(0 0 12px var(--secondary-blue)); }

        /* Toast Notification */
        #toast {
            visibility: hidden; min-width: 250px; background-color: var(--primary-green); color: #050810;
            text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1000; left: 50%; bottom: 30px;
            transform: translateX(-50%); font-weight: bold; box-shadow: 0 0 20px rgba(42, 245, 152, 0.4);
            opacity: 0; transition: opacity 0.3s;
        }
        #toast.show { visibility: visible; opacity: 1; }
        .hidden { display: none !important; }

        /* Custom style for discovery flow questions */
        .discovery-question-list { list-style: none; padding: 0; margin-top: 10px; }
        .discovery-question-list li { 
            position: relative; 
            padding-left: 20px; 
            margin-bottom: 12px; 
            color: var(--text-white);
            font-style: italic;
            line-height: 1.5;
        }
        .discovery-question-list li::before { 
            content: '>'; 
            position: absolute; 
            left: 0; 
            top: 0; 
            color: var(--primary-green); 
            font-weight: bold;
            font-style: normal;
        }

        /* --- SOLUTION OVERVIEW VISUAL --- */
        .solution-visual {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 30px;
            font-family: 'Inter', sans-serif;
        }
        .solution-title {
            color: #3b82f6;
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 30px;
        }
        .solution-main-pill {
            background: #ffffff;
            color: #3b82f6;
            font-weight: 700;
            font-size: 1.4rem;
            padding: 16px 30px;
            border-radius: 50px;
            display: inline-block;
            width: 90%;
            max-width: 800px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .solution-pillars {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .solution-pill {
            background: #ffffff;
            color: #3b82f6;
            font-weight: 700;
            font-size: 1.1rem;
            padding: 14px 20px;
            border-radius: 50px;
            flex: 1;
            min-width: 200px;
            max-width: 280px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .solution-plus {
            color: #3b82f6;
            font-size: 2rem;
            font-weight: 300;
        }
        .solution-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .solution-card-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .solution-card {
            background: #ffffff;
            border-radius: 20px;
            width: 100%;
            height: 180px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }
        .solution-card-label {
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        /* Inner Illustrations for Solution Cards */
        .sc-illus-1 { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: flex-end; padding-bottom: 25px;}
        .sc-illus-1 .blue-truck { font-size: 6rem; color: #60a5fa; margin-right: -10px; z-index: 1;}
        .sc-illus-1 .driver { font-size: 4.5rem; color: #1e3a8a; z-index: 2; margin-bottom: -5px;}
        .sc-illus-1 .badge { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); font-size: 2rem; color: #bfdbfe; opacity: 0.5; z-index: 0;}

        .sc-illus-2 { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
        .sc-illus-2 .truck-wrapper { display: flex; align-items: flex-end; position: relative; z-index: 2;}
        .sc-illus-2 .trailer { width: 120px; height: 50px; background: #f1f5f9; border: 1px solid #cbd5e1; border-right: none; background-image: repeating-linear-gradient(90deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 11px); border-radius: 4px 0 0 4px;}
        .sc-illus-2 .cab { width: 35px; height: 45px; background: #ef4444; border-radius: 0 8px 0 0; position: relative;}
        .sc-illus-2 .cab::after { content:''; position: absolute; top: 5px; right: 5px; width: 12px; height: 18px; background: #cbd5e1; border-radius: 0 4px 0 0; }
        .sc-illus-2 .wheel { width: 18px; height: 18px; background: #334155; border-radius: 50%; position: absolute; bottom: -6px; border: 2px solid #e2e8f0; }
        .sc-illus-2 .w1 { left: 15px; }
        .sc-illus-2 .w2 { right: 60px; }
        .sc-illus-2 .w3 { right: 35px; }
        .sc-illus-2 .thief1 { position: absolute; font-size: 2rem; color: #1e293b; bottom: 20px; right: 10px; z-index: 3;}
        .sc-illus-2 .thief2 { position: absolute; font-size: 2rem; color: #1e293b; bottom: 20px; left: 20px; transform: scaleX(-1); z-index: 3;}
        .sc-illus-2 .box-icon { position: absolute; color: #d97706; font-size: 1rem; bottom: 30px; right: -5px; z-index: 4;}

        .sc-illus-3 { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; border-radius: 20px; background: #475569;}
        .sc-illus-3 .road-line { position: absolute; width: 30px; height: 4px; background: rgba(255,255,255,0.3); }
        .sc-illus-3 .rl-1 { top: 25%; left: 15%; }
        .sc-illus-3 .rl-2 { top: 25%; right: 15%; }
        .sc-illus-3 .rl-3 { bottom: 25%; left: 15%; }
        .sc-illus-3 .rl-4 { bottom: 25%; right: 15%; }
        .sc-illus-3 .truck-body { position: relative; width: 130px; height: 30px; background: #e2e8f0; border-radius: 2px; z-index: 5; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .sc-illus-3 .truck-cab { position: absolute; right: -25px; top: 2px; width: 25px; height: 26px; background: #94a3b8; border-radius: 4px; z-index: 6; }
        .sc-illus-3 .bs-cone { position: absolute; background: repeating-linear-gradient(45deg, #f59e0b, #f59e0b 10px, #fbbf24 10px, #fbbf24 20px); opacity: 0.9; z-index: 2;}
        .sc-illus-3 .bs-front { width: 80px; height: 80px; right: -25px; top: 50%; transform: translateY(-50%) rotate(45deg); clip-path: polygon(0 0, 100% 0, 0 100%); }
        .sc-illus-3 .bs-side-top { width: 140px; height: 80px; bottom: 50%; right: 20px; clip-path: polygon(100% 100%, 0 0, 100% 0); }
        .sc-illus-3 .bs-side-bottom { width: 140px; height: 80px; top: 50%; right: 20px; clip-path: polygon(100% 0, 0 100%, 100% 100%); }
        .sc-illus-3 .warning-icon { position: absolute; color: white; font-size: 0.9rem; z-index: 10; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5)); }

        /* --- ACCIDENT PREVENTION VISUAL --- */
        .prevention-visual {
            background: #000000;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px 30px;
            margin-bottom: 30px;
            font-family: 'Inter', sans-serif;
            color: white;
            position: relative;
        }
        .prevention-title {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 40px;
        }
        .timeline-container {
            display: flex;
            position: relative;
            justify-content: space-between;
            align-items: stretch;
            gap: 15px;
        }
        .timeline-line {
            position: absolute;
            top: 48px;
            left: -15px;
            right: -25px;
            height: 4px;
            background: #0284c7; 
            z-index: 1;
        }
        .timeline-line::after {
            content: '';
            position: absolute;
            right: -10px;
            top: -8px;
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
            border-left: 16px solid #0284c7;
        }
        .timeline-step {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 2;
            width: 25%;
        }
        .step-percent {
            font-size: 2.2rem;
            font-weight: 800;
            font-style: italic;
            margin-bottom: 10px;
            color: #ffffff;
            line-height: 1;
        }
        .step-dot {
            width: 14px;
            height: 14px;
            background: white;
            border-radius: 50%;
            margin-bottom: 15px;
            box-shadow: 0 0 0 6px #000000;
        }
        .step-time {
            font-size: 1.6rem;
            font-weight: 800;
            font-style: italic;
            margin-bottom: 15px;
            text-align: center;
            line-height: 1.1;
        }
        .step-card-header {
            background: #0284c7;
            color: white;
            font-weight: 700;
            font-size: 1.05rem;
            padding: 12px 10px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 10px;
            width: 100%;
        }
        .step-card-body {
            background: transparent;
            border: 1px solid;
            border-radius: 8px;
            padding: 15px;
            font-size: 0.85rem;
            color: #e2e8f0;
            text-align: left;
            flex-grow: 1;
            width: 100%;
        }
        .step-card-body ul { padding-left: 15px; margin: 0; }
        .step-card-body li { margin-bottom: 0; list-style-type: disc; }
        
        .border-blue { border-color: #1e40af; }
        .border-orange { border-color: #c2410c; }
        .border-yellow { border-color: #a16207; }

        @media (max-width: 768px) {
            .icp-grid { grid-template-columns: 1fr; }
            .loop-visual-wrapper { height: 400px; }
            .center-logo-area h1 { font-size: 1.8rem; }
            .node-container { width: 50px; height: 50px; }
            .node-visual i { font-size: 1rem; }
            .solution-cards { grid-template-columns: 1fr; }
            .solution-plus { display: none; }
            .solution-pillars { flex-direction: column; gap: 10px; }
            .solution-pill { width: 100%; max-width: 100%; }
            .timeline-container { flex-direction: column; gap: 30px; }
            .timeline-line { display: none; }
            .timeline-step { width: 100%; }
        }

        /* --- TCO Custom CSS --- */
        .glass-panel {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        }
        .delay-1 { animation-delay: 0.1s; }
        .delay-2 { animation-delay: 0.2s; }
        .delay-3 { animation-delay: 0.3s; }
        .delay-4 { animation-delay: 0.4s; }
        input[type="number"] {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-white);
            transition: all 0.3s ease;
        }
        input[type="number"]:focus {
            border-color: var(--primary-green);
            box-shadow: 0 0 12px rgba(42, 245, 152, 0.2);
            outline: none;
            background: rgba(0, 0, 0, 0.5);
        }
        .highlighted-var {
            background-color: rgba(42, 245, 152, 0.15) !important;
            color: var(--primary-green) !important;
            border-radius: 4px;
            padding: 0.1rem 0.2rem;
            text-shadow: 0 0 8px var(--primary-green);
            border: 1px solid rgba(42, 245, 152, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        mjx-container {
            color: var(--text-white) !important;
        }
        details > summary { list-style: none; }
        details > summary::-webkit-details-marker { display: none; }
        .tooltip-bg {
            background: rgba(10, 15, 25, 0.95);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .tooltip-arrow-border {
            border-top-color: rgba(255, 255, 255, 0.1);
        }
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
        <!-- Navigation -->
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
            <button class="nav-btn" onclick="window.open('https://dripmailer.streamlit.app/#compose-email', '_blank')">
                <i data-lucide="mail"></i> Email Tool
            </button>
        </nav>

        <!-- SECTION: PROSPECTING FLOW -->
        <div id="prospecting-flow" class="content-section">
            <div class="card fade-up">
                <h2 class="gradient-text">The Sales Path: From Cold to Closed</h2>
                <p>Follow this step-by-step workflow to guide your prospecting journey from identifying targets to securing and executing a discovery meeting. Select your target audience below.</p>
            </div>

            <div class="sub-nav-tabs fade-up">
                <button class="sub-nav-btn active" onclick="switchSubTab('flow-tsp', this)">
                    <i data-lucide="network"></i> TSP / Channel Partner
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('flow-enduser', this)">
                    <i data-lucide="truck"></i> End Users (Fleets)
                </button>
            </div>

            <!-- TSP FLOW SUB-SECTION -->
            <div id="flow-tsp" class="sub-content active">
                <div class="flow-container">
                    
                    <!-- Step 1 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">1</div>
                        <div class="flow-title">Understand the Target</div>
                        <span class="flow-subtitle">Identify the TSP Business Model</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <h4 style="color: var(--secondary-blue);">What a TSP is vs. an End User (Key Differences)</h4>
                            <ul class="list-card-content" style="margin-top: 15px;">
                                <li><strong>Primary business model:</strong> TSPs <em>resell, bundle, or manage</em> telematics/video solutions for fleets; End Users <em>operate fleets</em> and consume the solution internally.</li>
                                <li><strong>Buyer motivation:</strong> TSPs optimize <em>margin, attach rate, differentiation, and retention</em>; End Users optimize <em>safety outcomes, claims reduction, operations efficiency, and compliance</em>.</li>
                                <li><strong>Decision criteria:</strong> TSPs care about <em>partner economics, platform openness, support SLAs, scalability, branding/white-label, and multi-tenant management</em>; End Users care about <em>ease of use, evidence quality, reliability, rollout speed, and ROI</em>.</li>
                                <li><strong>Sales motion:</strong> TSPs require <em>partner onboarding, enablement, joint GTM, deal registration, pricing tiers</em>; End Users require <em>discovery, demo, pilot, procurement, rollout</em>.</li>
                                <li><strong>Stakeholders:</strong> TSPs include <em>CEO/GM, Product, Sales leadership, Solutions/Support, Partnerships</em>; End Users include <em>Safety, Ops, IT, Finance/Procurement</em>.</li>
                                <li><strong>Implementation ownership:</strong> TSP often wants <em>repeatable deployment + multi-customer support workflows</em>; End Users want <em>their fleet installed and adopted</em>.</li>
                                <li><strong>Success metrics:</strong> TSP: <em>partner revenue, churn reduction, ARPU uplift, time-to-deploy, support ticket rate</em>; End User: <em>incident reduction, claims cycle time, coaching adoption, downtime reduction</em>.</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 2 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">Initial Outreach</div>
                        <span class="flow-subtitle">Cold Email & Calling</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Cold Email Template (TSP)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Subject options:</strong>
                                    <ul style="margin-top:5px; margin-bottom:15px; margin-left:20px; color: var(--text-grey);">
                                        <li>Partnering to add AI video telematics to your portfolio</li>
                                        <li>A scalable video telematics platform for TSPs</li>
                                        <li>Helping TSPs increase attach rate with video + AI</li>
                                    </ul>
                                    Hi {FirstName},<br><br>
                                    I’m {YourName} from Streamax. We work with Telematics Service Providers who want to add (or upgrade) AI video telematics in a way that scales—without creating a heavy support or integration burden.<br><br>
                                    A quick question: are you currently offering video telematics as part of your bundle, or are fleets requesting it and you’re evaluating partners?<br><br>
                                    If relevant, I’d love to share how partners use Streamax to:
                                    <ul style="margin-top:5px; margin-bottom:15px; margin-left:20px; color: var(--text-grey);">
                                        <li>package a differentiated safety offering (video + AI + evidence workflow),</li>
                                        <li>manage customers efficiently (repeatable deployment + platform operations),</li>
                                        <li>and improve retention by solving claims and driver coaching pain.</li>
                                    </ul>
                                    Would you be open to a <strong>15–20 minute partner fit call</strong> next week? I can do {TimeOption1} or {TimeOption2}.<br><br>
                                    Best,<br>
                                    {YourName}<br>
                                    {Title} | Streamax<br>
                                    {Phone}
                                </div>
                            </div>

                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Cold Calling Template (TSP)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Hi {Name}, this is {YourName} from Streamax—did I catch you at an okay time for 30 seconds?"<br><br>
                                    <strong>Prospect:</strong> {Yes/No}<br><br>
                                    <strong>Rep (30s):</strong> "We partner with TSPs and integrators to offer AI video telematics—reliable hardware, edge AI, and a cloud platform designed to scale across many fleets. The goal is to help you win more deals and retain customers with a higher-value safety bundle."<br><br>
                                    <strong>Rep (qualifier):</strong> "Quick question—do you currently offer video telematics today, or are you evaluating options due to customer demand?"<br><br>
                                    <strong>If offering today:</strong> "What are you hearing from customers—evidence quality, false alerts, installation burden, or platform usability?"<br><br>
                                    <strong>If evaluating:</strong> "What would a winning partner look like—margin, multi-tenant platform, support SLAs, or speed to deploy?"<br><br>
                                    <strong>CTA:</strong> "If it makes sense, can we schedule a <strong>15–20 minute partner fit call</strong> to review your portfolio and see where Streamax fits? I have {Option1} or {Option2}."
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">3</div>
                        <div class="flow-title">Opening & Qualification</div>
                        <span class="flow-subtitle">First Contact Dialogues</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Identify TSP vs End User</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Thanks for taking the time. Before we dive in, can I quickly confirm how your organization would use a video telematics solution?"<br><br>
                                    <strong>Rep:</strong> "Are you looking to <em>offer and manage telematics for multiple fleets as a service</em> (as a telematics provider / reseller / integrator), or are you looking to <em>deploy it for your own fleet operations</em>?"<br><br>
                                    <strong>If they say they manage multiple customers:</strong> "Got it—so you operate as a Telematics Service Provider. Perfect. I’ll focus on partner economics, platform management, and how we support you to scale."<br><br>
                                    <strong>If they say for their own fleet:</strong> "Understood—you’re an end user fleet. I’ll focus on safety outcomes, claims evidence, and rollout best practices."
                                </div>
                            </div>

                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Opening Dialogue (TSP-Specific)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Great—since you’re a TSP, I’d like to understand three things in the first 10 minutes: (1) your customer segments and typical fleet sizes, (2) what you bundle today and where you see gaps, and (3) what a winning partner looks like in terms of margin, support, and scalability. Sound good?"<br><br>
                                    <strong>Rep:</strong> "Quick question: do you primarily win business on <em>price</em>, <em>differentiation (AI/UX)</em>, <em>service/support</em>, or <em>a full managed offering</em>?"
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 4 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">4</div>
                        <div class="flow-title">Pitching Value</div>
                        <span class="flow-subtitle">Elevator Pitch & Story</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">30-Second Elevator Pitch (TSP)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    "Streamax is an AI-powered video telematics platform purpose-built for partners who want to scale. We provide reliable hardware, edge AI, and a unified cloud platform with partner-friendly capabilities like multi-tenant management, repeatable deployment, and strong technical support. TSPs work with us to increase attach rate and retention—offering fleets a modern safety and evidence workflow without taking on excessive integration or support burden."
                                </div>
                            </div>

                            <div class="script-box" style="border-left-color: var(--primary-green);">
                                <div class="script-header"><span class="script-tag" style="color: var(--primary-green);">Example Value Story (TSP)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Scenario:</strong> "A regional telematics provider wanted to differentiate beyond GPS and ELD. Their fleets were asking for better incident evidence and driver coaching, but the provider was worried about support load and rollout complexity."<br><br>
                                    <strong>What we did:</strong> "We aligned on a packaged offering (hardware + AI + platform), built a repeatable deployment checklist, and enabled their sales/support teams with demo scripts and escalation paths."<br><br>
                                    <strong>Outcome framing:</strong> "They added a new revenue line, improved competitiveness in RFPs, and positioned a higher-value safety bundle that strengthened customer retention."
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- END USER FLOW SUB-SECTION -->
            <div id="flow-enduser" class="sub-content">
                <div class="flow-container">
                    
                    <!-- Step 1 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">1</div>
                        <div class="flow-title">Understand the Target</div>
                        <span class="flow-subtitle">Identify the End User Dynamics</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <h4 style="color: var(--primary-green);">What an End User is vs. a TSP (Key Differences)</h4>
                            <ul class="list-card-content" style="margin-top: 15px;">
                                <li><strong>Primary objective:</strong> End Users run fleets and want <em>safer driving, fewer incidents, faster claims resolution, and operational visibility</em>. TSPs want to <em>sell/manage solutions for many fleets</em>.</li>
                                <li><strong>Value lens:</strong> End Users evaluate <em>outcomes and total cost of ownership</em>; TSPs evaluate <em>partner economics and scalability</em>.</li>
                                <li><strong>Buyer personas:</strong> End Users: <em>Safety, Ops, IT, Finance, Procurement, Legal</em>. TSP: <em>Partnerships, Product, Sales, Support</em>.</li>
                                <li><strong>Sales cycle:</strong> End Users follow <em>discovery → demo → pilot → procurement → rollout</em>; TSP follows <em>partner onboarding → enablement → joint GTM</em>.</li>
                                <li><strong>Success metrics:</strong> End Users track <em>incident rate, claims costs, coaching adoption, uptime, deployment speed</em>.</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 2 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">Initial Outreach</div>
                        <span class="flow-subtitle">Cold Email & Calling</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Cold Email Template (End Users)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Subject options:</strong>
                                    <ul style="margin-top:5px; margin-bottom:15px; margin-left:20px; color: var(--text-grey);">
                                        <li>Reducing claims friction with AI video evidence</li>
                                        <li>A faster way to get incident video and coach drivers</li>
                                        <li>Video telematics to improve safety outcomes</li>
                                    </ul>
                                    Hi {FirstName},<br><br>
                                    I’m {YourName} with Streamax. We help fleets reduce safety risk and claims friction by combining in-vehicle cameras, edge AI, and a cloud platform that makes video evidence and coaching workflows easy to run.<br><br>
                                    When an incident happens today, how long does it take your team to (a) find the right video, and (b) turn it into a coachable action?<br><br>
                                    If it’s worth exploring, I can share how fleets use Streamax to:
                                    <ul style="margin-top:5px; margin-bottom:15px; margin-left:20px; color: var(--text-grey);">
                                        <li>speed up incident evidence and reduce disputes,</li>
                                        <li>improve driver coaching consistency,</li>
                                        <li>and increase visibility without adding operational overhead.</li>
                                    </ul>
                                    Open to a <strong>15–20 minute discovery call</strong> this week to see if it’s relevant? I can do {TimeOption1} or {TimeOption2}.<br><br>
                                    Best,<br>
                                    {YourName}<br>
                                    {Title} | Streamax<br>
                                    {Phone}
                                </div>
                            </div>

                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Cold Calling Template (End Users)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Hi {Name}, this is {YourName} from Streamax—did I catch you at an okay time for 30 seconds?"<br><br>
                                    <strong>Prospect:</strong> {Yes/No}<br><br>
                                    <strong>Rep (30s):</strong> "Streamax helps fleets reduce incidents and claims friction using AI video telematics—reliable cameras plus a cloud platform that makes evidence review and driver coaching fast and consistent."<br><br>
                                    <strong>Rep (hook question):</strong> "Quick question—when an incident happens, is your bigger pain <em>getting the right video quickly</em>, <em>disputes/claims</em>, or <em>changing driver behavior through coaching</em>?"<br><br>
                                    <strong>Rep (follow-up):</strong> "What are you using today, and what’s prompting you to look at alternatives now?"<br><br>
                                    <strong>CTA:</strong> "If it makes sense, can we schedule a <strong>15–20 minute discovery call</strong> with the right stakeholders to map your current workflow and see if Streamax can help? I have {Option1} or {Option2}."
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">3</div>
                        <div class="flow-title">Opening & Qualification</div>
                        <span class="flow-subtitle">First Contact Dialogues</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Identify TSP vs End User</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Thanks for taking the time. Before we jump in, can I confirm your use case?"<br><br>
                                    <strong>Rep:</strong> "Are you evaluating video telematics <em>for your own fleet operations</em>, or are you looking to <em>offer it as a managed service / resale</em> to multiple fleets?"<br><br>
                                    <strong>If end user:</strong> "Perfect—then I’ll focus on safety outcomes, claims evidence, adoption, and rollout."<br><br>
                                    <strong>If TSP:</strong> "Got it—sounds like you’re a provider/reseller. I’ll switch to a partner-focused conversation."
                                </div>
                            </div>

                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">Opening Dialogue (End-User Specific)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Rep:</strong> "Great—so for your fleet, I’d like to learn three things first: (1) what safety or claims problem is most urgent, (2) what your current workflow looks like when incidents happen, and (3) what success would look like in 90 days. Sound good?"<br><br>
                                    <strong>Rep:</strong> "To make this concrete: is your priority more about <em>reducing incidents</em>, <em>speeding up claims and evidence</em>, or <em>improving driver coaching and compliance</em>?"
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Step 4 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">4</div>
                        <div class="flow-title">Pitching Value</div>
                        <span class="flow-subtitle">Elevator Pitch & Story</span>
                        
                        <div class="card" style="margin-left: 0;">
                            <div class="script-box">
                                <div class="script-header"><span class="script-tag">30-Second Elevator Pitch (End Users)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    "Streamax is an AI-powered video telematics solution that helps fleets prevent accidents, protect drivers, and reduce claims costs. We combine reliable in-vehicle hardware, edge AI, and a unified cloud platform so your team can quickly find video evidence, coach drivers consistently, and improve safety performance without creating extra operational burden."
                                </div>
                            </div>

                            <div class="script-box" style="border-left-color: var(--primary-green);">
                                <div class="script-header"><span class="script-tag" style="color: var(--primary-green);">Example Value Story (End Users)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                <div class="script-text">
                                    <strong>Scenario:</strong> "A fleet was spending too much time handling incidents—video was hard to find, disputes dragged on, and safety coaching wasn’t consistent."<br><br>
                                    <strong>What we did:</strong> "We deployed Streamax cameras and the cloud platform to streamline evidence capture and review, set up event workflows, and aligned coaching routines."<br><br>
                                    <strong>Outcome framing:</strong> "They shortened time-to-evidence, improved safety coaching adoption, and strengthened their position in claims disputes with clearer incident visibility."
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="height: 50px;"></div>
        </div>

        <!-- SECTION: DISCOVERY MEETING -->
        <div id="discovery" class="content-section hidden">
            <div class="card fade-up">
                <h2 class="gradient-text">Discovery Meetings</h2>
                <p>Structured question banks to guide your discovery calls and align on the best next steps. Choose your target audience below to see the specific discovery flow.</p>
            </div>

            <div class="sub-nav-tabs fade-up">
                <button class="sub-nav-btn active" onclick="switchSubTab('discovery-tsp', this)">
                    <i data-lucide="network"></i> TSP / Channel Partner
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('discovery-enduser', this)">
                    <i data-lucide="truck"></i> End Users (Fleets)
                </button>
            </div>

            <!-- TSP DISCOVERY SUB-SECTION -->
            <div id="discovery-tsp" class="sub-content active">
                <h3 class="section-header fade-up">TSP Discovery Meeting Question Bank (Natural Flow)</h3>
                
                <div class="card fade-up">
                    <h4 style="color: var(--primary-green);">Goal and Flow</h4>
                    <p><strong>Goal:</strong> Confirm whether the prospect is a true TSP motion (reseller/managed service/integrator), quantify partner fit (economics + scalability), and agree on next step (demo, pilot with one fleet, partner program review).</p>
                    <p><strong>Suggested time:</strong> 30–45 minutes.</p>
                    <p><strong>Flow:</strong> Rapport & context → TSP business model → customer/ICP → current portfolio & gaps → platform & operations requirements → partner economics → GTM/enablement → risks & procurement → next steps.</p>
                </div>

                <div class="flow-container">
                    <!-- Step 1 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">1</div>
                        <div class="flow-title">Opening</div>
                        <span class="flow-subtitle">2–3 min • Set the Frame</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"To make this useful, can I confirm how you go to market today—do you resell, bundle into a managed service, or integrate and deploy for fleets?"</li>
                                <li>"What would make this call a win for you? Are you hoping to validate technical fit, partner economics, or both?"</li>
                                <li>"Who else should be involved later—partnerships, product, support/ops, or your sales leadership?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 2 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">TSP Business Model & Strategy</div>
                        <span class="flow-subtitle">5 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"How do you make money today—hardware margin, monthly managed service, platform subscription, installation, or a mix?"</li>
                                <li>"What’s your current portfolio (GPS/ELD/video/safety), and what percentage of revenue comes from each?"</li>
                                <li>"Are you primarily competing on price, differentiated features, or service/support?"</li>
                                <li>"What’s your strategic goal this year: increase ARPU, reduce churn, win more RFPs, or expand into new segments?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 3 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">3</div>
                        <div class="flow-title">Your Customers / ICP</div>
                        <span class="flow-subtitle">5–7 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Who are your best-fit customers today (segments and typical fleet sizes)?"</li>
                                <li>"What regions do you cover, and do you serve cross-border fleets (US/Canada/Mexico)?"</li>
                                <li>"What are your customers asking for most right now related to video or AI? (claims, theft, driver coaching, compliance, live view, etc.)"</li>
                                <li>"What’s a typical deal size and buying cycle for your customers?"</li>
                                <li>"What triggers a purchase for them—renewal cycles, incident spikes, insurance pressure, new safety manager, compliance events?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 4 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">4</div>
                        <div class="flow-title">Current Video/Telematics Offering & Gap Analysis</div>
                        <span class="flow-subtitle">6–8 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Do you already offer video telematics today? If yes, which vendors are in your stack?"</li>
                                <li>"What do you like about your current solution, and what’s driving you to evaluate alternatives now?"</li>
                                <li>"Where are the biggest gaps—video quality, AI accuracy/false alerts, platform usability, install complexity, connectivity/data cost, or support burden?"</li>
                                <li>"Which features actually win deals for you versus features that look good but don’t move the needle?"</li>
                                <li>"What are the top 3 objections you hear from fleets when you propose video telematics?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 5 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">5</div>
                        <div class="flow-title">Partner Platform Requirements</div>
                        <span class="flow-subtitle">6–8 min • Multi-Tenant + Scale</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"How do you prefer to operate the platform—do you need multi-tenant management for many fleets under one portal?"</li>
                                <li>"Do you need white-labeling (branding, domain, app experience), or is co-branding acceptable?"</li>
                                <li>"What integration needs come up most—API access, webhooks, single sign-on, ELD/TMS integration, driver ID, or reporting exports?"</li>
                                <li>"How do you handle provisioning at scale today—device activation, SIM/data management, firmware updates, and user permissions?"</li>
                                <li>"What would your support team need to succeed—admin tools, diagnostics, remote troubleshooting, escalation SLAs?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 6 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">6</div>
                        <div class="flow-title">Deployment & Operations</div>
                        <span class="flow-subtitle">4–6 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Who installs today—your team, third-party installers, or fleet self-install? How important is speed of deployment?"</li>
                                <li>"What environments do your fleets operate in (urban, remote, cross-border)? Any connectivity challenges?"</li>
                                <li>"What are your must-have operational KPIs—uptime targets, ticket volume per 100 devices, mean time to resolve, replacement/RMA speed?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 7 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">7</div>
                        <div class="flow-title">Partner Economics & Commercial Structure</div>
                        <span class="flow-subtitle">6–8 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"How do you typically price video telematics to fleets—hardware up front, monthly bundle, or both?"</li>
                                <li>"What margin targets do you require on hardware and on monthly services? (Even ranges are fine.)"</li>
                                <li>"Do your customers expect financing, leasing, or a managed service model? If yes, how do you structure it?"</li>
                                <li>"What term lengths are most common—12, 36, or 60 months? What renewal/churn patterns do you see?"</li>
                                <li>"How do you want partner pricing to work—tiered by volume, deal registration, protected accounts, rebates/MDF?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 8 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">8</div>
                        <div class="flow-title">Go-to-Market & Enablement</div>
                        <span class="flow-subtitle">4–6 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"How do you generate demand today—your own sales team, channel sub-resellers, marketing, referrals?"</li>
                                <li>"What enablement do you need from a vendor partner—pitch decks, demo scripts, competitor battlecards, certification training, joint webinars?"</li>
                                <li>"What does a successful launch look like in the first 90 days—# of trained reps, # of demos, # of pilot fleets, target revenue?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 9 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">9</div>
                        <div class="flow-title">Risk, Compliance, and Deal Blockers</div>
                        <span class="flow-subtitle">3–5 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Are there any compliance/privacy requirements we should plan for (driver consent, retention policy, union rules, local regulations)?"</li>
                                <li>"What usually slows deals down—IT security, legal redlines, procurement, installation logistics, or incumbent contracts?"</li>
                                <li>"If we’re selected, what is the internal approval path and timeline on your side (partnership approval, product review, commercial sign-off)?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Step 10 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">10</div>
                        <div class="flow-title">Close & Next Steps</div>
                        <span class="flow-subtitle">2–3 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Based on what you shared, it sounds like the key priorities are {Priority1}, {Priority2}, and {Priority3}. Did I capture that correctly?"</li>
                                <li>"Would the best next step be (a) a partner-focused demo of the platform operations, (b) a commercial review of partner pricing tiers, or (c) identifying one fleet for a pilot to prove outcomes?"</li>
                                <li>"Who should join the next meeting from your side, and what timeline are you aiming for to make a partner decision?"</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Optional Step -->
                    <div class="flow-step-block fade-up" style="margin-bottom: 0;">
                        <div class="flow-marker" style="border-color: #A0AEC0; color: #A0AEC0; box-shadow: 0 0 10px rgba(160, 174, 192, 0.3);">*</div>
                        <div class="flow-title" style="color: #A0AEC0;">Optional (If Time)</div>
                        <span class="flow-subtitle">Qualification "Must Haves"</span>
                        <div class="card" style="margin-left: 0; padding: 20px; border-color: rgba(160, 174, 192, 0.3);">
                            <ul class="discovery-question-list" style="color: #A0AEC0;">
                                <li>"If we’re a fit, what are your <strong>non-negotiables</strong> in a partner: margin, multi-tenant tools, white-label, support SLAs, integrations, or something else?"</li>
                                <li>"Is there any scenario where you <strong>would not</strong> move forward, even if the product is strong? (e.g., certain commercial terms, lack of feature X, support model mismatch)"</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- END USER DISCOVERY SUB-SECTION -->
            <div id="discovery-enduser" class="sub-content">
                <h3 class="section-header fade-up">End User Discovery Meeting Question Bank (Natural Flow)</h3>
                
                <div class="card fade-up">
                    <h4 style="color: var(--primary-green);">Goal and Flow</h4>
                    <p><strong>Goal:</strong> Understand the fleet's safety/operations problems, quantify impact, confirm stakeholders and constraints, and align on a next step (tailored demo, pilot/POC, or proposal).</p>
                    <p><strong>Suggested time:</strong> 30–45 minutes.</p>
                    <p><strong>Flow:</strong> Context → objectives → current workflow → pains & impact → requirements → stakeholders & buying process → rollout constraints → success criteria → next steps.</p>
                </div>

                <div class="flow-container">
                    <!-- Step 1 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">1</div>
                        <div class="flow-title">Opening</div>
                        <span class="flow-subtitle">2–3 min • Set the Frame</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Thanks for the time. To make this useful, can I ask a few questions about your fleet, your current workflow, and what success looks like—then we can decide the best next step?"</li>
                                <li>"What prompted you to look at video telematics now? Was there a specific trigger event or goal?"</li>
                                <li>"Who’s joining today, and what roles do they play (safety, operations, IT, finance)? Who else should be involved later?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 2 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">Fleet Snapshot</div>
                        <span class="flow-subtitle">3–5 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Can you give me a quick overview of your operation—fleet size, vehicle types, and where you operate?"</li>
                                <li>"Are your routes mostly urban, long-haul, regional, or mixed? Any cross-border operations?"</li>
                                <li>"What does a typical driver day look like (hours, stops, yard time)?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 3 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">3</div>
                        <div class="flow-title">Top Objectives & Priorities</div>
                        <span class="flow-subtitle">4–6 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"If we fast-forward 6 months, what would you want to be true because you implemented a solution like this?"</li>
                                <li>"Which is the biggest priority right now: reducing incidents, speeding up claims/evidence, improving coaching, compliance, or operational visibility?"</li>
                                <li>"What KPIs do you track today for safety and operations (accidents per million miles, harsh events, claims cost, CSA, turnover)?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 4 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">4</div>
                        <div class="flow-title">Current Stack & Workflow</div>
                        <span class="flow-subtitle">6–8 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"What systems are you using today (ELD, GPS, cameras, safety platforms)? Who is the current vendor?"</li>
                                <li>"When an incident happens, can you walk me through your process from notification to finding video evidence to closing the case?"</li>
                                <li>"How long does it typically take to locate the right clip and share it internally or with insurance? What makes it slow or painful?"</li>
                                <li>"How do you coach drivers today—ride-alongs, manual review, scorecards? How consistent is it across terminals/managers?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 5 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">5</div>
                        <div class="flow-title">Pain Points & Business Impact</div>
                        <span class="flow-subtitle">5–7 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"What are the top 2–3 problems you want to solve with video and AI? Can you share a recent example?"</li>
                                <li>"Where do incidents cost you the most—injury claims, property damage, cargo loss, litigation, downtime, or reputational risk?"</li>
                                <li>"Do you have an estimate of incident frequency and total claims cost over the last 12 months (even a range)?"</li>
                                <li>"Are you seeing issues like false accusations, disputes about fault, or long claim cycle times?"</li>
                                <li>"What happens if you <em>don’t</em> solve this in the next 3–6 months?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 6 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">6</div>
                        <div class="flow-title">Feature and Operational Requirements</div>
                        <span class="flow-subtitle">6–8 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"What camera coverage do you need—road-facing, driver-facing, rear, side, trailer, cabin? Any special assets (reefers, buses, heavy equipment)?"</li>
                                <li>"What AI events matter most (distracted driving, following distance, lane departure, harsh braking, speeding, seatbelt, phone use)?"</li>
                                <li>"Do you need live view, two-way audio, panic button, geofencing, or driver ID?"</li>
                                <li>"How important is evidence workflow—search/filtering, event timeline, annotations, sharing links, retention policy?"</li>
                                <li>"Do you have IT/security requirements (SSO, SOC 2 expectations, data residency, encryption, access control)?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 7 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">7</div>
                        <div class="flow-title">Deployment Constraints</div>
                        <span class="flow-subtitle">4–6 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"How do you prefer to install—in-house, third-party, or self-install by drivers? What’s your acceptable downtime per vehicle?"</li>
                                <li>"Do you have multiple terminals/garages? Any constraints with scheduling, union rules, or driver consent policies?"</li>
                                <li>"How is connectivity today—cellular coverage, Wi-Fi in yard, remote routes? Any known dead zones?"</li>
                                <li>"What’s your ideal rollout timeline—pilot first or direct rollout?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 8 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">8</div>
                        <div class="flow-title">Stakeholders, Buying Process, and Budget</div>
                        <span class="flow-subtitle">5–7 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Who will own the project day-to-day (champion), and who signs off financially (economic buyer)?"</li>
                                <li>"What does procurement/legal typically require (MSA, insurance terms, data privacy language)?"</li>
                                <li>"Are you in a contract with a current vendor? If yes, when is renewal, and are there termination clauses?"</li>
                                <li>"How are you thinking about budget—capex hardware, monthly subscription, or an all-in managed service?"</li>
                                <li>"What other solutions are you comparing, and what will the decision be based on?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 9 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker">9</div>
                        <div class="flow-title">Success Criteria and Proof Plan</div>
                        <span class="flow-subtitle">3–5 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"What would make you confident to move forward—a demo, a pilot/POC, references, or a business case?"</li>
                                <li>"If we run a pilot, what success metrics should we measure (time-to-evidence, reduction in harsh events, coaching adoption, dispute resolution time)?"</li>
                                <li>"Who needs to see results, and by when, to make a decision?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 10 -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">10</div>
                        <div class="flow-title">Close and Next Steps</div>
                        <span class="flow-subtitle">2–3 min</span>
                        <div class="card" style="margin-left: 0; padding: 20px;">
                            <ul class="discovery-question-list">
                                <li>"Let me summarize what I heard: your top priorities are {Priority1}, {Priority2}, and {Priority3}. Is that accurate?"</li>
                                <li>"Based on that, the best next step is <strong>(a)</strong> a tailored demo for {personas}, or <strong>(b)</strong> a pilot plan with {fleet size} vehicles and agreed success metrics. Which do you prefer?"</li>
                                <li>"What’s the ideal decision date, and who should be on the next call to keep things moving?"</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Optional Step -->
                    <div class="flow-step-block fade-up" style="margin-bottom: 0;">
                        <div class="flow-marker" style="border-color: #A0AEC0; color: #A0AEC0; box-shadow: 0 0 10px rgba(160, 174, 192, 0.3);">*</div>
                        <div class="flow-title" style="color: #A0AEC0;">Optional (If Time)</div>
                        <span class="flow-subtitle">Risks and Objections</span>
                        <div class="card" style="margin-left: 0; padding: 20px; border-color: rgba(160, 174, 192, 0.3);">
                            <ul class="discovery-question-list" style="color: #A0AEC0;">
                                <li>"What concerns do you have about deploying cameras and AI (driver acceptance, privacy, false alerts, operational overhead)?"</li>
                                <li>"What would prevent this from moving forward internally, even if the product fit is strong?"</li>
                            </ul>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <!-- SECTION: PRESENTATION -->
        <div id="presentation" class="content-section hidden">
            
            <div class="card fade-up">
                <h2 class="gradient-text">Streamax Closed-Loop Trucking Solution</h2>
                <h5 style="color: var(--text-grey); margin-top: 5px;">Sales Presentation Script & Visuals</h5>
            </div>

            <!-- Subsection 3.1 Intro -->
            <h3 class="section-header fade-up">1. Introduction & Vision</h3>
            
            <!-- SOLUTION OVERVIEW VISUAL RECONSTRUCTION -->
            <div class="solution-visual fade-up">
                <div class="solution-title">Solution Overview</div>
                
                <div class="solution-main-pill">
                    The Streamax Fleet Management Solution
                </div>

                <div class="solution-pillars">
                    <div class="solution-pill">Video Telematics</div>
                    <div class="solution-plus">+</div>
                    <div class="solution-pill">Asset Security</div>
                    <div class="solution-plus">+</div>
                    <div class="solution-pill">Driver Visibility</div>
                </div>

                <div class="solution-cards">
                    <!-- Card 1 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card">
                            <div class="sc-illus-1">
                                <i class="fa-solid fa-id-badge badge"></i>
                                <i class="fa-solid fa-truck blue-truck"></i>
                                <i class="fa-solid fa-user-tie driver"></i>
                            </div>
                        </div>
                        <div class="solution-card-label">Driver Behavioral Risk</div>
                    </div>
                    
                    <!-- Card 2 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card">
                            <div class="sc-illus-2">
                                <div class="truck-wrapper">
                                    <div class="trailer"></div>
                                    <div class="cab"></div>
                                    <div class="wheel w1"></div>
                                    <div class="wheel w2"></div>
                                    <div class="wheel w3"></div>
                                </div>
                                <i class="fa-solid fa-person-walking thief1"></i>
                                <i class="fa-solid fa-box box-icon"></i>
                                <i class="fa-solid fa-person-walking thief2"></i>
                            </div>
                        </div>
                        <div class="solution-card-label">Asset & Cargo Security Risk</div>
                    </div>

                    <!-- Card 3 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card" style="background: #475569; padding: 0;">
                            <div class="sc-illus-3">
                                <div class="road-line rl-1"></div>
                                <div class="road-line rl-2"></div>
                                <div class="road-line rl-3"></div>
                                <div class="road-line rl-4"></div>
                                
                                <div class="bs-cone bs-side-top"></div>
                                <div class="bs-cone bs-side-bottom"></div>
                                <div class="bs-cone bs-front"></div>
                                
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="top: 25px; right: 70px;"></i>
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="bottom: 25px; right: 70px;"></i>
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="top: 50%; right: 10px; transform: translateY(-50%);"></i>

                                <div class="truck-body">
                                    <div class="truck-cab"></div>
                                </div>
                            </div>
                        </div>
                        <div class="solution-card-label">Driver Visibility Risk</div>
                    </div>
                </div>
            </div>

            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Speaker Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "Good morning/afternoon everyone. Thank you for the time.<br><br>
                        Today, I want to show you how Streamax is redefining fleet operations. We aren’t just selling cameras or sensors; our mission is to be the best technology partner for your entire operation.<br><br>
                        We know the challenges you face: stitching together different vendors for video, telematics, and AI is painful. Our goal is to solve that by connecting your devices, data, and workflows into one seamless system. We focus on three pillars:<br><br>
                        • <strong>Video Telematics & Safety:</strong> Trustworthy evidence and risk detection.<br><br>
                        • <strong>Asset & Cargo Security:</strong> Protecting your load in motion and at rest.<br><br>
                        • <strong>Visibility & Compliance:</strong> Giving you total situational awareness.<br><br>
                        "But the best way to understand this is to walk through the lifecycle of a single trip—our 'Closed-Loop' journey."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.2 The Loop -->
            <h3 class="section-header blue fade-up">2. The Closed-Loop Journey</h3>

            <!-- VISUAL LOOP CONTAINER -->
            <div class="loop-visual-wrapper fade-up">
                <div class="scene-container" id="scene">
                    <div class="center-logo-area">
                        <h1>STREAMAX</h1>
                        <p>Fleet Management<br>Solution</p>
                    </div>
                    <!-- SVG Orbit -->
                    <svg class="orbit-svg" id="orbitSvg" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <path id="roadBase" class="road-base" />
                        <path id="roadLane" class="road-lane" />
                    </svg>
                    <!-- Nodes injected by JS -->
                    <div id="nodes-layer"></div>
                    <!-- Labels injected by JS -->
                    <div id="labels-layer"></div>
                    <!-- Running Element -->
                    <div id="running-element"><i class="fa-solid fa-truck-fast"></i></div>
                </div>
            </div>
            
            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Full Journey Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "We believe value shouldn't just happen on the road. It starts before the key turns and continues after the engine stops. Let's look at the ten critical touchpoints."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 1: Before Departure</strong><br><br>
                        • <strong>Step 1: Compliance:</strong> "It starts here. Before a driver even approaches the vehicle, our system ensures you are meeting regional safety mandates—whether that’s specific blind-spot hardware requirements or DVS standards. We automate compliance so you don't have to worry about it."<br><br>
                        • <strong>Step 2: Driver ID:</strong> "Next, who is driving? We move beyond simple keys. We use <strong>Multi-Factor Verification</strong>—RFID badges, facial recognition, or even palm-vein scanning—to confirm the right driver is in the right asset. We can also integrate <strong>alcohol detection</strong> here to ensure fitness for duty before the engine starts."<br><br>
                        • <strong>Step 3: Cargo Loading:</strong> "This is a game-changer. Using our <strong>Z5 Intelligent Cargo Solution</strong>, we don't just 'transport air.' We measure <strong>cargo occupancy and volume</strong> automatically to help you maximize load efficiency. We also monitor the loading process itself, identifying bottlenecks or mishandling that could delay your schedule."<br><br>
                        • <strong>Step 4: Vehicle Status:</strong> "Before we roll, we check the health of the machine. Through deep <strong>CAN bus integration</strong> across thousands of makes and models, we give fleet managers a clear, real-time picture of ignition status, fuel levels, door sensors, and diagnostic trouble codes."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 2: Shipping (On the Road)</strong><br><br>
                        • <strong>Step 5: Starting:</strong> "As the vehicle moves off, risk spikes. Our <strong>Front Blind Spot Monitoring</strong> immediately activates to detect pedestrians or obstacles in that critical danger zone right in front of the cab, preventing low-speed tragedies."<br><br>
                        • <strong>Step 6: Driving:</strong> "On the open road, our <strong>ADAS and DSM (Driver Status Monitoring)</strong> systems are constantly vigilant. We detect fatigue, distraction, phone usage, and tailgating in real-time. But we don't just record it; we alert the driver instantly so they can self-correct <em>before</em> an incident happens."<br><br>
                        • <strong>Step 7: Turning:</strong> "Turns are a major liability. Our <strong>Side Blind Spot Detection</strong> works with the turn signal to alert the driver if a cyclist or pedestrian is in the danger zone, providing that extra pair of eyes when it matters most."<br><br>
                        • <strong>Step 8: Parking:</strong> "Cargo theft often happens when the vehicle is stopped. Our <strong>Sentinel Protection</strong> system guards the fuel and cargo during rest stops. It uses tamper detection and AI to send instant notifications if unauthorized access is attempted while the driver is sleeping or away."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 3: Arrival & Improvement</strong><br><br>
                        • <strong>Step 9: Arriving & Unloading:</strong> "When the truck arrives, our Z5 camera verifies the unloading process, ensuring proof of delivery and efficiency. We provide rear and side visibility assistance to make docking safe and precise."<br><br>
                        • <strong>Step 10: Coaching:</strong> "Finally, the trip ends, but the value continues. We close the loop with <strong>Analytics and Coaching</strong>. We take all the data captured—the near-misses, the distraction alerts—and turn them into targeted coaching sessions. This allows you to correct unsafe habits and document improvement over time."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.3 Process of Accident Prevention -->
            <h3 class="section-header fade-up">3. Process of Accident Prevention</h3>
            
            <div class="prevention-visual fade-up">
                <div class="prevention-title">The Process of Accident Prevention</div>
                
                <div class="timeline-container">
                    <div class="timeline-line"></div>
                    
                    <!-- Step 1 -->
                    <div class="timeline-step">
                        <div class="step-percent">10%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">Longterm</div>
                        <div class="step-card-header">Driver<br>Coaching</div>
                        <div class="step-card-body border-blue">
                            <ul>
                                <li>Utilizing driver behavior data to conduct targeted coaching to reduce driving risk in the long term</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 2 -->
                    <div class="timeline-step">
                        <div class="step-percent">20%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">30 Minutes</div>
                        <div class="step-card-header">Realtime<br>Intervention</div>
                        <div class="step-card-body border-orange">
                            <ul>
                                <li>Identify significant cognitive capability decline before the driver falls asleep and providing a window of intervention</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 3 -->
                    <div class="timeline-step">
                        <div class="step-percent">10%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">2 Seconds</div>
                        <div class="step-card-header">Realtime<br>Alerting</div>
                        <div class="step-card-body border-orange">
                            <ul>
                                <li>Identify critical risk with edge AI and provide real time alert to the driver to prevent accidents</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 4 -->
                    <div class="timeline-step">
                        <div class="step-percent">20%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">1 Second</div>
                        <div class="step-card-header">Automatic<br>Emergency Braking</div>
                        <div class="step-card-body border-yellow">
                            <ul>
                                <li>Activate vehicle brake on behalf of driver in imminent collision risk to prevent accidents</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (Slide: The Process of Accident Prevention)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Now that we've walked through the entire closed-loop journey of a vehicle, let's zoom in on the core goal: how we actually prevent accidents within that loop. This slide shows how accident prevention works across different time horizons, and why relying on just one safety feature isn't enough.<br><br>
                        Starting from the left, <strong>long-term driver coaching</strong> is about sustainable behavior change. It addresses about <strong>10%</strong> of prevention by using driver behavior data to run targeted coaching, reduce repeat risky habits, and lower risk over weeks and months.<br><br>
                        Next is a much shorter window: <strong>30 minutes — real-time intervention</strong>, around <strong>20%</strong>. This is where the system detects early signs of cognitive decline—like fatigue patterns—before a driver actually falls asleep, and creates a window where the fleet or the driver can intervene proactively.<br><br>
                        Then we move into the moment that matters most on the road: <strong>2 seconds — real-time alerting</strong>, about <strong>10%</strong>. Here, edge AI identifies critical risk and gives the driver an immediate alert, aiming to prevent the incident before it happens.<br><br>
                        Finally, the last line of defense is the shortest: <strong>1 second — automatic emergency braking</strong>, around <strong>20%</strong>. This is when the vehicle activates braking on behalf of the driver during imminent collision risk to prevent or reduce impact.<br><br>
                        So the key takeaway is this: <strong>accident prevention is a layered process</strong>. Coaching reduces long-term risk, intervention catches early warning signs, alerting prevents immediate hazards, and emergency braking is the last safeguard when time is nearly zero. To make this closed loop a reality, let's look at the specific Streamax hardware and software solutions that power each of these defensive layers.
                    </div>
                </div>
            </div>

            <!-- Subsection 3.4 Product Solution Details -->
            <h3 class="section-header fade-up">4. Product Solution Details</h3>
            
            <!-- Pillar 1 -->
            <div class="card fade-up">
                <h4 style="color: var(--primary-green); margin-bottom: 15px;">Pillar 1: Video Telematics (AD Plus 2.0, AD Max, C6 Lite 2.0, GT1 Pro + DC Max)</h4>
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me start with <strong>Video Telematics</strong>.<br><br>
                        The problem we solve is simple: when something happens on the road, fleets need two things immediately—<strong>the truth</strong> and <strong>a repeatable way to prevent it from happening again</strong>.<br>
                        Streamax video telematics is designed to <strong>capture the right evidence</strong>, <strong>surface the right risk signals</strong>, and <strong>turn events into coaching actions</strong>.<br><br>
                        Here’s the loop we illustrate:<br>
                        • <strong>Prevent:</strong> Edge AI detects risky behaviors and critical road events in real time.<br>
                        • <strong>Protect:</strong> Video evidence is recorded reliably so disputes and claims can be resolved faster.<br>
                        • <strong>Improve:</strong> Events feed coaching and continuous improvement so safety performance gets better over time.<br><br>
                        Product-wise, we offer a clear lineup depending on the fleet’s needs:<br><br>
                        <strong>AD Plus 2.0</strong> is our "bread-and-butter" solution for fleets that want high-confidence video telematics with a clean, practical workflow. With <strong>1080p dual lenses</strong>, <strong>integrated onboard memory</strong>, and <strong>eSIM</strong>, it is built to deploy at scale and be used daily by safety and operations teams.<br><br>
                        <strong>AD Max</strong> is for fleets that need more performance: more advanced AI capability, more demanding environments, and more intensity in risk management. The message is simple: when the customer cares about accuracy, responsiveness, and scale, <strong>AD Max is the premium choice</strong>.<br><br>
                        <strong>C6 Lite 2.0</strong> is for fleets that want a balance between AI capability and price. We push engineering to the edge to deliver core ADAS and DSC functions while keeping the solution more economical and video-ready.<br><br>
                        <strong>GT1 Pro + DC Max</strong> is a powerful upgrade path for fleets moving from telematics to video. You start with a capable telematics gateway with dead-reckoning. When you want video and edge AI, you add DC Max on top to extend the gateway into a video telematics solution with minimal disruption.<br><br>
                        Choosing Streamax means you are not choosing the cheapest, and we honor that choice with a clear philosophy: we optimize for <strong>outcomes and total cost of ownership</strong>.<br>
                        Cheap systems become expensive when they miss critical events, create noisy false alerts, or add operational overhead. Our value is reliability, evidence quality, and workflows that teams actually adopt.<br><br>
                        So the close is straightforward: if your priority is <strong>reducing incidents</strong>, <strong>winning claims with evidence</strong>, and <strong>running coaching consistently</strong>, this pillar is your foundation.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "We’re not selling cameras; we’re selling a safety and evidence workflow that scales."<br>
                        • "The best video system is the one your team can use in 30 seconds when an incident happens."<br>
                        • "Total cost of ownership matters more than sticker price in fleet safety."
                    </div>
                </div>
            </div>

            <!-- Pillar 2 -->
            <div class="card fade-up">
                <h4 style="color: var(--secondary-blue); margin-bottom: 15px;">Pillar 2: Asset Security (Z5, Sentinel)</h4>
                <div class="script-box" style="border-left-color: var(--primary-green);">
                    <div class="script-header"><span class="script-tag" style="color: var(--primary-green);">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me talk about <strong>Asset Security</strong>.<br><br>
                        Video telematics reduces liability on the road. Asset security protects your <strong>vehicle, cargo, and business continuity</strong> when assets are parked, unattended, or operating in higher-risk scenarios.<br><br>
                        The loop we use for security is:<br>
                        • <strong>Detect:</strong> Identify abnormal behavior and high-risk situations early.<br>
                        • <strong>Deter:</strong> Make it harder for theft and tampering to succeed.<br>
                        • <strong>Respond:</strong> Provide evidence and visibility so teams can act faster and reduce loss.<br><br>
                        Here is how we position the two products:<br><br>
                        <strong>Z5</strong> is the practical, scalable solution for fleets that want stronger cargo protection and improved cargo efficiency. Its proprietary AI spatial detection supports better cargo load awareness and helps reduce operational delays. With <strong>low-light capability</strong>, Z5 can detect and alert on unauthorized cargo-area access, even in challenging lighting.<br><br>
                        <strong>Sentinel</strong> is our premium, industry-dedicated, always-on guardian. With <strong>AOV camera technology</strong>, Sentinel can continue operating for up to <strong>90 days after ignition-off</strong>. It uses <strong>gesture learning and detection</strong> to wake only when real risk is present. The positioning is simple: it guards valuable assets day and night and notifies you when actual threats are taking place.<br><br>
                        When the buyer asks about ROI, security is one of the clearest paybacks:<br>
                        • One prevented theft incident can offset a meaningful portion of the program cost.<br>
                        • Faster response and better evidence reduce downstream losses and disputes.<br>
                        • Less operational chaos means fewer hidden costs.<br><br>
                        And importantly, asset security integrates naturally with your broader fleet workflow: consistent evidence, consistent operations, and a clear path to scale.<br><br>
                        So if your priority is <strong>protecting vehicles and cargo</strong>, <strong>reducing loss</strong>, and <strong>responding faster when risk appears</strong>, this pillar is built for that job.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "Safety reduces liability; security reduces loss."<br>
                        • "Security fails when response is slow; we shorten the time from detection to action."<br>
                        • "One prevented theft can justify the program."
                    </div>
                </div>
            </div>

            <!-- Pillar 3 -->
            <div class="card fade-up">
                <h4 style="color: var(--primary-green); margin-bottom: 15px;">Pillar 3: Visibility Assistance (BSD, 360 AVM)</h4>
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me introduce <strong>Visibility Assistance</strong>.<br><br>
                        Even good drivers get into trouble when visibility is limited—blind spots, tight yards, complex turns, loading zones, and crowded urban routes. Visibility assistance is about <strong>preventing accidents before they become incidents</strong>, especially the low-speed but high-frequency events that cost fleets time, money, and reputation.<br><br>
                        Here is the loop for visibility products:<br>
                        • <strong>See:</strong> Expand the driver’s awareness in real time.<br>
                        • <strong>Avoid:</strong> Reduce collisions caused by blind spots and low-visibility maneuvers.<br>
                        • <strong>Verify:</strong> Keep a consistent record for incident review and coaching.<br><br>
                        We package this pillar around two solutions:<br><br>
                        <strong>BSD</strong>—Blind Spot Detection—is the clean story for preventing side-impact collisions and lane-change incidents. The simplest way to say it is: <strong>help the driver recognize what they cannot see</strong>, in the moments that matter most.<br><br>
                        <strong>360 AVM</strong>—360 Around View Monitoring—is full situational awareness for tight operations like yards, loading docks, urban stops, and complex vehicles. We use it to <strong>reduce low-speed collisions</strong> and help drivers maneuver with more confidence.<br><br>
                        This pillar also strengthens adoption because it delivers value immediately to drivers:<br>
                        • Drivers feel safer and more supported.<br>
                        • Operations see fewer minor collisions and less downtime.<br>
                        • Safety teams get better context for coaching.<br><br>
                        And it connects back to the broader Streamax value: a consistent workflow and a consistent evidence chain.<br><br>
                        So if your priority is <strong>reducing blind-spot risk</strong>, <strong>cutting low-speed collisions</strong>, and <strong>improving driver confidence</strong>, this pillar is designed to deliver that impact.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "Most accidents are visibility problems before they are driving problems."<br>
                        • "A lot of cost comes from small collisions; 360 visibility reduces those repeatable losses."<br>
                        • "Drivers adopt what helps them immediately."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.5 ROI -->
            <h3 class="section-header blue fade-up">5. The Results (ROI)</h3>
            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Speaker Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "So, what does this technology actually deliver? It delivers results.<br><br>
                        By layering these technologies—coaching, cognitive risk indicators, edge-AI alerts, and active assistance—our customers typically see up to a <strong>60% reduction in preventable incidents</strong>.<br><br>
                        Every fleet is different, but when you put detection, assistance, and coaching into one closed loop, the safety gains are consistent, and they stick."
                    </div>
                </div>
            </div>

        </div>

        <!-- SECTION: VALUE CALCULATOR -->
        <div id="value-calculator" class="content-section hidden">
            <div class="card fade-up">
                <h2 class="gradient-text">Value Calculator</h2>
                <p>Calculate your expected return on investment and subscription costs using our advanced analytics tools.</p>
            </div>

            <div class="sub-nav-tabs fade-up">
                <button class="sub-nav-btn active" onclick="switchSubTab('tco-calc', this)">
                    <i data-lucide="calculator"></i> TCO Calculator
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('sub-calc', this)">
                    <i data-lucide="credit-card"></i> Subscription Calculator
                </button>
            </div>

            <!-- TCO CALCULATOR SUB-SECTION -->
            <div id="tco-calc" class="sub-content active">
                <div class="max-w-6xl w-full mx-auto glass-card overflow-visible fade-up delay-1">
                    <!-- Header -->
                    <div class="p-8 md:p-12 text-center border-b border-white/10 relative overflow-hidden rounded-t-2xl">
                        <!-- Decorative glow behind title -->
                        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-full bg-gradient-to-b from-[#2AF598]/10 to-transparent blur-3xl -z-10"></div>
                        
                        <h1 class="text-3xl md:text-5xl font-bold mb-4 tracking-tight">
                            Streamax <span class="text-gradient">Advanced TCO</span> Calculator
                        </h1>
                        <p class="text-[var(--text-grey)] text-base md:text-lg max-w-3xl mx-auto font-light leading-relaxed">
                            Tweak fleet metrics and advanced performance variables to discover your comprehensive projected ROI. See the exact formulas driving your savings below.
                        </p>
                    </div>
            
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-0 relative">
                        <!-- Decorative center line -->
                        <div class="hidden md:block absolute left-1/2 top-10 bottom-10 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent -translate-x-1/2"></div>
            
                        <!-- Input Section -->
                        <div class="p-8 md:p-10 lg:p-14 border-b md:border-b-0 md:border-r border-white/10 fade-up delay-2">
                            <h2 class="text-xl font-semibold mb-8 flex items-center text-white">
                                <i class="fas fa-sliders-h text-[var(--primary-green)] mr-3"></i> Fleet Parameters
                            </h2>
                            
                            <form id="calculator-form" class="space-y-6">
                                <!-- Basic Variables -->
                                <div class="glass-panel p-5">
                                    <label class="block text-sm font-medium text-[var(--text-grey)] mb-3">Vehicle Breakdown</label>
                                    <div class="grid grid-cols-3 gap-4">
                                        <div>
                                            <label class="flex items-center text-xs text-gray-400 mb-2">
                                                HDV
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-52 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Class 7-8 (Tractor-trailers)</strong>Highest resource usage. Applies a <span class="text-[var(--primary-green)]">1.5x</span> impact multiplier.
                                                        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <input type="number" id="hdvSize" value="20" min="0" class="w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-hdv')" onblur="unhighlight('f-hdv')">
                                        </div>
                                        <div>
                                            <label class="flex items-center text-xs text-gray-400 mb-2">
                                                MDV
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-52 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Class 4-6 (Box trucks)</strong>Standard usage. Applies a <span class="text-[var(--primary-green)]">1.0x</span> baseline multiplier.
                                                        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <input type="number" id="mdvSize" value="15" min="0" class="w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-mdv')" onblur="unhighlight('f-mdv')">
                                        </div>
                                        <div>
                                            <label class="flex items-center text-xs text-gray-400 mb-2">
                                                LDV
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                    <div class="absolute bottom-full right-0 mb-2 w-52 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Class 1-3 (Vans/Pickups)</strong>Lowest usage. Applies a <span class="text-[var(--primary-green)]">0.5x</span> multiplier.
                                                        <div class="absolute top-full right-4 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <input type="number" id="ldvSize" value="15" min="0" class="w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-ldv')" onblur="unhighlight('f-ldv')">
                                        </div>
                                    </div>
                                </div>
            
                                <div>
                                    <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Annual Miles per Vehicle</label>
                                    <div class="relative">
                                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                            <i class="fas fa-road text-gray-500"></i>
                                        </div>
                                        <input type="number" id="avgMiles" value="50000" min="0" class="pl-10 w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-miles')" onblur="unhighlight('f-miles')">
                                    </div>
                                </div>
            
                                <div class="grid grid-cols-2 gap-5">
                                    <div>
                                        <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Current Avg MPG</label>
                                        <input type="number" id="mpg" value="6.5" min="0.1" step="0.1" class="w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-mpg')" onblur="unhighlight('f-mpg')">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Fuel Price ($/gal)</label>
                                        <div class="relative">
                                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                            <input type="number" id="fuelPrice" value="4.00" min="0" step="0.01" class="pl-8 w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-fuelprice')" onblur="unhighlight('f-fuelprice')">
                                        </div>
                                    </div>
                                </div>
            
                                <div class="grid grid-cols-2 gap-5">
                                    <div>
                                        <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Accidents per Year</label>
                                        <input type="number" id="accidents" value="5" min="0" class="w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-accidents')" onblur="unhighlight('f-accidents')">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Avg. Accident Cost</label>
                                        <div class="relative">
                                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                            <input type="number" id="accidentCost" value="15000" min="0" step="1000" class="pl-8 w-full rounded-lg py-2.5 px-3" oninput="calculateROI()" onfocus="highlight('f-acccost')" onblur="unhighlight('f-acccost')">
                                        </div>
                                    </div>
                                </div>
            
                                <!-- Advanced Variables (Collapsible) -->
                                <details class="group glass-panel overflow-visible mt-2">
                                    <summary class="flex justify-between items-center font-medium cursor-pointer text-gray-300 hover:text-white p-4 transition-colors">
                                        <span class="flex items-center tracking-wide"><i class="fas fa-cogs mr-3 text-[var(--secondary-blue)]"></i> Advanced Estimations</span>
                                        <span class="transition-transform group-open:-rotate-180 text-gray-500">
                                            <i class="fas fa-chevron-down"></i>
                                        </span>
                                    </summary>
                                    <div class="p-5 space-y-5 border-t border-white/5">
                                        <div class="grid grid-cols-2 gap-5 overflow-visible">
                                            <div>
                                                <label class="flex items-center text-xs font-medium text-gray-400 mb-2">
                                                    Fuel Gain (0-1)
                                                    <div class="relative ml-1 inline-flex items-center z-20">
                                                        <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                            <strong class="text-white block mb-1">Suggested: 0.05 - 0.15</strong>Industry metrics indicate fleets often save 5-15% through idle reduction and routing.
                                                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                        </div>
                                                    </div>
                                                </label>
                                                <input type="number" id="fuelGain" value="0.10" min="0" max="1" step="0.01" class="w-full text-sm rounded-lg py-2 px-3" oninput="calculateROI()" onfocus="highlight('f-fuelgain')" onblur="unhighlight('f-fuelgain')">
                                            </div>
                                            <div>
                                                <label class="flex items-center text-xs font-medium text-gray-400 mb-2">
                                                    Accident Red. (0-1)
                                                    <div class="relative ml-1 inline-flex items-center z-20">
                                                        <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                            <strong class="text-white block mb-1">Suggested: 0.20 - 0.50</strong>Video telematics generally reduce accident rates by up to 50% via driver coaching.
                                                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                        </div>
                                                    </div>
                                                </label>
                                                <input type="number" id="accReduction" value="0.40" min="0" max="1" step="0.01" class="w-full text-sm rounded-lg py-2 px-3" oninput="calculateROI()" onfocus="highlight('f-accreduce')" onblur="unhighlight('f-accreduce')">
                                            </div>
                                        </div>
            
                                        <div class="grid grid-cols-2 gap-5 pt-2">
                                            <div>
                                                <label class="block text-xs font-medium text-gray-400 mb-2">Base Premium / Veh</label>
                                                <input type="number" id="insurancePrem" value="2500" min="0" step="100" class="w-full text-sm rounded-lg py-2 px-3" oninput="calculateROI()" onfocus="highlight('f-insprem')" onblur="unhighlight('f-insprem')">
                                            </div>
                                            <div>
                                                <label class="flex items-center text-xs font-medium text-gray-400 mb-2">
                                                    Premium Red. (0-1)
                                                    <div class="relative ml-1 inline-flex items-center z-20">
                                                        <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                        <div class="absolute bottom-full right-0 mb-2 w-56 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                            <strong class="text-white block mb-1">Suggested: 0.05 - 0.15</strong>Commercial providers often offer premium discounts ~10% for utilizing AI dashcams.
                                                            <div class="absolute top-full right-4 border-4 border-transparent tooltip-arrow-border"></div>
                                                        </div>
                                                    </div>
                                                </label>
                                                <input type="number" id="insuranceRed" value="0.10" min="0" max="1" step="0.01" class="w-full text-sm rounded-lg py-2 px-3" oninput="calculateROI()" onfocus="highlight('f-insreduce')" onblur="unhighlight('f-insreduce')">
                                            </div>
                                        </div>
                                    </div>
                                </details>
                            </form>
                        </div>
            
                        <!-- Output Section -->
                        <div class="p-8 md:p-10 lg:p-14 flex flex-col justify-start rounded-b-2xl md:rounded-bl-none md:rounded-br-2xl fade-up delay-3 relative">
                            <h2 class="text-xl font-semibold mb-8 flex items-center text-white">
                                <i class="fas fa-chart-line text-[var(--secondary-blue)] mr-3"></i> Estimated Annual Savings
                            </h2>
            
                            <div class="space-y-4 mb-8">
                                <!-- Neon tinted output cards -->
                                <div class="flex justify-between items-center p-4 rounded-xl border border-[#2AF598]/30 bg-[#2AF598]/5 backdrop-blur-sm shadow-[0_0_15px_rgba(42,245,152,0.05)] transition-all">
                                    <span class="text-sm font-medium text-gray-300">Fuel Efficiency</span>
                                    <span class="text-xl font-bold text-[var(--primary-green)] drop-shadow-[0_0_8px_rgba(42,245,152,0.4)]" id="out-fuel">$0</span>
                                </div>
            
                                <div class="flex justify-between items-center p-4 rounded-xl border border-[#009EFD]/30 bg-[#009EFD]/5 backdrop-blur-sm shadow-[0_0_15px_rgba(0,158,253,0.05)] transition-all">
                                    <span class="text-sm font-medium text-gray-300">Safety & Liability</span>
                                    <span class="text-xl font-bold text-[var(--secondary-blue)] drop-shadow-[0_0_8px_rgba(0,158,253,0.4)]" id="out-safety">$0</span>
                                </div>
            
                                <div class="flex justify-between items-center p-4 rounded-xl border border-purple-500/30 bg-purple-500/5 backdrop-blur-sm shadow-[0_0_15px_rgba(168,85,247,0.05)] transition-all">
                                    <span class="text-sm font-medium text-gray-300">Insurance Premiums</span>
                                    <span class="text-xl font-bold text-purple-400 drop-shadow-[0_0_8px_rgba(168,85,247,0.4)]" id="out-insurance">$0</span>
                                </div>
            
                                <div class="pt-6 mt-6 border-t border-white/10">
                                    <div class="flex justify-between items-end">
                                        <span class="text-base font-medium text-[var(--text-grey)] uppercase tracking-wider text-xs">Total Projected ROI</span>
                                        <span class="text-4xl font-extrabold text-gradient drop-shadow-[0_0_15px_rgba(42,245,152,0.3)]" id="out-total">$0</span>
                                    </div>
                                </div>
                            </div>
            
                            <!-- Interactive Formula Display (MathJax LaTeX) -->
                            <div class="sticky bottom-0 z-50 mt-auto glass-panel p-5 overflow-x-auto fade-up delay-4 shadow-[0_-10px_30px_rgba(0,0,0,0.8)]" style="background: rgba(11, 18, 33, 0.95); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-top: 1px solid var(--primary-green);">
                                <h3 class="text-gray-300 font-semibold mb-4 text-sm flex items-center">
                                    <i class="fas fa-square-root-alt mr-2 text-[var(--primary-green)]"></i> Live Computation Matrix
                                </h3>
                                
                                <div class="text-center pb-2 text-[0.8rem] space-y-2 text-gray-400">
                                    $V_{total} = \class{var-f-hdv}{V_{HD}} + \class{var-f-mdv}{V_{MD}} + \class{var-f-ldv}{V_{LD}}$<br><br>
                                    $V_{wt} = 1.5\class{var-f-hdv}{V_{HD}} + 1.0\class{var-f-mdv}{V_{MD}} + 0.5\class{var-f-ldv}{V_{LD}}$<br><br>
                                    $I_{avg} = \frac{V_{wt}}{V_{total}}$<br><br>
                                    $\text{Fuel}_{save} = \left( \frac{V_{total} \times \class{var-f-miles}{M_{avg}}}{\class{var-f-mpg}{MPG}} \right) \times \class{var-f-fuelprice}{P_{fuel}} \times \class{var-f-fuelgain}{G_{fuel}} \times I_{avg}$<br><br>
                                    $\text{Safety}_{save} = \class{var-f-accidents}{A_{yr}} \times \class{var-f-acccost}{C_{acc}} \times \class{var-f-accreduce}{R_{acc}} \times I_{avg}$<br><br>
                                    $\text{Ins}_{save} = V_{wt} \times \class{var-f-insprem}{P_{ins}} \times \class{var-f-insreduce}{R_{ins}}$
                                </div>
                            </div>
            
                        </div>
                    </div>
                </div>
            </div>

            <!-- SUBSCRIPTION CALCULATOR SUB-SECTION -->
            <div id="sub-calc" class="sub-content">
                <div class="card fade-up" style="min-height: 400px; display: flex; justify-content: center; align-items: center;">
                    <p style="color: var(--text-grey); font-size: 1.1rem;"><i class="fa-solid fa-person-digging" style="margin-right: 8px;"></i> Subscription Calculator module coming soon.</p>
                </div>
            </div>
        </div>

        <div style="height: 100px;"></div>
    </div>

    <!-- Toast Notification -->
    <div id="toast">Copied to Clipboard!</div>

    <script>
        // --- ICONS INITIALIZATION ---
        lucide.createIcons();

        // --- TAB SWITCHING LOGIC ---
        function switchTab(tabId, btnElement) {
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            if (btnElement) {
                btnElement.classList.add('active');
            } else if (event && event.currentTarget) {
                event.currentTarget.classList.add('active');
            }

            document.querySelectorAll('.content-section').forEach(section => section.classList.add('hidden'));
            
            const activeSection = document.getElementById(tabId);
            if (activeSection) {
                activeSection.classList.remove('hidden');
                
                // Re-trigger fade animations
                const elements = activeSection.querySelectorAll('.fade-up');
                elements.forEach(el => {
                    el.classList.remove('visible');
                    setTimeout(() => el.classList.add('visible'), 50);
                });
                observeElements(); 

                // Trigger MathJax re-render for formulas hidden on initial load
                if (tabId === 'value-calculator' && window.MathJax && MathJax.typesetPromise) {
                    MathJax.typesetPromise();
                }
            }
        }

        // --- SUB-TAB SWITCHING LOGIC ---
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

                // Ensure MathJax renders if they switch directly to the sub-tab
                if (tabId === 'tco-calc' && window.MathJax && MathJax.typesetPromise) {
                    MathJax.typesetPromise();
                }
            }
        }

        // --- COPY TO CLIPBOARD ---
        function copyText(btnElement) {
            const textToCopy = btnElement.closest('.script-header').nextElementSibling.innerText;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const toast = document.getElementById("toast");
                toast.className = "show";
                setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 3000);
            });
        }

        // --- SCROLL OBSERVER ---
        function observeElements() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) entry.target.classList.add('visible');
                });
            }, { threshold: 0.1 });
            document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));
        }

        document.addEventListener('DOMContentLoaded', () => {
            observeElements();
            setTimeout(() => { document.querySelectorAll('#prospecting-flow .fade-up').forEach(el => el.classList.add('visible')); }, 100);
            
            // Init Visual Loop
            initLoopVisual();

            // Initialize TCO Calculator on load
            calculateROI();
        });

        // --- VALUE CALCULATOR JS LOGIC ---
        const formatCurrency = (num) => {
            return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);
        };

        function highlight(varClass) {
            const elements = document.querySelectorAll('.var-' + varClass);
            elements.forEach(el => {
                el.classList.add('highlighted-var');
            });
        }

        function unhighlight(varClass) {
            const elements = document.querySelectorAll('.var-' + varClass);
            elements.forEach(el => {
                el.classList.remove('highlighted-var');
            });
        }

        function calculateROI() {
            // Fleet Sizes
            const hdv = Math.max(0, parseFloat(document.getElementById('hdvSize').value) || 0);
            const mdv = Math.max(0, parseFloat(document.getElementById('mdvSize').value) || 0);
            const ldv = Math.max(0, parseFloat(document.getElementById('ldvSize').value) || 0);
            const fleetSize = hdv + mdv + ldv;

            // Duty Impact Factors
            const impactHD = 1.5;
            const impactMD = 1.0;
            const impactLD = 0.5;
            
            const weightedFleet = (hdv * impactHD) + (mdv * impactMD) + (ldv * impactLD);
            const avgImpact = fleetSize > 0 ? (weightedFleet / fleetSize) : 1;

            // Operational Parameters
            const avgMiles = Math.max(0, parseFloat(document.getElementById('avgMiles').value) || 0);
            const mpg = Math.max(0.1, parseFloat(document.getElementById('mpg').value) || 1); 
            const fuelPrice = Math.max(0, parseFloat(document.getElementById('fuelPrice').value) || 0);
            const accidents = Math.max(0, parseFloat(document.getElementById('accidents').value) || 0);
            const accidentCost = Math.max(0, parseFloat(document.getElementById('accidentCost').value) || 0);

            // Advanced Parameters with constraints [0, 1] enforced for calculations
            const fuelGainPct = Math.min(1, Math.max(0, parseFloat(document.getElementById('fuelGain').value) || 0));
            const accReductionPct = Math.min(1, Math.max(0, parseFloat(document.getElementById('accReduction').value) || 0));
            const insurancePrem = Math.max(0, parseFloat(document.getElementById('insurancePrem').value) || 0);
            const insuranceRedPct = Math.min(1, Math.max(0, parseFloat(document.getElementById('insuranceRed').value) || 0));

            // Calculations incorporating the new Duty Impact Factor
            const totalGallons = (fleetSize * avgMiles) / mpg;
            const totalFuelCost = totalGallons * fuelPrice;
            const fuelSavings = totalFuelCost * fuelGainPct * avgImpact;

            const totalAccidentCost = accidents * accidentCost;
            const safetySavings = totalAccidentCost * accReductionPct * avgImpact;

            const insuranceSavings = weightedFleet * insurancePrem * insuranceRedPct;

            const totalSavings = fuelSavings + safetySavings + insuranceSavings;

            // Update DOM Outputs
            const outFuel = document.getElementById('out-fuel');
            const outSafety = document.getElementById('out-safety');
            const outInsurance = document.getElementById('out-insurance');
            const outTotal = document.getElementById('out-total');

            if(outFuel) outFuel.textContent = formatCurrency(fuelSavings);
            if(outSafety) outSafety.textContent = formatCurrency(safetySavings);
            if(outInsurance) outInsurance.textContent = formatCurrency(insuranceSavings);
            if(outTotal) outTotal.textContent = formatCurrency(totalSavings);
        }

        // --- VISUAL LOOP LOGIC ---
        function initLoopVisual() {
            const CAPSULE_R = 25; // Vertical Radius %
            const CAPSULE_S = 20; // Straight Line Half-Length %
            const nodesLayer = document.getElementById('nodes-layer');
            const labelsLayer = document.getElementById('labels-layer');
            const runner = document.getElementById('running-element');
            const scene = document.getElementById('scene');
            
            if (!nodesLayer || !scene) return; // Guard against missing elements if tab hidden initially

            const phases = [
                { text: "Departure", angle: 230 }, { text: "Pre-Ship", angle: 300 },     
                { text: "Shipping", angle: 35 },   { text: "Arriving", angle: 100 }, { text: "Post-Trip", angle: 140 }     
            ];

            const nodes = [
                { title: "Compliance", icon: "fa-file-shield", angle: 215, desc: ["Regional Compliance", "Hardware Self-Check"] },
                { title: "Driver ID", icon: "fa-id-card", angle: 245, desc: ["Multi-Factor Auth", "Alcohol Detection"] },
                { id: "cargo", title: "Cargo Loading", icon: "fa-truck-loading", angle: 275, desc: ["Occupancy Measure", "Loading Monitor"] },
                { title: "Status", icon: "fa-clipboard-check", angle: 305, desc: ["Health Check", "DTCs"] },
                { title: "Starting", icon: "fa-key", angle: 335, desc: ["Front Blind Spot", "Ignition Monitor"] },
                { title: "Driving", icon: "fa-road", angle: 10, desc: ["DMS / ADAS", "Realtime Alerts"] },
                { title: "Turning", icon: "fa-share", angle: 45, desc: ["Side Blind Spot", "Pedestrian Detect"] },
                { title: "Parking", icon: "fa-square-parking", angle: 80, desc: ["Theft Detection", "Perimeter Guard"] },
                { title: "Unloading", icon: "fa-truck-ramp-box", angle: 125, desc: ["Rear Visibility", "Cargo Counting"] },
                { title: "Coaching", icon: "fa-user-graduate", angle: 170, desc: ["Driver Scorecard", "Event Review"] }
            ];

            function getCapsulePoint(angleDeg) {
                let deg = angleDeg % 360;
                if (deg < 0) deg += 360;
                const rad = deg * (Math.PI / 180);
                const rayX = Math.cos(rad);
                const rayY = Math.sin(rad);
                let x, y, rotation;

                if (Math.abs(rayY) > 0.01) {
                    const yLine = (rayY > 0) ? CAPSULE_R : -CAPSULE_R;
                    const xIntersect = yLine / (rayY / rayX);
                    if (Math.abs(xIntersect) <= CAPSULE_S) {
                        x = xIntersect; y = yLine; rotation = (yLine < 0) ? 0 : Math.PI;
                    }
                }
                if (x === undefined) {
                    const isRight = (rayX > 0);
                    const circleCenter = isRight ? CAPSULE_S : -CAPSULE_S;
                    const B = -2 * circleCenter * rayX;
                    const C = (circleCenter * circleCenter) - (CAPSULE_R * CAPSULE_R);
                    const det = B*B - 4*C;
                    if (det >= 0) {
                        const t = (-B + Math.sqrt(det)) / 2;
                        x = t * rayX; y = t * rayY;
                        const nx = x - circleCenter;
                        rotation = Math.atan2(y, nx) + Math.PI/2;
                    }
                }
                if (x === undefined) { x = 0; y = 0; rotation = 0; }
                return { xPct: 50 + x, yPct: 50 + y, rotation: rotation };
            }

            // Render Paths
            const S = CAPSULE_S, R = CAPSULE_R;
            const d = `M ${50-S} ${50-R} L ${50+S} ${50-R} A ${R} ${R} 0 0 1 ${50+S} ${50+R} L ${50-S} ${50+R} A ${R} ${R} 0 0 1 ${50-S} ${50-R} Z`;
            document.getElementById('roadBase').setAttribute('d', d);
            document.getElementById('roadLane').setAttribute('d', d);

            // Render Nodes
            nodesLayer.innerHTML = ''; // Clear existing to prevent dupes if function recalled
            nodes.forEach(node => {
                const el = document.createElement('div');
                const pos = getCapsulePoint(node.angle);
                const isTopHalf = (pos.yPct < 50);
                const popClass = isTopHalf ? 'pop-down' : 'pop-up';
                
                el.className = `node-container ${popClass}`;
                el.style.left = `${pos.xPct}%`; el.style.top = `${pos.yPct}%`;
                el.innerHTML = `
                    <div class="node-visual"><i class="fa-solid ${node.icon}"></i></div>
                    <div class="node-static-label">${node.title}</div>
                    <div class="popup-card">
                        <div class="popup-header"><i class="fa-solid ${node.icon}"></i> ${node.title}</div>
                        <ul class="popup-list">${node.desc.map(d => `<li>${d}</li>`).join('')}</ul>
                    </div>`;
                nodesLayer.appendChild(el);
            });

            // Render Labels
            labelsLayer.innerHTML = ''; // Clear existing
            phases.forEach(phase => {
                const el = document.createElement('div');
                el.className = 'phase-label';
                const rad = phase.angle * (Math.PI / 180);
                const pos = getCapsulePoint(phase.angle);
                // Simple radial offset for labels
                const xOff = 10 * Math.cos(rad); 
                const yOff = 10 * Math.sin(rad);
                el.style.left = `${pos.xPct + xOff}%`; el.style.top = `${pos.yPct + yOff}%`;
                el.innerText = phase.text;
                labelsLayer.appendChild(el);
            });

            // Interaction
            scene.addEventListener('mousemove', (e) => {
                const rect = scene.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const rad = Math.atan2(e.clientY - centerY, e.clientX - centerX);
                let deg = rad * (180 / Math.PI);
                if (deg < 0) deg += 360;

                const pos = getCapsulePoint(deg);
                runner.style.left = pos.xPct + '%';
                runner.style.top = pos.yPct + '%';
                runner.style.transform = `translate(-50%, -50%) rotate(${pos.rotation}rad)`;

                const iconElement = runner.querySelector('i');
                if (deg >= 125 && deg <= 335) {
                    if (!iconElement.classList.contains('fa-person-walking')) iconElement.className = 'fa-solid fa-person-walking';
                } else {
                    if (!iconElement.classList.contains('fa-truck-fast')) iconElement.className = 'fa-solid fa-truck-fast';
                }
            });
        }
    </script>
</body>
</html>"""

# Render the HTML toolkit natively inside Streamlit
# We use a large viewport height and enable scrolling so all sections are accessible
components.html(html_code, height=1500, scrolling=True)
