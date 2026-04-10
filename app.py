import errno
import os

import io

import json
import hashlib

import re

import tempfile
import zipfile
import xml.etree.ElementTree as ET
import base64 as _b64
import smtplib

import subprocess

import platform

import ipaddress

import textwrap
import urllib.parse
from datetime import datetime, timezone
from email.message import EmailMessage

from html import escape as html_escape

from typing import Any
from collections import defaultdict


import pandas as pd  # type: ignore[import-untyped]

import streamlit as st  # type: ignore[import-untyped]

import streamlit.components.v1 as components  # type: ignore[import-untyped]
from ui_helpers import render_health_section_intro
from overview_helpers import (
    render_overview_chart_card,
    render_overview_header,
    render_overview_metric_cards,
    render_overview_section_kicker,
    render_overview_table_header,
    render_overview_theme,
)
from sidebar_theme import build_sidebar_theme_css
try:
    from st_aggrid import (  # type: ignore[import-untyped]
        AgGrid,
        ColumnsAutoSizeMode,
        DataReturnMode,
        GridOptionsBuilder,
        GridUpdateMode,
    )
except Exception:
    AgGrid = None  # type: ignore[assignment]
    ColumnsAutoSizeMode = None  # type: ignore[assignment]
    DataReturnMode = None  # type: ignore[assignment]
    GridOptionsBuilder = None  # type: ignore[assignment]
    GridUpdateMode = None  # type: ignore[assignment]
from streamlit import config as st_config  # type: ignore[import-untyped]
from camera_installation_builder import render_builder as render_camera_installation_builder

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore[assignment,misc]



def render_html(markup: str) -> None:

    cleaned_markup = textwrap.dedent(markup).strip()
    if hasattr(st, "html"):
        st.html(cleaned_markup)
        return
    st.markdown(cleaned_markup, unsafe_allow_html=True)


def render_sidebar_html(markup: str) -> None:

    cleaned_markup = textwrap.dedent(markup).strip()
    st.sidebar.markdown(cleaned_markup, unsafe_allow_html=True)


def render_sidebar_section_label(text: str) -> None:
    render_sidebar_html(f'<div class="sidebar-section-label">{html_escape(text)}</div>')


def render_sidebar_muted_copy(text: str) -> None:
    render_sidebar_html(f'<div class="sidebar-muted-copy">{html_escape(text)}</div>')


_WORKSPACE_BRAND: dict[str, tuple[str, str]] = {
    "Health Status": ("Health Status", "Enterprise Monitoring"),
    "Ticket Related": ("Ticket Dashboard", "Communications Hub"),
    "Project Related": ("Project Builder", "Expanding Security"),
}

_WORKSPACE_BRAND_ICON: dict[str, str] = {
    "Health Status": """
        <svg viewBox="0 0 24 24" aria-hidden="true" width="24" height="24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.5 12h4l1.6-2.7 2.2 5.2 1.7-3.1h5"></path>
            <path d="M5.5 7.5h13a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2Z"></path>
        </svg>
    """,
    "Ticket Related": """
        <svg viewBox="0 0 24 24" aria-hidden="true" width="24" height="24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 6.5h10a2 2 0 0 1 2 2v3a1.5 1.5 0 0 0 0 3v3a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-3a1.5 1.5 0 0 0 0-3v-3a2 2 0 0 1 2-2Z"></path>
            <path d="M9.25 10h5.5"></path>
            <path d="M9.25 14h3.5"></path>
        </svg>
    """,
    "Project Related": """
        <svg viewBox="0 0 24 24" aria-hidden="true" width="24" height="24" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 5.5 18.5 9.5"></path>
            <path d="M6 18l2.75-.55L18.5 7.7a1.4 1.4 0 0 0 0-1.95l-.25-.25a1.4 1.4 0 0 0-1.95 0L6.55 15.25 6 18Z"></path>
            <path d="M9.25 8.5h3"></path>
            <path d="M8 11.5h4.5"></path>
        </svg>
    """,
}


def render_sidebar_brand_card(workspace: str = "Health Status") -> None:
    title, subtitle = _WORKSPACE_BRAND.get(workspace, ("Health Status", "Enterprise Monitoring"))
    icon_markup = " ".join(_WORKSPACE_BRAND_ICON.get(workspace, _WORKSPACE_BRAND_ICON["Health Status"]).split())
    with st.sidebar.container():
        icon_col, text_col = st.columns([0.95, 2.8], gap="small")
        with icon_col:
            st.markdown(
                (
                    "<div style='width:50px;height:50px;border-radius:13px;"
                    "display:flex;align-items:center;justify-content:center;"
                    "background:linear-gradient(180deg,#357E9B,#2E708B);"
                    "box-shadow:0 6px 14px rgba(53,126,155,0.16);"
                    "margin-top:2px;'>"
                    f"{icon_markup}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
        with text_col:
            st.markdown(
                (
                    "<div style='padding-top:2px;margin-left:-8px;'>"
                    f"<div style='color:#2F738E;font-family:Inter,\"Segoe UI\",\"Helvetica Neue\",Arial,sans-serif;"
                    "font-size:22px;font-weight:800;letter-spacing:-0.03em;line-height:1.0;margin:0;'>"
                    f"{html_escape(title)}</div>"
                    f"<div style='color:#54616B;font-family:Inter,\"Segoe UI\",\"Helvetica Neue\",Arial,sans-serif;"
                    "font-size:13px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;"
                    "line-height:1.1;margin-top:10px;white-space:nowrap;'>"
                    f"{html_escape(subtitle)}</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


# Use a dome camera favicon; the animated sweep variant is injected below.
_favicon = "\U0001F4F9"



st.set_page_config(page_title="LSU Camera Health Tool", layout="wide", page_icon=_favicon)


# Theme styling uses one shared palette for now to keep the chrome consistent.
active_theme: dict[str, str] = {
    "primary": "#357E9B",
    "background": "#F1F3F4",
    "secondary_bg": "#E7ECEF",
    "text": "#40484D",
    "app_bg": "#F1F3F4",
    "app_bg_soft": "#E7ECEF",
    "surface": "#ffffff",
    "surface_2": "#FBFCFC",
    "surface_3": "#E9EEF1",
    "cell_shell": "#DCE4E8",
    "cell": "#ffffff",
    "cell_alt": "#F6F8F9",
    "cell_hover": "#EDF2F5",
    "cell_header": "#D8E1E6",
    "border": "rgba(101, 122, 132, 0.18)",
    "border_strong": "rgba(101, 122, 132, 0.34)",
    "text_main": "#40484D",
    "text_muted": "#657A84",
    "accent": "#357E9B",
    "accent_strong": "#2E6D86",
    "accent_soft": "#E5F2F7",
    "accent_soft_2": "#EFF6FA",
    "accent_text": "#2D6176",
    "accent_hover": "#264F61",
    "focus_ring": "rgba(53, 126, 155, 0.14)",
    "focus_border": "rgba(53, 126, 155, 0.38)",
    "sidebar_bg_top": "#F4F6F7",
    "sidebar_bg_bottom": "#E8EDF0",
    "sidebar_hover": "#EEF3F5",
    "sidebar_selected": "#E2E8EC",
    "sidebar_button_top": "#ffffff",
    "sidebar_button_bottom": "#F5F8F9",
    "sidebar_button_border": "rgba(101, 122, 132, 0.18)",
    "sidebar_button_text": "#40484D",
    "sidebar_button_hover_top": "#ffffff",
    "sidebar_button_hover_bottom": "#EEF3F5",
    "sidebar_text": "#40484D",
    "sidebar_text_muted": "#657A84",
    "sidebar_accent": "#657A84",
    "sidebar_accent_strong": "#4B5E67",
    "sidebar_panel_top": "#ffffff",
    "sidebar_panel_bottom": "#F8FAFB",
    "sidebar_panel_border": "rgba(101, 122, 132, 0.18)",
    "sidebar_shadow": "rgba(15, 23, 42, 0.06)",
    "sidebar_shadow_strong": "rgba(15, 23, 42, 0.10)",
    "sidebar_overlay_top": "rgba(255, 255, 255, 0.20)",
    "sidebar_overlay_bottom": "rgba(241, 243, 244, 0.14)",
    "header_bg": "#F1F3F4",
    "placeholder": "#8D9AA2",
    "tab_shadow": "#5E779E",
    "scrollbar": "#B7C5CD",
    "scrollbar_hover": "#657A84",
    "banner_line_start": "#AFC9D6",
    "banner_line_mid": "#357E9B",
    "banner_line_end": "#B8C2DE",
}
theme_dark_mode = True

theme_config = {
    "theme.base": "light",
    "theme.primaryColor": active_theme["primary"],
    "theme.backgroundColor": active_theme["background"],
    "theme.secondaryBackgroundColor": active_theme["secondary_bg"],
    "theme.textColor": active_theme["text"],
}

for _theme_key, _theme_value in theme_config.items():

    st_config.set_option(_theme_key, _theme_value)



# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ LSU Purple & Gold Theme ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

# Legacy LSU theme CSS retained for reference only. Current live styling is defined below.
_LEGACY_THEME_CSS = """

<style>

:root {
    --app-bg: #f6f8f4;
    --app-bg-soft: #eef4ec;
    --surface-1: #ffffff;
    --surface-2: #f1f6f1;
    --surface-3: #e7efe8;
    --border-soft: rgba(87, 119, 95, 0.14);
    --border-strong: rgba(87, 119, 95, 0.24);
    --text-main: #24362b;
    --text-muted: #627467;
    --text-soft: #56695c;
    --accent: #4f7a5b;
    --accent-soft: rgba(79, 122, 91, 0.14);
    --success: #4f8f67;
    --warning: #c2a15b;
    --danger: #c96d6d;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top right, rgba(79, 122, 91, 0.05), transparent 24%), linear-gradient(180deg, #f6f8f4 0%, #f2f6f0 100%);
}

[data-testid="stMain"] {
    background: transparent;
}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Sidebar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */




/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Top header bar (page title area) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

header[data-testid="stHeader"] {
    background: rgba(246, 248, 244, 0.94);
    border-bottom: 1px solid var(--border-soft);
    backdrop-filter: blur(12px);
}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ All text ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

html, body, [class*="css"] {
    color: var(--text-main);
}

h1, h2, h3 {
    color: #24362b !important;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    letter-spacing: -0.02em;
    font-weight: 700;
}

p, label, div, span {
    color: var(--text-soft);
}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Title ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stTitle"] {

    color: #24362b !important;

    font-size: 1.55rem !important;

    border-bottom: none !important;

    padding-bottom: 0 !important;

    margin-bottom: 0.28rem !important;

}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Metrics ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--surface-1), var(--surface-2));
    border: 1px solid var(--border-soft);
    border-radius: 14px;
    padding: 0.85rem 0.95rem !important;
    min-width: 0;
    overflow: hidden;
    box-shadow: none !important;
}

[data-testid="stMetricLabel"] > div {
    color: var(--text-muted) !important;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

[data-testid="stMetricValue"] > div {
    color: #f8fbff !important;
    font-size: clamp(1rem, 2vw, 1.45rem) !important;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

[data-testid="stMain"] .stButton > button {
    background: var(--surface-2) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease !important;
    box-shadow: none !important;
}

[data-testid="stMain"] .stButton > button:hover {
    background: var(--surface-3) !important;
    color: #ffffff !important;
    border-color: var(--border-strong) !important;
    transform: none !important;
    box-shadow: none !important;
}

[data-testid="stMain"] .stButton > button:hover * {
    color: #ffffff !important;
}

[data-testid="stMain"] input[type="text"],
[data-testid="stMain"] textarea,
[data-testid="stMain"] [data-baseweb="select"] > div,
[data-testid="stMain"] [data-baseweb="input"] > div {
    background-color: var(--surface-2) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

[data-testid="stMain"] input[type="text"]:focus,
[data-testid="stMain"] textarea:focus {
    border-color: rgba(124, 140, 255, 0.45) !important;
    box-shadow: 0 0 0 1px rgba(124, 140, 255, 0.25) !important;
}

[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: rgba(124, 140, 255, 0.14) !important;
    color: #dbe4ff !important;
    font-weight: 600;
    border: 1px solid rgba(124, 140, 255, 0.2) !important;
    border-radius: 999px !important;
}

[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #dbe4ff !important;
    fill: #dbe4ff !important;
}

[data-testid="stCheckbox"] label {
    color: var(--text-main) !important;
}

[data-testid="stDataFrame"] > div {
    border: 1px solid var(--border-soft);
    border-radius: 14px;
    overflow: hidden;
    background: var(--surface-1);
}

[data-testid="stDataFrame"] th {
    background-color: #1b222b !important;
    color: #dbe3ee !important;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    border-bottom: 1px solid var(--border-soft) !important;
}

[data-testid="stDataFrame"] tr:nth-child(even) {
    background-color: rgba(255,255,255,0.015) !important;
}

[data-testid="stDataFrame"] tr:hover {
    background-color: rgba(124, 140, 255, 0.08) !important;
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
}

div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background-color: rgba(63, 179, 127, 0.12) !important;
    border-left: 3px solid var(--success) !important;
}

div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
    background-color: rgba(212, 106, 106, 0.12) !important;
    border-left: 3px solid var(--danger) !important;
}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Expanders ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stExpander"] {

    background-color: #f7faf7 !important;

    border: 1px solid rgba(109, 145, 116, 0.16) !important;

    border-radius: 10px !important;

}

[data-testid="stExpander"] summary {

    color: #355340 !important;

    font-weight: 600;

}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Subheaders (st.subheader) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stHeading"] h2,

[data-testid="stHeading"] h3 {

    color: #274232 !important;

    border-left: none !important;

    padding-left: 0 !important;

}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Caption text ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stCaptionContainer"] {

    color: #c0a8f0 !important;

}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ File uploader ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

[data-testid="stFileUploader"] {

    background-color: #2D1259 !important;

    border: 2px dashed rgba(84, 124, 93, 0.28) !important;

    border-radius: 8px !important;

}

[data-testid="stFileUploader"]:hover {

    border-color: rgba(98, 143, 108, 0.38) !important;

}



/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Scrollbar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */

::-webkit-scrollbar { width: 8px; height: 8px; }

::-webkit-scrollbar-track { background: #edf4eb; }

::-webkit-scrollbar-thumb { background: #97b39d; border-radius: 4px; }

::-webkit-scrollbar-thumb:hover { background: #5d8667; }

</style>

"""


# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ LSU branded page header (tiger eye logo) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

_tiger_eye_path = os.path.join(os.path.dirname(__file__), "data", "tiger_eye.png")

try:

    with open(_tiger_eye_path, "rb") as _f:

        _tiger_b64 = _b64.b64encode(_f.read()).decode()

    _logo_html = f'<img src="data:image/png;base64,{_tiger_b64}" style="height:44px;width:44px;object-fit:cover;border-radius:4px;border:1px solid rgba(84,124,93,0.38);">'

except Exception:

    _logo_html = '<span style="font-size:1.6rem;">\U0001F42F</span>'  # fallback



render_html(
    """
    <style>
    .app-top-spacer {
        height: 0.25rem;
    }
    header[data-testid="stHeader"] [data-testid="stStatusWidget"],
    header[data-testid="stHeader"] [aria-label*="running" i],
    header[data-testid="stHeader"] [title*="running" i] {
        display: none !important;
    }
    .app-busy-indicator {
        position: fixed;
        top: 0.72rem;
        right: 10.5rem;
        z-index: 9999;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.68rem;
        border-radius: 999px;
        border: 1px solid var(--app-green-border);
        background: rgba(243, 244, 239, 0.96);
        color: var(--app-green-accent-text);
        box-shadow: 0 8px 18px rgba(53, 126, 155, 0.08);
        opacity: 0;
        transform: translateY(-6px);
        pointer-events: none;
        transition: opacity 140ms ease, transform 140ms ease;
        backdrop-filter: blur(10px);
    }
    .app-busy-indicator.is-busy {
        opacity: 1;
        transform: translateY(0);
    }
    .app-busy-indicator-camera {
        width: 1.15rem;
        height: 1.15rem;
        flex: 0 0 auto;
    }
    .app-busy-indicator-camera .cam-body {
        fill: var(--app-green-accent-strong);
    }
    .app-busy-indicator-camera .cam-cap,
    .app-busy-indicator-camera .cam-mount,
    .app-busy-indicator-camera .cam-arm {
        fill: var(--app-green-accent);
    }
    .app-busy-indicator-camera .cam-window {
        fill: var(--app-green-accent-soft);
    }
    .app-busy-indicator-camera .cam-lens {
        fill: var(--app-green-text);
        transform-box: fill-box;
        transform-origin: center;
        animation: app-camera-sweep 1s ease-in-out infinite;
    }
    .app-busy-indicator-label {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }
    @keyframes app-camera-sweep {
        0% { transform: translateX(-2.6px); }
        25% { transform: translateX(0); }
        50% { transform: translateX(2.6px); }
        75% { transform: translateX(0); }
        100% { transform: translateX(-2.6px); }
    }
    @media (max-width: 1100px) {
        .app-busy-indicator {
            right: 8rem;
            top: 0.68rem;
        }
    }
    </style>
    <div class="app-top-spacer"></div>
    <div class="app-busy-indicator" id="app-busy-indicator" aria-hidden="true">
        <svg class="app-busy-indicator-camera" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
            <rect class="cam-mount" x="28" y="7" width="8" height="8" rx="2"/>
            <rect class="cam-arm" x="22" y="13" width="20" height="6" rx="3"/>
            <rect class="cam-cap" x="16" y="18" width="32" height="8" rx="4"/>
            <path class="cam-body" d="M14 26 C14 17, 50 17, 50 26 L46 39 C44.8 43.4 40.8 46.5 36.2 46.5 H27.8 C23.2 46.5 19.2 43.4 18 39 Z"/>
            <ellipse class="cam-window" cx="32" cy="35.5" rx="11.5" ry="7.2"/>
            <circle class="cam-lens" cx="32" cy="35.5" r="4.3"/>
        </svg>
        <span class="app-busy-indicator-label">Working</span>
    </div>
    <script>
    (() => {
        const frameSvg = (pupilX) => `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
                <rect width="64" height="64" rx="14" fill="#f4f7fc"/>
                <rect x="28" y="8" width="8" height="7" rx="2" fill="#31476f"/>
                <rect x="22" y="13" width="20" height="6" rx="3" fill="#31476f"/>
                <rect x="16" y="18" width="32" height="8" rx="4" fill="#60779d"/>
                <path d="M14 26 C14 17, 50 17, 50 26 L46 39 C44.8 43.4 40.8 46.5 36.2 46.5 H27.8 C23.2 46.5 19.2 43.4 18 39 Z" fill="#1d2b46"/>
                <ellipse cx="32" cy="35.5" rx="11.5" ry="7.2" fill="#eaf0f7"/>
                <circle cx="${pupilX}" cy="35.5" r="4.2" fill="#223047"/>
            </svg>
        `;

        const frames = [27, 32, 37, 32].map((x) => `data:image/svg+xml,${encodeURIComponent(frameSvg(x))}`);
        const idleIcon = frames[1];
        let frameIndex = 0;
        let timer = null;
        let quietUntil = 0;
        let busyHideTimer = null;

        const ensureFavicon = () => {
            let link = document.querySelector('link[rel="icon"]');
            if (!link) {
                link = document.createElement('link');
                link.rel = 'icon';
                document.head.appendChild(link);
            }
            return link;
        };

        const setIcon = (href) => {
            ensureFavicon().setAttribute('href', href);
        };

        const busyIndicator = () => document.getElementById('app-busy-indicator');

        const setBusyVisible = (visible) => {
            const el = busyIndicator();
            if (!el) {
                return;
            }
            el.classList.toggle('is-busy', visible);
        };

        const hasActiveIndicators = () => {
            return Boolean(
                document.querySelector('[data-testid="stSpinner"]') ||
                document.querySelector('[aria-label*="running" i]') ||
                document.querySelector('[title*="running" i]') ||
                document.querySelector('button[title*="Stop" i]')
            );
        };

        const stopAnimation = () => {
            if (timer) {
                clearInterval(timer);
                timer = null;
            }
            if (busyHideTimer) {
                clearTimeout(busyHideTimer);
                busyHideTimer = null;
            }
            setBusyVisible(false);
            setIcon(idleIcon);
        };

        const tick = () => {
            if (Date.now() > quietUntil && !hasActiveIndicators()) {
                stopAnimation();
                return;
            }
            frameIndex = (frameIndex + 1) % frames.length;
            setIcon(frames[frameIndex]);
        };

        const startAnimation = (durationMs = 1800) => {
            quietUntil = Math.max(quietUntil, Date.now() + durationMs);
            setBusyVisible(true);
            if (busyHideTimer) {
                clearTimeout(busyHideTimer);
            }
            busyHideTimer = window.setTimeout(() => {
                if (!hasActiveIndicators() && Date.now() >= quietUntil) {
                    setBusyVisible(false);
                }
            }, durationMs + 80);
            if (timer) {
                return;
            }
            setIcon(frames[frameIndex]);
            timer = window.setInterval(tick, 180);
        };

        setIcon(idleIcon);
        startAnimation(1200);

        const observer = new MutationObserver((mutations) => {
            const meaningfulChange = mutations.some((mutation) => mutation.addedNodes.length || mutation.removedNodes.length);
            if (meaningfulChange) {
                startAnimation(1400);
            }
        });

        const boot = () => {
            observer.observe(document.body, { childList: true, subtree: true });
            document.addEventListener('click', (event) => {
                if (event.target instanceof Element && event.target.closest('button, [role="button"], input, textarea, select')) {
                    startAnimation(2200);
                }
            }, true);
            window.addEventListener('beforeunload', () => startAnimation(4000));
        };

        if (document.body) {
            boot();
        } else {
            window.addEventListener('DOMContentLoaded', boot, { once: true });
        }
    })();
    </script>
    """
)


if not theme_dark_mode:

    st.markdown("""

    <style>

    [data-testid="stAppViewContainer"],

    [data-testid="stMain"] {

        background:

            radial-gradient(circle at top right, rgba(53, 126, 155, 0.12), transparent 30%),

            radial-gradient(circle at top left, rgba(94, 119, 158, 0.18), transparent 26%),

            #f1f3f4 !important;

    }






    header[data-testid="stHeader"] {

        background: rgba(241, 243, 244, 0.96) !important;

        border-bottom: 1px solid rgba(101, 122, 132, 0.2) !important;

    }



    html, body, [class*="css"] {

        color: #40484d !important;

    }

    h1, h2, h3 {

        color: #40484d !important;

    }

    [data-testid="stMain"] p,

    [data-testid="stMain"] label,

    [data-testid="stMain"] .stMarkdown {

        color: #657a84 !important;

    }



    [data-testid="stTitle"] {

        color: #40484d !important;

        border-bottom: 1px solid rgba(101, 122, 132, 0.2) !important;

    }



    [data-testid="stMetric"] {

        background: linear-gradient(180deg, #ffffff, #edf2f5) !important;

        border: 1px solid rgba(101, 122, 132, 0.16) !important;

        box-shadow: 0 8px 18px rgba(53, 126, 155, 0.08), inset 0 0 0 1px rgba(184, 194, 222, 0.2) !important;

    }

    [data-testid="stMetricLabel"] > div {

        color: #657a84 !important;

    }

    [data-testid="stMetricValue"] > div {

        color: #40484d !important;

    }



    [data-testid="stMain"] .stButton > button {

        background: linear-gradient(180deg, #3f89a7, #357e9b) !important;

        color: #f7fbf7 !important;

        border: 1px solid rgba(53, 126, 155, 0.34) !important;

        box-shadow: 0 8px 18px rgba(53, 126, 155, 0.14) !important;

        border-radius: 10px !important;

        min-height: 44px !important;

    }

    [data-testid="stMain"] .stButton > button * {

        color: #f7fbf7 !important;

    }

    [data-testid="stMain"] .stButton > button:hover {

        background: linear-gradient(180deg, #4a90ab, #3f89a7) !important;

        color: #f7fbf7 !important;

        border-color: rgba(53, 126, 155, 0.52) !important;

        box-shadow: 0 10px 22px rgba(53, 126, 155, 0.18) !important;

    }

    [data-testid="stMain"] .stButton > button:hover * {

        color: #f7fbf7 !important;

    }

    [data-testid="stMain"] .stButton > button:focus-visible {

        outline: 3px solid rgba(53, 126, 155, 0.24) !important;

        outline-offset: 2px !important;

    }



    [data-testid="stMain"] input[type="text"],

    [data-testid="stMain"] textarea,

    [data-testid="stSelectbox"] > div > div,

    [data-testid="stMultiSelect"] > div > div {

        background-color: #ffffff !important;

        color: #40484d !important;

        border: 1px solid rgba(101, 122, 132, 0.18) !important;

        box-shadow: 0 0 0 1px rgba(184, 194, 222, 0.18) !important;

    }

    [data-testid="stMain"] input[type="text"]:focus,

    [data-testid="stMain"] textarea:focus {

        border-color: rgba(53, 126, 155, 0.42) !important;

        box-shadow: 0 0 0 3px rgba(53, 126, 155, 0.16) !important;

        animation: none !important;

    }

    div[data-testid="stTextInput"] label p {

        color: #5d6f78 !important;

        font-weight: 700 !important;

        letter-spacing: 0.2px !important;

    }

    div[data-testid="stTextInput"] input {

        min-height: 48px !important;

    }

    div[data-testid="stTextInput"] input::placeholder {

        color: #8d9aa2 !important;

        opacity: 1 !important;

    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {

        background-color: #e5f2f7 !important;

        color: #2d6176 !important;

        border: 1px solid rgba(53, 126, 155, 0.22) !important;

    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {

        color: #2d6176 !important;

        fill: #2d6176 !important;

    }



    [data-testid="stCheckbox"] label {

        color: #40484d !important;

    }



    [data-testid="stDataFrame"] > div {

        border: 1px solid rgba(101, 122, 132, 0.2) !important;

        border-radius: 10px !important;

        background-color: #ffffff !important;

        box-shadow: inset 0 0 0 1px rgba(184, 194, 222, 0.18) !important;

    }

    [data-testid="stDataFrame"] th {

        background-color: #d8e1e6 !important;

        color: #2d6176 !important;

    }

    [data-testid="stDataFrame"] tr:nth-child(even) {

        background-color: rgba(233, 238, 241, 0.75) !important;

    }

    [data-testid="stDataFrame"] tr:hover {

        background-color: rgba(229, 242, 247, 0.88) !important;

    }

    [data-testid="stDataFrame"] canvas {

        filter: invert(1) hue-rotate(180deg) brightness(1.03) contrast(0.96) !important;

    }

    [data-testid="stDataFrame"] input,

    [data-testid="stDataFrame"] textarea {

        background-color: #ffffff !important;

        color: #40484d !important;

        filter: none !important;

    }

    [data-testid="stDataFrame"] [role="toolbar"],

    [data-testid="stDataFrame"] [class*="toolbar"],

    [data-testid="stDataFrame"] [class*="menu"] {

        background: transparent !important;

        border: 0 !important;

        border-radius: 10px !important;

        box-shadow: none !important;

        backdrop-filter: none !important;

    }

    [data-testid="stDataFrame"] [role="toolbar"] > div,

    [data-testid="stDataFrame"] [class*="toolbar"] > div,

    [data-testid="stDataFrame"] [class*="menu"] > div,

    [data-testid="stDataFrame"] [role="toolbar"] > div > div,

    [data-testid="stDataFrame"] [class*="toolbar"] > div > div,

    [data-testid="stDataFrame"] [class*="menu"] > div > div {

        background: transparent !important;

        border: 0 !important;

        box-shadow: none !important;

    }

    [data-testid="stDataFrame"] button,

    [data-testid="stDataFrame"] [role="button"] {

        background: rgba(255, 255, 255, 0.88) !important;

        border: 1px solid rgba(101, 122, 132, 0.16) !important;

        color: #357e9b !important;

        border-radius: 8px !important;

        box-shadow: none !important;

    }

    [data-testid="stDataFrame"] button:hover,

    [data-testid="stDataFrame"] [role="button"]:hover {

        background: rgba(229, 242, 247, 0.98) !important;

        border-color: rgba(53, 126, 155, 0.42) !important;

        color: #357e9b !important;

        box-shadow: 0 2px 8px rgba(53, 126, 155, 0.08) !important;

    }

    [data-testid="stDataFrame"] button:focus-visible,

    [data-testid="stDataFrame"] [role="button"]:focus-visible {

        outline: 2px solid rgba(53, 126, 155, 0.28) !important;

        outline-offset: 1px !important;

    }

    [data-testid="stDataFrame"] button svg,

    [data-testid="stDataFrame"] [role="button"] svg {

        fill: #357e9b !important;

        stroke: #357e9b !important;

    }



    [data-testid="stAlert"] {

        background-color: rgba(255, 255, 255, 0.92) !important;

        border: 1px solid rgba(101, 122, 132, 0.2) !important;

    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {

        background-color: #e9f4f8 !important;

        border-left: 4px solid #357e9b !important;

    }

    div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {

        background-color: #fdeeee !important;

        border-left: 4px solid #b24a4a !important;

    }



    [data-testid="stExpander"] {

        background-color: rgba(255, 255, 255, 0.92) !important;

        border: 1px solid rgba(101, 122, 132, 0.2) !important;

        box-shadow: inset 0 0 0 1px rgba(184, 194, 222, 0.18) !important;

    }

    [data-testid="stExpander"] summary {

        color: #40484d !important;

        font-weight: 700 !important;

    }

    [data-testid="stExpander"] summary:focus-visible {

        outline: 3px solid rgba(53, 126, 155, 0.24) !important;

        outline-offset: 2px !important;

        border-radius: 6px !important;

    }



    [data-testid="stHeading"] h2,

    [data-testid="stHeading"] h3 {

        color: #40484d !important;

        border-left: 4px solid #5e779e !important;

    }



    [data-testid="stCaptionContainer"] {

        color: #657a84 !important;

    }



    [data-testid="stFileUploader"] {

        background-color: rgba(255, 255, 255, 0.92) !important;

        border: 2px dashed rgba(101, 122, 132, 0.32) !important;

    }

    [data-testid="stFileUploader"] > div,

    [data-testid="stFileUploader"] section,

    [data-testid="stFileUploader"] [class*="uploadDropzone"] {

        background-color: rgba(255, 255, 255, 0.96) !important;

    }

    [data-testid="stFileUploader"] * {

        color: #357e9b !important;

    }

    [data-testid="stFileUploader"] button {

        background: #eef6fa !important;

        border: 1px solid rgba(101, 122, 132, 0.22) !important;

        color: #357e9b !important;

    }

    [data-testid="stFileUploader"] button * {

        color: #357e9b !important;

    }

    [data-testid="stFileUploader"]:hover {

        border-color: rgba(53, 126, 155, 0.36) !important;

    }



    button[data-baseweb="tab"] {

        color: #657a84 !important;

        border: 1px solid rgba(101, 122, 132, 0.18) !important;

        border-bottom: 0 !important;

        background: #ffffff !important;

        border-radius: 10px 10px 0 0 !important;

        padding: 0.58rem 0.9rem !important;

    }

    button[data-baseweb="tab"][aria-selected="true"] {

        color: #40484d !important;

        border-color: rgba(101, 122, 132, 0.24) !important;

        background: #e9f4f8 !important;

        box-shadow: inset 0 -3px 0 #5e779e !important;

    }

    button[data-baseweb="tab"]:focus-visible {

        outline: 3px solid rgba(53, 126, 155, 0.24) !important;

        outline-offset: 2px !important;

    }



    ::-webkit-scrollbar-track { background: #e7ecef !important; }

    ::-webkit-scrollbar-thumb { background: #b7c5cd !important; }

    ::-webkit-scrollbar-thumb:hover { background: #657a84 !important; }



    .lsu-banner-wrapper {

        background: linear-gradient(90deg, #ffffff 0%, #f6f6f2 100%) !important;

        border: 1px solid rgba(101, 122, 132, 0.16) !important;

        box-shadow: 0 4px 14px rgba(64, 72, 77, 0.06), inset 0 0 0 1px rgba(216, 225, 230, 0.45) !important;

    }

    .lsu-banner-wrapper::after {

        background: linear-gradient(90deg, #357e9b 0%, #b8c2de 50%, #357e9b 100%) !important;

    }

    .lsu-banner-title {

        color: #2d6176 !important;

    }

    .lsu-banner-subtitle {

        color: #657a84 !important;

    }

    </style>

    """, unsafe_allow_html=True)

    theme_css_vars = "\n".join(
        [
            f'--app-green-bg: {active_theme["app_bg"]};',
            f'--app-green-bg-soft: {active_theme["app_bg_soft"]};',
            f'--app-green-surface: {active_theme["surface"]};',
            f'--app-green-surface-2: {active_theme["surface_2"]};',
            f'--app-green-surface-3: {active_theme["surface_3"]};',
            f'--app-green-cell-shell: {active_theme["cell_shell"]};',
            f'--app-green-cell: {active_theme["cell"]};',
            f'--app-green-cell-alt: {active_theme["cell_alt"]};',
            f'--app-green-cell-hover: {active_theme["cell_hover"]};',
            f'--app-green-cell-header: {active_theme["cell_header"]};',
            f'--app-green-border: {active_theme["border"]};',
            f'--app-green-border-strong: {active_theme["border_strong"]};',
            f'--app-green-text: {active_theme["text_main"]};',
            f'--app-green-muted: {active_theme["text_muted"]};',
            f'--app-green-accent: {active_theme["accent"]};',
            f'--app-green-accent-strong: {active_theme["accent_strong"]};',
            f'--app-green-accent-soft: {active_theme["accent_soft"]};',
            f'--app-green-hover: {active_theme["accent_soft_2"]};',
            f'--app-green-accent-text: {active_theme["accent_text"]};',
            f'--app-green-accent-hover: {active_theme["accent_hover"]};',
            f'--app-green-focus-ring: {active_theme["focus_ring"]};',
            f'--app-green-focus-border: {active_theme["focus_border"]};',
            f'--app-green-placeholder: {active_theme["placeholder"]};',
            f'--app-green-header-bg: {active_theme["header_bg"]};',
            f'--app-green-tab-shadow: {active_theme["tab_shadow"]};',
            f'--app-green-scrollbar: {active_theme["scrollbar"]};',
            f'--app-green-scrollbar-hover: {active_theme["scrollbar_hover"]};',
            f'--app-green-banner-line-start: {active_theme["banner_line_start"]};',
            f'--app-green-banner-line-mid: {active_theme["banner_line_mid"]};',
            f'--app-green-banner-line-end: {active_theme["banner_line_end"]};',
        ]
    )
    st.markdown(
        """
    <style>
    :root {
    """
        + theme_css_vars
        + """
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background:
            radial-gradient(circle at top right, rgba(84, 110, 122, 0.06), transparent 28%),
            radial-gradient(circle at top left, rgba(232, 239, 245, 0.78), transparent 24%),
            linear-gradient(180deg, var(--app-green-bg) 0%, var(--app-green-bg-soft) 100%) !important;
    }

    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"] {
        background-color: var(--app-green-bg) !important;
    }

    header[data-testid="stHeader"],
    header[data-testid="stHeader"] > div {
        background: var(--app-green-header-bg) !important;
        border-bottom: 1px solid var(--app-green-border-strong) !important;
    }

    header[data-testid="stHeader"] [data-testid="stToolbar"] {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, var(--app-green-banner-line-start) 0%, var(--app-green-banner-line-mid) 50%, var(--app-green-banner-line-end) 100%) !important;
    }

    header[data-testid="stHeader"] [data-testid="stToolbar"] button,
    header[data-testid="stHeader"] [data-testid="stToolbar"] [role="button"] {
        background: linear-gradient(180deg, var(--app-sidebar-panel-top), var(--app-sidebar-panel-bottom)) !important;
        border: 1px solid var(--app-sidebar-panel-border) !important;
        color: var(--app-sidebar-accent-strong) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px var(--app-sidebar-shadow) !important;
    }

    header[data-testid="stHeader"] [data-testid="stToolbar"] button:hover,
    header[data-testid="stHeader"] [data-testid="stToolbar"] [role="button"]:hover {
        background: linear-gradient(180deg, var(--app-sidebar-hover), var(--app-sidebar-selected)) !important;
        border-color: var(--app-sidebar-accent) !important;
        color: var(--app-sidebar-accent-strong) !important;
    }

    header[data-testid="stHeader"] [data-testid="stToolbar"] button svg,
    header[data-testid="stHeader"] [data-testid="stToolbar"] [role="button"] svg {
        fill: var(--app-sidebar-accent-strong) !important;
        stroke: var(--app-sidebar-accent-strong) !important;
    }

    [data-baseweb="popover"] [role="menu"],
    [data-baseweb="popover"] [role="dialog"] {
        background: linear-gradient(180deg, var(--app-sidebar-panel-top), var(--app-sidebar-panel-bottom)) !important;
        border: 1px solid var(--app-sidebar-panel-border) !important;
        box-shadow: 0 14px 28px var(--app-sidebar-shadow-strong) !important;
    }

    [data-baseweb="popover"] [role="menu"] *,
    [data-baseweb="popover"] [role="dialog"] * {
        color: var(--app-sidebar-text) !important;
    }

    [data-baseweb="popover"] [role="menuitem"],
    [data-baseweb="popover"] [role="option"],
    [data-baseweb="popover"] button {
        background: transparent !important;
        color: var(--app-sidebar-text) !important;
    }

    [data-baseweb="popover"] [role="menuitem"]:hover,
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] button:hover {
        background: var(--app-sidebar-hover) !important;
        color: var(--app-sidebar-accent-strong) !important;
    }

    html, body, [class*="css"] {
        color: var(--app-green-text) !important;
    }

    h1, h2, h3,
    [data-testid="stTitle"],
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: var(--app-green-text) !important;
        border-color: var(--app-green-accent) !important;
    }

    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] .stMarkdown,
    [data-testid="stCaptionContainer"],
    .stCaption {
        color: var(--app-green-muted) !important;
    }

    [data-testid="stMain"]:not(:has(.overview-page)) .stButton > button,
    [data-testid="stMainBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button,
    [data-testid="stAppViewBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button,
    .block-container:not(:has(.overview-page)) div[data-testid="stButton"] > button {
        background: linear-gradient(180deg, var(--app-green-surface), var(--app-green-cell-shell)) !important;
        color: var(--app-green-accent-strong) !important;
        border: 1px solid var(--app-green-border-strong) !important;
        box-shadow: 0 4px 10px rgba(53, 126, 155, 0.08) !important;
    }

    [data-testid="stMain"]:not(:has(.overview-page)) .stButton > button *,
    [data-testid="stMainBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button *,
    [data-testid="stAppViewBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button *,
    .block-container:not(:has(.overview-page)) div[data-testid="stButton"] > button * {
        color: var(--app-green-accent-text) !important;
    }

    [data-testid="stMain"]:not(:has(.overview-page)) .stButton > button:hover,
    [data-testid="stMainBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover,
    [data-testid="stAppViewBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover,
    .block-container:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover {
        background: linear-gradient(180deg, var(--app-green-surface-2), var(--app-green-cell-header)) !important;
        color: var(--app-green-accent-hover) !important;
        border-color: var(--app-green-accent) !important;
        box-shadow: 0 6px 16px rgba(53, 126, 155, 0.12) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stMain"]:not(:has(.overview-page)) .stButton > button:hover *,
    [data-testid="stMainBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover *,
    [data-testid="stAppViewBlockContainer"]:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover *,
    .block-container:not(:has(.overview-page)) div[data-testid="stButton"] > button:hover * {
        color: var(--app-green-accent-hover) !important;
    }

    [data-testid="stMain"] .stButton > button:focus-visible,
    div[data-testid="stButton"] > button:focus-visible,
    [data-testid="stExpander"] summary:focus-visible,
    button[data-baseweb="tab"]:focus-visible {
        outline: 2px solid var(--app-green-focus-border) !important;
        outline-offset: 2px !important;
    }

    [data-testid="stMain"] input[type="text"],
    [data-testid="stMain"] textarea,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div,
    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input {
        background: var(--app-green-surface) !important;
        color: var(--app-green-text) !important;
        border: 1px solid var(--app-green-border-strong) !important;
        box-shadow: inset 0 2px 5px rgba(101, 122, 132, 0.04), 0 3px 8px rgba(53, 126, 155, 0.06) !important;
    }

    [data-testid="stMain"] input[type="text"]::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--app-green-placeholder) !important;
    }

    [data-testid="stMain"] input[type="text"]:focus,
    [data-testid="stMain"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--app-green-focus-border) !important;
        box-shadow: 0 0 0 3px var(--app-green-focus-ring) !important;
    }

    div[data-testid="stTextInput"] label p {
        color: var(--app-green-accent-text) !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: var(--app-green-accent-soft) !important;
        color: var(--app-green-accent-text) !important;
        border: 1px solid var(--app-green-border-strong) !important;
    }

    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: var(--app-green-accent-text) !important;
        fill: var(--app-green-accent-text) !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, var(--app-green-surface), var(--app-green-surface-3)) !important;
        border: 1px solid var(--app-green-border) !important;
        box-shadow: 0 10px 24px rgba(74, 92, 79, 0.05) !important;
    }

    [data-testid="stMetricLabel"] > div {
        color: #6a7d6e !important;
    }

    [data-testid="stMetricValue"] > div {
        color: var(--app-green-text) !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        padding: 6px !important;
        border-radius: 14px !important;
        background: linear-gradient(180deg, var(--app-green-cell-shell), #dde3da) !important;
        border: 1px solid rgba(87, 119, 95, 0.22) !important;
        box-shadow: 0 14px 28px rgba(74, 92, 79, 0.08) !important;
    }

    [data-testid="stDataFrame"] > div,
    [data-testid="stDataEditor"] > div {
        background: var(--app-green-cell) !important;
        border: 1px solid rgba(87, 119, 95, 0.20) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    [data-testid="stDataFrame"] th,
    [data-testid="stDataEditor"] th {
        background: linear-gradient(180deg, var(--app-green-accent), var(--app-green-accent-strong)) !important;
        color: #eef6ee !important;
        border-bottom: 1px solid var(--app-green-border-strong) !important;
    }

    [data-testid="stDataFrame"] tr:nth-child(even),
    [data-testid="stDataEditor"] tr:nth-child(even) {
        background: var(--app-green-cell-alt) !important;
    }

    [data-testid="stDataFrame"] tr:hover,
    [data-testid="stDataEditor"] tr:hover {
        background: var(--app-green-cell-hover) !important;
    }

    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] div,
    [data-testid="stDataEditor"] td,
    [data-testid="stDataEditor"] div {
        color: #274231 !important;
    }

    [data-testid="stDataFrame"] td,
    [data-testid="stDataEditor"] td {
        background: transparent !important;
    }

    [data-testid="stDataFrame"] canvas {
        filter: none !important;
    }

    [data-testid="stDataFrame"] button,
    [data-testid="stDataFrame"] [role="button"],
    [data-testid="stDataEditor"] button,
    [data-testid="stDataEditor"] [role="button"] {
        background: #f7faf5 !important;
        color: var(--app-green-accent-text) !important;
        border: 1px solid var(--app-green-border) !important;
        box-shadow: none !important;
    }

    [data-testid="stDataFrame"] button:hover,
    [data-testid="stDataFrame"] [role="button"]:hover,
    [data-testid="stDataEditor"] button:hover,
    [data-testid="stDataEditor"] [role="button"]:hover {
        background: #f1f3ee !important;
        color: var(--app-green-accent-hover) !important;
        border-color: var(--app-green-border-strong) !important;
    }

    [data-testid="stDataFrame"] button svg,
    [data-testid="stDataFrame"] [role="button"] svg,
    [data-testid="stDataEditor"] button svg,
    [data-testid="stDataEditor"] [role="button"] svg {
        fill: var(--app-green-accent-strong) !important;
        stroke: var(--app-green-accent-strong) !important;
    }

    [data-testid="stMain"] [data-testid="stFileUploader"],
    [data-testid="stMain"] [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid var(--app-green-border) !important;
        box-shadow: none !important;
    }

    [data-testid="stMain"] [data-testid="stFileUploader"] > div,
    [data-testid="stMain"] [data-testid="stFileUploader"] section,
    [data-testid="stMain"] [data-testid="stFileUploader"] [class*="uploadDropzone"] {
        background: rgba(255, 255, 255, 0.96) !important;
    }

    [data-testid="stMain"] [data-testid="stFileUploader"] *,
    [data-testid="stMain"] [data-testid="stExpander"] summary {
        color: var(--app-green-text) !important;
    }

    [data-testid="stMain"] [data-testid="stFileUploader"] button {
        background: #f7faf5 !important;
        border: 1px solid var(--app-green-border) !important;
        color: var(--app-green-accent-text) !important;
    }

    [data-testid="stMain"] [data-testid="stFileUploader"]:hover {
        border-color: var(--app-green-border-strong) !important;
    }

    button[data-baseweb="tab"] {
        color: var(--app-green-muted) !important;
        border: 1px solid var(--app-green-border) !important;
        border-bottom: 0 !important;
        background: linear-gradient(180deg, #fafcf9, #eff5ee) !important;
        box-shadow: none !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--app-green-text) !important;
        border-color: var(--app-green-border-strong) !important;
        background: linear-gradient(180deg, #ffffff, #f3f4ef) !important;
        box-shadow: inset 0 -3px 0 var(--app-green-tab-shadow) !important;
    }

    ::-webkit-scrollbar-track {
        background: #f1f3ee !important;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--app-green-scrollbar) !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--app-green-scrollbar-hover) !important;
    }

    .lsu-banner-wrapper {
        background: linear-gradient(90deg, #ffffff 0%, #f3f4ef 100%) !important;
        border: 1px solid var(--app-green-border) !important;
        box-shadow: 0 8px 20px rgba(53, 126, 155, 0.06) !important;
    }

    .lsu-banner-wrapper::after {
        background: linear-gradient(90deg, var(--app-green-banner-line-start) 0%, var(--app-green-banner-line-mid) 50%, var(--app-green-banner-line-end) 100%) !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(build_sidebar_theme_css(active_theme), unsafe_allow_html=True)



DEFAULT_SITE_HEALTH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "LSU Public Safety Surveillance .csv",
)

NOTES_PATH = os.path.join("data", "notes.csv")

TRACKING_PATH = os.path.join("data", "device_tracking.csv")

TICKETS_PATH = os.path.join("data", "tickets.csv")

TRANSITIONS_PATH = os.path.join("data", "state_transitions.csv")

SERVER_ROLE_MAP_PATH = os.path.join("data", "server_roles.csv")

TDX_HELPDESK_EMAIL = "helpdesk@lsu.edu"

RETENTION_POLICY_DAYS = 28





# -----------------------------

# Helpers

# -----------------------------

def normalize_avigilon_headers(df: pd.DataFrame) -> pd.DataFrame:

    """

    Standardizes inconsistent Avigilon CSV headers (e.g. trailing spaces, case changes).

    """

    column_mapping = {

        "device id": "Device ID",

        "mac": "MAC Address",

        "serial": "Serial Number",

        "status": "Status"

    }

    df.columns = [column_mapping.get(c.strip().lower(), c.strip()) for c in df.columns]

    return df





def decode_site_health_csv_bytes(raw_bytes: bytes) -> str:

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):

        try:

            return raw_bytes.decode(encoding)

        except UnicodeDecodeError:

            continue

    return raw_bytes.decode("utf-8", errors="replace")





def parse_site_health_csv_text(csv_text: str) -> pd.DataFrame:

    """

    Avigilon Site Health exports can include metadata lines above the device table.

    Find the actual table header and parse from there.

    """

    lines = csv_text.splitlines()

    header_idx = None

    for i, line in enumerate(lines):

        if "Server Name" in line and "Device Name" in line:

            header_idx = i

            break



    if header_idx is None:

        raise ValueError("Could not find device table header row containing 'Server Name' and 'Device Name'.")



    table_text = "\n".join(lines[header_idx:])

    df = pd.read_csv(io.StringIO(table_text), engine="python", on_bad_lines="skip")

    return normalize_avigilon_headers(df)





def parse_site_health_csv_bytes(raw_bytes: bytes) -> pd.DataFrame:

    return parse_site_health_csv_text(decode_site_health_csv_bytes(raw_bytes))



def generate_ticket_payload(row: pd.Series) -> str:

    """

    Generates a copy-paste ready string for IT ticketing systems.

    Usage: Apply this to selected rows in the dataframe.

    """

    return (

        f"Camera Issue Report:\n"

        f"- Device Name: {row.get('Device Name Base', 'N/A')}\n"

        f"- Location: {row.get('Location', 'N/A')}\n"

        f"- IP: {row.get('IP Address', 'N/A')} | MAC: {row.get('MAC Address', 'N/A')}\n"

        f"- Error: {row.get('Error Flags', 'None')}\n"

        f"- Disposition Notes: {row.get('notes', 'None')}"

    )



@st.cache_data(ttl=600)

def read_site_health_csv(path: str, file_signature: str = "") -> pd.DataFrame:

    """

    Avigilon Site Health export often has a few non-table lines at the top.

    This finds the real header row (containing Server Name + Device Name) and reads from there.

    """

    # file_signature is intentionally unused in function logic.

    # It is part of the cache key so updates to the same file path are picked up promptly.

    _ = file_signature

    with open(path, "rb") as f:

        raw_bytes = f.read()

    return parse_site_health_csv_bytes(raw_bytes)





def get_file_signature(path: str) -> str:

    try:

        stat = os.stat(path)

        return f"{stat.st_mtime_ns}:{stat.st_size}"

    except OSError:

        return "missing"





def truthy_to_bool(series: pd.Series) -> pd.Series:

    return (

        series.astype(str)

        .str.strip()

        .str.upper()

        .map({"TRUE": True, "FALSE": False})

        .fillna(False)

    )





def clean_text_series(s: pd.Series) -> pd.Series:

    return (

        s.fillna("")

        .astype(str)

        .str.strip()

        .replace({"nan": "", "NaN": "", "None": "", "none": "", "<NA>": "", "<na>": ""})

    )





def normalize_server_name(value: Any) -> str:

    return str(value).strip()





def canonical_server_name_key(value: Any) -> str:

    return normalize_server_name(value).casefold()





def normalize_server_role(value: Any) -> str:

    role = str(value).strip().lower()

    if role in {"primary", "p", "1"}:

        return "Primary"

    if role in {"secondary", "s", "2"}:

        return "Secondary"

    return ""





def clean_server_roles_df(roles_df: pd.DataFrame) -> pd.DataFrame:

    work = roles_df.copy()

    if "Server Name" not in work.columns:

        work["Server Name"] = ""

    if "Role" not in work.columns:

        work["Role"] = ""

    work = work[["Server Name", "Role"]].copy()

    work["Server Name"] = work["Server Name"].map(normalize_server_name)

    work["Role"] = work["Role"].map(normalize_server_role)

    work = work[work["Server Name"] != ""].copy()

    if not work.empty:

        work = work.drop_duplicates(subset=["Server Name"], keep="last")

        work = work.sort_values("Server Name").reset_index(drop=True)

    return work





def save_server_roles(path: str, roles_df: pd.DataFrame) -> pd.DataFrame:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cleaned = clean_server_roles_df(roles_df)

    try:
        cleaned.to_csv(path, index=False)
        st.session_state.pop("server_role_map_save_error", None)
    except OSError as exc:
        if exc.errno == errno.ENOSPC:
            st.session_state["server_role_map_save_error"] = (
                "Server role mapping could not be saved because this machine is out of disk space."
            )
            return cleaned
        raise

    return cleaned





def load_server_roles(path: str, observed_servers: list[str] | None = None) -> pd.DataFrame:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):

        try:

            existing = pd.read_csv(path)

        except Exception:

            existing = pd.DataFrame(columns=["Server Name", "Role"])

    else:

        existing = pd.DataFrame(columns=["Server Name", "Role"])



    cleaned = clean_server_roles_df(existing)

    if observed_servers:

        existing_names = set(cleaned["Server Name"].tolist())

        missing = sorted({normalize_server_name(s) for s in observed_servers if normalize_server_name(s)} - existing_names)

        if missing:

            add_df = pd.DataFrame({"Server Name": missing, "Role": [""] * len(missing)})

            cleaned = clean_server_roles_df(pd.concat([cleaned, add_df], ignore_index=True))

    save_server_roles(path, cleaned)

    return cleaned





def server_role_map_from_df(roles_df: pd.DataFrame) -> dict[str, str]:

    mapping: dict[str, str] = {}

    for _, row in roles_df.iterrows():

        server_name = normalize_server_name(row.get("Server Name", ""))

        role = normalize_server_role(row.get("Role", ""))

        if server_name and role:

            mapping[canonical_server_name_key(server_name)] = role

    return mapping





def classify_error_flags(error_flags: pd.Series) -> tuple[pd.Series, pd.Series]:

    cleaned = clean_text_series(error_flags)

    normalized = (

        cleaned

        .str.lower()

        .str.replace("|", ",", regex=False)

        .str.replace(" ", "", regex=False)

    )

    has_any = normalized.ne("")

    # Treat stale/noisy transport flags as soft. Any other non-empty token is "hard".

    soft_token = r"(?:notpresent|network|longfailed)"

    only_soft = normalized.str.fullmatch(fr"{soft_token}(,{soft_token})*", na=False)

    hard = has_any & ~only_soft

    return has_any, hard





def compute_action_required_mask(
    df: pd.DataFrame,
    ping_status_col: str = "Ping Status",
    use_ping_results: bool = True,
) -> pd.Series:
    if df.empty:

        return pd.Series(dtype=bool, index=df.index)



    health_state = clean_text_series(

        df.get("Health State", pd.Series([""] * len(df), index=df.index))

    )

    visible_bool = (

        df.get("Visible_bool", pd.Series([True] * len(df), index=df.index))

        .fillna(True)

        .astype(bool)

    )

    _, hard_error_flags = classify_error_flags(

        df.get("Error Flags", pd.Series([""] * len(df), index=df.index))

    )



    offline_strict = health_state.eq("Offline") | (~visible_bool)

    offline_visible = health_state.eq("Offline (but still visible)")

    if use_ping_results:

        ping_status = clean_text_series(
            df.get(ping_status_col, pd.Series([""] * len(df), index=df.index))
        )
        ping_lower = ping_status.str.lower()
        ping_is_good = ping_lower.str.contains("pingable", na=False) & ~ping_lower.str.contains("not pingable", na=False)


        offline_visible_needs_attention = offline_visible & (hard_error_flags | ~ping_is_good)

    else:

        # Keep issue counts stable for a fixed CSV instead of letting async ping checks
        # change the headline number after load.
        offline_visible_needs_attention = offline_visible
    base_mask = (offline_strict | hard_error_flags | offline_visible_needs_attention).fillna(False)



    # If a row is Online and mapped connection columns show no red state,

    # treat it as not requiring attention.

    if ("Primary Connection" in df.columns) or ("Secondary Connection" in df.columns):

        primary_conn = clean_text_series(

            df.get("Primary Connection", pd.Series([""] * len(df), index=df.index))

        )

        secondary_conn = clean_text_series(

            df.get("Secondary Connection", pd.Series([""] * len(df), index=df.index))

        )

        any_conn_value = primary_conn.ne("") | secondary_conn.ne("")

        primary_red = (

            primary_conn.str.startswith("\U0001F534")

            | primary_conn.str.contains(r"\(\s*Disconnected\s*\)", case=False, regex=True)

        )

        secondary_red = (

            secondary_conn.str.startswith("\U0001F534")

            | secondary_conn.str.contains(r"\(\s*Disconnected\s*\)", case=False, regex=True)

        )

        online_no_red_connections = health_state.eq("Online") & any_conn_value & ~(primary_red | secondary_red)

        return (base_mask & ~online_no_red_connections).fillna(False)



    return base_mask





def device_name_base(df: pd.DataFrame) -> pd.Series:

    # Remove trailing "(1)", "(2)" etc

    return (

        df["Device Name"]

        .astype(str)

        .str.strip()

        .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)

    )





def extract_device_id_base(df: pd.DataFrame) -> pd.Series:

    """

    Device ID field often contains comma-separated tokens. Example:

    Device,1.1.00188545e5cc.cam00,3.<guid>,4.<guid>

    We grab the second token and strip .camNN.

    """

    if "Device ID" not in df.columns:

        return pd.Series([pd.NA] * len(df), index=df.index)



    token = df["Device ID"].astype(str).str.split(",", expand=True)

    if token.shape[1] < 2:

        return pd.Series([pd.NA] * len(df), index=df.index)



    dev = token[1].fillna("").astype(str).str.strip()

    dev = dev.str.replace(r"\.cam\d+$", "", regex=True)

    dev = dev.replace("", pd.NA)

    return dev





def build_physical_key(df: pd.DataFrame) -> pd.Series:

    """

    Build a PHYSICAL device key (one per camera), collapsing:

      - multi-lens rows

      - primary/secondary server duplicates



    Priority:

      1) MAC Address (best for primary/secondary duplicates)

      2) Serial Number

      3) Device ID base (strips .camNN)

      4) Device Name Base

    """

    mac = clean_text_series(df["MAC Address"]) if "MAC Address" in df.columns else pd.Series([pd.NA]*len(df), index=df.index)

    mac = mac.replace("", pd.NA)



    serial = clean_text_series(df["Serial Number"]) if "Serial Number" in df.columns else pd.Series([pd.NA]*len(df), index=df.index)

    serial = serial.replace("", pd.NA)



    dev_base = extract_device_id_base(df)

    name_base = device_name_base(df).replace("", pd.NA)



    physical = mac.combine_first(serial).combine_first(dev_base).combine_first(name_base).fillna("UNKNOWN")

    return physical





def load_notes(notes_path: str) -> pd.DataFrame:

    os.makedirs(os.path.dirname(notes_path), exist_ok=True)



    if os.path.exists(notes_path):

        ndf = pd.read_csv(notes_path)

        ndf.columns = [c.strip() for c in ndf.columns]

    else:

        ndf = pd.DataFrame(columns=["key", "disposition", "notes"])



    for col in ["key", "disposition", "notes"]:

        if col not in ndf.columns:

            ndf[col] = ""



    ndf = ndf[["key", "disposition", "notes"]].copy()

    ndf["key"] = ndf["key"].astype(str)

    ndf["disposition"] = ndf["disposition"].fillna("")

    ndf["notes"] = ndf["notes"].fillna("")

    return ndf





def save_notes(notes_path: str, edited_notes: pd.DataFrame) -> None:

    os.makedirs(os.path.dirname(notes_path), exist_ok=True)



    out = edited_notes.copy()

    out["key"] = out["key"].astype(str)

    out["disposition"] = out["disposition"].fillna("")

    out["notes"] = out["notes"].fillna("")

    out = out.drop_duplicates(subset=["key"], keep="last")

    out.to_csv(notes_path, index=False)





def utc_now_timestamp() -> pd.Timestamp:

    return pd.Timestamp(datetime.now(timezone.utc)).floor("s")





def format_timestamp(ts: pd.Timestamp | str | None) -> str:

    parsed = pd.to_datetime(ts, utc=True, errors="coerce")

    if pd.isna(parsed):

        return ""

    return parsed.isoformat()





def hours_since(ts: pd.Timestamp | str | None, now_ts: pd.Timestamp) -> float:

    parsed = pd.to_datetime(ts, utc=True, errors="coerce")

    if pd.isna(parsed):

        return 0.0

    delta = now_ts - parsed

    return max(delta.total_seconds() / 3600.0, 0.0)





def load_tracking_state(path: str) -> pd.DataFrame:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cols = [

        "key",

        "device_name",

        "location",

        "current_health_state",

        "first_seen_at",

        "last_seen_at",

        "first_offline_at",

        "last_offline_seen_at",

        "last_online_at",

        "offline_hours",

        "ticket_status",

        "ticket_id",

        "active",

    ]

    if os.path.exists(path):

        df = pd.read_csv(path)

        df.columns = [c.strip() for c in df.columns]

    else:

        df = pd.DataFrame(columns=cols)



    for col in cols:

        if col not in df.columns:

            df[col] = ""



    df = df[cols].copy()

    df["key"] = df["key"].astype(str)

    df["device_name"] = df["device_name"].fillna("")

    df["location"] = df["location"].fillna("")

    df["current_health_state"] = df["current_health_state"].fillna("")

    df["offline_hours"] = pd.to_numeric(df["offline_hours"], errors="coerce").fillna(0.0)

    df["ticket_status"] = df["ticket_status"].fillna("")

    df["ticket_id"] = df["ticket_id"].fillna("")

    df["active"] = df["active"].astype(str).str.strip().str.upper().map({"TRUE": True, "FALSE": False}).fillna(True)

    return df





def save_tracking_state(path: str, tracking_df: pd.DataFrame) -> None:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cols = [

        "key",

        "device_name",

        "location",

        "current_health_state",

        "first_seen_at",

        "last_seen_at",

        "first_offline_at",

        "last_offline_seen_at",

        "last_online_at",

        "offline_hours",

        "ticket_status",

        "ticket_id",

        "active",

    ]

    out = tracking_df.copy()

    for col in cols:

        if col not in out.columns:

            out[col] = ""

    out = out[cols].copy()

    out["key"] = out["key"].astype(str)

    out["offline_hours"] = pd.to_numeric(out["offline_hours"], errors="coerce").fillna(0.0).round(2)

    out["active"] = out["active"].fillna(True)

    out = out.drop_duplicates(subset=["key"], keep="last")

    out.to_csv(path, index=False)





def load_tickets(path: str) -> pd.DataFrame:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cols = [

        "ticket_key",

        "key",

        "device_name",

        "location",

        "health_state",

        "offline_since",

        "offline_hours_at_creation",

        "ticket_state",

        "ticket_id",

        "email_to",

        "email_subject",

        "created_at",

        "email_sent_at",

        "resolved_at",

        "resolution",

        "resolution_notes",

        "last_error",

    ]

    if os.path.exists(path):

        df = pd.read_csv(path)

        df.columns = [c.strip() for c in df.columns]

    else:

        df = pd.DataFrame(columns=cols)



    for col in cols:

        if col not in df.columns:

            df[col] = ""



    df = df[cols].copy()

    for col in ["ticket_key", "key", "device_name", "location", "health_state", "ticket_state", "ticket_id", "email_to", "email_subject", "resolution", "resolution_notes", "last_error"]:

        df[col] = df[col].fillna("").astype(str)

    df["offline_hours_at_creation"] = pd.to_numeric(df["offline_hours_at_creation"], errors="coerce").fillna(0.0)

    return df





def normalize_ticket_updates(tickets_df: pd.DataFrame) -> pd.DataFrame:

    out = tickets_df.copy()

    now_iso = format_timestamp(utc_now_timestamp())

    out["ticket_state"] = out["ticket_state"].fillna("").astype(str)
    out["resolved_at"] = out["resolved_at"].fillna("").astype(str)

    resolved_mask = out["ticket_state"].eq("Resolved")

    out.loc[resolved_mask & out["resolved_at"].fillna("").eq(""), "resolved_at"] = now_iso

    out.loc[~resolved_mask, "resolved_at"] = out.loc[~resolved_mask, "resolved_at"].fillna("")

    return out





def save_tickets(path: str, tickets_df: pd.DataFrame) -> None:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    out = normalize_ticket_updates(tickets_df)

    out = out.drop_duplicates(subset=["ticket_key"], keep="last")

    out.to_csv(path, index=False)





def load_state_transitions(path: str) -> pd.DataFrame:

    os.makedirs(os.path.dirname(path), exist_ok=True)

    cols = [

        "timestamp_utc",

        "key",

        "from_state",

        "to_state",

        "device_name",

        "location",

    ]

    if os.path.exists(path):

        df = pd.read_csv(path)

        df.columns = [c.strip() for c in df.columns]

    else:

        df = pd.DataFrame(columns=cols)



    for col in cols:

        if col not in df.columns:

            df[col] = ""

    return df[cols].copy()





def append_state_transitions(path: str, devices_df: pd.DataFrame, prior_tracking_df: pd.DataFrame, observed_at: pd.Timestamp) -> None:

    os.makedirs(os.path.dirname(path), exist_ok=True)



    if os.path.exists(path):

        ndf = pd.read_csv(path)

        ndf.columns = [c.strip() for c in ndf.columns]

    else:

        ndf = pd.DataFrame(columns=["key", "disposition", "notes"])



    for col in ["key", "disposition", "notes"]:

        if col not in ndf.columns:

            ndf[col] = ""



    ndf = ndf[["key", "disposition", "notes"]].copy()

    ndf["key"] = ndf["key"].astype(str)

    ndf["disposition"] = ndf["disposition"].fillna("")

    ndf["notes"] = ndf["notes"].fillna("")

    return ndf





def add_flap_metrics(devices_df: pd.DataFrame, transitions_df: pd.DataFrame, observed_at: pd.Timestamp) -> pd.DataFrame:

    out = devices_df.copy()

    out["Flaps (24h)"] = 0

    out["Flaps (7d)"] = 0

    if out.empty or transitions_df.empty:

        return out



    tdf = transitions_df.copy()

    tdf["key"] = tdf["key"].astype(str)

    tdf["timestamp_utc"] = pd.to_datetime(tdf["timestamp_utc"], utc=True, errors="coerce")

    tdf = tdf.dropna(subset=["timestamp_utc"])

    if tdf.empty:

        return out



    cutoff_24h = observed_at - pd.Timedelta(hours=24)

    cutoff_7d = observed_at - pd.Timedelta(days=7)

    flaps_24h = tdf.loc[tdf["timestamp_utc"] >= cutoff_24h].groupby("key").size()

    flaps_7d = tdf.loc[tdf["timestamp_utc"] >= cutoff_7d].groupby("key").size()



    out["key"] = out["key"].astype(str)

    out["Flaps (24h)"] = out["key"].map(flaps_24h).fillna(0).astype(int)

    out["Flaps (7d)"] = out["key"].map(flaps_7d).fillna(0).astype(int)

    return out





def _is_online_state(state: str) -> bool:

    return str(state).strip().lower() == "online"





def _accumulate_state_seconds_by_day(

    start_ts: pd.Timestamp,

    end_ts: pd.Timestamp,

    state: str,

    online_seconds: dict[pd.Timestamp, float],

    offline_seconds: dict[pd.Timestamp, float],

) -> None:

    if pd.isna(start_ts) or pd.isna(end_ts) or end_ts <= start_ts:

        return



    cursor = start_ts

    online = _is_online_state(state)

    while cursor < end_ts:

        day_bucket = cursor.floor("D")

        next_day = day_bucket + pd.Timedelta(days=1)

        slice_end = min(end_ts, next_day)

        seconds = float((slice_end - cursor).total_seconds())

        if seconds <= 0:

            break

        if online:

            online_seconds[day_bucket] = online_seconds.get(day_bucket, 0.0) + seconds

        else:

            offline_seconds[day_bucket] = offline_seconds.get(day_bucket, 0.0) + seconds

        cursor = slice_end





def build_connectivity_trend_tables(

    devices_df: pd.DataFrame,

    transitions_df: pd.DataFrame,

    observed_at: pd.Timestamp,

    lookback_days: int = 30,

) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float | int]]:

    lookback = max(int(lookback_days), 1)

    window_start = observed_at - pd.Timedelta(days=lookback)



    summary: dict[str, float | int] = {

        "window_uptime_pct": 0.0,

        "window_downtime_pct": 0.0,

        "last_7d_uptime_pct": 0.0,

        "last_7d_downtime_pct": 0.0,

        "window_state_changes": 0,

        "tracked_devices": 0,

        "assumed_static_devices": 0,

    }

    if devices_df.empty or "key" not in devices_df.columns:

        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), summary



    devices = devices_df.copy()

    devices["key"] = devices["key"].astype(str)

    devices["Health State"] = devices.get(

        "Health State",

        pd.Series([""] * len(devices), index=devices.index),

    ).fillna("").astype(str)

    devices["Device Name Base"] = devices.get(

        "Device Name Base",

        pd.Series([""] * len(devices), index=devices.index),

    ).fillna("").astype(str)

    devices["Location"] = devices.get(

        "Location",

        pd.Series([""] * len(devices), index=devices.index),

    ).fillna("").astype(str)

    devices = devices.drop_duplicates(subset=["key"], keep="last")

    current_state_by_key = devices.set_index("key")["Health State"].to_dict()

    camera_name_by_key = devices.set_index("key")["Device Name Base"].to_dict()

    location_by_key = devices.set_index("key")["Location"].to_dict()

    keys = list(current_state_by_key.keys())

    summary["tracked_devices"] = len(keys)

    if not keys:

        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), summary



    day_start = window_start.floor("D")

    day_end = observed_at.floor("D")

    day_index = pd.date_range(start=day_start, end=day_end, freq="D", tz="UTC")

    online_seconds: dict[pd.Timestamp, float] = {d: 0.0 for d in day_index}

    offline_seconds: dict[pd.Timestamp, float] = {d: 0.0 for d in day_index}

    camera_online_seconds: dict[str, float] = {}

    camera_offline_seconds: dict[str, float] = {}

    camera_state_changes: dict[str, int] = {}



    if transitions_df.empty:

        transitions = pd.DataFrame(columns=["timestamp_utc", "key", "from_state", "to_state"])

    else:

        transitions = transitions_df.copy()

    for col in ["timestamp_utc", "key", "from_state", "to_state"]:

        if col not in transitions.columns:

            transitions[col] = ""

    transitions["key"] = transitions["key"].astype(str)

    transitions["timestamp_utc"] = pd.to_datetime(transitions["timestamp_utc"], utc=True, errors="coerce")

    transitions["from_state"] = transitions["from_state"].fillna("").astype(str)

    transitions["to_state"] = transitions["to_state"].fillna("").astype(str)

    transitions = transitions.dropna(subset=["timestamp_utc"])

    transitions = transitions[

        transitions["key"].isin(keys)

        & transitions["timestamp_utc"].ge(window_start)

        & transitions["timestamp_utc"].le(observed_at)

    ].sort_values(["key", "timestamp_utc"], ascending=[True, True])



    events_by_key: dict[str, pd.DataFrame] = {

        str(k): g.copy()

        for k, g in transitions.groupby("key", sort=False)

    }



    for key in keys:

        key_events = events_by_key.get(str(key), pd.DataFrame())

        current_state = str(current_state_by_key.get(str(key), "")).strip() or "Unknown"

        camera_state_changes[str(key)] = int(len(key_events))

        if key_events.empty:

            summary["assumed_static_devices"] = int(summary["assumed_static_devices"]) + 1

            _accumulate_state_seconds_by_day(

                start_ts=window_start,

                end_ts=observed_at,

                state=current_state,

                online_seconds=online_seconds,

                offline_seconds=offline_seconds,

            )

            window_seconds = float((observed_at - window_start).total_seconds())

            if _is_online_state(current_state):

                camera_online_seconds[str(key)] = camera_online_seconds.get(str(key), 0.0) + window_seconds

                camera_offline_seconds[str(key)] = camera_offline_seconds.get(str(key), 0.0)

            else:

                camera_offline_seconds[str(key)] = camera_offline_seconds.get(str(key), 0.0) + window_seconds

                camera_online_seconds[str(key)] = camera_online_seconds.get(str(key), 0.0)

            continue



        first_event = key_events.iloc[0]

        start_state = str(first_event.get("from_state", "")).strip() or current_state



        cursor = window_start

        state = start_state

        for _, evt in key_events.iterrows():

            evt_ts = pd.to_datetime(evt.get("timestamp_utc"), utc=True, errors="coerce")

            if pd.isna(evt_ts):

                continue

            if evt_ts <= cursor:

                to_state = str(evt.get("to_state", "")).strip()

                if to_state:

                    state = to_state

                continue

            _accumulate_state_seconds_by_day(

                start_ts=cursor,

                end_ts=evt_ts,

                state=state,

                online_seconds=online_seconds,

                offline_seconds=offline_seconds,

            )

            segment_seconds = float((evt_ts - cursor).total_seconds())

            if segment_seconds > 0:

                if _is_online_state(state):

                    camera_online_seconds[str(key)] = camera_online_seconds.get(str(key), 0.0) + segment_seconds

                else:

                    camera_offline_seconds[str(key)] = camera_offline_seconds.get(str(key), 0.0) + segment_seconds

            to_state = str(evt.get("to_state", "")).strip()

            if to_state:

                state = to_state

            cursor = evt_ts



        _accumulate_state_seconds_by_day(

            start_ts=cursor,

            end_ts=observed_at,

            state=state,

            online_seconds=online_seconds,

            offline_seconds=offline_seconds,

        )

        tail_seconds = float((observed_at - cursor).total_seconds())

        if tail_seconds > 0:

            if _is_online_state(state):

                camera_online_seconds[str(key)] = camera_online_seconds.get(str(key), 0.0) + tail_seconds

            else:

                camera_offline_seconds[str(key)] = camera_offline_seconds.get(str(key), 0.0) + tail_seconds



    changes_by_day = transitions.groupby(transitions["timestamp_utc"].dt.floor("D")).size()



    daily_rows: list[dict[str, float | int | pd.Timestamp | str]] = []

    for day in day_index:

        online_hrs = float(online_seconds.get(day, 0.0) / 3600.0)

        offline_hrs = float(offline_seconds.get(day, 0.0) / 3600.0)

        total_hrs = online_hrs + offline_hrs

        uptime_pct = (online_hrs / total_hrs * 100.0) if total_hrs > 0 else 0.0

        downtime_pct = (offline_hrs / total_hrs * 100.0) if total_hrs > 0 else 0.0

        daily_rows.append({

            "Period Start UTC": day.tz_convert(None),

            "Period": day.strftime("%Y-%m-%d"),

            "Online Hours": round(online_hrs, 2),

            "Offline Hours": round(offline_hrs, 2),

            "Uptime %": round(uptime_pct, 2),

            "Downtime %": round(downtime_pct, 2),

            "State Changes": int(changes_by_day.get(day, 0)),

        })



    daily_df = pd.DataFrame(daily_rows)

    if daily_df.empty:

        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), summary



    camera_rows: list[dict[str, float | int | str]] = []

    for key in keys:

        online_hrs = float(camera_online_seconds.get(str(key), 0.0) / 3600.0)

        offline_hrs = float(camera_offline_seconds.get(str(key), 0.0) / 3600.0)

        total_hrs = online_hrs + offline_hrs

        uptime_pct = (online_hrs / total_hrs * 100.0) if total_hrs > 0 else 0.0

        downtime_pct = (offline_hrs / total_hrs * 100.0) if total_hrs > 0 else 0.0

        camera_rows.append({

            "Device Name Base": str(camera_name_by_key.get(str(key), "")),

            "key": str(key),

            "Location": str(location_by_key.get(str(key), "")),

            "Current Health State": str(current_state_by_key.get(str(key), "")),

            "Online Hours": round(online_hrs, 2),

            "Offline Hours": round(offline_hrs, 2),

            "Uptime %": round(uptime_pct, 2),

            "Downtime %": round(downtime_pct, 2),

            "State Changes": int(camera_state_changes.get(str(key), 0)),

        })

    camera_uptime_df = pd.DataFrame(camera_rows).sort_values(

        by=["Uptime %", "State Changes", "Device Name Base"],

        ascending=[False, True, True],

        na_position="last",

    )



    weekly_df = daily_df.copy()

    weekly_df["Week Start UTC"] = weekly_df["Period Start UTC"].dt.to_period("W-SUN").apply(lambda p: p.start_time)

    weekly_df = (

        weekly_df.groupby("Week Start UTC", as_index=False)

        .agg({

            "Online Hours": "sum",

            "Offline Hours": "sum",

            "State Changes": "sum",

        })

        .sort_values("Week Start UTC")

    )

    weekly_df["Total Hours"] = weekly_df["Online Hours"] + weekly_df["Offline Hours"]

    weekly_df["Uptime %"] = (

        (weekly_df["Online Hours"] / weekly_df["Total Hours"]).fillna(0.0) * 100.0

    ).round(2)

    weekly_df["Downtime %"] = (

        (weekly_df["Offline Hours"] / weekly_df["Total Hours"]).fillna(0.0) * 100.0

    ).round(2)

    weekly_df["Period"] = pd.to_datetime(weekly_df["Week Start UTC"]).dt.strftime("%Y-%m-%d")

    weekly_df = weekly_df[[

        "Week Start UTC",

        "Period",

        "Online Hours",

        "Offline Hours",

        "Uptime %",

        "Downtime %",

        "State Changes",

    ]].copy()



    total_online = float(daily_df["Online Hours"].sum())

    total_offline = float(daily_df["Offline Hours"].sum())

    total = total_online + total_offline

    summary["window_uptime_pct"] = (total_online / total * 100.0) if total > 0 else 0.0

    summary["window_downtime_pct"] = (total_offline / total * 100.0) if total > 0 else 0.0

    summary["window_state_changes"] = int(transitions.shape[0])



    observed_naive = observed_at.tz_convert("UTC").tz_localize(None)

    cutoff_7d = (observed_naive - pd.Timedelta(days=6)).floor("D")

    last_7d = daily_df[daily_df["Period Start UTC"] >= cutoff_7d].copy()

    last_7d_online = float(last_7d["Online Hours"].sum())

    last_7d_offline = float(last_7d["Offline Hours"].sum())

    last_7d_total = last_7d_online + last_7d_offline

    summary["last_7d_uptime_pct"] = (last_7d_online / last_7d_total * 100.0) if last_7d_total > 0 else 0.0

    summary["last_7d_downtime_pct"] = (last_7d_offline / last_7d_total * 100.0) if last_7d_total > 0 else 0.0



    return daily_df, weekly_df, camera_uptime_df, summary





def detect_retention_column(columns: list[str]) -> str | None:

    for col in columns:

        if "retention" in str(col).lower():

            return col

    return None





def parse_retention_days(series: pd.Series) -> pd.Series:

    extracted = series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)

    return pd.to_numeric(extracted, errors="coerce")





def add_retention_fields(devices_df: pd.DataFrame, views_df: pd.DataFrame) -> tuple[pd.DataFrame, bool, str | None]:

    out = devices_df.copy()

    retention_col = detect_retention_column(list(views_df.columns))

    if retention_col is None or "physical_key" not in out.columns or "physical_key" not in views_df.columns:

        return out, False, None



    retention_df = views_df[["physical_key", retention_col]].copy()

    retention_df["physical_key"] = retention_df["physical_key"].astype(str)

    retention_df["_retention_days"] = parse_retention_days(retention_df[retention_col])

    # Treat all rows for the same physical camera (including primary/secondary server rows)

    # as one camera by taking the best observed retention value for that device.

    retention_by_key = retention_df.groupby("physical_key")["_retention_days"].max()



    out["physical_key"] = out["physical_key"].astype(str)

    out["Retention (days)"] = pd.to_numeric(out["physical_key"].map(retention_by_key), errors="coerce").round(1)

    out["Retention OK"] = out["Retention (days)"].ge(RETENTION_POLICY_DAYS) & out["Retention (days)"].notna()

    out["Retention Gap"] = (RETENTION_POLICY_DAYS - out["Retention (days)"]).clip(lower=0).fillna(0).round(1) # type: ignore

    return out, True, retention_col





def compute_priority_table(devices_df: pd.DataFrame) -> pd.DataFrame:

    if devices_df.empty:

        out = devices_df.copy()

        out["Priority Score"] = []

        out["Priority Reason"] = []

        return out



    out = devices_df.copy()

    if "Ping Status" not in out.columns:

        out = add_ping_status_for_issues(out)



    health_state = out.get("Health State", pd.Series([""] * len(out), index=out.index)).fillna("").astype(str)

    ping_status = out.get("Ping Status", pd.Series([""] * len(out), index=out.index)).fillna("").astype(str)

    ping_lower = ping_status.str.lower()

    _, hard_error_flags = classify_error_flags(

        out.get("Error Flags", pd.Series([""] * len(out), index=out.index))

    )

    offline_hours = pd.to_numeric(out.get("Offline For (hrs)", 0.0), errors="coerce").fillna(0.0).clip(lower=0)

    missing_ip = out.get("IP Address", pd.Series([""] * len(out), index=out.index)).fillna("").astype(str).str.strip().eq("")



    offline_mask = health_state.eq("Offline")

    offline_visible_mask = health_state.eq("Offline (but still visible)")

    not_pingable_mask = ping_lower.str.contains("not pingable", na=False)

    ping_error_mask = ping_lower.str.contains("ping error", na=False)



    score = pd.Series(0.0, index=out.index, dtype=float)

    score += offline_mask.astype(float) * 50

    score += offline_visible_mask.astype(float) * 25

    score += hard_error_flags.astype(float) * 10

    score += (not_pingable_mask | ping_error_mask).astype(float) * 15

    score += offline_hours.clip(upper=72)

    score += missing_ip.astype(float) * -5



    def _reason_for_idx(idx: object) -> str:

        reasons: list[str] = []

        if bool(offline_mask.loc[idx]):

            reasons.append("Offline")

        elif bool(offline_visible_mask.loc[idx]):

            reasons.append("Offline (visible)")

        if bool(not_pingable_mask.loc[idx]):

            reasons.append("Not Pingable")

        elif bool(ping_error_mask.loc[idx]):

            reasons.append("Ping Error")

        if bool(hard_error_flags.loc[idx]):

            reasons.append("Hard Error Flags")

        hrs = float(offline_hours.loc[idx])

        if hrs > 0:

            reasons.append(f"{hrs:.1f}h offline")

        if bool(missing_ip.loc[idx]):

            reasons.append("Missing IP")

        return "; ".join(reasons) if reasons else "No active issues"



    out["Priority Score"] = score.round(1)

    out["Priority Reason"] = [_reason_for_idx(idx) for idx in out.index]

    out = out.sort_values(

        by=["Priority Score", "Offline For (hrs)", "Device Name Base"],

        ascending=[False, False, True],

        na_position="last",

    )

    return out





def build_weekly_digest(

    devices_df: pd.DataFrame,

    tracking_df: pd.DataFrame,

    tickets_df: pd.DataFrame,

    transitions_df: pd.DataFrame,

    ticket_threshold_hours: int,

    retention_available: bool,

) -> str:

    now_ts = utc_now_timestamp()

    cutoff_7d = now_ts - pd.Timedelta(days=7)



    devices = devices_df.copy()

    device_health = devices.get("Health State", pd.Series(["Online"] * len(devices), index=devices.index)).fillna("Online").astype(str)

    total_offline_now = int(device_health.ne("Online").sum())



    tracking = tracking_df.copy()

    if tracking.empty:

        tracking = pd.DataFrame(columns=["current_health_state", "first_offline_at", "offline_hours"])

    tracking["current_health_state"] = tracking.get("current_health_state", "").fillna("").astype(str)

    tracking["offline_hours"] = pd.to_numeric(tracking.get("offline_hours", 0.0), errors="coerce").fillna(0.0)

    first_offline_ts = pd.to_datetime(tracking.get("first_offline_at", ""), utc=True, errors="coerce")

    offline_now_tracking = tracking["current_health_state"].ne("Online")

    new_offline_7d = int((offline_now_tracking & first_offline_ts.notna() & (first_offline_ts >= cutoff_7d)).sum())

    still_offline_over_threshold = int((offline_now_tracking & tracking["offline_hours"].ge(float(ticket_threshold_hours))).sum())



    tickets = tickets_df.copy()

    tickets["ticket_state"] = tickets.get("ticket_state", "").fillna("").astype(str)

    pending_count = int(tickets["ticket_state"].eq("Pending Send").sum())

    open_count = int(tickets["ticket_state"].eq("Open").sum())

    resolved_ts = pd.to_datetime(tickets.get("resolved_at", ""), utc=True, errors="coerce")

    resolved_7d = int((tickets["ticket_state"].eq("Resolved") & resolved_ts.notna() & (resolved_ts >= cutoff_7d)).sum())



    retention_violations = None

    if retention_available and "Retention OK" in devices.columns:

        retention_violations = int((~devices["Retention OK"].fillna(False)).sum())



    transitions = transitions_df.copy()

    if transitions.empty:

        top_flappers = pd.Series(dtype="int64")

    else:

        transitions["timestamp_utc"] = pd.to_datetime(transitions["timestamp_utc"], utc=True, errors="coerce")

        transitions["key"] = transitions["key"].astype(str)

        top_flappers = (

            transitions.loc[transitions["timestamp_utc"] >= cutoff_7d]

            .groupby("key")

            .size()

            .sort_values(ascending=False)

            .head(10)

        )



    device_name_map: dict[str, str] = {}

    if {"key", "Device Name Base"}.issubset(devices.columns):

        device_name_map = (

            devices[["key", "Device Name Base"]]

            .drop_duplicates(subset=["key"], keep="last")

            .set_index("key")["Device Name Base"]

            .fillna("")

            .astype(str)

            .to_dict()

        )



    lines = [

        f"Weekly Digest ({now_ts.strftime('%Y-%m-%d %H:%M UTC')})",

        "",

        f"- Total offline right now: {total_offline_now}",

        f"- New offline devices since 7 days ago: {new_offline_7d}",

        f"- Cameras still offline >= {ticket_threshold_hours}h: {still_offline_over_threshold}",

    ]

    if retention_violations is not None:

        lines.append(f"- Retention violations (<{RETENTION_POLICY_DAYS} days): {retention_violations}")

    lines.extend([

        f"- Tickets: Pending Send={pending_count}, Open={open_count}, Resolved in last 7d={resolved_7d}",

        "",

        "- Top 10 flappers (7d):",

    ])

    if top_flappers.empty:

        lines.append("  - None")

    else:

        for key, count in top_flappers.items():

            camera_name = device_name_map.get(str(key), str(key))

            lines.append(f"  - {camera_name}: {int(count)} state changes")

    return "\n".join(lines)





def build_ticket_subject(row: pd.Series, threshold_hours: int = 24) -> str:

    device_name = row.get("Device Name Base") or row.get("device_name") or row.get("key") or "Unknown device"

    location = row.get("Location") or row.get("location") or "Unknown location"

    return f"Camera Offline >{int(threshold_hours)}h: {device_name} ({location})"





def build_ticket_email_body(row: pd.Series, offline_hours: float) -> str:

    return (

        f"{generate_ticket_payload(row)}\n"

        f"- Health State: {row.get('Health State', row.get('health_state', 'N/A'))}\n"

        f"- Offline For (hours): {offline_hours:.1f}\n"

        f"- Requested Action: Create/assign TDX ticket for initial troubleshooting."

    )





def send_ticket_email(smtp_host: str, smtp_port: int, smtp_username: str, smtp_password: str, from_email: str, to_email: str, subject: str, body: str) -> tuple[bool, str]:

    if not all([smtp_host, smtp_port, smtp_username, smtp_password, from_email, to_email]):

        return False, "SMTP settings are incomplete."



    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = from_email

    msg["To"] = to_email

    msg.set_content(body)



    try:

        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:

            smtp.starttls()

            smtp.login(smtp_username, smtp_password)

            smtp.send_message(msg)

        return True, ""

    except Exception as exc:

        return False, str(exc)





def clean_cell_value(value: object) -> str:

    text = str(value).strip()

    return "" if text.lower() in {"", "nan", "none", "nat"} else text





def row_first_non_empty(row: pd.Series, candidate_columns: list[str]) -> str:
    for col in candidate_columns:
        if col in row.index:
            value = clean_cell_value(row.get(col, ""))
            if value:
                return value
    return ""


TICKET_ASSISTANT_WORKFLOWS = [
    "Auto Detect",
    "Camera System Video Request",
    "Payment Confirmation Email",
    "Camera Asset Record",
    "Vendor Escalation Response",
    "No Video Available Response",
    "Paid Video Link Delivery",
    "Link Re-upload Response",
    "Multi-Media Fee Response",
    "General Ticket Review",
]

TICKET_ASSISTANT_FIELDS: list[tuple[str, str]] = [
    ("date", "Date"),
    ("time", "Time"),
    ("location", "Location"),
    ("case_number", "LSUPD Case Number"),
    ("service_request_id", "Service Request ID"),
    ("tdx_ticket_id", "TDX Ticket ID"),
    ("name", "Name"),
    ("camera_name", "Camera Name"),
    ("issue_description", "Issue Description"),
    ("actions_taken", "Actions Taken / Status"),
    ("camera_location", "Camera Location"),
    ("asset_id", "Asset ID"),
    ("product_model", "Product Model"),
    ("serial_number", "Serial Number"),
    ("service_tag", "Service Tag"),
    ("camera_ip", "Camera IP"),
    ("camera_server", "Camera Server"),
    ("failover_server", "Failover Server"),
    ("camera_power_source", "Camera Power Source"),
    ("its_switch_ip", "ITS Switch IP"),
    ("its_switch_name", "ITS Switch Name"),
    ("its_switch_port", "ITS Switch Port"),
    ("department_for_maintenance", "Department for Maintenance"),
    ("installation_company", "Installation Company"),
    ("budget_code", "Budget Code"),
]

TICKET_ASSISTANT_DEFAULT_PLAYER_LINK = "https://lsu.box.com/s/shf2qvrdsblqcezpeq80fz38bbr11mtv"

TICKET_ASSISTANT_ROUTING_MAP: dict[str, tuple[str, str]] = {
    "LSUPD-PD1": ("Landon Troxclair & Mike Morrow", "Event Payment"),
    "LSUPD-PD2": ("Josh Stephenson", "Basic Video (less than or equal to 1hr)"),
    "LSUPD-PD3": ("Josh Stephenson", "Extended video"),
    "LSUPD-PD4": ("Theresa Griffin", "Photo Request"),
    "LSUPD-PD5": ("Theresa Griffin", "Basic Report"),
}

TICKET_ASSISTANT_NO_VIDEO_REASONS = [
    "The area is not covered by LSU security cameras.",
    "Footage was not preserved.",
    "No formal report was filed.",
]

TICKET_ASSISTANT_TESSERACT_CANDIDATES = [
    os.getenv("TESSERACT_CMD", "").strip(),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "tesseract",
]

TICKET_ASSISTANT_AI_MODEL = "gpt-4o-mini"
TICKET_ASSISTANT_PAYMENT_ROUTE_FIELDS = {
    "itemcode": "itemcode",
    "amount": "amount",
    "qty": "quantity",
    "ref1val": "first_name",
    "ref2val": "last_name",
    "ref3val": "phone",
    "ref4val": "email",
    "ref5val": "lsupd_case_number",
    "ref6val": "ticket_number_tdx_id",
}

TICKET_ASSISTANT_FIELD_PATTERNS: dict[str, list[str]] = {
    "date": [r"\bdate\b\s*[:#-]?\s*([^\n\r]+)", r"\bincident date\b\s*[:#-]?\s*([^\n\r]+)", r"(?im)^sent\s*:\s*([^\n\r]+)"],
    "time": [r"\btime\b\s*[:#-]?\s*([^\n\r]+)", r"\bincident time\b\s*[:#-]?\s*([^\n\r]+)"],
    "location": [r"\blocation\b\s*[:#-]?\s*([^\n\r]+)", r"\bincident location\b\s*[:#-]?\s*([^\n\r]+)"],
    "case_number": [r"\b(?:lsupd\s*)?case\s*(?:number|#)?\b\s*[:#-]?\s*([A-Za-z0-9\-\/]+)"],
    "service_request_id": [r"\bservice request id\b\s*[:#-]?\s*([A-Za-z0-9\-]+)", r"\brequest id\b\s*[:#-]?\s*([A-Za-z0-9\-]+)"],
    "tdx_ticket_id": [r"\btdx ticket id\b\s*[:#-]?\s*([A-Za-z0-9\-]+)", r"\bticket number\b\s*[:#-]?\s*([A-Za-z0-9\-]+)", r"ref6val1[^A-Za-z0-9]*([A-Za-z0-9\-]+)", r"\btdx\b.*?\b([A-Za-z]{2,}-\d+)\b"],
    "name": [r"\bname\b\s*[:#-]?\s*([^\n\r]+)"],
    "camera_name": [r"(?im)^cam issue:\s*(.+?)\s*$", r"(?s)VMS\.\s*([^\n\r]+)\s*\nCamera Location:"],
    "issue_description": [r"(?im)^description of issue\b\s*[:#-]?\s*([^\n\r]+)"],
    "actions_taken": [r"(?im)^actions taken\b\s*[:#-]?\s*([^\n\r]+)"],
    "itemcodes": [r"\bitemcodes?\b\s*[:#-]?\s*([^\n\r]+)", r"\bitem codes?\b\s*[:#-]?\s*([^\n\r]+)"],
    "amounts": [r"\bamounts?\b\s*[:#-]?\s*([^\n\r]+)", r"\btotal\b\s*[:#-]?\s*(\$?\d[\d,]*\.?\d{0,2})"],
    "camera_location": [r"\bcamera location\b\s*[:#-]?\s*([^\n\r]+)", r"\blocation\b\s*[:#-]?\s*([^\n\r]+)"],
    "asset_id": [r"\basset id\b\s*[:#-]?\s*([^\n\r]+)", r"\basset\b\s*[:#-]?\s*([^\n\r]+)"],
    "product_model": [r"\bproduct model\b\s*[:#-]?\s*([^\n\r]+)", r"\bmodel\b\s*[:#-]?\s*([^\n\r]+)"],
    "serial_number": [r"\bserial(?: number)?\b\s*[:#-]?\s*([^\n\r]+)"],
    "service_tag": [r"\bservice tag\b\s*[:#-]?\s*([^\n\r]+)"],
    "camera_ip": [r"\bcamera ip\b\s*[:#-]?\s*([^\n\r]+)", r"\bip(?: address)?\b\s*[:#-]?\s*([^\n\r]+)"],
    "camera_server": [r"\bcamera server\b\s*[:#-]?\s*([^\n\r]+)", r"\bserver\b\s*[:#-]?\s*([^\n\r]+)"],
    "failover_server": [r"\bfailover server\b\s*[:#-]?\s*([^\n\r]+)"],
    "camera_power_source": [r"\bcamera power source\b\s*[:#-]?\s*([^\n\r]+)", r"\bpower source\b\s*[:#-]?\s*([^\n\r]+)"],
    "its_switch_ip": [r"\bits switch ip\b\s*[:#-]?\s*([^\n\r]+)"],
    "its_switch_name": [r"\bits switch name\b\s*[:#-]?\s*([^\n\r]+)"],
    "its_switch_port": [
        r"\bits switch port\b\s*[:#-]?\s*([^\n\r]+)",
        r"\bswitch port\b\s*[:#-]?\s*([^\n\r]+)",
        r"\bnetwork switch port\b\s*[:#-]?\s*([^\n\r]+)",
    ],
    "department_for_maintenance": [r"\bdepartment for maintenance\b\s*[:#-]?\s*([^\n\r]+)", r"\bmaintenance\b\s*[:#-]?\s*([^\n\r]+)"],
    "installation_company": [r"\binstallation company\b\s*[:#-]?\s*([^\n\r]+)", r"\binstalled by\b\s*[:#-]?\s*([^\n\r]+)"],
    "budget_code": [r"\bbudget code\b\s*[:#-]?\s*([^\n\r]+)"],
}


def clean_ticket_text(value: str) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def clean_extracted_value(value: str) -> str:
    text = clean_ticket_text(value)
    text = re.sub(r"\s+", " ", text).strip(" :;-")
    return "" if text.lower() in {"", "none", "null", "nan", "not provided"} else text


def find_first_pattern(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            for group in match.groups():
                value = clean_extracted_value(group)
                if value:
                    return value
    return ""


def parse_text_key_value_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for raw_line in clean_ticket_text(text).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
        elif "\t" in line:
            key, value = line.split("\t", 1)
        else:
            continue
        key_clean = clean_extracted_value(key).lower()
        value_clean = clean_extracted_value(value)
        if key_clean and value_clean and key_clean not in pairs:
            pairs[key_clean] = value_clean
    return pairs


def parse_stacked_key_value_pairs(text: str, alias_map: dict[str, str]) -> dict[str, str]:
    lines = [clean_ticket_text(line) for line in clean_ticket_text(text).splitlines()]
    normalized_aliases = {clean_extracted_value(key).lower(): value for key, value in alias_map.items()}
    pairs: dict[str, str] = {}
    for index, line in enumerate(lines):
        key_candidate = clean_extracted_value(line).lower()
        if not key_candidate or key_candidate not in normalized_aliases:
            continue
        for next_index in range(index + 1, len(lines)):
            next_line = clean_ticket_text(lines[next_index])
            next_key = clean_extracted_value(next_line).lower()
            if not next_line:
                continue
            if next_key in normalized_aliases:
                break
            if ":" in next_line and len(next_line.split(":", 1)[0].strip()) < 50:
                break
            pairs[key_candidate] = clean_extracted_value(next_line)
            break
    return pairs


def split_incident_datetime(value: str) -> tuple[str, str]:
    cleaned = clean_extracted_value(value)
    if not cleaned:
        return "", ""
    match = re.match(
        r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})[\s,]+(.+?)\s*$",
        cleaned,
        flags=re.IGNORECASE,
    )
    if match:
        return clean_extracted_value(match.group(1)), clean_extracted_value(match.group(2))
    return cleaned, ""


def maybe_set_field(field_map: dict[str, str], field_name: str, value: str) -> None:
    cleaned = clean_extracted_value(value)
    if cleaned and not clean_extracted_value(field_map.get(field_name, "")):
        field_map[field_name] = cleaned


def parse_general_ticket_fields(text: str) -> dict[str, str]:
    cleaned_text = clean_ticket_text(text)
    alias_map = {
        "lsupd case number": "case_number",
        "lsupd case number of incident (if known)": "case_number",
        "service request id": "service_request_id",
        "ticket number": "tdx_ticket_id",
        "tdx ticket id": "tdx_ticket_id",
        "date/time of incident (approximate if not known)": "incident_datetime",
        "date/time of incident": "incident_datetime",
        "location of incident": "location",
        "description": "issue_description",
        "requestor": "name",
        "camera location": "camera_location",
        "asset id": "asset_id",
        "product model": "product_model",
        "serial number": "serial_number",
        "service tag": "service_tag",
        "camera ip": "camera_ip",
        "camera server": "camera_server",
        "failover server": "failover_server",
        "camera power source": "camera_power_source",
        "its switch ip": "its_switch_ip",
        "its switch name": "its_switch_name",
        "its switch port": "its_switch_port",
        "department for maintenance": "department_for_maintenance",
        "installation company": "installation_company",
        "budget code": "budget_code",
        "location": "location",
        "date": "date",
        "time": "time",
        "name": "name",
    }
    key_value_pairs = parse_text_key_value_pairs(cleaned_text)
    key_value_pairs.update(parse_stacked_key_value_pairs(cleaned_text, alias_map))
    parsed: dict[str, str] = {field_name: "" for field_name, _ in TICKET_ASSISTANT_FIELDS}
    for field_name, patterns in TICKET_ASSISTANT_FIELD_PATTERNS.items():
        maybe_set_field(parsed, field_name, find_first_pattern(cleaned_text, patterns))
    for key, field_name in alias_map.items():
        if key in key_value_pairs:
            if field_name == "incident_datetime":
                incident_date, incident_time = split_incident_datetime(key_value_pairs[key])
                maybe_set_field(parsed, "date", incident_date)
                maybe_set_field(parsed, "time", incident_time)
            else:
                maybe_set_field(parsed, field_name, key_value_pairs[key])
    if parsed.get("service_request_id") and not parsed.get("tdx_ticket_id"):
        parsed["tdx_ticket_id"] = parsed["service_request_id"]
    return parsed


def normalize_payment_email_text(text: str) -> tuple[str, str]:
    raw_text = str(text or "")
    normalized_text = raw_text.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    normalized_text = normalized_text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    normalized_text = re.sub(r"[ \t]+", " ", normalized_text)
    normalized_text = re.sub(
        r"\s+(?=(?:tx|itemcnt|itemcode\d+|amount\d+|qty\d+|ref[1-6](?:type|val)\d+)=)",
        "\n",
        normalized_text,
        flags=re.IGNORECASE,
        )
    normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text)
    return raw_text, normalized_text.strip()


def _payment_group_sort_key(group_key: str) -> tuple[int, int | str]:
    return (0, int(group_key)) if str(group_key).isdigit() else (1, str(group_key))


def _first_non_empty_payment_value(payment_groups: dict[str, dict[str, str]], field_name: str) -> str:
    for group_key in sorted(payment_groups, key=_payment_group_sort_key):
        value = clean_extracted_value(payment_groups[group_key].get(field_name, ""))
        if value:
            return value
    return ""


def parse_payment_confirmation_email(text: str) -> tuple[dict[str, str], list[dict[str, str]], dict[str, Any]]:
    raw_text, normalized_text = normalize_payment_email_text(text)
    payment_groups: dict[str, dict[str, str]] = {}
    warnings: list[str] = []

    transaction_number = clean_extracted_value(find_first_pattern(normalized_text, [r"(?im)^tx=(.+?)\s*$"]))
    item_count = clean_extracted_value(find_first_pattern(normalized_text, [r"(?im)^itemcnt=(.+?)\s*$"]))

    for key_prefix, field_name in TICKET_ASSISTANT_PAYMENT_ROUTE_FIELDS.items():
        pattern = rf"(?im)^{re.escape(key_prefix)}(\d+)=(.+?)\s*$"
        for group_suffix, raw_value in re.findall(pattern, normalized_text):
            group = payment_groups.setdefault(str(group_suffix), {})
            group[field_name] = clean_extracted_value(raw_value)

    sorted_group_keys = sorted(payment_groups, key=_payment_group_sort_key)
    ticket_number = _first_non_empty_payment_value(payment_groups, "ticket_number_tdx_id")
    case_number = _first_non_empty_payment_value(payment_groups, "lsupd_case_number")
    first_name = _first_non_empty_payment_value(payment_groups, "first_name")
    last_name = _first_non_empty_payment_value(payment_groups, "last_name")
    name = " ".join(part for part in [first_name, last_name] if clean_extracted_value(part)).strip()
    phone = _first_non_empty_payment_value(payment_groups, "phone")
    email = _first_non_empty_payment_value(payment_groups, "email")

    comparison_fields = {
        "Ticket Number / TDX Ticket ID": "ticket_number_tdx_id",
        "LSUPD Case Number": "lsupd_case_number",
        "Phone": "phone",
        "Email": "email",
    }
    for label, field_name in comparison_fields.items():
        values = [
            clean_extracted_value(payment_groups[group_key].get(field_name, ""))
            for group_key in sorted_group_keys
            if clean_extracted_value(payment_groups[group_key].get(field_name, ""))
        ]
        if len(set(values)) > 1:
            warnings.append(f"Conflicting {label} values found across payment groups.")

    name_values = []
    for group_key in sorted_group_keys:
        group_first = clean_extracted_value(payment_groups[group_key].get("first_name", ""))
        group_last = clean_extracted_value(payment_groups[group_key].get("last_name", ""))
        group_name = " ".join(part for part in [group_first, group_last] if part).strip()
        if group_name:
            name_values.append(group_name)
    if len(set(name_values)) > 1:
        warnings.append("Conflicting Name values found across payment groups.")

    paid_items: list[dict[str, str]] = []
    for group_key in sorted_group_keys:
        group = payment_groups[group_key]
        itemcode = clean_extracted_value(group.get("itemcode", "")).upper()
        if not itemcode:
            continue
        amount = clean_extracted_value(group.get("amount", ""))
        quantity = clean_extracted_value(group.get("quantity", ""))
        routing_contacts, routing_note = TICKET_ASSISTANT_ROUTING_MAP.get(itemcode, ("", ""))
        if itemcode not in TICKET_ASSISTANT_ROUTING_MAP:
            warnings.append(f"Unmapped itemcode: {itemcode}")
        if not amount:
            warnings.append(f"Missing amount for item group {group_key}.")
        if not quantity:
            warnings.append(f"Missing qty for item group {group_key}.")
        paid_items.append({
            "group": str(group_key),
            "itemcode": itemcode,
            "routing_contacts": routing_contacts,
            "routing_note": routing_note,
            "amount": amount,
            "quantity": quantity,
        })

    if not ticket_number:
        warnings.append("Missing ticket ID.")
    if not case_number:
        warnings.append("Missing case number.")
    if not name:
        warnings.append("Missing name.")

    parsed = parse_general_ticket_fields(normalized_text)
    parsed["ticket_number"] = ticket_number
    parsed["tdx_ticket_id"] = ticket_number
    parsed["case_number"] = case_number
    parsed["name"] = name
    sent_date = clean_extracted_value(
        find_first_pattern(
            raw_text,
            [
                r"(?im)^sent\s*:\s*([^\n\r]+)",
                r"(?im)^date\s*:\s*([^\n\r]+)",
            ],
        )
    )
    if sent_date:
        parsed["date"] = sent_date
    parsed["itemcodes"] = "\n".join(item["itemcode"] for item in paid_items)
    parsed["amounts"] = "\n".join(
        f"${float(item['amount']):.2f}" for item in paid_items if clean_extracted_value(item.get("amount", ""))
        )

    result = {
        "raw_text": raw_text,
        "normalized_text": normalized_text,
        "transaction_number": transaction_number,
        "item_count": item_count,
        "ticket_number_tdx_id": ticket_number,
        "lsupd_case_number": case_number,
        "name": name,
        "phone": phone,
        "email": email,
        "payment_groups": payment_groups,
        "paid_items": paid_items,
        "warnings": warnings,
    }
    return parsed, paid_items, result


def parse_camera_asset_record(text: str) -> dict[str, str]:
    parsed = parse_general_ticket_fields(text)
    if not parsed.get("camera_location") and parsed.get("location"):
        parsed["camera_location"] = parsed["location"]
    return parsed


def extract_vendor_issue_description(text: str) -> str:
    cleaned_text = clean_ticket_text(text)
    status_match = re.search(
        r"(?is)Changed Status.*?\.\s*(.+?)(?:\n\s*Notified:|\n\s*Requestor\b|\n\s*Attachments\b|\n\s*Read By\b)",
        cleaned_text,
    )
    if status_match:
        block = status_match.group(1)
        lines: list[str] = []
        for raw_line in block.splitlines():
            line = clean_ticket_text(raw_line)
            if not line:
                continue
            if re.match(r"^(hi|hello|hey)\b", line, flags=re.IGNORECASE):
                continue
            if re.match(r"^[A-Z][a-z]{2}\s+\d{1,2}/\d{1,2}/\d{2,4}", line):
                continue
            lines.append(line)
        if lines:
            return " ".join(lines).strip()

    for raw_line in cleaned_text.splitlines():
        line = clean_ticket_text(raw_line)
        if any(marker in line.lower() for marker in ["not pingable", "start-up loop", "configuration and power look good", "switch shows"]):
            return line
    return ""


def extract_tdx_note_entries(text: str) -> list[tuple[pd.Timestamp, str]]:
    cleaned_text = clean_ticket_text(text)
    timestamp_pattern = re.compile(
        r"^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})\s+\d{1,2}:\d{2}\s*(?:AM|PM)$",
        flags=re.IGNORECASE,
    )
    action_markers = [
        "changed status",
        "comment",
        "not pingable",
        "start-up loop",
        "configuration and power",
        "switch shows",
        "mac address",
        "tested the line",
    ]
    entries: list[tuple[pd.Timestamp, str]] = []
    current_lines: list[str] = []

    for raw_line in cleaned_text.splitlines():
        line = clean_ticket_text(raw_line)
        if not line:
            continue
        current_lines.append(line)
        if timestamp_pattern.match(line):
            timestamp_text = current_lines[-1]
            block_lines = current_lines[:-1]
            block_text = "\n".join(block_lines).strip()
            current_lines = []
            if not block_text:
                continue
            if not any(marker in block_text.lower() for marker in action_markers):
                continue
            parsed_ts = pd.to_datetime(timestamp_text, errors="coerce")
            if pd.isna(parsed_ts):
                continue
            entries.append((parsed_ts, block_text))

    entries.sort(key=lambda item: item[0])
    return entries


def extract_action_items_from_note_block(block_text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", clean_ticket_text(block_text))
    actions: list[str] = []
    for sentence in sentences:
        cleaned_sentence = clean_ticket_text(sentence).strip(". ")
        if not cleaned_sentence:
            continue
        if re.match(r"^(hi|hello|hey)\b", cleaned_sentence, flags=re.IGNORECASE):
            continue
        if cleaned_sentence.lower().startswith("changed status"):
            continue
        if cleaned_sentence.lower().startswith("notified:"):
            continue
        lowered_sentence = cleaned_sentence.lower()

        action = ""
        if "configuration and power" in lowered_sentence:
            action = "Configuration and power checked - Good" if any(token in lowered_sentence for token in ["look good", "looks good", "good"]) else "Configuration and power checked - Completed"
        elif "tested the line from the camera to the closet" in lowered_sentence:
            action = "Line from camera to closet tested - Good" if any(token in lowered_sentence for token in ["look good", "looks good", "good"]) else "Line from camera to closet tested - Completed"
        elif "not pingable" in lowered_sentence:
            action = "Camera ping test - Failed"
        elif "mac address" in lowered_sentence and any(token in lowered_sentence for token in ["does not show up", "doesn't show up", "did not show up", "not show up"]):
            action = "MAC address visibility on switch port - Failed"
        elif "start-up loop" in lowered_sentence:
            action = "Camera boot stability - Failed (appears stuck in a start-up loop)"
        elif "switch shows" in lowered_sentence and "few seconds" in lowered_sentence:
            action = "Switch port link stability - Failed (camera only stays up for a few seconds)"
        else:
            status = "Completed"
            if any(token in lowered_sentence for token in ["not ", "failed", "stuck", "does not", "did not", "unable", "loop"]):
                status = "Failed"
            elif any(token in lowered_sentence for token in ["good", "looks good", "look good", "success", "passed"]):
                status = "Good"
            action = f"{cleaned_sentence} - {status}"

        if action and action not in actions:
            actions.append(action)
    return actions


def extract_vendor_action_items(text: str) -> list[str]:
    ordered_entries = extract_tdx_note_entries(text)
    if ordered_entries:
        ordered_actions: list[str] = []
        for _, block_text in ordered_entries:
            for action in extract_action_items_from_note_block(block_text):
                if action not in ordered_actions:
                    ordered_actions.append(action)
        if ordered_actions:
            return ordered_actions

    return extract_action_items_from_note_block(text)


def extract_tdx_incident_id(text: str) -> str:
    return clean_extracted_value(find_first_pattern(text, [r"(?im)^incident id\s*:\s*([A-Za-z0-9\-]+)"]))


def extract_vendor_reference(text: str) -> str:
    return clean_extracted_value(find_first_pattern(text, [r"(?<!incident id:)\B#(\d{5,})\b", r"(?im)\bvendor (?:case|ticket)\b.*?#?(\d{5,})"]))


def extract_vendor_action_requests(text: str) -> list[str]:
    request_keywords = ["seal", "watertight", "repair", "replace", "rma", "dispatch", "technician", "terminate", "termination"]
    ordered_entries = extract_tdx_note_entries(text)
    candidate_blocks = [block_text for _, block_text in reversed(ordered_entries)] if ordered_entries else [clean_ticket_text(text)]
    requests: list[str] = []
    for block_text in candidate_blocks:
        sentences = re.split(r"(?<=[.!?])\s+", clean_ticket_text(block_text))
        for sentence in sentences:
            cleaned_sentence = clean_ticket_text(sentence).strip(". ")
            if not cleaned_sentence:
                continue
            lowered = cleaned_sentence.lower()
            if any(keyword in lowered for keyword in request_keywords):
                if cleaned_sentence not in requests:
                    requests.append(cleaned_sentence)
            if len(requests) >= 3:
                return requests
    return requests


def extract_vendor_issue_summary(source_text: str, fields: dict[str, str]) -> list[str]:
    bullets: list[str] = []
    normalized = clean_ticket_text(source_text).lower()
    if "cannot be pinged nor is it connected to the vms" in normalized:
        bullets.append("Camera cannot be pinged and is not connected to the VMS.")
    if "not pingable" in normalized and "Camera remains not pingable." not in bullets:
        bullets.append("Camera remains not pingable.")
    if "mac address does not show up on the port" in normalized:
        bullets.append("MAC address does not appear on the switch port.")
    if "start-up loop" in normalized:
        bullets.append("Camera appears to be stuck in a start-up loop.")
    if "few seconds at a time" in normalized:
        bullets.append("Switch shows the camera is only up for a few seconds at a time.")
    if "corrosion" in normalized:
        bullets.append("Corrosion was observed.")
    if "water intrusion" in normalized or "water in" in normalized:
        bullets.append("Water intrusion was observed.")

    issue_description = clean_extracted_value(fields.get("issue_description", ""))
    if issue_description and issue_description not in bullets:
        bullets.append(issue_description)

    return bullets[:5]


def extract_vendor_notes_evidence(source_text: str, fields: dict[str, str]) -> list[str]:
    notes: list[str] = []
    actions_taken_text = clean_ticket_text(fields.get("actions_taken", ""))
    for line in actions_taken_text.splitlines():
        cleaned = clean_ticket_text(line)
        if cleaned and cleaned not in notes:
            notes.append(cleaned)

    normalized = clean_ticket_text(source_text)
    evidence_patterns = [
        r"(?im)^.*not pingable.*$",
        r"(?im)^.*mac address.*port.*$",
        r"(?im)^.*start-up loop.*$",
        r"(?im)^.*corrosion.*$",
        r"(?im)^.*water intrusion.*$",
        r"(?im)^.*interface down.*$",
    ]
    for pattern in evidence_patterns:
        match = re.search(pattern, normalized)
        if match:
            cleaned = clean_ticket_text(match.group(0)).strip(". ")
            if cleaned and cleaned not in notes:
                notes.append(cleaned)
    return notes[:5]


def extract_tdx_ticket_title(text: str) -> str:
    title = clean_extracted_value(find_first_pattern(text, [r"(?im)^cam issue:\s*(.+?)\s*$"]))
    title = re.sub(r"\s+(?:open|closed|assigned|on hold|waiting on customer)\s*$", "", title, flags=re.IGNORECASE)
    return clean_extracted_value(title)


def extract_requestor_contact(text: str) -> tuple[str, str, str]:
    cleaned_text = clean_ticket_text(text)
    direct_pairs = parse_stacked_key_value_pairs(cleaned_text, {"requestor": "name", "alternative contact": "alt_contact"})
    name = clean_extracted_value(direct_pairs.get("requestor", ""))
    email = ""
    phone = ""
    alt_contact = clean_extracted_value(direct_pairs.get("alternative contact", ""))
    if alt_contact:
        phone_match = re.search(r"(\+?1?\s*\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})", alt_contact)
        if phone_match:
            phone = clean_ticket_text(phone_match.group(1))
        if not name:
            alt_name = clean_ticket_text(re.split(r",|\d{3}[\s\-]?\d{3}[\s\-]?\d{4}", alt_contact)[0])
            if alt_name:
                name = alt_name
    block_match = re.search(
        r"(?is)\bRequestor\b\s*(.+?)(?:\n\s*Attachments\b|\n\s*Read By\b|\n\s*LSU\b|\Z)",
        cleaned_text,
    )
    block = block_match.group(1) if block_match else cleaned_text
    lines = [clean_ticket_text(line) for line in block.splitlines() if clean_ticket_text(line)]
    for line in lines:
        if not email:
            email_match = re.search(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", line, flags=re.IGNORECASE)
            if email_match:
                email = email_match.group(0)
        if not phone:
            phone_match = re.search(r"(\+?1?\s*\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})", line)
            if phone_match:
                phone = clean_ticket_text(phone_match.group(1))
        if not name and line.lower() != "requestor" and "@" not in line and not re.search(r"\d{3}[\s\-]?\d{3}[\s\-]?\d{4}", line):
            name = line
    posted_by_match = re.search(
        r"(?im)^Posted By:\s*([^<\n\r]+?)(?:\s*<([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})>)?\s*$",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    if posted_by_match:
        if not name:
            name = clean_ticket_text(posted_by_match.group(1))
        if not email and posted_by_match.group(2):
            email = clean_ticket_text(posted_by_match.group(2))
    return clean_extracted_value(name), clean_extracted_value(email), clean_extracted_value(phone)


def extract_vendor_work_performed(source_text: str, fields: dict[str, str]) -> list[str]:
    work_items: list[str] = []
    actions_taken_text = clean_ticket_text(fields.get("actions_taken", ""))
    for line in actions_taken_text.splitlines():
        cleaned = clean_ticket_text(line).strip(". ")
        if cleaned and cleaned not in work_items:
            work_items.append(cleaned)

    normalized = clean_ticket_text(source_text)
    summary_patterns = [
        (r"(?im)^.*re-terminated.*$", None),
        (r"(?im)^.*camera is pingable again.*$", None),
        (r"(?im)^.*properly networked.*$", None),
        (r"(?im)^.*found that the device.*require outside resources.*$", None),
        (r"(?im)^.*water had made its way.*corrosion.*$", "Water intrusion and corrosion were found in the junction box."),
        (r"(?im)^.*made the repair on\s+([0-9/]+).*$", lambda m: f"Repair was performed on {m.group(1)}."),
    ]
    for pattern, replacement in summary_patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        if callable(replacement):
            cleaned = clean_ticket_text(replacement(match))
        elif isinstance(replacement, str):
            cleaned = replacement
        else:
            cleaned = clean_ticket_text(match.group(0)).strip(". ")
        if cleaned and cleaned not in work_items:
            work_items.append(cleaned)
    return work_items[:3]


def extract_vendor_evidence_summary(source_text: str) -> list[str]:
    evidence: list[str] = []
    normalized = clean_ticket_text(source_text)

    ping_match = re.search(
        r"(?is)Ping statistics for\s+([0-9.]+)\s*:\s*Packets:\s*Sent\s*=\s*(\d+),\s*Received\s*=\s*(\d+),\s*Lost\s*=\s*(\d+)\s*\((\d+)%\s*loss\)",
        normalized,
    )
    if ping_match:
        evidence.append(
            f"Ping to {ping_match.group(1)} showed {ping_match.group(2)} sent, {ping_match.group(3)} received, {ping_match.group(4)} lost ({ping_match.group(5)}% loss)."
        )

    interface_match = re.search(
        r"(?is)(?:sh int|show int)\s+([0-9/]+).*?Interface\s+\1\s+is\s+down.*?Link state:\s+down\s+for\s+(.+?)(?:\n|$)",
        normalized,
    )
    if interface_match:
        evidence.append(f"Switch port {interface_match.group(1)} reported link down for {clean_ticket_text(interface_match.group(2)).rstrip('.')}.")

    short_patterns = [
        (r"(?im)^.*water had made its way.*$", None),
        (r"(?im)^.*corrosion.*$", None),
        (r"(?im)^.*camera is pingable again.*$", None),
        (r"(?im)^.*not pingable.*$", None),
    ]
    for pattern, replacement in short_patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        cleaned = replacement or clean_ticket_text(match.group(0)).strip(". ")
        if cleaned and cleaned not in evidence:
            evidence.append(cleaned)
    return evidence[:2]


def parse_vendor_escalation_record(text: str) -> dict[str, str]:
    parsed = parse_camera_asset_record(text)
    camera_name = clean_extracted_value(parsed.get("camera_name", ""))
    if not camera_name:
        camera_name = clean_extracted_value(
            find_first_pattern(
                text,
                [
                    r"(?im)^cam issue:\s*(.+?)\s*$",
                    r"(?s)The following camera cannot be pinged nor is it connected to the VMS\.\s*([^\n\r]+)\s*\nCamera Location:",
                ],
            )
        )
    if camera_name:
        parsed["camera_name"] = camera_name
    issue_description = extract_vendor_issue_description(text)
    if issue_description:
        parsed["issue_description"] = issue_description
    action_items = extract_vendor_action_items(text)
    if action_items:
        parsed["actions_taken"] = "\n".join(action_items)
    return parsed


def detect_ticket_assistant_workflow(text: str) -> str:
    normalized = clean_ticket_text(text).lower()
    if not normalized:
        return "General Ticket Review"
    payment_markers = ["noreply@bursar.lsu.edu", "cashnet", "itemcode", "ref6val1", "payment", "lsupd-pd"]
    if sum(1 for marker in payment_markers if marker in normalized) >= 2:
        return "Payment Confirmation Email"
    vendor_markers = [
        "changed status",
        "waiting on customer",
        "how you'd like to proceed",
        "requestor",
        "attachments",
        "start-up loop",
        "configuration and power look good",
        "still not pingable",
    ]
    if ("cam issue:" in normalized or "incident id:" in normalized) and sum(1 for marker in vendor_markers if marker in normalized) >= 2:
        return "Vendor Escalation Response"
    asset_markers = [
        "camera location",
        "asset id",
        "product model",
        "camera i.p. address",
        "camera ip",
        "camera server",
        "its switch",
    ]
    if sum(1 for marker in asset_markers if marker in normalized) >= 2:
        return "Camera Asset Record"
    if sum(1 for marker in vendor_markers if marker in normalized) >= 2:
        return "Vendor Escalation Response"
    if "didn't work" in normalized and ("standalone player" in normalized or "player link" in normalized):
        return "Link Re-upload Response"
    if "no video" in normalized or "no footage" in normalized:
        return "No Video Available Response"
    if "standalone player" in normalized or "avigilon player" in normalized:
        return "Paid Video Link Delivery"
    video_markers = ["video", "footage", "avigilon", "case number", "lsupd case", "incident", "preserved", "service request"]
    if sum(1 for marker in video_markers if marker in normalized) >= 2:
        return "Camera System Video Request"
    return "General Ticket Review"


def apply_parsed_fields_to_session(parsed_fields: dict[str, str], overwrite: bool = False) -> None:
    for field_name, _ in TICKET_ASSISTANT_FIELDS:
        key = f"tra_field_{field_name}"
        current_value = clean_extracted_value(st.session_state.get(key, ""))
        parsed_value = clean_extracted_value(parsed_fields.get(field_name, ""))
        if parsed_value and (overwrite or not current_value):
            st.session_state[key] = parsed_value


def resolve_tesseract_command() -> str:
    for candidate in TICKET_ASSISTANT_TESSERACT_CANDIDATES:
        if not candidate:
            continue
        if os.path.isabs(candidate):
            if os.path.exists(candidate):
                return candidate
            continue
        try:
            result = subprocess.run(
                ["where.exe", candidate],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if result.returncode == 0:
                first_match = clean_ticket_text(result.stdout).splitlines()
                if first_match:
                    return first_match[0].strip()
        except Exception:
            continue
    return ""


def extract_ticket_data_with_openai(text: str, api_key: str) -> tuple[dict[str, str], list[dict[str, str]], list[str], str]:
    if OpenAI is None:
        return {}, [], ["OpenAI package is not available in this environment."], ""
    cleaned_text = clean_ticket_text(text)
    if not cleaned_text:
        return {}, [], [], ""

    schema_properties = {field_name: {"type": "string"} for field_name, _ in TICKET_ASSISTANT_FIELDS}
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=TICKET_ASSISTANT_AI_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "Extract LSU ticket-processing data from the user text. "
                    "Do not guess missing values. Use empty strings for missing fields. "
                    "Only capture facts stated in the input."
                ),
            },
            {
                "role": "user",
                "content": cleaned_text,
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ticket_assistant_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "suggested_workflow": {
                            "type": "string",
                            "enum": TICKET_ASSISTANT_WORKFLOWS[1:],
                        },
                        "fields": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": schema_properties,
                            "required": [field_name for field_name, _ in TICKET_ASSISTANT_FIELDS],
                        },
                        "line_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "itemcode": {"type": "string"},
                                    "amount": {"type": "string"},
                                },
                                "required": ["itemcode", "amount"],
                            },
                        },
                        "warnings": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["suggested_workflow", "fields", "line_items", "warnings"],
                },
            }
        },
    )
    payload = json.loads(response.output_text)
    fields = payload.get("fields", {})
    line_items = payload.get("line_items", [])
    warnings = payload.get("warnings", [])
    suggested_workflow = clean_extracted_value(payload.get("suggested_workflow", ""))
    cleaned_fields = {
        field_name: clean_extracted_value(fields.get(field_name, ""))
        for field_name, _ in TICKET_ASSISTANT_FIELDS
    }
    cleaned_items = []
    for item in line_items:
        cleaned_items.append(
            {
                "itemcode": clean_extracted_value(item.get("itemcode", "")),
                "amount": clean_extracted_value(item.get("amount", "")),
            }
        )
    return cleaned_fields, cleaned_items, [clean_ticket_text(w) for w in warnings if clean_ticket_text(w)], suggested_workflow


def extract_text_from_image_bytes(raw_bytes: bytes, suffix: str = ".png") -> tuple[str, str]:
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image:
            temp_image.write(raw_bytes)
            temp_path = temp_image.name
        tesseract_command = resolve_tesseract_command()
        if not tesseract_command:
            return "", "OCR unavailable on this machine. Install Tesseract or paste the text manually."
        result = subprocess.run(
            [tesseract_command, temp_path, "stdout"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        extracted = clean_ticket_text(result.stdout)
        if result.returncode != 0 or not extracted:
            error_text = clean_ticket_text(result.stderr) or "OCR did not return readable text."
            return "", error_text
        return extracted, ""
    except Exception as exc:
        return "", f"OCR failed: {exc}"
    finally:
        try:
            if temp_path:
                os.unlink(temp_path)
        except Exception:
            pass


def extract_text_from_uploaded_file(uploaded_file: Any) -> tuple[str, str]:
    file_name = str(getattr(uploaded_file, "name", "upload")).lower()
    raw_bytes = uploaded_file.getvalue()
    if file_name.endswith((".txt", ".csv", ".log", ".json", ".eml", ".md")):
        return decode_site_health_csv_bytes(raw_bytes), ""
    if file_name.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")):
        return extract_text_from_image_bytes(raw_bytes, os.path.splitext(file_name)[1] or ".png")
    return "", f"{uploaded_file.name}: unsupported file type"


def format_payment_item_quantity(itemcode: str, quantity: str) -> str:
    qty_text = clean_extracted_value(quantity)
    if not qty_text:
        return ""
    if itemcode == "LSUPD-PD4":
        return f" (Qty {qty_text})"
    return "" if qty_text == "1" else f" (Qty {qty_text})"


def infer_media_request_quantities(text: str) -> tuple[int, int]:
    normalized = clean_ticket_text(text).lower()
    explicit_photo_qty = re.search(r"\b(\d+)\s+(?:photos?|images?)\b", normalized)
    explicit_video_qty = re.search(r"\b(\d+)\s+videos?\b", normalized)

    photo_qty = int(explicit_photo_qty.group(1)) if explicit_photo_qty else 0
    video_qty = int(explicit_video_qty.group(1)) if explicit_video_qty else 0

    if photo_qty == 0 and re.search(r"\bphotos?\b", normalized):
        photo_qty = 1
    if video_qty == 0 and re.search(r"\bvideos?\b", normalized):
        video_qty = 1

    return photo_qty, video_qty


def build_general_ticket_review_output(text: str, fields: dict[str, str]) -> str:
    cleaned_text = clean_ticket_text(text)
    lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
    summary = ""
    if lines:
        summary = " ".join(lines[:2])
        if len(summary) > 240:
            summary = summary[:237].rstrip() + "..."

    key_lines: list[str] = []
    field_map = [
        ("Ticket/Request ID", fields.get("service_request_id") or fields.get("ticket_number") or fields.get("tdx_ticket_id") or ""),
        ("Location", fields.get("location", "")),
        ("Building", clean_extracted_value(find_first_pattern(cleaned_text, [r"(?im)^building\s*[:#-]?\s*(.+?)\s*$"]))),
        ("Room/Door/Camera", fields.get("camera_location") or clean_extracted_value(find_first_pattern(cleaned_text, [r"(?im)^(?:room|door|camera)\s*[:#-]?\s*(.+?)\s*$"]))),
        ("System", clean_extracted_value(find_first_pattern(cleaned_text, [r"(?im)^system\s*[:#-]?\s*(.+?)\s*$", r"\b(access control|video|lpr|blue light)\b"]))),
        ("Asset ID", fields.get("asset_id", "")),
        ("IP Address", fields.get("camera_ip", "")),
        ("Switch Name", fields.get("its_switch_name", "")),
        ("Switch IP", fields.get("its_switch_ip", "")),
        ("Switch Port", fields.get("its_switch_port", "")),
        ("Department/Owner", fields.get("department_for_maintenance", "")),
        ("Vendor/Installer", fields.get("installation_company", "")),
        ("Priority/Urgency", clean_extracted_value(find_first_pattern(cleaned_text, [r"(?im)^(?:priority|urgency)\s*[:#-]?\s*(.+?)\s*$"]))),
    ]
    for label, value in field_map:
        cleaned = clean_extracted_value(value)
        if cleaned:
            key_lines.append(f"- {label}: {cleaned}")

    action_needed = clean_extracted_value(
        find_first_pattern(
            cleaned_text,
            [
                r"(?im)^action needed\s*[:#-]?\s*(.+?)\s*$",
                r"(?im)^requested action\s*[:#-]?\s*(.+?)\s*$",
            ],
        )
    )
    if not action_needed:
        if "access control" in cleaned_text.lower():
            action_needed = "Review the pasted access control scope and route it to the appropriate owner."
        elif "video" in cleaned_text.lower() or "camera" in cleaned_text.lower():
            action_needed = "Review the pasted video-system details and determine the next ticket update or routing step."
        else:
            action_needed = "Review the pasted details and route the request based on the stated issue."

    output_lines = [f"Summary: {summary or 'No clear summary available from the paste.'}", "Key Fields:"]
    output_lines.extend(key_lines)
    output_lines.append(f"Action Needed: {action_needed}")
    return "\n".join(output_lines).strip()


def build_payment_confirmation_output(fields: dict[str, str], line_items: list[dict[str, str]]) -> str:
    payment_data = st.session_state.get("tra_payment_data", {}) or {}
    tdx_ticket_id = clean_extracted_value(payment_data.get("ticket_number_tdx_id", "")) or clean_extracted_value(fields.get("tdx_ticket_id", "")) or "Not provided"
    name = clean_extracted_value(payment_data.get("name", "")) or fields.get("name") or ""
    phone = clean_extracted_value(payment_data.get("phone", ""))
    email = clean_extracted_value(payment_data.get("email", ""))
    case_number = clean_extracted_value(payment_data.get("lsupd_case_number", "")) or clean_extracted_value(fields.get("case_number", ""))
    player_link = clean_extracted_value(st.session_state.get("tra_player_link", "")) or TICKET_ASSISTANT_DEFAULT_PLAYER_LINK
    video_link = clean_extracted_value(st.session_state.get("tra_video_link", ""))

    paid_itemcodes = {clean_extracted_value(item.get("itemcode", "")).upper() for item in line_items}
    has_video_item = bool({"LSUPD-PD2", "LSUPD-PD3"} & paid_itemcodes)
    extra_paid_items = [
        item for item in line_items
        if clean_extracted_value(item.get("itemcode", "")).upper() not in {"LSUPD-PD2", "LSUPD-PD3"}
    ]

    lines = []
    if name:
        lines.append(f"Requestor: {name}")
    if phone:
        lines.append(f"Phone: {phone}")
    if email:
        lines.append(f"Email: {email}")
    if lines:
        lines.append("")

    if has_video_item or video_link:
        lines.extend([
            "Please use the following links to download both the video surveillance and the required standalone player.",
            "Ensure both files are downloaded to your computer before attempting to open the video.",
            "Start by installing the player, then open the video file.",
            "",
            "Avigilon Player",
            player_link,
            "",
            f"{case_number or tdx_ticket_id} Video Surveillance",
            video_link or "[video link]",
            "",
            "Note: This is not compatible with Mac devices.",
        ])
        if st.session_state.get("tra_include_thanks", True):
            lines.append("Thank you...")
    else:
        lines.extend([
            f"TDX Ticket ID: {tdx_ticket_id}",
            "",
            "Paid Items:",
        ])
        if line_items:
            for item in line_items:
                code = item.get("itemcode", "")
                amount = item.get("amount", "")
                contacts = item.get("routing_contacts", "")
                note = item.get("routing_note", "")
                if amount:
                    lines.append(f'{code} -> {contacts} -> "{note}" - ${float(amount):.2f}')
                else:
                    lines.append(f'{code} -> {contacts} -> "{note}"')
        else:
            lines.append("")

    if extra_paid_items:
        lines.extend(["", "Additional Paid Items:"])
        for item in extra_paid_items:
            code = item.get("itemcode", "")
            amount = item.get("amount", "")
            note = item.get("routing_note", "")
            if amount:
                lines.append(f"- {code}: {note} - ${float(amount):.2f}")
            else:
                lines.append(f"- {code}: {note}")
    return "\n".join(lines).strip()


def build_camera_asset_email(fields: dict[str, str]) -> str:
    serial_or_service_tag = fields.get("serial_number") or fields.get("service_tag") or ""
    ordered_pairs = [
        ("Camera Location", fields.get("camera_location", "")),
        ("Asset ID", fields.get("asset_id", "")),
        ("Product Model", fields.get("product_model", "")),
        ("MAC Address", serial_or_service_tag),
        ("Camera IP", fields.get("camera_ip", "")),
        ("Camera Server", fields.get("camera_server", "")),
        ("Failover Server", fields.get("failover_server", "")),
        ("Camera Power Source", fields.get("camera_power_source", "")),
        ("ITS Switch IP", fields.get("its_switch_ip", "")),
        ("ITS Switch Name", fields.get("its_switch_name", "")),
        ("ITS Switch Port", fields.get("its_switch_port", "")),
        ("Department for Maintenance", fields.get("department_for_maintenance", "")),
    ]
    lines = ["The following camera cannot be pinged nor is it connected to the VMS. Please troubleshoot configurations and cycle the power to the port.", ""]
    for label, value in ordered_pairs:
        cleaned = clean_extracted_value(value)
        if cleaned:
            lines.append(f"- {label}: {cleaned}")
    return "\n".join(lines).strip()


def build_vendor_escalation_output(fields: dict[str, str], source_text: str = "") -> str:
    def append_section(lines: list[str], heading: str, bullets: list[str]) -> None:
        clean_bullets = [clean_ticket_text(bullet) for bullet in bullets if clean_ticket_text(bullet)]
        if not clean_bullets:
            return
        if lines:
            lines.append("")
        lines.append(heading)
        lines.append("")
        for index, bullet in enumerate(clean_bullets):
            lines.append(bullet)
            if index < len(clean_bullets) - 1:
                lines.append("")

    incident_id = extract_tdx_incident_id(source_text)
    ticket_title = extract_tdx_ticket_title(source_text)
    camera_location = clean_extracted_value(fields.get("camera_location", ""))
    camera_name = clean_extracted_value(fields.get("camera_name", "")) or camera_location or ticket_title
    subject_target = camera_location or ticket_title
    subject_parts = ["Subject: Vendor service request"]
    if subject_target:
        subject_parts.append(subject_target)
    if incident_id:
        subject_parts.append(f"TDX {incident_id}")

    serial_or_service_tag = clean_extracted_value(fields.get("serial_number", "")) or clean_extracted_value(fields.get("service_tag", ""))
    installation_company = clean_extracted_value(fields.get("installation_company", ""))
    requestor_name, requestor_email, requestor_phone = extract_requestor_contact(source_text)
    issue_summary = extract_vendor_issue_summary(source_text, fields)[:3]
    work_performed = extract_vendor_work_performed(source_text, fields)
    vendor_actions = extract_vendor_action_requests(source_text)
    notes_evidence = extract_vendor_evidence_summary(source_text)
    vendor_ref = extract_vendor_reference(source_text)

    asset_detail_lines: list[str] = []
    ordered_pairs = [
        ("Camera Location", camera_location),
        ("Asset ID", fields.get("asset_id", "")),
        ("Product Model", fields.get("product_model", "")),
        ("Serial/Service Tag", serial_or_service_tag),
        ("Camera IP", fields.get("camera_ip", "")),
        ("Camera Server", fields.get("camera_server", "")),
        ("Failover Server", fields.get("failover_server", "")),
        ("Power Source", fields.get("camera_power_source", "")),
        ("ITS Switch Name", fields.get("its_switch_name", "")),
        ("ITS Switch IP", fields.get("its_switch_ip", "")),
        ("ITS Switch Port", fields.get("its_switch_port", "")),
    ]
    for label, value in ordered_pairs:
        cleaned = clean_extracted_value(value)
        if cleaned:
            asset_detail_lines.append(f"- {label}: {cleaned}")

    if "pcr360" in clean_ticket_text(source_text).lower():
        pcr_bullet = "Perform watertight sealing or repair of the exterior junction box to prevent water intrusion."
        if pcr_bullet not in vendor_actions:
            vendor_actions.append(pcr_bullet)

    lines = [camera_name] if camera_name else []
    if lines:
        lines.append("")
    lines.append(" - ".join(subject_parts))

    if installation_company:
        append_section(lines, "Vendor:", [f"- Company: {installation_company}"])

    reference_lines: list[str] = []
    if incident_id:
        reference_lines.append(f"- TDX Incident ID: {incident_id}")
    if vendor_ref:
        reference_lines.append(f"- Vendor Ticket/Ref: {vendor_ref}")
    append_section(lines, "Reference:", reference_lines)

    append_section(lines, "Asset details:", asset_detail_lines)

    append_section(lines, "Issue:", [f"- {item}" for item in issue_summary])

    append_section(lines, "Work already performed:", [f"- {item}" for item in work_performed[:3]])

    append_section(lines, "Vendor action requested:", [f"- {item}" for item in vendor_actions[:3]])

    append_section(lines, "Evidence (keep brief):", [f"- {item}" for item in notes_evidence[:2]])

    contact_parts = [part for part in [requestor_name, requestor_email, requestor_phone] if part]
    if contact_parts:
        append_section(lines, "Contacts (only if present in paste and relevant):", [f"- Requestor: {' - '.join(contact_parts)}"])

    lines.extend(["", "END."])
    return "\n".join(lines).strip()


def validate_ticket_assistant_fields(workflow: str, fields: dict[str, str]) -> list[str]:
    required_map = {
        "Camera System Video Request": ["date", "time", "location", "case_number", "service_request_id"],
        "No Video Available Response": ["date", "location", "case_number"],
        "Paid Video Link Delivery": ["case_number"],
        "Payment Confirmation Email": ["tdx_ticket_id"],
        "Vendor Escalation Response": ["camera_name"],
    }
    labels = dict(TICKET_ASSISTANT_FIELDS)
    missing: list[str] = []
    for field_name in required_map.get(workflow, []):
        if not clean_extracted_value(fields.get(field_name, "")):
            missing.append(labels[field_name])
    return missing


def generate_ticket_assistant_output(workflow: str, fields: dict[str, str], line_items: list[dict[str, str]], source_text: str = "") -> tuple[str, list[str]]:
    missing = validate_ticket_assistant_fields(workflow, fields)
    date_text = fields.get("date", "")
    time_text = fields.get("time", "")
    location_text = fields.get("location", "")
    case_number = fields.get("case_number", "")
    service_request_id = fields.get("service_request_id", "") or fields.get("tdx_ticket_id", "")

    if workflow == "Camera System Video Request":
        output = "\n".join([
            f"The requested video for the {date_text} incident at {time_text} at {location_text}, related to LSUPD Case Number {case_number}, has been preserved from deletion.",
            "To proceed with fulfillment, a 25-dollar processing fee is required.",
            "Please submit payment here: https://commerce.cashnet.com/LSUPD",
            "",
            "When prompted, select Incident Report Basic Video from the available options.",
            f"Be sure to include the ticket number {service_request_id} in the payment form to avoid delays.",
            "Once payment is received, an update to this ticket will be provided with download links to the video.",
        ])
        return output.strip(), missing

    if workflow == "Multi-Media Fee Response":
        inferred_photo_qty, inferred_video_qty = infer_media_request_quantities(source_text)
        photo_qty = int(st.session_state.get("tra_photo_quantity", 0) or 0) or inferred_photo_qty
        video_qty = int(st.session_state.get("tra_video_quantity", 0) or 0) or inferred_video_qty
        total_due = (photo_qty * 5.0) + (video_qty * 25.0)
        lines = []
        if photo_qty > 0:
            lines.append(f"Photos: $5.00 each - select Incident Report Photo Fee, quantity {photo_qty}")
        if video_qty > 0:
            lines.append(f"Video (each): $25.00 - select Incident Report Basic Video, quantity {video_qty}")
        if not lines:
            missing.append("At least one photo or video quantity")
        lines.extend([
            "",
            f"Total amount due: ${total_due:.2f}",
            f"Include the Service Request ID {service_request_id} in the payment form.",
            "Links will be provided after payment is received.",
        ])
        return "\n".join(lines).strip(), missing

    if workflow == "No Video Available Response":
        reason = clean_extracted_value(st.session_state.get("tra_no_video_reason_custom", "")) or clean_extracted_value(st.session_state.get("tra_no_video_reason", ""))
        output = "\n".join([
            f"No video surveillance was secured for the {date_text} incident at {location_text}, related to LSUPD Case Number {case_number}.",
            f"{reason or 'The area is not covered by LSU security cameras / footage was not preserved / no formal report was filed.'}",
            "As a result, no footage is available, and no further action can be taken on this request.",
        ])
        return output.strip(), missing

    if workflow == "Paid Video Link Delivery":
        player_link = clean_extracted_value(st.session_state.get("tra_player_link", "")) or TICKET_ASSISTANT_DEFAULT_PLAYER_LINK
        video_link = clean_extracted_value(st.session_state.get("tra_video_link", ""))
        if not video_link:
            missing.append("Video link")
        lines = [
            "Please use the following links to download both the video surveillance and the required standalone player.",
            "Ensure both files are downloaded to your computer before attempting to open the video.",
            "Start by installing the player, then open the video file.",
            "",
            "Avigilon Player",
            player_link,
            "",
            f"{case_number} Video Surveillance",
            video_link,
            "",
            "Note: This is not compatible with Mac devices.",
        ]
        if st.session_state.get("tra_include_thanks", True):
            lines.append("Thank you.")
        return "\n".join(lines).strip(), missing

    if workflow == "Link Re-upload Response":
        new_player_link = clean_extracted_value(st.session_state.get("tra_new_player_link", ""))
        existing_video_link = clean_extracted_value(st.session_state.get("tra_existing_video_link", ""))
        if not new_player_link:
            missing.append("New player link")
        if not existing_video_link:
            missing.append("Existing video link")
        output = "\n".join([
            "After testing the links, it appears the Standalone Player was the one that didn't work.",
            f"I've created a new link here: {new_player_link}",
            f"The previous link for the actual video file still functions: {existing_video_link}",
            "Copy/download both to your computer prior to trying to open. Start with the player and then open the video.",
        ])
        return output.strip(), missing

    if workflow == "Camera Asset Record":
        return build_camera_asset_email(fields), missing

    if workflow == "Vendor Escalation Response":
        return build_vendor_escalation_output(fields, source_text), missing

    if workflow == "Payment Confirmation Email":
        return build_payment_confirmation_output(fields, line_items), missing

    return build_general_ticket_review_output(source_text, fields), missing


def render_copy_button(text: str, button_label: str, component_key: str) -> None:
    payload = json.dumps(text or "")
    disabled_attr = "disabled" if not text else ""
    cursor_style = "not-allowed" if not text else "pointer"
    opacity = "0.55" if not text else "1"
    components.html(
        f"""
        <div style="display:flex; gap:10px; align-items:center;">
            <button id="{component_key}" {disabled_attr}
                style="background:linear-gradient(180deg,#3f89a7,#357e9b);color:#f7fbf7;border:1px solid #357e9b;border-radius:10px;padding:0.6rem 1rem;font-weight:700;cursor:{cursor_style};opacity:{opacity};box-shadow:0 8px 18px rgba(53,126,155,0.16);">
                {html_escape(button_label)}
            </button>
            <span id="{component_key}_msg" style="font-family:sans-serif;font-size:0.9rem;color:#657a84;"></span>
        </div>
        <script>
        const btn = document.getElementById("{component_key}");
        if (btn && !btn.disabled) {{
            btn.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText({payload});
                    document.getElementById("{component_key}_msg").textContent = "Copied";
                }} catch (err) {{
                    document.getElementById("{component_key}_msg").textContent = "Clipboard access failed";
                }}
            }});
        }}
        </script>
        """,
        height=52,
    )


def build_ticket_assistant_helpdesk_mailto(fields: dict[str, str], body: str) -> str:
    subject_target = (
        clean_extracted_value(fields.get("camera_name", ""))
        or clean_extracted_value(fields.get("camera_location", ""))
        or clean_extracted_value(fields.get("location", ""))
        or "Camera Issue"
    )
    subject = f"Cam Issue: {subject_target}"
    params = urllib.parse.urlencode({"subject": subject, "body": body or ""}, quote_via=urllib.parse.quote)
    return f"mailto:{TDX_HELPDESK_EMAIL}?{params}"


def reset_ticket_assistant_fields(clear_input: bool = False) -> None:
    for field_name, _ in TICKET_ASSISTANT_FIELDS:
        st.session_state[f"tra_field_{field_name}"] = ""
    for key, value in {
        "tra_workflow": "Auto Detect",
        "tra_output_text": "",
        "tra_output_editor": "",
        "tra_photo_quantity": 0,
        "tra_video_quantity": 0,
        "tra_include_thanks": True,
        "tra_player_link": "",
        "tra_video_link": "",
        "tra_new_player_link": "",
        "tra_existing_video_link": "",
        "tra_uploads": [],
        "tra_line_items": [],
        "tra_last_parse_messages": [],
        "tra_last_missing_fields": [],
        "tra_last_ai_status": "",
        "tra_payment_data": {},
    }.items():
        st.session_state[key] = value
    if clear_input:
        st.session_state["tra_raw_input"] = ""
        st.session_state["tra_extracted_text"] = ""
        st.session_state["tra_output_history"] = []
        st.session_state["tra_detected_workflow"] = "General Ticket Review"
        st.session_state["tra_input_widget_nonce"] = int(st.session_state.get("tra_input_widget_nonce", 0)) + 1
        st.session_state.pop("tra_history_selector", None)
    st.session_state["tra_no_video_reason"] = TICKET_ASSISTANT_NO_VIDEO_REASONS[0]
    st.session_state["tra_no_video_reason_custom"] = ""


def ensure_ticket_assistant_state() -> None:
    defaults: dict[str, Any] = {
        "tra_workflow": "Auto Detect",
        "tra_raw_input": "",
        "tra_extracted_text": "",
        "tra_output_text": "",
        "tra_output_editor": "",
        "tra_output_history": [],
        "tra_include_thanks": True,
        "tra_no_video_reason": TICKET_ASSISTANT_NO_VIDEO_REASONS[0],
        "tra_no_video_reason_custom": "",
        "tra_player_link": "",
        "tra_video_link": "",
        "tra_new_player_link": "",
        "tra_existing_video_link": "",
        "tra_photo_quantity": 0,
        "tra_video_quantity": 0,
        "tra_line_items": [],
        "tra_last_parse_messages": [],
        "tra_last_missing_fields": [],
        "tra_last_ai_status": "",
        "tra_payment_data": {},
        "tra_input_widget_nonce": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    for field_name, _ in TICKET_ASSISTANT_FIELDS:
        st.session_state.setdefault(f"tra_field_{field_name}", "")


def process_ticket_assistant_inputs(overwrite_fields: bool = False) -> str:
    ensure_ticket_assistant_state()
    sections: list[str] = []
    parse_messages: list[str] = []
    raw_input = clean_ticket_text(st.session_state.get("tra_raw_input", ""))
    if raw_input:
        sections.append(raw_input)
    for uploaded_file in st.session_state.get("tra_uploads", []) or []:
        extracted_text, message = extract_text_from_uploaded_file(uploaded_file)
        if extracted_text:
            sections.append(f"[From {uploaded_file.name}]\n{extracted_text}")
        if message:
            parse_messages.append(message)
    combined_text = "\n\n".join(section for section in sections if clean_ticket_text(section))
    st.session_state["tra_extracted_text"] = combined_text
    st.session_state["tra_last_parse_messages"] = parse_messages

    effective_workflow = st.session_state.get("tra_workflow", "Auto Detect")
    workflow_to_parse = detect_ticket_assistant_workflow(combined_text) if effective_workflow == "Auto Detect" else effective_workflow
    parsed_fields = parse_general_ticket_fields(combined_text)
    line_items: list[dict[str, str]] = []
    payment_data: dict[str, Any] = {}

    if workflow_to_parse == "Payment Confirmation Email":
        regex_fields, regex_items, payment_data = parse_payment_confirmation_email(combined_text)
        for field_name, value in regex_fields.items():
            parsed_fields[field_name] = clean_extracted_value(value)
        line_items = regex_items
        parse_messages.extend(payment_data.get("warnings", []))
        st.session_state["tra_last_ai_status"] = "Local bursar parser used."
    else:
        st.session_state["tra_last_ai_status"] = "Regex extraction used."

    if workflow_to_parse == "Camera Asset Record":
        regex_fields = parse_camera_asset_record(combined_text)
        for field_name, value in regex_fields.items():
            maybe_set_field(parsed_fields, field_name, value)
    if workflow_to_parse == "Vendor Escalation Response":
        regex_fields = parse_vendor_escalation_record(combined_text)
        for field_name, value in regex_fields.items():
            maybe_set_field(parsed_fields, field_name, value)
    apply_parsed_fields_to_session(parsed_fields, overwrite=overwrite_fields)
    st.session_state["tra_line_items"] = line_items
    st.session_state["tra_payment_data"] = payment_data
    st.session_state["tra_last_parse_messages"] = parse_messages
    return workflow_to_parse


def generate_ticket_assistant_output_from_state(workflow: str, extracted_text: str) -> None:
    fields = {field_name: st.session_state.get(f"tra_field_{field_name}", "") for field_name, _ in TICKET_ASSISTANT_FIELDS}
    if extracted_text:
        parsed_fields = parse_general_ticket_fields(extracted_text)
        line_items = st.session_state.get("tra_line_items", [])
        if workflow == "Payment Confirmation Email":
            parsed_fields, line_items, payment_data = parse_payment_confirmation_email(extracted_text)
            st.session_state["tra_payment_data"] = payment_data
            st.session_state["tra_line_items"] = line_items
        elif workflow == "Vendor Escalation Response":
            parsed_fields = parse_vendor_escalation_record(extracted_text)
        elif workflow == "Camera Asset Record":
            parsed_fields = parse_camera_asset_record(extracted_text)
        else:
            st.session_state["tra_line_items"] = []
        for field_name, parsed_value in parsed_fields.items():
            if field_name in fields and clean_extracted_value(parsed_value) and not clean_extracted_value(fields.get(field_name, "")):
                fields[field_name] = clean_extracted_value(parsed_value)
    output_text, missing_fields = generate_ticket_assistant_output(
        workflow,
        fields,
        st.session_state.get("tra_line_items", []),
        extracted_text,
    )
    st.session_state["tra_output_text"] = output_text
    st.session_state["tra_output_editor"] = output_text
    st.session_state["tra_last_missing_fields"] = missing_fields
    if output_text:
        history = list(st.session_state.get("tra_output_history", []))
        history.insert(
            0,
            {
                "workflow": workflow,
                "created_at": format_timestamp(utc_now_timestamp()),
                "tdx_ticket_id": clean_extracted_value(fields.get("tdx_ticket_id", "")),
                "output": output_text,
            },
        )
        st.session_state["tra_output_history"] = history[:12]


def render_ticket_assistant_field_editor(workflow: str, compact_mode: bool = False) -> dict[str, str]:
    values: dict[str, str] = {}
    field_groups = [
        ("Incident", ["date", "time", "location", "case_number", "service_request_id", "name", "camera_name"]),
        ("Notes", ["issue_description", "actions_taken"]),
        ("Asset", ["camera_location", "asset_id", "product_model", "serial_number", "service_tag", "camera_ip"]),
        ("Network", ["camera_server", "failover_server", "camera_power_source", "its_switch_ip", "its_switch_name", "its_switch_port"]),
        ("Ownership", ["department_for_maintenance", "installation_company", "budget_code"]),
    ]
    workflow_groups = {
        "Payment Confirmation Email": {"Incident"},
        "Camera Asset Record": {"Incident", "Asset", "Network", "Ownership"},
        "Vendor Escalation Response": {"Incident", "Notes", "Asset", "Network", "Ownership"},
        "Camera System Video Request": {"Incident"},
        "No Video Available Response": {"Incident"},
        "Paid Video Link Delivery": {"Incident"},
        "Link Re-upload Response": {"Incident"},
        "Multi-Media Fee Response": {"Incident"},
        "General Ticket Review": {"Incident", "Asset", "Network", "Ownership"},
    }
    label_map = dict(TICKET_ASSISTANT_FIELDS)
    multiline_fields = {"location", "camera_location", "name", "issue_description", "actions_taken"}
    prioritized_groups = workflow_groups.get(workflow, {"Incident"})
    compact_primary_fields = {"date", "time", "case_number", "service_request_id"}

    def render_group(group_label: str, group_fields: list[str]) -> None:
        st.markdown(f'<div class="tra-section-label">{html_escape(group_label)}</div>', unsafe_allow_html=True)
        short_fields = [field_name for field_name in group_fields if field_name not in multiline_fields]
        long_fields = [field_name for field_name in group_fields if field_name in multiline_fields]

        if short_fields:
            columns = st.columns(5, gap="small")
            for idx, field_name in enumerate(short_fields):
                with columns[idx % 5]:
                    key = f"tra_field_{field_name}"
                    st.markdown(f'<div class="tra-field-label">{html_escape(label_map[field_name])}</div>', unsafe_allow_html=True)
                    values[field_name] = st.text_input(label_map[field_name], key=key, label_visibility="collapsed")

        if long_fields:
            columns = st.columns(2, gap="small")
            for idx, field_name in enumerate(long_fields):
                with columns[idx % 2]:
                    key = f"tra_field_{field_name}"
                    st.markdown(f'<div class="tra-field-label">{html_escape(label_map[field_name])}</div>', unsafe_allow_html=True)
                    values[field_name] = st.text_area(label_map[field_name], key=key, height=62, label_visibility="collapsed")

    def render_field_list(group_label: str, group_fields: list[str], expanded: bool = True) -> None:
        if expanded:
            render_group(group_label, group_fields)
        else:
            with st.expander(group_label, expanded=False):
                render_group(group_label, group_fields)

    if compact_mode:
        render_field_list(
            "Incident",
            [field_name for field_name in field_groups[0][1] if field_name in compact_primary_fields],
            expanded=True,
        )
        compact_secondary: list[tuple[str, list[str]]] = []
        incident_extra = [field_name for field_name in field_groups[0][1] if field_name not in compact_primary_fields]
        if incident_extra:
            compact_secondary.append(("Incident Details", incident_extra))
        compact_secondary.extend(field_groups[1:])
        with st.expander("Additional Fields", expanded=False):
            for group_label, group_fields in compact_secondary:
                render_group(group_label, group_fields)
        return values

    secondary_groups: list[tuple[str, list[str]]] = []
    for group_label, group_fields in field_groups:
        if group_label in prioritized_groups:
            render_group(group_label, group_fields)
        else:
            secondary_groups.append((group_label, group_fields))

    if secondary_groups:
        with st.expander("Additional Fields", expanded=False):
            for group_label, group_fields in secondary_groups:
                render_group(group_label, group_fields)
    return values


def render_ticket_response_assistant() -> None:
    ensure_ticket_assistant_state()
    st.markdown(
        """
        <style>
        .tra-hero {
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(231,239,244,0.99));
            border: 1px solid rgba(53, 126, 155, 0.24);
            border-radius: 18px;
            padding: 0.72rem 0.9rem 0.78rem 0.9rem;
            margin: 0.05rem 0 0.55rem 0;
            box-shadow: 0 12px 28px rgba(53, 126, 155, 0.08);
        }
        .tra-kicker {
            color: #5E779E;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.28rem;
        }
        .tra-hero-title {
            font-size: 1.52rem;
            font-weight: 760;
            letter-spacing: -0.03em;
            color: #2F4350;
            line-height: 1.05;
            margin-bottom: 0.22rem;
        }
        .tra-hero-sub {
            color: #657A84;
            font-size: 0.88rem;
            line-height: 1.36;
            max-width: 54rem;
        }
        .tra-progress-shell {
            margin: 0.46rem 0 0.02rem 0;
        }
        .tra-progress-line {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.6rem;
            align-items: start;
        }
        .tra-progress-step {
            position: relative;
            padding-top: 0.24rem;
        }
        .tra-progress-step::before {
            content: "";
            display: block;
            height: 7px;
            border-radius: 999px;
            background: rgba(94, 119, 158, 0.24);
            margin-bottom: 0.48rem;
        }
        .tra-progress-step.active::before,
        .tra-progress-step.complete::before {
            background: linear-gradient(90deg, #357E9B, #5E779E);
        }
        .tra-progress-badge {
            position: absolute;
            top: -0.42rem;
            left: 0.62rem;
            width: 1.8rem;
            height: 1.8rem;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(241, 243, 244, 0.98);
            border: 1px solid rgba(94, 119, 158, 0.24);
            color: #657A84;
            font-size: 0.82rem;
            font-weight: 800;
        }
        .tra-progress-step.active .tra-progress-badge,
        .tra-progress-step.complete .tra-progress-badge {
            background: linear-gradient(180deg, #357E9B, #5E779E);
            border-color: rgba(53, 126, 155, 0.52);
            color: #ffffff;
            box-shadow: 0 10px 24px rgba(53, 126, 155, 0.18);
        }
        .tra-progress-label {
            color: #2F4350;
            font-size: 0.88rem;
            font-weight: 680;
            line-height: 1.18;
            padding-left: 0.15rem;
            margin-top: 0.12rem;
        }
        .tra-progress-copy {
            color: #657A84;
            font-size: 0.75rem;
            line-height: 1.24;
            margin-top: 0.08rem;
            padding-left: 0.15rem;
        }
        .tra-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(236,242,245,0.99));
            border: 1px solid rgba(101, 122, 132, 0.22);
            border-radius: 18px;
            padding: 0.68rem 0.82rem 0.75rem 0.82rem;
            margin-bottom: 0.55rem;
            box-shadow: 0 12px 26px rgba(53, 126, 155, 0.07);
        }
        .tra-card-title {
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #5E779E;
            margin-bottom: 0.46rem;
        }
        .tra-card-headline {
            color: #2F4350;
            font-size: 1.04rem;
            font-weight: 720;
            line-height: 1.18;
            margin-bottom: 0.16rem;
        }
        .tra-card-subcopy {
            color: #657A84;
            font-size: 0.78rem;
            line-height: 1.32;
            margin-bottom: 0.55rem;
        }
        .tra-source-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0 0 0.55rem 0;
            align-items: stretch;
        }
        .tra-source-option {
            background: linear-gradient(180deg, rgba(247,250,251,0.99), rgba(236,242,245,0.99));
            border: 1px solid rgba(101, 122, 132, 0.2);
            border-radius: 16px;
            padding: 0.68rem;
            min-height: 5.5rem;
            box-shadow: none;
        }
        .tra-source-option.primary {
            background: linear-gradient(180deg, rgba(229, 236, 248, 0.99), rgba(216, 226, 242, 0.99));
            border-color: rgba(94, 119, 158, 0.42);
            box-shadow: 0 10px 22px rgba(53, 126, 155, 0.11);
        }
        .tra-source-icon {
            font-size: 1.55rem;
            line-height: 1;
            margin-bottom: 0.42rem;
        }
        .tra-source-title {
            color: #2F4350;
            font-size: 0.94rem;
            font-weight: 700;
            line-height: 1.18;
            margin-bottom: 0.22rem;
        }
        .tra-source-copy {
            color: #657A84;
            font-size: 0.77rem;
            line-height: 1.28;
        }
        .tra-meta-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.5rem;
            margin: 0.08rem 0 0.45rem 0;
        }
        .tra-meta-chip {
            background: linear-gradient(180deg, rgba(247,250,252,0.99), rgba(238,243,246,0.99));
            border: 1px solid rgba(94, 119, 158, 0.18);
            border-radius: 14px;
            padding: 0.5rem 0.62rem;
        }
        .tra-meta-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #5E779E;
            margin-bottom: 0.18rem;
        }
        .tra-meta-value {
            font-size: 0.9rem;
            font-weight: 700;
            color: #2F4350;
            word-break: break-word;
        }
        .tra-section-label {
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #5E779E;
            margin: 0.12rem 0 0.22rem 0;
        }
        .tra-field-label {
            font-size: 0.67rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #657A84;
            margin: 0 0 0.18rem 0.02rem;
        }
        .tra-upload-hint {
            color: #657A84;
            font-size: 0.74rem;
            line-height: 1.24;
            margin-top: 0.18rem;
        }
        .tra-upload-shell {
            display: flex;
            flex-direction: column;
        }
        .tra-upload-shell div[data-testid="stFileUploader"] {
            min-height: 178px;
        }
        .tra-upload-shell div[data-testid="stFileUploader"] section {
            min-height: 178px;
            padding: 0.48rem 0.58rem 0.56rem 0.58rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(244,248,250,0.99), rgba(233,240,244,0.99));
            border: 1px dashed rgba(94, 119, 158, 0.34);
        }
        @media (max-width: 980px) {
            .tra-progress-line,
            .tra-source-grid {
                grid-template-columns: 1fr;
            }
        }
        div[data-testid="stTextInput"] {
            margin-bottom: 0.2rem;
        }
        div[data-testid="stTextInput"] input {
            border-radius: 8px !important;
            min-height: 2rem !important;
            padding-top: 0.18rem !important;
            padding-bottom: 0.18rem !important;
            background: rgba(255,255,255,0.99) !important;
            border: 1px solid rgba(101, 122, 132, 0.28) !important;
            color: #2F4350 !important;
        }
        div[data-testid="stTextArea"] {
            margin-bottom: 0.25rem;
        }
        div[data-testid="stTextArea"] textarea {
            border-radius: 8px !important;
            padding-top: 0.3rem !important;
            padding-bottom: 0.3rem !important;
            background: rgba(255,255,255,0.99) !important;
            border: 1px solid rgba(101, 122, 132, 0.28) !important;
            color: #2F4350 !important;
        }
        div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
            gap: 0.12rem;
        }
        div[data-testid="stTextArea"] textarea[disabled] {
            opacity: 0.98;
            background: linear-gradient(180deg, rgba(244,248,250,0.99), rgba(233,240,244,0.99)) !important;
            color: #425761 !important;
            -webkit-text-fill-color: #425761 !important;
        }
        div[data-testid="stTextInput"] input:disabled {
            background: linear-gradient(180deg, rgba(244,248,250,0.99), rgba(233,240,244,0.99)) !important;
            color: #425761 !important;
            -webkit-text-fill-color: #425761 !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: rgba(255,255,255,0.99) !important;
            border: 1px solid rgba(101, 122, 132, 0.28) !important;
            color: #2F4350 !important;
        }
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        a[data-testid="stLinkButton"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(241,243,244,0.99)) !important;
            border: 1px solid rgba(101, 122, 132, 0.28) !important;
            color: #357E9B !important;
        }
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        a[data-testid="stLinkButton"]:hover {
            border-color: rgba(53, 126, 155, 0.5) !important;
            color: #2D6E88 !important;
        }
        div[data-testid="stExpander"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(239,244,247,0.99));
            border: 1px solid rgba(94, 119, 158, 0.2);
        }
        div[data-testid="stAlert"] {
            border: 1px solid rgba(94, 119, 158, 0.22);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    input_nonce = int(st.session_state.get("tra_input_widget_nonce", 0))
    workflow_key = f"tra_workflow_widget_{input_nonce}"
    raw_input_key = f"tra_raw_input_widget_{input_nonce}"
    extracted_text_key = f"tra_extracted_text_widget_{input_nonce}"
    upload_key = f"tra_uploads_widget_{input_nonce}"
    if workflow_key not in st.session_state:
        st.session_state[workflow_key] = st.session_state.get("tra_workflow", "Auto Detect")
    if raw_input_key not in st.session_state:
        st.session_state[raw_input_key] = st.session_state.get("tra_raw_input", "")
    if extracted_text_key not in st.session_state:
        st.session_state[extracted_text_key] = st.session_state.get("tra_extracted_text", "")

    has_source_material = bool(
        clean_ticket_text(st.session_state.get(raw_input_key, "")) or st.session_state.get(upload_key, [])
    )
    has_processed_text = bool(clean_ticket_text(st.session_state.get(extracted_text_key, "")))
    has_output_text = bool(clean_ticket_text(st.session_state.get("tra_output_text", "")))
    current_step = 3 if has_output_text else 2 if has_processed_text else 1
    step_classes = [
        "complete" if current_step > idx else "active" if current_step == idx else ""
        for idx in (1, 2, 3)
    ]

    st.markdown(
        f"""
        <div class="tra-hero">
            <div class="tra-kicker">Ticket Workflow</div>
            <div class="tra-hero-title">Ticket Assistant</div>
            <div class="tra-hero-sub">Move from raw ticket material to a reviewed LSU-ready response without bouncing between separate tools.</div>
            <div class="tra-progress-shell">
                <div class="tra-progress-line">
                    <div class="tra-progress-step {step_classes[0]}">
                        <div class="tra-progress-badge">1</div>
                        <div class="tra-progress-label">Select Source</div>
                        <div class="tra-progress-copy">Paste ticket text or upload screenshots and files.</div>
                    </div>
                    <div class="tra-progress-step {step_classes[1]}">
                        <div class="tra-progress-badge">2</div>
                        <div class="tra-progress-label">Review Extraction</div>
                        <div class="tra-progress-copy">Confirm the workflow, extracted text, and captured fields.</div>
                    </div>
                    <div class="tra-progress-step {step_classes[2]}">
                        <div class="tra-progress-badge">3</div>
                        <div class="tra-progress-label">Generate Response</div>
                        <div class="tra-progress-copy">Produce, edit, and hand off the final message.</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.03, 0.97], gap="medium")

    with left_col:
        st.markdown(
            f'''
            <div class="tra-card">
                <div class="tra-card-title">Step 1</div>
                <div class="tra-card-headline">Select Source Material</div>
                <div class="tra-card-subcopy">Bring in raw ticket details from pasted text, screenshots, exports, or supporting files before extraction begins.</div>
                <div class="tra-source-grid">
                    <div class="tra-source-option {'primary' if bool(st.session_state.get(upload_key, [])) and not clean_ticket_text(st.session_state.get(raw_input_key, '')) else ''}">
                        <div class="tra-source-icon">☁</div>
                        <div class="tra-source-title">Upload Files</div>
                        <div class="tra-source-copy">Use screenshots, email files, or text exports when the source is not already clean copy.</div>
                    </div>
                    <div class="tra-source-option {'primary' if clean_ticket_text(st.session_state.get(raw_input_key, '')) else ''}">
                        <div class="tra-source-icon">▤</div>
                        <div class="tra-source-title">Paste Raw Ticket Text</div>
                        <div class="tra-source-copy">Best for copied email threads, ticket updates, notes, and asset record text.</div>
                    </div>
                </div>
            ''',
            unsafe_allow_html=True,
        )
        st.selectbox("Input Type Selector", TICKET_ASSISTANT_WORKFLOWS, key=workflow_key)
        st.session_state["tra_workflow"] = st.session_state.get(workflow_key, "Auto Detect")
        source_cols = st.columns([1.72, 0.88], gap="small")
        with source_cols[0]:
            st.markdown('<div class="tra-field-label">Paste Email, Ticket Text, or Asset Record</div>', unsafe_allow_html=True)
            st.text_area(
                "Paste Email, Ticket Text, or Asset Record",
                key=raw_input_key,
                height=215,
                placeholder="Paste copied email text, ticket details, payment confirmation text, asset records, or case details here.",
                label_visibility="collapsed",
            )
        with source_cols[1]:
            st.markdown('<div class="tra-field-label">Upload Files</div><div class="tra-upload-shell">', unsafe_allow_html=True)
            st.file_uploader(
                "Upload Files",
                type=["png", "jpg", "jpeg", "bmp", "webp", "tif", "tiff", "txt", "csv", "log", "json", "eml", "md"],
                accept_multiple_files=True,
                key=upload_key,
                help="Supports screenshots and text files. OCR runs only if Tesseract is installed on this machine.",
                label_visibility="collapsed",
            )
            st.markdown(
                '<div class="tra-upload-hint">Drop screenshots or text files here.</div></div>',
                unsafe_allow_html=True,
            )
        st.session_state["tra_raw_input"] = st.session_state.get(raw_input_key, "")
        st.session_state["tra_extracted_text"] = st.session_state.get(extracted_text_key, st.session_state.get("tra_extracted_text", ""))
        st.session_state["tra_uploads"] = st.session_state.get(upload_key, [])
        action_cols = st.columns(3)
        with action_cols[0]:
            if st.button("Process Inputs", key="tra_process_inputs", use_container_width=True):
                st.session_state["tra_output_text"] = ""
                st.session_state["tra_output_editor"] = ""
                st.session_state["tra_last_missing_fields"] = []
                st.session_state["tra_detected_workflow"] = process_ticket_assistant_inputs(overwrite_fields=False)
                st.session_state[extracted_text_key] = st.session_state.get("tra_extracted_text", "")
                if st.session_state.get("tra_detected_workflow") == "Camera Asset Record":
                    generate_ticket_assistant_output_from_state(
                        "Camera Asset Record",
                        clean_ticket_text(st.session_state.get("tra_extracted_text", "")),
                    )
        with action_cols[1]:
            if st.button("Re-parse Edited Text", key="tra_reparse_inputs", use_container_width=True):
                extracted_text = clean_ticket_text(st.session_state.get(extracted_text_key, ""))
                st.session_state["tra_extracted_text"] = extracted_text
                st.session_state["tra_raw_input"] = extracted_text
                st.session_state["tra_uploads"] = []
                st.session_state["tra_detected_workflow"] = process_ticket_assistant_inputs(overwrite_fields=True)
                if st.session_state.get("tra_detected_workflow") == "Camera Asset Record":
                    generate_ticket_assistant_output_from_state("Camera Asset Record", extracted_text)
        with action_cols[2]:
            if st.button("Clear", key="tra_clear_all", use_container_width=True):
                reset_ticket_assistant_fields(clear_input=True)
                st.rerun()

        detected_workflow = st.session_state.get("tra_detected_workflow", detect_ticket_assistant_workflow(st.session_state.get("tra_extracted_text", "")))
        tesseract_command = resolve_tesseract_command()
        st.markdown(
            f"""
            <div class="tra-meta-grid">
                <div class="tra-meta-chip"><div class="tra-meta-label">Workflow</div><div class="tra-meta-value">{html_escape(detected_workflow)}</div></div>
                <div class="tra-meta-chip"><div class="tra-meta-label">OCR</div><div class="tra-meta-value">{'Ready' if tesseract_command else 'Unavailable'}</div></div>
                <div class="tra-meta-chip"><div class="tra-meta-label">Parser</div><div class="tra-meta-value">{html_escape(st.session_state.get("tra_last_ai_status", "") or 'Idle')}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for parse_message in st.session_state.get("tra_last_parse_messages", []):
            st.warning(parse_message)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Review Extracted Text", expanded=False):
            st.text_area(
                "Review and edit extracted text before generating output",
                key=extracted_text_key,
                height=230,
                placeholder="Processed text will appear here. You can edit it before extracting fields or generating the final response.",
            )

    with right_col:
        st.markdown(
            '<div class="tra-card"><div class="tra-card-title">Step 2</div><div class="tra-card-headline">Review Extracted Data</div><div class="tra-card-subcopy">Validate the detected workflow and correct any fields before generating the final response.</div>',
            unsafe_allow_html=True,
        )
        workflow_for_output = st.session_state.get("tra_workflow", "Auto Detect")
        effective_workflow = detected_workflow if workflow_for_output == "Auto Detect" else workflow_for_output
        payment_data = st.session_state.get("tra_payment_data", {}) or {}
        compact_extracted_data = not any(
            clean_extracted_value(st.session_state.get(f"tra_field_{field_name}", ""))
            for field_name, _ in TICKET_ASSISTANT_FIELDS
        ) and not payment_data

        if effective_workflow == "Payment Confirmation Email":
            summary_cols = st.columns(2)
            with summary_cols[0]:
                st.text_input("TDX Ticket ID", value=str(payment_data.get("ticket_number_tdx_id", "")), disabled=True)
                st.text_input("Name", value=str(payment_data.get("name", "")), disabled=True)
                st.text_input("Email", value=str(payment_data.get("email", "")), disabled=True)
                st.text_input("Item Count", value=str(payment_data.get("item_count", "")), disabled=True)
            with summary_cols[1]:
                st.text_input("LSUPD Case Number", value=str(payment_data.get("lsupd_case_number", "")), disabled=True)
                st.text_input("Phone", value=str(payment_data.get("phone", "")), disabled=True)
                st.text_input("Transaction Number", value=str(payment_data.get("transaction_number", "")), disabled=True)

            paid_items = payment_data.get("paid_items", []) or []
            paid_items_df = pd.DataFrame(paid_items)
            if not paid_items_df.empty:
                paid_items_df = paid_items_df.rename(columns={
                    "group": "Group",
                    "itemcode": "Itemcode",
                    "routing_contacts": "Routing Contact(s)",
                    "routing_note": "Routing Note",
                    "amount": "Amount",
                    "quantity": "Quantity",
                })
                st.markdown("#### Paid Items")
                st.dataframe(
                    paid_items_df[["Group", "Itemcode", "Routing Contact(s)", "Routing Note", "Amount", "Quantity"]],
                    use_container_width=True,
                    hide_index=True,
                )

            warnings = payment_data.get("warnings", []) or []
            if warnings:
                st.markdown('<div class="tra-section-label">Warnings</div>', unsafe_allow_html=True)
                for warning in warnings:
                    st.warning(str(warning))

        fields = render_ticket_assistant_field_editor(effective_workflow, compact_mode=compact_extracted_data)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="tra-card"><div class="tra-card-title">Workflow Controls</div><div class="tra-card-headline">Adjust Response Options</div><div class="tra-card-subcopy">Fine-tune workflow-specific settings before generation.</div>',
            unsafe_allow_html=True,
        )
        with st.container():
            if effective_workflow == "No Video Available Response":
                st.selectbox("No Video Reason", TICKET_ASSISTANT_NO_VIDEO_REASONS, key="tra_no_video_reason")
                st.text_area("Custom Reason Override", key="tra_no_video_reason_custom", height=80, placeholder="Optional. Leave blank to use the selected reason.")
            elif effective_workflow in {"Paid Video Link Delivery", "Payment Confirmation Email"}:
                link_cols = st.columns(2)
                with link_cols[0]:
                    st.toggle("Include Thank you", key="tra_include_thanks")
                with link_cols[1]:
                    if st.button("Reset Fields", key="tra_reset_fields_top", use_container_width=True):
                        reset_ticket_assistant_fields(clear_input=False)
                        st.rerun()
                st.text_input("Player Link", key="tra_player_link", placeholder=TICKET_ASSISTANT_DEFAULT_PLAYER_LINK)
                st.text_input("Video Link", key="tra_video_link")
            elif effective_workflow == "Link Re-upload Response":
                st.text_input("New Player Link", key="tra_new_player_link")
                st.text_input("Existing Video Link", key="tra_existing_video_link")
            elif effective_workflow == "Multi-Media Fee Response":
                qty_cols = st.columns(2)
                with qty_cols[0]:
                    st.number_input("Photo Quantity", min_value=0, step=1, key="tra_photo_quantity")
                with qty_cols[1]:
                    st.number_input("Video Quantity", min_value=0, step=1, key="tra_video_quantity")
            else:
                if st.button("Reset Fields", key="tra_reset_fields_standard", use_container_width=True):
                    reset_ticket_assistant_fields(clear_input=False)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="tra-card"><div class="tra-card-title">Step 3</div><div class="tra-card-headline">Generate Final Response</div><div class="tra-card-subcopy">Create the drafted response, edit it, and hand it off through the next operational action.</div>',
            unsafe_allow_html=True,
        )
        button_cols = st.columns([1.15, 0.85])
        with button_cols[0]:
            if st.button("Generate Response", key="tra_generate_response", use_container_width=True):
                extracted_text = clean_ticket_text(st.session_state.get(extracted_text_key, ""))
                st.session_state["tra_extracted_text"] = extracted_text
                generate_ticket_assistant_output_from_state(effective_workflow, extracted_text)
        with button_cols[1]:
            if st.button("Reset Fields", key="tra_reset_fields_bottom", use_container_width=True):
                reset_ticket_assistant_fields(clear_input=False)
                st.rerun()

        output_text = st.session_state.get("tra_output_text", "")
        editor_text = st.session_state.get("tra_output_editor", output_text)
        missing_fields = st.session_state.get("tra_last_missing_fields", [])
        if missing_fields:
            st.warning("Missing key fields: " + ", ".join(missing_fields))
        st.text_area("Final Output", key="tra_output_editor", height=230, placeholder="Generated response text will appear here. You can edit it before copying or downloading.")
        copy_cols = st.columns(3)
        with copy_cols[0]:
            render_copy_button(editor_text, "Copy to Clipboard", "tra_copy_output")
        with copy_cols[1]:
            st.download_button(
                "Download Text",
                data=editor_text or "",
                file_name="ticket-response.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with copy_cols[2]:
            if effective_workflow == "Camera Asset Record" and editor_text.strip():
                st.link_button(
                    "Create Helpdesk Email",
                    build_ticket_assistant_helpdesk_mailto(fields, editor_text),
                    use_container_width=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        history = st.session_state.get("tra_output_history", [])
        if history:
            with st.expander("Recent Output History", expanded=False):
                history_labels = []
                for item in history:
                    ticket_id = clean_extracted_value(item.get("tdx_ticket_id", ""))
                    if ticket_id:
                        history_labels.append(f"TDX {ticket_id} | {item['workflow']} | {item['created_at']}")
                    else:
                        history_labels.append(f"{item['workflow']} | {item['created_at']}")
                selected_history = st.selectbox("Recent Output History", options=history_labels, index=0, key="tra_history_selector")
                selected_idx = history_labels.index(selected_history)
                st.text_area("History Preview", value=history[selected_idx]["output"], height=120, disabled=True)
def extract_camera_and_failover_servers(row: pd.Series) -> tuple[str, str]:

    server_blob = row_first_non_empty(row, ["Servers", "Server Name"])

    if not server_blob:

        return "", ""

    servers = [part.strip() for part in server_blob.split("|") if part.strip()]

    if not servers:

        return "", ""

    camera_server = servers[0]

    failover_server = servers[1] if len(servers) > 1 else ""

    return camera_server, failover_server





def build_manual_tdx_ticket_subject(row: pd.Series) -> str:

    camera_name = row_first_non_empty(row, ["Device Name Base", "Device Name", "device_name", "key"]) or "Unknown Camera"

    return f"Camera Offline: {camera_name}"





def build_manual_tdx_ticket_body(row: pd.Series) -> str:

    camera_server, failover_server = extract_camera_and_failover_servers(row)

    metadata_fields = [

        ("Camera Location", row_first_non_empty(row, ["Location", "location"])),

        ("Asset ID", row_first_non_empty(row, ["Asset ID", "AssetID", "Logical ID", "Asset Tag"])),

        ("Product Model", row_first_non_empty(row, ["Model", "Product Model", "Model Name"])),

        ("MAC Address", row_first_non_empty(row, ["MAC Address", "key"])),

        ("Serial Number", row_first_non_empty(row, ["Serial Number", "Serial"])),

        ("Camera IP", row_first_non_empty(row, ["IP Address"])),

        ("Camera Server", camera_server),

        ("Failover Server", failover_server),

        ("Camera Power Source", row_first_non_empty(row, ["Camera Power Source", "Power Source", "Power"])),

        ("ITS Switch IP", row_first_non_empty(row, ["ITS Switch IP", "Switch IP", "Network Switch IP"])),

        ("ITS Switch Name", row_first_non_empty(row, ["ITS Switch Name", "Switch Name", "Network Switch Name"])),

        ("ITS Switch Port", row_first_non_empty(row, ["ITS Switch Port", "Switch Port", "Network Switch Port"])),

    ]



    lines = [

        "The following camera cannot be pinged nor is it connected to the VMS. Please troubleshoot configurations and cycle the power to the port.",

        "",

    ]

    for label, value in metadata_fields:

        if value:

            lines.append(f"{label}: {value}")

    return "\n".join(lines)





def send_manual_tdx_ticket_for_row(

    row: pd.Series,

    smtp_host: str,

    smtp_port: int,

    smtp_username: str,

    smtp_password: str,

    smtp_from_email: str,

    tdx_email_to: str,

) -> tuple[bool, str]:

    now_iso = format_timestamp(utc_now_timestamp())

    key_value = row_first_non_empty(row, ["key", "MAC Address"])

    device_name = row_first_non_empty(row, ["Device Name Base", "Device Name", "device_name"])

    location = row_first_non_empty(row, ["Location", "location"])

    health_state = row_first_non_empty(row, ["Health State", "Health"])

    offline_hours = pd.to_numeric(row.get("Offline For (hrs)", 0.0), errors="coerce")

    if pd.isna(offline_hours):

        offline_hours = 0.0



    subject = build_manual_tdx_ticket_subject(row)

    body = build_manual_tdx_ticket_body(row)

    sent, err = send_ticket_email(

        smtp_host,

        smtp_port,

        smtp_username,

        smtp_password,

        smtp_from_email,

        tdx_email_to,

        subject,

        body,

    )



    unique_suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

    ticket_key = f"{key_value or device_name or 'UNKNOWN'}|manual|{unique_suffix}"

    ticket_row = pd.DataFrame([{

        "ticket_key": ticket_key,

        "key": key_value,

        "device_name": device_name,

        "location": location,

        "health_state": health_state,

        "offline_since": "",

        "offline_hours_at_creation": float(offline_hours),

        "ticket_state": "Open" if sent else "Pending Send",

        "ticket_id": "",

        "email_to": tdx_email_to,

        "email_subject": subject,

        "created_at": now_iso,

        "email_sent_at": now_iso if sent else "",

        "resolved_at": "",

        "resolution": "",

        "resolution_notes": "",

        "last_error": "" if sent else str(err),

    }])



    tickets = load_tickets(TICKETS_PATH)

    tickets = pd.concat([tickets, ticket_row], ignore_index=True)

    save_tickets(TICKETS_PATH, tickets)

    return sent, err





def is_row_eligible_for_manual_tdx(row: pd.Series) -> bool:

    health_state = row_first_non_empty(row, ["Health", "Health State"]).lower()

    ping_status = row_first_non_empty(row, ["Ping Status"]).lower()

    if "offline" not in health_state:

        return False

    bad_ping_markers = ("not pingable", "ping error", "no ip", "invalid ip")

    return any(marker in ping_status for marker in bad_ping_markers)





def sync_tracking_and_tickets(

    devices_df: pd.DataFrame,

    tracking_df: pd.DataFrame,

    tickets_df: pd.DataFrame,

    observed_at: pd.Timestamp,

    tdx_email_to: str,

    smtp_settings: dict,

    ticket_threshold_hours: int,

) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str]]:

    tracking = load_tracking_state(TRACKING_PATH) if tracking_df is None else tracking_df.copy()

    tickets = load_tickets(TICKETS_PATH) if tickets_df is None else tickets_df.copy()

    notices: list[str] = []

    errors: list[str] = []

    observed_iso = format_timestamp(observed_at)



    tickets["ticket_state"] = tickets["ticket_state"].fillna("").astype(str)

    blocking_states = {"Pending Send", "Open", "Acknowledged", "Suppressed"}

    blocking_mask = tickets["ticket_state"].isin(blocking_states)

    blocking_keys = set(tickets.loc[blocking_mask, "key"].astype(str))

    suppressed_keys = set(tickets.loc[tickets["ticket_state"].eq("Suppressed"), "key"].astype(str))



    tracking_map: dict[str, Any] = {}

    if not tracking.empty:

        tracking_map_raw = tracking.set_index("key").to_dict(orient="index")

        tracking_map = tracking_map_raw # type: ignore



    rows = []

    for _, row in devices_df.iterrows():

        key = str(row["key"])

        prior: dict[str, Any] = tracking_map[key] if key in tracking_map else {}  # type: ignore[index]

        health_state = str(row.get("Health State", "Online"))

        is_offline = health_state != "Online"

        is_strict_offline = health_state == "Offline"

        first_offline_at = prior.get("first_offline_at", "")



        if is_offline and not format_timestamp(first_offline_at):

            first_offline_at = observed_iso

        if not is_offline and key not in blocking_keys:

            first_offline_at = ""



        offline_hours = hours_since(first_offline_at, observed_at) if is_offline else 0.0

        ticket_status = prior.get("ticket_status", "")

        ticket_id = prior.get("ticket_id", "")

        blocking_for_device = tickets[(tickets["key"].astype(str) == key) & tickets["ticket_state"].isin(blocking_states)]

        if not blocking_for_device.empty:

            latest_ticket = blocking_for_device.iloc[-1]

            ticket_status = latest_ticket.get("ticket_state", ticket_status)

            ticket_id = latest_ticket.get("ticket_id", ticket_id)

        else:

            ticket_status = ""

            ticket_id = ""



        offline_hours_rounded = float(f"{float(offline_hours):.2f}")

        rows.append({

            "key": key,

            "device_name": row.get("Device Name Base", ""),

            "location": row.get("Location", ""),

            "current_health_state": row.get("Health State", ""),

            "first_seen_at": prior.get("first_seen_at", observed_iso) or observed_iso,

            "last_seen_at": observed_iso,

            "first_offline_at": first_offline_at,

            "last_offline_seen_at": observed_iso if is_offline else prior.get("last_offline_seen_at", ""),

            "last_online_at": prior.get("last_online_at", observed_iso if not is_offline else ""),

            "offline_hours": offline_hours_rounded,

            "ticket_status": ticket_status,

            "ticket_id": ticket_id,

            "active": True,

        })



        should_queue_ticket = (

            is_strict_offline

            and offline_hours >= float(ticket_threshold_hours)

            and key not in blocking_keys

            and key not in suppressed_keys

        )

        if should_queue_ticket:

            ticket_key = f"{key}|{observed_iso}"

            subject = build_ticket_subject(row, threshold_hours=ticket_threshold_hours)

            tickets = pd.concat([

                tickets,

                pd.DataFrame([{

                    "ticket_key": ticket_key,

                    "key": key,

                    "device_name": row.get("Device Name Base", ""),

                    "location": row.get("Location", ""),

                    "health_state": row.get("Health State", ""),

                    "offline_since": format_timestamp(first_offline_at),

                    "offline_hours_at_creation": offline_hours_rounded,

                    "ticket_state": "Pending Send",

                    "ticket_id": "",

                    "email_to": tdx_email_to,

                    "email_subject": subject,

                    "created_at": observed_iso,

                    "email_sent_at": "",

                    "resolved_at": "",

                    "resolution": "",

                    "resolution_notes": "",

                    "last_error": "",

                }]),

            ], ignore_index=True)

            blocking_keys.add(key)

            notices.append(

                f"Queued ticket for {row.get('Device Name Base', key)} after {offline_hours:.1f} offline hours "

                f"(threshold {ticket_threshold_hours}h)."

            )



    missing_rows = tracking[~tracking["key"].astype(str).isin(devices_df["key"].astype(str))].copy()

    if not missing_rows.empty:

        missing_rows["active"] = False

        rows.extend(missing_rows.to_dict(orient="records"))



    tracking = pd.DataFrame(rows)



    # No more auto-emailing from here. It is handled by interactive UI.



    active_view = tickets[tickets["ticket_state"].isin(blocking_states)].copy()

    if not active_view.empty:

        active_view = active_view.sort_values("created_at").drop_duplicates(subset=["key"], keep="last")

        tracking = tracking.merge(

            active_view[["key", "ticket_state", "ticket_id"]],

            on="key",

            how="left",

            suffixes=("", "_latest"),

        )

        tracking["ticket_status"] = tracking["ticket_state"].combine_first(tracking["ticket_status"])

        tracking["ticket_id"] = tracking["ticket_id_latest"].combine_first(tracking["ticket_id"])

        tracking = tracking.drop(columns=[c for c in ["ticket_state", "ticket_id_latest"] if c in tracking.columns])



    devices_enriched = devices_df.merge(

        tracking[["key", "first_offline_at", "offline_hours", "ticket_status", "ticket_id"]],

        on="key",

        how="left",

    )

    devices_enriched["Offline For (hrs)"] = pd.to_numeric(devices_enriched["offline_hours"], errors="coerce").fillna(0.0).round(1)

    devices_enriched["Ticket Status"] = devices_enriched["ticket_status"].fillna("")

    devices_enriched["Ticket ID"] = devices_enriched["ticket_id"].fillna("")

    return devices_enriched, tracking, tickets, notices, errors





@st.cache_data

def compute_health_state(df: pd.DataFrame) -> pd.DataFrame:

    if "Connected" in df.columns:

        df["Connected_bool"] = truthy_to_bool(df["Connected"])

    else:

        df["Connected_bool"] = False



    if "Visible" in df.columns:

        df["Visible_bool"] = truthy_to_bool(df["Visible"])

    else:

        df["Visible_bool"] = False



    if "Status" in df.columns:

        status = clean_text_series(df["Status"]).str.lower()

        failed_status = status.str.contains("fail", na=False)

    else:

        failed_status = pd.Series(False, index=df.index)



    if "Error Flags" in df.columns:

        err = clean_text_series(df["Error Flags"])

        has_err = err.ne("")

    else:

        has_err = pd.Series(False, index=df.index)



    offline = (~df["Connected_bool"]) | failed_status | has_err

    offline_but_visible = offline & df["Visible_bool"]



    df["Health State"] = "Online"

    df.loc[offline, "Health State"] = "Offline"

    df.loc[offline_but_visible, "Health State"] = "Offline (but still visible)"



    bubble_map = {

        "Online": "\U0001F7E2 Online",

        "Offline": "\U0001F534 Offline",

        "Offline (but still visible)": "\U0001F7E0 Offline (visible)",

    }

    df["Health"] = df["Health State"].map(bubble_map).fillna(df["Health State"])

    return df





@st.cache_data

def build_devices_table(df_views: pd.DataFrame, server_role_map: dict[str, str] | None = None) -> pd.DataFrame:

    """

    Collapse view-level export into one row per physical camera.

    - Views = number of rows in export for that physical camera (lenses / ONVIF channels / duplicates)

    - Servers = list of servers camera appears on (primary/secondary)

    """

    severity = {"Online": 0, "Offline (but still visible)": 1, "Offline": 2}



    def worst_state(states: pd.Series) -> str:

        states = states.fillna("Online").astype(str)

        return max(states, key=lambda s: severity.get(s, 0))



    bubble_map = {

        "Online": "\U0001F7E2 Online",

        "Offline": "\U0001F534 Offline",

        "Offline (but still visible)": "\U0001F7E0 Offline (visible)",

    }



    def worst_bubble(states: pd.Series) -> str:

        s = worst_state(states)

        return bubble_map.get(s, s)



    def join_unique(series: pd.Series) -> str:

        vals = clean_text_series(series)

        vals = [v for v in vals.tolist() if v]

        if not vals:

            return ""

        return " | ".join(sorted(set(vals)))



    def summarize_server_connection(series: pd.Series) -> str:

        vals = series.fillna(False).astype(bool)

        if vals.empty:

            return "Unknown"

        has_true = bool(vals.any())

        has_false = bool((~vals).any())

        if has_true and has_false:

            return "Mixed"

        return "Connected" if has_true else "Disconnected"



    def connection_dot(state: str) -> str:

        s = str(state).strip().lower()

        if s == "connected":

            return "\U0001F7E2"

        if s == "disconnected":

            return "\U0001F534"

        return "\U0001F7E1"



    def format_connection_label(server_name: str, state: str) -> str:

        return f"{connection_dot(state)} {str(server_name).strip()}"



    def yellow_health_dot(label: str) -> str:

        text = str(label).strip()

        if not text:

            return "\U0001F7E1 Unknown"

        parts = text.split(" ", 1)

        if len(parts) == 2:

            return f"\U0001F7E1 {parts[1]}"

        return f"\U0001F7E1 {text}"



    agg_map: dict[str, object] = {

        "physical_key": "first",

        "key": "first",  # notes key (same as physical_key)

        "Device Name Base": "first",

        "Device Name": "first",

        "Location": "first",

        "Make": "first",

        "Model": "first",

        "IP Address": "first",

        "MAC Address": "first",

        "Connected_bool": "max",

        "Visible_bool": "max",

        "Health State": worst_state,

        "Health": worst_bubble,

        "Error Flags": join_unique,

        "Status": join_unique,

        "disposition": "first",

        "notes": "first",

        "Server Name": join_unique,  # temporary, we'll rename to Servers

    }

    optional_metadata_cols = [

        "Serial Number",

        "Logical ID",

        "Asset ID",

        "Asset Tag",

        "Product Model",

        "Model Name",

        "Camera Power Source",

        "Power Source",

        "ITS Switch IP",

        "ITS Switch Name",

        "ITS Switch Port",

        "Switch IP",

        "Switch Name",

        "Switch Port",

    ]

    for col in optional_metadata_cols:

        if col in df_views.columns:

            agg_map[col] = "first"



    devices = (

        df_views

        .groupby("physical_key", as_index=False)

        .agg(agg_map)

    )



    devices = devices.rename(columns={"Server Name": "Servers"})

    devices["Views"] = df_views.groupby("physical_key").size().reindex(devices["physical_key"]).values

    role_lookup = {

        canonical_server_name_key(k): normalize_server_role(v)

        for k, v in (server_role_map or {}).items()

        if normalize_server_role(v)

    }



    # Preserve per-server connectivity so Action Required can show split primary/secondary states.
    # In the Site Health Report, a listed server on the same MAC row means the camera is connected
    # to that server, even if other status fields disagree.

    if {"physical_key", "Server Name"}.issubset(df_views.columns):

        server_rows = (

            df_views[["physical_key", "Server Name"]]

            .copy()

            .reset_index()

            .rename(columns={"index": "_row_order"})

        )

        server_rows["Server Name"] = clean_text_series(server_rows["Server Name"])

        server_rows = server_rows[server_rows["Server Name"] != ""]

        if not server_rows.empty:

            server_state = (
                server_rows[["physical_key", "Server Name"]]
                .drop_duplicates()
                .assign(**{"Connection State": "Connected"})
            )

            server_order = (

                server_rows

                .groupby(["physical_key", "Server Name"], as_index=False)["_row_order"]

                .min()

                .sort_values(["physical_key", "_row_order"])

            )

            server_pairs = server_order.merge(server_state, on=["physical_key", "Server Name"], how="left")

            server_pairs["Role"] = server_pairs["Server Name"].map(

                lambda name: role_lookup.get(canonical_server_name_key(name), "")

            )



            connection_map: dict[str, tuple[str, str]] = {}

            server_count_map: dict[str, int] = {}

            for key, grp in server_pairs.groupby("physical_key", sort=False):

                key_str = str(key)

                grp_sorted = grp.sort_values("_row_order").reset_index(drop=True)

                server_count_map[key_str] = len(grp_sorted)



                primary_row = pd.Series(dtype=object)

                primary_candidates = grp_sorted[grp_sorted["Role"] == "Primary"]

                non_secondary_candidates = grp_sorted[grp_sorted["Role"] != "Secondary"]

                if not primary_candidates.empty:

                    primary_row = primary_candidates.iloc[0]

                elif not non_secondary_candidates.empty:

                    primary_row = non_secondary_candidates.iloc[0]

                elif not grp_sorted.empty:

                    primary_row = grp_sorted.iloc[0]



                primary_label = ""

                primary_server = ""

                if not primary_row.empty:

                    primary_server = str(primary_row.get("Server Name", "")).strip()

                    primary_label = format_connection_label(

                        primary_server,

                        str(primary_row.get("Connection State", "")).strip(),

                    )



                secondary_label = ""

                secondary_candidates = grp_sorted[

                    (grp_sorted["Role"] == "Secondary")

                    & (grp_sorted["Server Name"].astype(str).str.strip() != primary_server)

                ]

                remaining_candidates = grp_sorted[

                    grp_sorted["Server Name"].astype(str).str.strip() != primary_server

                ]

                secondary_row = pd.Series(dtype=object)

                if not secondary_candidates.empty:

                    secondary_row = secondary_candidates.iloc[0]

                elif not remaining_candidates.empty:

                    secondary_row = remaining_candidates.iloc[0]

                if not secondary_row.empty:

                    secondary_label = format_connection_label(

                        str(secondary_row.get("Server Name", "")).strip(),

                        str(secondary_row.get("Connection State", "")).strip(),

                    )

                    extra = max(0, len(grp_sorted) - 2)

                    if extra > 0:

                        secondary_label = f"{secondary_label} (+{extra} more)"



                connection_map[key_str] = (primary_label, secondary_label)



            primary_vals: list[str] = []

            secondary_vals: list[str] = []

            health_vals = devices["Health"].astype(str).tolist()

            for idx, key in enumerate(devices["physical_key"].astype(str)):

                primary_label, secondary_label = connection_map.get(key, ("", ""))

                primary_vals.append(primary_label)

                secondary_vals.append(secondary_label)

                if server_count_map.get(key, 0) == 1:

                    health_vals[idx] = yellow_health_dot(health_vals[idx])



            devices["Primary Connection"] = primary_vals

            devices["Secondary Connection"] = secondary_vals

            devices["Health"] = health_vals

        else:

            devices["Primary Connection"] = ""

            devices["Secondary Connection"] = ""

    else:

        devices["Primary Connection"] = ""

        devices["Secondary Connection"] = ""



    # Nice ordering

    if "Device Name Base" in devices.columns:

        devices["Device Name Base"] = devices["Device Name Base"].fillna(devices["Device Name"])



    return devices





SEARCH_ALIASES: dict[str, tuple[str, ...]] = {

    "antigravity": ("anti gravity", "anti-gravity", "innovation park"),

}



def normalize_search_token(value: object) -> str:

    return re.sub(r"[^a-z0-9]+", "", str(value).lower())



def apply_global_search(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    if not search_text:

        return df



    raw_terms = [term for term in search_text.lower().split() if term]

    normalized_terms = [normalize_search_token(term) for term in raw_terms]

    expanded_raw_terms = [

        [term, *SEARCH_ALIASES.get(normalized_terms[idx], ())]

        for idx, term in enumerate(raw_terms)

    ]


    def row_matches(row) -> bool:

        blob = " ".join(row.astype(str)).lower()

        normalized_blob = normalize_search_token(blob)

        for idx, term in enumerate(raw_terms):

            aliases = expanded_raw_terms[idx]

            normalized_aliases = [normalize_search_token(alias) for alias in aliases if alias]

            if any(alias in blob for alias in aliases if alias):

                continue

            if any(alias and alias in normalized_blob for alias in normalized_aliases):

                continue

            if normalized_terms[idx] and normalized_terms[idx] in normalized_blob:

                continue

            return False

        return True


    return df[df.apply(row_matches, axis=1)]





def ping_one_ip(ip: str) -> str:

    ip_clean = str(ip).strip()

    if not ip_clean:

        return "\u26AA No IP"

    try:

        ipaddress.ip_address(ip_clean)

    except ValueError:

        return "\U0001F7E0 Invalid IP"



    is_windows = platform.system().lower().startswith("win")

    cmd = ["ping", "-n", "1", "-w", "900", ip_clean] if is_windows else ["ping", "-c", "1", "-W", "1", ip_clean]

    try:

        proc = subprocess.run(cmd, capture_output=True, timeout=2, check=False)

        return "\U0001F7E2 Pingable" if proc.returncode == 0 else "\U0001F534 Not Pingable"

    except Exception:

        return "\U0001F7E0 Ping Error"





def initialize_ping_queue(df_in: pd.DataFrame) -> None:

    if "ping_status_by_ip" not in st.session_state:

        st.session_state.ping_status_by_ip = {}

    if "ping_pending_ips" not in st.session_state:

        st.session_state.ping_pending_ips = []



    health_col = "Health" if "Health" in df_in.columns else ("Health State" if "Health State" in df_in.columns else None)

    ip_col = "IP Address" if "IP Address" in df_in.columns else None

    if not health_col or not ip_col or df_in.empty:

        st.session_state.ping_pending_ips = []

        return



    health_text = df_in[health_col].fillna("").astype(str).str.lower()

    offline_mask = health_text.str.contains("offline", na=False)

    ip_series = df_in[ip_col].fillna("").astype(str).str.strip()

    offline_ips = sorted({ip for ip in ip_series[offline_mask] if ip})

    offline_ip_set = set(offline_ips)



    for ip in list(st.session_state.ping_status_by_ip.keys()):

        if ip not in offline_ip_set:

            st.session_state.ping_status_by_ip.pop(ip, None)



    for ip in offline_ips:

        if ip not in st.session_state.ping_status_by_ip:

            st.session_state.ping_status_by_ip[ip] = "\U0001F7E1 Checking..."



    pending = [

        ip for ip in offline_ips

        if st.session_state.ping_status_by_ip.get(ip) == "\U0001F7E1 Checking..."

    ]

    st.session_state.ping_pending_ips = pending





def process_ping_batch(batch_size: int = 2) -> bool:

    pending: list[str] = [str(x) for x in st.session_state.get("ping_pending_ips", [])]

    if not pending:

        return False



    batch: list[str] = list(pending[:batch_size])  # type: ignore[misc]

    remaining: list[str] = list(pending[batch_size:])  # type: ignore[misc]

    for ip in batch:

        st.session_state.ping_status_by_ip[ip] = ping_one_ip(ip)

    st.session_state.ping_pending_ips = remaining

    return len(remaining) > 0







def add_ping_status_for_issues(df_in: pd.DataFrame) -> pd.DataFrame:

    out = df_in.copy()

    if out.empty:

        out["Ping Status"] = []

        return out



    health_col = "Health" if "Health" in out.columns else ("Health State" if "Health State" in out.columns else None)

    ip_col = "IP Address" if "IP Address" in out.columns else None

    out["Ping Status"] = "N/A"

    if not health_col or not ip_col:

        return out



    health_text = out[health_col].fillna("").astype(str).str.lower()

    offline_mask = health_text.str.contains("offline", na=False)

    ip_series = out[ip_col].fillna("").astype(str).str.strip()

    ping_map = st.session_state.get("ping_status_by_ip", {})



    for idx in out.index:

        if not bool(offline_mask.loc[idx]):

            continue

        ip_value = ip_series.loc[idx]

        out.at[idx, "Ping Status"] = "\u26AA No IP" if not ip_value else ping_map.get(ip_value, "\U0001F7E1 Checking...")



    return out





def recolor_health_badge(label: str, dot: str) -> str:

    text = str(label).strip()

    if not text:

        return f"{dot} Unknown"

    parts = text.split(" ", 1)

    if len(parts) == 2:

        return f"{dot} {parts[1]}"

    return f"{dot} {text}"





def apply_action_required_health_badge_rules(df_in: pd.DataFrame) -> pd.DataFrame:

    """

    Action Required visual override:

    - Not Pingable => red health badge (always).

    - Pingable + (primary OR secondary connected) => yellow health badge.

    """

    out = df_in.copy()

    if out.empty:

        return out



    if "Health" not in out.columns:

        if "Health State" in out.columns:

            bubble_map = {

                "Online": "\U0001F7E2 Online",

                "Offline": "\U0001F534 Offline",

                "Offline (but still visible)": "\U0001F7E0 Offline (visible)",

            }

            out["Health"] = (

                clean_text_series(out["Health State"])

                .map(bubble_map)

                .fillna(clean_text_series(out["Health State"]))

            )

        else:

            return out



    ping_lower = clean_text_series(

        out.get("Ping Status", pd.Series([""] * len(out), index=out.index))

    ).str.lower()

    not_pingable = ping_lower.str.contains("not pingable", na=False)

    pingable = ping_lower.str.contains("pingable", na=False) & ~not_pingable



    def connected_from_col(col_name: str) -> pd.Series:

        if col_name not in out.columns:

            return pd.Series(False, index=out.index)

        s = clean_text_series(out[col_name])

        return (

            s.str.startswith("\U0001F7E2")

            | s.str.contains(r"\(\s*Connected\s*\)", case=False, regex=True)

        )



    primary_connected = connected_from_col("Primary Connection")

    secondary_connected = connected_from_col("Secondary Connection")

    any_connection_connected = primary_connected | secondary_connected



    red_mask = not_pingable

    yellow_mask = pingable & any_connection_connected & ~red_mask



    if red_mask.any():

        out.loc[red_mask, "Health"] = (

            out.loc[red_mask, "Health"]

            .astype(str)

            .map(lambda v: recolor_health_badge(v, "\U0001F534"))

        )

    if yellow_mask.any():

        out.loc[yellow_mask, "Health"] = (

            out.loc[yellow_mask, "Health"]

            .astype(str)

            .map(lambda v: recolor_health_badge(v, "\U0001F7E1"))

        )



    return out


def annotate_action_required_ping_status(df_in: pd.DataFrame) -> pd.DataFrame:

    out = df_in.copy()
    if out.empty or "Ping Status" not in out.columns:
        return out

    ping_status = clean_text_series(out["Ping Status"])
    ping_lower = ping_status.str.lower()
    pingable_mask = ping_lower.str.contains("pingable", na=False) & ~ping_lower.str.contains("not pingable", na=False)

    def connected_from_col(col_name: str) -> pd.Series:

        if col_name not in out.columns:
            return pd.Series(False, index=out.index)
        s = clean_text_series(out[col_name])
        return (
            s.str.startswith("\U0001F7E2")
            | s.str.contains(r"\(\s*Connected\s*\)", case=False, regex=True)
        )

    primary_series = clean_text_series(out.get("Primary Connection", pd.Series([""] * len(out), index=out.index)))
    secondary_series = clean_text_series(out.get("Secondary Connection", pd.Series([""] * len(out), index=out.index)))
    any_connection_present = primary_series.ne("") | secondary_series.ne("")

    primary_connected = connected_from_col("Primary Connection")
    secondary_connected = connected_from_col("Secondary Connection")
    any_connection_connected = primary_connected | secondary_connected

    error_flags_present = clean_text_series(
        out.get("Error Flags", pd.Series([""] * len(out), index=out.index))
    ).ne("")
    health_lower = clean_text_series(
        out.get("Health State", out.get("Health", pd.Series([""] * len(out), index=out.index)))
    ).str.lower()
    offline_like = health_lower.str.contains("offline", na=False)

    mismatch_mask = pingable_mask & any_connection_present & ~any_connection_connected
    failed_source_mask = pingable_mask & offline_like & error_flags_present

    out.loc[mismatch_mask, "Ping Status"] = "\U0001F7E2 Pingable (server status mismatch)"
    out.loc[failed_source_mask & ~mismatch_mask, "Ping Status"] = "\U0001F7E2 Pingable (error flags present)"
    return out


def apply_confirmed_healthy_override(df_in: pd.DataFrame) -> pd.DataFrame:

    out = df_in.copy()
    if out.empty:
        return out

    def connected_from_col(col_name: str) -> pd.Series:

        if col_name not in out.columns:
            return pd.Series(False, index=out.index)
        s = clean_text_series(out[col_name])
        return (
            s.str.startswith("\U0001F7E2")
            | s.str.contains(r"\(\s*Connected\s*\)", case=False, regex=True)
        )

    ping_status = clean_text_series(out.get("Ping Status", pd.Series([""] * len(out), index=out.index)))
    ping_lower = ping_status.str.lower()
    pingable = ping_lower.str.contains("pingable", na=False) & ~ping_lower.str.contains("not pingable", na=False)

    primary_connected = connected_from_col("Primary Connection")
    secondary_connected = connected_from_col("Secondary Connection")
    both_servers_connected = primary_connected & secondary_connected

    retention_days = pd.to_numeric(
        out.get("Retention (days)", pd.Series([pd.NA] * len(out), index=out.index)),
        errors="coerce",
    )
    retention_good = retention_days.gt(20)

    healthy_override_mask = pingable & both_servers_connected & retention_good
    if not healthy_override_mask.any():
        return out

    out.loc[healthy_override_mask, "Health State"] = "Online"
    out.loc[healthy_override_mask, "Health"] = "\U0001F7E2 Online"
    return out


# -----------------------------

# UI

# -----------------------------



workspace_options = ["Health Status", "Ticket Related", "Project Related"]
workspace_button_labels = {
    "Health Status": ":material/ecg_heart:  Health Status",
    "Ticket Related": ":material/confirmation_number:  Ticket Dashboard",
    "Project Related": ":material/construction:  Project Builder",
}
ticket_area_options = ["Open Tickets", "Ticket Response Assistant"]
health_area_options = ["Overview", "Action Queue", "Trends", "Retention"]
project_area_options = ["Camera Installation Builder"]
workspace_help = {
    "Health Status": "Review camera health, outage prioritization, trends, and retention.",
    "Ticket Related": "Work queued tickets and generate LSU-specific responses.",
    "Project Related": "Build camera installation packages and BOMs.",
}
area_help = {
    "Overview": "Browse the currently filtered camera inventory.",
    "Action Queue": "Focus on cameras that need attention now.",
    "Trends": "Review uptime, downtime, and state changes over time.",
    "Retention": "Find cameras below the retention target.",
    "Open Tickets": "Review and update tracked ticket records.",
    "Ticket Response Assistant": "Turn pasted ticket material into structured responses.",
    "Camera Installation Builder": "Build workbook-driven camera installation packages.",
}

overview_nav_target = st.query_params.get("overview_nav", "")
if overview_nav_target == "action_queue":
    st.session_state["app_workspace"] = "Health Status"
    st.session_state["app_area_health"] = "Action Queue"
    try:
        del st.query_params["overview_nav"]
    except Exception:
        st.query_params.clear()
elif overview_nav_target == "open_tickets":
    st.session_state["app_workspace"] = "Ticket Related"
    st.session_state["app_area_ticket"] = "Open Tickets"
    try:
        del st.query_params["overview_nav"]
    except Exception:
        st.query_params.clear()
elif overview_nav_target == "retention":
    st.session_state["app_workspace"] = "Health Status"
    st.session_state["app_area_health"] = "Retention"
    try:
        del st.query_params["overview_nav"]
    except Exception:
        st.query_params.clear()

st.session_state.setdefault("app_workspace", workspace_options[0])
st.session_state.setdefault("app_area_health", health_area_options[0])
st.session_state.setdefault("app_area_ticket", ticket_area_options[0])
st.session_state.setdefault("app_area_project", project_area_options[0])

_current_workspace_for_brand = str(st.session_state.get("app_workspace", workspace_options[0]))
render_sidebar_brand_card(_current_workspace_for_brand)
st.sidebar.markdown("<div style='height:0.38rem;'></div>", unsafe_allow_html=True)
workspace_button_container = st.sidebar.container(border=True)
with workspace_button_container:
    st.markdown('<div class="workspace-button-group-marker"></div>', unsafe_allow_html=True)
    for workspace_name in workspace_options:
        if st.button(
            workspace_button_labels.get(workspace_name, workspace_name),
            key=f"workspace_btn_{workspace_name}",
            use_container_width=True,
            type="primary" if st.session_state.get("app_workspace") == workspace_name else "secondary",
        ):
            st.session_state["app_workspace"] = workspace_name
            st.rerun()

selected_workspace = str(st.session_state.get("app_workspace", workspace_options[0]))

if selected_workspace == "Health Status":
    area_options = health_area_options
    area_state_key = "app_area_health"
elif selected_workspace == "Ticket Related":
    area_options = ticket_area_options
    area_state_key = "app_area_ticket"
else:
    area_options = project_area_options
    area_state_key = "app_area_project"

render_sidebar_section_label("Main Navigation")
area_button_labels = {
    "Overview": ":material/grid_view:  Overview",
    "Action Queue": ":material/content_paste_search:  Action Queue",
    "Trends": ":material/trending_up:  Trends",
    "Retention": ":material/history:  Retention",
    "Open Tickets": ":material/confirmation_number:  Open Tickets",
    "Ticket Response Assistant": ":material/robot_2:  Response Assistant",
    "Camera Installation Builder": ":material/construction:  Installation Builder",
}
for area_name in area_options:
    if st.sidebar.button(
        area_button_labels.get(area_name, area_name),
        key=f"area_btn_{selected_workspace}_{area_name}",
        use_container_width=True,
        type="primary" if st.session_state.get(area_state_key, area_options[0]) == area_name else "secondary",
    ):
        st.session_state[area_state_key] = area_name
        st.rerun()

selected_area = str(st.session_state.get(area_state_key, area_options[0]))

csv_path = DEFAULT_SITE_HEALTH_PATH

if "site_health_upload_nonce" not in st.session_state:

    st.session_state.site_health_upload_nonce = 0

if "site_health_source_mode" not in st.session_state:

    st.session_state.site_health_source_mode = "CSV path"

if "site_health_last_upload_signature" not in st.session_state:

    st.session_state.site_health_last_upload_signature = None

if selected_workspace == "Health Status":
    with st.sidebar.expander("Health Data Source", expanded=False):
        csv_path = st.text_input(
            "Local Path",
            value=DEFAULT_SITE_HEALTH_PATH,
            help="Default is the repo-local export next to app.py.",
        )
        uploaded = st.file_uploader(
            "Upload Site Health CSV",
            type=["csv"],
            key=f"site_health_upload_{st.session_state.site_health_upload_nonce}",
            help="Use this for a temporary local file when you do not want to change the path field.",
        )
        source_mode = "Uploaded file" if uploaded is not None else "CSV path"
        st.session_state.site_health_source_mode = source_mode
        if uploaded is not None:
            if st.button("Clear Uploaded File", use_container_width=True):
                st.session_state.site_health_upload_nonce += 1
                st.session_state.site_health_source_mode = "CSV path"
                st.session_state.site_health_last_upload_signature = None
                st.rerun()
    load_clicked = False
    hard_reset_clicked = False
else:
    uploaded = None
    source_mode = st.session_state.site_health_source_mode
    load_clicked = False
    hard_reset_clicked = False

upload_signature = None

if uploaded is not None:

    upload_signature = (uploaded.name, uploaded.size)

if upload_signature is not None and upload_signature != st.session_state.site_health_last_upload_signature:

    st.session_state.site_health_last_upload_signature = upload_signature

elif uploaded is None and st.session_state.site_health_last_upload_signature is not None:

    st.session_state.site_health_last_upload_signature = None

source_mode = st.session_state.site_health_source_mode



if load_clicked:

    clear_func = getattr(read_site_health_csv, "clear", None)

    if clear_func:

        clear_func()

if hard_reset_clicked:

    st.cache_data.clear()

    st.session_state.ping_status_by_ip = {}

    st.session_state.ping_pending_ips = []

    st.sidebar.success("All data caches cleared.")

    st.rerun()



tdx_email_to = TDX_HELPDESK_EMAIL
smtp_host = os.getenv("SMTP_HOST", "")
smtp_port = int(os.getenv("SMTP_PORT", "587"))
smtp_username = os.getenv("SMTP_USERNAME", "")
smtp_password = os.getenv("SMTP_PASSWORD", "")
smtp_from_email = os.getenv("SMTP_FROM", "")
ticket_threshold_hours = 24

if selected_workspace == "Ticket Related":
    with st.sidebar.expander("Ticket Automation Settings", expanded=False):

        st.caption("Administrative settings")
        st.caption(f"Help tickets are sent to: {TDX_HELPDESK_EMAIL}")

        smtp_host = st.text_input("SMTP host", value=smtp_host)

        smtp_port = st.number_input("SMTP port", min_value=1, max_value=65535, value=smtp_port)

        smtp_username = st.text_input("SMTP username", value=smtp_username)

        smtp_password = st.text_input("SMTP password", value=smtp_password, type="password")

        smtp_from_email = st.text_input("From email", value=smtp_from_email)

        ticket_threshold_hours = st.number_input(

            "Auto-ticket threshold (hours)",

            min_value=1,

            max_value=168,

            value=24,

            step=1,

            help="Auto-queue a ticket when a device remains offline at or above this threshold.",

        )



generate_weekly_digest_clicked = False



if st.session_state.get("last_source_mode") != source_mode:

    clear_func = getattr(read_site_health_csv, "clear", None)

    if clear_func:

        clear_func()

    st.session_state["last_source_mode"] = source_mode



if source_mode == "Uploaded file":

    should_load = load_clicked or (uploaded is not None)

else:

    should_load = load_clicked or os.path.exists(csv_path)

if not should_load:

    if source_mode == "Uploaded file":

        st.info("Select an uploaded CSV file and click **Load / Reload**.")

    else:

        st.info("Set the CSV path and click **Load / Reload**.")

    st.stop()



# Load view-level CSV

df = pd.DataFrame()

active_source_label = ""

active_source_detail = ""

active_source_signature = ""

try:

    if source_mode == "Uploaded file":

        if uploaded is None:

            st.info("Please upload a CSV file for Uploaded file mode.")

            st.stop()

        assert uploaded is not None

        active_source_label = f"Uploaded file: {uploaded.name}"

        df = parse_site_health_csv_bytes(uploaded.getvalue())

    else:

        active_source_label = f"CSV path: {csv_path}"

        active_source_signature = get_file_signature(csv_path)

        df = read_site_health_csv(csv_path, active_source_signature)

        try:

            modified_local = datetime.fromtimestamp(os.path.getmtime(csv_path), tz=timezone.utc).astimezone()

            active_source_detail = f"Path file modified: {modified_local.strftime('%Y-%m-%d %H:%M:%S %Z')}"

        except OSError:

            active_source_detail = ""

except Exception as e:

    st.error(f"Failed to load site-health CSV: {e}")
    st.info("Check the active CSV path or switch to Uploaded file in the Health Data Source panel, then reload.")

    st.stop()



if active_source_label:
    if selected_workspace == "Health Status":
        pass



# Validate minimum columns

required_cols = {"Server Name", "Device Name"}

missing = required_cols - set(df.columns)

if missing:

    st.error(f"The site-health CSV is missing required columns: {sorted(list(missing))}")
    st.info("The file must include at least 'Server Name' and 'Device Name'. Export a fresh Site Health CSV and reload it.")

    st.stop()

if selected_workspace == "Health Status":
    st.sidebar.caption(f"Loaded rows: {len(df):,}")
    st.sidebar.markdown("---")



# Physical identity + notes identity

df["physical_key"] = build_physical_key(df)

df["key"] = df["physical_key"]  # notes follow physical camera

df["Device Name Base"] = device_name_base(df)



# Merge notes into views

notes_df = load_notes(NOTES_PATH)

df = df.merge(notes_df, on="key", how="left")

df["disposition"] = df["disposition"].fillna("")

df["notes"] = df["notes"].fillna("")



# Health on views

df = compute_health_state(df)



# Keep views + build devices

df_views = df.copy()

observed_server_names: list[str] = []

if "Server Name" in df_views.columns:

    observed_server_names = sorted(

        {

            normalize_server_name(server)

            for server in df_views["Server Name"].dropna().astype(str).tolist()

            if normalize_server_name(server)

        }

    )

server_roles_df = load_server_roles(SERVER_ROLE_MAP_PATH, observed_server_names)

server_role_map = server_role_map_from_df(server_roles_df)

unmapped_servers = [

    server_name

    for server_name in observed_server_names

    if canonical_server_name_key(server_name) not in server_role_map

]

if selected_workspace == "Health Status":
    with st.sidebar.expander("Server Role Mapping", expanded=False):

        st.caption("Advanced admin")
        st.caption(f"Map file: {SERVER_ROLE_MAP_PATH}")
        save_error = str(st.session_state.get("server_role_map_save_error", "") or "")
        if save_error:
            st.warning(save_error)

        st.caption(

            "Assign each server as Primary or Secondary. "

            "Unmapped servers fall back to first/second order."

        )

        role_editor_df = server_roles_df.copy().reset_index(drop=True)

        if role_editor_df.empty:

            st.info("No servers discovered yet from the current CSV.")

        else:

            edited_roles = st.data_editor(

                role_editor_df,

                width="stretch",

                hide_index=True,

                disabled=["Server Name"],

                column_config={

                    "Server Name": st.column_config.TextColumn("Server Name", width="large"),

                    "Role": st.column_config.SelectboxColumn(

                        "Role",

                        options=["", "Primary", "Secondary"],

                        width="medium",

                    ),

                },

                key="server_role_mapping_editor",

            )

            if st.button("Save Server Role Mapping", key="save_server_role_mapping"):

                save_server_roles(SERVER_ROLE_MAP_PATH, edited_roles)
                if st.session_state.get("server_role_map_save_error"):
                    st.warning(str(st.session_state["server_role_map_save_error"]))
                else:
                    st.success("Saved server role mapping.")

                st.rerun()

        if unmapped_servers:

            st.warning(

                f"{len(unmapped_servers)} server(s) are unmapped: "

                + ", ".join(unmapped_servers[:6])

                + ("..." if len(unmapped_servers) > 6 else "")

            )

        else:

            st.caption("All discovered servers are mapped.")

df_devices = build_devices_table(df_views, server_role_map)

df_devices, retention_available, retention_source_col = add_retention_fields(df_devices, df_views)

observed_at = utc_now_timestamp()

tracking_df = load_tracking_state(TRACKING_PATH)

tickets_df = load_tickets(TICKETS_PATH)

append_state_transitions(TRANSITIONS_PATH, df_devices, tracking_df, observed_at)

transitions_df = load_state_transitions(TRANSITIONS_PATH)

df_devices, tracking_df, tickets_df, ticket_notices, ticket_errors = sync_tracking_and_tickets(

    df_devices,

    tracking_df,

    tickets_df,

    observed_at,

    tdx_email_to=tdx_email_to,

    smtp_settings={

        "host": smtp_host,

        "port": smtp_port,

        "username": smtp_username,

        "password": smtp_password,

        "from_email": smtp_from_email,

    },

    ticket_threshold_hours=int(ticket_threshold_hours),

)

df_devices = add_flap_metrics(df_devices, transitions_df, observed_at)

save_tracking_state(TRACKING_PATH, tracking_df)

save_tickets(TICKETS_PATH, tickets_df)

# Ticket automation notices/errors

for note in ticket_notices:

    st.toast(note)

for err in ticket_errors:

    st.toast(err, icon="\u26A0\uFE0F")

# -------- Brand rollup (device-level) --------

for d in [df_views, df_devices]:

    make_norm = d["Make"].astype(str).str.strip().str.lower()

    d["Brand"] = "Other"

    d.loc[make_norm.str.contains("avigilon", na=False), "Brand"] = "Avigilon"

    d.loc[make_norm.str.contains("axis", na=False), "Brand"] = "Axis"

    d.loc[make_norm.isin(["", "nan", "none"]), "Brand"] = "Unknown"



if {"key", "Flaps (24h)", "Flaps (7d)"}.issubset(df_devices.columns):

    flap_cols = df_devices[["key", "Flaps (24h)", "Flaps (7d)"]].copy()

    flap_cols["key"] = flap_cols["key"].astype(str)

    df_views["key"] = df_views["key"].astype(str)

    df_views = df_views.merge(flap_cols, on="key", how="left")

    df_views["Flaps (24h)"] = pd.to_numeric(df_views["Flaps (24h)"], errors="coerce").fillna(0).astype(int)

    df_views["Flaps (7d)"] = pd.to_numeric(df_views["Flaps (7d)"], errors="coerce").fillna(0).astype(int)



if retention_available and {"physical_key", "Retention (days)", "Retention OK", "Retention Gap"}.issubset(df_devices.columns):

    retention_cols = df_devices[["physical_key", "Retention (days)", "Retention OK", "Retention Gap"]].copy()

    retention_cols["physical_key"] = retention_cols["physical_key"].astype(str)

    df_views["physical_key"] = df_views["physical_key"].astype(str)

    df_views = df_views.merge(retention_cols, on="physical_key", how="left")



# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Summary bar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

if "view_mode" not in st.session_state:

    st.session_state.view_mode = "devices"



brand_options = ["Avigilon", "Axis", "Other", "Unknown"]



if "brand_select" not in st.session_state:

    st.session_state.brand_select = []



def on_metric_click(btype):

    if btype == "unique":

        st.session_state.view_mode = "devices"

        st.session_state.brand_select = []

    elif btype == "export":

        st.session_state.view_mode = "views"

        st.session_state.brand_select = []

    elif btype == "avigilon":

        st.session_state.view_mode = "devices"

        st.session_state.brand_select = ["Avigilon"]

    elif btype == "axis":

        st.session_state.view_mode = "devices"

        st.session_state.brand_select = ["Axis"]

    elif btype == "other":

        st.session_state.view_mode = "devices"

        st.session_state.brand_select = ["Other", "Unknown"]



if selected_workspace == "Health Status":
    st.session_state.setdefault("health_scope_mode", "unique")



# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Sidebar Filters ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

brand_selected: list[str] = st.session_state.get("brand_select", [])
health_selected: list[str] = st.session_state.get("health_select", [])
show_only_issues = bool(st.session_state.get("show_only_issues", False))
connected_filter = st.session_state.get("connected_filter", "Any")
visible_filter = st.session_state.get("visible_filter", "Any")

if selected_workspace == "Health Status":
    with st.sidebar.expander("Filters", expanded=False):
        st.caption("View controls")
        st.caption("Narrow the health views without changing the loaded CSV.")

        brand_selected = st.multiselect(

            "Brand",

            options=brand_options,

            key="brand_select",

            help="Filter the camera inventory by manufacturer/brand values found in the export.",
        )

        health_options = ["Online", "Offline", "Offline (but still visible)"]

        health_selected = st.multiselect(

            "Health state",

            options=health_options,

            default=[],

            key="health_select",

            help="Limit the view to one or more computed health states.",
        )

        show_only_issues = st.checkbox(

            "Show only cameras needing attention",

            value=False,

            key="show_only_issues",

            help="Strict offline, not visible, hard error flags, or offline-visible devices that are not confirmed pingable.",

        )

        connected_filter = st.selectbox(
            "Connected status",
            ["Any", "TRUE", "FALSE"],
            index=["Any", "TRUE", "FALSE"].index(connected_filter if connected_filter in ["Any", "TRUE", "FALSE"] else "Any"),
            key="connected_filter",
            help="Filter by the export's connected flag.",
        )

        visible_filter = st.selectbox(
            "Visible status",
            ["Any", "TRUE", "FALSE"],
            index=["Any", "TRUE", "FALSE"].index(visible_filter if visible_filter in ["Any", "TRUE", "FALSE"] else "Any"),
            key="visible_filter",
            help="Filter by the export's visible flag.",
        )

    with st.sidebar.expander("Export Diagnostics", expanded=False):

        st.caption("Advanced diagnostics")
        st.caption("Helpful when validating a new export format or debugging missing fields.")
        st.write(list(df_views.columns))



# Main area search ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

search_text = st.session_state.get("search_text", "")
if selected_workspace == "Health Status":
    render_sidebar_section_label("Configuration & Tools")




# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Apply all filters ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

if st.session_state.get("view_mode", "devices") == "views":

    base = df_views.copy()

else:

    base = df_devices.copy()

filtered = base.copy()



if brand_selected:

    filtered = filtered[filtered["Brand"].isin(brand_selected)]

filtered = apply_global_search(filtered, search_text)

if health_selected:

    filtered = filtered[filtered["Health State"].isin(health_selected)]

if connected_filter != "Any":

    want = connected_filter == "TRUE"

    filtered = filtered[filtered["Connected_bool"] == want]

if visible_filter != "Any":

    want = visible_filter == "TRUE"

    filtered = filtered[filtered["Visible_bool"] == want]



initialize_ping_queue(filtered)

process_ping_batch(batch_size=2)

filtered_with_ping = add_ping_status_for_issues(filtered)

filtered_with_ping = apply_confirmed_healthy_override(filtered_with_ping)

issues_mask = compute_action_required_mask(filtered_with_ping, use_ping_results=False)


if show_only_issues:

    filtered = filtered[issues_mask]

    filtered_with_ping = filtered_with_ping.loc[filtered.index].copy()

    issues_mask = pd.Series(True, index=filtered.index, dtype=bool)



issues_df = filtered_with_ping[issues_mask]

all_df = filtered



# Device-level filtered set for additive tabs (always device-level, regardless view mode).

filtered_devices = df_devices.copy()

if brand_selected:

    filtered_devices = filtered_devices[filtered_devices["Brand"].isin(brand_selected)]

filtered_devices = apply_global_search(filtered_devices, search_text)

if health_selected:

    filtered_devices = filtered_devices[filtered_devices["Health State"].isin(health_selected)]

if connected_filter != "Any":

    want = connected_filter == "TRUE"

    filtered_devices = filtered_devices[filtered_devices["Connected_bool"] == want]

if visible_filter != "Any":

    want = visible_filter == "TRUE"

    filtered_devices = filtered_devices[filtered_devices["Visible_bool"] == want]

initialize_ping_queue(filtered_devices)

process_ping_batch(batch_size=2)

filtered_devices_with_ping = add_ping_status_for_issues(filtered_devices)

filtered_devices_with_ping = apply_confirmed_healthy_override(filtered_devices_with_ping)

device_issues_mask = compute_action_required_mask(filtered_devices_with_ping, use_ping_results=False)
if show_only_issues:

    filtered_devices = filtered_devices_with_ping[device_issues_mask].copy()

else:

    filtered_devices = filtered_devices_with_ping



prioritized_source = filtered_devices.copy()

prioritized_df = compute_priority_table(prioritized_source)



retention_violations_df = pd.DataFrame()

if retention_available and {"Retention (days)", "Retention Gap", "Retention OK"}.issubset(prioritized_df.columns):

    retention_violations_df = prioritized_df[~prioritized_df["Retention OK"].fillna(False)].copy()

    retention_violations_df = retention_violations_df.sort_values("Retention Gap", ascending=False)



open_ticket_states = ["Open"]

open_tickets_df = tickets_df[tickets_df["ticket_state"].isin(open_ticket_states)].copy()

tickets_editor_states = ["Open", "Suppressed"]

tickets_editor_df = tickets_df[tickets_df["ticket_state"].isin(tickets_editor_states)].copy()

pending_tickets_df = tickets_df[tickets_df["ticket_state"] == "Pending Send"].copy()

if selected_workspace == "Health Status":
    export_filename = f"system-pulse-{selected_area.lower().replace(' ', '-')}.csv"
    export_frame = filtered_devices if selected_area in {"Overview", "Action Queue", "Trends", "Retention"} else all_df
    with st.sidebar.container():
        render_sidebar_html(
            '<div class="sidebar-bottom-shell"><div class="sidebar-bottom-meta"></div></div>'
        )
        st.sidebar.button(
            ":material/settings:  Settings",
            use_container_width=True,
            key="sidebar_settings_button",
            type="secondary",
        )
        generate_weekly_digest_clicked = st.sidebar.button(
            "Generate Weekly Digest",
            use_container_width=True,
            key="sidebar_generate_weekly_digest_bottom",
            type="secondary",
        )
        st.sidebar.download_button(
            ":material/file_export:  Export Report",
            data=export_frame.to_csv(index=False).encode("utf-8"),
            file_name=export_filename,
            mime="text/csv",
            use_container_width=True,
            key="sidebar_export_report",
            type="primary",
        )

issue_keys = set(issues_df["key"].astype(str)) if "key" in issues_df.columns else set()

pending_issue_tickets_df = pending_tickets_df[

    pending_tickets_df["key"].astype(str).isin(issue_keys)

].copy()



if generate_weekly_digest_clicked:

    st.session_state["weekly_digest_text"] = build_weekly_digest(

        devices_df=df_devices,

        tracking_df=tracking_df,

        tickets_df=tickets_df,

        transitions_df=transitions_df,

        ticket_threshold_hours=int(ticket_threshold_hours),

        retention_available=retention_available,

    )

    st.session_state["weekly_digest_generated_at"] = format_timestamp(utc_now_timestamp())



# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Worklist Tabs ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬

# Tabs are defined below after ticket state is prepared.



digest_text = st.session_state.get("weekly_digest_text", "")

if selected_workspace == "Health Status" and digest_text:

    with st.expander("Weekly Digest", expanded=True):

        st.text_area(

            "Copy/Paste Digest",

            value=digest_text,

            height=260,

            key="weekly_digest_text_area",

        )

        can_send_digest = all([smtp_host, smtp_port, smtp_username, smtp_password, smtp_from_email, tdx_email_to])

        if st.button("Send Digest Email", key="send_weekly_digest_email", disabled=not can_send_digest):

            digest_subject = f"Weekly Camera Health Digest - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

            sent, err = send_ticket_email(

                smtp_host=smtp_host,

                smtp_port=int(smtp_port),

                smtp_username=smtp_username,

                smtp_password=smtp_password,

                from_email=smtp_from_email,

                to_email=tdx_email_to,

                subject=digest_subject,

                body=digest_text,

            )

            if sent:

                st.toast("Weekly digest email sent.")

            else:

                st.toast(f"Weekly digest email failed: {err}", icon="\u26A0\uFE0F")





def render_operations_snapshot(

    devices_subset: pd.DataFrame,

    tickets_subset: pd.DataFrame,

    retention_enabled: bool,

) -> None:

    def _extract_selected_category(selection_event: object, selection_name: str) -> str | None:

        if selection_event is None:

            return None

        selection_payload: Any = getattr(selection_event, "selection", None)

        if selection_payload is None and isinstance(selection_event, dict):

            selection_payload = selection_event.get("selection")



        if not selection_payload:

            return None



        selected = None

        if isinstance(selection_payload, dict):

            selected = selection_payload.get(selection_name)

            if selected is None and len(selection_payload) == 1:

                selected = next(iter(selection_payload.values()))

        else:

            selected = selection_payload



        if isinstance(selected, list) and selected:

            first = selected[0]

            if isinstance(first, dict):

                value = first.get("Category")

                if value is not None:

                    return str(value)

                if first:

                    return str(next(iter(first.values())))

        if isinstance(selected, dict):

            if "Category" in selected:

                value = selected.get("Category")

                if isinstance(value, list):

                    return str(value[0]) if value else None

                return str(value) if value is not None else None

            for nested in selected.values():

                if isinstance(nested, list) and nested and isinstance(nested[0], dict):

                    value = nested[0].get("Category")

                    if value is not None:

                        return str(value)

        return None



    def _render_snapshot_metric(
        label: str,
        value: str,
        *,
        variant: str = "default",
        eyebrow: str | None = None,
    ) -> None:

        render_html(
            f"""

            <div class="ops-snapshot-metric-card ops-snapshot-metric-card--{html_escape(variant)}">

                {f'<div class="ops-snapshot-metric-eyebrow">{html_escape(eyebrow)}</div>' if eyebrow else ''}

                <div class="ops-snapshot-metric-row">
                    <div class="ops-snapshot-metric-label">{label}</div>
                    <div class="ops-snapshot-metric-value">{value}</div>
                </div>

            </div>

            """
        )



    def render_donut_chart(

        data: pd.Series,

        center_text: str,

        center_label: str = "Devices",

        panel_title: str | None = None,

        max_slices: int = 8,

        empty_message: str = "No data in current scope.",

        category_colors: dict[str, str] | None = None,

        chart_key: str | None = None,

        selection_name: str = "slice_select",

        legend_columns: int = 2,

        legend_label_limit: int = 120,

        legend_max_width_px: int = 280,

        legend_position: str = "right",

    ) -> str | None:

        counts = pd.to_numeric(data, errors="coerce").fillna(0)

        counts = counts[counts > 0].sort_values(ascending=False)

        if counts.empty:

            st.info(empty_message)

            return None



        if max_slices >= 2 and len(counts) > max_slices:

            head = counts.head(max_slices - 1).copy()

            other_count = counts.iloc[max_slices - 1:].sum()

            if other_count > 0:

                head.loc["Other"] = other_count

            counts = head



        chart_df = pd.DataFrame({

            "Category": counts.index.astype(str),

            "Count": counts.values,

        })



        width = 300

        height = 232

        donut_outer_radius = 74

        donut_inner_radius = 44

        balanced_palette = [

            "#5B8FF9",

            "#6DC8EC",

            "#9270CA",

            "#F6903D",

            "#F08BB4",

            "#5AD8A6",

            "#C2C8D5",

            "#7C6AF2",

            "#FF9D4D",

        ]

        domain = chart_df["Category"].tolist()

        if category_colors:

            palette = [

                category_colors.get(category, balanced_palette[i % len(balanced_palette)])

                for i, category in enumerate(domain)

            ]

        else:

            palette = [balanced_palette[i % len(balanced_palette)] for i in range(len(domain))]

        legend_is_right = str(legend_position).strip().lower() == "right"



        try:

            import altair as alt  # type: ignore[import-untyped]



            legend_cfg = alt.Legend(

                title=panel_title or None,

                orient="right" if legend_is_right else "bottom",

                direction="vertical" if legend_is_right else "horizontal",

                columns=1 if legend_is_right else legend_columns,

                labelLimit=legend_label_limit,

                columnPadding=8,

                rowPadding=3,

                symbolType="circle",

                symbolSize=120,

                offset=8,

            )

            chart_select = alt.selection_point(fields=["Category"], name=selection_name, empty=True)

            donut = (

                alt.Chart(chart_df)

                .mark_arc(innerRadius=donut_inner_radius, outerRadius=donut_outer_radius, cornerRadius=3)

                .encode(

                    theta=alt.Theta("Count:Q"),

                    opacity=alt.condition(chart_select, alt.value(1.0), alt.value(0.45)),

                    color=alt.Color(

                        "Category:N",

                        scale=alt.Scale(domain=domain, range=palette),

                        legend=legend_cfg,

                    ),

                    tooltip=[

                        alt.Tooltip("Category:N", title="Category"),

                        alt.Tooltip("Count:Q", title="Count", format=",.0f"),

                    ],

                )

                .add_params(chart_select)

                .properties(width=width, height=height)

            )

            center_value = (

                alt.Chart(pd.DataFrame({"Label": [center_text]}))

                .mark_text(fontSize=13, fontWeight="bold", color="#F5FAFF")

                .encode(

                    text="Label:N",

                    x=alt.value(width // 2),

                    y=alt.value((height // 2) - 8),

                )

                .properties(width=width, height=height)

            )

            center_label_mark = (

                alt.Chart(pd.DataFrame({"Label": [center_label]}))

                .mark_text(fontSize=9, color="#B7C5DA")

                .encode(

                    text="Label:N",

                    x=alt.value(width // 2),

                    y=alt.value((height // 2) + 12),

                )

                .properties(width=width, height=height)

            )

            final_chart = (

                (donut + center_value + center_label_mark)

                .properties(width=width, height=(height if legend_is_right else height + 36))

                .configure(background="transparent")

                .configure_view(strokeWidth=0)

                .configure_legend(

                    orient="right" if legend_is_right else "bottom",

                    direction="vertical" if legend_is_right else "horizontal",

                    columns=1 if legend_is_right else legend_columns,

                    titleColor="#C9D4E5",

                    titleFontSize=16,

                    titleFontWeight=650,

                    titlePadding=4,

                    labelColor="#DEE6F2",

                    symbolStrokeColor="#DEE6F2",

                )

            )

            selection_event = st.altair_chart(

                final_chart,

                use_container_width=True,

                key=chart_key,

                on_select="rerun",

                selection_mode=[selection_name],

            )

            return _extract_selected_category(selection_event, selection_name)

        except Exception:

            total = float(chart_df["Count"].sum())

            if total <= 0:

                st.info(empty_message)

                return None



            segment_parts: list[str] = []

            legend_items: list[str] = []

            pct_cursor = 0.0

            for idx, row in chart_df.iterrows():

                category = str(row["Category"])

                count_value = float(row["Count"])

                color = palette[idx % len(palette)]

                pct = (count_value / total) * 100

                start_pct = pct_cursor

                end_pct = pct_cursor + pct

                segment_parts.append(f"{color} {start_pct:.3f}% {end_pct:.3f}%")

                pct_cursor = end_pct

                legend_items.append(

                    f'<div class="ops-donut-fallback-legend-item">'

                    f'<span class="ops-donut-fallback-swatch" style="background:{color};"></span>'

                    f'<span class="ops-donut-fallback-label">{html_escape(category)}</span>'

                    f'<span class="ops-donut-fallback-count">{int(count_value):,}</span>'

                    f'</div>'

                )



            legend_cols = max(1, min(4, int(legend_columns)))

            legend_max_width = max(140, min(420, int(legend_max_width_px)))

            title_html = (

                f'<div class="ops-donut-fallback-panel-title">{html_escape(panel_title)}</div>'

                if panel_title

                else ""

            )

            st.markdown(

                """

                <style>

                .ops-donut-fallback-wrap {

                    display: flex;

                    flex-direction: row;

                    align-items: flex-start;

                    justify-content: center;

                    gap: 0.54rem;

                    margin-top: -0.10rem;

                    width: fit-content;

                    max-width: 100%;

                    margin-left: auto;

                    margin-right: auto;

                }

                .ops-donut-fallback-ring {

                    width: 168px;

                    height: 168px;

                    border-radius: 50%;

                    display: flex;

                    align-items: center;

                    justify-content: center;

                    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.05);

                    flex-shrink: 0;

                }

                .ops-donut-fallback-center {

                    width: 102px;

                    height: 102px;

                    border-radius: 50%;

                    display: flex;

                    flex-direction: column;

                    align-items: center;

                    justify-content: center;

                    text-align: center;

                    background: radial-gradient(circle at 32% 25%, #3A4554, #1D2530);

                    border: 1px solid rgba(255, 255, 255, 0.08);

                }

                .ops-donut-fallback-center-value {

                    color: #F5FAFF;

                    font-size: 0.96rem;

                    line-height: 1.05;

                    font-weight: 700;

                    letter-spacing: 0.01em;

                }

                .ops-donut-fallback-center-label {

                    color: #B7C5DA;

                    margin-top: 0.15rem;

                    font-size: 0.64rem;

                    text-transform: uppercase;

                    letter-spacing: 0.08em;

                    line-height: 1;

                }

                .ops-donut-fallback-legend {

                    width: fit-content;

                    max-width: min(100%, var(--legend-max-width));

                    display: grid;

                    grid-template-columns: repeat(var(--legend-cols), minmax(0, 1fr));

                    gap: 0.16rem 0.34rem;

                    margin-left: 0;

                }

                .ops-donut-fallback-legend-wrap {

                    display: flex;

                    flex-direction: column;

                    align-self: flex-start;

                    min-width: 0;

                }

                .ops-donut-fallback-panel-title {

                    color: #C9D4E5;

                    font-size: 1rem;

                    font-weight: 650;

                    line-height: 1.2;

                    margin: 0 0 0.24rem 0;

                }

                .ops-donut-fallback-legend-item {

                    display: grid;

                    grid-template-columns: auto minmax(88px, 1fr) auto;

                    align-items: center;

                    column-gap: 0.4rem;

                    min-width: 0;

                    color: #DEE6F2;

                    font-size: 0.76rem;

                    line-height: 1.1;

                    padding: 0.05rem 0;

                }

                .ops-donut-fallback-swatch {

                    width: 0.62rem;

                    height: 0.62rem;

                    border-radius: 999px;

                    flex-shrink: 0;

                    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.14);

                }

                .ops-donut-fallback-label {

                    min-width: 0;

                    overflow: hidden;

                    text-overflow: ellipsis;

                    white-space: nowrap;

                    opacity: 0.95;

                }

                .ops-donut-fallback-count {

                    font-variant-numeric: tabular-nums;

                    color: #F7FBFF;

                    font-weight: 700;

                    min-width: 2.4rem;

                    text-align: right;

                }

                @media (max-width: 1500px) {

                    .ops-donut-fallback-wrap {

                        flex-direction: column;

                        gap: 0.5rem;

                    }

                }

                </style>

                """,

                unsafe_allow_html=True,

            )

            fallback_html = (

                f'<div class="ops-donut-fallback-wrap" style="--legend-cols:{legend_cols}; --legend-max-width:{legend_max_width}px;">'

                f'<div class="ops-donut-fallback-ring" style="background: conic-gradient({", ".join(segment_parts)});">'

                '<div class="ops-donut-fallback-center">'

                f'<div class="ops-donut-fallback-center-value">{html_escape(center_text)}</div>'

                f'<div class="ops-donut-fallback-center-label">{html_escape(center_label)}</div>'

                '</div>'

                '</div>'

                '<div class="ops-donut-fallback-legend-wrap">'

                f'{title_html}'

                '<div class="ops-donut-fallback-legend">'

                f'{"".join(legend_items)}'

                '</div>'

                '</div>'

                '</div>'

            )

            st.markdown(fallback_html, unsafe_allow_html=True)

            return None



    def render_ping_progress_visual(

        ping_counts: pd.Series,

        total_devices: int,

        panel_title: str,

    ) -> None:

        pingable = int(ping_counts.get("Pingable", 0))

        not_pingable = int(ping_counts.get("Do Not Ping", 0))

        pending = int(ping_counts.get("Pending / Unknown", 0))

        total = int(total_devices)

        if total <= 0:

            st.info("No action-required devices in current scope.")

            return



        checked = pingable + not_pingable

        checked_pct = int(round((checked / total) * 100))



        segment_parts: list[str] = []

        pct_cursor = 0.0

        for count, color in [

            (pingable, OPS_COLOR_GOOD),

            (not_pingable, OPS_COLOR_WARN),

            (pending, OPS_COLOR_UNKNOWN),

        ]:

            pct = (float(count) / float(total)) * 100 if total else 0.0

            start_pct = pct_cursor

            end_pct = pct_cursor + pct

            if pct > 0:

                segment_parts.append(f"{color} {start_pct:.3f}% {end_pct:.3f}%")

            pct_cursor = end_pct

        if not segment_parts:

            segment_parts = [f"{OPS_COLOR_UNKNOWN} 0% 100%"]



        legend_rows = [

            ("Pingable", pingable, OPS_COLOR_GOOD),

            ("Do Not Ping", not_pingable, OPS_COLOR_WARN),

            ("Pending / Unknown", pending, OPS_COLOR_UNKNOWN),

        ]

        legend_html = "".join(

            (

                f'<div class="ops-ping-progress-legend-item">'

                f'<span class="ops-ping-progress-swatch" style="background:{row_color};"></span>'

                f'<span class="ops-ping-progress-label">{html_escape(row_label)}</span>'

                f'<span class="ops-ping-progress-count">{row_value:,}</span>'

                f'</div>'

            )

            for row_label, row_value, row_color in legend_rows

        )



        progress_html = (

            '<div class="ops-ping-progress-wrap">'

            f'<div class="ops-ping-progress-ring" style="background: conic-gradient({", ".join(segment_parts)});">'

            '<div class="ops-ping-progress-center">'

            f'<div class="ops-ping-progress-center-value">{checked_pct}%</div>'

            '<div class="ops-ping-progress-center-label">Checked</div>'

            '</div>'

            '</div>'

            '<div class="ops-ping-progress-legend-wrap">'

            f'<div class="ops-ping-progress-panel-title">{html_escape(panel_title)}</div>'

            '<div class="ops-ping-progress-legend-title">Ping Status</div>'

            f'{legend_html}'

            f'<div class="ops-ping-progress-sub">Checked {checked:,} of {total:,} devices</div>'

            '</div>'

            '</div>'

        )

        st.markdown(progress_html, unsafe_allow_html=True)



    def render_fixed_ring_chart(

        title: str,

        data: pd.Series,

        *,

        center_text: str,

        center_label: str,

        empty_message: str,

        category_colors: dict[str, str] | None = None,

        max_items: int = 7,

    ) -> None:

        counts = pd.to_numeric(data, errors="coerce").fillna(0)

        counts = counts[counts > 0].sort_values(ascending=False)

        if max_items > 0:

            counts = counts.head(max_items)

        if counts.empty:

            st.info(empty_message)

            return

        palette_fallback = [

            "#2E8B57",

            "#A93838",

            "#D89A1E",

            "#A4ADBB",

            "#6DC8EC",

            "#9270CA",

        ]

        total = float(counts.sum())

        segment_parts: list[str] = []

        legend_items: list[str] = []

        pct_cursor = 0.0

        for idx, (category, count_value_raw) in enumerate(counts.items()):

            category_text = str(category)

            count_value = float(count_value_raw)

            color = (

                category_colors.get(category_text, palette_fallback[idx % len(palette_fallback)])

                if category_colors

                else palette_fallback[idx % len(palette_fallback)]

            )

            pct = (count_value / total) * 100

            start_pct = pct_cursor

            end_pct = pct_cursor + pct

            pct_cursor = end_pct

            segment_parts.append(f"{color} {start_pct:.3f}% {end_pct:.3f}%")

            legend_items.append(

                f'<div class="ops-chart-legend-item">'

                f'<span class="ops-chart-legend-swatch" style="background:{color};"></span>'

                f'<span class="ops-chart-legend-label">{html_escape(category_text)}</span>'

                f'<span class="ops-chart-legend-count">{int(count_value):,}</span>'

                f'</div>'

            )

        render_html(

            f"""
            <div class="ops-chart-shell">
                <div class="ops-chart-card-title">{html_escape(title)}</div>
                <div class="ops-chart-card-body" style="align-items:flex-start; gap:0.72rem;">
                    <div class="ops-chart-ring" style="background: conic-gradient({", ".join(segment_parts)});">
                        <div class="ops-chart-ring-center">
                            <div class="ops-chart-ring-value">{html_escape(center_text)}</div>
                            <div class="ops-chart-ring-label">{html_escape(center_label)}</div>
                        </div>
                    </div>
                    <div class="ops-chart-legend">
                        {"".join(legend_items)}
                    </div>
                </div>
            </div>
            """

        )



    if devices_subset.empty:

        st.info("No devices in the current filtered scope.")

        return



    devices_subset_with_ping = add_ping_status_for_issues(devices_subset)

    devices_subset_with_ping = apply_confirmed_healthy_override(devices_subset_with_ping)

    health_state = devices_subset_with_ping.get(

        "Health State",

        pd.Series([""] * len(devices_subset_with_ping), index=devices_subset_with_ping.index),

    ).fillna("").astype(str)

    issues_mask_local = compute_action_required_mask(devices_subset_with_ping, use_ping_results=False)

    live_issues_mask_local = compute_action_required_mask(devices_subset_with_ping, use_ping_results=True)

    live_ping_exceptions_local = int((issues_mask_local != live_issues_mask_local).sum())


    scoped_tickets = tickets_subset.copy()

    if "key" in scoped_tickets.columns and "key" in devices_subset.columns:

        scoped_keys = set(devices_subset["key"].astype(str).tolist())

        scoped_tickets = scoped_tickets[scoped_tickets["key"].astype(str).isin(scoped_keys)]



    ticket_states_order = ["Pending Send", "Open", "Acknowledged", "Suppressed", "Resolved"]

    ticket_state_counts = (

        scoped_tickets.get("ticket_state", pd.Series(dtype=str))

        .fillna("")

        .astype(str)

        .value_counts()

        .reindex(ticket_states_order, fill_value=0)

    )



    flaps_7d = pd.to_numeric(

        devices_subset.get("Flaps (7d)", pd.Series([0] * len(devices_subset), index=devices_subset.index)),

        errors="coerce",

    ).fillna(0).astype(int)

    OPS_COLOR_GOOD = "#2E8B57"

    OPS_COLOR_WARN = "#A93838"

    OPS_COLOR_WARN_SOFT = "#D89A1E"

    OPS_COLOR_UNKNOWN = "#A4ADBB"



    st.markdown(

        """

            <style>

            .ops-snapshot-title {
                display: none;
            }

            .ops-snapshot-subtitle {
                display: none;
            }

            .ops-snapshot-metric-card {
                background: linear-gradient(180deg, rgba(26, 31, 39, 0.96), rgba(21, 26, 33, 0.98));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                min-height: 72px;
                padding: 0.65rem 0.78rem 0.68rem 0.78rem;
                box-shadow: none;
            }

            .ops-snapshot-metric-card--priority {
                background: linear-gradient(180deg, rgba(34, 39, 49, 0.98), rgba(27, 33, 41, 0.98));
                border: 1px solid rgba(124, 140, 255, 0.28);
                box-shadow: none;
            }

            .ops-snapshot-metric-eyebrow {
                color: #8ea0b4;
                font-size: 0.62rem;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }

            .ops-snapshot-metric-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.65rem;
            }

            .ops-snapshot-metric-label {
                color: #dce4ef;
                font-size: 0.76rem;
                font-weight: 620;
                line-height: 1.15;
                margin-bottom: 0;
                max-width: none;
            }

            .ops-snapshot-metric-card--priority .ops-snapshot-metric-eyebrow,
            .ops-snapshot-metric-card--priority .ops-snapshot-metric-label,
            .ops-snapshot-metric-card--priority .ops-snapshot-metric-value {
                color: #eef3ff;
            }

            .ops-snapshot-metric-value {
                color: #ffffff;
                font-size: 1.34rem;
                font-weight: 720;
                line-height: 1.0;
                letter-spacing: -0.03em;
            }

            .ops-snapshot-metrics-anchor + div[data-testid="stHorizontalBlock"] {

                gap: 0.35rem;

            }

            @media (max-width: 820px) {
                .ops-snapshot-metrics-anchor + div[data-testid="stHorizontalBlock"] {
                    display: flex;
                    overflow-x: auto;
                    gap: 0.65rem;
                    padding-bottom: 0.2rem;
                    scroll-snap-type: x proximity;
                }
                .ops-snapshot-metrics-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                    min-width: 9.8rem;
                    flex: 0 0 9.8rem;
                    scroll-snap-align: start;
                }
                .ops-snapshot-title {
                    font-size: 1.45rem;
                }
                .ops-snapshot-chart-row-anchor + div[data-testid="stHorizontalBlock"] {
                    gap: 0.7rem;
                }
                .ops-snapshot-chart-row-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {
                    min-height: 14.5rem;
                }
            }

            .ops-snapshot-chart-row-anchor + div[data-testid="stHorizontalBlock"] {

                gap: 0.35rem;

            }

            .ops-snapshot-chart-row-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div {

                background:
                    radial-gradient(circle at top left, rgba(255, 255, 255, 0.05), transparent 34%),
                    linear-gradient(180deg, rgba(38, 45, 56, 0.96), rgba(24, 29, 37, 0.98));

                border: 1px solid rgba(134, 149, 172, 0.2);

                border-radius: 16px;

                padding: 0.34rem 0.38rem 0.3rem 0.38rem;

                box-shadow:
                    0 16px 28px rgba(0, 0, 0, 0.18),
                    inset 0 1px 0 rgba(255, 255, 255, 0.03);

                min-height: 10.9rem;

            }

            .ops-snapshot-chart-card-title {

                color: #F4F7FB;

                font-size: 0.9rem;

                font-weight: 720;

                line-height: 1.2;

                margin: 0 0 0.45rem 0;

                letter-spacing: -0.01em;

            }

            .ops-snapshot-chart-card-subtitle {

                color: #9CB0C9;

                font-size: 0.7rem;

                line-height: 1.25;

                margin: -0.14rem 0 0.45rem 0;

            }

            .ops-chart-card-title {

                color: #F4F7FB;

                font-size: 0.9rem;

                font-weight: 720;

                line-height: 1.2;

                text-align: left;

                margin: 0 0 0.4rem 0;

                letter-spacing: -0.01em;

            }

            .ops-chart-shell {

                width: 100%;

                display: flex;

                flex-direction: column;

                align-items: stretch;

                justify-content: flex-start;

                padding: 0.18rem 0.2rem 0.22rem 0.2rem;

                border-radius: 14px;

                border: 1px solid rgba(255, 255, 255, 0.06);

                background: linear-gradient(180deg, rgba(33, 38, 47, 0.68), rgba(24, 28, 35, 0.5));

                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);

                min-height: 9.25rem;

            }

            .ops-chart-card-body {

                display: flex;

                flex-direction: row;

                align-items: center;

                justify-content: center;

                gap: 0.45rem;

                width: 100%;

                max-width: 285px;

                margin: 0 auto;

                min-height: 8.7rem;

            }

            .ops-chart-ring {

                width: 118px;

                height: 118px;

                border-radius: 50%;

                display: flex;

                align-items: center;

                justify-content: center;

                flex-shrink: 0;

                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.05);

            }

            .ops-chart-ring-center {

                width: 68px;

                height: 68px;

                border-radius: 50%;

                display: flex;

                flex-direction: column;

                align-items: center;

                justify-content: center;

                text-align: center;

                background: radial-gradient(circle at 32% 25%, #3A4554, #1D2530);

                border: 1px solid rgba(255, 255, 255, 0.08);

            }

            .ops-chart-ring-value {

                color: #F5FAFF;

                font-size: 0.96rem;

                line-height: 1.05;

                font-weight: 700;

                letter-spacing: 0.01em;

            }

            .ops-chart-ring-label {

                color: #B7C5DA;

                margin-top: 0.1rem;

                font-size: 0.6rem;

                text-transform: uppercase;

                letter-spacing: 0.08em;

                line-height: 1;

            }

            .ops-chart-legend {

                width: auto;

                max-width: 150px;

                display: flex;

                flex-direction: column;

                gap: 0.18rem;

                align-self: flex-start;

                margin-top: 0.02rem;

            }

            .ops-chart-legend-item {

                display: grid;

                grid-template-columns: auto auto auto;

                align-items: center;

                column-gap: 0.48rem;

                justify-content: start;

                color: #DEE6F2;

                font-size: 0.76rem;

                line-height: 1.1;

                padding: 0.03rem 0;

            }

            .ops-chart-legend-swatch {

                width: 0.62rem;

                height: 0.62rem;

                border-radius: 999px;

                flex-shrink: 0;

                box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.14);

            }

            .ops-chart-legend-label {

                min-width: 0;

                overflow: hidden;

                text-overflow: ellipsis;

                white-space: nowrap;

                opacity: 0.95;

                text-align: left;

            }

            .ops-chart-legend-count {

                font-variant-numeric: tabular-nums;

                color: #F7FBFF;

                font-weight: 700;

                min-width: 2.2rem;

                text-align: left;

            }

            @media (max-width: 1100px) {
                .ops-chart-card-body {
                    flex-direction: column;
                    align-items: center;
                    gap: 0.55rem;
                }
                .ops-chart-card-title {
                    text-align: center;
                }
                .ops-chart-legend {
                    width: 100%;
                    max-width: 220px;
                }
            }

            .ops-ping-progress-wrap {

                display: flex;

                align-items: flex-start;

                justify-content: center;

                gap: 0.4rem;

                width: fit-content;

                max-width: 100%;

                margin: 0.25rem auto 0 auto;

            }

            .ops-ping-progress-ring {

                width: 148px;

                height: 148px;

                border-radius: 50%;

                display: flex;

                align-items: center;

                justify-content: center;

                flex-shrink: 0;

                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.05);

            }

            .ops-ping-progress-center {

                width: 88px;

                height: 88px;

                border-radius: 50%;

                display: flex;

                flex-direction: column;

                align-items: center;

                justify-content: center;

                text-align: center;

                background: radial-gradient(circle at 32% 25%, #3A4554, #1D2530);

                border: 1px solid rgba(255, 255, 255, 0.08);

            }

            .ops-ping-progress-center-value {

                color: #F5FAFF;

                font-size: 1.02rem;

                line-height: 1.05;

                font-weight: 700;

                letter-spacing: 0.01em;

            }

            .ops-ping-progress-center-label {

                color: #B7C5DA;

                margin-top: 0.14rem;

                font-size: 0.64rem;

                text-transform: uppercase;

                letter-spacing: 0.08em;

                line-height: 1;

            }

            .ops-ping-progress-legend-wrap {

                width: min(100%, 190px);

                display: flex;

                flex-direction: column;

                gap: 0.16rem;

            }

            .ops-ping-progress-panel-title {

                color: #F4F7FB;

                font-size: 1.05rem;

                font-weight: 720;

                line-height: 1.2;

                margin: 0 0 0.3rem 0;

            }

            .ops-ping-progress-legend-title {

                color: #9CB0C9;

                font-size: 0.64rem;

                letter-spacing: 0.08em;

                text-transform: uppercase;

                line-height: 1.15;

                margin-bottom: 0.12rem;

            }

            .ops-ping-progress-legend-item {

                display: grid;

                grid-template-columns: auto minmax(88px, 1fr) auto;

                align-items: center;

                column-gap: 0.4rem;

                font-size: 0.76rem;

                line-height: 1.1;

                color: #DEE6F2;

                min-width: 0;

                padding: 0.05rem 0;

            }

            .ops-ping-progress-swatch {

                width: 0.62rem;

                height: 0.62rem;

                border-radius: 50%;

                flex-shrink: 0;

                box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.14);

            }

            .ops-ping-progress-label {

                color: #DEE6F2;

                font-size: 0.76rem;

                overflow: hidden;

                text-overflow: ellipsis;

                white-space: nowrap;

            }

            .ops-ping-progress-count {

                color: #F7FBFF;

                font-size: 0.76rem;

                font-weight: 700;

                text-align: right;

                min-width: 2.4rem;

            }

            .ops-ping-progress-sub {

                color: #B7C5DA;

                font-size: 0.7rem;

                line-height: 1.2;

                margin-top: 0.18rem;

            }

            .ops-snapshot-chart-row-anchor + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {

                display: flex;

                align-items: stretch;

            }

            </style>

            """,

            unsafe_allow_html=True,

        )



    st.markdown('<div class="ops-snapshot-metrics-anchor"></div>', unsafe_allow_html=True)

    metric_1, metric_2, metric_3, metric_4, metric_5 = st.columns(5)
    with metric_1:

        _render_snapshot_metric("Filtered Devices", f"{len(devices_subset):,}", eyebrow="Scope")

    with metric_2:

        _render_snapshot_metric(
            "Needs Attention",
            f"{int(issues_mask_local.sum()):,}",
            variant="priority",
            eyebrow="Priority",
        )
    with metric_3:

        _render_snapshot_metric("Live Ping Exceptions", f"{live_ping_exceptions_local:,}", eyebrow="Ping")
    with metric_4:

        _render_snapshot_metric("Open Tickets", f"{int(ticket_state_counts.get('Open', 0)):,}", eyebrow="Queue")

    with metric_5:

        if retention_enabled and "Retention OK" in devices_subset.columns:
            retention_violations = int((~devices_subset["Retention OK"].fillna(False)).sum())

            _render_snapshot_metric("Retention Violations", f"{retention_violations:,}", eyebrow="Storage")

        else:

            _render_snapshot_metric("Flapping Cameras", f"{int((flaps_7d > 0).sum()):,}", eyebrow="7-Day")



    selected_health = None

    selected_location = None



    st.markdown('<div class="ops-snapshot-chart-row-anchor"></div>', unsafe_allow_html=True)

    chart_left, chart_middle, chart_right = st.columns(3, gap="medium")

    with chart_left:

        health_order = ["Offline", "Offline (but still visible)", "Online"]

        health_counts = health_state.value_counts().reindex(health_order, fill_value=0)

        health_display_map = {

            "Offline (but still visible)": "Offline (visible)",

        }

        health_counts_display = health_counts.rename(index=health_display_map)

        render_fixed_ring_chart(

            "Health Mix",

            health_counts_display.rename("Count"),

            center_text=f"{int(health_counts.sum()):,}",

            center_label="Devices",

            empty_message="No health data in current scope.",

            category_colors={

                "Offline": OPS_COLOR_WARN,

                "Offline (visible)": OPS_COLOR_WARN_SOFT,

                "Online": OPS_COLOR_GOOD,

            },

        )

        selected_health = None

    with chart_middle:

        issue_locations = devices_subset_with_ping.loc[issues_mask_local].copy()

        if not issue_locations.empty and "Location" in issue_locations.columns:

            location_counts = (

                issue_locations["Location"]

                .fillna("")

                .astype(str)

                .str.strip()

                .replace("", "Unknown")

                .value_counts()

                .head(10)

            )

            location_palette = [

                "#5B8FF9",

                "#6DC8EC",

                "#9270CA",

                "#F6903D",

                "#F08BB4",

                "#5AD8A6",

                "#C2C8D5",

                "#7C6AF2",

                "#FF9D4D",

                "#53A1A9",

            ]

            location_colors = {

                category: location_palette[idx % len(location_palette)]

                for idx, category in enumerate(location_counts.index.astype(str).tolist())

            }

            render_fixed_ring_chart(

                "Top Locations Needing Attention",

                location_counts.rename("Count"),

                center_text=f"{int(location_counts.sum()):,}",

                center_label="Devices",

                empty_message="No issue locations in current scope.",

                category_colors=location_colors,

            )

            selected_location = None

        else:

            st.info("No issue locations in current scope.")

            selected_location = None

    with chart_right:

        action_required_subset = devices_subset_with_ping.loc[issues_mask_local].copy()

        if action_required_subset.empty:

            st.info("No action-required devices in current scope.")

        else:

            ping_labeled = add_ping_status_for_issues(action_required_subset)

            ping_text = (

                ping_labeled.get("Ping Status", pd.Series([""] * len(ping_labeled), index=ping_labeled.index))

                .fillna("")

                .astype(str)

                .str.lower()

            )

            pingable_mask = ping_text.str.contains("pingable", na=False) & ~ping_text.str.contains("not pingable", na=False)

            not_pingable_mask = ping_text.str.contains("not pingable|ping error|no ip|invalid ip", na=False)

            unknown_mask = ~(pingable_mask | not_pingable_mask)

            ping_counts = pd.Series(

                {

                    "Pingable": int(pingable_mask.sum()),

                    "Do Not Ping": int(not_pingable_mask.sum()),

                    "Pending / Unknown": int(unknown_mask.sum()),

                }

            )

            render_fixed_ring_chart(

                "Ping Status",

                ping_counts,

                center_text=f"{int(len(action_required_subset)):,}",

                center_label="Devices",

                empty_message="No action-required devices in current scope.",

                category_colors={

                    "Pingable": OPS_COLOR_GOOD,

                    "Do Not Ping": OPS_COLOR_WARN_SOFT,

                    "Pending / Unknown": OPS_COLOR_UNKNOWN,

                },

            )



    if selected_health:

        st.session_state["ops_snapshot_selected_health"] = selected_health

    if selected_location:

        st.session_state["ops_snapshot_selected_location"] = selected_location

    selected_health = st.session_state.get("ops_snapshot_selected_health", "")

    selected_location = st.session_state.get("ops_snapshot_selected_location", "")



    if selected_health or selected_location:

        active_parts = []

        if selected_health:

            active_parts.append(f"Health = {selected_health}")

        if selected_location:

            active_parts.append(f"Location = {selected_location}")

        st.caption(

            "Snapshot filter active for All Filtered Cameras: "

            + " | ".join(active_parts)

        )



        action_col, _ = st.columns([0.24, 0.76])

        with action_col:

            if st.button("Clear Chart Selection", key="ops_snapshot_clear_selection", use_container_width=True):

                st.session_state.pop("ops_snapshot_selected_health", None)

                st.session_state.pop("ops_snapshot_selected_location", None)

                st.rerun()


def render_health_dashboard_chrome(active_area: str) -> None:
    # Legacy mobile chrome removed in favor of a cleaner, quieter app shell.
    return


def _health_status_badge_html(value: object) -> str:

    text = str(value or "").strip() or "Unknown"
    lowered = text.lower()
    badge_class = "neutral"
    if "online" in lowered:
        badge_class = "online"
    elif "offline" in lowered and "visible" not in lowered:
        badge_class = "offline"
    elif "visible" in lowered or "warning" in lowered:
        badge_class = "warning"
    return f'<span class="health-table-status {badge_class}">{html_escape(text)}</span>'


def render_mobile_filtered_cameras_table(data_subset: pd.DataFrame) -> None:

    overview_display_order = [
        "Health",
        "Device Name Base",
        "key",
        "IP Address",
        "Location",
        "Ping Status",
        "Ticket ID",
        "Primary Connection",
        "Secondary Connection",
        "Error Flags",
        "Servers",
        "disposition",
        "notes",
    ]
    render_data_editor(
        data_subset,
        "overview",
        preferred_order=overview_display_order,
        default_visible_cols=[
            "Health",
            "Device Name Base",
            "key",
            "IP Address",
            "Location",
            "Ping Status",
            "Ticket ID",
        ],
    )


if selected_workspace == "Health Status" and selected_area == "Overview":

    render_health_dashboard_chrome(selected_area)



preferred_cols = [

    "Health",

    "Device Name Base",

    "key",

    "IP Address",

    "Offline For (hrs)",

    "Ticket ID",

    "Error Flags",

    "Servers",

    "Ping Status",

    "disposition",

    "notes",

    "Location",

    "Ticket Status",

]



AGGRID_HEADER_LABELS = {

    "Device Name Base": "Camera Name",

    "key": "MAC Address",

    "Offline For (hrs)": "Offline Hrs",

    "Ticket Status": "Ticket",

    "Error Flags": "Errors",

    "Primary Connection": "Primary Conn",

    "Secondary Connection": "Secondary Conn",

    "Create TDX": "TDX",

}



# Excel-style width units mapped to Streamlit small/medium/large buckets.

CAMERA_GRID_WIDTHS_ALL = {

    "Health": 14,

    "Device Name Base": 57,

    "key": 18,

    "IP Address": 14,

    "Offline For (hrs)": 16,

    "Ticket ID": 10,

    "Error Flags": 50,

    "Primary Connection": 50,

    "Secondary Connection": 50,

    "Ping Status": 17,

    "Flaps (24h)": 10,

    "Flaps (7d)": 10,

    "Retention (days)": 14,

    "Retention Gap": 14,

    "Servers": 40,

    "disposition": 20,

    "notes": 40,

    "Location": 30,

    "Ticket Status": 12,

}



CAMERA_GRID_WIDTHS_ISSUES = {

    "Health": 14,

    "Device Name Base": 57,

    "key": 18,

    "IP Address": 14,

    "Ping Status": 17,

    "Flaps (24h)": 10,

    "Flaps (7d)": 10,

    "Retention (days)": 14,

    "Retention Gap": 14,

    "Offline For (hrs)": 16,

    "Ticket ID": 10,

    "Create TDX": 10,

    "Error Flags": 50,

    "Primary Connection": 50,

    "Secondary Connection": 50,

    "Servers": 40,

    "disposition": 20,

    "notes": 40,

    "Location": 30,

    "Ticket Status": 12,

}





def save_notes_from_editor(edited_df: pd.DataFrame):

    edited_notes = edited_df[["key", "disposition", "notes"]].copy()

    existing = load_notes(NOTES_PATH)

    combined = pd.concat([existing[~existing["key"].isin(edited_notes["key"])], edited_notes], ignore_index=True)

    save_notes(NOTES_PATH, combined)

    st.success(f"Saved notes to: {NOTES_PATH}")





def save_tickets_from_editor(edited_df: pd.DataFrame):

    existing = load_tickets(TICKETS_PATH)

    keep = existing[~existing["ticket_key"].isin(edited_df["ticket_key"])]

    combined = pd.concat([keep, edited_df], ignore_index=True)

    save_tickets(TICKETS_PATH, combined)

    st.success(f"Saved tickets to: {TICKETS_PATH}")





def render_data_editor(

    data_subset: pd.DataFrame,

    key_suffix: str,

    preferred_order: list[str] | None = None,

    enable_inline_tdx_actions: bool = False,

    default_visible_cols: list[str] | None = None,

    selected_optional_cols_override: list[str] | None = None,

    table_height: int = 550,

):

    order = preferred_order if preferred_order is not None else preferred_cols

    available_cols = [c for c in order if c in data_subset.columns]

    available_cols += [c for c in data_subset.columns if c not in available_cols]



    if data_subset.empty:

        st.info("No cameras match the current filters in this view.")

        return



    default_open_cols = (

        [c for c in default_visible_cols]

        if default_visible_cols is not None

        else [

            "Health",

            "Device Name Base",

            "key",

            "IP Address",

            "Offline For (hrs)",

            "Ticket ID",

            "Error Flags",

        ]

    )

    inline_tdx_col = "Create TDX"

    if enable_inline_tdx_actions:

        data_subset = data_subset.copy()

        data_subset[inline_tdx_col] = False

        if inline_tdx_col not in available_cols:

            available_cols.append(inline_tdx_col)

        if "Error Flags" in default_open_cols:

            default_open_cols.insert(default_open_cols.index("Error Flags"), inline_tdx_col)

        else:

            default_open_cols.append(inline_tdx_col)

    default_open_cols = [c for c in default_open_cols if c in available_cols]

    optional_cols = [c for c in available_cols if c not in default_open_cols]

    if selected_optional_cols_override is not None:

        display_cols = [c for c in selected_optional_cols_override if c in available_cols]
        if not display_cols:
            display_cols = default_open_cols or available_cols
        selected_optional_cols = [c for c in display_cols if c in optional_cols]

    elif key_suffix == "issues":

        st.markdown(
            """
            <style>
            .issues-control-label-spacer {
                font-size: 0.875rem;
                line-height: 1.6;
                min-height: 1.4rem;
                margin: 0 0 0.25rem 0;
                opacity: 0;
                user-select: none;
            }
            div[data-testid="stButton"] > button[kind="secondary"],
            div[data-testid="stButton"] > button[kind="primary"] {
                height: 2.85rem;
                min-height: 2.85rem;
                padding-top: 0;
                padding-bottom: 0;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        controls_col, action_col = st.columns([0.78, 0.22], gap="medium")

        with controls_col:

            selected_optional_cols = st.multiselect(

                "Show Additional Columns",

                options=optional_cols,

                default=[],

                key=f"extra_cols_{key_suffix}",

                help="These columns are hidden by default. Select any to add them to the table.",

            )

        with action_col:

            st.markdown('<div class="issues-control-label-spacer">Action</div>', unsafe_allow_html=True)

            if st.button("Refresh Ping Status", key="refresh_ping_status", use_container_width=True):

                st.session_state.ping_status_by_ip = {}

                st.session_state.ping_pending_ips = []

    else:

        selected_optional_cols = st.multiselect(

            "Show Additional Columns",

            options=optional_cols,

            default=[],

            key=f"extra_cols_{key_suffix}",

            help="These columns are hidden by default. Select any to add them to the table.",

        )

    if selected_optional_cols_override is None:

        display_cols = default_open_cols + [c for c in selected_optional_cols if c in optional_cols]

    if not display_cols:

        display_cols = available_cols



    use_manual_widths = True

    editable_cols = {"disposition", "notes"}

    if enable_inline_tdx_actions:

        editable_cols.add(inline_tdx_col)



    grid_df = data_subset[available_cols].copy()

    display_df = grid_df[display_cols].copy()



    disposition_options = ["", "Investigating", "Vendor", "ITS/Network", "Construction", "Offline/Expected", "Replaced", "Closed"]

    preferred_width_px = {
        "Priority Score": 90,
        "Health": 130,
        "Device Name Base": 250,
        "key": 125,
        "IP Address": 90,
        "Primary Connection": 240,
        "Secondary Connection": 240,
        "Ping Status": 115,
        "Offline For (hrs)": 115,
        "Ticket ID": 65,
        inline_tdx_col: 75,
        "Error Flags": 400,
    }

    max_width_px = {
        "Priority Score": 110,
        "Health": 170,
        "Device Name Base": 320,
        "key": 170,
        "IP Address": 145,
        "Primary Connection": 310,
        "Secondary Connection": 310,
        "Ping Status": 145,
        "Offline For (hrs)": 140,
        "Ticket ID": 95,
        inline_tdx_col: 95,
        "Error Flags": 460,
        "Location": 260,
        "disposition": 185,
        "notes": 420,
        "Servers": 320,
    }



    def editor_width(col_name: str) -> str:

        def px_to_bucket(px: int) -> str:

            if px <= 115:

                return "small"

            if px <= 280:

                return "medium"

            return "large"

        if col_name in preferred_width_px:

            return px_to_bucket(int(preferred_width_px[col_name]))

        if col_name == inline_tdx_col:

            return "small"

        header_text = str(AGGRID_HEADER_LABELS.get(col_name, col_name))

        if col_name not in grid_df.columns:

            sample_len = len(header_text)

        else:

            series = grid_df[col_name]

            if col_name == "Offline For (hrs)":

                formatted_series = pd.to_numeric(series, errors="coerce").map(
                    lambda value: "" if pd.isna(value) else f"{float(value):.1f}"
                )

            else:

                formatted_series = series.fillna("").astype(str)

            non_empty = formatted_series[formatted_series.astype(str).str.strip() != ""]

            sample_len = max(
                len(header_text),
                int(non_empty.astype(str).str.len().max()) if not non_empty.empty else 0,
            )

        if sample_len <= 12:

            return "small"

        if sample_len <= 28:

            return "medium"

        return "large"

    def grid_text_width_px(col_name: str) -> int:

        header_text = str(AGGRID_HEADER_LABELS.get(col_name, col_name))
        if col_name not in grid_df.columns:
            longest_len = len(header_text)
        else:
            series = grid_df[col_name]
            if col_name == "Offline For (hrs)":
                formatted_series = pd.to_numeric(series, errors="coerce").map(
                    lambda value: "" if pd.isna(value) else f"{float(value):.1f}"
                )
            else:
                formatted_series = series.fillna("").astype(str)
            non_empty = formatted_series[formatted_series.astype(str).str.strip() != ""]
            longest_len = max(
                len(header_text),
                int(non_empty.astype(str).str.len().max()) if not non_empty.empty else 0,
            )
        base_width = max(72, int(longest_len * 8.4) + 32)
        target_width = max(base_width, int(preferred_width_px.get(col_name, 0)))
        capped_width = int(min(target_width, max_width_px.get(col_name, target_width)))
        return capped_width



    column_config: dict[str, object] = {}

    for col in display_cols:

        col_key: str = str(col)

        header = str(AGGRID_HEADER_LABELS.get(col_key, col_key))

        if col_key == "disposition":

            if use_manual_widths:

                width = editor_width(col_key)

                column_config[col_key] = st.column_config.SelectboxColumn(

                    header,

                    options=disposition_options,

                    width=width,

                )

            else:

                column_config[col_key] = st.column_config.SelectboxColumn(

                    header,

                    options=disposition_options,

                )

        elif col_key == inline_tdx_col:

            column_config[col_key] = st.column_config.CheckboxColumn(

                header,

                width="small",

            )

        elif col_key == "Offline For (hrs)":

            if use_manual_widths:

                width = editor_width(col_key)

                column_config[col_key] = st.column_config.NumberColumn(

                    header,

                    format="%.1f",

                    width=width,

                )

            else:

                column_config[col_key] = st.column_config.NumberColumn(

                    header,

                    format="%.1f",

                )

        else:

            if use_manual_widths:

                width = editor_width(col_key)

                column_config[col_key] = st.column_config.TextColumn(

                    header,

                    width=width,

                )

            else:

                column_config[col_key] = st.column_config.TextColumn(

                    header,

                )



    if key_suffix == "issues" and all(
        dependency is not None
        for dependency in (AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode)
    ):

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(
            editable=False,
            filter=False,
            sortable=True,
            resizable=True,
            suppressMenu=True,
            wrapHeaderText=True,
            autoHeaderHeight=True,
        )
        gb.configure_grid_options(
            autoSizeStrategy={"type": "fitCellContents"},
            rowHeight=38,
            headerHeight=42,
            suppressMovableColumns=True,
            ensureDomOrder=True,
            stopEditingWhenCellsLoseFocus=True,
            tooltipShowDelay=0,
            tooltipMouseTrack=True,
            enableCellTextSelection=True,
        )

        for col in display_cols:
            col_key = str(col)
            header = str(AGGRID_HEADER_LABELS.get(col_key, col_key))
            col_width = grid_text_width_px(col_key)
            col_kwargs: dict[str, Any] = {
                "header_name": header,
                "editable": col_key in editable_cols,
                "width": col_width,
                "minWidth": max(68, min(col_width, int(preferred_width_px.get(col_key, col_width) or col_width))),
                "maxWidth": max_width_px.get(col_key, max(col_width, int(preferred_width_px.get(col_key, col_width) or col_width))),
                "tooltipField": col_key,
            }

            if col_key in {"Error Flags", "notes"}:
                col_kwargs["wrapText"] = True
                col_kwargs["autoHeight"] = True

            if col_key == "disposition":
                col_kwargs["cellEditor"] = "agSelectCellEditor"
                col_kwargs["cellEditorParams"] = {"values": disposition_options}
            elif col_key == inline_tdx_col:
                col_kwargs["cellRenderer"] = "agCheckboxCellRenderer"
                col_kwargs["cellEditor"] = "agCheckboxCellEditor"
            elif col_key == "Offline For (hrs)":
                col_kwargs["type"] = ["numericColumn"]
                col_kwargs["precision"] = 1

            gb.configure_column(col_key, **col_kwargs)

        grid_response = AgGrid(
            display_df,
            gridOptions=gb.build(),
            height=table_height,
            theme="streamlit",
            key=f"editor_{key_suffix}",
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=False,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            fit_columns_on_grid_load=False,
        )

        edited_display = grid_response.data if hasattr(grid_response, "data") else display_df
    else:

        edited_display = st.data_editor(

            display_df,

            width="stretch",

            height=table_height,

            hide_index=True,

            disabled=[c for c in display_cols if c not in editable_cols],

            column_config=column_config,

            key=f"editor_{key_suffix}",

        )



    edited = grid_df.copy()

    if isinstance(edited_display, pd.DataFrame) and not edited_display.empty:

        for col in display_cols:

            if col in edited_display.columns:

                edited[col] = edited_display[col]



    if enable_inline_tdx_actions and inline_tdx_col in edited.columns and "key" in edited.columns:

        checked_mask = (

            edited[inline_tdx_col]

            .fillna(False)

            .astype(str)

            .str.strip()

            .str.lower()

            .isin(["true", "1", "yes", "y", "t"])

        )

        checked_keys = set(

            edited.loc[checked_mask, "key"].astype(str).tolist()

        )

        state_key = f"inline_tdx_checked_{key_suffix}"

        prev_checked_keys = set(st.session_state.get(state_key, set()))

        newly_checked_keys = checked_keys - prev_checked_keys



        if newly_checked_keys:

            source = data_subset.copy()

            source["key"] = source["key"].astype(str)

            sent_count = 0

            failed_count = 0

            skipped_count = 0

            for cam_key in sorted(newly_checked_keys):

                row_match = source[source["key"] == cam_key]

                if row_match.empty:

                    failed_count += 1

                    continue

                row = row_match.iloc[0]

                if not is_row_eligible_for_manual_tdx(row):

                    skipped_count += 1  # type: ignore[operator]

                    continue

                sent, err = send_manual_tdx_ticket_for_row(

                    row=row,

                    smtp_host=smtp_host,

                    smtp_port=smtp_port,

                    smtp_username=smtp_username,

                    smtp_password=smtp_password,

                    smtp_from_email=smtp_from_email,

                    tdx_email_to=tdx_email_to,

                )

                if sent:

                    sent_count += 1  # type: ignore[operator]

                else:

                    failed_count += 1  # type: ignore[operator]

                    camera_name = row_first_non_empty(row, ["Device Name Base", "Device Name", "key"]) or cam_key

                    st.toast(f"TDX email failed for {camera_name}: {err}", icon="\u26A0\uFE0F")



            if sent_count:

                st.toast(f"Sent {sent_count} TDX ticket email(s).")

            if skipped_count:

                st.toast(f"Skipped {skipped_count} row(s): only offline + not-pingable rows are allowed.")



        st.session_state[state_key] = checked_keys



    if st.button("Save Notes", key=f"save_{key_suffix}"):

        notes_source = edited.copy()

        for col in ["key", "disposition", "notes"]:

            if col not in notes_source.columns:

                notes_source[col] = data_subset[col] if col in data_subset.columns else ""

        save_notes_from_editor(notes_source)





def render_action_required_ticket_queue(ticket_subset: pd.DataFrame):

    st.markdown("###### Help Ticket Queue")

    if ticket_subset.empty:

        st.info("No pending help tickets for the current Action Required filters.")

        return



    if "selected_tickets" not in st.session_state:

        st.session_state.selected_tickets = set()



    all_keys = set(ticket_subset["ticket_key"].astype(str).tolist())

    st.session_state.selected_tickets.intersection_update(all_keys)



    queue_df = ticket_subset[["ticket_key", "device_name", "location", "offline_hours_at_creation", "health_state"]].copy()

    queue_df["ticket_key"] = queue_df["ticket_key"].astype(str)

    queue_df["Select"] = queue_df["ticket_key"].isin(st.session_state.selected_tickets)

    queue_df = queue_df[["Select", "device_name", "location", "offline_hours_at_creation", "health_state", "ticket_key"]]



    queue_edited = st.data_editor(

        queue_df,

        width="stretch",

        height=260,

        hide_index=True,

        disabled=["device_name", "location", "offline_hours_at_creation", "health_state", "ticket_key"],

        column_config={

            "Select": st.column_config.CheckboxColumn("Select", width="small"),

            "device_name": st.column_config.TextColumn("Camera", width="medium"),

            "location": st.column_config.TextColumn("Location", width="medium"),

            "offline_hours_at_creation": st.column_config.NumberColumn("Offline Hrs", format="%.1f", width="small"),

            "health_state": st.column_config.TextColumn("Health", width="small"),

            "ticket_key": st.column_config.TextColumn("Ticket Key", width="small"),

        },

        key="action_required_ticket_queue",

    )



    selected_keys = set(queue_edited.loc[queue_edited["Select"], "ticket_key"].astype(str).tolist())

    st.session_state.selected_tickets = selected_keys

    selected_count = len(selected_keys)



    st.caption("Select one or more pending items below, then use the queue actions to create emails or acknowledge them.")

    c1, c2, c3 = st.columns(3)

    with c1:

        all_selected = len(all_keys) > 0 and all_keys.issubset(selected_keys)

        if st.button("Deselect All" if all_selected else "Select All", key="tab2_select_all", use_container_width=True):

            st.session_state.selected_tickets = set() if all_selected else set(all_keys)

            st.rerun()



    with c2:

        if st.button(f"Send Help Ticket Email ({selected_count})", key="tab2_create_help_ticket", use_container_width=True, disabled=selected_count == 0):

            selected_rows = tickets_df[

                tickets_df["ticket_key"].astype(str).isin(selected_keys)

                & tickets_df["ticket_state"].eq("Pending Send")

            ]

            sent_count = 0

            failed_count = 0



            for idx, row in selected_rows.iterrows():

                dev_match = df_devices[df_devices["key"] == row["key"]]

                if dev_match.empty:

                    failed_count += 1

                    tickets_df.loc[idx, "last_error"] = "Could not find full device info for email."

                    continue



                dev = dev_match.iloc[0]

                body = build_ticket_email_body(dev, row["offline_hours_at_creation"])

                sent, err = send_ticket_email(

                    smtp_host, smtp_port, smtp_username, smtp_password,

                    smtp_from_email, tdx_email_to, row["email_subject"], body,

                )

                if sent:

                    sent_count += 1  # type: ignore[operator]

                    t_key = str(row["ticket_key"])

                    tickets_df.loc[idx, "ticket_state"] = "Open"

                    tickets_df.loc[idx, "email_sent_at"] = format_timestamp(utc_now_timestamp())

                    tickets_df.loc[idx, "last_error"] = ""

                    st.session_state.selected_tickets.discard(t_key)

                else:

                    failed_count += 1

                    tickets_df.loc[idx, "last_error"] = str(err)



            save_tickets(TICKETS_PATH, tickets_df)

            if sent_count:

                st.toast(f"Created {sent_count} help ticket email(s).")

            if failed_count:

                st.toast(f"{failed_count} ticket email(s) failed. Check Last Email Error in Open Tickets.")

            st.rerun()



    with c3:

        if st.button(f"Acknowledge Selected ({selected_count})", key="tab2_ack_selected", use_container_width=True, disabled=selected_count == 0):

            ack_mask = (

                tickets_df["ticket_key"].astype(str).isin(selected_keys)

                & tickets_df["ticket_state"].eq("Pending Send")

            )

            tickets_df.loc[ack_mask, "ticket_state"] = "Acknowledged"

            save_tickets(TICKETS_PATH, tickets_df)

            st.session_state.selected_tickets.clear()

            st.rerun()

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

render_html(
    """
    <style>
    .ops-command-shell {
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        margin: 0.35rem 0 0.4rem 0;
        padding: 1rem 1.05rem;
        border-radius: 18px;
        border: 1px solid rgba(101, 122, 132, 0.14);
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(237, 242, 245, 0.96)),
            radial-gradient(circle at top right, rgba(53, 126, 155, 0.12), transparent 36%);
        box-shadow: 0 12px 28px rgba(53, 126, 155, 0.08);
    }
    .ops-command-kicker {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #657A84;
        margin-bottom: 0.25rem;
        font-weight: 700;
    }
    .ops-command-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #40484D;
        line-height: 1.1;
    }
    .ops-command-subtitle {
        color: #657A84;
        font-size: 0.93rem;
        line-height: 1.45;
        max-width: 58rem;
        margin-top: 0.28rem;
    }
    .ops-command-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
        gap: 0.7rem;
    }
    .ops-command-card {
        background: linear-gradient(180deg, rgba(252, 253, 253, 0.98), rgba(237, 242, 245, 0.98));
        border: 1px solid rgba(101, 122, 132, 0.12);
        border-radius: 14px;
        padding: 0.8rem 0.85rem 0.72rem 0.85rem;
    }
    .ops-command-label {
        color: #657A84;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        margin-bottom: 0.24rem;
    }
    .ops-command-value {
        color: #40484D;
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.05;
    }
    .ops-scope-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
    }
    .ops-scope-chip {
        display: inline-flex;
        align-items: center;
        min-height: 2rem;
        padding: 0.38rem 0.68rem;
        border-radius: 999px;
        border: 1px solid rgba(101, 122, 132, 0.16);
        background: rgba(248, 250, 251, 0.98);
        color: #5D6F78;
        font-size: 0.78rem;
        font-weight: 600;
    }
    </style>
    """
)




def render_tickets_editor(ticket_subset: pd.DataFrame):

    st.caption("Work the active ticket queue here. Update status, TDX IDs, and resolution details, then save the queue when you are done.")

    if ticket_subset.empty:

        st.markdown(
            """
            <div style="
                max-width: 36rem;
                padding: 0.85rem 1rem;
                border-radius: 14px;
                border: 1px solid rgba(101, 122, 132, 0.16);
                background: linear-gradient(180deg, rgba(248,250,251,0.96), rgba(237,242,245,0.96));
                color: #5D6F78;
                box-shadow: 0 8px 18px rgba(53, 126, 155, 0.04);
            ">
                No queued or open tickets right now.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return



    cols = [

        "ticket_key", "ticket_state", "ticket_id", "device_name", "location",

        "offline_since", "offline_hours_at_creation", "email_to", "created_at",

        "email_sent_at", "resolution", "resolution_notes", "last_error",

    ]

    ticket_view = ticket_subset[cols].copy()
    extra_ticket_cols = [
        c for c in ["offline_since", "email_to", "created_at", "email_sent_at", "last_error"] if c in ticket_view.columns
    ]
    selected_extra_cols = st.multiselect(
        "Show Additional Columns",
        options=extra_ticket_cols,
        default=[],
        key="ticket_editor_extra_cols",
        help="Show less-used ticket fields without crowding the default ticket queue view.",
    )
    default_ticket_cols = [
        c for c in [
            "ticket_state", "ticket_id", "device_name", "location", "offline_hours_at_creation", "resolution", "resolution_notes"
        ] if c in ticket_view.columns
    ]
    display_ticket_cols = default_ticket_cols + [c for c in selected_extra_cols if c not in default_ticket_cols]

    st.caption("Default queue view stays focused on the fields you are most likely to update during active ticket work.")

    edited = st.data_editor(

        ticket_view[display_ticket_cols],

        width="stretch",

        height=410,

        hide_index=True,

        disabled=[c for c in display_ticket_cols if c not in ["ticket_state", "ticket_id", "resolution", "resolution_notes"]],

        column_config={

            "ticket_state": st.column_config.SelectboxColumn("State", options=["Pending Send", "Open", "Acknowledged", "Suppressed", "Resolved"]),

            "ticket_id": st.column_config.TextColumn("TDX Ticket", width="medium"),

            "device_name": st.column_config.TextColumn("Camera", width="large"),

            "location": st.column_config.TextColumn("Location", width="large"),

            "offline_hours_at_creation": st.column_config.NumberColumn("Offline Hrs", format="%.1f", width="small"),

            "resolution": st.column_config.SelectboxColumn(

                "Resolution",

                options=["", "Investigating", "Resolved", "Replaced", "Removed", "False Alarm"],

                width="medium",

            ),

            "resolution_notes": st.column_config.TextColumn("Resolution Notes", width="large"),

            "last_error": st.column_config.TextColumn("Last Email Error", width="large"),

        },

        key="ticket_editor",

    )

    ticket_save_df = ticket_view.copy()
    for col in edited.columns:
        ticket_save_df[col] = edited[col]

    save_col, helper_col = st.columns([0.24, 0.76])
    with save_col:
        if st.button("Save Tickets", key="save_tickets", use_container_width=True):

            save_tickets_from_editor(ticket_save_df)
    with helper_col:
        st.caption("Saving writes the current queue edits back to the tracked tickets file.")



def render_retention_tab(retention_subset: pd.DataFrame):

    render_health_section_intro(
        "Retention",
        f"Review cameras currently below the {RETENTION_POLICY_DAYS}-day retention target within the active filter scope.",
    )

    if retention_subset.empty:

        st.info("No retention violations in the current filtered scope. That means every visible camera is at or above the current retention threshold.")

        return



    preferred_cols_retention = [

        "Retention Gap",

        "Retention (days)",

        "Retention OK",

        "Health",

        "Device Name Base",

        "key",

        "IP Address",

        "Location",

        "Ticket Status",

        "Ticket ID",

        "Servers",

    ]

    cols = [c for c in preferred_cols_retention if c in retention_subset.columns]

    cols += [c for c in retention_subset.columns if c not in cols]

    display_df = retention_subset[cols].copy()

    render_data_editor(
        display_df,
        "retention",
        preferred_order=preferred_cols_retention,
        default_visible_cols=[
            "Retention Gap",
            "Retention (days)",
            "Health",
            "Device Name Base",
            "key",
            "Location",
            "Ticket ID",
        ],
        table_height=420,
    )





def render_trends_tab(devices_subset: pd.DataFrame, transitions_subset: pd.DataFrame, observed_at_ts: pd.Timestamp):

    render_health_section_intro(
        "Connectivity Trends",
        "Review historical uptime, downtime, and volatility within the current camera scope so you can spot persistent operational risk.",
    )

    if devices_subset.empty:

        st.info("No cameras match the current filters in this view. Broaden the filters to generate trend charts.")

        return



    lookback_days = st.slider(

        "Lookback Window (days)",

        min_value=7,

        max_value=90,

        value=30,

        step=1,

        key="trends_lookback_days",

        help="Daily/weekly uptime and downtime percentages are computed for this rolling period.",

    )

    daily_trends_df, weekly_trends_df, camera_uptime_df, trend_summary = build_connectivity_trend_tables(

        devices_df=devices_subset,

        transitions_df=transitions_subset,

        observed_at=observed_at_ts,

        lookback_days=int(lookback_days),

    )

    if daily_trends_df.empty:

        st.info("No trend data is available yet for the selected camera scope. Keep collecting state transitions and try again later.")

        return



    st.caption("Window summary")
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    with metric_1:

        st.metric("Uptime % (Window)", f"{float(trend_summary['window_uptime_pct']):.2f}%")

    with metric_2:

        st.metric("Downtime % (Window)", f"{float(trend_summary['window_downtime_pct']):.2f}%")

    with metric_3:

        st.metric("Uptime % (Last 7d)", f"{float(trend_summary['last_7d_uptime_pct']):.2f}%")

    with metric_4:

        st.metric("State Changes", f"{int(trend_summary['window_state_changes']):,}")



    assumed_static_devices = int(trend_summary.get("assumed_static_devices", 0))

    tracked_devices = int(trend_summary.get("tracked_devices", 0))

    if assumed_static_devices:

        st.caption(

            f"{assumed_static_devices:,}/{tracked_devices:,} cameras had no state changes in this window; "

            "their current state is assumed to have persisted throughout the window."

        )



    granularity = st.radio(

        "Trend Granularity",

        options=["Daily", "Weekly"],

        horizontal=True,

        key="connectivity_trend_granularity",

    )

    trend_df = daily_trends_df if granularity == "Daily" else weekly_trends_df

    if trend_df.empty:

        st.info("No trend points available for the selected granularity.")

        return



    chart_col_left, chart_col_right = st.columns(2, gap="medium")

    uptime_chart_df = trend_df.set_index("Period")[["Uptime %", "Downtime %"]]
    with chart_col_left:
        st.caption("Trend view")
        st.line_chart(uptime_chart_df, height=230)

    changes_chart_df = trend_df.set_index("Period")[["State Changes"]]
    with chart_col_right:
        st.caption("Change activity")
        st.bar_chart(changes_chart_df, height=230)



    st.caption("Trend data table")

    if granularity == "Daily":

        table_cols = ["Period", "Online Hours", "Offline Hours", "Uptime %", "Downtime %", "State Changes"]

    else:

        table_cols = ["Period", "Online Hours", "Offline Hours", "Uptime %", "Downtime %", "State Changes"]

    render_data_editor(
        trend_df[table_cols].copy(),
        "connectivity_trends",
        preferred_order=table_cols,
        default_visible_cols=table_cols,
        table_height=360,
    )

    st.caption("Per-camera uptime leaderboard (within selected lookback window)")

    leaderboard_size = st.slider(

        "Leaderboard Size",

        min_value=5,

        max_value=50,

        value=20,

        step=5,

        key="connectivity_leaderboard_size",

    )

    leaderboard_cols = [

        "Device Name Base",

        "key",

        "Location",

        "Current Health State",

        "Uptime %",

        "Downtime %",

        "Online Hours",

        "Offline Hours",

        "State Changes",

    ]

    best_uptime_df = camera_uptime_df.sort_values(

        by=["Uptime %", "State Changes", "Device Name Base"],

        ascending=[False, True, True],

        na_position="last",

    ).head(int(leaderboard_size))

    worst_uptime_df = camera_uptime_df.sort_values(

        by=["Uptime %", "State Changes", "Device Name Base"],

        ascending=[True, False, True],

        na_position="last",

    ).head(int(leaderboard_size))



    leader_col, lagger_col = st.columns(2, gap="small")

    with leader_col:

        st.markdown("###### Top Uptime")

        render_data_editor(
            best_uptime_df[leaderboard_cols].copy(),
            "top_uptime_leaderboard",
            preferred_order=leaderboard_cols,
            default_visible_cols=leaderboard_cols,
            table_height=320,
        )

    with lagger_col:

        st.markdown("###### Lowest Uptime")

        render_data_editor(
            worst_uptime_df[leaderboard_cols].copy(),
            "lowest_uptime_leaderboard",
            preferred_order=leaderboard_cols,
            default_visible_cols=leaderboard_cols,
            table_height=320,
        )





def render_overview_section() -> None:
    render_overview_theme()

    overview_scope_key = st.session_state.get("health_scope_mode", "unique")
    scope_labels = {
        "unique": f"Devices ({df_devices['physical_key'].nunique():,})",
        "export": f"All Views ({len(df_views):,})",
        "avigilon": f"Avigilon ({len(df_devices[df_devices['Brand'] == 'Avigilon']):,})",
        "axis": f"Axis ({len(df_devices[df_devices['Brand'] == 'Axis']):,})",
        "other": f"Other ({len(df_devices[df_devices['Brand'].isin(['Other', 'Unknown'])]):,})",
    }

    overview_issue_mask = compute_action_required_mask(filtered_devices, use_ping_results=False)
    overview_issue_subset = filtered_devices.loc[overview_issue_mask].copy()
    scoped_keys = set(filtered_devices["key"].astype(str).tolist()) if "key" in filtered_devices.columns else set()
    scoped_open_tickets = tickets_df[
        tickets_df["ticket_state"].eq("Open")
        & tickets_df["key"].astype(str).isin(scoped_keys)
    ].copy() if {"ticket_state", "key"}.issubset(tickets_df.columns) else pd.DataFrame()
    search_scope_label = "Views" if st.session_state.get("view_mode", "devices") == "views" else "Devices"

    render_overview_header(
        scope_label=scope_labels.get(overview_scope_key, scope_labels["unique"]),
        device_count=len(filtered_devices),
        issue_count=len(overview_issue_subset),
        view_mode=search_scope_label,
    )

    retention_metric_note = "Retention OK not loaded"
    retention_metric_value = "N/A"
    retention_violations = 0
    if retention_available and "Retention OK" in filtered_devices.columns:
        retention_violations = int((~filtered_devices["Retention OK"].fillna(False)).sum())
        retention_metric_value = f"{retention_violations:,}"
        retention_metric_note = "Retention exceptions in scope"
    elif "Flaps (7d)" in filtered_devices.columns:
        flapping_count = int((pd.to_numeric(filtered_devices["Flaps (7d)"], errors="coerce").fillna(0) > 0).sum())
        retention_metric_value = f"{flapping_count:,}"
        retention_metric_note = "Devices with 7-day flaps"

    ping_exception_count = 0
    if "Ping Status" in overview_issue_subset.columns:
        issue_ping = overview_issue_subset["Ping Status"].fillna("").astype(str).str.lower()
        ping_exception_count = int(issue_ping.str.contains("not pingable|ping error|no ip|invalid ip", na=False).sum())

    render_overview_metric_cards(
        [
            {
                "label": "Devices In Scope",
                "value": f"{len(filtered_devices):,}",
                "note": "Current filtered device set",
                "href": "#inventory-controls-anchor",
                "status_label": "Live scope",
                "status_tone": "live",
                "trend": (
                    f"{(len(overview_issue_subset) / len(filtered_devices)):.1%} flagged"
                    if len(filtered_devices)
                    else "0% flagged"
                ),
                "trend_tone": "neutral",
            },
            {
                "label": "Needs Attention",
                "value": f"{len(overview_issue_subset):,}",
                "note": "Offline, visible-offline, or error-driven",
                "priority": True,
                "href": "?overview_nav=action_queue",
                "status_label": "Needs review",
                "status_tone": "attention",
                "trend": (
                    f"{(len(overview_issue_subset) / len(filtered_devices)):.1%} of scope"
                    if len(filtered_devices)
                    else "0% of scope"
                ),
                "trend_tone": "attention",
            },
            {
                "label": "Open Tickets",
                "value": f"{len(scoped_open_tickets):,}",
                "note": f"{ping_exception_count:,} hard ping exceptions",
                "href": "?overview_nav=open_tickets",
                "status_label": "Ticket queue",
                "status_tone": "neutral",
                "trend": (
                    f"{(len(scoped_open_tickets) / max(len(filtered_devices), 1)):.1%} of scope"
                    if len(scoped_open_tickets)
                    else "0 active"
                ),
                "trend_tone": "neutral",
            },
            {
                "label": "Retention / Stability",
                "value": retention_metric_value,
                "note": retention_metric_note,
                "href": "?overview_nav=retention",
                "status_label": "Stable signal" if retention_metric_value in {"N/A", "0"} else "Watchlist",
                "status_tone": "live" if retention_metric_value in {"N/A", "0"} else "attention",
                "trend": (
                    f"{(retention_violations / len(filtered_devices)):.1%} impacted"
                    if retention_available and "Retention OK" in filtered_devices.columns and len(filtered_devices)
                    else ""
                ),
                "trend_tone": "attention" if retention_metric_value not in {"N/A", "0"} else "live",
            },
        ]
    )

    overview_location_palette = [
        "#357E9B",
        "#5E779E",
        "#657A84",
        "#4D92AE",
        "#7B90B0",
        "#8E9DA5",
        "#AFC9D6",
        "#B8C2DE",
    ]
    health_color_map = {
        "Online": "#357E9B",
        "Offline": "#C85A4B",
        "Offline (visible)": "#5E779E",
        "Unknown": "#AAB5BC",
    }
    ping_color_map = {
        "Pingable": "#357E9B",
        "Do Not Ping": "#C85A4B",
        "Pending / Unknown": "#AAB5BC",
    }

    health_col_name = "Health State" if "Health State" in filtered_devices.columns else ("Health" if "Health" in filtered_devices.columns else None)
    health_counts = pd.Series(dtype="int64")
    if health_col_name:
        health_counts = (
            filtered_devices[health_col_name]
            .fillna("Unknown")
            .astype(str)
            .str.replace(r"<[^>]+>", "", regex=True)
            .replace({"Offline (but still visible)": "Offline (visible)"})
            .replace({"": "Unknown"})
            .value_counts()
            .reindex(["Offline", "Offline (visible)", "Online", "Unknown"], fill_value=0)
        )

    location_counts = pd.Series(dtype="int64")
    if "Location" in overview_issue_subset.columns:
        location_counts = (
            overview_issue_subset["Location"]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
            .value_counts()
            .head(8)
        )

    ping_counts = pd.Series(dtype="int64")
    if "Ping Status" in overview_issue_subset.columns:
        ping_text = overview_issue_subset["Ping Status"].fillna("").astype(str).str.lower()
        pingable_mask = ping_text.str.contains("pingable", na=False) & ~ping_text.str.contains("not pingable", na=False)
        not_pingable_mask = ping_text.str.contains("not pingable|ping error|no ip|invalid ip", na=False)
        pending_mask = ~(pingable_mask | not_pingable_mask)
        ping_counts = pd.Series(
            {
                "Pingable": int(pingable_mask.sum()),
                "Do Not Ping": int(not_pingable_mask.sum()),
                "Pending / Unknown": int(pending_mask.sum()),
            }
        )

    render_overview_section_kicker("Snapshot Charts")
    chart_left, chart_middle, chart_right = st.columns(3, gap="medium")
    with chart_left:
        render_overview_chart_card(
            title="Health Mix",
            subtitle="Current state distribution for the filtered device set.",
            data=health_counts,
            color_map=health_color_map,
            empty_message="No health data in the current scope.",
        )
    with chart_middle:
        render_overview_chart_card(
            title="Top Attention Locations",
            subtitle="Where the current problem devices are clustering.",
            data=location_counts,
            color_map={label: overview_location_palette[index % len(overview_location_palette)] for index, label in enumerate(location_counts.index.astype(str).tolist())},
            empty_message="No issue locations in the current scope.",
            shade_by_value=True,
        )
    with chart_right:
        render_overview_chart_card(
            title="Ping Status",
            subtitle="Live ping posture for the devices that need attention.",
            data=ping_counts,
            color_map=ping_color_map,
            empty_message="No ping results are available in the current scope.",
            chart_kind="donut",
        )

    render_overview_section_kicker("Inventory Controls")
    render_html('<div id="inventory-controls-anchor"></div><div class="overview-shortcuts-row"></div>')

    def handle_scope_click(s_key):
        st.session_state["health_scope_mode"] = s_key
        on_metric_click(s_key)

    scope_cols = st.columns(5, gap="small")
    for scope_col, scope_key in zip(scope_cols, ["unique", "export", "avigilon", "axis", "other"]):
        with scope_col:
            is_active = st.session_state.get("health_scope_mode", "unique") == scope_key
            st.button(
                scope_labels[scope_key],
                key=f"overview_scope_tab_{scope_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=handle_scope_click,
                args=(scope_key,)
            )

    controls_left, controls_right = st.columns([0.82, 0.18], gap="small")
    with controls_left:
        search_term = st.text_input(
            "Search Inventory",
            key="overview_camera_keyword_search",
            placeholder="Search by camera name, MAC Address, location, IP, ticket, server, or any visible field...",
            label_visibility="collapsed",
        ).strip()

    overview_default_cols = [
        c for c in [
            "Health",
            "Device Name Base",
            "key",
            "IP Address",
            "Location",
            "Primary Connection",
            "Secondary Connection",
        ] if c in all_df.columns
    ]
    overview_display_order = [
        "Health",
        "Device Name Base",
        "key",
        "IP Address",
        "Location",
        "Ping Status",
        "Ticket ID",
        "Primary Connection",
        "Secondary Connection",
        "Error Flags",
        "Servers",
        "Flaps (24h)",
        "Flaps (7d)",
        "Retention (days)",
        "Retention Gap",
        "Retention OK",
        "disposition",
        "notes",
    ]
    overview_all_cols = [c for c in overview_display_order if c in all_df.columns]
    overview_all_cols += [c for c in all_df.columns if c not in overview_all_cols]

    with controls_right:
        with st.popover("Columns", use_container_width=True):
            selected_extra_cols: list[str] = []
            for col_name in overview_all_cols:
                visible_label = AGGRID_HEADER_LABELS.get(col_name, col_name)
                checked = st.checkbox(
                    visible_label,
                    key=f"overview_col_toggle_{col_name}",
                    value=(col_name in overview_default_cols),
                )
                if checked:
                    selected_extra_cols.append(col_name)

    filtered_table_df = all_df.copy()
    if search_term:
        search_mask = (
            all_df.fillna("")
            .astype(str)
            .apply(lambda row: row.str.contains(search_term, case=False, regex=False).any(), axis=1)
        )
        filtered_table_df = all_df.loc[search_mask].copy()

    overview_visible_cols = [c for c in selected_extra_cols if c in filtered_table_df.columns]
    if not overview_visible_cols:
        overview_visible_cols = [c for c in overview_default_cols if c in filtered_table_df.columns]
    ordered_visible_cols = [c for c in overview_all_cols if c in overview_visible_cols]
    overview_table_df = filtered_table_df[ordered_visible_cols].copy()

    overview_column_config = {
        "Health": st.column_config.TextColumn("Health", width="medium"),
        "Device Name Base": st.column_config.TextColumn("Camera Name", width="large"),
        "key": st.column_config.TextColumn("MAC Address", width="medium"),
        "IP Address": st.column_config.TextColumn("IP Address", width="medium"),
        "Location": st.column_config.TextColumn("Location", width="large"),
        "Ping Status": st.column_config.TextColumn("Ping Status", width="medium"),
        "Ticket ID": st.column_config.TextColumn("Ticket ID", width="medium"),
        "Primary Connection": st.column_config.TextColumn("Primary Connection", width="large"),
        "Secondary Connection": st.column_config.TextColumn("Secondary Connection", width="large"),
        "Error Flags": st.column_config.TextColumn("Errors", width="large"),
        "Servers": st.column_config.TextColumn("Servers", width="large"),
        "Flaps (24h)": st.column_config.NumberColumn("Flaps (24h)", width="small"),
        "Flaps (7d)": st.column_config.NumberColumn("Flaps (7d)", width="small"),
        "Retention (days)": st.column_config.NumberColumn("Retention (days)", width="small"),
        "Retention Gap": st.column_config.NumberColumn("Retention Gap", width="small"),
        "Retention OK": st.column_config.CheckboxColumn("Retention OK", width="small"),
        "disposition": st.column_config.TextColumn("Disposition", width="medium"),
        "notes": st.column_config.TextColumn("Notes", width="large"),
    }

    table_chip = f"{len(filtered_table_df):,} matched '{search_term}'" if search_term else "All scoped rows"
    render_overview_table_header(len(filtered_table_df), table_chip)
    if (
        not overview_table_df.empty
        and all(
            dependency is not None
            for dependency in (AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode)
        )
    ):
        overview_width_px = {
            "Health": 170,
            "Device Name Base": 250,
            "key": 165,
            "IP Address": 135,
            "Location": 240,
            "Ping Status": 170,
            "Ticket ID": 110,
            "Primary Connection": 250,
            "Secondary Connection": 250,
            "Error Flags": 260,
            "Servers": 220,
            "Flaps (24h)": 110,
            "Flaps (7d)": 110,
            "Retention (days)": 130,
            "Retention Gap": 120,
            "Retention OK": 120,
            "disposition": 150,
            "notes": 260,
        }
        gb = GridOptionsBuilder.from_dataframe(overview_table_df)
        gb.configure_default_column(
            editable=False,
            filter=False,
            sortable=True,
            resizable=True,
            suppressMenu=True,
            wrapHeaderText=True,
            autoHeaderHeight=True,
        )
        gb.configure_grid_options(
            rowHeight=34,
            headerHeight=44,
            suppressMovableColumns=True,
            ensureDomOrder=True,
            tooltipShowDelay=0,
            tooltipMouseTrack=True,
            enableCellTextSelection=True,
        )
        for col in overview_table_df.columns:
            header = str(AGGRID_HEADER_LABELS.get(col, col))
            gb.configure_column(
                str(col),
                header_name=header,
                width=int(overview_width_px.get(str(col), 150)),
                minWidth=90,
                tooltipField=str(col),
            )
        overview_grid_header_top = "#657A84"
        overview_grid_header_bottom = "#357E9B"
        overview_grid_border = "rgba(101, 122, 132, 0.18)"
        overview_grid_row = "#FBFCFC"
        overview_grid_row_even = "#F3F6F8"
        overview_grid_row_hover = "#E8F1F5"
        overview_grid_text = "#40484D"
        AgGrid(
            overview_table_df,
            gridOptions=gb.build(),
            height=520,
            theme="streamlit",
            key="overview_inventory_grid",
            data_return_mode=DataReturnMode.AS_INPUT,
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=False,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            fit_columns_on_grid_load=False,
            custom_css={
                ".ag-root-wrapper": {
                    "border": f"1px solid {overview_grid_border}",
                    "border-radius": "18px",
                    "overflow": "hidden",
                    "box-shadow": "0 14px 28px rgba(15, 23, 42, 0.08)",
                },
                ".ag-header": {
                    "background": f"linear-gradient(180deg, {overview_grid_header_top}, {overview_grid_header_bottom})",
                    "border-bottom": "1px solid rgba(255, 255, 255, 0.10)",
                },
                ".ag-header-cell": {
                    "background": f"linear-gradient(180deg, {overview_grid_header_top}, {overview_grid_header_bottom})",
                    "border-right": "1px solid rgba(255, 255, 255, 0.10)",
                },
                ".ag-header-cell-text": {
                    "color": "#f8fafc",
                    "font-weight": "700",
                    "font-size": "15px",
                },
                ".ag-header-icon": {
                    "color": "#f8fafc",
                },
                ".ag-row": {
                    "background-color": overview_grid_row,
                    "color": overview_grid_text,
                    "border-bottom": f"1px solid {overview_grid_border}",
                },
                ".ag-cell": {
                    "line-height": "32px",
                    "font-size": "13px",
                },
                ".ag-row-even": {
                    "background-color": overview_grid_row_even,
                },
                ".ag-row-hover": {
                    "background-color": f"{overview_grid_row_hover} !important",
                },
            },
        )
    else:
        st.dataframe(
            overview_table_df,
            width="stretch",
            height=520,
            hide_index=True,
            column_config={k: v for k, v in overview_column_config.items() if k in overview_table_df.columns},
        )



@st.fragment(run_every=1.0)

def render_action_required_tab():

    render_health_section_intro(
        "Action Queue",
        "Focus on the cameras most likely to need action now: offline devices, error-heavy rows, and cameras with unresolved visibility or ping concerns.",
    )

    st.caption("Prioritized by score: strict offline, not visible, hard error flags, or offline-visible devices that are not confirmed pingable.")

    initialize_ping_queue(issues_df)

    process_ping_batch(batch_size=2)

    issues_with_ping = add_ping_status_for_issues(issues_df)

    issues_with_ping = apply_confirmed_healthy_override(issues_with_ping)

    issues_with_ping = annotate_action_required_ping_status(issues_with_ping)

    issues_with_ping = apply_action_required_health_badge_rules(issues_with_ping)

    issues_with_ping = compute_priority_table(issues_with_ping)

    preview_df = issues_with_ping.copy()
    if "Priority Score" in preview_df.columns:
        preview_df["Priority Score"] = pd.to_numeric(preview_df["Priority Score"], errors="coerce").fillna(0)
        preview_df = preview_df.sort_values(["Priority Score", "Device Name Base"], ascending=[False, True])
    preview_rows = []
    for _, row in preview_df.head(6).iterrows():
        score = float(pd.to_numeric(pd.Series([row.get("Priority Score", 0)]), errors="coerce").fillna(0).iloc[0])
        if score >= 80:
            severity_label = "Critical"
            severity_bg = "rgba(225, 29, 72, 0.10)"
            severity_fg = "#BE123C"
            action_label = "Triage"
        elif score >= 45:
            severity_label = "Warning"
            severity_bg = "rgba(217, 119, 6, 0.12)"
            severity_fg = "#B45309"
            action_label = "Monitor"
        else:
            severity_label = "Routine"
            severity_bg = "rgba(13, 148, 136, 0.10)"
            severity_fg = "#0F766E"
            action_label = "Schedule"
        issue_name = html_escape(str(row.get("Device Name Base") or row.get("key") or "Unknown item"))
        issue_reason = html_escape(str(row.get("Priority Reason", "Needs review")))
        issue_eta = html_escape(str(row.get("Offline For (hrs)", row.get("Ping Status", "")) or "Review now"))
        preview_rows.append(
            f"""
            <tr>
                <td style="padding:0.9rem 0.75rem;border-top:1px solid rgba(148,163,184,0.16);color:#1E293B;font-weight:600;">{issue_name}<div style="color:#64748B;font-size:0.78rem;font-weight:500;margin-top:0.16rem;">{issue_reason}</div></td>
                <td style="padding:0.9rem 0.75rem;border-top:1px solid rgba(148,163,184,0.16);"><span style="display:inline-flex;padding:0.24rem 0.56rem;border-radius:999px;background:{severity_bg};color:{severity_fg};font-size:0.75rem;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;">{severity_label}</span></td>
                <td style="padding:0.9rem 0.75rem;border-top:1px solid rgba(148,163,184,0.16);color:#475569;">{issue_eta}</td>
                <td style="padding:0.9rem 0.75rem;border-top:1px solid rgba(148,163,184,0.16);color:#0F172A;font-weight:700;">{action_label}</td>
            </tr>
            """
        )
    if preview_rows:
        render_html(
            """
            <div style="margin:0.65rem 0 1rem 0;padding:1.05rem 1.08rem;border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(248,250,252,0.96));box-shadow:0 10px 24px rgba(15,23,42,0.06);">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:0.75rem;margin-bottom:0.75rem;">
                    <div>
                        <div style="color:#475569;font-size:0.74rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">Action Queue &amp; System Events</div>
                        <div style="color:#1E293B;font-size:1rem;font-weight:750;letter-spacing:-0.02em;margin-top:0.2rem;">Operational triage preview</div>
                    </div>
                </div>
                <table style="width:100%;border-collapse:collapse;">
                    <thead>
                        <tr>
                            <th style="text-align:left;padding:0 0.75rem 0.5rem 0.75rem;color:#64748B;font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">Source Item</th>
                            <th style="text-align:left;padding:0 0.75rem 0.5rem 0.75rem;color:#64748B;font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">Severity</th>
                            <th style="text-align:left;padding:0 0.75rem 0.5rem 0.75rem;color:#64748B;font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">Signal</th>
                            <th style="text-align:left;padding:0 0.75rem 0.5rem 0.75rem;color:#64748B;font-size:0.72rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            + "".join(preview_rows)
            + """
                    </tbody>
                </table>
            </div>
            """
        )

    issues_display_order = [

        "Priority Score",

        "Priority Reason",

        "Health",

        "Device Name Base",

        "key",

        "IP Address",

        "Primary Connection",

        "Secondary Connection",

        "Offline For (hrs)",

        "Ticket ID",

        "Error Flags",

        "Ping Status",

        "Servers",

        "disposition",

        "notes",

        "Location",

        "Ticket Status",

    ]

    render_data_editor(

        issues_with_ping,

        "issues",

        preferred_order=issues_display_order,

        enable_inline_tdx_actions=True,

        default_visible_cols=[

            "Priority Score",

            "Health",

            "Device Name Base",

            "key",

            "IP Address",

            "Primary Connection",

            "Secondary Connection",

            "Ping Status",

            "Offline For (hrs)",

            "Ticket ID",

            "Error Flags",

        ],

        table_height=500,

    )

    pending_ping_count = len(st.session_state.get("ping_pending_ips", []))

    if pending_ping_count > 0:

        st.caption(f"Pinging cameras... {pending_ping_count} remaining (updating this Action Queue view only)")

    st.caption("Create help tickets or acknowledge pending items from this filtered action queue.")

    render_action_required_ticket_queue(pending_issue_tickets_df)





if selected_workspace == "Health Status":
    if selected_area == "Overview":
        render_overview_section()
    elif selected_area == "Action Queue":
        render_action_required_tab()
    elif selected_area == "Trends":
        render_trends_tab(filtered_devices, transitions_df, observed_at)
    elif selected_area == "Retention":
        if retention_available:
            render_retention_tab(retention_violations_df)
        else:
            st.info("Retention data is not available in the current loaded export.")
elif selected_workspace == "Ticket Related":
    if selected_area == "Open Tickets":
        render_health_section_intro(
            "Queued / Open Tickets",
            "Review and update active ticket records until they are resolved, removed, or replaced.",
            eyebrow="Ticket Related",
        )
        render_tickets_editor(tickets_editor_df)
    else:
        render_ticket_response_assistant()
else:
    render_camera_installation_builder()









