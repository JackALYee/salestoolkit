content = r"""        <!-- SECTION: PROSPECTING FLOW -->
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
        </div>"""
