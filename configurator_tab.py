"""Sales Configurator tab — launch card for the vendored Streamax Sales
Configurator (a separate project by Kevin Wang, served at /configurator).

The configurator itself is ~7 MB of static HTML/JS/assets copied into
./configurator by sync_configurator.sh. This module only provides the toolkit
tab that introduces and links to it, and credits its author.
"""

content = r"""        <!-- SECTION: SALES CONFIGURATOR -->
        <div id="configurator" class="content-section hidden">
            <div class="card fade-up">
                <h2 class="gradient-text">Streamax Sales Configurator</h2>
                <p>A guided, step-by-step way to build a complete solution &mdash; host, cameras,
                   cables, storage, display and accessories &mdash; around the customer's real
                   installation conditions, then export the material list for quotation.</p>
                <p style="color: var(--text-grey); font-size: 0.9rem; margin-top: 12px;">
                    <i class="fa-solid fa-user-pen" style="margin-right: 8px; color: var(--primary-green);"></i>
                    Built and maintained by <strong style="color: var(--text-white);">Kevin Wang</strong>
                    (<a href="mailto:kevinwang@streamax.com" style="color: var(--secondary-blue);">kevinwang@streamax.com</a>).
                    Send product-rule corrections, missing SKUs and feedback directly to Kevin.
                </p>
            </div>

            <div class="card fade-up" style="text-align: center; padding: 50px 20px;">
                <i class="fa-solid fa-sliders" style="font-size: 3.5rem; color: var(--primary-green); margin-bottom: 20px; filter: drop-shadow(0 0 15px rgba(42, 245, 152, 0.3));"></i>
                <h3 style="font-size: 1.8rem; margin-bottom: 15px; color: var(--text-white);">Build a solution</h3>
                <p style="color: var(--text-grey); max-width: 620px; margin: 0 auto 28px auto; line-height: 1.6;">
                    Pick the product line, answer the installation questions, and the configurator
                    applies the compatibility rules for you &mdash; camera and interface limits,
                    algorithm and recording-channel capacity, and the adapter or extension cables a
                    selection requires.
                </p>
                <a href="/configurator/" target="_blank" rel="noopener" style="display: inline-flex; align-items: center; gap: 10px; background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%); color: #050810; font-weight: 700; font-size: 1.05rem; padding: 14px 32px; border-radius: 30px; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 10px 20px rgba(42, 245, 152, 0.2);">
                    Open Sales Configurator <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 fade-up">
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                    <div style="color: var(--primary-green); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-list-check"></i></div>
                    <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Rules applied for you</h4>
                    <p style="font-size: 0.9rem; color: var(--text-grey);">Interface and camera limits, algorithm capacity, recording channels, and the supporting cables a configuration needs &mdash; checked as you go instead of after the quote.</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                    <div style="color: var(--secondary-blue); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-file-excel"></i></div>
                    <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Exports a material list</h4>
                    <p style="font-size: 0.9rem; color: var(--text-grey);">Produces the approved Excel format, ready for quotation and order follow-up &mdash; no manual re-typing from the sales list.</p>
                </div>
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 16px;">
                    <div style="color: var(--primary-green); font-size: 1.5rem; margin-bottom: 15px;"><i class="fa-solid fa-triangle-exclamation"></i></div>
                    <h4 style="color: var(--text-white); margin-bottom: 10px; font-size: 1.1rem;">Still verify before ordering</h4>
                    <p style="font-size: 0.9rem; color: var(--text-grey);">It reduces routine selection risk, it does not replace technical validation. Check the export against the latest sellable catalog, Salesforce SKUs and the vehicle's real install conditions.</p>
                </div>
            </div>
        </div>
"""
