import streamlit as st
import pandas as pd
import smtplib
import ssl
import time
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid

DEFAULT_BODY = """Hi {first_name},

I hope this email finds you well. I noticed that {company} is doing some incredible work lately.

As someone working as a {role}, I thought you might be interested in how our new tools can help streamline your daily operations. We've helped similar teams increase their efficiency by over 20%.

Would you be open to a brief 10-minute chat next week?

Best regards,"""

DISCLAIMER_HTML = (
    '<div style="margin-top: 25px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-family: Arial, sans-serif; font-size: 10px; color: #64748b; line-height: 1.4; text-align: justify;">'
    '<strong>Email Disclaimer:</strong> This e-mail is intended only for the person or entity to which it is addressed and may contain confidential and/or privileged material. Any review, retransmission, dissemination or other use of, or taking of any action in reliance upon, the information in this e-mail by persons or entities other than the intended recipient is prohibited and may be unlawful. If you received this e-mail in error, please contact the sender and delete it from any computer.'
    '</div>'
)

def get_signature_html(sig_id, data):
    if sig_id == "Minimalist Professional":
        html = (
            '<div style="font-family: Arial, sans-serif; color: #333; margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px;">'
            f'<p style="margin: 0; font-weight: bold; font-size: 14px; color: #000000;">{data["name"]}</p>'
            f'<p style="margin: 0; font-size: 12px; color: #666;">{data["title"]} | <a href="{data["website"]}" style="color: #666; text-decoration: none;">{data["company"]}</a></p>'
            f'<p style="margin: 0; font-size: 12px; color: #0066cc;">{data["email"]} | {data["phone"]}</p>'
            '</div>'
        )
        return html + DISCLAIMER_HTML
    elif sig_id == "Creative with Avatar":
        html = (
            '<div style="font-family: \'Helvetica Neue\', Helvetica, Arial, sans-serif; margin-top: 20px; display: flex; align-items: center; gap: 15px;">'
            f'<img src="{data["avatarUrl"]}" alt="Avatar" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #e2e8f0;" />'
            '<div>'
            f'<p style="margin: 0; font-weight: 600; font-size: 15px; color: #1e293b;">{data["name"]}</p>'
            f'<p style="margin: 2px 0; font-size: 13px; color: #64748b;">{data["title"]}</p>'
            f'<p style="margin: 2px 0; font-size: 13px; color: #3b82f6;">{data["email"]} <span style="color: #94a3b8;">|</span> <span style="color: #64748b;">{data["phone"]}</span></p>'
            f'<a href="{data["website"]}" style="margin: 0; font-size: 13px; color: #3b82f6; text-decoration: none;">{data["company"]}</a>'
            '</div></div>'
        )
        return html + DISCLAIMER_HTML
    else: # Corporate with Logo
        html = (
            '<div style="font-family: Arial, sans-serif; margin-top: 25px;">'
            f'<p style="margin: 0; font-weight: bold; font-size: 14px; color: #0f172a;">{data["name"]}</p>'
            f'<p style="margin: 2px 0 5px 0; font-size: 12px; color: #475569;">{data["title"]}</p>'
            f'<p style="margin: 0; font-size: 12px; color: #2AF598;"><strong><a href="{data["website"]}" style="color: #2AF598; text-decoration: none;">{data["company"]}</a></strong></p>'
            f'<p style="margin: 4px 0 12px 0; font-size: 12px; color: #475569;"><a href="mailto:{data["email"]}" style="color: #2AF598; text-decoration: none;">{data["email"]}</a> | {data["phone"]}</p>'
            f'<img src="{data["logoUrl"]}" alt="Company Logo" style="height: 45px; border-radius: 4px;" />'
            '</div>'
        )
        return html + DISCLAIMER_HTML

def render_template(template_str, row):
    def replace_var(match):
        key = match.group(1).lower().strip()
        val = row.get(key, "")
        return str(val) if pd.notna(val) and val != "" else f"[{match.group(1)}]"
    return re.sub(r'\{([^}]+)\}', replace_var, template_str)

def create_message(subject, html_body, to_addr, from_name, from_email):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    return msg

