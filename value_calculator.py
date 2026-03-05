from ifta_calculator import content as ifta_calculator_content

part1 = r"""        <!-- SECTION: VALUE CALCULATOR -->
        <div id="value-calculator" class="content-section hidden">
            <div class="card fade-up">
                <h2 class="gradient-text">Value Calculator</h2>
                <p>Calculate your expected return on investment, IFTA liabilities, and subscription costs using our advanced analytics tools.</p>
            </div>

            <div class="sub-nav-tabs fade-up">
                <button class="sub-nav-btn active" onclick="switchSubTab('tco-calc', this)">
                    <i data-lucide="calculator"></i> TCO Calculator
                </button>
                <button class="sub-nav-btn" onclick="switchSubTab('ifta-calc', this)">
                    <i data-lucide="map"></i> IFTA Calculator
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
"""

part2 = r"""
            <!-- SUBSCRIPTION CALCULATOR SUB-SECTION -->
            <div id="sub-calc" class="sub-content">
                <!-- Load Chart.js for dynamic visualization -->
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

                <div class="max-w-6xl w-full mx-auto glass-card overflow-visible fade-up delay-1">
                    
                    <div class="p-8 md:p-12 text-center border-b border-white/10 relative overflow-hidden rounded-t-2xl">
                        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-full bg-gradient-to-b from-[#8b5cf6]/10 to-transparent blur-3xl -z-10"></div>
                        <h1 class="text-3xl md:text-5xl font-bold mb-4 tracking-tight">
                            Subscription <span class="gradient-text" style="background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); -webkit-background-clip: text; color: transparent;">Economics</span>
                        </h1>
                        <p class="text-[var(--text-grey)] text-base md:text-lg max-w-3xl mx-auto font-light leading-relaxed">
                            Model out pricing, fixed costs, and recurring margins to instantly visualize your payback period and contract profitability.
                        </p>
                        
                        <!-- Internal Warning Message -->
                        <div class="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-2 rounded-lg inline-flex items-center mt-6 font-bold text-xs uppercase tracking-widest shadow-[0_0_15px_rgba(239,68,68,0.2)]">
                            <i class="fas fa-exclamation-triangle mr-2 text-lg"></i> This is Internal Calculator. DO NOT SHOW RESULTS TO CLIENTS
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-0 relative">
                        <!-- Decorative center line -->
                        <div class="hidden lg:block absolute left-5/12 top-10 bottom-10 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent -translate-x-1/2"></div>
            
                        <!-- Input Section (Left) -->
                        <div class="lg:col-span-5 p-6 md:p-10 border-b lg:border-b-0 lg:border-r border-white/10 fade-up delay-2">
                            
                            <!-- Cost Section -->
                            <h2 class="text-lg font-semibold mb-6 flex items-center text-white">
                                <i class="fas fa-coins text-[#ec4899] mr-3"></i> Cost Parameters
                            </h2>
                            
                            <form id="sub-calculator-form" class="space-y-5">
                                <div class="glass-panel p-4 space-y-4">
                                    <h3 class="text-xs uppercase tracking-wider text-gray-500 font-bold mb-2">Fixed Costs (Upfront)</h3>
                                    
                                    <div>
                                        <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                            Hardware Cost
                                            <div class="relative ml-2 inline-flex items-center z-20">
                                                <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                    <strong class="text-white block mb-1">Hardware Setup</strong>Please include any hardware and hardware add-ons such as memory.
                                                    <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                </div>
                                            </div>
                                        </label>
                                        <div class="relative">
                                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                            <input type="number" id="sub-hw-cost" value="250.00" min="0" step="10" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-hw')" onblur="unhighlight('sub-hw')">
                                        </div>
                                    </div>

                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                                Delivery Cost
                                                <div class="relative ml-2 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Logistics</strong>Include shipping, tax, tariff.
                                                        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <div class="relative">
                                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                                <input type="number" id="sub-del-cost" value="30.00" min="0" step="5" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-del')" onblur="unhighlight('sub-del')">
                                            </div>
                                        </div>
                                        <div>
                                            <label class="block text-sm font-medium text-[var(--text-grey)] mb-2">Other Fixed</label>
                                            <div class="relative">
                                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                                <input type="number" id="sub-fix-cost" value="20.00" min="0" step="5" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-fix')" onblur="unhighlight('sub-fix')">
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="glass-panel p-4 space-y-4">
                                    <h3 class="text-xs uppercase tracking-wider text-gray-500 font-bold mb-2">Monthly Costs (Recurring)</h3>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                                Platform Cost
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Platform</strong>FT Cloud Platform per month.
                                                        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <div class="relative">
                                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                                <input type="number" id="sub-plat-cost" value="4.00" min="0" step="0.5" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-plat')" onblur="unhighlight('sub-plat')">
                                            </div>
                                        </div>
                                        <div>
                                            <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                                Other Monthly
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                    <div class="absolute bottom-full right-0 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Misc</strong>Interest rate etc.
                                                        <div class="absolute top-full right-4 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <div class="relative">
                                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                                <input type="number" id="sub-other-mo" value="0.00" min="0" step="1" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-othermo')" onblur="unhighlight('sub-othermo')">
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                                Data Cost/GB
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Telecom</strong>Data cost per GB.
                                                        <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <div class="relative">
                                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">$</div>
                                                <input type="number" id="sub-data-cost" value="1.50" min="0" step="0.1" class="pl-8 w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-datac')" onblur="unhighlight('sub-datac')">
                                            </div>
                                        </div>
                                        <div>
                                            <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                                Data Used (GB)
                                                <div class="relative ml-1 inline-flex items-center z-20">
                                                    <i class="fas fa-question-circle text-[#8b5cf6] cursor-help opacity-70 hover:opacity-100 hover:text-[#ec4899] transition-all peer"></i>
                                                    <div class="absolute bottom-full right-0 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                        <strong class="text-white block mb-1">Volume</strong>Data used per month.
                                                        <div class="absolute top-full right-4 border-4 border-transparent tooltip-arrow-border"></div>
                                                    </div>
                                                </div>
                                            </label>
                                            <input type="number" id="sub-data-amt" value="2.0" min="0" step="0.5" class="w-full rounded-lg py-2 px-3 text-sm" oninput="calculateSub()" onfocus="highlight('sub-dataa')" onblur="unhighlight('sub-dataa')">
                                        </div>
                                    </div>
                                </div>

                                <!-- Revenue Section -->
                                <h2 class="text-lg font-semibold mt-8 mb-4 flex items-center text-white">
                                    <i class="fas fa-hand-holding-usd text-[#8b5cf6] mr-3"></i> Revenue Parameters
                                </h2>

                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                            Monthly Sub Fee
                                            <div class="relative ml-1 inline-flex items-center z-20">
                                                <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                    <strong class="text-white block mb-1">Revenue</strong>Monthly fee charge to client.
                                                    <div class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent tooltip-arrow-border"></div>
                                                </div>
                                            </div>
                                        </label>
                                        <div class="relative">
                                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--primary-green)]">$</div>
                                            <input type="number" id="sub-mo-fee" value="35.00" min="0" step="1" class="pl-8 w-full rounded-lg py-3 px-3 font-bold border-[var(--primary-green)]/50" style="color: var(--primary-green);" oninput="calculateSub()" onfocus="highlight('sub-fee')" onblur="unhighlight('sub-fee')">
                                        </div>
                                    </div>
                                    <div>
                                        <label class="flex items-center text-sm font-medium text-[var(--text-grey)] mb-2">
                                            Contract Period
                                            <div class="relative ml-1 inline-flex items-center z-20">
                                                <i class="fas fa-question-circle text-[var(--secondary-blue)] cursor-help opacity-70 hover:opacity-100 hover:text-[var(--primary-green)] transition-all peer"></i>
                                                <div class="absolute bottom-full right-0 mb-2 w-48 p-3 tooltip-bg text-gray-300 text-xs rounded-lg opacity-0 invisible peer-hover:opacity-100 peer-hover:visible transition-all duration-200 pointer-events-none">
                                                    <strong class="text-white block mb-1">Duration</strong>In months.
                                                    <div class="absolute top-full right-4 border-4 border-transparent tooltip-arrow-border"></div>
                                                </div>
                                            </div>
                                        </label>
                                        <div class="relative">
                                            <div class="absolute inset-y-0 right-4 flex items-center pointer-events-none text-gray-500 text-xs">mo</div>
                                            <input type="number" id="sub-months" value="36" min="1" step="1" class="w-full rounded-lg py-3 px-3 font-bold" oninput="calculateSub()" onfocus="highlight('sub-months')" onblur="unhighlight('sub-months')">
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
            
                        <!-- Output Section (Right) -->
                        <div class="lg:col-span-7 p-6 md:p-10 flex flex-col justify-start rounded-b-2xl lg:rounded-bl-none lg:rounded-br-2xl fade-up delay-3 relative bg-black/20">
                            
                            <!-- Key Metrics Grid -->
                            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                                <div class="glass-panel p-4 text-center border-t-2 border-t-red-400/50">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Total Fixed Cost</div>
                                    <div class="text-lg font-bold text-red-400" id="out-sub-fixed">$0</div>
                                </div>
                                <div class="glass-panel p-4 text-center border-t-2 border-t-orange-400/50">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Monthly Cost</div>
                                    <div class="text-lg font-bold text-orange-400" id="out-sub-mcost">$0</div>
                                </div>
                                <div class="glass-panel p-4 text-center border-t-2 border-t-[var(--secondary-blue)]">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Total Revenue</div>
                                    <div class="text-lg font-bold text-[var(--secondary-blue)]" id="out-sub-rev">$0</div>
                                </div>
                                <div class="glass-panel p-4 text-center border-t-2 border-t-[var(--primary-green)]/70">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Monthly Margin</div>
                                    <div class="text-lg font-bold text-[var(--primary-green)]" id="out-sub-margin">$0</div>
                                </div>
                                <div class="glass-panel p-4 text-center border-t-2 border-t-[var(--primary-green)]">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Total Margin</div>
                                    <div class="text-lg font-bold text-[var(--primary-green)]" id="out-sub-tmargin">$0</div>
                                </div>
                                <div class="glass-panel p-4 text-center border-t-2 border-t-[#8b5cf6]">
                                    <div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">ARR</div>
                                    <div class="text-lg font-bold text-[#8b5cf6]" id="out-sub-arr">$0</div>
                                </div>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                                <div class="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col justify-center items-center relative overflow-hidden">
                                    <div class="text-xs text-gray-400 uppercase tracking-wider mb-2 z-10">Pay-back Period</div>
                                    <div class="text-2xl font-extrabold text-white z-10" id="out-sub-payback">0 mo</div>
                                    <div class="absolute bottom-0 w-full h-1 bg-gradient-to-r from-red-400 to-yellow-400"></div>
                                </div>
                                <div class="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col justify-center items-center relative overflow-hidden">
                                    <div class="text-xs text-gray-400 uppercase tracking-wider mb-2 z-10">Pure Profit Period</div>
                                    <div class="text-2xl font-extrabold text-white z-10" id="out-sub-profit-mo">0 mo</div>
                                    <div class="absolute bottom-0 w-full h-1 bg-gradient-to-r from-yellow-400 to-[#2AF598]"></div>
                                </div>
                                <div class="bg-[var(--primary-green)]/10 border border-[var(--primary-green)]/30 rounded-xl p-4 flex flex-col justify-center items-center relative overflow-hidden shadow-[0_0_20px_rgba(42,245,152,0.1)]">
                                    <div class="text-xs text-[var(--primary-green)] uppercase tracking-wider mb-2 z-10 font-bold">Total Profit</div>
                                    <div class="text-3xl font-extrabold text-[var(--primary-green)] z-10 drop-shadow-[0_0_8px_rgba(42,245,152,0.5)]" id="out-sub-profit">$0</div>
                                </div>
                            </div>

                            <!-- Interactive Chart -->
                            <div class="glass-panel p-4 mb-6 relative" style="height: 300px; width: 100%;">
                                <canvas id="subChart"></canvas>
                            </div>
            
                            <!-- Interactive Formula Display (MathJax) -->
                            <div class="mt-auto glass-panel p-5 overflow-x-auto shadow-inner bg-black/40 border-t border-[#8b5cf6]/50">
                                <h3 class="text-gray-300 font-semibold mb-3 text-sm flex items-center">
                                    <i class="fas fa-square-root-alt mr-2 text-[#8b5cf6]"></i> Subscription Logic Matrix
                                </h3>
                                <div class="text-center pb-2 text-[0.8rem] space-y-3 text-gray-400 leading-relaxed">
                                    <div>$F_{total} = \class{var-sub-hw}{C_{hw}} + \class{var-sub-del}{C_{del}} + \class{var-sub-fix}{C_{fix}}$</div>
                                    <div>$M_{cost} = \class{var-sub-plat}{C_{plat}} + (\class{var-sub-datac}{C_{data}} \times \class{var-sub-dataa}{A_{data}}) + \class{var-sub-othermo}{C_{other}}$</div>
                                    <div>$Margin_{mo} = \class{var-sub-fee}{Fee_{mo}} - M_{cost}$ &nbsp; | &nbsp; $Margin_{total} = Margin_{mo} \times \class{var-sub-months}{T_{mo}}$</div>
                                    <div>$R_{total} = \class{var-sub-fee}{Fee_{mo}} \times \class{var-sub-months}{T_{mo}}$ &nbsp; | &nbsp; $ARR = \class{var-sub-fee}{Fee_{mo}} \times 12$</div>
                                    <div>$P_{payback} = \frac{F_{total}}{Margin_{mo}}$ &nbsp; | &nbsp; $P_{profit} = \class{var-sub-months}{T_{mo}} - P_{payback}$</div>
                                    <div>$Profit = Margin_{total} - F_{total}$</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Subscription Calculator JS Logic -->
                <script>
                    let subChartInstance = null;

                    // Custom Plugin to draw vertical profit line on hover
                    const profitLinePlugin = {
                        id: 'profitLine',
                        afterDatasetsDraw: (chart) => {
                            if (chart.tooltip?._active?.length) {
                                const ctx = chart.ctx;
                                const activePoint = chart.tooltip._active[0];
                                const index = activePoint.index;
                                
                                const metaRev = chart.getDatasetMeta(0);
                                const metaCost = chart.getDatasetMeta(1);
                                
                                if(!metaRev.data[index] || !metaCost.data[index]) return;

                                const x = metaRev.data[index].x;
                                const yRev = metaRev.data[index].y;
                                const yCost = metaCost.data[index].y;
                                
                                const revVal = chart.data.datasets[0].data[index];
                                const costVal = chart.data.datasets[1].data[index];
                                const profit = revVal - costVal;

                                ctx.save();
                                // Draw the vertical dashed line
                                ctx.beginPath();
                                ctx.moveTo(x, yRev);
                                ctx.lineTo(x, yCost);
                                ctx.lineWidth = 2;
                                ctx.strokeStyle = profit >= 0 ? 'rgba(42, 245, 152, 0.8)' : 'rgba(255, 71, 87, 0.8)';
                                ctx.setLineDash([4, 4]);
                                ctx.stroke();
                                
                                // Draw numerical profit box
                                const midY = (yRev + yCost) / 2;
                                ctx.font = 'bold 12px "Inter", sans-serif';
                                ctx.textAlign = 'left';
                                ctx.textBaseline = 'middle';
                                const text = (profit >= 0 ? '+$' : '-$') + Math.abs(profit).toLocaleString('en-US', {maximumFractionDigits: 0});
                                
                                const textWidth = ctx.measureText(text).width;
                                ctx.fillStyle = 'rgba(5, 8, 16, 0.9)';
                                ctx.beginPath();
                                ctx.roundRect(x + 10, midY - 14, textWidth + 16, 28, 6);
                                ctx.fill();
                                ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                                ctx.lineWidth = 1;
                                ctx.stroke();
                                
                                ctx.fillStyle = profit >= 0 ? '#2AF598' : '#ff4757';
                                ctx.fillText(text, x + 18, midY);
                                
                                ctx.restore();
                            }
                        }
                    };

                    function calculateSub() {
                        // 1. Get Inputs (Fallback to 0 if NaN)
                        const hwCost = parseFloat(document.getElementById('sub-hw-cost').value) || 0;
                        const delCost = parseFloat(document.getElementById('sub-del-cost').value) || 0;
                        const fixCost = parseFloat(document.getElementById('sub-fix-cost').value) || 0;

                        const platCost = parseFloat(document.getElementById('sub-plat-cost').value) || 0;
                        const dataCost = parseFloat(document.getElementById('sub-data-cost').value) || 0;
                        const dataAmt = parseFloat(document.getElementById('sub-data-amt').value) || 0;
                        const otherMo = parseFloat(document.getElementById('sub-other-mo').value) || 0;

                        const moFee = parseFloat(document.getElementById('sub-mo-fee').value) || 0;
                        const months = parseInt(document.getElementById('sub-months').value) || 0;

                        // 2. Perform Calculations
                        const fTotal = hwCost + delCost + fixCost;
                        const mCost = platCost + (dataCost * dataAmt) + otherMo;
                        const rTotal = moFee * months;
                        
                        const margin = moFee - mCost;
                        const totalMargin = margin * months;
                        let payback = margin > 0 ? (fTotal / margin) : Infinity;
                        
                        let pureProfitPeriod = 0;
                        if (margin > 0 && months > payback) {
                            pureProfitPeriod = months - payback;
                        }
                        
                        const totalProfit = totalMargin - fTotal;
                        const arr = moFee * 12;

                        // 3. Format & Update DOM
                        const formatCurr = (num) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
                        const formatMo = (num) => isFinite(num) ? num.toFixed(1) + " mo" : "Never";

                        document.getElementById('out-sub-fixed').innerText = formatCurr(fTotal);
                        document.getElementById('out-sub-mcost').innerText = formatCurr(mCost);
                        document.getElementById('out-sub-margin').innerText = formatCurr(margin);
                        document.getElementById('out-sub-tmargin').innerText = formatCurr(totalMargin);
                        document.getElementById('out-sub-rev').innerText = formatCurr(rTotal);
                        document.getElementById('out-sub-arr').innerText = formatCurr(arr);
                        
                        document.getElementById('out-sub-payback').innerText = formatMo(payback);
                        document.getElementById('out-sub-profit-mo').innerText = formatMo(pureProfitPeriod);
                        document.getElementById('out-sub-profit').innerText = formatCurr(totalProfit);

                        // Color handling for Margin
                        if (margin < 0) {
                            document.getElementById('out-sub-margin').style.color = '#ff4757'; // Red
                            document.getElementById('out-sub-tmargin').style.color = '#ff4757'; // Red
                        } else {
                            document.getElementById('out-sub-margin').style.color = 'var(--primary-green)'; // Green
                            document.getElementById('out-sub-tmargin').style.color = 'var(--primary-green)'; // Green
                        }

                        // Color handling for Profit/Payback
                        if (totalProfit < 0) {
                            document.getElementById('out-sub-profit').style.color = '#ff4757'; // Red
                            document.getElementById('out-sub-payback').style.color = '#ff4757';
                        } else {
                            document.getElementById('out-sub-profit').style.color = 'var(--primary-green)';
                            document.getElementById('out-sub-payback').style.color = 'white';
                        }

                        // 4. Update Chart
                        updateSubChart(months, fTotal, mCost, moFee, payback);
                    }

                    function updateSubChart(months, fTotal, mCost, moFee, payback) {
                        const ctx = document.getElementById('subChart');
                        if (!ctx) return;

                        // Generate Data arrays
                        const labels = [];
                        const costData = [];
                        const revData = [];

                        for (let i = 0; i <= months; i++) {
                            labels.push(`Mo ${i}`);
                            costData.push(fTotal + (i * mCost));
                            revData.push(i * moFee);
                        }

                        if (subChartInstance) {
                            subChartInstance.destroy();
                        }

                        Chart.defaults.color = '#94A3B8';
                        Chart.defaults.font.family = '"Inter", sans-serif';

                        subChartInstance = new Chart(ctx, {
                            type: 'line',
                            plugins: [profitLinePlugin],
                            data: {
                                labels: labels,
                                datasets: [
                                    {
                                        label: 'Cumulative Revenue',
                                        data: revData,
                                        borderColor: '#2AF598',
                                        backgroundColor: 'rgba(42, 245, 152, 0.1)',
                                        borderWidth: 3,
                                        pointRadius: 0,
                                        pointHoverRadius: 6,
                                        fill: true,
                                        tension: 0.1
                                    },
                                    {
                                        label: 'Cumulative Cost',
                                        data: costData,
                                        borderColor: '#ff4757',
                                        backgroundColor: 'transparent',
                                        borderWidth: 2,
                                        borderDash: [5, 5],
                                        pointRadius: 0,
                                        pointHoverRadius: 6,
                                        fill: false,
                                        tension: 0.1
                                    }
                                ]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: {
                                    mode: 'index',
                                    intersect: false,
                                },
                                plugins: {
                                    legend: {
                                        position: 'top',
                                        labels: { boxWidth: 12, usePointStyle: true }
                                    },
                                    tooltip: {
                                        backgroundColor: 'rgba(5, 8, 16, 0.9)',
                                        titleColor: '#2AF598',
                                        borderColor: 'rgba(255,255,255,0.1)',
                                        borderWidth: 1,
                                        padding: 10,
                                        callbacks: {
                                            label: function(context) {
                                                let label = context.dataset.label || '';
                                                if (label) { label += ': '; }
                                                if (context.parsed.y !== null) {
                                                    label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                                                }
                                                return label;
                                            }
                                        }
                                    }
                                },
                                scales: {
                                    x: {
                                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                        ticks: { maxTicksLimit: 12 }
                                    },
                                    y: {
                                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                        ticks: {
                                            callback: function(value) { return '$' + value; }
                                        }
                                    }
                                }
                            }
                        });
                    }

                    // Attach local event listener to initialize the calculator when DOM is ready
                    document.addEventListener('DOMContentLoaded', () => {
                        if (typeof calculateSub === 'function') {
                            calculateSub();
                        }
                    });
                </script>
            </div>
        </div>
"""

# Safely stitch the strings together
content = part1 + "\n" + ifta_calculator_content + "\n" + part2
