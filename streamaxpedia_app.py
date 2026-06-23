import json
import os
import base64
import re
import itertools
from terminology_db import TERMINOLOGY_DB, PRODUCT_COMBINATIONS


# --- Jerry GPT portrait loader (used by the launch card below) -----------
def _load_jerry_portrait_data_uri() -> str | None:
    """Return Jerry's portrait as a base64 data URI, or None if not present.

    Looks for any of: assets/jerry.jpg, jerry.jpeg, jerry.png, jerry.webp
    in the same folder as this file. Encodes the bytes inline so the image
    travels with the components.html iframe (no static-file server needed).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        ("assets/jerry.jpg", "image/jpeg"),
        ("assets/jerry.jpeg", "image/jpeg"),
        ("assets/jerry.png", "image/png"),
        ("assets/jerry.webp", "image/webp"),
    ]
    for rel, mime in candidates:
        path = os.path.join(base_dir, rel)
        if os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                return f"data:{mime};base64,{b64}"
            except Exception:
                continue
    return None


JERRY_PORTRAIT_URI = _load_jerry_portrait_data_uri()


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

                /* --- SPECIAL FEATURE CTA (e.g. Emily → Jack GPT) --- */
                .special-feature-wrap {
                    margin-top: 14px;
                    padding: 12px 14px;
                    background: linear-gradient(135deg, rgba(42,245,152,0.06) 0%, rgba(0,158,253,0.06) 100%);
                    border: 1px solid rgba(42,245,152,0.22);
                    border-radius: 12px;
                }
                .special-feature-title {
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    color: var(--primary-green);
                    margin-bottom: 6px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                .special-feature-title i { font-size: 0.75rem; }
                .special-blurb {
                    font-size: 0.82rem;
                    color: var(--text-grey);
                    margin-bottom: 10px;
                    line-height: 1.45;
                }
                .special-feature-btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 9px 18px;
                    border-radius: 22px;
                    text-decoration: none;
                    font-size: 0.85rem;
                    font-weight: 700;
                    cursor: pointer;
                    background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%);
                    color: #050810;
                    border: none;
                    transition: var(--transition);
                    box-shadow: 0 6px 14px rgba(42,245,152,0.18);
                }
                .special-feature-btn:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 10px 22px rgba(42,245,152,0.30);
                }

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
                
                /* ---- Ecosystem topology graph (D3) ---- */
                .topo-header { width:100%; display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap; }
                .topo-title { color:var(--text-white); font-size:1.25rem; font-weight:700; margin:0; }
                .topo-sub { color:var(--text-grey); font-size:0.78rem; margin-top:4px; }
                .topo-tools { display:flex; align-items:center; gap:8px; }
                .topo-search { background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.12); border-radius:8px; color:var(--text-white); padding:7px 12px; font-size:0.85rem; outline:none; width:170px; }
                .topo-search:focus { border-color:var(--primary-green); }
                .topo-btn { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12); color:var(--text-grey); border-radius:8px; padding:7px 12px; font-size:0.8rem; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:6px; transition:var(--transition); }
                .topo-btn:hover { border-color:var(--primary-green); color:var(--primary-green); }

                .topo-legend { width:100%; display:flex; flex-wrap:wrap; gap:8px 14px; margin:12px 0 4px; }
                .topo-legend-item { display:inline-flex; align-items:center; gap:6px; font-size:0.74rem; color:var(--text-grey); cursor:pointer; user-select:none; padding:2px 6px; border-radius:6px; transition:all 0.15s; }
                .topo-legend-item:hover { background:rgba(255,255,255,0.05); color:var(--text-white); }
                .topo-legend-item.off { opacity:0.35; text-decoration:line-through; }
                .topo-legend-dot { width:11px; height:11px; border-radius:50%; flex-shrink:0; }

                .topo-viewport { width:100%; flex:1; position:relative; overflow:hidden; background:rgba(0,0,0,0.25); border-radius:12px; margin-top:8px; border:1px solid rgba(255,255,255,0.06); cursor:grab; }
                .topo-viewport:active { cursor:grabbing; }
                #topoSvg { width:100%; height:100%; display:block; }
                #topoSvg text { font-family:'Inter',sans-serif; pointer-events:none; user-select:none; }
                #topoSvg .topo-node { cursor:pointer; }

                .topo-tooltip { position:absolute; pointer-events:none; background:rgba(5,8,16,0.96); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:8px 11px; font-size:0.78rem; color:var(--text-white); max-width:260px; line-height:1.45; z-index:30; opacity:0; transition:opacity 0.12s; box-shadow:0 8px 24px rgba(0,0,0,0.5); }
                .topo-tooltip.show { opacity:1; }
                .topo-tooltip .tt-cat { font-size:0.62rem; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:3px; }

                .topo-detail { position:absolute; top:14px; left:14px; width:300px; max-width:60%; z-index:40; background:rgba(5,8,16,0.97); border:1px solid rgba(255,255,255,0.12); border-left:4px solid var(--primary-green); border-radius:10px; padding:16px 18px; box-shadow:0 12px 32px rgba(0,0,0,0.6); display:none; }
                .topo-detail.show { display:block; animation:spediaFadeUp 0.25s ease-out forwards; }
                .topo-detail .td-cat { font-size:0.62rem; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; margin-bottom:5px; }
                .topo-detail .td-title { color:var(--text-white); font-size:1.1rem; font-weight:700; margin-bottom:7px; }
                .topo-detail .td-desc { color:var(--text-grey); font-size:0.88rem; line-height:1.55; }
                .topo-detail .td-conn { color:var(--text-grey); font-size:0.78rem; margin-top:10px; }
                .topo-detail .td-conn b { color:var(--text-white); font-weight:600; }
                .topo-detail .td-close { position:absolute; top:8px; right:10px; background:none; border:none; color:var(--text-grey); cursor:pointer; font-size:1rem; }
                .topo-detail .td-close:hover { color:var(--text-white); }
                .see-details-btn { background:var(--secondary-blue); color:#fff; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:600; font-size:0.83rem; margin-top:14px; display:inline-flex; align-items:center; gap:8px; transition:var(--transition); }
                .see-details-btn:hover { background:var(--primary-green); color:var(--bg-deep); }

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
                <button class="sub-nav-btn" onclick="switchSpediaMode('spedia-jerry-mode', this)">
                    <i class="fa-solid fa-robot"></i> Jerry GPT
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
                            This is a temporary Streamax info library. Check out Jerry GPT for more!
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

            <!-- MODE 3: JERRY GPT -->
            <div id="spedia-jerry-mode" class="spedia-mode hidden w-full">
                <style>
                    .jerry-portrait-wrap {
                        width: 140px; height: 140px; margin: 0 auto 24px;
                        border-radius: 50%;
                        padding: 4px;
                        background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%);
                        box-shadow: 0 0 40px rgba(42, 245, 152, 0.25), 0 10px 30px rgba(0,0,0,0.4);
                        animation: jerryFloat 5s ease-in-out infinite;
                    }
                    .jerry-portrait-wrap img {
                        width: 100%; height: 100%;
                        border-radius: 50%;
                        object-fit: cover;
                        display: block;
                        border: 3px solid #050810;
                        background: #050810;
                    }
                    .jerry-portrait-fallback {
                        width: 100%; height: 100%;
                        border-radius: 50%;
                        background: #050810;
                        border: 3px solid #050810;
                        display: flex; align-items: center; justify-content: center;
                    }
                    .jerry-portrait-fallback i {
                        font-size: 4rem;
                        background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%);
                        -webkit-background-clip: text; background-clip: text; color: transparent;
                    }
                    @keyframes jerryFloat {
                        0%, 100% { transform: translateY(0); }
                        50% { transform: translateY(-8px); }
                    }
                </style>
                <div class="w-full max-w-5xl mx-auto px-4 mt-8 fade-up">
                    <div class="card" style="text-align: center; padding: 50px 30px;">
                        <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; background:rgba(42,245,152,0.08); border:1px solid rgba(42,245,152,0.25); border-radius:30px; color:var(--primary-green); font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin-bottom:24px;">
                            <i class="fa-solid fa-sparkles"></i> NEW
                        </div>
                        <div class="jerry-portrait-wrap">
                            __JERRY_PORTRAIT_HTML__
                        </div>
                        <h2 style="font-size: 2.4rem; margin-bottom: 12px; letter-spacing: -1px;"><span class="gradient-text">Jerry GPT</span></h2>
                        <p style="color: var(--text-grey); max-width: 680px; margin: 0 auto 28px; font-size: 1.05rem; line-height: 1.65;">
                            A digital version of Jerry — Streamax's Product Marketing Director.
                            Ten years inside Streamax, distilled into one conversation — so you walk into every customer meeting with a sharper, more convincing pitch.
                            Ask anything about positioning, the competitive landscape, regional plays,
                            product portfolio, or how to handle a specific customer conversation.
                        </p>
                        <a href="?view=jerry_gpt" target="_blank" rel="noopener" onclick="
                            (function(evt, anchor) {
                                evt.preventDefault();
                                // Detect the parent Streamlit app's URL.
                                // Inside components.html iframe, document.referrer points at the parent.
                                var base = '';
                                try { if (document.referrer) base = document.referrer; } catch (e) {}
                                if (!base) {
                                    try { base = window.parent.location.href; } catch (e) { base = ''; }
                                }
                                if (!base) base = anchor.href;
                                // Strip any existing query/hash from the base URL
                                var url = base.split('?')[0].split('#')[0] + '?view=jerry_gpt';
                                window.open(url, '_blank', 'noopener');
                            })(event, this);
                            return false;
                        " style="display: inline-flex; align-items: center; gap: 10px; background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%); color: #050810; font-weight: 700; font-size: 1.05rem; padding: 14px 32px; border-radius: 30px; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 10px 20px rgba(42, 245, 152, 0.2); cursor: pointer;">
                            Open Jerry GPT <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </a>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 fade-up">
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                            <div style="color: var(--primary-green); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-comments"></i></div>
                            <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Conversational</h4>
                            <p style="font-size: 0.9rem; color: var(--text-grey);">Streaming responses with full chat history. Ask follow-ups, dig deeper, switch topics — Jerry holds context.</p>
                        </div>
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                            <div style="color: var(--secondary-blue); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-book-open"></i></div>
                            <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Knowledge-grounded</h4>
                            <p style="font-size: 0.9rem; color: var(--text-grey);">Sales playbook, value propositions, global strategy, and white papers all live in Jerry's working memory.</p>
                        </div>
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                            <div style="color: var(--primary-green); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-bullhorn"></i></div>
                            <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Jerry's voice</h4>
                            <p style="font-size: 0.9rem; color: var(--text-grey);">Numbers, sources, structured frameworks. Leads with outcomes, never with feature lists. Sharp closers.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ECOSYSTEM TOPOLOGY MODAL (interactive D3 force graph) -->
            <div class="modal-overlay" id="relevanceModal">
                <div class="modal-box" id="topoModalBox">
                    <button class="close-modal" onclick="window.closeModal()"><i class="fa-solid fa-xmark"></i></button>
                    <div class="topo-header">
                        <div>
                            <h3 class="topo-title">Streamax Ecosystem Map</h3>
                            <div class="topo-sub" id="topoSub">Drag to pan · scroll to zoom · hover to focus · click a node for details</div>
                        </div>
                        <div class="topo-tools">
                            <input type="text" id="topoSearch" class="topo-search" placeholder="Find a term…" autocomplete="off">
                            <button class="topo-btn" id="topoReset" title="Reset view"><i class="fa-solid fa-expand"></i> Fit</button>
                        </div>
                    </div>
                    <div class="topo-legend" id="topoLegend"></div>
                    <div class="topo-viewport" id="topoViewport">
                        <svg id="topoSvg" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"></svg>
                        <div class="topo-tooltip" id="topoTooltip"></div>
                        <div class="topo-detail" id="topoDetail"></div>
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

# ---------------------------------------------------------------------------
# ECOSYSTEM TOPOLOGY — curated, accurate product/relationship graph distilled
# from the Jerry knowledge base (company/products, SafeGPT, school bus, public
# transport, mining, eSIM, CAN, Vision 2.0). Replaces the old auto-generated
# relevance graph. Rendered as an interactive D3 force-directed map.
#   cat: capability | device | camera | platform | solution | competitor
# ---------------------------------------------------------------------------
_TOPO_NODES = [
    # Capabilities
    ("ADAS", "capability", "Advanced Driver Assistance — forward-collision, lane-departure, headway and pedestrian warnings."),
    ("DMS", "capability", "Driver Monitoring — fatigue, distraction, phone, smoking, seatbelt via in-cab face-tracing AI."),
    ("BSD", "capability", "Blind Spot Detection — warns of pedestrians/cyclists in the vehicle's blind zones; predicts trajectory."),
    ("AVM", "capability", "Around-View Monitor — stitched seamless 360° bird's-eye view of the vehicle."),
    ("DSC", "capability", "Driver Safety Camera — entry-level driver-facing safety, below a full DMS."),
    ("Child Check", "capability", "Anti-left-behind — guarantees no child is left on a school bus (button + AI camera + motion sensor)."),
    ("APC", "capability", "Automatic Passenger Counting — boarding/alighting counts plus origin-destination analysis."),
    ("Stop-Arm Capture", "capability", "Captures vehicles illegally passing a stopped school bus with court-grade evidence."),
    ("ANPR", "capability", "Automatic Number Plate Recognition — reads license plates for evidence/enforcement."),
    ("V2V", "capability", "Vehicle-to-vehicle warning beyond line of sight, independent of network infrastructure."),
    ("Blacklight", "capability", "Full-colour night vision in near-darkness (down to ~0.5 / 0.02 lux)."),
    ("CAN / OBD", "capability", "Reads the vehicle bus (fuel, RPM, DTCs) — the $20 inherent-CAN license on the AD Plus 2.0."),
    ("eSIM", "capability", "Built-in connectivity (eSIM / eUICC) — OTA carrier provisioning, lower TCO, higher uptime."),
    # Platforms / cloud
    ("SafeGPT", "platform", "Cloud behavioural-AI engine — prioritises risk, profiles & coaches drivers, real-time accident response."),
    ("FT Cloud", "platform", "Fleet management platform (trucking) — devices, video, telematics, CAN, alerts."),
    ("SBS Cloud", "platform", "School Bus Solution cloud — attendance, child-check, stop-arm evidence."),
    ("PT Cloud", "platform", "Public Transport platform — safety, passenger-flow analytics, operations."),
    ("MineSync-Cloud", "platform", "Mining production + transportation safety platform (big-data + video AI)."),
    # Devices / MDVRs
    ("AD Plus 2.0", "device", "Flagship 3-channel AI dashcam/MDVR — hosts ADAS + DMS, inherent CAN."),
    ("C6 Lite 2.0", "device", "Cost-effective 2-channel AI dashcam — ADAS + DSC."),
    ("M1N 2.0", "device", "Entry MDVR — child check + attendance + surveillance (school bus / mining basic)."),
    ("X3N", "device", "MDVR for 2–4 lane stop-arm capture and standard buses."),
    ("X5N Pro", "device", "MDVR for 5–8 lane stop-arm capture / regional regulatory needs."),
    ("IBCU", "device", "Intelligent Bus Central Unit (A16Max) — all-in-one flagship, up to 24 HD ch, 6 TOPS."),
    ("M10", "device", "Mining MDVR (Advanced tier)."),
    ("M10 PRO", "device", "Mining MDVR flagship (+ thermal cam, fuel management)."),
    ("DC MAX", "device", "Next-gen AI dashcam — dual 2K lenses, onboard large AI model, dual tamper-proof storage."),
    ("GT1", "device", "Independent telematics gateway pairing with DC MAX."),
    ("FMS Tracker", "device", "Compact dead-reckoning asset tracker — positioning without GPS."),
    # Cameras / sensors
    ("C29N", "camera", "DMS driver-monitoring camera with face-tracing IR."),
    ("CA20S", "camera", "Single-lens ADAS camera."),
    ("C20D", "camera", "Dual-lens ADAS camera (adds near-pedestrian + close-range)."),
    ("CA20D", "camera", "Triple-lens ADAS camera (adds ANPR)."),
    ("C46", "camera", "Top-down BSD camera (16 m both sides)."),
    ("C53", "camera", "Flagship long-range black-light BSD (50 m lateral)."),
    ("CA24S", "camera", "Rear-to-front BSD camera for core blind-spot zones."),
    ("AI-AVM", "camera", "360° around-view monitor with transparent-vehicle effect."),
    ("CMS20", "camera", "Digital rear-view mirror (Blacklight 1.8T)."),
    ("C34", "camera", "AI child-check camera (92% accuracy)."),
    ("DP7S", "camera", "Motion sensor for child check (99.9% accuracy)."),
    ("P3", "camera", "Automatic passenger counter (99%)."),
    ("P3D", "camera", "Passenger counter + origin-destination (85%)."),
    ("Palm Vein Reader", "camera", "Palm-vein student attendance — forget/lose/copy-proof."),
    ("C28", "camera", "Stop-arm AI detection camera."),
    ("C27", "camera", "Stop-arm license-plate camera."),
    ("B2", "camera", "Stop-arm audio-visual alarm."),
    ("Thermal Smart CAM", "camera", "Thermal imaging camera (mining loading hazards)."),
    ("mmWave Radar", "camera", "Millimeter-wave radar — dust-penetrating, mining BSD / fusion."),
    # Solutions / verticals
    ("Fleet / Trucking", "solution", "Core video-telematics for commercial trucking fleets and TSP partners."),
    ("School Bus", "solution", "Known · protected · never left behind — attendance, stop-arm, child check."),
    ("Public Transport", "solution", "One platform, four jobs — driving safety, operations, passenger service, recording."),
    ("Mining", "solution", "Safety + intelligent dispatch for open-pit & underground mining fleets."),
    ("Cargo Security", "solution", "Trailer / cargo theft prevention with black-light in-cargo cameras."),
    # Competitors
    ("Samsara", "competitor", "US fleet-telematics incumbent — subscription dashcam + platform."),
    ("Motive", "competitor", "US fleet safety/ELD platform; missing fatigue/FCW/PCW today."),
    ("Lytx", "competitor", "Video-based driver-risk / DMS vendor."),
    ("Netradyne", "competitor", "AI dashcam / driver-behaviour vendor (Driveri)."),
    ("Geotab", "competitor", "Telematics / OBD data platform."),
    ("MiTac", "competitor", "OEM AI camera competitor."),
    ("Hikvision", "competitor", "Surveillance / camera vendor."),
]

_TOPO_LINKS = [
    # device → capability
    ("AD Plus 2.0", "ADAS"), ("AD Plus 2.0", "DMS"), ("AD Plus 2.0", "DSC"),
    ("AD Plus 2.0", "CAN / OBD"), ("AD Plus 2.0", "SafeGPT"),
    ("C6 Lite 2.0", "ADAS"), ("C6 Lite 2.0", "DSC"),
    ("DC MAX", "ADAS"), ("DC MAX", "DMS"), ("DC MAX", "DSC"), ("DC MAX", "SafeGPT"),
    ("GT1", "FT Cloud"), ("GT1", "eSIM"),
    ("FMS Tracker", "FT Cloud"), ("FMS Tracker", "eSIM"),
    ("IBCU", "ADAS"), ("IBCU", "DMS"), ("IBCU", "BSD"), ("IBCU", "AVM"),
    ("IBCU", "APC"), ("IBCU", "SafeGPT"),
    ("M10", "DMS"), ("M10", "BSD"), ("M10", "ADAS"),
    ("M10 PRO", "DMS"), ("M10 PRO", "BSD"), ("M10 PRO", "ADAS"), ("M10 PRO", "Thermal Smart CAM"),
    ("M1N 2.0", "Child Check"),
    ("X3N", "Stop-Arm Capture"), ("X3N", "Child Check"),
    ("X5N Pro", "Stop-Arm Capture"), ("X5N Pro", "BSD"),
    # camera → capability
    ("C29N", "DMS"), ("CA20S", "ADAS"), ("C20D", "ADAS"),
    ("CA20D", "ADAS"), ("CA20D", "ANPR"),
    ("C46", "BSD"), ("C53", "BSD"), ("C53", "Blacklight"), ("CA24S", "BSD"),
    ("AI-AVM", "AVM"), ("CMS20", "BSD"), ("CMS20", "Blacklight"),
    ("C34", "Child Check"), ("DP7S", "Child Check"),
    ("P3", "APC"), ("P3D", "APC"),
    ("C28", "Stop-Arm Capture"), ("C27", "Stop-Arm Capture"), ("C27", "ANPR"),
    ("B2", "Stop-Arm Capture"),
    ("Thermal Smart CAM", "Mining"), ("mmWave Radar", "BSD"), ("mmWave Radar", "Mining"),
    # platform wiring
    ("SafeGPT", "ADAS"), ("SafeGPT", "DMS"), ("SafeGPT", "BSD"),
    ("SafeGPT", "FT Cloud"), ("SafeGPT", "SBS Cloud"), ("SafeGPT", "PT Cloud"),
    ("SafeGPT", "MineSync-Cloud"),
    ("FT Cloud", "Fleet / Trucking"), ("SBS Cloud", "School Bus"),
    ("PT Cloud", "Public Transport"), ("MineSync-Cloud", "Mining"),
    ("eSIM", "FT Cloud"), ("CAN / OBD", "FT Cloud"),
    # solution → key parts
    ("Fleet / Trucking", "AD Plus 2.0"), ("Fleet / Trucking", "C6 Lite 2.0"),
    ("Fleet / Trucking", "DC MAX"), ("Fleet / Trucking", "GT1"), ("Fleet / Trucking", "FMS Tracker"),
    ("Fleet / Trucking", "ADAS"), ("Fleet / Trucking", "DMS"), ("Fleet / Trucking", "DSC"),
    ("School Bus", "M1N 2.0"), ("School Bus", "X3N"), ("School Bus", "X5N Pro"),
    ("School Bus", "IBCU"), ("School Bus", "Palm Vein Reader"), ("School Bus", "C34"),
    ("School Bus", "DP7S"), ("School Bus", "C28"), ("School Bus", "C27"), ("School Bus", "B2"),
    ("School Bus", "Child Check"), ("School Bus", "Stop-Arm Capture"),
    ("Public Transport", "IBCU"), ("Public Transport", "C29N"), ("Public Transport", "CA20D"),
    ("Public Transport", "C53"), ("Public Transport", "C46"), ("Public Transport", "AI-AVM"),
    ("Public Transport", "CMS20"), ("Public Transport", "P3"), ("Public Transport", "P3D"),
    ("Public Transport", "APC"), ("Public Transport", "BSD"), ("Public Transport", "AVM"),
    ("Mining", "M10"), ("Mining", "M10 PRO"), ("Mining", "V2V"), ("Mining", "DMS"), ("Mining", "BSD"),
    ("Cargo Security", "Blacklight"), ("Cargo Security", "FT Cloud"), ("Cargo Security", "Fleet / Trucking"),
    # competitor → where they compete
    ("Samsara", "Fleet / Trucking"), ("Samsara", "ADAS"), ("Samsara", "DMS"),
    ("Motive", "Fleet / Trucking"), ("Motive", "ADAS"), ("Motive", "DMS"),
    ("Lytx", "DMS"), ("Lytx", "ADAS"),
    ("Netradyne", "DMS"), ("Netradyne", "ADAS"),
    ("Geotab", "Fleet / Trucking"), ("Geotab", "CAN / OBD"),
    ("MiTac", "ADAS"), ("MiTac", "DMS"),
    ("Hikvision", "BSD"), ("Hikvision", "Public Transport"),
]

TOPOLOGY = {
    "nodes": [{"id": n, "cat": c, "desc": d} for (n, c, d) in _TOPO_NODES],
    "links": [{"source": a, "target": b} for (a, b) in _TOPO_LINKS],
}
topology_json = json.dumps(TOPOLOGY)


js_code = """
            <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
            <script>
                const terminologyDB = __TERMINOLOGY_DB_JSON__;
                const TOPOLOGY = __TOPOLOGY_JSON__;
                const matrixData = """ + matrix_json + """;
                const ALL_PRODUCTS = """ + products_json + """;
                const pdfBase64 = \"""" + pdf_base64 + """\";

                const ENABLE_DOWNLOADS = true;
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
                        
                        let relHTML = `<div style="margin-top: 8px;"><button class="relevance-btn" onclick="window.openRelevanceGraph('${item.term}', this)"><i class="fa-solid fa-diagram-project"></i> Ecosystem map</button></div>`;

                        // Special Feature: a custom CTA on a result card that
                        // navigates the PARENT Streamlit frame to ?view=<view>.
                        // Used today for Emily → Jack GPT; the routing trick
                        // mirrors the Jerry GPT launch card.
                        let specialHTML = '';
                        if (item.special && item.special.view) {
                            const sp = item.special;
                            const iconCls = sp.icon || 'fa-solid fa-sparkles';
                            const lbl = String(sp.label || 'Open');
                            const blurb = sp.blurb ? `<div class="special-blurb">${String(sp.blurb)}</div>` : '';
                            specialHTML = `
                                <div class="special-feature-wrap">
                                    <div class="special-feature-title"><i class="fa-solid fa-star"></i> Special Feature</div>
                                    ${blurb}
                                    <a href="?view=${encodeURIComponent(sp.view)}" target="_blank" rel="noopener" class="special-feature-btn" onclick="
                                        (function(evt, anchor) {
                                            evt.preventDefault();
                                            var base = '';
                                            try { if (document.referrer) base = document.referrer; } catch (e) {}
                                            if (!base) { try { base = window.parent.location.href; } catch (e) { base = ''; } }
                                            if (!base) base = anchor.href;
                                            var url = base.split('?')[0].split('#')[0] + '?view=${encodeURIComponent(sp.view)}';
                                            window.open(url, '_blank', 'noopener');
                                        })(event, this);
                                        return false;
                                    "><i class="${iconCls}"></i> ${lbl} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.75rem; margin-left:4px;"></i></a>
                                </div>
                            `;
                        }

                        return `
                            <div class="result-card" style="animation-delay: ${delay}s">
                                <div class="term-header">
                                    <h3 class="term-title">${highlightText(item.term, query)}</h3>
                                    <span class="term-category">${highlightText(item.category, query)}</span>
                                </div>
                                <p class="term-desc">${highlightText(item.desc, query)}</p>
                                ${relHTML}
                                ${specialHTML}
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

                // --- ECOSYSTEM TOPOLOGY (interactive D3 force graph) ---
                const TOPO_CAT = {
                    capability: { label: 'Capability',      color: '#2AF598' },
                    device:     { label: 'Device / MDVR',   color: '#009EFD' },
                    camera:     { label: 'Camera / Sensor', color: '#7F77DD' },
                    platform:   { label: 'Platform / Cloud',color: '#1D9E75' },
                    solution:   { label: 'Solution',        color: '#EF9F27' },
                    competitor: { label: 'Competitor',      color: '#E24B4A' },
                };
                let _topoState = null;

                window.openRelevanceGraph = function(termName, btnElement) {
                    const overlay = document.getElementById('relevanceModal');
                    const modalBox = document.getElementById('topoModalBox');
                    if (!overlay || !modalBox) return;
                    const docHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, document.documentElement.clientHeight);
                    overlay.style.height = docHeight + 'px';
                    let boxTop = (window.scrollY || 0) + 60;
                    if (btnElement) { const r = btnElement.getBoundingClientRect(); boxTop = r.top + window.scrollY - 50; }
                    if (boxTop < 20) boxTop = 20;
                    modalBox.style.top = boxTop + 'px';
                    overlay.classList.add('active');
                    const det = document.getElementById('topoDetail'); if (det) det.classList.remove('show');
                    const sb = document.getElementById('topoSub');
                    if (sb) sb.textContent = termName ? ('Focused on ' + termName + ' — drag · scroll to zoom · click any node') : 'Drag to pan · scroll to zoom · hover to focus · click a node for details';
                    setTimeout(() => renderTopology(termName || null), 70);
                };

                function _topoNeighbors(id, links) {
                    const s = new Set();
                    links.forEach(l => {
                        const a = (l.source.id || l.source), b = (l.target.id || l.target);
                        if (a === id) s.add(b); else if (b === id) s.add(a);
                    });
                    return s;
                }

                function renderTopology(focusId) {
                    if (typeof d3 === 'undefined') return;
                    const vp = document.getElementById('topoViewport');
                    const svgEl = document.getElementById('topoSvg');
                    if (!vp || !svgEl) return;
                    const W = vp.clientWidth || 880, H = vp.clientHeight || 420;

                    const nodes = TOPOLOGY.nodes.map(n => Object.assign({}, n));
                    const links = TOPOLOGY.links.map(l => Object.assign({}, l));
                    const hidden = (_topoState && _topoState.hidden) ? _topoState.hidden : new Set();

                    const svg = d3.select(svgEl);
                    svg.selectAll('*').remove();
                    svg.attr('viewBox', '0 0 ' + W + ' ' + H);
                    const root = svg.append('g');

                    const zoom = d3.zoom().scaleExtent([0.3, 3]).on('zoom', (e) => root.attr('transform', e.transform));
                    svg.call(zoom).on('dblclick.zoom', null);

                    const deg = {}; nodes.forEach(n => deg[n.id] = 0);
                    links.forEach(l => { deg[l.source]=(deg[l.source]||0)+1; deg[l.target]=(deg[l.target]||0)+1; });

                    const link = root.append('g').selectAll('line').data(links).join('line')
                        .attr('class','topo-link').attr('stroke','rgba(255,255,255,0.13)').attr('stroke-width',1.2);

                    const node = root.append('g').selectAll('g').data(nodes).join('g').attr('class','topo-node');
                    node.append('circle')
                        .attr('r', d => 7 + Math.min(10, (deg[d.id]||0)))
                        .attr('fill', d => (TOPO_CAT[d.cat]||{}).color || '#888')
                        .attr('stroke', '#050810').attr('stroke-width', 1.5);
                    node.append('text').text(d => d.id)
                        .attr('x', d => 11 + Math.min(10,(deg[d.id]||0))).attr('y', 4)
                        .attr('fill', '#E6EAF0').attr('font-size', '10px').attr('font-weight','500');

                    const sim = d3.forceSimulation(nodes)
                        .force('link', d3.forceLink(links).id(d=>d.id).distance(72).strength(0.5))
                        .force('charge', d3.forceManyBody().strength(-280))
                        .force('center', d3.forceCenter(W/2, H/2))
                        .force('collide', d3.forceCollide().radius(d => 24 + Math.min(10,(deg[d.id]||0))))
                        .on('tick', () => {
                            link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
                            node.attr('transform', d=>'translate(' + d.x + ',' + d.y + ')');
                        });
                    _topoState = { svg, zoom, nodes, links, deg, hidden, W, H, sim };

                    node.call(d3.drag()
                        .on('start',(e,d)=>{ if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
                        .on('drag',(e,d)=>{ d.fx=e.x; d.fy=e.y; })
                        .on('end',(e,d)=>{ if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));

                    const tip = document.getElementById('topoTooltip');
                    node.on('mouseenter', (e,d) => {
                        const nb = _topoNeighbors(d.id, links); nb.add(d.id);
                        node.style('opacity', n => nb.has(n.id) ? 1 : 0.12);
                        link.style('stroke', l => (l.source.id===d.id||l.target.id===d.id) ? ((TOPO_CAT[d.cat]||{}).color || '#fff') : 'rgba(255,255,255,0.04)')
                            .style('stroke-width', l => (l.source.id===d.id||l.target.id===d.id) ? 2 : 1);
                        if (tip) {
                            const c = TOPO_CAT[d.cat]||{};
                            tip.innerHTML = '<div class="tt-cat" style="color:' + (c.color||'#fff') + '">' + (c.label||'') + '</div><b>' + d.id + '</b><br>' + (d.desc||'');
                            tip.classList.add('show');
                        }
                    }).on('mousemove', (e) => {
                        if (!tip) return;
                        const r = vp.getBoundingClientRect();
                        let x = e.clientX - r.left + 14, y = e.clientY - r.top + 14;
                        if (x + 280 > r.width) x -= 300;
                        tip.style.left = x + 'px'; tip.style.top = y + 'px';
                    }).on('mouseleave', () => {
                        node.style('opacity', 1); link.style('stroke', null).style('stroke-width', null);
                        if (tip) tip.classList.remove('show');
                    });

                    node.on('click', (e,d) => { e.stopPropagation(); _topoShowDetail(d, links); _topoFocus(d.id); });

                    _topoBuildLegend();
                    _topoApplyHidden();

                    sim.tick(140);
                    setTimeout(() => { focusId ? _topoFocus(focusId, true) : _topoFit(); }, 380);
                }

                function _topoFit() {
                    const st = _topoState; if (!st || !st.nodes.length) return;
                    const xs = st.nodes.map(n=>n.x), ys = st.nodes.map(n=>n.y);
                    const minX=Math.min.apply(null,xs), maxX=Math.max.apply(null,xs), minY=Math.min.apply(null,ys), maxY=Math.max.apply(null,ys);
                    const gw=(maxX-minX)||1, gh=(maxY-minY)||1;
                    const k = Math.min(1.6, 0.82*Math.min(st.W/gw, st.H/gh));
                    const tx = st.W/2 - k*(minX+maxX)/2, ty = st.H/2 - k*(minY+maxY)/2;
                    st.svg.transition().duration(500).call(st.zoom.transform, d3.zoomIdentity.translate(tx,ty).scale(k));
                }

                function _topoFocus(id, openDetail) {
                    const st = _topoState; if (!st) return;
                    const n = st.nodes.find(x=>x.id===id); if (!n) return;
                    const k = 1.35;
                    const tx = st.W/2 - k*n.x, ty = st.H/2 - k*n.y;
                    st.svg.transition().duration(500).call(st.zoom.transform, d3.zoomIdentity.translate(tx,ty).scale(k));
                    if (openDetail) _topoShowDetail(n, st.links);
                }

                function _topoShowDetail(d, links) {
                    const det = document.getElementById('topoDetail'); if (!det) return;
                    const c = TOPO_CAT[d.cat]||{};
                    const nbs = Array.from(_topoNeighbors(d.id, links)).sort();
                    const t = terminologyDB.find(x => x.term && x.term.toLowerCase() === d.id.toLowerCase());
                    const detailBtn = t ? '<button class="see-details-btn" onclick="window.masterSearch(\'' + t.term + '\')">Open in search <i class="fa-solid fa-arrow-right"></i></button>' : '';
                    det.innerHTML = '<button class="td-close" onclick="document.getElementById(\'topoDetail\').classList.remove(\'show\')"><i class="fa-solid fa-xmark"></i></button>'
                        + '<div class="td-cat" style="color:' + (c.color||'#fff') + '">' + (c.label||'') + '</div>'
                        + '<div class="td-title">' + d.id + '</div>'
                        + '<div class="td-desc">' + (d.desc||'') + '</div>'
                        + (nbs.length ? '<div class="td-conn"><b>Connects to:</b> ' + nbs.join(' · ') + '</div>' : '')
                        + detailBtn;
                    det.classList.add('show');
                }

                function _topoBuildLegend() {
                    const lg = document.getElementById('topoLegend'); if (!lg || !_topoState) return;
                    if (!_topoState.hidden) _topoState.hidden = new Set();
                    lg.innerHTML = '';
                    Object.keys(TOPO_CAT).forEach(cat => {
                        const c = TOPO_CAT[cat];
                        const el = document.createElement('div');
                        el.className = 'topo-legend-item' + (_topoState.hidden.has(cat)?' off':'');
                        el.innerHTML = '<span class="topo-legend-dot" style="background:' + c.color + '"></span>' + c.label;
                        el.onclick = () => { if(_topoState.hidden.has(cat)) _topoState.hidden.delete(cat); else _topoState.hidden.add(cat); el.classList.toggle('off'); _topoApplyHidden(); };
                        lg.appendChild(el);
                    });
                }

                function _topoApplyHidden() {
                    const st = _topoState; if (!st) return;
                    const hid = st.hidden || new Set();
                    st.svg.selectAll('.topo-node').style('display', d => hid.has(d.cat) ? 'none' : null);
                    st.svg.selectAll('.topo-link').style('display', l => (hid.has((l.source.cat)||'') || hid.has((l.target.cat)||'')) ? 'none' : null);
                }

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

                    // 2. Topology graph bindings
                    const topoSearch = document.getElementById('topoSearch');
                    if (topoSearch) {
                        topoSearch.addEventListener('keydown', (e) => {
                            if (e.key !== 'Enter') return;
                            const q = topoSearch.value.trim().toLowerCase();
                            if (!q || !_topoState) return;
                            const hit = _topoState.nodes.find(n => n.id.toLowerCase().includes(q));
                            if (hit) _topoFocus(hit.id, true);
                        });
                    }
                    const topoReset = document.getElementById('topoReset');
                    if (topoReset) topoReset.addEventListener('click', () => _topoFit());
                    const topoVp = document.getElementById('topoViewport');
                    if (topoVp) topoVp.addEventListener('click', (e) => {
                        if (e.target.id === 'topoViewport' || e.target.id === 'topoSvg') {
                            const det = document.getElementById('topoDetail'); if (det) det.classList.remove('show');
                        }
                    });
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

# Inject Jerry's portrait (if assets/jerry.{jpg,png,webp} exists) or fall back
# to a robot icon. Done after css_and_html is built so the data URI doesn't
# tangle with the raw string escaping above.
if JERRY_PORTRAIT_URI:
    _jerry_portrait_html = (
        f'<img src="{JERRY_PORTRAIT_URI}" alt="Jerry — Product Marketing Director">'
    )
else:
    _jerry_portrait_html = (
        '<div class="jerry-portrait-fallback"><i class="fa-solid fa-robot"></i></div>'
    )
css_and_html = css_and_html.replace("__JERRY_PORTRAIT_HTML__", _jerry_portrait_html)


# --- Per-user content assembly ----------------------------------------
# Some terminology rows are gated to a specific logged-in user (today:
# Emily, visible only to jhsun@streamax.com). The terminology DB is
# embedded as JSON inside the JS bundle, so gating has to happen at the
# moment we hand the HTML to Streamlit — not at module-import time.
#
# build_content(user_email) filters TERMINOLOGY_DB accordingly and
# substitutes the resulting JSON into the js_code template placeholder
# (__TERMINOLOGY_DB_JSON__). Falls back to the unfiltered list for any
# unknown caller.
JHSUN_EMAIL = "jhsun@streamax.com"


def _filtered_db_for(user_email: str) -> list:
    """Return TERMINOLOGY_DB filtered to entries the caller is allowed to see.

    Strips not only the gated rows themselves but also any back-references
    to those rows in other entries' `related` arrays — the bidirectional
    link resolver in terminology_db.py + streamaxpedia_app's auto-link
    step adds Emily into Jerry/Jack's related lists, and we don't want
    that name leaking into non-jhsun bundles either.
    """
    email_norm = (user_email or "").strip().lower()
    if email_norm == JHSUN_EMAIL:
        # JHSun sees everything, including Emily.
        return TERMINOLOGY_DB

    # Build the set of term names that should be hidden, then strip them
    # from every other entry's related list AND drop the rows themselves.
    hidden_terms = {
        row.get("term", "")
        for row in TERMINOLOGY_DB
        if row.get("jhsun_only")
    }
    out = []
    for row in TERMINOLOGY_DB:
        if row.get("jhsun_only"):
            continue
        if hidden_terms and row.get("related"):
            row = dict(row)  # don't mutate the shared module-level list
            row["related"] = [r for r in row["related"] if r not in hidden_terms]
        out.append(row)
    return out


def build_content(user_email: str = "") -> str:
    """Return the full Streamaxpedia HTML+JS bundle for a given user.

    The terminology DB is filtered per-user so jhsun-only rows (Emily and
    her Jack GPT shortcut) never reach non-jhsun browsers — not even as
    inert JSON. Matrix data and the static product list are user-agnostic
    and substituted at module-import time.
    """
    filtered = _filtered_db_for(user_email)
    js_filled = (
        js_code
        .replace("__TERMINOLOGY_DB_JSON__", json.dumps(filtered))
        .replace("__TOPOLOGY_JSON__", topology_json)
    )
    return css_and_html + js_filled


# Backwards-compat: any caller still doing `from streamaxpedia_app import
# content` gets the no-jhsun-extras default (safest for unknown callers).
content = build_content("")
