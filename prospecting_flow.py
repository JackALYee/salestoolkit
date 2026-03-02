content = r"""        <!-- SECTION: PROSPECTING FLOW -->
        <div id="prospecting-flow" class="content-section hidden">
            
            <!-- Custom CSS for Horizontal Nested Tabs -->
            <style>
                .nested-tab-btn {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: var(--text-grey);
                    padding: 10px 24px;
                    border-radius: 30px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: var(--transition);
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                }
                .nested-tab-btn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    color: var(--text-white);
                    transform: translateY(-2px);
                }
                .nested-tab-btn.active-nested-tab {
                    background: rgba(42, 245, 152, 0.1) !important;
                    border-color: var(--primary-green) !important;
                    color: var(--primary-green) !important;
                    box-shadow: var(--glow-shadow);
                }
            </style>

            <!-- Script to handle Nested Tabs -->
            <script>
                function switchNestedTab(tabId, btnElement, contentClass) {
                    const container = btnElement.closest('.nested-tabs-container');
                    
                    // Reset all buttons in this specific container
                    container.querySelectorAll('.nested-tab-btn').forEach(btn => {
                        btn.classList.remove('active-nested-tab');
                        btn.style.background = '';
                        btn.style.color = '';
                        btn.style.borderColor = '';
                    });
                    
                    // Set active state on clicked button
                    btnElement.classList.add('active-nested-tab');

                    // Hide all content blocks in this specific container
                    container.querySelectorAll('.' + contentClass).forEach(content => {
                        content.classList.add('hidden');
                    });
                    
                    // Show the targeted content block
                    const targetContent = document.getElementById(tabId);
                    if (targetContent) {
                        targetContent.classList.remove('hidden');
                        
                        // Small animation effect
                        targetContent.style.opacity = '0';
                        targetContent.style.transform = 'translateY(10px)';
                        setTimeout(() => {
                            targetContent.style.transition = 'all 0.3s ease';
                            targetContent.style.opacity = '1';
                            targetContent.style.transform = 'translateY(0)';
                        }, 10);
                    }
                }
            </script>

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

            <!-- ========================================== -->
            <!-- TSP FLOW SUB-SECTION                       -->
            <!-- ========================================== -->
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

                    <!-- Step 2 (Scripts inside Horizontal Tabs) -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">Prospecting Scripts</div>
                        <span class="flow-subtitle">Initial Outreach & Value Pitching</span>
                        
                        <div class="card nested-tabs-container" style="margin-left: 0; padding: 25px;">
                            
                            <!-- Horizontal Tabs Nav -->
                            <div class="flex flex-wrap gap-4 mb-6 border-b border-white/10 pb-5">
                                <button onclick="switchNestedTab('tsp-emails', this, 'tsp-script-content')" class="nested-tab-btn active-nested-tab">
                                    <i class="fa-solid fa-envelope"></i> Email Template
                                </button>
                                <button onclick="switchNestedTab('tsp-calls', this, 'tsp-script-content')" class="nested-tab-btn">
                                    <i class="fa-solid fa-phone"></i> Cold Calling Script
                                </button>
                                <button onclick="switchNestedTab('tsp-pitches', this, 'tsp-script-content')" class="nested-tab-btn">
                                    <i class="fa-solid fa-microphone"></i> Elevator Pitch Script
                                </button>
                            </div>
                            
                            <!-- Tabs Content Area -->
                            <div class="w-full">
                                
                                <!-- ================== TSP EMAILS ================== -->
                                <div id="tsp-emails" class="tsp-script-content">
                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">1) Business professional (general audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Partnering with {company} to scale AI video telematics<br><br>
                                            Hi {first_name},<br><br>
                                            I’m reaching out because Streamax partners with Telematics Service Providers to deliver AI video telematics to fleets with a scalable, support-friendly model.<br><br>
                                            If you’re expanding your portfolio or upgrading an existing video solution, I’d like to learn how {company} goes to market today and what a “good partner” looks like for you (margin, platform operations, integrations, and support).<br><br>
                                            Would you be open to a 15–20 minute partner fit call next week? If it’s not a priority right now, I’m happy to follow your timing.
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">2) Business casual (general audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Quick chat on video telematics for {company}?<br><br>
                                            Hi {first_name},<br><br>
                                            I work with Streamax, and we help TSPs add or upgrade AI video telematics without turning it into a support headache.<br><br>
                                            Curious—are your fleet customers asking for better video/AI lately, or are you already offering video and looking to improve it?<br><br>
                                            If it’s worth exploring, can we do a quick 15-minute call to see whether there’s a fit for {company}?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">3) Technical (technical audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Multi-tenant video telematics + APIs for TSP operations<br><br>
                                            Hi {first_name},<br><br>
                                            Streamax supports TSP deployments that require scalable operations—multi-tenant management, provisioning at volume, remote diagnostics, and integration paths (API/webhooks/export) to fit existing workflows.<br><br>
                                            I’m trying to understand how {company} operates today: provisioning, firmware management, user/role administration, and your top integration requirements (ELD/TMS/SSO/reporting).<br><br>
                                            If you’re open, I’d value a 20-minute technical discovery to align on architecture needs and what “operationally scalable” means for your team.
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">4) C-level professional (C-suite audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Expanding ARPU and retention with a modern video safety bundle<br><br>
                                            Hi {first_name},<br><br>
                                            Streamax partners with Telematics Service Providers to create differentiated video + AI safety offerings that increase attach rate, improve retention, and strengthen competitiveness in RFPs.<br><br>
                                            I’d like to understand {company}’s growth focus this year—ARPU expansion, churn reduction, or new segment penetration—and share how leading TSPs structure a scalable video program without diluting service quality.<br><br>
                                            Would you be open to a brief 15–20 minute conversation?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">5) C-level casual (C-suite audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Could Streamax help {company} win more fleets with video?<br><br>
                                            Hi {first_name},<br><br>
                                            I’ll keep this short. Streamax helps TSPs add a video + AI safety layer that makes your offering stickier and more competitive—without a messy rollout.<br><br>
                                            If you’re open, I’d love 15 minutes to learn what {company} is optimizing for this year (growth, retention, differentiation) and see if there’s a fit.<br><br>
                                            Would next week work?
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- ================== TSP COLD CALLS ================== -->
                                <div id="tsp-calls" class="tsp-script-content hidden">
                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">1) Business Professional (General)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Book a 15–20 min partner fit call.<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} with Streamax. Did I catch you with 30 seconds?<br><br>
                                            <strong>Prospect:</strong> I have a minute.<br><br>
                                            <strong>Rep:</strong> Thanks. We partner with telematics service providers to offer AI video telematics to fleets—designed to scale without turning into a support burden. I’m calling to see if it’s relevant for {company}.<br><br>
                                            <strong>Prospect:</strong> What do you mean by “partner”?<br><br>
                                            <strong>Rep:</strong> You keep the customer relationship. We provide the video + AI platform, partner enablement, and operational tools so you can package it as part of your offering.<br><br>
                                            <strong>Prospect:</strong> We already have a video vendor.<br><br>
                                            <strong>Rep:</strong> That makes sense. When TSPs switch or add a second option, it’s usually because of one of three reasons: platform usability, false alerts/AI performance, or support load. Which of those is most painful today—if any?<br><br>
                                            <strong>Prospect:</strong> Support load and reliability.<br><br>
                                            <strong>Rep:</strong> Got it. If we can show you an ops-friendly approach—deployment, diagnostics, escalation—would it be worth a quick 15–20 minute partner fit call next week?<br><br>
                                            <strong>Prospect:</strong> Maybe.<br><br>
                                            <strong>Rep:</strong> Great. I can do Tuesday 10:00 or Wednesday 2:00. Which is better?<br><br>
                                            <em>If prospect says “Not interested”:</em><br>
                                            <strong>Rep:</strong> Totally fair. Before I let you go, is video telematics simply not a focus for {company} this year, or is it more about timing?<br><br>
                                            <strong>Prospect:</strong> Timing.<br><br>
                                            <strong>Rep:</strong> Understood—what month should I circle back?
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">2) Business Casual (General)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Quickly qualify if they’re a TSP motion and get a meeting.<br><br>
                                            <strong>Rep:</strong> Hey {first_name}, {your_name} here from Streamax. Quick one—am I calling the right person for partnerships or product at {company}?<br><br>
                                            <strong>Prospect:</strong> Depends—what’s this about?<br><br>
                                            <strong>Rep:</strong> We help TSPs roll out AI video telematics to fleets without creating a ton of support tickets. I’m trying to see if video is on your roadmap or if fleets are asking you for it.<br><br>
                                            <strong>Prospect:</strong> Yeah, we get requests.<br><br>
                                            <strong>Rep:</strong> Makes sense. What’s the #1 thing you wish was better with video solutions—install, platform usability, AI accuracy, or support?<br><br>
                                            <strong>Prospect:</strong> AI accuracy.<br><br>
                                            <strong>Rep:</strong> Got it. If I could show you how we handle edge AI and reduce noise while keeping the workflow simple, would a 15-minute call be worth it?<br><br>
                                            <strong>Prospect:</strong> Sure, send something.<br><br>
                                            <strong>Rep:</strong> Will do—what’s the best email? And should we just lock 15 minutes now so it doesn’t get lost?<br><br>
                                            <em>If prospect says “Send info”:</em><br>
                                            <strong>Rep:</strong> Happy to. To make it relevant, are you selling video today or still evaluating partners?<br><br>
                                            <strong>Prospect:</strong> Selling.<br><br>
                                            <strong>Rep:</strong> Perfect—I’ll send a short overview and a couple of questions. Want to do a quick 15 minutes Thursday or Friday to see if it’s a fit?
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">3) Technical / Operations (Technical Audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Book a technical discovery call (ops scalability + integration).<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} from Streamax. Do you have 30 seconds?<br><br>
                                            <strong>Prospect:</strong> Okay—what’s up?<br><br>
                                            <strong>Rep:</strong> We support TSP deployments where the hard part is scale: multi-tenant operations, provisioning, remote diagnostics, and integrations. I’m calling to see how {company} runs video operations today and whether you have pain points we can help with.<br><br>
                                            <strong>Prospect:</strong> We’re pretty set.<br><br>
                                            <strong>Rep:</strong> Understood. Quick calibration—how are you handling device provisioning and firmware management at volume right now?<br><br>
                                            <strong>Prospect:</strong> Mostly manual, some scripts.<br><br>
                                            <strong>Rep:</strong> That’s common. When TSPs talk to us, they usually want fewer escalations and faster time-to-resolution. What’s your biggest ops bottleneck today?<br><br>
                                            <strong>Prospect:</strong> Too many support tickets after install.<br><br>
                                            <strong>Rep:</strong> Got it. If we did a 20-minute technical call, I’d like to map your flow—activation, diagnostics, escalation—and share how our partner toolset reduces ticket volume. Is next week reasonable?<br><br>
                                            <strong>Prospect:</strong> Possibly.<br><br>
                                            <strong>Rep:</strong> Great. Monday 3:00 or Wednesday 11:00?<br><br>
                                            <em>If prospect asks “Do you have APIs?”</em><br>
                                            <strong>Rep:</strong> Yes—API-based integration options plus exports and admin tooling. On the call we can cover your top integration targets and what you need for multi-tenant support.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">4) C-Level Professional (CEO/GM/VP)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Executive alignment call (growth, ARPU, retention).<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} with Streamax. I’ll be brief—do you have 20 seconds?<br><br>
                                            <strong>Prospect:</strong> Go ahead.<br><br>
                                            <strong>Rep:</strong> Streamax partners with telematics providers to add AI video telematics as a differentiated bundle that increases ARPU and retention. I’m calling to ask one question: is {company} more focused this year on growing ARPU, reducing churn, or winning more RFPs?<br><br>
                                            <strong>Prospect:</strong> Winning more RFPs.<br><br>
                                            <strong>Rep:</strong> Makes sense. Video is often the missing layer in RFPs, but it only works if it scales without hurting service quality. If I could share how other TSPs launch a video bundle with a clean operational model, would you be open to a 15-minute conversation?<br><br>
                                            <strong>Prospect:</strong> Maybe—send me details.<br><br>
                                            <strong>Rep:</strong> Happy to. To tailor it: are you already offering video, or evaluating adding it?<br><br>
                                            <strong>Prospect:</strong> Offering video.<br><br>
                                            <strong>Rep:</strong> Great. Let’s do 15 minutes and I’ll come prepared with a migration/upgrade checklist and partner economics discussion. Tuesday or Thursday?
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">5) C-Level Casual (CEO/GM/Founder)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Fast “fit check” and book a short meeting.<br><br>
                                            <strong>Rep:</strong> Hey {first_name}, {your_name} from Streamax—did I catch you at a bad time?<br><br>
                                            <strong>Prospect:</strong> What do you need?<br><br>
                                            <strong>Rep:</strong> Super quick. We help TSPs add video + AI in a way that’s scalable—so it helps you win fleets, not drown your team in support. I’m trying to see if this is even on your radar at {company}.<br><br>
                                            <strong>Prospect:</strong> We get asked about video sometimes.<br><br>
                                            <strong>Rep:</strong> That tracks. If you could wave a magic wand, what would video do for your business—help you win deals, increase ARPU, or reduce churn?<br><br>
                                            <strong>Prospect:</strong> Win deals.<br><br>
                                            <strong>Rep:</strong> Perfect. If I can show a straightforward partner playbook for packaging and launching video, can we do 15 minutes next week?<br><br>
                                            <strong>Prospect:</strong> Fine.<br><br>
                                            <strong>Rep:</strong> Great—what’s better, Tuesday morning or Wednesday afternoon?<br><br>
                                            <em>If prospect pushes back on price:</em><br>
                                            <strong>Prospect:</strong> Video is expensive.<br><br>
                                            <strong>Rep:</strong> Totally fair. Most TSPs don’t win on cheapest hardware—they win on reliability, fewer escalations, and a platform fleets actually use. On a short call, we can map your economics and see if the margin and ops model make sense.
                                        </div>
                                    </div>
                                </div>

                                <!-- ================== TSP PITCHES ================== -->
                                <div id="tsp-pitches" class="tsp-script-content hidden">
                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">1) "Who is Streamax?" (General)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Good morning, I’m from Streamax. We’re a global provider of AI-powered video safety and fleet management solutions, operating in 100+ countries with millions of connected vehicles. We help fleets turn video into action—prevent incidents, resolve claims faster, and coach drivers consistently—so safety teams spend less time chasing evidence and more time reducing risk.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">2) "Why Streamax?" (Outcome-driven)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax is built for fleets that care about measurable outcomes. Our customers use Streamax to reduce accident rates, speed up incident investigation, and improve fleet efficiency through a practical loop: detect risk with edge AI, capture reliable evidence, and turn events into coaching. The result is fewer disputes, fewer repeat incidents, and a safety program that actually gets adopted day-to-day.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">3) Public Transit / Bus Operators</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax is a trusted AI video safety partner for large-scale operations like public transit. We help bus operators reduce accidents and operating costs by combining in-vehicle video, edge AI, and a unified cloud platform that supports daily safety workflows. In markets like Latin America, major transit operators have adopted Streamax to improve safety performance and reduce incident-related expenses—especially at scale across thousands of buses.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">4) TSP / Channel Partner (Partner angle)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax partners with Telematics Service Providers to add a scalable video + AI safety layer to their portfolio. We help you offer a differentiated bundle that fleets want—without creating a heavy support burden—by providing reliable hardware, edge AI, and a platform designed for repeatable deployment and operations. The goal is simple: help you win more deals, increase ARPU, and improve retention with a solution that scales.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">5) "Why is it not cheap?" (Value + ROI)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax may not be the cheapest option, but we focus on total cost of ownership and long-term value. Cheaper systems become expensive when they miss critical events, generate noisy false alerts, or create operational overhead. Streamax is designed to deliver outcomes—customers have reported improvements like lower accident-related costs, reduced maintenance and insurance burden, and stronger uptime—often achieving payback within a multi-year program while improving safety for drivers and passengers.
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- ========================================== -->
            <!-- END USER FLOW SUB-SECTION                  -->
            <!-- ========================================== -->
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

                    <!-- Step 2 (Scripts inside Horizontal Tabs) -->
                    <div class="flow-step-block fade-up">
                        <div class="flow-marker blue">2</div>
                        <div class="flow-title">Prospecting Scripts</div>
                        <span class="flow-subtitle">Initial Outreach & Value Pitching</span>
                        
                        <div class="card nested-tabs-container" style="margin-left: 0; padding: 25px;">
                            
                            <!-- Horizontal Tabs Nav -->
                            <div class="flex flex-wrap gap-4 mb-6 border-b border-white/10 pb-5">
                                <button onclick="switchNestedTab('eu-emails', this, 'eu-script-content')" class="nested-tab-btn active-nested-tab">
                                    <i class="fa-solid fa-envelope"></i> Email Template
                                </button>
                                <button onclick="switchNestedTab('eu-calls', this, 'eu-script-content')" class="nested-tab-btn">
                                    <i class="fa-solid fa-phone"></i> Cold Calling Script
                                </button>
                                <button onclick="switchNestedTab('eu-pitches', this, 'eu-script-content')" class="nested-tab-btn">
                                    <i class="fa-solid fa-microphone"></i> Elevator Pitch Script
                                </button>
                            </div>
                            
                            <!-- Tabs Content Area -->
                            <div class="w-full">
                                
                                <!-- ================== EU EMAILS ================== -->
                                <div id="eu-emails" class="eu-script-content">
                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">1) Business professional (General Audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Reducing incidents and speeding up claims evidence for {company}<br><br>
                                            Hi {first_name},<br><br>
                                            I’m {your_name} with Streamax. We help fleets reduce safety risk and claims friction using AI-powered video telematics—reliable in-vehicle video plus a platform that makes it fast to find, review, and share evidence.<br><br>
                                            If {company} is focused on improving driver safety, reducing preventable incidents, or shortening the time it takes to resolve claims, I’d like to learn how your team handles incidents today and where the workflow gets stuck.<br><br>
                                            Would you be open to a 15–20 minute discovery call next week to see if Streamax is relevant for your fleet?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">2) Business casual (General Audience)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Quick question about your incident video workflow at {company}<br><br>
                                            Hi {first_name},<br><br>
                                            When something happens on the road, how long does it take your team to pull the right video and share it with the right people?<br><br>
                                            Streamax helps fleets make that process fast and repeatable with AI video telematics—so safety teams spend less time chasing footage and more time preventing repeat incidents.<br><br>
                                            If it’s worth exploring, open to a quick 15-minute call to see whether Streamax could help {company}?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">3) Technical (Technical/IT)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Video telematics deployment + security requirements for {company}<br><br>
                                            Hi {first_name},<br><br>
                                            I’m {your_name} from Streamax. We support fleet deployments of AI video telematics with a focus on operational reliability and security—device provisioning at scale, role-based access control, auditability, and integration paths (APIs/exports) to fit existing systems.<br><br>
                                            If you’re involved in evaluation for {company}, I’d like to understand your requirements around access control, data retention, connectivity, and integration needs (ELD/TMS/SSO/reporting).<br><br>
                                            Would you be open to a 20-minute technical discovery to confirm fit and outline a deployment approach?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">4) C-level professional (C-suite)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Lowering accident exposure and claims costs for {company}<br><br>
                                            Hi {first_name},<br><br>
                                            Streamax helps fleets reduce accident exposure and improve safety performance by combining in-vehicle video, edge AI, and a platform built for fast evidence retrieval and consistent driver coaching.<br><br>
                                            Leaders typically come to us when they want to reduce preventable incidents, shorten claims cycle time, and improve accountability without adding operational overhead.<br><br>
                                            If those priorities align with {company}’s goals this year, would you be open to a brief 15–20 minute conversation to evaluate whether Streamax is a fit?
                                        </div>
                                    </div>

                                    <div class="script-box">
                                        <div class="script-header"><span class="script-tag">5) C-level casual (C-suite)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Subject:</strong> Could we help {company} cut claims friction and repeat incidents?<br><br>
                                            Hi {first_name},<br><br>
                                            I’ll keep this short. Streamax helps fleets reduce incidents and make claims/evidence workflows faster with AI video telematics. The biggest difference is adoption: safety teams can find the right clip quickly, act on it, and coach drivers consistently.<br><br>
                                            If you’re open, I’d love 15 minutes to learn what {company} is trying to improve right now—incident rates, claims cycle time, or coaching consistency—and see if Streamax is relevant.
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- ================== EU COLD CALLS ================== -->
                                <div id="eu-calls" class="eu-script-content hidden">
                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">1) Business Professional (Safety/Ops)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Book a 15–20 min discovery call.<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} with Streamax. Did I catch you with 30 seconds?<br><br>
                                            <strong>Prospect:</strong> Sure, what’s this about?<br><br>
                                            <strong>Rep:</strong> We help fleets reduce incidents and speed up claims evidence using AI video telematics—so safety teams can find the right video fast and coach drivers consistently. I’m calling to see if it’s relevant for {company}.<br><br>
                                            <strong>Prospect:</strong> We already have cameras.<br><br>
                                            <strong>Rep:</strong> Totally fair. Most fleets do. When teams talk to us, it’s usually because evidence is still slow to retrieve, or coaching isn’t consistent, or the system creates too much noise. Which one is most true for you today?<br><br>
                                            <strong>Prospect:</strong> Evidence retrieval is slow.<br><br>
                                            <strong>Rep:</strong> Got it. If we could show a workflow that cuts time-to-video and makes incidents easier to manage, would you be open to a 15–20 minute discovery call next week?<br><br>
                                            <strong>Prospect:</strong> Maybe.<br><br>
                                            <strong>Rep:</strong> Great—does Tuesday morning or Wednesday afternoon work better?<br><br>
                                            <em>If they say “Not interested”:</em><br>
                                            <strong>Rep:</strong> Understood. Before I let you go, is it not a priority this year, or is it more about timing?<br><br>
                                            <strong>Prospect:</strong> Timing.<br><br>
                                            <strong>Rep:</strong> Makes sense—when should I circle back?
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">2) Business Casual (Dispatcher / Ops)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Identify pain fast and secure meeting.<br><br>
                                            <strong>Rep:</strong> Hey {first_name}, {your_name} from Streamax—did I catch you at a bad time?<br><br>
                                            <strong>Prospect:</strong> What do you need?<br><br>
                                            <strong>Rep:</strong> Quick one. When an incident happens, do you have the video you need within a few minutes—or does it turn into a hunt?<br><br>
                                            <strong>Prospect:</strong> It’s definitely a hunt.<br><br>
                                            <strong>Rep:</strong> That’s exactly what we fix. Streamax is AI video telematics that makes evidence retrieval fast and consistent, and helps reduce repeat incidents with coaching workflows.<br><br>
                                            <strong>Prospect:</strong> We’re busy right now.<br><br>
                                            <strong>Rep:</strong> Totally get it. That’s why I’m asking for just 15 minutes. If I can show you a faster incident workflow and what the rollout looks like, would next week be crazy?<br><br>
                                            <strong>Prospect:</strong> Maybe.<br><br>
                                            <strong>Rep:</strong> Fair—what day is typically lighter for you, Tuesday or Thursday?<br><br>
                                            <em>If they say “Send info”:</em><br>
                                            <strong>Rep:</strong> Happy to. What’s the best email? And should we lock 15 minutes so I can tailor it to your workflow?
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">3) Technical Audience (IT / Tech)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Book a 20-min technical discovery.<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} from Streamax. Do you have 30 seconds?<br><br>
                                            <strong>Prospect:</strong> Okay—go ahead.<br><br>
                                            <strong>Rep:</strong> Streamax provides AI video telematics with a focus on reliable deployment: provisioning at scale, role-based access control, and integration options like APIs and exports. I’m calling to see if {company} is evaluating video telematics upgrades this year.<br><br>
                                            <strong>Prospect:</strong> We’re not changing anything.<br><br>
                                            <strong>Rep:</strong> Understood. Quick check—are there any pain points you consistently hear from safety or ops about the current system?<br><br>
                                            <strong>Prospect:</strong> Complaints about too many false alerts.<br><br>
                                            <strong>Rep:</strong> Got it. If we do a 20-minute technical call, we can cover edge AI event tuning, alert noise reduction, and how data access and retention are controlled. Would next week be reasonable?<br><br>
                                            <strong>Prospect:</strong> Possibly.<br><br>
                                            <strong>Rep:</strong> Great. Monday 2:00 or Wednesday 11:00?<br><br>
                                            <em>If they ask “Do you support SSO/security?”</em><br>
                                            <strong>Rep:</strong> Yes—role-based access controls and enterprise security options. We can align your requirements on the call.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">4) C-Level Professional (CEO/COO/CFO)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Executive alignment + meeting.<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} from Streamax. I’ll be brief—do you have 20 seconds?<br><br>
                                            <strong>Prospect:</strong> Go ahead.<br><br>
                                            <strong>Rep:</strong> Streamax helps fleets reduce accident exposure and claims friction using AI video telematics—reliable video evidence plus workflows that drive consistent coaching. I’m calling to ask one question: is {company} more focused this year on reducing incidents, reducing claims costs, or improving operational efficiency?<br><br>
                                            <strong>Prospect:</strong> Claims costs.<br><br>
                                            <strong>Rep:</strong> Makes sense. Faster, cleaner evidence and fewer disputed claims usually drive direct savings. If I could share a quick framework for ROI and rollout risk, would you be open to a 15-minute call?<br><br>
                                            <strong>Prospect:</strong> Maybe—send me something.<br><br>
                                            <strong>Rep:</strong> Happy to. To make it relevant, who owns safety and claims workflow day-to-day at {company}?<br><br>
                                            <strong>Prospect:</strong> Our safety director.<br><br>
                                            <strong>Rep:</strong> Great. If you’re okay with it, let’s schedule 15 minutes with them as well so we can align outcomes and timeline.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: var(--secondary-blue);">
                                        <div class="script-header"><span class="script-tag" style="color: var(--secondary-blue);">5) Driver / Small Fleet Owner (SMB)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            <strong>Goal:</strong> Book a short fit check; keep language simple.<br><br>
                                            <strong>Rep:</strong> Hi {first_name}, this is {your_name} with Streamax. Did I catch you at a bad time?<br><br>
                                            <strong>Prospect:</strong> What is this?<br><br>
                                            <strong>Rep:</strong> Totally fair—quick one. Streamax is a dashcam + AI safety system that helps protect drivers with video evidence and alerts, and makes it easier to handle accidents or false claims.<br><br>
                                            <strong>Prospect:</strong> I already have a dashcam.<br><br>
                                            <strong>Rep:</strong> Many drivers do. The difference is whether it actually helps when something happens—can you pull the right clip fast, and does it help avoid repeat issues?<br><br>
                                            <strong>Prospect:</strong> Getting clips is annoying.<br><br>
                                            <strong>Rep:</strong> Got it. If I can show you a setup that makes clips easy to access and share, can we do a quick 10–15 minute call to see if it fits what you want?<br><br>
                                            <strong>Prospect:</strong> Maybe.<br><br>
                                            <strong>Rep:</strong> Great—what’s a better time, later today or tomorrow?<br><br>
                                            <em>If they push back on price:</em><br>
                                            <strong>Prospect:</strong> Sounds expensive.<br><br>
                                            <strong>Rep:</strong> I hear you. Most people justify it with avoided headaches—faster proof when something happens and fewer repeat incidents. On a short call we can see if it’s even worth it for your situation.
                                        </div>
                                    </div>
                                </div>

                                <!-- ================== EU PITCHES ================== -->
                                <div id="eu-pitches" class="eu-script-content hidden">
                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">1) General (Safety + Evidence)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax is an AI-powered video telematics solution that helps fleets prevent incidents and resolve claims faster. We combine reliable in-vehicle cameras with edge AI and a cloud platform so your team can quickly find the right video, understand what happened, and coach drivers consistently—turning every event into a repeatable safety improvement.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">2) Claims & Risk (Insurance / Litigation)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax helps fleets reduce risk by making video evidence easy to capture, retrieve, and share. When an incident happens, your team can pull the right clip fast, reduce disputes, and strengthen your position in claims. Over time, the same event data supports better coaching and fewer repeat incidents—so you lower exposure without adding operational overhead.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">3) Operations-Focused (Efficiency + Downtime)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax improves fleet operations by turning video and AI into actionable workflows. Instead of chasing footage, your safety and ops teams get a structured process to identify risk, review incidents quickly, and reduce preventable downtime—especially from repeat events and minor collisions. It’s safety technology designed to be used every day, not just after accidents.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">4) Driver Coaching (Behavior Change)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax helps safety managers run a coaching program that actually sticks. We detect risk with edge AI, capture the right moments on video, and make it simple to turn events into coaching conversations. The result is more consistent coaching, fewer repeat behaviors, and a measurable improvement in safety culture across the fleet.
                                        </div>
                                    </div>

                                    <div class="script-box" style="border-left-color: #A0AEC0;">
                                        <div class="script-header"><span class="script-tag" style="color: #A0AEC0;">5) "Not the cheapest" (TCO + Adoption)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                                        <div class="script-text">
                                            Streamax isn’t built to be the cheapest camera—it’s built to deliver outcomes. Cheaper systems become expensive when video is hard to access, alerts are noisy, or the platform creates extra work. Streamax focuses on reliability, evidence quality, and adoption—so your team can act fast when it matters and improve safety over time with a lower total cost of ownership.
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>

                </div>
            </div>
            
            <div style="height: 50px;"></div>
        </div>"""
