content = r"""        <!-- SECTION: PRESENTATION -->
        <div id="presentation" class="content-section hidden">
            
            <div class="card fade-up">
                <h2 class="gradient-text">Streamax Closed-Loop Trucking Solution</h2>
                <h5 style="color: var(--text-grey); margin-top: 5px;">Sales Presentation Script & Visuals</h5>
            </div>

            <!-- Subsection 3.1 Intro -->
            <h3 class="section-header fade-up">1. Introduction & Vision</h3>
            
            <!-- SOLUTION OVERVIEW VISUAL RECONSTRUCTION -->
            <div class="solution-visual fade-up">
                <div class="solution-title">Solution Overview</div>
                
                <div class="solution-main-pill">
                    The Streamax Fleet Management Solution
                </div>

                <div class="solution-pillars">
                    <div class="solution-pill">Video Telematics</div>
                    <div class="solution-plus">+</div>
                    <div class="solution-pill">Asset Security</div>
                    <div class="solution-plus">+</div>
                    <div class="solution-pill">Driver Visibility</div>
                </div>

                <div class="solution-cards">
                    <!-- Card 1 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card">
                            <div class="sc-illus-1">
                                <i class="fa-solid fa-id-badge badge"></i>
                                <i class="fa-solid fa-truck blue-truck"></i>
                                <i class="fa-solid fa-user-tie driver"></i>
                            </div>
                        </div>
                        <div class="solution-card-label">Driver Behavioral Risk</div>
                    </div>
                    
                    <!-- Card 2 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card">
                            <div class="sc-illus-2">
                                <div class="truck-wrapper">
                                    <div class="trailer"></div>
                                    <div class="cab"></div>
                                    <div class="wheel w1"></div>
                                    <div class="wheel w2"></div>
                                    <div class="wheel w3"></div>
                                </div>
                                <i class="fa-solid fa-person-walking thief1"></i>
                                <i class="fa-solid fa-box box-icon"></i>
                                <i class="fa-solid fa-person-walking thief2"></i>
                            </div>
                        </div>
                        <div class="solution-card-label">Asset & Cargo Security Risk</div>
                    </div>

                    <!-- Card 3 -->
                    <div class="solution-card-wrapper">
                        <div class="solution-card" style="background: #475569; padding: 0;">
                            <div class="sc-illus-3">
                                <div class="road-line rl-1"></div>
                                <div class="road-line rl-2"></div>
                                <div class="road-line rl-3"></div>
                                <div class="road-line rl-4"></div>
                                
                                <div class="bs-cone bs-side-top"></div>
                                <div class="bs-cone bs-side-bottom"></div>
                                <div class="bs-cone bs-front"></div>
                                
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="top: 25px; right: 70px;"></i>
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="bottom: 25px; right: 70px;"></i>
                                <i class="fa-solid fa-triangle-exclamation warning-icon" style="top: 50%; right: 10px; transform: translateY(-50%);"></i>

                                <div class="truck-body">
                                    <div class="truck-cab"></div>
                                </div>
                            </div>
                        </div>
                        <div class="solution-card-label">Driver Visibility Risk</div>
                    </div>
                </div>
            </div>

            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Speaker Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "Good morning/afternoon everyone. Thank you for the time.<br><br>
                        Today, I want to show you how Streamax is redefining fleet operations. We aren’t just selling cameras or sensors; our mission is to be the best technology partner for your entire operation.<br><br>
                        We know the challenges you face: stitching together different vendors for video, telematics, and AI is painful. Our goal is to solve that by connecting your devices, data, and workflows into one seamless system. We focus on three pillars:<br><br>
                        • <strong>Video Telematics & Safety:</strong> Trustworthy evidence and risk detection.<br><br>
                        • <strong>Asset & Cargo Security:</strong> Protecting your load in motion and at rest.<br><br>
                        • <strong>Visibility & Compliance:</strong> Giving you total situational awareness.<br><br>
                        "But the best way to understand this is to walk through the lifecycle of a single trip—our 'Closed-Loop' journey."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.2 The Loop -->
            <h3 class="section-header blue fade-up">2. The Closed-Loop Journey</h3>

            <!-- VISUAL LOOP CONTAINER -->
            <div class="loop-visual-wrapper fade-up">
                <div class="scene-container" id="scene">
                    <div class="center-logo-area">
                        <h1>STREAMAX</h1>
                        <p>Fleet Management<br>Solution</p>
                    </div>
                    <!-- SVG Orbit -->
                    <svg class="orbit-svg" id="orbitSvg" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <path id="roadBase" class="road-base" />
                        <path id="roadLane" class="road-lane" />
                    </svg>
                    <!-- Nodes injected by JS -->
                    <div id="nodes-layer"></div>
                    <!-- Labels injected by JS -->
                    <div id="labels-layer"></div>
                    <!-- Running Element -->
                    <div id="running-element"><i class="fa-solid fa-truck-fast"></i></div>
                </div>
            </div>
            
            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Full Journey Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "We believe value shouldn't just happen on the road. It starts before the key turns and continues after the engine stops. Let's look at the ten critical touchpoints."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 1: Before Departure</strong><br><br>
                        • <strong>Step 1: Compliance:</strong> "It starts here. Before a driver even approaches the vehicle, our system ensures you are meeting regional safety mandates—whether that’s specific blind-spot hardware requirements or DVS standards. We automate compliance so you don't have to worry about it."<br><br>
                        • <strong>Step 2: Driver ID:</strong> "Next, who is driving? We move beyond simple keys. We use <strong>Multi-Factor Verification</strong>—RFID badges, facial recognition, or even palm-vein scanning—to confirm the right driver is in the right asset. We can also integrate <strong>alcohol detection</strong> here to ensure fitness for duty before the engine starts."<br><br>
                        • <strong>Step 3: Cargo Loading:</strong> "This is a game-changer. Using our <strong>Z5 Intelligent Cargo Solution</strong>, we don't just 'transport air.' We measure <strong>cargo occupancy and volume</strong> automatically to help you maximize load efficiency. We also monitor the loading process itself, identifying bottlenecks or mishandling that could delay your schedule."<br><br>
                        • <strong>Step 4: Vehicle Status:</strong> "Before we roll, we check the health of the machine. Through deep <strong>CAN bus integration</strong> across thousands of makes and models, we give fleet managers a clear, real-time picture of ignition status, fuel levels, door sensors, and diagnostic trouble codes."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 2: Shipping (On the Road)</strong><br><br>
                        • <strong>Step 5: Starting:</strong> "As the vehicle moves off, risk spikes. Our <strong>Front Blind Spot Monitoring</strong> immediately activates to detect pedestrians or obstacles in that critical danger zone right in front of the cab, preventing low-speed tragedies."<br><br>
                        • <strong>Step 6: Driving:</strong> "On the open road, our <strong>ADAS and DSM (Driver Status Monitoring)</strong> systems are constantly vigilant. We detect fatigue, distraction, phone usage, and tailgating in real-time. But we don't just record it; we alert the driver instantly so they can self-correct <em>before</em> an incident happens."<br><br>
                        • <strong>Step 7: Turning:</strong> "Turns are a major liability. Our <strong>Side Blind Spot Detection</strong> works with the turn signal to alert the driver if a cyclist or pedestrian is in the danger zone, providing that extra pair of eyes when it matters most."<br><br>
                        • <strong>Step 8: Parking:</strong> "Cargo theft often happens when the vehicle is stopped. Our <strong>Sentinel Protection</strong> system guards the fuel and cargo during rest stops. It uses tamper detection and AI to send instant notifications if unauthorized access is attempted while the driver is sleeping or away."<br><br>

                        <strong style="color: var(--secondary-blue);">Phase 3: Arrival & Improvement</strong><br><br>
                        • <strong>Step 9: Arriving & Unloading:</strong> "When the truck arrives, our Z5 camera verifies the unloading process, ensuring proof of delivery and efficiency. We provide rear and side visibility assistance to make docking safe and precise."<br><br>
                        • <strong>Step 10: Coaching:</strong> "Finally, the trip ends, but the value continues. We close the loop with <strong>Analytics and Coaching</strong>. We take all the data captured—the near-misses, the distraction alerts—and turn them into targeted coaching sessions. This allows you to correct unsafe habits and document improvement over time."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.3 Process of Accident Prevention -->
            <h3 class="section-header fade-up">3. Process of Accident Prevention</h3>
            
            <div class="prevention-visual fade-up">
                <div class="prevention-title">The Process of Accident Prevention</div>
                
                <div class="timeline-container">
                    <div class="timeline-line"></div>
                    
                    <!-- Step 1 -->
                    <div class="timeline-step">
                        <div class="step-percent">10%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">Longterm</div>
                        <div class="step-card-header">Driver<br>Coaching</div>
                        <div class="step-card-body border-blue">
                            <ul>
                                <li>Utilizing driver behavior data to conduct targeted coaching to reduce driving risk in the long term</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 2 -->
                    <div class="timeline-step">
                        <div class="step-percent">20%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">30 Minutes</div>
                        <div class="step-card-header">Realtime<br>Intervention</div>
                        <div class="step-card-body border-orange">
                            <ul>
                                <li>Identify significant cognitive capability decline before the driver falls asleep and providing a window of intervention</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 3 -->
                    <div class="timeline-step">
                        <div class="step-percent">10%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">2 Seconds</div>
                        <div class="step-card-header">Realtime<br>Alerting</div>
                        <div class="step-card-body border-orange">
                            <ul>
                                <li>Identify critical risk with edge AI and provide real time alert to the driver to prevent accidents</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Step 4 -->
                    <div class="timeline-step">
                        <div class="step-percent">20%</div>
                        <div class="step-dot"></div>
                        <div class="step-time">1 Second</div>
                        <div class="step-card-header">Automatic<br>Emergency Braking</div>
                        <div class="step-card-body border-yellow">
                            <ul>
                                <li>Activate vehicle brake on behalf of driver in imminent collision risk to prevent accidents</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (Slide: The Process of Accident Prevention)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Now that we've walked through the entire closed-loop journey of a vehicle, let's zoom in on the core goal: how we actually prevent accidents within that loop. This slide shows how accident prevention works across different time horizons, and why relying on just one safety feature isn't enough.<br><br>
                        Starting from the left, <strong>long-term driver coaching</strong> is about sustainable behavior change. It addresses about <strong>10%</strong> of prevention by using driver behavior data to run targeted coaching, reduce repeat risky habits, and lower risk over weeks and months.<br><br>
                        Next is a much shorter window: <strong>30 minutes — real-time intervention</strong>, around <strong>20%</strong>. This is where the system detects early signs of cognitive decline—like fatigue patterns—before a driver actually falls asleep, and creates a window where the fleet or the driver can intervene proactively.<br><br>
                        Then we move into the moment that matters most on the road: <strong>2 seconds — real-time alerting</strong>, about <strong>10%</strong>. Here, edge AI identifies critical risk and gives the driver an immediate alert, aiming to prevent the incident before it happens.<br><br>
                        Finally, the last line of defense is the shortest: <strong>1 second — automatic emergency braking</strong>, around <strong>20%</strong>. This is when the vehicle activates braking on behalf of the driver during imminent collision risk to prevent or reduce impact.<br><br>
                        So the key takeaway is this: <strong>accident prevention is a layered process</strong>. Coaching reduces long-term risk, intervention catches early warning signs, alerting prevents immediate hazards, and emergency braking is the last safeguard when time is nearly zero. To make this closed loop a reality, let's look at the specific Streamax hardware and software solutions that power each of these defensive layers.
                    </div>
                </div>
            </div>

            <!-- Subsection 3.4 Product Solution Details -->
            <h3 class="section-header fade-up">4. Product Solution Details</h3>
            
            <!-- Pillar 1 -->
            <div class="card fade-up">
                <h4 style="color: var(--primary-green); margin-bottom: 15px;">Pillar 1: Video Telematics (AD Plus 2.0, AD Max, C6 Lite 2.0, GT1 Pro + DC Max)</h4>
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me start with <strong>Video Telematics</strong>.<br><br>
                        The problem we solve is simple: when something happens on the road, fleets need two things immediately—<strong>the truth</strong> and <strong>a repeatable way to prevent it from happening again</strong>.<br>
                        Streamax video telematics is designed to <strong>capture the right evidence</strong>, <strong>surface the right risk signals</strong>, and <strong>turn events into coaching actions</strong>.<br><br>
                        Here’s the loop we illustrate:<br>
                        • <strong>Prevent:</strong> Edge AI detects risky behaviors and critical road events in real time.<br>
                        • <strong>Protect:</strong> Video evidence is recorded reliably so disputes and claims can be resolved faster.<br>
                        • <strong>Improve:</strong> Events feed coaching and continuous improvement so safety performance gets better over time.<br><br>
                        Product-wise, we offer a clear lineup depending on the fleet’s needs:<br><br>
                        <strong>AD Plus 2.0</strong> is our "bread-and-butter" solution for fleets that want high-confidence video telematics with a clean, practical workflow. With <strong>1080p dual lenses</strong>, <strong>integrated onboard memory</strong>, and <strong>eSIM</strong>, it is built to deploy at scale and be used daily by safety and operations teams.<br><br>
                        <strong>AD Max</strong> is for fleets that need more performance: more advanced AI capability, more demanding environments, and more intensity in risk management. The message is simple: when the customer cares about accuracy, responsiveness, and scale, <strong>AD Max is the premium choice</strong>.<br><br>
                        <strong>C6 Lite 2.0</strong> is for fleets that want a balance between AI capability and price. We push engineering to the edge to deliver core ADAS and DSC functions while keeping the solution more economical and video-ready.<br><br>
                        <strong>GT1 Pro + DC Max</strong> is a powerful upgrade path for fleets moving from telematics to video. You start with a capable telematics gateway with dead-reckoning. When you want video and edge AI, you add DC Max on top to extend the gateway into a video telematics solution with minimal disruption.<br><br>
                        Choosing Streamax means you are not choosing the cheapest, and we honor that choice with a clear philosophy: we optimize for <strong>outcomes and total cost of ownership</strong>.<br>
                        Cheap systems become expensive when they miss critical events, create noisy false alerts, or add operational overhead. Our value is reliability, evidence quality, and workflows that teams actually adopt.<br><br>
                        So the close is straightforward: if your priority is <strong>reducing incidents</strong>, <strong>winning claims with evidence</strong>, and <strong>running coaching consistently</strong>, this pillar is your foundation.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "We’re not selling cameras; we’re selling a safety and evidence workflow that scales."<br>
                        • "The best video system is the one your team can use in 30 seconds when an incident happens."<br>
                        • "Total cost of ownership matters more than sticker price in fleet safety."
                    </div>
                </div>
            </div>

            <!-- Pillar 2 -->
            <div class="card fade-up">
                <h4 style="color: var(--secondary-blue); margin-bottom: 15px;">Pillar 2: Asset Security (Z5, Sentinel)</h4>
                <div class="script-box" style="border-left-color: var(--primary-green);">
                    <div class="script-header"><span class="script-tag" style="color: var(--primary-green);">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me talk about <strong>Asset Security</strong>.<br><br>
                        Video telematics reduces liability on the road. Asset security protects your <strong>vehicle, cargo, and business continuity</strong> when assets are parked, unattended, or operating in higher-risk scenarios.<br><br>
                        The loop we use for security is:<br>
                        • <strong>Detect:</strong> Identify abnormal behavior and high-risk situations early.<br>
                        • <strong>Deter:</strong> Make it harder for theft and tampering to succeed.<br>
                        • <strong>Respond:</strong> Provide evidence and visibility so teams can act faster and reduce loss.<br><br>
                        Here is how we position the two products:<br><br>
                        <strong>Z5</strong> is the practical, scalable solution for fleets that want stronger cargo protection and improved cargo efficiency. Its proprietary AI spatial detection supports better cargo load awareness and helps reduce operational delays. With <strong>low-light capability</strong>, Z5 can detect and alert on unauthorized cargo-area access, even in challenging lighting.<br><br>
                        <strong>Sentinel</strong> is our premium, industry-dedicated, always-on guardian. With <strong>AOV camera technology</strong>, Sentinel can continue operating for up to <strong>90 days after ignition-off</strong>. It uses <strong>gesture learning and detection</strong> to wake only when real risk is present. The positioning is simple: it guards valuable assets day and night and notifies you when actual threats are taking place.<br><br>
                        When the buyer asks about ROI, security is one of the clearest paybacks:<br>
                        • One prevented theft incident can offset a meaningful portion of the program cost.<br>
                        • Faster response and better evidence reduce downstream losses and disputes.<br>
                        • Less operational chaos means fewer hidden costs.<br><br>
                        And importantly, asset security integrates naturally with your broader fleet workflow: consistent evidence, consistent operations, and a clear path to scale.<br><br>
                        So if your priority is <strong>protecting vehicles and cargo</strong>, <strong>reducing loss</strong>, and <strong>responding faster when risk appears</strong>, this pillar is built for that job.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "Safety reduces liability; security reduces loss."<br>
                        • "Security fails when response is slow; we shorten the time from detection to action."<br>
                        • "One prevented theft can justify the program."
                    </div>
                </div>
            </div>

            <!-- Pillar 3 -->
            <div class="card fade-up">
                <h4 style="color: var(--primary-green); margin-bottom: 15px;">Pillar 3: Visibility Assistance (BSD, 360 AVM)</h4>
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Read-off Script (2–3 minutes)</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        Let me introduce <strong>Visibility Assistance</strong>.<br><br>
                        Even good drivers get into trouble when visibility is limited—blind spots, tight yards, complex turns, loading zones, and crowded urban routes. Visibility assistance is about <strong>preventing accidents before they become incidents</strong>, especially the low-speed but high-frequency events that cost fleets time, money, and reputation.<br><br>
                        Here is the loop for visibility products:<br>
                        • <strong>See:</strong> Expand the driver’s awareness in real time.<br>
                        • <strong>Avoid:</strong> Reduce collisions caused by blind spots and low-visibility maneuvers.<br>
                        • <strong>Verify:</strong> Keep a consistent record for incident review and coaching.<br><br>
                        We package this pillar around two solutions:<br><br>
                        <strong>BSD</strong>—Blind Spot Detection—is the clean story for preventing side-impact collisions and lane-change incidents. The simplest way to say it is: <strong>help the driver recognize what they cannot see</strong>, in the moments that matter most.<br><br>
                        <strong>360 AVM</strong>—360 Around View Monitoring—is full situational awareness for tight operations like yards, loading docks, urban stops, and complex vehicles. We use it to <strong>reduce low-speed collisions</strong> and help drivers maneuver with more confidence.<br><br>
                        This pillar also strengthens adoption because it delivers value immediately to drivers:<br>
                        • Drivers feel safer and more supported.<br>
                        • Operations see fewer minor collisions and less downtime.<br>
                        • Safety teams get better context for coaching.<br><br>
                        And it connects back to the broader Streamax value: a consistent workflow and a consistent evidence chain.<br><br>
                        So if your priority is <strong>reducing blind-spot risk</strong>, <strong>cutting low-speed collisions</strong>, and <strong>improving driver confidence</strong>, this pillar is designed to deliver that impact.<br><br>
                        <strong>Optional One-Liners (for Q&A)</strong><br>
                        • "Most accidents are visibility problems before they are driving problems."<br>
                        • "A lot of cost comes from small collisions; 360 visibility reduces those repeatable losses."<br>
                        • "Drivers adopt what helps them immediately."
                    </div>
                </div>
            </div>

            <!-- Subsection 3.5 ROI -->
            <h3 class="section-header blue fade-up">5. The Results (ROI)</h3>
            <div class="card fade-up">
                <div class="script-box">
                    <div class="script-header"><span class="script-tag">Speaker Script</span><button class="copy-btn" onclick="copyText(this)"><i data-lucide="copy"></i> Copy</button></div>
                    <div class="script-text">
                        "So, what does this technology actually deliver? It delivers results.<br><br>
                        By layering these technologies—coaching, cognitive risk indicators, edge-AI alerts, and active assistance—our customers typically see up to a <strong>60% reduction in preventable incidents</strong>.<br><br>
                        Every fleet is different, but when you put detection, assistance, and coaching into one closed loop, the safety gains are consistent, and they stick."
                    </div>
                </div>
            </div>

        </div>"""
