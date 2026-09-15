"""
Reusable UI Components and Styling for CivicEase AI.
Provides clean public-service styling, cards, status badges, and comparison diffs.
"""
from typing import Any, Dict, List, Optional
import streamlit as st


def inject_custom_css():
    """Injects modern, professional public-service theme styling."""
    st.markdown("""
    <style>
        /* Import Public Sans / Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Top Header & Branding */
        .civic-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #0F766E 100%);
            color: #FFFFFF;
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(30, 58, 138, 0.15);
        }
        .civic-header h1 {
            color: #FFFFFF !important;
            font-size: 26px;
            font-weight: 700;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }
        .civic-header p {
            color: #E0F2FE;
            font-size: 14px;
            margin: 0;
            opacity: 0.95;
        }

        /* Mode Selection Cards */
        .mode-card {
            background: #FFFFFF;
            border: 2px solid #E2E8F0;
            border-radius: 14px;
            padding: 24px;
            text-align: center;
            transition: all 0.25s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            height: 100%;
        }
        .mode-card:hover {
            border-color: #2563EB;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12);
        }
        .mode-card.active {
            border-color: #2563EB;
            background: #F8FAFC;
        }
        .mode-icon {
            font-size: 38px;
            margin-bottom: 12px;
        }
        .mode-title {
            font-size: 19px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 8px;
        }
        .mode-desc {
            font-size: 14px;
            color: #475569;
            line-height: 1.5;
            margin-bottom: 16px;
        }

        /* Metric Cards */
        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
            margin-bottom: 12px;
        }
        .metric-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #0F172A;
        }

        /* Score Display Widget */
        .score-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
            margin-bottom: 20px;
        }
        .score-circle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .score-tier-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.02em;
        }

        /* Issue Card */
        .issue-card {
            background: #FFFFFF;
            border-left: 4px solid #F59E0B;
            border-top: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }
        .issue-card.high {
            border-left-color: #EF4444;
        }
        .issue-card.medium {
            border-left-color: #F59E0B;
        }
        .issue-card.low {
            border-left-color: #3B82F6;
        }
        .issue-title {
            font-size: 15px;
            font-weight: 600;
            color: #1E293B;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .issue-meta {
            font-size: 12px;
            color: #64748B;
            margin-top: 2px;
            margin-bottom: 8px;
        }
        .issue-excerpt {
            background: #F8FAFC;
            border-left: 2px solid #CBD5E1;
            padding: 8px 12px;
            font-size: 13px;
            color: #334155;
            border-radius: 4px;
            margin-bottom: 8px;
            font-style: italic;
        }
        .issue-recommendation {
            font-size: 13px;
            color: #0F766E;
            font-weight: 500;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-high { background: #FEE2E2; color: #991B1B; }
        .badge-medium { background: #FEF3C7; color: #92400E; }
        .badge-low { background: #EFF6FF; color: #1E40AF; }
        .badge-found { background: #DCFCE7; color: #166534; }
        .badge-missing { background: #FEE2E2; color: #991B1B; }
        .badge-partial { background: #FEF3C7; color: #92400E; }
        .badge-ambiguous { background: #FFEDD5; color: #9A3412; }

        /* Comparison Diff Box */
        .diff-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .diff-before {
            background: #FFF1F2;
            border-left: 3px solid #E11D48;
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            color: #881337;
            margin-bottom: 12px;
        }
        .diff-after {
            background: #F0FDF4;
            border-left: 3px solid #16A34A;
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            color: #14532D;
        }

        /* Disclaimer */
        .disclaimer-text {
            font-size: 11px;
            color: #94A3B8;
            text-align: center;
            margin-top: 18px;
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header(user_name: Optional[str] = None, current_mode: Optional[str] = None):
    """Renders application top banner."""
    mode_text = ""
    if current_mode == "citizen":
        mode_text = " • 👤 Citizen Mode"
    elif current_mode == "auditor":
        mode_text = " • 🏛 Government Auditor Mode"

    st.markdown(f"""
    <div class="civic-header">
        <h1>CivicEase AI</h1>
        <p>Government Information Accessibility Analyzer{mode_text}</p>
    </div>
    """, unsafe_allow_html=True)


def render_score_card(composite_score: float, tier_label: str, tier_color: str, tier_desc: str):
    """Renders composite score gauge card."""
    bg_color = f"{tier_color}18"
    st.markdown(f"""
    <div class="score-box">
        <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; margin-bottom: 12px;">
            CivicEase AI Composite Accessibility Score
        </div>
        <div class="score-circle" style="background: {bg_color}; color: {tier_color}; border: 3px solid {tier_color};">
            {int(composite_score)}
        </div>
        <div>
            <span class="score-tier-badge" style="background: {bg_color}; color: {tier_color};">
                {tier_label} ( {composite_score} / 100 )
            </span>
        </div>
        <p style="font-size: 13px; color: #64748B; margin-top: 10px; margin-bottom: 0;">
            {tier_desc}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_completeness_table(fields: List[Dict[str, Any]]):
    """Renders 7-field information completeness matrix."""
    for field in fields:
        status = field.get("status", "MISSING")
        badge_cls = f"badge-{status.lower()}"
        icon = field.get("badge_icon", "")
        name = field.get("display_name", "")
        details = field.get("details", "")

        col1, col2 = st.columns([1, 2.5])
        with col1:
            st.markdown(f"**{icon} {name}**")
            st.markdown(f"<span class='badge {badge_cls}'>{status}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='font-size:13px; color:#334155;'>{details}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)
