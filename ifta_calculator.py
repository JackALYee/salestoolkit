content = r"""        </div> <!-- FIX: Close previous tco-calc section -->
        
        <!-- TCO IFTA CALCULATOR SUB-SECTION -->
        <div id="ifta-calc" class="sub-content">
            <div class="max-w-6xl w-full mx-auto glass-card overflow-visible fade-up delay-1">
                <!-- Header -->
                <div class="p-8 md:p-12 text-center border-b border-white/10 relative overflow-hidden rounded-t-2xl">
                    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-full bg-gradient-to-b from-[#009EFD]/10 to-transparent blur-3xl -z-10"></div>
                    
                    <h1 class="text-3xl md:text-5xl font-bold mb-4 tracking-tight">
                        Streamax <span class="text-gradient">IFTA</span> Optimizer
                    </h1>
                    <p class="text-[var(--text-grey)] text-base md:text-lg max-w-3xl mx-auto font-light leading-relaxed">
                        Calculate your International Fuel Tax Agreement (IFTA) liability across multiple jurisdictions. Discover your true net fuel cost and find out exactly which state is the most cost-effective for refueling.
                    </p>
                </div>
        
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-0 relative">
                    <!-- Decorative center line -->
                    <div class="hidden lg:block absolute left-[66.666%] top-10 bottom-10 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent -translate-x-1/2"></div>
        
                    <!-- Input Section (Left 2 Columns) -->
                    <div class="lg:col-span-2 p-8 md:p-10 border-b lg:border-b-0 lg:border-r border-white/10 fade-up delay-2">
                        <div class="flex justify-between items-center mb-6">
                            <h2 class="text-xl font-semibold flex items-center text-white m-0">
                                <i class="fas fa-map-marked-alt text-[var(--secondary-blue)] mr-3"></i> Route Data
                            </h2>
                            <div class="flex items-center gap-3">
                                <label class="text-sm font-medium text-[var(--text-grey)]">Avg Fleet MPG:</label>
                                <input type="number" id="ifta-mpg" value="5.95" min="0.1" step="0.01" class="w-24 rounded-lg py-1.5 px-3 text-center" oninput="calculateIFTA()">
                            </div>
                        </div>
                        
                        <!-- State Rows Container -->
                        <div id="ifta-states-container" class="space-y-3 mb-6">
                            <!-- Rows injected by JS on load -->
                        </div>

                        <button type="button" onclick="addIftaStateRow()" class="nav-btn w-full justify-center mt-4 border border-dashed border-white/20 hover:border-[var(--secondary-blue)] hover:text-[var(--secondary-blue)]">
                            <i class="fa-solid fa-plus"></i> Add Jurisdiction
                        </button>
                    </div>
        
                    <!-- Output Section (Right 1 Column) -->
                    <div class="p-8 md:p-10 flex flex-col justify-start rounded-b-2xl lg:rounded-bl-none lg:rounded-br-2xl fade-up delay-3 relative">
                        <h2 class="text-xl font-semibold mb-6 flex items-center text-white">
                            <i class="fas fa-file-invoice-dollar text-[var(--primary-green)] mr-3"></i> Reconciliation
                        </h2>
        
                        <div class="space-y-4 mb-6">
                            <div class="flex justify-between items-center p-3 border-b border-white/10">
                                <span class="text-sm font-medium text-gray-400">Cost at Pump</span>
                                <span class="text-lg font-bold text-white" id="ifta-out-pump">$0</span>
                            </div>
                            <div class="flex justify-between items-center p-3 border-b border-white/10">
                                <span class="text-sm font-medium text-gray-400">Total Tax Owed <span class="text-xs font-normal opacity-70">(Usage)</span></span>
                                <span class="text-lg font-bold text-white" id="ifta-out-owed">$0</span>
                            </div>
                            <div class="flex justify-between items-center p-3 border-b border-white/10">
                                <span class="text-sm font-medium text-gray-400">Total Tax Paid <span class="text-xs font-normal opacity-70">(Purchased)</span></span>
                                <span class="text-lg font-bold text-white" id="ifta-out-paid">$0</span>
                            </div>
                            
                            <div class="flex justify-between items-center p-4 mt-2 rounded-xl bg-white/5 border border-white/10">
                                <span class="text-sm font-medium text-gray-300">Net IFTA Balance</span>
                                <span class="text-xl font-bold" id="ifta-out-balance">$0</span>
                            </div>
        
                            <div class="pt-4 mt-4 border-t border-[var(--primary-green)]/30">
                                <div class="flex flex-col gap-1">
                                    <span class="text-xs font-medium text-[var(--primary-green)] uppercase tracking-wider">True Net Cost (Post-IFTA)</span>
                                    <span class="text-4xl font-extrabold text-gradient drop-shadow-[0_0_15px_rgba(42,245,152,0.3)]" id="ifta-out-net">$0</span>
                                </div>
                            </div>
                        </div>

                        <!-- Optimization Insight -->
                        <div class="mt-auto glass-panel p-5 relative overflow-hidden border border-[var(--secondary-blue)]/40 shadow-[0_0_15px_rgba(0,158,253,0.1)]">
                            <div class="absolute top-0 left-0 w-1 h-full bg-[var(--secondary-blue)]"></div>
                            <h3 class="text-[var(--text-white)] font-semibold mb-2 text-sm flex items-center">
                                <i class="fas fa-lightbulb mr-2 text-[var(--secondary-blue)]"></i> AI Optimization Insight
                            </h3>
                            <p id="ifta-opt-insight" class="text-sm text-gray-300 leading-relaxed m-0">
                                Add state data to generate routing insights.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Interactive Formula Display (MathJax LaTeX) -->
                <div class="border-t border-white/10 p-8 md:p-10 fade-up delay-4">
                    <h3 class="text-gray-300 font-semibold mb-6 text-sm flex items-center justify-center">
                        <i class="fas fa-square-root-alt mr-2 text-[var(--primary-green)]"></i> Cost Logic & Mathematical Proof
                    </h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 text-[0.85rem] text-gray-400">
                        <div class="glass-panel p-5 space-y-3">
                            <h4 class="text-[var(--secondary-blue)] mb-2 uppercase text-xs tracking-wider">Base Formulas</h4>
                            <div>$C_{\text{fuel}} = \sum_{k=1}^{m} P_{\text{pump}}^{(k)} \cdot g_{\text{fuel}}^{(k)}$</div>
                            <div class="text-xs opacity-70 mb-3">Total pump cost across $m$ fueling stops.</div>
                            
                            <div>$T_{\text{owed}} = \sum_{j=1}^{n} r^{(j)} \cdot g^{(j)}$</div>
                            <div class="text-xs opacity-70 mb-3">Total tax owed based on gallons consumed ($g$) per jurisdiction $j$.</div>

                            <div>$T_{\text{credit}} = \sum_{k=1}^{m} r^{(k)} \cdot g_{\text{fuel}}^{(k)}$</div>
                            <div class="text-xs opacity-70">Total tax credited from purchases at the pump.</div>
                        </div>
                        <div class="glass-panel p-5 space-y-3">
                            <h4 class="text-[var(--secondary-blue)] mb-2 uppercase text-xs tracking-wider">Optimization Proof</h4>
                            <div>$T_{\text{net}} = T_{\text{owed}} - T_{\text{credit}}$</div>
                            <div class="text-xs opacity-70 mb-3">Net tax liability (positive) or refund (negative).</div>

                            <div>$C_{\text{net}} = C_{\text{fuel}} + T_{\text{net}}$</div>
                            <div class="text-xs opacity-70 mb-3">Recalculated True Net Cost.</div>

                            <div class="border-t border-white/10 pt-3 mt-3">
                                $\arg\min_i \left( P_{\text{pump}}^{(i)} - r^{(i)} \right)$
                            </div>
                            <div class="text-xs opacity-70"><strong>The Theorem:</strong> To minimize total net cost, purchase fuel in the jurisdiction with the lowest pre-tax base price, not necessarily the lowest pump price.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- IFTA Calculator Specific Scripts -->
        <script>
            // Sample Data (CA to IL example from doc)
            const initialIftaData = [
                { state: 'CA', miles: 3000, price: 4.49, rate: 1.023, bought: 6050.42 },
                { state: 'AZ', miles: 7500, price: 3.20, rate: 0.180, bought: 0 },
                { state: 'NM', miles: 10000, price: 2.90, rate: 0.210, bought: 0 },
                { state: 'OK', miles: 10000, price: 3.14, rate: 0.200, bought: 0 },
                { state: 'IL', miles: 5500, price: 3.14, rate: 0.736, bought: 0 }
            ];

            function addIftaStateRow(data = {state: '', miles: 0, price: 0, rate: 0, bought: 0}) {
                const container = document.getElementById('ifta-states-container');
                const row = document.createElement('div');
                row.className = 'ifta-state-row glass-panel p-3 flex flex-wrap md:flex-nowrap items-center gap-2 relative';
                
                row.innerHTML = `
                    <div class="flex-1 min-w-[80px]">
                        <label class="block text-[10px] text-gray-500 uppercase mb-1">State</label>
                        <input type="text" class="state-name w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white" value="${data.state}" placeholder="e.g. CA" oninput="calculateIFTA()">
                    </div>
                    <div class="flex-1 min-w-[80px]">
                        <label class="block text-[10px] text-gray-500 uppercase mb-1">Miles Driven</label>
                        <input type="number" class="state-miles w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white" value="${data.miles}" step="1" oninput="calculateIFTA()">
                    </div>
                    <div class="flex-1 min-w-[80px]">
                        <label class="block text-[10px] text-gray-500 uppercase mb-1">Pump $</label>
                        <input type="number" class="state-price w-full bg-black/40 border border-white/10 rounded px-2 py-1.5 text-sm text-white" value="${data.price}" step="0.01" oninput="calculateIFTA()">
                    </div>
                    <div class="flex-1 min-w-[80px]">
                        <label class="block text-[10px] text-[var(--primary-green)] uppercase mb-1">IFTA Rate</label>
                        <input type="number" class="state-rate w-full bg-black/40 border border-[var(--primary-green)]/40 rounded px-2 py-1.5 text-sm text-[var(--primary-green)]" value="${data.rate}" step="0.001" oninput="calculateIFTA()">
                    </div>
                    <div class="flex-1 min-w-[80px]">
                        <label class="block text-[10px] text-[var(--secondary-blue)] uppercase mb-1">Gal Bought</label>
                        <input type="number" class="state-purchased w-full bg-black/40 border border-[var(--secondary-blue)]/40 rounded px-2 py-1.5 text-sm text-[var(--secondary-blue)]" value="${data.bought}" step="1" oninput="calculateIFTA()">
                    </div>
                    <button type="button" onclick="this.parentElement.remove(); calculateIFTA();" class="text-red-400 hover:text-red-300 mt-5 px-2 transition-colors">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                    <!-- Display calculated gallons used below row -->
                    <div class="w-full text-right text-[10px] text-gray-500 mt-1">
                        Est. Used: <span class="state-gal-used font-mono text-gray-300">0.00 gal</span>
                    </div>
                `;
                container.appendChild(row);
            }

            function initIfta() {
                const container = document.getElementById('ifta-states-container');
                if (!container) return; // Prevent errors if tab not open
                container.innerHTML = '';
                initialIftaData.forEach(d => addIftaStateRow(d));
                calculateIFTA();
            }

            function calculateIFTA() {
                const mpg = parseFloat(document.getElementById('ifta-mpg').value) || 1;
                const rows = document.querySelectorAll('.ifta-state-row');
                
                let totalPumpCost = 0;
                let totalTaxOwed = 0;
                let totalTaxPaid = 0;
                let totalGalUsed = 0;
                let totalGalBought = 0;
                
                let bestState = null;
                let lowestBasePrice = Infinity;
                
                rows.forEach(row => {
                    const stateName = row.querySelector('.state-name').value || 'Unknown';
                    const miles = parseFloat(row.querySelector('.state-miles').value) || 0;
                    const pumpPrice = parseFloat(row.querySelector('.state-price').value) || 0;
                    const iftaRate = parseFloat(row.querySelector('.state-rate').value) || 0;
                    const galPurchased = parseFloat(row.querySelector('.state-purchased').value) || 0;
                    
                    const galUsed = miles / mpg;
                    
                    totalPumpCost += (galPurchased * pumpPrice);
                    totalTaxOwed += (galUsed * iftaRate);
                    totalTaxPaid += (galPurchased * iftaRate);
                    
                    totalGalUsed += galUsed;
                    totalGalBought += galPurchased;
                    
                    // Optimization Logic: Find lowest (Pump Price - IFTA Rate)
                    const basePrice = pumpPrice - iftaRate;
                    if (pumpPrice > 0 && iftaRate > 0 && basePrice < lowestBasePrice) {
                        lowestBasePrice = basePrice;
                        bestState = stateName;
                    }
                    
                    // Update local row UI
                    const usedSpan = row.querySelector('.state-gal-used');
                    if(usedSpan) usedSpan.innerText = galUsed.toFixed(2) + ' gal';
                });
                
                const netBalance = totalTaxOwed - totalTaxPaid;
                const netCost = totalPumpCost + netBalance;
                
                // Update Main Outputs
                const elPump = document.getElementById('ifta-out-pump');
                const elOwed = document.getElementById('ifta-out-owed');
                const elPaid = document.getElementById('ifta-out-paid');
                const elBalance = document.getElementById('ifta-out-balance');
                const elNet = document.getElementById('ifta-out-net');
                
                if(elPump) elPump.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(totalPumpCost);
                if(elOwed) elOwed.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(totalTaxOwed);
                if(elPaid) elPaid.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(totalTaxPaid);
                if(elNet) elNet.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(netCost);
                
                if (elBalance) {
                    if (netBalance > 0) {
                        elBalance.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(netBalance) + " (Owed)";
                        elBalance.style.color = "#ff4757"; // Red for owed
                    } else {
                        elBalance.innerText = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Math.abs(netBalance)) + " (Refund)";
                        elBalance.style.color = "var(--primary-green)"; // Green for refund
                    }
                }
                
                // Update Optimization Insight
                const insightEl = document.getElementById('ifta-opt-insight');
                if (insightEl) {
                    if (bestState && lowestBasePrice !== Infinity) {
                        insightEl.innerHTML = `To minimize your overall Net Cost after IFTA reconciliation, shift as much purchasing volume as possible into <strong>${bestState}</strong>. Its effective untaxed base price is only <strong>$${lowestBasePrice.toFixed(3)}/gal</strong>.`;
                    } else {
                        insightEl.innerHTML = "Add valid state pricing and tax data to generate routing insights.";
                    }
                    
                    // Warning if gal bought doesn't match gal used
                    if (Math.abs(totalGalUsed - totalGalBought) > (totalGalUsed * 0.05) && totalGalBought > 0) {
                        insightEl.innerHTML += `<br><br><span style="color:#f59e0b; font-size:0.8rem;"><i class="fas fa-exclamation-triangle"></i> Note: Total gallons purchased (${totalGalBought.toFixed(0)}) significantly differs from estimated gallons used (${totalGalUsed.toFixed(0)}).</span>`;
                    }
                }
            }
            
            // Run initialization if script is loaded
            document.addEventListener('DOMContentLoaded', initIfta);
        </script>
"""
