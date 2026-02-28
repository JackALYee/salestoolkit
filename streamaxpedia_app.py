import json
from terminology_db import TERMINOLOGY_DB

# Process Bidirectional Links Programmatically
for item in TERMINOLOGY_DB:
    if "related" in item:
        for related_term in item["related"]:
            target = next((t for t in TERMINOLOGY_DB if t["term"] == related_term), None)
            if target:
                if "related" not in target:
                    target["related"] = []
                if item["term"] not in target["related"]:
                    target["related"].append(item["term"])

db_json = json.dumps(TERMINOLOGY_DB)

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
                    /* height dynamically set by JS to cover full doc */
                    background: rgba(5, 8, 16, 0.85); 
                    backdrop-filter: blur(8px); 
                    z-index: 1000; 
                    opacity: 0; 
                    visibility: hidden; 
                    transition: opacity 0.3s ease-out, visibility 0.3s ease-out; 
                }
                .modal-overlay.active { opacity: 1; visibility: visible; }
                
                /* Modal Window Design with Resizing Enabled */
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
                    /* Notice we isolate transform and opacity so the JS 'top' positioning doesn't animate */
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
            </style>

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
                    <!-- Native instant search keystroke input -->
                    <input type="text" id="searchInput" class="search-input" placeholder="Search for ADAS, MDVR, APIs, metrics..." autocomplete="off">
                    <i class="fa-solid fa-magnifying-glass search-icon"></i>
                    <i class="fa-solid fa-xmark clear-icon" id="clearBtn"></i>
                </div>
            </div>

            <div class="stats" id="statsBar">Found <span id="resultCount">0</span> terms</div>
            <div class="results-container" id="resultsContainer">
                <!-- Results will be injected here via JavaScript instantly without reloading -->
            </div>

            <!-- RELEVANCE GRAPH MODAL -->
            <div class="modal-overlay" id="relevanceModal">
                <div class="modal-box">
                    <button class="close-modal" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
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

            <!-- SECURITY WARNING MODAL -->
            <div class="modal-overlay" id="securityModal">
                <div class="modal-box" style="width: 450px; height: auto; min-height: unset; padding: 30px; text-align: center; background: rgba(5, 8, 16, 0.98); border: 1px solid rgba(255, 71, 87, 0.3); box-shadow: 0 20px 60px rgba(0,0,0,0.8);">
                    <button class="close-modal" onclick="document.getElementById('securityModal').classList.remove('active')"><i class="fa-solid fa-xmark"></i></button>
                    <i class="fa-solid fa-shield-halved" style="font-size: 3.5rem; color: #ff4757; margin-bottom: 20px; filter: drop-shadow(0 0 15px rgba(255, 71, 87, 0.4));"></i>
                    <h3 style="color: var(--text-white); font-size: 1.3rem; margin-bottom: 15px;">Access Denied</h3>
                    <p style="color: var(--text-grey); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                        Due to Company IT Security Policy, downloading the selected document is prohibited.
                        <br><br>
                        根据公司网络安全法规，该文件的下载已被禁止。
                    </p>
                    <button class="see-details-btn" style="margin: 25px auto 0;" onclick="document.getElementById('securityModal').classList.remove('active')">Acknowledge / 确认</button>
                </div>
            </div>
"""

js_part_1 = r"""
            <script>
                const terminologyDB = 
