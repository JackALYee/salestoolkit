import json
import os
import base64
import re
import itertools
from terminology_db import TERMINOLOGY_DB, PRODUCT_COMBINATIONS

# --- 1. RECURSIVE ARCHITECTURE PARSER & CLEANUP ---
ALL_PRODUCTS_SET = set()

for combo in PRODUCT_COMBINATIONS:
    raw = combo["composition"]
    
    # Standardize string
    text = raw.replace('（', '(').replace('）', ')').replace('＋', '+')
    
    # Normalize common component names so they don't break logic
    text = text.replace('Power Box Max', 'PBM')
    text = text.replace('C6 Lite2.0', 'C6 Lite 2.0')
    text = text.replace('M1N2.0', 'M1N 2.0')
    text = text.replace('C6D7.0', 'C6D 7.0')
    text = text.replace('X3NPro', 'X3N Pro')
    text = text.replace('CA42kit', 'CA42 Kit 2.0')
    
    # FIX: Handle known DB typo in architecture formula where a stray brace was left after parenthesis
    text = text.replace(') }', ')') 
    
    combo["composition"] = text # Crucial for UI matching!
    
    # Extract parenthesis notes
    notes = re.findall(r'\((.*?)\)', text)
    clean = re.sub(r'\(.*?\)', '', text)
    
    # Extract smart loose Chinese (e.g. "存储4宫格") and treat as notes
    loose_chinese = re.findall(r'[\u4e00-\u9fff]+[^\+/{}]*', clean)
    notes.extend([lc.strip() for lc in loose_chinese if lc.strip()])
    
    # Strip loose Chinese and ANY preceding dash/hyphen/space so it doesn't leave "C53-"
    clean = re.sub(r'[-_\s]*[\u4e00-\u9fff]+[^\+/{}\*]*', '', clean)
    clean = re.sub(r'\bor\b', '/', clean)
    combo["notes"] = notes
    
    # Recursive parsing to handle {}, +, and / logic correctly
    def split_outside(s, chars):
        parts, curr, depth = [], [], 0
        for c in s:
            if c == '{': depth += 1
            elif c == '}': depth -= 1
            
            if depth < 0: depth = 0 # Prevent unbalanced brackets from destroying parser
            
            if c in chars and depth == 0:
                parts.append("".join(curr))
                curr = []
            else:
                curr.append(c)
        parts.append("".join(curr))
        return parts

    def parse_expr(s):
        # 1. Base layer is addition (+)
        terms = split_outside(s, ['+'])
        term_combos = []
        for t in terms:
            # 2. Sub-layer is alternatives (/)
            alts = split_outside(t, ['/'])
            alt_res = []
            for a in alts:
                a = a.strip()
                if not a: continue
                # 3. If grouped, recursively unpack
                if a.startswith('{') and a.endswith('}'):
                    alt_res.extend(parse_expr(a[1:-1]))
                else:
                    # Strip multipliers gracefully whether they are *4 or 1*
                    a_clean = re.sub(r'\b\d+\s*\*', '', a)
                    a_clean = re.sub(r'\*\s*\d+\b', '', a_clean)
                    
                    # Hard strip any final brackets that leaked from typos in the raw string
                    a_clean = a_clean.replace('{', '').replace('}', '').strip()
                    
                    if a_clean:
                        alt_res.append([a_clean])
            if alt_res:
                term_combos.append(alt_res)
        
        # Cross product to build all valid subset permutations
        res = []
        for c in itertools.product(*term_combos):
            flat = []
            for lst in c:
                flat.extend(lst)
            res.append(flat)
        return res
        
    combos = parse_expr(clean)
    valid_sets = []
    products_involved = set()
    
    for c in combos:
        unique_set = []
        for item in c:
            # Bulletproof filter: Split by + or / again to ensure absolutely NO compound strings make it to Component Library
            safe_items = [x.strip() for x in re.split(r'[\+/]', item) if x.strip()]
            for si in safe_items:
                if si not in unique_set:
                    unique_set.append(si)
                    
        unique_set = sorted(list(set(unique_set)))
        if unique_set not in valid_sets:
            valid_sets.append(unique_set)
        products_involved.update(unique_set)
        ALL_PRODUCTS_SET.update(unique_set)
        
    combo["valid_sets"] = valid_sets
    combo["products_involved"] = list(products_involved)

    # Auto-link Knowledge Graph
    for prod_name in products_involved:
        db_entry = next((item for item in TERMINOLOGY_DB if item.get("term", "").lower() == prod_name.lower()), None)
        if not db_entry:
            db_entry = {
                "term": prod_name, 
                "category": "Auto-Discovered Component", 
                "desc": "Component dynamically extracted from the Master Product Matrix.", 
                "related": []
            }
            TERMINOLOGY_DB.append(db_entry)
        
        if "related" not in db_entry:
            db_entry["related"] = []
            
        for other_prod in products_involved:
            if prod_name != other_prod and other_prod not in db_entry["related"]:
                db_entry["related"].append(other_prod)

# Sanitize Data for Frontend
for item in TERMINOLOGY_DB:
    item["term"] = str(item.get("term", ""))
    item["desc"] = str(item.get("desc", ""))
    item["category"] = str(item.get("category", ""))
    item["exact"] = bool(item.get("exact", False))
    if "related" not in item or not isinstance(item["related"], list):
        item["related"] = []
    item["related"] = [str(r) for r in item["related"] if r]

# Resolve final bidirectional links
for item in TERMINOLOGY_DB:
    if "related" in item:
        for related_term in item["related"]:
            target = next((t for t in TERMINOLOGY_DB if t["term"].lower() == related_term.lower()), None)
            if target:
                if item["term"] not in target["related"]:
                    target["related"].append(item["term"])

# Export sorted list (longest first, to prevent tokenizing bugs in JS)
ALL_PRODUCTS = sorted(list(ALL_PRODUCTS_SET), key=len, reverse=True)


db_json = json.dumps(TERMINOLOGY_DB)
matrix_json = json.dumps(PRODUCT_COMBINATIONS)
products_json = json.dumps(ALL_PRODUCTS)

# Ensure robust path resolution for GitHub / Streamlit Cloud deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "关于严禁核心技术资料公网发布的安全管控通知-CN.pdf")

pdf_base64 = ""
try:
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
    else:
        print(f"Streamlit Cloud Warning: PDF not found at {pdf_path}")
except Exception as e:
    print(f"Error reading PDF: {e}")