def render_dripmailer():
    # Initialize defaults
    if 'sig_name' not in st.session_state: st.session_state['sig_name'] = "Jack Yi"
    if 'sig_title' not in st.session_state: st.session_state['sig_title'] = "Sales Director"
    if 'sig_company' not in st.session_state: st.session_state['sig_company'] = "Streamax Technology"
    if 'sig_phone' not in st.session_state: st.session_state['sig_phone'] = "(555) 123-4567"
    if 'sig_website' not in st.session_state: st.session_state['sig_website'] = "https://www.streamax.com"
    if 'sig_avatar' not in st.session_state: st.session_state['sig_avatar'] = "https://images.unsplash.com/photo-1531831108325-7fe9616bc780?auto=format&fit=crop&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.1.0&q=60&w=3000"
    if 'sig_logo' not in st.session_state: st.session_state['sig_logo'] = "https://mail.streamax.com/coremail/s?func=lp:getImg&org_id=&img_id=logo_001"
    if 'sig_layout' not in st.session_state: st.session_state['sig_layout'] = "Creative with Avatar"

    # Minimal structural CSS to ensure Streamlit native elements blend perfectly with the toolkit
    st.markdown(
        """
        <style>
            /* Apply Streamax Theme to default buttons in this module */
            [data-testid="stButton"] button {
                background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%) !important;
                color: #050810 !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 8px;
            }
            [data-testid="stButton"] button:hover {
                box-shadow: 0 0 15px rgba(42, 245, 152, 0.4);
                transform: translateY(-2px);
            }
            /* Native Streamlit horizontal tabs styling */
            .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
            .stTabs [data-baseweb="tab"] { color: #A0AEC0; font-weight: 600; font-size: 1.05rem; }
            .stTabs [aria-selected="true"] { color: #2AF598 !important; border-bottom-color: #2AF598 !important; border-bottom-width: 2px !important; }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown("""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 25px; margin-bottom: 30px; text-align: center; backdrop-filter: blur(10px);">
            <h2 style="margin:0; font-size: 2rem;"><span style="background: linear-gradient(135deg, #2AF598 0%, #009EFD 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Drip Mailer</span> Tool</h2>
            <p style="color: #A0AEC0; margin-top: 5px;">Build your signature, draft dynamic templates, and securely dispatch batched emails directly from your Streamax account.</p>
        </div>
    """, unsafe_allow_html=True)

    sig_data = {
        "name": st.session_state['sig_name'],
        "title": st.session_state['sig_title'],
        "company": st.session_state['sig_company'],
        "phone": st.session_state['sig_phone'],
        "email": st.session_state.get('user_email', 'your.email@streamax.com'),
        "website": st.session_state['sig_website'],
        "avatarUrl": st.session_state['sig_avatar'],
        "logoUrl": st.session_state['sig_logo']
    }
    selected_sig_html = get_signature_html(st.session_state['sig_layout'], sig_data)

    # 3 Horizontal workflow tabs
    tab_sig, tab_compose, tab_send = st.tabs(["1. Signatures", "2. Compose", "3. Data & Send"])

    # --- SECTION 1: SIGNATURES ---
    with tab_sig:
        st.write("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.text_input("Full Name", key="sig_name")
            st.text_input("Job Title", key="sig_title")
            st.text_input("Company Name", key="sig_company")
            st.text_input("Phone", key="sig_phone")
            st.text_input("Website", key="sig_website")
            st.text_input("Avatar URL", key="sig_avatar")
            st.text_input("Logo URL", key="sig_logo")
            st.caption(f"Authenticated Sender: **{st.session_state.get('user_email', '')}**")

        with col2:
            st.radio("Select Layout", ["Minimalist Professional", "Creative with Avatar", "Corporate with Logo"], key="sig_layout", horizontal=True)
            st.markdown("<div style='background: white; padding: 25px; border-radius: 8px; border: 1px solid #cbd5e1; color: black; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2); margin-top: 15px;'>" + selected_sig_html + "</div>", unsafe_allow_html=True)

    # --- SECTION 2: COMPOSE ---
    with tab_compose:
        st.write("<br>", unsafe_allow_html=True)
        with st.expander("💡 Where do these variables come from?"):
            st.markdown("""
            **Variable Reference Guide:**
            * `{first_name}`, `{last_name}`, `{company}`, `{role}`: These are obtained directly from the **CSV file** you upload in the *Data & Sending* tab.
            * `{your_name}`: This is obtained dynamically from the **Full Name** input in the *Signatures* tab.
            """)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            subject_template = st.text_input("Subject Line", "Streamlining Operations at {company}")
            body_template = st.text_area("Email Body", DEFAULT_BODY, height=350)
        with col2:
            st.caption("Live HTML Preview (Sample Data)")
            sample_row = {
                "first_name": "John", 
                "company": "Acme Corp", 
                "role": "Manager",
                "your_name": st.session_state['sig_name']
            }
            
            rendered_subject = render_template(subject_template, sample_row)
            rendered_body_html = render_template(body_template, sample_row).replace('\n', '<br>')
            
            preview_html = (
                '<div style="background-color: #ffffff; color: #1e293b; padding: 24px; border-radius: 8px; border: 1px solid #cbd5e1; font-family: Arial, sans-serif; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);">'
                '<div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 20px;">'
                '<span style="color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;">Subject:</span>'
                f'<span style="color: #0f172a; font-size: 15px; font-weight: bold; margin-left: 8px;">{rendered_subject}</span>'
                '</div>'
                '<div style="font-size: 14px; line-height: 1.6; color: #334155;">'
                f'{rendered_body_html}'
                '<br><br>'
                f'{selected_sig_html}'
                '</div></div>'
            )
            st.markdown(preview_html, unsafe_allow_html=True)

    # --- SECTION 3: DATA & SEND ---
    with tab_send:
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("<h4>📝 Lead List Template</h4>", unsafe_allow_html=True)
        st.write("Ensure your contacts are formatted correctly before uploading below.")
        
        template_df = pd.DataFrame([{
            "Email": "example@streamax.com",
            "First_Name": "John",
            "Last_Name": "Doe",
            "Company": "Streamax",
            "Role": "Sales Manager"
        }])
        st.dataframe(template_df, hide_index=True, use_container_width=True)
        
        CSV_TEMPLATE = "Email,First_Name,Last_Name,Company,Role\nexample@streamax.com,John,Doe,Streamax,Sales Manager\n"
        st.download_button("Download leadList.csv", data=CSV_TEMPLATE, file_name="leadList.csv", mime="text/csv")
        
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1); margin-bottom: 25px;'><br>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload your completed leadList.csv", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                df.columns = [str(c).lower().strip() for c in df.columns]
                required = ['first_name', 'last_name', 'email', 'role', 'company']
                missing = [r for r in required if r not in df.columns]
                
                if missing:
                    st.error(f"Missing required columns: {', '.join(missing)}")
                else:
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    auth_mode = st.session_state.get('auth_mode', 'Success')
                    
                    # MASTER OVERRIDE SECURITY CHECK
                    if auth_mode != "Success":
                        st.warning(f"⚠️ You are in **{auth_mode} Override Mode**. Due to missing real credentials, the SMTP email sending functionality is intentionally disabled.")
                        st.button("🚀 INITIATE BATCH SEND", disabled=True)
                    else:
                        if st.button("🚀 INITIATE BATCH SEND"):
                            progress_bar = st.progress(0)
                            log_container = st.empty()
                            logs = []
                            
                            try:
                                context = ssl.create_default_context()
                                server = smtplib.SMTP_SSL("mail.streamax.com", 465, timeout=30, context=context)
                                server.login(st.session_state['user_email'], st.session_state['user_password'])
                                
                                total = len(df)
                                for index, row in df.iterrows():
                                    row_dict = row.to_dict()
                                    row_dict["your_name"] = st.session_state['sig_name']
                                    
                                    target_email = row_dict.get('email')
                                    if pd.isna(target_email):
                                        continue
                                    
                                    rendered_subj = render_template(subject_template, row_dict)
                                    rendered_body = render_template(body_template, row_dict)
                                    html_content = rendered_body.replace('\n', '<br>') + f"<br><br>{selected_sig_html}"
                                    
                                    msg = create_message(rendered_subj, html_content, target_email, st.session_state['sig_name'], st.session_state['user_email'])
                                    
                                    try:
                                        server.send_message(msg)
                                        logs.append(f"✅ [{time.strftime('%X')}] Sent successfully to {target_email}")
                                    except Exception as e:
                                        logs.append(f"❌ [{time.strftime('%X')}] Failed to send to {target_email}: {str(e)}")
                                    
                                    progress_bar.progress((index + 1) / total)
                                    log_container.code('\n'.join(logs[-10:]), language='text')
                                    time.sleep(0.5)
                                    
                                server.quit()
                                st.success("Batch Processing Complete!")
                                
                            except Exception as e:
                                st.error(f"SMTP Connection Error: {str(e)}")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
