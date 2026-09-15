"""
Authentication and Session Manager for CivicEase AI.
"""
from typing import Optional
import streamlit as st

from database.database import db
from database.models import UserRecord
from utils.logging import get_logger

logger = get_logger(__name__)


def init_session_state():
    """Initialize default keys in Streamlit session state."""
    defaults = {
        "authenticated": False,
        "user": None,
        "selected_mode": None,  # 'citizen' or 'auditor'
        "current_document": None,
        "current_analysis": None,
        "analysis_in_progress": False,
        "selected_language": "English",  # 'English' or 'Tamil'
        "active_tab": "Overview",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def login_user(username: str, password: str) -> bool:
    """Attempt user login and set session."""
    user = db.authenticate_user(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        # Set default mode based on user's registered role, but user can always change it
        st.session_state.selected_mode = "auditor" if user.role == "auditor" else "citizen"
        logger.info("User logged in successfully: %s (Role: %s)", username, user.role)
        return True
    return False


def logout_user():
    """Clear session authentication state."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.selected_mode = None
    st.session_state.current_document = None
    st.session_state.current_analysis = None
    st.session_state.analysis_in_progress = False


def get_current_user() -> Optional[UserRecord]:
    """Retrieve current logged in user."""
    return st.session_state.get("user")


def is_authenticated() -> bool:
    """Check if session is currently authenticated."""
    return bool(st.session_state.get("authenticated", False))


def set_mode(mode: str):
    """Update active mode ('citizen' or 'auditor')."""
    if mode in ["citizen", "auditor"]:
        st.session_state.selected_mode = mode
        logger.info("Mode changed to: %s", mode)