css_and_html = r"""
        <!-- SECTION: STREAMAXPEDIA -->
        <div id="streamaxpedia" class="content-section hidden">
            <style>
                #streamaxpedia:not(.hidden) { display: flex; flex-direction: column; align-items: center; width: 100%; }
                
                /* --- SEARCH CONTAINER --- */
                .search-wrapper { width: 100%; max-width: 800px; padding: 40px 20px; margin-top: 5vh; display: flex; flex-direction: column; align-items: center; transition: margin-top 0.5s ease; }
                .search-wrapper.active-search { margin-top: 1vh; }

                .title-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 30px; }
                .subtitle-box { text-align: center; margin-top: -15px; margin-bottom: 30px; padding: 0 20px; animation: spediaFadeUp 0.5s ease-out forwards; }
                .temp-note { color: var(--text-grey); font-size: 0.95rem; font-style: italic; margin-bottom: 5px; }
                .credit-line { color: var(--primary-green); font-size: 0.85rem; font-weight: 600; margin-top: 0; letter-spacing: 0.5px; }

                /* --- MASCOT --- */
                .mascot-container { width: 140px; height: 140px; animation: float 4s ease-in-out infinite; perspective: 600px; z-index: 10; filter: drop-shadow(0 15px 20px rgba(42, 245, 152, 0.15)); }
                .mascot { width: 100%; height: 100%; object-fit: contain; transition: transform 0.15s ease-out; transform-origin: center center; }
                .mascot.jumping-heart { animation: heartBounce 0.4s infinite alternate cubic-bezier(0.5, 0.05, 1, 0.5); filter: none;}

                @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-12px); } }
                @keyframes heartBounce { 0% { transform: translateY(0) scale(1); } 100% { transform: translateY(-20px) scale(1.15); } }
                @keyframes spediaFadeUp { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }

                .brand-title { font-size: 3rem; font-weight: 700; text-align: center; letter-spacing: -1px; margin: 0; }

                .search-box { width: 100%; position: relative; display: flex; align-items: center; }
                .search-input { width: 100%; padding: 20px 25px 20px 60px; font-size: 1.2rem; border-radius: 50px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-white); font-family: var(--font-main); backdrop-filter: blur(10px); transition: var(--transition); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); }
                .search-input:focus { outline: none; border-color: var(--primary-green); background: rgba(255, 255, 255, 0.08); box-shadow: 0 0 20px rgba(42, 245, 152, 0.2); }
                .search-icon { position: absolute; left: 25px; font-size: 1.2rem; color: var(--text-grey); transition: var(--transition); }
                .search-input:focus ~ .search-icon { color: var(--primary-green); }
                .clear-icon { position: absolute; right: 25px; font-size: 1.2rem; color: var(--text-grey); cursor: pointer; display: none; transition: var(--transition); }
                .clear-icon:hover { color: var(--text-white); }

                .stats { width: 100%; max-width: 800px; margin: 0 auto 15px auto; padding: 0 20px; color: var(--text-grey); font-size: 0.9rem; display: none; }
                .stats.show { display: block; }
                .stats span { color: var(--primary-green); font-weight: bold; }

                /* --- RESULTS AREA --- */
                .results-container { width: 100%; max-width: 800px; padding: 0 20px 40px; display: flex; flex-direction: column; gap: 16px; }
                .result-card { background: var(--glass-bg); border: var(--glass-border); border-radius: var(--card-radius); padding: 24px; transition: var(--transition); opacity: 0; transform: translateY(10px); animation: spediaFadeUp 0.4s ease-out forwards; position: relative; overflow: hidden; }
                .result-card::before { content: ''; position: absolute; left: 0; top: 0; height: 100%; width: 4px; background: var(--gradient-text); opacity: 0.7; }
                .result-card:hover { background: rgba(255, 255, 255, 0.06); border-color: rgba(42, 245, 152, 0.3); transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); }
                
                .term-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
                .term-title { font-size: 1.4rem; font-weight: 700; color: var(--primary-green); margin:0; }
                .term-category { font-size: 0.75rem; text-transform: uppercase; background: rgba(0, 158, 253, 0.1); color: var(--secondary-blue); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(0, 158, 253, 0.3); }
                .term-desc { font-size: 1rem; color: var(--text-grey); line-height: 1.6; margin-bottom: 10px; }
                .highlight { background: rgba(42, 245, 152, 0.2); color: #2AF598; padding: 2px 4px; border-radius: 4px; }

                .download-btn, .relevance-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 0.85rem; font-weight: 600; cursor: pointer; border: none; transition: var(--transition); }
                .download-btn { background: rgba(42, 245, 152, 0.1); color: var(--primary-green); border: 1px solid var(--primary-green); margin-top: 12px; margin-right: 10px; }
                .download-btn:hover { background: var(--primary-green); color: var(--bg-deep); box-shadow: 0 0 15px rgba(42, 245, 152, 0.4); }
                .relevance-btn { background: rgba(0, 158, 253, 0.1); color: var(--secondary-blue); border: 1px solid var(--secondary-blue); }
                .relevance-btn:hover { background: var(--secondary-blue); color: var(--text-white); box-shadow: 0 0 15px rgba(0, 158, 253, 0.4); }

                /* --- DIAGRAMS --- */
                .diagram-box { margin-top: 15px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
                .diagram-title { text-align: center; font-weight: 700; margin-bottom: 15px; color: var(--primary-green); font-size: 0.9rem; }
                .flex-row { display: flex; align-items: center; justify-content: center; gap: 5px; }
                .flex-col { display: flex; flex-direction: column; align-items: center; gap: 5px; }
                .frame-block { padding: 8px 4px; text-align: center; font-size: 0.75rem; color: #fff; display: flex; flex-direction: column; justify-content: center; }
                .frame-block small { opacity: 0.8; font-size: 0.65rem; margin-top: 3px; }
                .bg-blue { background: #3b82f6; } .bg-orange { background: #f59e0b; } .bg-green { background: #10b981; } .bg-purple { background: #8b5cf6; } .bg-pink { background: #ec4899; } .bg-grey { background: #64748b; } .bg-red { background: #ef4444; }
                .rounded-l { border-radius: 4px 0 0 4px; } .rounded-r { border-radius: 0 4px 4px 0; }
                .pin { width: 32px; height: 32px; border: 1px solid rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; border-radius: 4px; font-family: monospace; font-size: 0.8rem; color: rgba(255,255,255,0.5); }
                .pin-green { border-color: #10b981; color: #10b981; font-weight: bold; background: rgba(16,185,129,0.1); }
                .pin-grey { border-color: #a8a29e; color: #a8a29e; font-weight: bold; background: rgba(168,162,158,0.1); }
                .pin-blue { border-color: #3b82f6; color: #3b82f6; font-weight: bold; background: rgba(59,130,246,0.1); }
                .pin-orange { border-color: #f59e0b; color: #f59e0b; font-weight: bold; background: rgba(245,158,11,0.1); }
                .pin-red { border-color: #ef4444; color: #ef4444; font-weight: bold; background: rgba(239,68,68,0.1); }
                .diagram-legend { display: flex; justify-content: center; gap: 15px; margin-top: 15px; font-size: 0.75rem; flex-wrap: wrap; }
                .diagram-legend span { display: flex; align-items: center; gap: 4px; }
                .c-green { color: #10b981; } .c-grey { color: #a8a29e; } .c-blue { color: #3b82f6; } .c-orange { color: #f59e0b; } .c-red { color: #ef4444; }
                .flow-node { background: #10b981; color: #fff; padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
                .flow-gateway { background: #3b82f6; color: #fff; padding: 15px 10px; border-radius: 8px; font-weight: bold; font-size: 0.9rem; text-align: center; box-shadow: 0 4px 15px rgba(59,130,246,0.3); }
                .flow-cloud { background: #8b5cf6; color: #fff; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 4px 15px rgba(139,92,246,0.3); }
                .flow-arrow { color: var(--text-grey); display: flex; flex-direction: column; align-items: center; font-size: 1rem; }
                .flow-arrow small { font-size: 0.65rem; margin-top: 4px; }

                /* --- GRAPH MODAL --- */
                .modal-overlay { 
                    position: absolute; 
                    top: 0; left: 0; right: 0; 
                    background: rgba(5, 8, 16, 0.85); 
                    backdrop-filter: blur(8px); 
                    z-index: 1000; 
                    opacity: 0; 
                    visibility: hidden; 
                    transition: opacity 0.3s ease-out, visibility 0.3s ease-out; 
                }
                .modal-overlay.active { opacity: 1; visibility: visible; }
                
                .modal-box { 
                    background: var(--glass-bg); 
                    border: var(--glass-border); 
                    border-radius: var(--card-radius); 
                    width: 950px; 
                    max-width: 95%; 
                    height: 600px; 
                    min-height: 400px; 
                    max-height: 90vh; 
                    position: absolute; 
                    left: 50%;
                    transform: translateX(-50%) scale(0.95); 
                    opacity: 0;
                    padding: 20px; 
                    display: flex; 
                    flex-direction: column; 
                    align-items: center; 
                    overflow: hidden; 
                    box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
                    resize: both; 
                    transition: opacity 0.3s ease-out, transform 0.3s ease-out;
                }
                .modal-overlay.active .modal-box { 
                    transform: translateX(-50%) scale(1); 
                    opacity: 1;
                }
                
                .close-modal { position: absolute; top: 20px; right: 20px; background: transparent; border: none; color: var(--text-grey); font-size: 1.5rem; cursor: pointer; z-index: 100; transition: var(--transition); }
                .close-modal:hover { color: var(--text-white); }
                
                .graph-viewport { width: 100%; flex: 1; position: relative; overflow: hidden; cursor: grab; background: rgba(0, 0, 0, 0.2); border-radius: 12px; margin-top: 10px; border: 1px solid rgba(255, 255, 255, 0.05); }
                .graph-viewport:active { cursor: grabbing; }
                .graph-container { position: absolute; top: 0; left: 0; display: flex; align-items: center; gap: 120px; padding: 100px; transform-origin: 0 0; will-change: transform; }
                .graph-col { display: flex; flex-direction: column; gap: 20px; position: relative; z-index: 2; }
                
                .round-node { 
                    background: rgba(255, 255, 255, 0.05); 
                    border: 1px solid rgba(255, 255, 255, 0.1); 
                    color: var(--text-white); 
                    padding: 10px 20px; 
                    border-radius: 20px; 
                    min-width: 80px; 
                    max-width: 160px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: 600; 
                    text-align: center; 
                    backdrop-filter: blur(10px); 
                    cursor: pointer; 
                    position: relative; 
                    z-index: 2; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
                    font-size: 0.85rem; 
                    line-height: 1.3; 
                    white-space: normal;
                    transition: var(--transition);
                }
                .node-master { 
                    background: rgba(42, 245, 152, 0.1); 
                    border-color: var(--primary-green); 
                    color: var(--primary-green); 
                    padding: 15px 30px; 
                    border-radius: 25px; 
                    font-size: 1.1rem; 
                    min-width: 120px; 
                    box-shadow: 0 0 20px rgba(42, 245, 152, 0.2); 
                    cursor: default; 
                }
                .node-related:hover { background: var(--secondary-blue); color: var(--text-white); box-shadow: 0 0 20px rgba(0, 158, 253, 0.4); transform: scale(1.05); }
                .node-dist2 { margin-left: 100px; transform: scale(0.9); opacity: 0.9; }
                .node-dist2:hover { transform: scale(0.95); }
                
                .graph-lines { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; overflow: visible; }
                
                #modalChildExplanation { position: absolute; top: 20px; left: 20px; width: 320px; z-index: 100; box-shadow: 0 10px 30px rgba(0,0,0,0.5); background: rgba(5, 8, 16, 0.95); border: 1px solid var(--secondary-blue); border-top: 4px solid var(--primary-green); padding: 16px 20px; border-radius: 8px; display: none; animation: spediaFadeUp 0.3s ease-out forwards; }
                #modalChildExplanation.active { display: block; }
                .see-details-btn { background: var(--secondary-blue); color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 0.85rem; margin-top: 15px; display: flex; align-items: center; gap: 8px; transition: var(--transition); }
                .see-details-btn:hover { background: var(--primary-green); color: var(--bg-deep); }

                /* Checkbox styling */
                .matrix-filter-label {
                    display: flex; align-items: center; gap: 10px; color: var(--text-grey); cursor: pointer; transition: all 0.2s; font-size: 0.95rem;
                }
                .matrix-filter-label:hover { color: var(--text-white); }
                .matrix-filter-checkbox {
                    width: 18px; height: 18px; accent-color: var(--primary-green); cursor: pointer;
                }
                
                /* Custom Scrollbar for matrix panels */
                .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
                .custom-scroll::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); border-radius: 4px; }
                .custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
                .custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }
            </style>
            
            <div class="sub-nav-tabs fade-up w-full justify-center mt-6">
                <button class="sub-nav-btn active" onclick="switchSpediaMode('spedia-search-mode', this)">
                    <i class="fa-solid fa-magnifying-glass"></i> Search Engine
                </button>
                <button class="sub-nav-btn" onclick="switchSpediaMode('spedia-matrix-mode', this)">
                    <i class="fa-solid fa-table-cells-large"></i> Product Matrix
                </button>
            </div>

            <!-- MODE 1: SEARCH ENGINE -->
            <div id="spedia-search-mode" class="spedia-mode w-full flex flex-col items-center">
                <div class="search-wrapper" id="searchWrapper">
                    <div class="title-container">
                        <div class="mascot-container">
                            <img src="https://drive.google.com/thumbnail?id=1bXf5psHrw4LOk0oMAkTJRL15_mLCabad&sz=w500" alt="Streamax Mascot" class="mascot" id="mascotImage" onerror="this.src='https://cdn-icons-png.flaticon.com/512/4712/4712035.png'">
                        </div>
                        <h1 class="brand-title"><span class="gradient-text">Streamaxpedia</span></h1>
                    </div>
                    
                    <div class="subtitle-box">
                        <p class="temp-note">
                            <i class="fa-solid fa-circle-info" style="color: var(--secondary-blue); margin-right: 5px;"></i>
                            This is a temporary Streamax info library. A more powerful Streamax AI agent is coming soon!
                        </p>
                        <p class="credit-line">
                            <i class="fa-solid fa-bolt" style="margin-right: 5px;"></i>By Trucking BU - a Sales Toolkit Extension
                        </p>
                    </div>
                    
                    <div class="search-box">
                        <input type="text" id="searchInput" class="search-input" placeholder="Search for ADAS, MDVR, APIs, metrics..." autocomplete="off">
                        <i class="fa-solid fa-magnifying-glass search-icon"></i>
                        <i class="fa-solid fa-xmark clear-icon" id="clearBtn"></i>
                    </div>
                </div>

                <div class="stats" id="statsBar">Found <span id="resultCount">0</span> terms</div>
                <div class="results-container" id="resultsContainer">
                    <!-- Results will be injected here via JavaScript -->
                </div>
            </div>
            
            <!-- MODE 2: PRODUCT MATRIX -->
            <div id="spedia-matrix-mode" class="spedia-mode hidden w-full">
                
                <!-- DESCRIPTION INFO BOX (Collapsible) -->
                <div class="w-full max-w-7xl mx-auto px-4 mt-6 mb-4 fade-up">
                    <style>
                        .matrix-intro-details { background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; overflow: hidden; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
                        .matrix-intro-details[open] { border-color: rgba(42, 245, 152, 0.3); }
                        .matrix-intro-summary { padding: 16px 24px; cursor: pointer; font-weight: 600; color: var(--primary-green); display: flex; align-items: center; justify-content: space-between; user-select: none; background: rgba(0,0,0,0.2); }
                        .matrix-intro-summary:hover { background: rgba(255,255,255,0.05); }
                        .matrix-intro-details[open] .matrix-intro-summary .chevron { transform: rotate(180deg); }
                        .matrix-intro-summary::-webkit-details-marker { display: none; }
                        .matrix-intro-content { padding: 24px; font-size: 0.9rem; color: var(--text-grey); line-height: 1.6; border-top: 1px solid rgba(255, 255, 255, 0.05); position: relative; }
                    </style>
                    
                    <details class="matrix-intro-details">
                        <summary class="matrix-intro-summary">
                            <div class="flex items-center justify-between w-full pr-4">
                                <span id="matrix-intro-title" class="flex items-center text-white font-bold text-lg"><i class="fa-solid fa-circle-info text-[var(--secondary-blue)] mr-2"></i> What is the Product Matrix?</span>
                                
                                <!-- Language Toggle -->
                                <div class="flex items-center bg-black/50 border border-white/20 rounded-full p-1 cursor-pointer ml-4 z-10" onclick="toggleMatrixLang(event)">
                                    <div id="lang-en" class="px-3 py-1 rounded-full text-xs font-bold bg-[var(--primary-green)] text-[#050810] transition-colors">EN</div>
                                    <div id="lang-zh" class="px-3 py-1 rounded-full text-xs font-bold text-gray-400 transition-colors">中文</div>
                                </div>
                            </div>
                            <i class="fa-solid fa-chevron-down chevron text-[var(--text-grey)] transition-transform duration-300"></i>
                        </summary>
                        
                        <div class="matrix-intro-content">
                            <!-- English Content -->
                            <div id="matrix-intro-en" class="block">
                                <p class="mb-5 text-gray-300 text-sm">The <strong>Product Matrix</strong> is an intelligent, interactive configuration tool designed to help you quickly build, discover, and validate official Streamax hardware architectures. It bridges the gap between individual hardware components and complex, fully-integrated fleet solutions.</p>
                                
                                <h3 class="text-md font-bold text-white mb-3"><i class="fa-solid fa-rocket text-[var(--primary-green)] mr-2"></i> How to Use It</h3>
                                <ul class="space-y-3 pl-2 text-sm text-gray-300">
                                    <li><strong class="text-[var(--primary-green)]">1. Pick & Search (Left Panel - Component Library):</strong> Use the search bar to find individual discrete components (e.g., <em>AD Plus 2.0</em>, <em>C29N</em>, <em>AVM</em>). Click on any component "chip" to instantly add it to your working Basket at the bottom of the screen.</li>
                                    <li><strong class="text-[var(--secondary-blue)]">2. Filter by Features (Right Panel - Composition Discovery):</strong> Not sure what components you need? Check the feature boxes (like <em>DMS</em>, <em>ADAS</em>, or <em>Blind Spot Detection</em>) to filter the official Streamax master configurations. Every formula displayed is interactive—click any product inside the formula string to add it directly to your Basket.</li>
                                    <li><strong class="text-yellow-500">3. Validate & Expand (Bottom Panel - Solution Validator):</strong> As you add components to your Basket, the Validator engine works in real time. 
                                        <ul class="list-disc pl-6 mt-2 text-gray-400 space-y-1">
                                            <li>If your selection matches an official architecture perfectly, it will display a <strong class="text-[var(--primary-green)]">Valid Solution Confirmed</strong> badge along with full technical specs.</li>
                                            <li>If your selection is incomplete, it will flash an <strong class="text-yellow-500">Incomplete Combination</strong> warning and intelligently suggest the exact missing components you need to add to complete the system!</li>
                                        </ul>
                                    </li>
                                </ul>
                            </div>

                            <!-- Chinese Content -->
                            <div id="matrix-intro-zh" class="hidden">
                                <p class="mb-5 text-gray-300 text-sm"><strong>产品组合矩阵 (Product Matrix)</strong> 是一个智能的、交互式的配置工具，旨在帮助您快速构建、发现和验证官方的 Streamax 硬件架构。它弥补了独立硬件组件与复杂的全集成车队解决方案之间的空白。</p>
                                
                                <h3 class="text-md font-bold text-white mb-3"><i class="fa-solid fa-rocket text-[var(--primary-green)] mr-2"></i> 如何使用</h3>
                                <ul class="space-y-3 pl-2 text-sm text-gray-300">
                                    <li><strong class="text-[var(--primary-green)]">1. 挑选与搜索 (左侧面板 - 组件库):</strong> 使用搜索栏查找独立的硬件组件（例如 <em>AD Plus 2.0</em>, <em>C29N</em>, <em>AVM</em>）。点击任何组件“名牌”即可将其立即添加到屏幕底部的方案验证器中。</li>
                                    <li><strong class="text-[var(--secondary-blue)]">2. 按功能过滤 (右侧面板 - 配置筛选):</strong> 不确定需要哪些组件？勾选功能框（如 <em>DMS</em>, <em>ADAS</em>, 或 <em>盲区检测</em>）来过滤 Streamax 官方推荐配置。每一个显示的方案都是可交互的——点击产品组合中的任何产品即可将其直接添加到方案验证器中。</li>
                                    <li><strong class="text-yellow-500">3. 验证与扩展 (底部面板 - 方案验证器):</strong> 当您向方案验证器添加组件时，验证引擎会实时工作。
                                        <ul class="list-disc pl-6 mt-2 text-gray-400 space-y-1">
                                            <li>如果您的选择与官方架构完全匹配，它将显示<strong class="text-[var(--primary-green)]">有效方案已确认</strong>徽章以及完整的技术规格。</li>
                                            <li>如果您的选择不完整，它会闪烁<strong class="text-yellow-500">组合不完整</strong>警告，并智能提示您需要添加的确切缺失组件以完成系统配置！</li>
                                        </ul>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </details>
                </div>

                <!-- TOP AREA: Grid Layout -->
                <div style="display: flex; flex-direction: row; flex-wrap: nowrap; gap: 1.5rem; width: 100%; max-width: 80rem; margin: 1rem auto 0; padding: 0 1rem;">
                    
                    <!-- Left Column: Component Search & Pick -->
                    <div class="glass-panel p-5 flex flex-col h-[500px] bg-black/40 border border-white/10 rounded-xl" style="width: 35%; flex-shrink: 0; overflow: hidden;">
                        <h3 class="text-lg font-bold text-white mb-2"><i class="fa-solid fa-box-open text-[var(--primary-green)] mr-2"></i> Component Library</h3>
                        <p class="text-xs text-gray-400 mb-4 leading-relaxed">Search and pick discrete hardware components. Click any chip to add it to your basket below.</p>
                        
                        <div class="relative mb-4">
                            <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"></i>
                            <input type="text" id="componentSearch" placeholder="Find AD Plus 2.0, C29N..." class="w-full bg-black/60 border border-white/20 rounded-lg py-2.5 pl-9 pr-3 text-white outline-none focus:border-[var(--primary-green)] transition-all text-sm" oninput="renderComponents()">
                        </div>
                        
                        <div id="componentsList" class="flex flex-wrap gap-2 overflow-y-auto custom-scroll pr-2 pb-2 flex-grow content-start">
                            <!-- Populated by JS -->
                        </div>
                    </div>

                    <!-- Right Column: Filters & Formulas -->
                    <div class="glass-panel p-5 flex flex-col h-[500px] bg-black/40 border border-white/10 rounded-xl" style="width: 65%; overflow: hidden;">
                        <h3 class="text-lg font-bold text-white mb-2"><i class="fa-solid fa-wand-magic-sparkles text-[var(--secondary-blue)] mr-2"></i> Composition Discovery</h3>
                        <p class="text-xs text-gray-400 mb-4 leading-relaxed">Filter official architectures by requested features. Click components inside the formulas to add them to your basket.</p>
                        
                        <!-- Feature Filters Row -->
                        <div class="flex flex-col gap-3 mb-4 pb-4 border-b border-white/10">
                            <!-- Top row: Checkboxes -->
                            <div class="flex flex-wrap items-center gap-x-5 gap-y-2">
                                <label class="matrix-filter-label"><input type="checkbox" id="filter-dms" class="matrix-filter-checkbox" onchange="updateMatrix()"> DMS</label>
                                <label class="matrix-filter-label"><input type="checkbox" id="filter-adas" class="matrix-filter-checkbox" onchange="updateMatrix()"> ADAS</label>
                                <label class="matrix-filter-label"><input type="checkbox" id="filter-dsc" class="matrix-filter-checkbox" onchange="updateMatrix()"> DSC</label>
                                <label class="matrix-filter-label"><input type="checkbox" id="filter-bsis" class="matrix-filter-checkbox" onchange="updateMatrix()"> BSIS/MOIS</label>
                                <label class="matrix-filter-label"><input type="checkbox" id="filter-avm" class="matrix-filter-checkbox" onchange="updateMatrix()"> AI-AVM</label>
                            </div>
                            <!-- Bottom row: Dropdowns -->
                            <div class="flex flex-wrap items-center gap-4">
                                <div class="flex items-center gap-2">
                                    <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">AI Reqs:</label>
                                    <select id="filter-ai" class="bg-black/60 border border-white/20 rounded px-2 py-1 text-white outline-none focus:border-[var(--primary-green)] text-xs font-medium" onchange="updateMatrix()">
                                        <option value="Any">Any</option>
                                        <option value="No AI">No AI</option>
                                        <option value="2-Channel AI">2-Channel AI</option>
                                        <option value="3-Channel AI">3-Channel AI</option>
                                        <option value="4-Channel AI">4-Channel AI</option>
                                        <option value="5-Channel AI">5-Channel AI</option>
                                        <option value="6-Channel AI">6-Channel AI</option>
                                        <option value="8-Channel AI">8-Channel AI</option>
                                    </select>
                                </div>
                                <div class="flex items-center gap-2">
                                    <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">Channels:</label>
                                    <select id="filter-ch" class="bg-black/60 border border-white/20 rounded px-2 py-1 text-white outline-none focus:border-[var(--primary-green)] text-xs font-medium" onchange="updateMatrix()">
                                        <option value="Any">Any</option>
                                        <option value="2-channel monitoring">2-Ch</option>
                                        <option value="3-channel monitoring">3-Ch</option>
                                        <option value="4-channel monitoring">4-Ch</option>
                                        <option value="5-channel monitoring">5-Ch</option>
                                        <option value="6-channel monitoring">6-Ch</option>
                                        <option value="7-channel monitoring">7-Ch</option>
                                        <option value="8-channel monitoring">8-Ch</option>
                                        <option value="9-channel monitoring">9-Ch</option>
                                        <option value="11-channel monitoring">11-Ch</option>
                                        <option value="12-channel monitoring">12-Ch</option>
                                    </select>
                                </div>
                                <div class="flex items-center gap-2 ml-auto">
                                    <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">BSD Config:</label>
                                    <select id="filter-bsd" class="bg-black/60 border border-white/20 rounded px-2 py-1 text-white outline-none focus:border-[var(--primary-green)] text-xs font-medium" onchange="updateMatrix()">
                                        <option value="Any">Any</option>
                                        <option value="NO">NO</option>
                                        <option value="四选一">四选一</option>
                                        <option value="四选二">四选二</option>
                                        <option value="后BSD">后BSD</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Results Container -->
                        <div id="matrixResults" class="overflow-y-auto custom-scroll pr-2 pb-2 flex-grow space-y-3">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>

                <!-- BOTTOM AREA: Validator Basket -->
                <div class="w-full max-w-7xl mx-auto px-4 mt-6 pb-20">
                    <div class="glass-panel p-6 border-t-4 border-[var(--primary-green)] bg-black/60 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
                        <div class="flex items-center justify-between mb-4">
                            <h2 class="text-xl font-bold text-white"><i class="fa-solid fa-layer-group text-[var(--secondary-blue)] mr-2"></i> Solution Validator</h2>
                            <button onclick="clearBasket()" class="text-xs text-gray-400 hover:text-white underline"><i class="fa-solid fa-trash-can mr-1"></i> Clear Basket</button>
                        </div>
                        
                        <div class="mb-5">
                            <div id="basketArea" class="flex flex-wrap gap-3 min-h-[56px] p-3 border border-white/10 rounded-lg bg-black/40 items-center">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <div id="validatorResult" class="rounded-xl border border-white/10 p-5 bg-black/20 transition-all min-h-[120px] flex items-center justify-center">
                            <div class="text-center text-gray-500">
                                <i class="fa-solid fa-microchip text-3xl mb-2 opacity-50"></i>
                                <p>Select components to validate your solution architecture.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RELEVANCE GRAPH MODAL -->
            <div class="modal-overlay" id="relevanceModal">
                <div class="modal-box">
                    <button class="close-modal" onclick="window.closeModal()"><i class="fa-solid fa-xmark"></i></button>
                    <h3 style="color: var(--text-white); font-size: 1.2rem; margin-bottom: 5px; z-index: 10;">Relevance Graph</h3>
                    
                    <div class="graph-viewport" id="graphViewport">
                        <div class="graph-container" id="graphContainer">
                            <svg class="graph-lines" id="graphLines" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"></svg>
                            <div class="round-node node-master" id="graphMasterNode"></div>
                            <div class="graph-col" id="graphRelatedNodes"></div>
                        </div>
                        <div id="modalChildExplanation"></div>
                    </div>
                </div>
            </div>

            <!-- SECURITY WARNING MODAL WITH POLICY EMBED -->
            <div class="modal-overlay" id="securityModal">
                <div class="modal-box" style="width: 550px; height: auto; min-height: unset; padding: 40px; text-align: center; background: rgba(5, 8, 16, 0.98); border: 1px solid rgba(255, 71, 87, 0.3); box-shadow: 0 20px 60px rgba(0,0,0,0.8);">
                    <button class="close-modal" onclick="window.closeModal()"><i class="fa-solid fa-xmark"></i></button>
                    <i class="fa-solid fa-shield-halved" style="font-size: 3.5rem; color: #ff4757; margin-bottom: 20px; filter: drop-shadow(0 0 15px rgba(255, 71, 87, 0.4));"></i>
                    <h3 style="color: var(--text-white); font-size: 1.4rem; margin-bottom: 15px;">Access Denied / 下载受限</h3>
                    <p style="color: var(--text-grey); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                        Due to Company IT Security Policy, downloading core technical documents, specs, and manuals to the public network is strictly prohibited.
                        <br><br>
                        根据公司信息安全管理规范，严禁将核心技术资料（含白皮书、规格书、手册等）发布或下载至公网环境。
                    </p>
                    <div style="display: flex; gap: 15px; justify-content: center; margin-top: 30px;">
                        <button class="see-details-btn" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); color: white;" onclick="window.closeModal()">Cancel / 取消</button>
                        <button class="see-details-btn" style="background: #ff4757; color: white;" onclick="window.viewSecurityPolicy()"><i class="fa-solid fa-arrow-up-right-from-square"></i> View Policy / 查看管控通知</button>
                    </div>
                </div>
            </div>
"""

