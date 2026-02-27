import streamlit as st
import streamlit.components.v1 as components

# Import the HTML contents from the modular section files
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

# The HTML head, styling, and structural shell
html_head = r"""<!DOCTYPE html>
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
            <button class="nav-btn active" onclick="switchTab('streamaxpedia', this)">
                <i data-lucide="book-open"></i> Streamaxpedia
            </button>
            <button class="nav-btn" onclick="switchTab('prospecting-flow', this)">
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
"""

# The HTML scripts and closing tags
html_tail = r"""
        <div style="height: 100px;"></div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" style="visibility: hidden; min-width: 250px; background-color: var(--primary-green); color: #050810; text-align: center; border-radius: 8px; padding: 16px; position: fixed; z-index: 1000; left: 50%; bottom: 30px; transform: translateX(-50%); font-weight: bold; box-shadow: 0 0 20px rgba(42, 245, 152, 0.4); opacity: 0; transition: opacity 0.3s;">Copied to Clipboard!</div>

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
            document.execCommand('copy'); // Fallback for iFrame usage
            navigator.clipboard.writeText(textToCopy).then(() => {
                const toast = document.getElementById("toast");
                toast.style.visibility = "visible";
                toast.style.opacity = "1";
                setTimeout(function(){ toast.style.opacity = "0"; toast.style.visibility = "hidden"; }, 3000);
            }).catch(err => {
                // If navigator clipboard fails (often does in Streamlit iframe without secure context)
                const textArea = document.createElement("textarea");
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    const toast = document.getElementById("toast");
                    toast.style.visibility = "visible";
                    toast.style.opacity = "1";
                    setTimeout(function(){ toast.style.opacity = "0"; toast.style.visibility = "hidden"; }, 3000);
                } catch (err) {
                    console.error('Fallback: Oops, unable to copy', err);
                }
                document.body.removeChild(textArea);
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
            
            // Set Streamaxpedia as the initial active tab automatically
            const defaultTabBtn = document.querySelector('.nav-tabs button:first-child');
            if (defaultTabBtn) {
                switchTab('streamaxpedia', defaultTabBtn);
            }
            
            // Init Visual Loop
            if (typeof initLoopVisual === 'function') initLoopVisual();

            // Initialize TCO Calculator on load
            if (typeof calculateROI === 'function') calculateROI();
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
</html>
"""

# Reconstruct the entire HTML by appending all the modular pieces
html_code = (
    html_head + "\n" +
    streamaxpedia_content + "\n" +
    prospecting_flow_content + "\n" +
    discovery_meeting_content + "\n" +
    presentation_content + "\n" +
    value_calculator_content + "\n" +
    html_tail
)

# Render the HTML toolkit natively inside Streamlit
# We use a large viewport height and enable scrolling so all sections are accessible
components.html(html_code, height=1800, scrolling=True)
