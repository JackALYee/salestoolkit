content = r"""        <!-- SECTION: DISCOVERY MEETING -->
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
        </div>"""