js_code = """
            <script>
                const terminologyDB = """ + db_json + """;
                const matrixData = """ + matrix_json + """;
                const ALL_PRODUCTS = """ + products_json + """;
                const pdfBase64 = \"""" + pdf_base64 + """\";
                
                const ENABLE_DOWNLOADS = false;
""" + r"""
                let selectedBasket = new Set();

                // Language Toggle Logic
                function toggleMatrixLang(e) {
                    if (e) { e.preventDefault(); e.stopPropagation(); }
                    const enContent = document.getElementById('matrix-intro-en');
                    const zhContent = document.getElementById('matrix-intro-zh');
                    const enBtn = document.getElementById('lang-en');
                    const zhBtn = document.getElementById('lang-zh');
                    const titleSpan = document.getElementById('matrix-intro-title');

                    if (enContent.classList.contains('hidden')) {
                        // Switch to EN
                        enContent.classList.remove('hidden');
                        zhContent.classList.add('hidden');
                        enBtn.className = "px-3 py-1 rounded-full text-xs font-bold bg-[var(--primary-green)] text-[#050810] transition-colors";
                        zhBtn.className = "px-3 py-1 rounded-full text-xs font-bold text-gray-400 transition-colors";
                        if (titleSpan) titleSpan.innerHTML = '<i class="fa-solid fa-circle-info text-[var(--secondary-blue)] mr-2"></i> What is the Product Matrix?';
                    } else {
                        // Switch to ZH
                        enContent.classList.add('hidden');
                        zhContent.classList.remove('hidden');
                        zhBtn.className = "px-3 py-1 rounded-full text-xs font-bold bg-[var(--primary-green)] text-[#050810] transition-colors";
                        enBtn.className = "px-3 py-1 rounded-full text-xs font-bold text-gray-400 transition-colors";
                        if (titleSpan) titleSpan.innerHTML = '<i class="fa-solid fa-circle-info text-[var(--secondary-blue)] mr-2"></i> 什么是产品组合矩阵？';
                    }
                }

                // Toggle Sub-Tabs
                function switchSpediaMode(modeId, btnElement) {
                    const container = btnElement.closest('.sub-nav-tabs');
                    container.querySelectorAll('.sub-nav-btn').forEach(btn => btn.classList.remove('active'));
                    btnElement.classList.add('active');

                    document.querySelectorAll('.spedia-mode').forEach(el => el.classList.add('hidden'));
                    const target = document.getElementById(modeId);
                    target.classList.remove('hidden');
                    
                    if (modeId === 'spedia-matrix-mode') {
                        renderComponents();
                        updateMatrix(); 
                    }
                }

                // Render Left Library Panel
                function renderComponents() {
                    const searchEl = document.getElementById('componentSearch');
                    const query = searchEl ? searchEl.value.toLowerCase().trim() : '';
                    const container = document.getElementById('componentsList');
                    if (!container) return;
                    
                    let html = '';
                    ALL_PRODUCTS.forEach(p => {
                        const safeP = p ? String(p) : '';
                        if (safeP.toLowerCase().includes(query)) {
                            const isSelected = selectedBasket.has(safeP);
                            const activeClass = isSelected ? "bg-[var(--primary-green)] text-[#050810]" : "bg-black/50 text-gray-300 border-white/20 hover:border-[var(--primary-green)] hover:text-white";
                            html += `<button type="button" class="border px-3 py-1.5 rounded-lg text-sm font-bold transition-all shadow-sm ${activeClass}" onclick="toggleBasket('${safeP}')">${safeP}</button>`;
                        }
                    });
                    if(html === '') html = '<span class="text-gray-500 text-sm">No components found.</span>';
                    container.innerHTML = html;
                }

                // Manage Basket State
                function toggleBasket(p) {
                    if (selectedBasket.has(p)) {
                        selectedBasket.delete(p);
                    } else {
                        selectedBasket.add(p);
                    }
                    renderComponents(); // update left panel active states
                    renderBasketUI();
                    validateCombination();
                }
                
                function clearBasket() {
                    selectedBasket.clear();
                    renderComponents();
                    renderBasketUI();
                    validateCombination();
                }
                
                function addMultipleToBasket(itemsListStr) {
                    let items = itemsListStr.split(',');
                    items.forEach(p => selectedBasket.add(p.trim()));
                    renderComponents();
                    renderBasketUI();
                    validateCombination();
                }

                // Render Bottom Basket UI
                function renderBasketUI() {
                    const container = document.getElementById('basketArea');
                    if (selectedBasket.size === 0) {
                        container.innerHTML = '<span class="text-gray-500 italic text-sm">No components selected. Click items above to add.</span>';
                        return;
                    }
                    
                    let html = '';
                    selectedBasket.forEach(p => {
                        html += `
                            <div class="inline-flex items-center bg-[var(--primary-green)] text-[#050810] font-bold px-3 py-1.5 rounded-full text-sm shadow-[0_0_10px_rgba(42,245,152,0.3)] animate-pulse" style="animation-iteration-count: 1;">
                                ${p}
                                <button class="ml-2 hover:text-white transition outline-none" onclick="toggleBasket('${p}')"><i class="fa-solid fa-circle-xmark"></i></button>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                }

                // Horizontal Flow Formula Renderer with Smart Anchoring for Chinese Hints
                function makeClickableFormula(sol) {
                    let res = sol ? String(sol) : "";
                    if (!res) return "";
                    
                    let notes = [];
                    let longNotes = [];
                    
                    // 1. Extract Parenthesis First
                    res = res.replace(/（/g, '(').replace(/）/g, ')');
                    res = res.replace(/\s*\((.*?)\)/g, (match, p1) => {
                        let text = p1.trim();
                        // If it's a long explanation (>8 chars), treat as a solution-level note
                        if (text.length > 8) {
                            longNotes.push(text);
                            return ``; // Remove from the horizontal inline flow entirely
                        } else {
                            notes.push(text);
                            return `__NOTE${notes.length-1}__`; // Keep short hints inline
                        }
                    });

                    // 2. Extract Loose Chinese Hints (including preceding hyphens, e.g., "-左")
                    res = res.replace(/[-\s]*([\u4e00-\u9fa5]+[^+\/{}\*\(\)]*)/g, (match, p1) => {
                        let text = p1.replace(/^[-_\s]+/, '').trim();
                        if (text.length > 8) {
                            longNotes.push(text);
                            return ``;
                        } else {
                            notes.push(text);
                            return `__NOTE${notes.length-1}__`;
                        }
                    });

                    // 3. Tokenize Products (Longest first to prevent partial matches)
                    const sortedProducts = [...(ALL_PRODUCTS || [])].sort((a, b) => b.length - a.length);
                    sortedProducts.forEach((p, idx) => {
                        if (p) {
                            res = res.split(p).join(`__TKN${idx}__`);
                        }
                    });

                    // 4. Safely Replace Syntax with Placeholders
                    res = res.replace(/\s+or\s+/gi, '__OR__');
                    res = res.replace(/\//g, '__SLASH__');
                    res = res.replace(/\{/g, '__LBRACE__');
                    res = res.replace(/\}/g, '__RBRACE__');
                    res = res.replace(/\s*\+\s*/g, '__PLUS__');
                    res = res.replace(/\*(\d+)/g, '__MULT$1__');

                    // Group Preceding Elements (Product Token or Brackets) with their associated short Note
                    res = res.replace(/((?:__TKN\d__|__RBRACE__)(?:__MULT\d__)?)\s*(__NOTE\d__)/g, '<div style="position: relative; display: inline-block; margin: 0 2px;">$1$2</div>');
                    // Wrap any stray short notes to give them a relative positioning anchor too
                    res = res.replace(/(^|[^>])(__NOTE\d__)/g, '$1<div style="position: relative; display: inline-block; margin: 0 2px;">$2</div>');

                    // Apply HTML replacements to syntax placeholders (strictly inline items)
                    res = res.replace(/__OR__/g, '<span style="margin: 0 6px; font-size: 10px; text-transform: uppercase; font-weight: bold; color: #94a3b8; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; display: inline-block; vertical-align: middle;">OR</span>');
                    res = res.replace(/__SLASH__/g, '<span style="margin: 0 4px; font-weight: bold; color: #94a3b8; display: inline-block; vertical-align: middle;">/</span>');
                    res = res.replace(/__PLUS__/g, '<span style="margin: 0 6px; color: #2AF598; font-weight: 900; font-size: 1rem; display: inline-block; vertical-align: middle;">+</span>');
                    res = res.replace(/__LBRACE__/g, '<span style="margin: 0 2px; color: #009EFD; font-weight: 900; font-size: 1.25rem; display: inline-block; vertical-align: middle;">[</span>');
                    res = res.replace(/__RBRACE__/g, '<span style="margin: 0 2px; color: #009EFD; font-weight: 900; font-size: 1.25rem; display: inline-block; vertical-align: middle;">]</span>');
                    res = res.replace(/__MULT(\d+)__/g, '<span style="margin-left: 2px; font-size: 11px; font-weight: bold; padding: 2px 6px; background: rgba(255,255,255,0.2); color: white; border-radius: 4px; display: inline-block; vertical-align: middle;">x$1</span>');

                    // Restore Products as Buttons (strictly inline items)
                    sortedProducts.forEach((p, idx) => {
                        if (p) {
                            let btn = `<button type="button" class="bg-[var(--secondary-blue)]/20 hover:bg-[var(--secondary-blue)] text-[var(--secondary-blue)] hover:text-white border border-[var(--secondary-blue)]/50 px-2 py-1 rounded-lg text-[13px] font-bold cursor-pointer transition-colors shadow-sm whitespace-nowrap" style="display: inline-flex; align-items: center; vertical-align: middle;" onclick="toggleBasket('${p}')"><i class="fa-solid fa-plus text-[10px] mr-1 opacity-50"></i>${p}</button>`;
                            res = res.split(`__TKN${idx}__`).join(btn);
                        }
                    });

                    // Restore SHORT Notes as absolute positioned tags beneath the item (they will NOT affect the row's inline flow)
                    notes.forEach((n, idx) => {
                        let noteHtml = `<span style="position: absolute; top: 100%; margin-top: 6px; left: 50%; transform: translateX(-50%); font-size: 10px; color: #cbd5e1; font-weight: 500; font-style: italic; white-space: nowrap; background: rgba(0,0,0,0.85); padding: 3px 6px; border-radius: 4px; border: 1px solid rgba(42,245,152,0.4); z-index: 10; line-height: 1; box-shadow: 0 4px 10px rgba(0,0,0,0.5); pointer-events: none;">${n}</span>`;
                        res = res.split(`__NOTE${idx}__`).join(noteHtml);
                    });

                    // 5. Generate UI for LONG solution-level notes
                    let longNotesHtml = '';
                    if (longNotes.length > 0) {
                        let combinedNotes = longNotes.join('<br><br>');
                        // Place a discrete, absolute "Solution Note" tab on the top right
                        longNotesHtml = `
                        <div class="absolute right-0 top-0 z-20 group">
                            <div class="flex items-center gap-1.5 px-2.5 py-1 text-[10px] font-bold text-yellow-400 bg-yellow-400/10 border-l border-b border-yellow-400/30 rounded-bl-lg rounded-tr-lg cursor-help transition-all group-hover:bg-yellow-400 group-hover:text-[#050810]">
                                <i class="fa-solid fa-lightbulb"></i> Solution Note
                            </div>
                            <div class="absolute top-full right-0 mt-1 w-max max-w-[300px] whitespace-normal bg-[#0B1221] text-gray-200 font-medium text-xs p-3 rounded-lg border border-yellow-400/40 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-[100] shadow-[0_15px_35px_rgba(0,0,0,0.8)] text-left leading-relaxed">
                                ${combinedNotes}
                            </div>
                        </div>`;
                    }

                    // 6. Wrap everything in a unified container. 
                    // Dynamic padding-right ensures the scroll bar doesn't hide text underneath the absolute Solution Note tab!
                    return `
                    <div class="relative w-full">
                        ${longNotesHtml}
                        <div style="display: flex; flex-direction: row; flex-wrap: nowrap; align-items: center; overflow-x: auto; overflow-y: visible; padding-bottom: 24px; padding-top: 8px; padding-left: 4px; padding-right: ${longNotes.length > 0 ? '90px' : '4px'}; width: 100%; white-space: nowrap; scrollbar-width: thin;">
                            ${res}
                        </div>
                    </div>`;
                }

                // Validator Engine with dynamic suggestions
                function validateCombination() {
                    const resEl = document.getElementById('validatorResult');
                    if (!resEl) return;
                    
                    if (selectedBasket.size === 0) {
                        resEl.className = "rounded-xl border border-white/10 p-5 bg-black/20 transition-all min-h-[120px] flex flex-col items-center justify-center";
                        resEl.innerHTML = `
                            <div class="text-center text-gray-500">
                                <i class="fa-solid fa-microchip text-3xl mb-2 opacity-50"></i>
                                <p class="text-sm m-0">Select components to validate your solution architecture.</p>
                            </div>
                        `;
                        return;
                    }

                    // Sort arrays for deterministic comparison
                    const basketArr = Array.from(selectedBasket).sort();
                    let matchedRow = null;
                    let suggestionsMap = new Map();

                    for (let row of (matrixData || [])) {
                        const validSets = row.valid_sets || [];
                        for (let vSet of validSets) {
                            let vArr = [...vSet].sort();
                            
                            // Check Exact Match
                            if (JSON.stringify(basketArr) === JSON.stringify(vArr)) {
                                if (!matchedRow) matchedRow = row; 
                            }
                            
                            // Suggestion Search: Is basket a strict subset of this valid set?
                            let isSubset = basketArr.every(val => vArr.includes(val));
                            if (isSubset && vArr.length > basketArr.length) {
                                let missing = vArr.filter(x => !basketArr.includes(x));
                                let key = missing.sort().join(' + ');
                                if (!suggestionsMap.has(key)) {
                                    suggestionsMap.set(key, missing);
                                }
                            }
                        }
                    }

                    // Render Suggestions UI
                    let suggestionsHtml = '';
                    if (suggestionsMap.size > 0) {
                        let pillsHtml = '';
                        suggestionsMap.forEach((missingArr, key) => {
                            let itemsStr = missingArr.join(',');
                            pillsHtml += `<button onclick="addMultipleToBasket('${itemsStr}')" class="bg-black/40 border border-white/20 hover:border-[var(--secondary-blue)] text-[var(--secondary-blue)] hover:text-white px-3 py-1.5 rounded-full text-xs font-bold transition-all shadow-sm flex items-center gap-1.5"><i class="fa-solid fa-plus text-[10px]"></i> ${key}</button>`;
                        });
                        
                        suggestionsHtml = `
                            <div class="mt-5 pt-4 border-t border-white/10 w-full">
                                <div class="text-xs text-gray-400 font-bold uppercase tracking-wider mb-3"><i class="fa-solid fa-lightbulb text-yellow-500 mr-1"></i> Expand Solution With:</div>
                                <div class="flex flex-wrap gap-2">
                                    ${pillsHtml}
                                </div>
                            </div>
                        `;
                    }

                    // Apply Final UI
                    if (matchedRow) {
                        const formulaStr = matchedRow.composition || matchedRow.sol || "Unknown Architecture";
                        resEl.className = "rounded-xl border border-[var(--primary-green)] p-5 bg-[var(--primary-green)]/5 transition-all shadow-[0_0_20px_rgba(42,245,152,0.15)] flex flex-col";
                        resEl.innerHTML = `
                            <div class="text-[var(--primary-green)] font-bold text-xl mb-4 flex items-center">
                                <i class="fa-solid fa-circle-check mr-2 text-2xl"></i> Valid Solution Confirmed
                            </div>
                            
                            <div class="bg-black/30 border border-[var(--primary-green)]/30 rounded-lg pb-3 mb-4 flex flex-col overflow-visible relative">
                                <div class="text-[10px] text-[var(--primary-green)] uppercase tracking-wider font-bold mb-1 mt-3 ml-4"><i class="fa-solid fa-microchip mr-1"></i> Full System Architecture</div>
                                ${makeClickableFormula(formulaStr)}
                            </div>

                            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">AI Reqs</div><div class="text-sm text-white font-bold">${matchedRow.ai || 'N/A'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">Channels</div><div class="text-sm text-white font-bold">${matchedRow.ch || 'N/A'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">HDD</div><div class="text-sm font-bold">${matchedRow.hdd === 'YES' ? '<span class="text-[var(--primary-green)]"><i class="fa-solid fa-check"></i> YES</span>' : '<span class="text-gray-400">NO</span>'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">DMS</div><div class="text-sm font-bold ${matchedRow.dms==='YES'?'text-[var(--secondary-blue)]':'text-gray-400'}">${matchedRow.dms || 'NO'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">ADAS</div><div class="text-sm font-bold ${matchedRow.adas==='YES'?'text-[var(--secondary-blue)]':'text-gray-400'}">${matchedRow.adas || 'NO'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">DSC</div><div class="text-sm font-bold ${matchedRow.dsc==='YES'?'text-[var(--secondary-blue)]':'text-gray-400'}">${matchedRow.dsc || 'NO'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">BSIS/MOIS</div><div class="text-sm font-bold ${matchedRow.bsis==='YES'?'text-[var(--secondary-blue)]':'text-gray-400'}">${matchedRow.bsis || 'NO'}</div></div>
                                <div class="p-3 bg-black/40 rounded-lg border border-[var(--primary-green)]/30 text-center"><div class="text-[10px] text-gray-400 uppercase mb-1">AI-AVM</div><div class="text-sm font-bold ${matchedRow.avm==='YES'?'text-[var(--secondary-blue)]':'text-gray-400'}">${matchedRow.avm || 'NO'}</div></div>
                            </div>
                            ${suggestionsHtml}
                        `;
                    } else {
                        let errorMsg = suggestionsMap.size > 0 
                            ? "Your basket has components from a valid architecture, but is currently incomplete. Add the suggested items below to complete it." 
                            : "The components currently in your basket do not match any recognized standalone system architecture. Try starting over.";
                        
                        let statusColor = suggestionsMap.size > 0 ? "text-yellow-500" : "text-red-400";
                        let borderColor = suggestionsMap.size > 0 ? "border-yellow-500/50" : "border-red-500/50";
                        let bgColor = suggestionsMap.size > 0 ? "bg-yellow-500/5" : "bg-red-500/5";
                        let icon = suggestionsMap.size > 0 ? "fa-circle-exclamation" : "fa-circle-xmark";

                        resEl.className = `rounded-xl border ${borderColor} p-5 ${bgColor} transition-all flex flex-col`;
                        resEl.innerHTML = `
                            <div class="${statusColor} font-bold text-xl mb-2 flex items-center">
                                <i class="fa-solid ${icon} mr-2 text-2xl"></i> ${suggestionsMap.size > 0 ? 'Incomplete Combination' : 'Invalid Combination'}
                            </div>
                            <p class="text-sm text-gray-400 m-0">${errorMsg}</p>
                            ${suggestionsHtml}
                        `;
                    }
                }

                // Render Right Configurations Panel
                function updateMatrix() {
                    const dmsEl = document.getElementById('filter-dms');
                    const adasEl = document.getElementById('filter-adas');
                    const dscEl = document.getElementById('filter-dsc');
                    const bsisEl = document.getElementById('filter-bsis');
                    const avmEl = document.getElementById('filter-avm');
                    const bsdEl = document.getElementById('filter-bsd');
                    const aiEl = document.getElementById('filter-ai');
                    const chEl = document.getElementById('filter-ch');

                    const dms = dmsEl ? dmsEl.checked : false;
                    const adas = adasEl ? adasEl.checked : false;
                    const dsc = dscEl ? dscEl.checked : false;
                    const bsis = bsisEl ? bsisEl.checked : false;
                    const avm = avmEl ? avmEl.checked : false;
                    const bsd = bsdEl ? bsdEl.value : 'Any';
                    const ai = aiEl ? aiEl.value : 'Any';
                    const ch = chEl ? chEl.value : 'Any';

                    const container = document.getElementById('matrixResults');
                    if (!container) return;

                    let html = '';

                    (matrixData || []).forEach(item => {
                        let match = true;
                        
                        // Checkbox requires 'YES' if clicked
                        if (dms && item.dms !== 'YES') match = false;
                        if (adas && item.adas !== 'YES') match = false;
                        if (dsc && item.dsc !== 'YES') match = false;
                        if (bsis && item.bsis !== 'YES') match = false;
                        if (avm && item.avm !== 'YES') match = false;
                        
                        // Dropdown logic
                        if (bsd !== 'Any' && item.bsd !== bsd) match = false;
                        if (ai !== 'Any' && item.ai !== ai) match = false;
                        if (ch !== 'Any' && item.ch !== ch) match = false;

                        if (match) {
                            const formulaStr = item.composition || item.sol || "";
                            html += `
                                <div class="bg-black/30 border border-white/10 rounded-lg pb-3 hover:border-white/20 transition-all flex flex-col overflow-visible mb-3 relative">
                                    ${makeClickableFormula(formulaStr)}
                                    <div class="flex gap-2 text-[10px] uppercase font-bold tracking-wider mt-1 ml-4">
                                        <span class="bg-white/5 text-gray-400 px-2 py-1 rounded">${item.ai || 'N/A'}</span>
                                        <span class="bg-white/5 text-gray-400 px-2 py-1 rounded">${item.ch || 'N/A'}</span>
                                    </div>
                                </div>
                            `;
                        }
                    });

                    if (html === '') {
                        html = `
                            <div class="text-center text-gray-500 py-10 w-full rounded-xl bg-black/20 border border-white/5">
                                <i class="fa-solid fa-filter-circle-xmark text-3xl mb-3 opacity-50"></i>
                                <h3 class="text-white text-base mb-1">No Matching Architectures</h3>
                                <p class="text-xs">Adjust your filters to discover valid configurations.</p>
                            </div>
                        `;
                    }
                    container.innerHTML = html;
                }

                // --- SEARCH ENGINE LOGIC ---
                function highlightText(text, query) {
                    if (!text) return '';
                    const strText = String(text);
                    if (!query) return strText;
                    
                    // Simple escape
                    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    const regex = new RegExp(`(${escapedQuery})(?![^<]*>)`, 'gi');
                    return strText.replace(regex, '<span class="highlight">$1</span>');
                }

                function performSearch() {
                    const searchInput = document.getElementById('searchInput');
                    const clearBtn = document.getElementById('clearBtn');
                    const resultsContainer = document.getElementById('resultsContainer');
                    const searchWrapper = document.getElementById('searchWrapper');
                    const statsBar = document.getElementById('statsBar');
                    const mascotImg = document.getElementById('mascotImage');
                    const resultCount = document.getElementById('resultCount');
                    
                    if (!searchInput) return;

                    const rawQuery = searchInput.value.trim();
                    const query = rawQuery.toLowerCase();
                    
                    if (query.length > 0) {
                        if (searchWrapper) searchWrapper.classList.add('active-search');
                        if (clearBtn) clearBtn.style.display = 'block';
                    } else {
                        if (searchWrapper) searchWrapper.classList.remove('active-search');
                        if (clearBtn) clearBtn.style.display = 'none';
                        if (resultsContainer) resultsContainer.innerHTML = '';
                        if (statsBar) statsBar.classList.remove('show');
                        if (mascotImg) {
                            mascotImg.src = 'https://drive.google.com/thumbnail?id=1bXf5psHrw4LOk0oMAkTJRL15_mLCabad&sz=w500';
                            mascotImg.classList.remove('jumping-heart');
                        }
                        return;
                    }

                    // Bulletproof search logic with fallback strings to prevent toLowerCase() crashes
                    const isExactMatch = terminologyDB.some(item => {
                        const termSafe = item.term ? String(item.term) : '';
                        return item.exact && termSafe.toLowerCase() === rawQuery.toLowerCase();
                    });
                    
                    if (mascotImg) {
                        if (isExactMatch) {
                            mascotImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23ff3366"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';
                            mascotImg.classList.add('jumping-heart');
                        } else {
                            mascotImg.src = 'https://drive.google.com/thumbnail?id=1bXf5psHrw4LOk0oMAkTJRL15_mLCabad&sz=w500';
                            mascotImg.classList.remove('jumping-heart');
                        }
                    }

                    const scoredResults = terminologyDB.map(item => {
                        let score = 0;
                        const safeTerm = item.term ? String(item.term).toLowerCase() : '';
                        const safeDesc = item.desc ? String(item.desc).toLowerCase() : '';
                        const safeCat = item.category ? String(item.category).toLowerCase() : '';

                        if (item.exact) {
                            if (safeTerm === rawQuery.toLowerCase()) score += 1000;
                        } else {
                            if (safeTerm === query) score += 1000;
                            else if (safeTerm.includes(query)) score += 500;
                            
                            if (item.related && Array.isArray(item.related)) {
                                if (item.related.some(r => r && String(r).toLowerCase() === query)) score += 400;
                                else if (item.related.some(r => r && String(r).toLowerCase().includes(query))) score += 300;
                            }
                            
                            if (safeCat === query) score += 50;
                            else if (safeCat.includes(query)) score += 20;
                            if (safeDesc.includes(query)) score += 10;
                        }
                        return { item, score };
                    }).filter(scoredItem => scoredItem.score > 0);

                    scoredResults.sort((a, b) => b.score - a.score);
                    const results = scoredResults.map(s => s.item);

                    if (statsBar) statsBar.classList.add('show');
                    if (resultCount) resultCount.textContent = results.length;

                    if (!resultsContainer) return;

                    if (results.length === 0) {
                        resultsContainer.innerHTML = `
                            <div style="text-align: center; color: var(--text-grey); padding: 40px;">
                                <i class="fa-solid fa-ghost" style="font-size: 2rem; color: var(--primary-green); margin-bottom: 15px;"></i>
                                <p>No results found for "<strong>${rawQuery}</strong>".</p>
                            </div>`;
                        return;
                    }

                    resultsContainer.innerHTML = results.map((item, index) => {
                        const delay = index * 0.05;
                        let downHTML = '';
                        
                        if (item.file) {
                            let singleLabel = (item.term && item.term.includes("DMS")) ? "Download DMS vs. DSC white paper" : "Download Document";
                            if (ENABLE_DOWNLOADS) {
                                downHTML += `<a href="${item.file}" target="_blank" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${singleLabel}</a>`;
                            } else {
                                downHTML += `<button onclick="window.showSecurityWarning(this)" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${singleLabel}</button>`;
                            }
                        }
                        
                        if (item.files && Array.isArray(item.files)) {
                            item.files.forEach(f => {
                                if (ENABLE_DOWNLOADS) {
                                    downHTML += `<a href="${f.url}" target="_blank" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${f.label}</a>`;
                                } else {
                                    downHTML += `<button onclick="window.showSecurityWarning(this)" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${f.label}</button>`;
                                }
                            });
                        }
                        
                        let relHTML = (item.related && item.related.length > 0) ? `<div style="margin-top: 8px;"><button class="relevance-btn" onclick="window.openRelevanceGraph('${item.term}', this)"><i class="fa-solid fa-project-diagram"></i> Relevance</button></div>` : '';
                        
                        return `
                            <div class="result-card" style="animation-delay: ${delay}s">
                                <div class="term-header">
                                    <h3 class="term-title">${highlightText(item.term, query)}</h3>
                                    <span class="term-category">${highlightText(item.category, query)}</span>
                                </div>
                                <p class="term-desc">${highlightText(item.desc, query)}</p>
                                ${relHTML}
                                ${downHTML}
                            </div>
                        `;
                    }).join('');
                }

                // --- MODAL & GRAPH LOGIC ---
                window.showSecurityWarning = function(btnElement) {
                    const overlay = document.getElementById('securityModal');
                    const modalBox = overlay ? overlay.querySelector('.modal-box') : null;
                    
                    if (!overlay || !modalBox) return;

                    const docHeight = Math.max(
                        document.body.scrollHeight, document.documentElement.scrollHeight,
                        document.body.offsetHeight, document.documentElement.offsetHeight,
                        document.documentElement.clientHeight
                    );
                    overlay.style.height = docHeight + 'px';
                    
                    if (btnElement) {
                        const rect = btnElement.getBoundingClientRect();
                        const absoluteY = rect.top + window.scrollY; 
                        
                        let boxHeight = modalBox.offsetHeight || 350;
                        let boxTop = absoluteY - (boxHeight / 2) + (rect.height / 2); 
                        
                        if (boxTop < 20) boxTop = 20; 
                        if (boxTop + boxHeight + 20 > docHeight) boxTop = docHeight - boxHeight - 20;
                        
                        modalBox.style.top = boxTop + 'px';
                    } else {
                        modalBox.style.top = (window.scrollY + 100) + 'px';
                    }
                    
                    overlay.classList.add('active');
                };

                function getCenterSafe(node) {
                    let x = node.offsetWidth / 2;
                    let y = node.offsetHeight / 2;
                    let current = node;
                    while (current && current.id !== 'graphContainer') {
                        x += current.offsetLeft;
                        y += current.offsetTop;
                        current = current.offsetParent;
                    }
                    return { x, y };
                }

                let isGraphDragging = false;
                let hasGraphDragged = false;
                let graphStartX = 0;
                let graphStartY = 0;
                let graphTranslateX = 0;
                let graphTranslateY = 0;

                window.openRelevanceGraph = function(termName, btnElement) {
                    const termData = terminologyDB.find(t => t.term === termName);
                    if (!termData || !termData.related) return;

                    const overlay = document.getElementById('relevanceModal');
                    const modalBox = overlay ? overlay.querySelector('.modal-box') : null;
                    
                    if (!overlay || !modalBox) return;

                    const docHeight = Math.max(
                        document.body.scrollHeight, document.documentElement.scrollHeight,
                        document.body.offsetHeight, document.documentElement.offsetHeight,
                        document.documentElement.clientHeight
                    );
                    overlay.style.height = docHeight + 'px';
                    
                    if (btnElement) {
                        const rect = btnElement.getBoundingClientRect();
                        const absoluteY = rect.top + window.scrollY; 
                        
                        let boxHeight = modalBox.offsetHeight || 600;
                        let boxTop = absoluteY - (boxHeight / 2) + (rect.height / 2); 
                        
                        if (boxTop < 20) boxTop = 20; 
                        if (boxTop + boxHeight + 20 > docHeight) boxTop = docHeight - boxHeight - 20;
                        
                        modalBox.style.top = boxTop + 'px';
                    } else {
                        modalBox.style.top = (window.scrollY + 100) + 'px';
                    }

                    const expBox = document.getElementById('modalChildExplanation');
                    if (expBox) expBox.classList.remove('active');
                    
                    const masterNode = document.getElementById('graphMasterNode');
                    if (masterNode) masterNode.innerText = termData.term;

                    const dist1 = termData.related || [];
                    const allRelatedTermsSet = new Set(dist1);
                    dist1.forEach(d1 => {
                        const d1Data = terminologyDB.find(t => t.term === d1);
                        if (d1Data && d1Data.related) d1Data.related.forEach(d2 => { if (d2 !== termName) allRelatedTermsSet.add(d2); });
                    });

                    const allRelated = Array.from(allRelatedTermsSet);
                    const clusters = [], visited = new Set();

                    allRelated.forEach(term => {
                        if (!visited.has(term)) {
                            const cluster = [], queue = [term];
                            visited.add(term);
                            while (queue.length > 0) {
                                const curr = queue.shift();
                                cluster.push(curr);
                                const currData = terminologyDB.find(t => t.term === curr);
                                if (currData && currData.related) {
                                    currData.related.forEach(n => {
                                        if (allRelated.includes(n) && !visited.has(n)) { visited.add(n); queue.push(n); }
                                    });
                                }
                            }
                            clusters.push(cluster);
                        }
                    });

                    clusters.forEach(c => c.sort((a,b) => {
                        const catA = (terminologyDB.find(t=>t.term===a)?.category || '');
                        const catB = (terminologyDB.find(t=>t.term===b)?.category || '');
                        return catA.localeCompare(catB);
                    }));
                    clusters.sort((a,b) => {
                        const catA = (terminologyDB.find(t=>t.term===a[0])?.category || '');
                        const catB = (terminologyDB.find(t=>t.term===b[0])?.category || '');
                        return catA.localeCompare(catB);
                    });

                    const grouped = clusters.flat();
                    const relatedNodesContainer = document.getElementById('graphRelatedNodes');
                    if (relatedNodesContainer) relatedNodesContainer.innerHTML = '';

                    grouped.forEach(rTerm => {
                        const n = document.createElement('div');
                        n.className = 'round-node node-related';
                        if (!dist1.includes(rTerm)) n.classList.add('node-dist2');
                        n.innerText = rTerm; n.dataset.term = rTerm;
                        n.onclick = (e) => { if (hasGraphDragged) return; window.showChildTerm(rTerm); };
                        if (relatedNodesContainer) relatedNodesContainer.appendChild(n);
                    });

                    overlay.classList.add('active');

                    setTimeout(() => {
                        const vp = document.getElementById('graphViewport');
                        const ct = document.getElementById('graphContainer');
                        const mn = document.getElementById('graphMasterNode');
                        
                        if (!vp || !ct || !mn) return;

                        ct.style.transform = 'translate(0,0)';
                        
                        const vpWidth = vp.offsetWidth;
                        const vpHeight = vp.offsetHeight;
                        const masterCenter = getCenterSafe(mn);
                        
                        graphTranslateX = (vpWidth * 0.3) - masterCenter.x;
                        graphTranslateY = (vpHeight * 0.5) - masterCenter.y;
                        
                        ct.style.transform = `translate(${graphTranslateX}px, ${graphTranslateY}px)`;
                        drawLines();
                        
                        if (document.fonts) document.fonts.ready.then(() => drawLines());
                    }, 50);
                };

                function drawLines() {
                    const svg = document.getElementById('graphLines');
                    if (!svg) return;
                    svg.innerHTML = '';
                    
                    const mNode = document.getElementById('graphMasterNode');
                    if (!mNode) return;
                    
                    const mCenter = getCenterSafe(mNode);
                    const mData = terminologyDB.find(t => t.term === mNode.innerText);
                    const d1Terms = mData?.related || [];
                    const nodes = Array.from(document.querySelectorAll('.node-related'));
                    const drawn = new Set();

                    nodes.forEach(n => {
                        if (d1Terms.includes(n.dataset.term)) {
                            const nc = getCenterSafe(n);
                            const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                            l.setAttribute('x1', mCenter.x); l.setAttribute('y1', mCenter.y);
                            l.setAttribute('x2', nc.x); l.setAttribute('y2', nc.y);
                            l.setAttribute('stroke', 'rgba(255,255,255,0.15)'); l.setAttribute('stroke-width', '2');
                            svg.appendChild(l);
                        }
                    });

                    nodes.forEach(na => {
                        const da = terminologyDB.find(t => t.term === na.dataset.term);
                        if (da && da.related) {
                            da.related.forEach(tb => {
                                const nb = nodes.find(n => n.dataset.term === tb);
                                if (nb) {
                                    const key = [na.dataset.term, tb].sort().join('|');
                                    if (!drawn.has(key)) {
                                        drawn.add(key);
                                        const ca = getCenterSafe(na), cb = getCenterSafe(nb);
                                        const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                                        const midX = Math.max(ca.x, cb.x) + (Math.abs(ca.y - cb.y) * 0.35);
                                        const midY = (ca.y + cb.y) / 2;
                                        p.setAttribute('d', `M ${ca.x} ${ca.y} Q ${midX} ${midY} ${cb.x} ${cb.y}`);
                                        p.setAttribute('stroke', 'rgba(255,255,255,0.15)'); p.setAttribute('stroke-width', '2'); p.setAttribute('fill', 'none');
                                        svg.appendChild(p);
                                    }
                                }
                            });
                        }
                    });
                }

                window.showChildTerm = function(name) {
                    const d = terminologyDB.find(t => t.term === name);
                    if (!d) return;
                    const b = document.getElementById('modalChildExplanation');
                    if (!b) return;
                    
                    const safeTerm = d.term || '';
                    const safeDesc = d.desc || '';
                    b.innerHTML = `<div style="font-weight:700; color:#2AF598; margin-bottom:5px; font-size: 1.1rem;">${safeTerm}</div><div style="font-size:0.95rem; color:#A0AEC0;">${safeDesc}</div><button class="see-details-btn" onclick="window.masterSearch('${safeTerm}')">See Details <i class="fa-solid fa-arrow-right"></i></button>`;
                    b.classList.add('active');
                };

                window.closeModal = function() { 
                    const modal = document.getElementById('relevanceModal');
                    if (modal) modal.classList.remove('active'); 
                    const secModal = document.getElementById('securityModal');
                    if (secModal) secModal.classList.remove('active');
                };
                
                window.masterSearch = function(name) {
                    window.closeModal();
                    const searchInput = document.getElementById('searchInput');
                    if (searchInput) {
                        searchInput.value = name;
                        performSearch();
                    }
                    const searchWrapper = document.getElementById('searchWrapper');
                    if (searchWrapper) {
                        searchWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                };

                // --- APP INITIALIZATION ---
                function initStreamaxpedia() {
                    // 1. Search Engine Bindings
                    const searchInput = document.getElementById('searchInput');
                    const clearBtn = document.getElementById('clearBtn');
                    
                    if (searchInput) {
                        searchInput.addEventListener('input', performSearch);
                    }
                    if (clearBtn) {
                        clearBtn.addEventListener('click', () => {
                            if (searchInput) {
                                searchInput.value = ''; 
                                searchInput.focus(); 
                            }
                            performSearch();
                        });
                    }

                    // 2. Relevance Graph Bindings
                    const vp = document.getElementById('graphViewport');
                    const ct = document.getElementById('graphContainer');
                    if (vp && ct) {
                        vp.onmousedown = (e) => { isGraphDragging = true; hasGraphDragged = false; graphStartX = e.clientX - graphTranslateX; graphStartY = e.clientY - graphTranslateY; };
                        window.addEventListener('mousemove', (e) => { if(isGraphDragging) { if(Math.abs(e.clientX - graphStartX - graphTranslateX)>3 || Math.abs(e.clientY - graphStartY - graphTranslateY)>3) hasGraphDragged = true; graphTranslateX = e.clientX - graphStartX; graphTranslateY = e.clientY - graphStartY; ct.style.transform = `translate(${graphTranslateX}px, ${graphTranslateY}px)`; } });
                        window.addEventListener('mouseup', () => isGraphDragging = false);
                        vp.onclick = (e) => { 
                            const modalChild = document.getElementById('modalChildExplanation');
                            if(!hasGraphDragged && !e.target.closest('.node-related') && modalChild && !modalChild.contains(e.target)) {
                                modalChild.classList.remove('active'); 
                            }
                        };
                    }
            
                    if (typeof ResizeObserver !== 'undefined') {
                        const modalBox = document.querySelector('.modal-box');
                        if (modalBox) {
                            new ResizeObserver(() => {
                                const modal = document.getElementById('relevanceModal');
                                if (modal && modal.classList.contains('active')) {
                                    drawLines();
                                }
                            }).observe(modalBox);
                        }
                    }
                }
                
                // Execute immediately bypassing DOMContentLoaded timing issues in iframes
                initStreamaxpedia();
                
                window.viewSecurityPolicy = function() {
                    try {
                        if (pdfBase64 && pdfBase64.length > 0) {
                            // Decode base64 to a standard Blob representing the PDF
                            const byteCharacters = atob(pdfBase64);
                            const byteNumbers = new Array(byteCharacters.length);
                            for (let i = 0; i < byteCharacters.length; i++) {
                                byteNumbers[i] = byteCharacters.charCodeAt(i);
                            }
                            const byteArray = new Uint8Array(byteNumbers);
                            const blob = new Blob([byteArray], { type: 'application/pdf' });
                            const url = URL.createObjectURL(blob);
                            
                            const newWindow = window.open(url, '_blank');
                            
                            // If pop-ups are blocked, download it automatically
                            if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = 'Streamax_Security_Policy.pdf';
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                alert("Popup blocked! The PDF document has been downloaded to your computer instead.");
                            }
                            
                            setTimeout(() => URL.revokeObjectURL(url), 5000);
                            
                        } else {
                            // Fallback to HTML if PDF is missing from the server
                            alert("The original PDF file was not found on the server. Please contact your administrator.");
                        }
                    } catch (e) {
                        alert('Error attempting to render the document. Please allow pop-ups or check your browser settings.');
                    }
                };
            </script>
        </div>
"""

# Stitch everything together into a variable that app.py imports
content = css_and_html + js_code