"""

js_part_2 = r""";
                // ==========================================
                // MASTER SWITCH TO ENABLE/DISABLE DOWNLOADS
                // ==========================================
                const ENABLE_DOWNLOADS = false; // Change to true to enable "Spec" and "User Manual" downloads
                // ==========================================

                let currentMascotSrc = 'https://drive.google.com/thumbnail?id=1bXf5psHrw4LOk0oMAkTJRL15_mLCabad&sz=w500'; 
                let isGraphDragging = false, graphStartX = 0, graphStartY = 0, graphTranslateX = 0, graphTranslateY = 0, hasGraphDragged = false;

                const searchInput = document.getElementById('searchInput');
                const resultsContainer = document.getElementById('resultsContainer');
                const searchWrapper = document.getElementById('searchWrapper');
                const clearBtn = document.getElementById('clearBtn');
                const statsBar = document.getElementById('statsBar');
                const resultCount = document.getElementById('resultCount');

                function escapeRegExp(string) { return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
                
                function highlightText(text, query) {
                    if (!text) return '';
                    if (!query) return text;
                    const escapedQuery = escapeRegExp(query);
                    const regex = new RegExp(`(${escapedQuery})(?![^<]*>)`, 'gi');
                    return text.replace(regex, '<span class="highlight">$1</span>');
                }

                // --- SEARCH ENGINE LOGIC ---
                function performSearch() {
                    const rawQuery = searchInput.value.trim();
                    const query = rawQuery.toLowerCase();
                    
                    if (query.length > 0) {
                        searchWrapper.classList.add('active-search');
                        clearBtn.style.display = 'block';
                    } else {
                        searchWrapper.classList.remove('active-search');
                        clearBtn.style.display = 'none';
                        resultsContainer.innerHTML = '';
                        statsBar.classList.remove('show');
                        document.getElementById('mascotImage').src = currentMascotSrc;
                        document.getElementById('mascotImage').classList.remove('jumping-heart');
                        return;
                    }

                    const isExactMatch = terminologyDB.some(item => item.exact && item.term.toLowerCase() === rawQuery.toLowerCase());
                    const mascotImg = document.getElementById('mascotImage');
                    if (isExactMatch) {
                        mascotImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23ff3366"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';
                        mascotImg.classList.add('jumping-heart');
                    } else {
                        mascotImg.src = currentMascotSrc;
                        mascotImg.classList.remove('jumping-heart');
                    }

                    const scoredResults = terminologyDB.map(item => {
                        let score = 0;
                        if (item.exact) {
                            if (item.term.toLowerCase() === rawQuery.toLowerCase()) score += 1000;
                        } else {
                            const lowerTerm = item.term.toLowerCase();
                            const lowerDesc = item.desc.toLowerCase();
                            const lowerCat = item.category ? item.category.toLowerCase() : '';
                            if (lowerTerm === query) score += 1000;
                            else if (lowerTerm.includes(query)) score += 500;
                            if (item.related && item.related.some(r => r.toLowerCase() === query)) score += 400;
                            else if (item.related && item.related.some(r => r.toLowerCase().includes(query))) score += 300;
                            if (lowerCat === query) score += 50;
                            else if (lowerCat.includes(query)) score += 20;
                            if (lowerDesc.includes(query)) score += 10;
                        }
                        return { item, score };
                    }).filter(scoredItem => scoredItem.score > 0);

                    scoredResults.sort((a, b) => b.score - a.score);
                    const results = scoredResults.map(s => s.item);

                    statsBar.classList.add('show');
                    resultCount.textContent = results.length;

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
                        
                        // Check the MASTER SWITCH before building the download buttons
                        if (item.file) {
                            if (ENABLE_DOWNLOADS) {
                                downHTML += `<a href="${item.file}" target="_blank" class="download-btn"><i class="fa-solid fa-file-pdf"></i> Download DMS vs. DSC white paper</a>`;
                            } else {
                                downHTML += `<button onclick="showSecurityWarning(this)" class="download-btn"><i class="fa-solid fa-file-pdf"></i> Download DMS vs. DSC white paper</button>`;
                            }
                        }
                        
                        if (item.files) {
                            item.files.forEach(f => {
                                if (ENABLE_DOWNLOADS) {
                                    downHTML += `<a href="${f.url}" target="_blank" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${f.label}</a>`;
                                } else {
                                    downHTML += `<button onclick="showSecurityWarning(this)" class="download-btn"><i class="fa-solid fa-file-pdf"></i> ${f.label}</button>`;
                                }
                            });
                        }
                        
                        // FIX: Pass the clicked button ('this') so we can dynamically calculate Y position!
                        let relHTML = item.related ? `<div style="margin-top: 8px;"><button class="relevance-btn" onclick="openRelevanceGraph('${item.term}', this)"><i class="fa-solid fa-project-diagram"></i> Relevance</button></div>` : '';
                        
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

                // Live Keystroke listener instead of waiting for "Enter"
                searchInput.addEventListener('input', performSearch);
                
                clearBtn.addEventListener('click', () => {
                    searchInput.value = ''; searchInput.focus(); performSearch();
                });

                // Function to pop up the security warning modal
                window.showSecurityWarning = function(btnElement) {
                    const overlay = document.getElementById('securityModal');
                    const modalBox = overlay.querySelector('.modal-box');
                    
                    const docHeight = Math.max(
                        document.body.scrollHeight, document.documentElement.scrollHeight,
                        document.body.offsetHeight, document.documentElement.offsetHeight,
                        document.documentElement.clientHeight
                    );
                    overlay.style.height = docHeight + 'px';
                    
                    if (btnElement) {
                        const rect = btnElement.getBoundingClientRect();
                        const absoluteY = rect.top + window.scrollY; 
                        
                        let boxHeight = modalBox.offsetHeight || 300;
                        let boxTop = absoluteY - (boxHeight / 2) + (rect.height / 2); 
                        
                        if (boxTop < 20) boxTop = 20; 
                        if (boxTop + boxHeight + 20 > docHeight) boxTop = docHeight - boxHeight - 20;
                        
                        modalBox.style.top = boxTop + 'px';
                    } else {
                        modalBox.style.top = (window.scrollY + 100) + 'px';
                    }
                    
                    overlay.classList.add('active');
                };

                // --- FIXED: GET CENTER ANIMATION SAFE ---
                // Navigates the DOM hierarchy to find the exact relative center of a node without relying on the animated bounding box.
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

                // --- GRAPH LOGIC ---
                window.openRelevanceGraph = function(termName, btnElement) {
                    const termData = terminologyDB.find(t => t.term === termName);
                    if (!termData || !termData.related) return;

                    const overlay = document.getElementById('relevanceModal');
                    const modalBox = overlay.querySelector('.modal-box');
                    
                    // Match the overlay height to the full document height dynamically
                    const docHeight = Math.max(
                        document.body.scrollHeight, document.documentElement.scrollHeight,
                        document.body.offsetHeight, document.documentElement.offsetHeight,
                        document.documentElement.clientHeight
                    );
                    overlay.style.height = docHeight + 'px';
                    
                    // FIX: Dynamically anchor the modal perfectly to where the user scrolled/clicked!
                    if (btnElement) {
                        const rect = btnElement.getBoundingClientRect();
                        // Get absolute Y position in the document
                        const absoluteY = rect.top + window.scrollY; 
                        
                        // Center the modal over the button (Modal defaults to ~600px tall)
                        let boxHeight = modalBox.offsetHeight || 600;
                        let boxTop = absoluteY - (boxHeight / 2) + (rect.height / 2); 
                        
                        // Boundaries
                        if (boxTop < 20) boxTop = 20; 
                        if (boxTop + boxHeight + 20 > docHeight) boxTop = docHeight - boxHeight - 20;
                        
                        modalBox.style.top = boxTop + 'px';
                    } else {
                        modalBox.style.top = (window.scrollY + 100) + 'px';
                    }

                    document.getElementById('modalChildExplanation').classList.remove('active');
                    document.getElementById('graphMasterNode').innerText = termData.term;

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

                    clusters.forEach(c => c.sort((a,b) => (terminologyDB.find(t=>t.term===a)?.category||'').localeCompare((terminologyDB.find(t=>t.term===b)?.category||''))));
                    clusters.sort((a,b) => (terminologyDB.find(t=>t.term===a[0])?.category||'').localeCompare((terminologyDB.find(t=>t.term===b[0])?.category||'')));

                    const grouped = clusters.flat();
                    const relatedNodesContainer = document.getElementById('graphRelatedNodes');
                    relatedNodesContainer.innerHTML = '';

                    grouped.forEach(rTerm => {
                        const n = document.createElement('div');
                        n.className = 'round-node node-related';
                        if (!dist1.includes(rTerm)) n.classList.add('node-dist2');
                        n.innerText = rTerm; n.dataset.term = rTerm;
                        n.onclick = (e) => { if (hasGraphDragged) return; showChildTerm(rTerm); };
                        relatedNodesContainer.appendChild(n);
                    });

                    overlay.classList.add('active');

                    // FIX: Calculate Auto-Pan using offset geometry to ignore CSS scale animations
                    setTimeout(() => {
                        const vp = document.getElementById('graphViewport');
                        const ct = document.getElementById('graphContainer');
                        const mn = document.getElementById('graphMasterNode');
                        
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

                // FIX: drawLines completely bypasses getBoundingClientRect for animation immunity
                function drawLines() {
                    const svg = document.getElementById('graphLines');
                    svg.innerHTML = '';
                    
                    const mNode = document.getElementById('graphMasterNode');
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
                    b.innerHTML = `<div style="font-weight:700; color:#2AF598; margin-bottom:5px; font-size: 1.1rem;">${d.term}</div><div style="font-size:0.95rem; color:#A0AEC0;">${d.desc}</div><button class="see-details-btn" onclick="masterSearch('${d.term}')">See Details <i class="fa-solid fa-arrow-right"></i></button>`;
                    b.classList.add('active');
                };

                window.closeModal = function() { document.getElementById('relevanceModal').classList.remove('active'); };
                
                // --- COMPLETELY FIXED "SEE DETAILS" LOGIC ---
                // Instead of reloading the parent URL and breaking the Streamlit iframe,
                // it seamlessly updates the internal text box and live searches instantly!
                window.masterSearch = function(name) {
                    closeModal();
                    const searchInput = document.getElementById('searchInput');
                    searchInput.value = name;
                    performSearch();
                    
                    // Native smooth scroll back to the search bar!
                    document.getElementById('searchWrapper').scrollIntoView({ behavior: 'smooth', block: 'start' });
                };

                // Mascot mouse tracking
                document.addEventListener('mousemove', (e) => {
                    const mascotImg = document.getElementById('mascotImage');
                    if (!mascotImg || mascotImg.classList.contains('jumping-heart')) return;
                    const x = (e.clientX / window.innerWidth - 0.5) * 40; 
                    const y = (e.clientY / window.innerHeight - 0.5) * -40; 
                    const translateX = (e.clientX / window.innerWidth - 0.5) * 15;
                    mascotImg.style.transform = `rotateY(${x}deg) rotateX(${y}deg) translateX(${translateX}px)`;
                });

                // Pan Logic
                const vp = document.getElementById('graphViewport');
                const ct = document.getElementById('graphContainer');
                if (vp) {
                    vp.onmousedown = (e) => { isGraphDragging = true; hasGraphDragged = false; graphStartX = e.clientX - graphTranslateX; graphStartY = e.clientY - graphTranslateY; };
                    window.addEventListener('mousemove', (e) => { if(isGraphDragging) { if(Math.abs(e.clientX - graphStartX - graphTranslateX)>3 || Math.abs(e.clientY - graphStartY - graphTranslateY)>3) hasGraphDragged = true; graphTranslateX = e.clientX - graphStartX; graphTranslateY = e.clientY - graphStartY; ct.style.transform = `translate(${graphTranslateX}px, ${graphTranslateY}px)`; } });
                    window.addEventListener('mouseup', () => isGraphDragging = false);
                    vp.onclick = (e) => { if(!hasGraphDragged && !e.target.closest('.node-related') && !document.getElementById('modalChildExplanation').contains(e.target)) document.getElementById('modalChildExplanation').classList.remove('active'); };
                }

                // Observe modal resize to redraw lines dynamically
                if (typeof ResizeObserver !== 'undefined') {
                    const modalBox = document.querySelector('.modal-box');
                    if (modalBox) {
                        new ResizeObserver(() => {
                            if (document.getElementById('relevanceModal').classList.contains('active')) {
                                drawLines();
                            }
                        }).observe(modalBox);
                    }
                }
            </script>
        </div>
"""

# Stitch everything together into a variable that app.py imports
content = css_and_html + js_part_1 + db_json + js_part_2
