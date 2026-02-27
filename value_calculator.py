from ifta_calculator import content as ifta_calculator_content

content = r"""        <!-- SECTION: VALUE CALCULATOR -->
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
""" + "\n" + ifta_calculator_content + "\n" + r"""
            <!-- SUBSCRIPTION CALCULATOR SUB-SECTION -->
            <div id="sub-calc" class="sub-content">
                <div class="card fade-up" style="min-height: 400px; display: flex; justify-content: center; align-items: center;">
                    <p style="color: var(--text-grey); font-size: 1.1rem;"><i class="fa-solid fa-person-digging" style="margin-right: 8px;"></i> Subscription Calculator module coming soon.</p>
                </div>
            </div>
        </div>
"""                        <!-- Input Section -->
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
        </div>"""
