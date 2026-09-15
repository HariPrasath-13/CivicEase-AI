"""
Login and User Registration View for CivicEase AI.
"""
import streamlit as st

from auth.authentication import login_user
from database.database import db
from ui.components import render_header
from utils.logging import get_logger

logger = get_logger(__name__)


def render_login_view():
    """Renders the authentication screen."""
    render_header()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <h3 style="color: #1E3A8A; margin-bottom: 4px;">Welcome to CivicEase AI</h3>
            <p style="color: #64748B; font-size: 14px;">Sign in to analyze and simplify public service documentation.</p>
        </div> 
        
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register New Account"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="e.g. citizen or auditor")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submitted:
                    if not username.strip() or not password.strip():
                        st.error("Please enter both username and password.")
                    else:
                        success = login_user(username.strip(), password.strip())
                        if success:
                            st.success("Authentication successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Use demo accounts below or register.")

            # Quick Demo Access Buttons
            st.markdown("<hr style='margin: 18px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; margin-bottom: 8px;'>Instant Demo Login (1-Click):</p>", unsafe_allow_html=True)
            
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                if st.button("👤 Citizen Demo", use_container_width=True):
                    login_user("citizen", "citizen123")
                    st.rerun()
            with dcol2:
                if st.button("🏛 Auditor Demo", use_container_width=True):
                    login_user("auditor", "auditor123")
                    st.rerun()

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username", placeholder="e.g. john_doe")
                new_name = st.text_input("Full Name", placeholder="e.g. John Doe")
                new_role = st.selectbox("Select Account Role", ["citizen", "auditor"], format_func=lambda x: "Citizen (Public User)" if x == "citizen" else "Government Auditor (Compliance)")
                new_pass = st.text_input("Create Password", type="password")
                reg_submit = st.form_submit_button("Create Account", use_container_width=True)

                if reg_submit:
                    if not new_user.strip() or not new_pass.strip() or not new_name.strip():
                        st.error("All fields are required.")
                    else:
                        created = db.register_user(new_user, new_pass, new_name, new_role)
                        if created:
                            st.success("Account created successfully! Signing you in...")
                            login_user(new_user, new_pass)
                            st.rerun()
                        else:
                            st.error("Username already exists. Please pick a different one.")
