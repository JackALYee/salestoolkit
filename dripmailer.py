content = r"""
        <!-- SECTION: DRIP MAILER -->
        <div id="dripmailer" class="content-section hidden">
            <div class="card fade-up">
                <h2 class="gradient-text">Drip Mailer Tool</h2>
                <p>Build your signature, draft dynamic templates, and batch send emails directly from your Streamax account securely via the Python backend.</p>
            </div>

            <div class="sub-nav-tabs fade-up">
                <button class="sub-nav-btn active" onclick="switchSubTab('drip-sig', this)">
                    <i data-lucide="pen-tool"></i> 1. Signatures
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('drip-compose', this)">
                    <i data-lucide="edit-3"></i> 2. Compose
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('drip-send', this)">
                    <i data-lucide="send"></i> 3. Data & Send
                </button>
            </div>

            <!-- TAB 1: Signatures -->
            <div id="drip-sig" class="sub-content active">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 fade-up">
                    <div class="md:col-span-1 glass-panel p-5 space-y-4 rounded-xl border border-white/10 bg-black/20">
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Full Name</label>
                            <input type="text" id="sig_name" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="Jack Yi" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Job Title</label>
                            <input type="text" id="sig_title" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="Sales Director" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Company Name</label>
                            <input type="text" id="sig_company" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="Streamax Technology" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Phone</label>
                            <input type="text" id="sig_phone" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="(555) 123-4567" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Website</label>
                            <input type="text" id="sig_website" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="https://www.streamax.com" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Avatar URL</label>
                            <input type="text" id="sig_avatar" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="https://images.unsplash.com/photo-1531831108325-7fe9616bc780?auto=format&fit=crop&w=100&q=80" oninput="updateSignature()">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-400 mb-1">Logo URL</label>
                            <input type="text" id="sig_logo" class="w-full rounded bg-black/40 border border-white/10 px-3 py-2 text-white text-sm focus:border-[var(--primary-green)] outline-none" value="https://mail.streamax.com/coremail/s?func=lp:getImg&org_id=&img_id=logo_001" oninput="updateSignature()">
                        </div>
                        <div class="text-xs text-gray-500 mt-4 border-t border-white/10 pt-3">
                            Authenticated Sender: <strong class="text-[var(--primary-green)]">__USER_EMAIL__</strong>
                        </div>
                    </div>
                    
                    <div class="md:col-span-2 space-y-4">
                        <div class="glass-panel p-4 flex flex-wrap gap-4 rounded-xl border border-white/10 bg-black/20">
                            <label class="flex items-center text-sm text-gray-300 cursor-pointer hover:text-white transition">
                                <input type="radio" name="sig_layout" value="Minimalist Professional" onchange="updateSignature()" class="mr-2 accent-[var(--primary-green)]"> Minimalist Professional
                            </label>
                            <label class="flex items-center text-sm text-gray-300 cursor-pointer hover:text-white transition">
                                <input type="radio" name="sig_layout" value="Creative with Avatar" onchange="updateSignature()" checked class="mr-2 accent-[var(--primary-green)]"> Creative with Avatar
                            </label>
                            <label class="flex items-center text-sm text-gray-300 cursor-pointer hover:text-white transition">
                                <input type="radio" name="sig_layout" value="Corporate with Logo" onchange="updateSignature()" class="mr-2 accent-[var(--primary-green)]"> Corporate with Logo
                            </label>
                        </div>
                        <div id="sig_preview_box" class="bg-white p-8 rounded-xl border border-gray-300 shadow-xl text-black overflow-x-auto min-h-[250px]">
                            <!-- Signature HTML injected here -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: Compose -->
            <div id="drip-compose" class="sub-content">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 fade-up">
                    <div class="space-y-5">
                        <div class="glass-panel p-4 text-sm text-gray-300 rounded-xl border border-white/10 bg-black/20">
                            <strong>💡 Variables:</strong> Use <code class="text-[var(--primary-green)] font-bold">{first_name}</code>, <code class="text-[var(--primary-green)] font-bold">{last_name}</code>, <code class="text-[var(--primary-green)] font-bold">{company}</code>, <code class="text-[var(--primary-green)] font-bold">{role}</code> from your CSV, and <code class="text-[var(--primary-green)] font-bold">{your_name}</code> from your signature.
                        </div>
                        <div>
                            <label class="block text-sm text-gray-400 mb-2">Subject Line</label>
                            <input type="text" id="email_subject" class="w-full rounded-lg bg-black/40 border border-white/10 px-4 py-3 text-white focus:border-[var(--primary-green)] outline-none transition" value="Streamlining Operations at {company}" oninput="updateEmailPreview()">
                        </div>
                        <div>
                            <label class="block text-sm text-gray-400 mb-2">Email Body</label>
                            <textarea id="email_body" class="w-full rounded-lg bg-black/40 border border-white/10 px-4 py-3 text-white h-[350px] font-sans focus:border-[var(--primary-green)] outline-none transition" oninput="updateEmailPreview()">Hi {first_name},

I hope this email finds you well. I noticed that {company} is doing some incredible work lately.

As someone working as a {role}, I thought you might be interested in how our new tools can help streamline your daily operations. We've helped similar teams increase their efficiency by over 20%.

Would you be open to a brief 10-minute chat next week?

Best regards,</textarea>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-2">Live HTML Preview (Sample Data)</label>
                        <div class="bg-white p-8 rounded-xl border border-gray-300 shadow-xl text-black h-[530px] overflow-y-auto">
                            <div class="border-b border-gray-200 pb-3 mb-5">
                                <span class="text-xs text-gray-500 font-bold uppercase tracking-wider">Subject:</span>
                                <span id="preview_subject" class="ml-2 font-bold text-gray-900 text-lg"></span>
                            </div>
                            <div id="preview_body" class="text-[15px] text-gray-800 whitespace-pre-wrap leading-relaxed font-sans"></div>
                            <div id="preview_signature" class="mt-8 pt-4 border-t border-gray-100"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 3: Data & Send -->
            <div id="drip-send" class="sub-content">
                <div class="fade-up space-y-6">
                    <div class="glass-panel p-6 rounded-xl border border-white/10 bg-black/20">
                        <h4 class="text-[var(--primary-green)] mb-2 font-bold text-lg"><i class="fa-solid fa-file-csv mr-2"></i> Lead List Template</h4>
                        <p class="text-sm text-gray-400 mb-5">Ensure your contacts are formatted correctly. Required columns: Email, First_Name, Last_Name, Company, Role.</p>
                        
                        <div class="overflow-x-auto mb-5 rounded border border-white/10">
                            <table class="w-full text-sm text-left text-gray-300 border-collapse">
                                <thead class="text-xs text-white uppercase bg-white/5 border-b border-white/10">
                                    <tr>
                                        <th class="px-4 py-3">Email</th>
                                        <th class="px-4 py-3">First_Name</th>
                                        <th class="px-4 py-3">Last_Name</th>
                                        <th class="px-4 py-3">Company</th>
                                        <th class="px-4 py-3">Role</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="bg-black/20 hover:bg-white/5 transition">
                                        <td class="px-4 py-3 border-t border-white/5">example@streamax.com</td>
                                        <td class="px-4 py-3 border-t border-white/5">John</td>
                                        <td class="px-4 py-3 border-t border-white/5">Doe</td>
                                        <td class="px-4 py-3 border-t border-white/5">Streamax</td>
                                        <td class="px-4 py-3 border-t border-white/5">Sales Manager</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <a href="data:text/csv;charset=utf-8,Email,First_Name,Last_Name,Company,Role%0Aexample@streamax.com,John,Doe,Streamax,Sales Manager" download="leadList.csv" class="inline-flex items-center justify-center bg-white/5 hover:bg-white/10 text-white text-sm font-semibold py-2.5 px-5 rounded-lg transition-colors border border-white/20">
                            <i class="fa-solid fa-download mr-2"></i> Download CSV Template
                        </a>
                    </div>

                    <div class="glass-panel p-6 rounded-xl border border-white/10 bg-black/20">
                        <label class="block font-bold text-white mb-4 text-lg"><i class="fa-solid fa-upload mr-2 text-[var(--secondary-blue)]"></i> Upload your completed leadList.csv</label>
                        
                        <input type="file" id="csv_upload" accept=".csv" class="block w-full text-sm text-gray-400 file:mr-4 file:py-2.5 file:px-5 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[var(--secondary-blue)] file:text-white hover:file:opacity-90 mb-6 cursor-pointer">
                        
                        <div id="csv_preview_container" class="hidden overflow-x-auto mb-6 rounded border border-white/10 max-h-[300px] overflow-y-auto">
                            <table class="w-full text-sm text-left text-gray-300 border-collapse" id="csv_preview_table">
                                <!-- Populated by JS -->
                            </table>
                        </div>

                        <!-- Warnings and Actions -->
                        <div id="auth_warning" class="hidden bg-orange-500/10 border border-orange-500/30 text-orange-300 p-4 rounded-lg text-sm mb-6 flex items-center">
                            <i class="fa-solid fa-triangle-exclamation text-xl mr-3"></i>
                            <div>You are in <strong>__AUTH_MODE__ Override Mode</strong>. Real SMTP email sending functionality is disabled.</div>
                        </div>

                        <button id="btn_send" class="w-full bg-gradient-to-r from-[var(--primary-green)] to-[var(--secondary-blue)] text-[#050810] font-bold py-4 rounded-xl shadow-[0_4px_20px_rgba(42,245,152,0.3)] hover:scale-[1.01] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 text-lg uppercase tracking-wide" onclick="startBatchSend()">
                            🚀 Initiate Batch Send
                        </button>

                        <div id="send_progress_container" class="hidden mt-8 space-y-4">
                            <div class="w-full bg-black/50 rounded-full h-4 border border-white/10 overflow-hidden">
                                <div id="send_progress_bar" class="bg-gradient-to-r from-[var(--primary-green)] to-[var(--secondary-blue)] h-full rounded-full transition-all duration-300 relative" style="width: 100%">
                                    <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
                                </div>
                            </div>
                            <div class="bg-black/60 border border-white/10 rounded-lg p-4 h-32 overflow-y-auto font-mono text-sm text-[var(--primary-green)] whitespace-pre-wrap shadow-inner" id="send_logs">Transmitting data to secure Python backend... Check Streamlit notification bar above!</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // --- DRIP MAILER JS LOGIC ---
                const authMode = "__AUTH_MODE__";
                const userEmail = "__USER_EMAIL__";
                let currentCsvData = [];
                let isSending = false;

                const disclaimerHtml = `<div style="margin: 25px 0 0 0; padding: 15px 0 0 0; border-top: 1px solid #e2e8f0; font-family: Arial, sans-serif; font-size: 10px; color: #64748b; line-height: 1.4; text-align: left;">This e-mail is intended only for the person or entity to which it is addressed and may contain confidential and/or privileged material. Any review, retransmission, dissemination or other use of, or taking of any action in reliance upon, the information in this e-mail by persons or entities other than the intended recipient is prohibited and may be unlawful. If you received this e-mail in error, please contact the sender and delete it from any computer.</div>`;

                function getSignatureHtml() {
                    const name = document.getElementById('sig_name').value;
                    const title = document.getElementById('sig_title').value;
                    const company = document.getElementById('sig_company').value;
                    const phone = document.getElementById('sig_phone').value;
                    const website = document.getElementById('sig_website').value;
                    const avatar = document.getElementById('sig_avatar').value;
                    const logo = document.getElementById('sig_logo').value;
                    const layout = document.querySelector('input[name="sig_layout"]:checked').value;
                    
                    let html = '';
                    if (layout === "Minimalist Professional") {
                        html = `<div style="font-family: Arial, sans-serif; color: #333; margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px;"><p style="margin: 0; font-weight: bold; font-size: 14px; color: #000000;">${name}</p><p style="margin: 0; font-size: 12px; color: #666;">${title} | <a href="${website}" style="color: #666; text-decoration: none;">${company}</a></p><p style="margin: 0; font-size: 12px; color: #B2CC40;">${userEmail} | ${phone}</p></div>`;
                    } else if (layout === "Creative with Avatar") {
                        html = `<div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin-top: 20px; display: flex; align-items: center; gap: 15px;"><img src="${avatar}" alt="Avatar" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #e2e8f0;" /><div><p style="margin: 0; font-weight: 600; font-size: 15px; color: #1e293b;">${name}</p><p style="margin: 2px 0; font-size: 13px; color: #64748b;">${title}</p><p style="margin: 2px 0; font-size: 13px; color: #B2CC40;">${userEmail} <span style="color: #94a3b8;">|</span> <span style="color: #64748b;">${phone}</span></p><a href="${website}" style="margin: 0; font-size: 13px; color: #B2CC40; text-decoration: none;">${company}</a></div></div>`;
                    } else {
                        html = `<div style="font-family: Arial, sans-serif; margin-top: 25px;"><p style="margin: 0; font-weight: bold; font-size: 14px; color: #0f172a;">${name}</p><p style="margin: 2px 0 5px 0; font-size: 12px; color: #475569;">${title}</p><p style="margin: 0; font-size: 12px; color: #B2CC40;"><strong><a href="${website}" style="color: #B2CC40; text-decoration: none;">${company}</a></strong></p><p style="margin: 4px 0 12px 0; font-size: 12px; color: #475569;"><a href="mailto:${userEmail}" style="color: #B2CC40; text-decoration: none;">${userEmail}</a> | ${phone}</p><img src="${logo}" alt="Company Logo" style="height: 45px; border-radius: 4px;" /></div>`;
                    }
                    return html + disclaimerHtml;
                }

                function updateSignature() {
                    const html = getSignatureHtml();
                    const box = document.getElementById('sig_preview_box');
                    if(box) box.innerHTML = html;
                    updateEmailPreview();
                }

                function renderTemplate(templateStr, data) {
                    return templateStr.replace(/\{([^}]+)\}/g, (match, key) => {
                        const val = data[key.toLowerCase().trim()];
                        return val !== undefined ? val : match;
                    });
                }

                function updateEmailPreview() {
                    const subj = document.getElementById('email_subject').value;
                    const body = document.getElementById('email_body').value;
                    const sigHtml = getSignatureHtml();
                    
                    const sampleData = {
                        first_name: "John",
                        last_name: "Doe",
                        company: "Acme Corp",
                        role: "Manager",
                        your_name: document.getElementById('sig_name').value
                    };
                    
                    const renderedSubj = renderTemplate(subj, sampleData);
                    const renderedBody = renderTemplate(body, sampleData);
                    
                    const elSubj = document.getElementById('preview_subject');
                    const elBody = document.getElementById('preview_body');
                    const elSig = document.getElementById('preview_signature');
                    
                    if(elSubj) elSubj.innerText = renderedSubj;
                    if(elBody) elBody.innerText = renderedBody;
                    if(elSig) elSig.innerHTML = sigHtml;
                }

                // File Upload Logic
                document.addEventListener('DOMContentLoaded', () => {
                    updateSignature();
                    
                    if (authMode !== "Success") {
                        const warn = document.getElementById('auth_warning');
                        const btn = document.getElementById('btn_send');
                        if (warn) warn.classList.remove('hidden');
                        if (btn) btn.disabled = true;
                    }
                    
                    const fileInput = document.getElementById('csv_upload');
                    if (fileInput) {
                        fileInput.addEventListener('change', function(e) {
                            const file = e.target.files[0];
                            if (!file) return;
                            
                            const reader = new FileReader();
                            reader.onload = function(e) {
                                const text = e.target.result;
                                parseCsv(text);
                            };
                            reader.readAsText(file);
                        });
                    }
                });

                function parseCsv(csvText) {
                    const lines = csvText.split('\n').filter(l => l.trim() !== '');
                    if(lines.length < 2) return;
                    
                    const headers = lines[0].split(',').map(h => h.toLowerCase().trim());
                    const required = ['first_name', 'last_name', 'email', 'role', 'company'];
                    
                    let missing = required.filter(r => !headers.includes(r));
                    if(missing.length > 0) {
                        alert("Missing required columns: " + missing.join(', '));
                        return;
                    }
                    
                    const data = [];
                    for(let i=1; i<lines.length; i++) {
                        const cols = lines[i].split(',').map(c => c.trim());
                        const row = {};
                        headers.forEach((h, idx) => {
                            row[h] = cols[idx] || '';
                        });
                        data.push(row);
                    }
                    currentCsvData = data;
                    renderCsvPreview(headers, data.slice(0, 10)); // Show top 10
                }

                function renderCsvPreview(headers, rows) {
                    const container = document.getElementById('csv_preview_container');
                    const table = document.getElementById('csv_preview_table');
                    
                    let thead = '<thead class="text-xs text-white uppercase bg-white/5 sticky top-0"><tr>';
                    headers.forEach(h => thead += `<th class="px-4 py-3 border-b border-white/10">${h}</th>`);
                    thead += '</tr></thead>';
                    
                    let tbody = '<tbody>';
                    rows.forEach(row => {
                        tbody += '<tr class="bg-black/20 hover:bg-white/5 transition">';
                        headers.forEach(h => {
                            tbody += `<td class="px-4 py-2 border-b border-white/5 truncate max-w-[150px]">${row[h]}</td>`;
                        });
                        tbody += '</tr>';
                    });
                    tbody += '</tbody>';
                    
                    table.innerHTML = thead + tbody;
                    container.classList.remove('hidden');
                }

                function startBatchSend() {
                    if(isSending) return;
                    if(currentCsvData.length === 0) {
                        alert("Please upload a valid CSV first.");
                        return;
                    }
                    
                    isSending = true;
                    document.getElementById('btn_send').disabled = true;
                    document.getElementById('btn_send').innerText = "Processing via Secure Python Backend...";
                    
                    const container = document.getElementById('send_progress_container');
                    
                    container.classList.remove('hidden');
                    
                    // Bundle all UI inputs into a payload for Python
                    const payload = {
                        action: "send_batch",
                        csvData: currentCsvData,
                        subjectTemplate: document.getElementById('email_subject').value,
                        bodyTemplate: document.getElementById('email_body').value,
                        sigHtml: getSignatureHtml(),
                        sigName: document.getElementById('sig_name').value
                    };
                    
                    // Fire the payload across the bridge to app.py!
                    Streamlit.setComponentValue(payload);
                    
                    // Re-enable button after a short delay so users can send again if needed
                    setTimeout(() => {
                        isSending = false;
                        document.getElementById('btn_send').disabled = false;
                        document.getElementById('btn_send').innerText = "🚀 Initiate Batch Send";
                        container.classList.add('hidden');
                    }, 8000);
                }
            </script>
        </div>
"""
