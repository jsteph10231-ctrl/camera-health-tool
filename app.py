import os
import base64 as _b64
import smtplib
import subprocess
import platform
import ipaddress
from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape as html_escape
from typing import Any

import pandas as pd
import streamlit as st
from streamlit import config as st_config

# Load tiger eye as favicon (PIL Image so Streamlit renders it as a real icon)
try:
    from PIL import Image as _PILImage
    _favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tiger_eye.png")
    _favicon = _PILImage.open(_favicon_path)
except Exception:
    _favicon = "\U0001F42F"  # fallback if file missing or PIL unavailable

st.set_page_config(page_title="LSU Camera Health Tool", layout="wide", page_icon=_favicon)

# Minimal dark/light switch in sidebar.
if "theme_dark_mode" not in st.session_state:
    st.session_state.theme_dark_mode = True
theme_dark_mode = st.sidebar.toggle("Dark Mode", key="theme_dark_mode")

theme_config = {
    "theme.base": "dark" if theme_dark_mode else "light",
    "theme.primaryColor": "#FDD023" if theme_dark_mode else "#461D7C",
    "theme.backgroundColor": "#12161c" if theme_dark_mode else "#FFFFFF",
    "theme.secondaryBackgroundColor": "#1b222c" if theme_dark_mode else "#F7F4FB",
    "theme.textColor": "#E7ECF3" if theme_dark_mode else "#24183D",
}
for _theme_key, _theme_value in theme_config.items():
    st_config.set_option(_theme_key, _theme_value)

# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ LSU Purple & Gold Theme ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
_LEGACY_THEME_CSS = """
<style>
/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Palette ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
/* Purple : #461D7C  |  Gold : #FDD023  |  Dark purple bg : #2D1259 */

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ App background ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stAppViewContainer"] {
    background-color: #1a0a36;
}
[data-testid="stMain"] {
    background-color: #1a0a36;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Sidebar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2D1259 0%, #461D7C 100%);
    border-right: 3px solid #FDD023;
}
[data-testid="stSidebar"] * {
    color: #FDD023 !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background-color: #3a1a6e !important;
    color: #FDD023 !important;
    border: 1px solid #FDD023 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
    color: #FDD023 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background-color: #FDD023 !important;
    color: #461D7C !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #ffe566 !important;
    color: #2D1259 !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Top header bar (page title area) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
header[data-testid="stHeader"] {
    background: #461D7C;
    border-bottom: 3px solid #FDD023;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ All text ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
html, body, [class*="css"] {
    color: #f5f0ff;
}
h1, h2, h3 {
    color: #FDD023 !important;
    font-family: 'Georgia', serif;
    letter-spacing: 0.5px;
}
p, label, div, span {
    color: #e8deff;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Title ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stTitle"] {
    color: #FDD023 !important;
    font-size: 2rem !important;
    border-bottom: 2px solid #FDD023;
    padding-bottom: 0.4rem;
    margin-bottom: 0.8rem;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Metrics ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stMetric"] {
    background: #2D1259;
    border: 1px solid #FDD023;
    border-radius: 10px;
    padding: 8px 10px !important;
    min-width: 0;
    overflow: hidden;
}
[data-testid="stMetricLabel"] > div {
    color: #FDD023 !important;
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stMetricValue"] > div {
    color: #ffffff !important;
    font-size: clamp(1rem, 2vw, 1.6rem) !important;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Keyframe Animations ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
@keyframes btn-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(253,208,35,0.55); }
    60%  { box-shadow: 0 0 0 7px rgba(253,208,35,0); }
    100% { box-shadow: 0 0 0 0 rgba(253,208,35,0); }
}
@keyframes sidebar-shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes input-glow-pulse {
    0%, 100% { box-shadow: 0 0 0 2px rgba(253,208,35,0.15); }
    50%       { box-shadow: 0 0 0 4px rgba(253,208,35,0.40); }
}
@keyframes tab-alert-blink {
    0%, 100% { color: #ff6b6b !important; }
    50%       { color: #ffb3b3 !important; }
}
@keyframes metric-lift {
    0%   { transform: translateY(0px); }
    50%  { transform: translateY(-2px); }
    100% { transform: translateY(0px); }
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Main buttons ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stMain"] .stButton > button {
    background-color: #461D7C !important;
    color: #FDD023 !important;
    border: 2px solid #FDD023 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.22s ease, box-shadow 0.22s ease, transform 0.18s ease !important;
}
[data-testid="stMain"] .stButton > button:hover {
    background-color: #FDD023 !important;
    color: #461D7C !important;
    border-color: #FDD023 !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(253,208,35,0.35) !important;
}
[data-testid="stMain"] .stButton > button:hover * {
    color: #461D7C !important;
}
[data-testid="stMain"] .stButton > button:active {
    transform: translateY(0px) scale(0.98) !important;
    box-shadow: 0 2px 6px rgba(253,208,35,0.2) !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Text inputs ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stMain"] input[type="text"],
[data-testid="stMain"] textarea {
    background-color: #2D1259 !important;
    color: #f5f0ff !important;
    border: 1px solid #7a52b5 !important;
    border-radius: 6px !important;
}
[data-testid="stMain"] input[type="text"]:focus,
[data-testid="stMain"] textarea:focus {
    border-color: #FDD023 !important;
    box-shadow: 0 0 0 2px rgba(253,208,35,0.3) !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Selectbox / Multiselect ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #2D1259 !important;
    border: 1px solid #7a52b5 !important;
    border-radius: 6px !important;
    color: #f5f0ff !important;
}
/* Multiselect tags ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ gold bg needs purple text */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #FDD023 !important;
    color: #461D7C !important;
    font-weight: 700;
    border-radius: 4px !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #461D7C !important;
    fill: #461D7C !important;
}
/* Sidebar Load button (gold bg) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ text must be purple */
[data-testid="stSidebar"] .stButton > button * {
    color: #461D7C !important;
}
/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Checkbox ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stCheckbox"] label {
    color: #f5f0ff !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Dataframe / table ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stDataFrame"] > div {
    border: 1px solid #461D7C;
    border-radius: 8px;
    overflow: hidden;
}
[data-testid="stDataFrame"] th {
    background-color: #461D7C !important;
    color: #FDD023 !important;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.78rem;
    letter-spacing: 0.5px;
}
[data-testid="stDataFrame"] tr:nth-child(even) {
    background-color: #2a1155 !important;
}
[data-testid="stDataFrame"] tr:hover {
    background-color: #3d1a72 !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Success / error / info / warning banners ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background-color: #1a3d1a !important;
    border-left: 4px solid #4caf50 !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
    background-color: #3d0a0a !important;
    border-left: 4px solid #e53935 !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Expanders ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stExpander"] {
    background-color: #2D1259 !important;
    border: 1px solid #461D7C !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #FDD023 !important;
    font-weight: 600;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Subheaders (st.subheader) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    color: #FDD023 !important;
    border-left: 4px solid #FDD023;
    padding-left: 10px;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Caption text ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stCaptionContainer"] {
    color: #c0a8f0 !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ File uploader ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
[data-testid="stFileUploader"] {
    background-color: #2D1259 !important;
    border: 2px dashed #7a52b5 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #FDD023 !important;
}

/* ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Scrollbar ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #1a0a36; }
::-webkit-scrollbar-thumb { background: #461D7C; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #FDD023; }
</style>
"""
st.markdown("""
<style>
:root {
    --lsu-purple: #461D7C;
    --lsu-gold: #FDD023;
    --warning: #d49a00;
    --bg: #12161c;
    --panel: #1b222c;
    --panel-2: #222b36;
    --panel-3: #2a3442;
    --border: #2d3846;
    --text: #e7ecf3;
    --muted: #aab4c3;
    --accent: #6b4ea2;
    --accent-2: #5876a8;
    --gold: #d6b24c;
    --warm: #d9785a;
    --success: #2f7d57;
    --success-bg: #16281f;
    --danger: #b24a4a;
    --danger-bg: #2b1719;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background:
        radial-gradient(circle at top right, rgba(107, 78, 162, 0.12), transparent 32%),
        radial-gradient(circle at top left, rgba(88, 118, 168, 0.08), transparent 28%),
        var(--bg) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #171d26 0%, #11161d 100%) !important;
    border-right: 2px solid rgba(214, 178, 76, 0.32) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background-color: var(--panel-2) !important;
    color: var(--text) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(
        270deg,
        var(--accent) 0%,
        var(--accent-2) 40%,
        var(--accent) 80%
    ) !important;
    background-size: 300% 100% !important;
    color: #f7f9fc !important;
    border: 2px solid rgba(214, 178, 76, 0.35) !important;
    transition: all 0.25s ease, transform 0.18s ease !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    filter: brightness(1.15) !important;
    border-color: rgba(214, 178, 76, 0.75) !important;
    transform: scale(1.02) !important;
    box-shadow: 0 4px 14px rgba(107, 78, 162, 0.5) !important;
}
[data-testid="stSidebar"] .stButton > button:focus-visible {
    outline: 3px solid var(--lsu-gold) !important;
    outline-offset: 2px !important;
}
[data-testid="stSidebar"] .stButton > button * {
    color: #f7f9fc !important;
}
[data-testid="stSidebar"] [data-baseweb="checkbox"]:first-of-type {
    margin: 0 0 10px 0 !important;
    padding: 2px 0 10px 0 !important;
    border-bottom: 1px solid rgba(214, 178, 76, 0.2) !important;
}
[data-testid="stSidebar"] [data-baseweb="checkbox"]:first-of-type > div:first-of-type p {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #dfe6f0 !important;
}
[data-testid="stSidebar"] [data-baseweb="checkbox"]:first-of-type > div:nth-of-type(2) {
    transform: scale(0.92) !important;
}

header[data-testid="stHeader"] {
    background: rgba(18, 22, 28, 0.92) !important;
    border-bottom: 2px solid rgba(214, 178, 76, 0.22) !important;
}

html, body, [class*="css"] {
    color: var(--text) !important;
}
h1, h2, h3 {
    color: var(--text) !important;
    letter-spacing: 0.3px !important;
}
[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] .stMarkdown {
    color: var(--muted);
}

[data-testid="stTitle"] {
    color: var(--text) !important;
    border-bottom: 1px solid var(--border) !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(34, 43, 54, 0.96), rgba(27, 34, 44, 0.96)) !important;
    border: 2px solid rgba(214, 178, 76, 0.18) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 6px 18px rgba(4, 8, 14, 0.25);
}
[data-testid="stMetricLabel"] > div {
    color: #d7c9f2 !important;
}
[data-testid="stMetricValue"] > div {
    color: var(--text) !important;
}

[data-testid="stMain"] .stButton > button {
    background: linear-gradient(180deg, rgba(49, 60, 78, 0.96), rgba(34, 44, 58, 0.96)) !important;
    color: #f7f9fc !important;
    border: 1px solid rgba(214, 178, 76, 0.24) !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    padding: 0.72rem 0.95rem !important;
    transition: all 0.22s ease, transform 0.18s ease, box-shadow 0.22s ease !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 8px 18px rgba(7, 14, 24, 0.24) !important;
}
[data-testid="stMain"] .stButton > button * {
    color: #f7f9fc !important;
}
[data-testid="stMain"] .stButton > button:hover {
    background: linear-gradient(180deg, rgba(61, 74, 96, 0.98), rgba(40, 52, 69, 0.98)) !important;
    border-color: rgba(214, 178, 76, 0.55) !important;
    transform: translateY(-2px) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 10px 24px rgba(107, 78, 162, 0.24) !important;
}
[data-testid="stMain"] .stButton > button:hover * {
    color: #f7f9fc !important;
}
[data-testid="stMain"] .stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
    filter: brightness(0.95) !important;
}
[data-testid="stMain"] .stButton > button:focus-visible {
    outline: 3px solid var(--lsu-gold) !important;
    outline-offset: 2px !important;
}

[data-testid="stMain"] input[type="text"],
[data-testid="stMain"] textarea,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: linear-gradient(180deg, rgba(34, 43, 54, 0.98), rgba(27, 34, 44, 0.98)) !important;
    color: var(--text) !important;
    border: 1px solid rgba(107, 78, 162, 0.32) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 8px 20px rgba(5, 10, 18, 0.16) !important;
}
[data-testid="stMain"] input[type="text"]:focus,
[data-testid="stMain"] textarea:focus {
    border-color: var(--lsu-gold) !important;
    box-shadow: 0 0 0 3px rgba(214, 178, 76, 0.22) !important;
}
div[data-testid="stTextInput"] label p {
    color: #dfe6f0 !important;
    font-weight: 700 !important;
    letter-spacing: 0.35px !important;
    text-transform: uppercase !important;
    font-size: 0.8rem !important;
}
div[data-testid="stTextInput"] input {
    min-height: 48px !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #a5b0bf !important;
    opacity: 1 !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: rgba(107, 78, 162, 0.2) !important;
    color: #d7c9f2 !important;
    border: 1px solid rgba(107, 78, 162, 0.45) !important;
    border-radius: 999px !important;
}
[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #d7c9f2 !important;
    fill: #d7c9f2 !important;
}

[data-testid="stCheckbox"] label {
    color: var(--text) !important;
}

[data-testid="stDataFrame"] {
    padding: 6px !important;
    border-radius: 14px !important;
    background: linear-gradient(180deg, rgba(45, 18, 89, 0.92), rgba(26, 10, 54, 0.94)) !important;
    border: 1px solid rgba(253, 208, 35, 0.30) !important;
    box-shadow: 0 14px 28px rgba(10, 4, 20, 0.30) !important;
}
[data-testid="stDataFrame"] > div {
    border: 1px solid rgba(253, 208, 35, 0.30) !important;
    border-radius: 12px !important;
    background: rgba(32, 15, 66, 0.94) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02) !important;
}
[data-testid="stDataFrame"] th {
    background: #461D7C !important;
    color: #FDD023 !important;
    border-bottom: 1px solid rgba(253, 208, 35, 0.42) !important;
}
[data-testid="stDataFrame"] tr:nth-child(even) {
    background-color: rgba(253, 208, 35, 0.05) !important;
}
[data-testid="stDataFrame"] tr:hover {
    background-color: rgba(253, 208, 35, 0.16) !important;
}

[data-testid="stDataFrame"] [role="toolbar"],
[data-testid="stDataFrame"] [class*="toolbar"],
[data-testid="stDataFrame"] [class*="menu"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
[data-testid="stDataFrame"] button,
[data-testid="stDataFrame"] [role="button"] {
    background: rgba(70, 29, 124, 0.94) !important;
    border: 1px solid rgba(253, 208, 35, 0.34) !important;
    color: #FDD023 !important;
    border-radius: 9px !important;
    box-shadow: none !important;
}
[data-testid="stDataFrame"] button:hover,
[data-testid="stDataFrame"] [role="button"]:hover {
    background: rgba(95, 62, 152, 0.96) !important;
    border-color: rgba(253, 208, 35, 0.92) !important;
    color: #fff7d1 !important;
}
[data-testid="stDataFrame"] button svg,
[data-testid="stDataFrame"] [role="button"] svg {
    fill: #FDD023 !important;
    stroke: #FDD023 !important;
}

div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
    background-color: var(--success-bg) !important;
    border-left: 4px solid var(--success) !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
    background-color: var(--danger-bg) !important;
    border-left: 4px solid var(--danger) !important;
}

[data-testid="stExpander"] {
    background-color: rgba(27, 34, 44, 0.96) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: var(--text) !important;
}
[data-testid="stExpander"] summary:focus-visible {
    outline: 3px solid var(--lsu-gold) !important;
    outline-offset: 2px !important;
    border-radius: 6px !important;
}

button[data-baseweb="tab"] {
    color: #aeb8c8 !important;
    border: 1px solid rgba(214, 178, 76, 0.12) !important;
    border-bottom: 0 !important;
    background: linear-gradient(180deg, rgba(24, 34, 51, 0.86), rgba(19, 28, 40, 0.9)) !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 0.62rem 1rem !important;
    margin-right: 0.28rem !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #f4f7fb !important;
    border-color: rgba(214, 178, 76, 0.42) !important;
    background: linear-gradient(180deg, rgba(41, 55, 77, 0.98), rgba(28, 40, 57, 0.98)) !important;
    box-shadow: inset 0 -3px 0 var(--lsu-gold), 0 8px 18px rgba(7, 14, 24, 0.16) !important;
}
button[data-baseweb="tab"]:nth-of-type(2) {
    color: #d8b9ae !important;
    border-color: rgba(217, 120, 90, 0.16) !important;
}
button[data-baseweb="tab"]:nth-of-type(2)[aria-selected="true"] {
    color: #fff2eb !important;
    border-color: rgba(217, 120, 90, 0.38) !important;
    background: linear-gradient(180deg, rgba(66, 38, 41, 0.92), rgba(42, 28, 38, 0.95)) !important;
    box-shadow: inset 0 -3px 0 var(--warm), 0 8px 18px rgba(20, 10, 10, 0.18) !important;
}
button[data-baseweb="tab"]:focus-visible {
    outline: 3px solid var(--lsu-gold) !important;
    outline-offset: 2px !important;
}

[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    color: var(--text) !important;
    border-left: 4px solid var(--accent) !important;
    padding-left: 12px !important;
    margin-top: 0.35rem !important;
    letter-spacing: 0.2px !important;
}

[data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
}

[data-testid="stFileUploader"] {
    background-color: rgba(27, 34, 44, 0.96) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

::-webkit-scrollbar-track { background: #141a21 !important; }
::-webkit-scrollbar-thumb { background: #334154 !important; }
::-webkit-scrollbar-thumb:hover { background: var(--accent) !important; }

</style>
""", unsafe_allow_html=True)

# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ LSU branded page header (tiger eye logo) ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
_tiger_eye_path = os.path.join(os.path.dirname(__file__), "data", "tiger_eye.png")
try:
    with open(_tiger_eye_path, "rb") as _f:
        _tiger_b64 = _b64.b64encode(_f.read()).decode()
    _logo_html = f'<img src="data:image/png;base64,{_tiger_b64}" style="height:44px;width:44px;object-fit:cover;border-radius:4px;border:1px solid #FDD023;">'
except Exception:
    _logo_html = '<span style="font-size:1.6rem;">\U0001F42F</span>'  # fallback

st.markdown(f"""
<style>
@keyframes shimmer-border {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
.lsu-banner-wrapper {{
    position: relative;
    background: linear-gradient(90deg, #2D1259 0%, #1a0a36 100%);
    padding: 16px 18px;
    border-radius: 6px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 14px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}}
.lsu-banner-wrapper::after {{
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #FDD023 0%, #461D7C 50%, #FDD023 100%);
    background-size: 200% 100%;
    animation: shimmer-border 3s infinite linear;
}}
</style>

<div class="lsu-banner-wrapper">
    {_logo_html}
    <div>
        <div class="lsu-banner-title" style="color:#FDD023; font-size:1.4rem; font-weight:700;
                    font-family:'Georgia',serif; letter-spacing:0.5px; line-height:1.0;">
            LSU CAMERA HEALTH TOOL
        </div>
        <div class="lsu-banner-subtitle" style="color:#c0a8f0; font-size:0.85rem; letter-spacing:1px; margin-top:3px;">
            PUBLIC SAFETY \u00B7 SURVEILLANCE OPERATIONS
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not theme_dark_mode:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background:
            radial-gradient(circle at top right, rgba(70, 29, 124, 0.08), transparent 30%),
            radial-gradient(circle at top left, rgba(253, 208, 35, 0.12), transparent 26%),
            #f6f4fb !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fcfaff 0%, #f5effc 100%) !important;
        border-right: 3px solid #FDD023 !important;
    }
    [data-testid="stSidebar"] * {
        color: #2f1e52 !important;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        background-color: #ffffff !important;
        color: #2f1e52 !important;
        border: 2px solid #461D7C !important;
        box-shadow: 0 0 0 1px rgba(253, 208, 35, 0.2) !important;
    }
    [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        color: #461D7C !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #461D7C, #5f3e98) !important;
        color: #FDD023 !important;
        border: 2px solid #FDD023 !important;
        animation: none !important;
        box-shadow: 0 6px 14px rgba(70, 29, 124, 0.14) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #5b2791 !important;
        color: #FDD023 !important;
        border-color: #FDD023 !important;
        box-shadow: 0 8px 18px rgba(70, 29, 124, 0.18) !important;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #FDD023 !important;
    }
    [data-testid="stSidebar"] .stButton > button:focus-visible {
        outline: 3px solid #FDD023 !important;
        outline-offset: 2px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="checkbox"]:first-of-type {
        border-bottom: 1px solid rgba(70, 29, 124, 0.2) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="checkbox"]:first-of-type > div:first-of-type p {
        color: #461D7C !important;
    }

    header[data-testid="stHeader"] {
        background: rgba(252, 249, 255, 0.96) !important;
        border-bottom: 3px solid #FDD023 !important;
    }

    html, body, [class*="css"] {
        color: #24183d !important;
    }
    h1, h2, h3 {
        color: #2f1e52 !important;
    }
    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] .stMarkdown {
        color: #5e5473 !important;
    }

    [data-testid="stTitle"] {
        color: #2f1e52 !important;
        border-bottom: 2px solid #461D7C !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff, #f7f1ff) !important;
        border: 2px solid #461D7C !important;
        box-shadow: 0 8px 18px rgba(70, 29, 124, 0.08), inset 0 0 0 1px rgba(253, 208, 35, 0.2) !important;
    }
    [data-testid="stMetricLabel"] > div {
        color: #461D7C !important;
    }
    [data-testid="stMetricValue"] > div {
        color: #2f1e52 !important;
    }

    [data-testid="stMain"] .stButton > button {
        background: linear-gradient(135deg, #461D7C, #5f3e98) !important;
        color: #FDD023 !important;
        border: 2px solid #FDD023 !important;
        box-shadow: 0 4px 12px rgba(70, 29, 124, 0.14) !important;
        border-radius: 10px !important;
        min-height: 44px !important;
    }
    [data-testid="stMain"] .stButton > button * {
        color: #FDD023 !important;
    }
    [data-testid="stMain"] .stButton > button:hover {
        background: #5b2791 !important;
        color: #FDD023 !important;
        border-color: #FDD023 !important;
        box-shadow: 0 8px 18px rgba(70, 29, 124, 0.18) !important;
    }
    [data-testid="stMain"] .stButton > button:hover * {
        color: #FDD023 !important;
    }
    [data-testid="stMain"] .stButton > button:focus-visible {
        outline: 3px solid #FDD023 !important;
        outline-offset: 2px !important;
    }

    [data-testid="stMain"] input[type="text"],
    [data-testid="stMain"] textarea,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background-color: #ffffff !important;
        color: #24183d !important;
        border: 2px solid #461D7C !important;
        box-shadow: 0 0 0 1px rgba(253, 208, 35, 0.16) !important;
    }
    [data-testid="stMain"] input[type="text"]:focus,
    [data-testid="stMain"] textarea:focus {
        border-color: #FDD023 !important;
        box-shadow: 0 0 0 3px rgba(253, 208, 35, 0.22) !important;
        animation: none !important;
    }
    div[data-testid="stTextInput"] label p {
        color: #461D7C !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
    }
    div[data-testid="stTextInput"] input {
        min-height: 48px !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #6d6484 !important;
        opacity: 1 !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #FDD023 !important;
        color: #461D7C !important;
        border: 1px solid #461D7C !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        color: #461D7C !important;
        fill: #461D7C !important;
    }

    [data-testid="stCheckbox"] label {
        color: #2f1e52 !important;
    }

    [data-testid="stDataFrame"] > div {
        border: 2px solid #461D7C !important;
        border-radius: 10px !important;
        background-color: #ffffff !important;
        box-shadow: inset 0 0 0 1px rgba(253, 208, 35, 0.18) !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: #461D7C !important;
        color: #FDD023 !important;
    }
    [data-testid="stDataFrame"] tr:nth-child(even) {
        background-color: rgba(70, 29, 124, 0.04) !important;
    }
    [data-testid="stDataFrame"] tr:hover {
        background-color: rgba(253, 208, 35, 0.12) !important;
    }
    [data-testid="stDataFrame"] canvas {
        filter: invert(1) hue-rotate(180deg) brightness(1.03) contrast(0.96) !important;
    }
    [data-testid="stDataFrame"] input,
    [data-testid="stDataFrame"] textarea {
        background-color: #ffffff !important;
        color: #24183d !important;
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
        border: 1px solid rgba(70, 29, 124, 0.16) !important;
        color: #461D7C !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }
    [data-testid="stDataFrame"] button:hover,
    [data-testid="stDataFrame"] [role="button"]:hover {
        background: rgba(247, 241, 255, 0.98) !important;
        border-color: rgba(253, 208, 35, 0.9) !important;
        color: #461D7C !important;
        box-shadow: 0 2px 8px rgba(70, 29, 124, 0.08) !important;
    }
    [data-testid="stDataFrame"] button:focus-visible,
    [data-testid="stDataFrame"] [role="button"]:focus-visible {
        outline: 2px solid #FDD023 !important;
        outline-offset: 1px !important;
    }
    [data-testid="stDataFrame"] button svg,
    [data-testid="stDataFrame"] [role="button"] svg {
        fill: #461D7C !important;
        stroke: #461D7C !important;
    }

    [data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border: 2px solid #461D7C !important;
    }
    div[data-testid="stAlert"][data-baseweb="notification"][kind="positive"] {
        background-color: #edf8f1 !important;
        border-left: 4px solid #2f7d57 !important;
    }
    div[data-testid="stAlert"][data-baseweb="notification"][kind="negative"] {
        background-color: #fdeeee !important;
        border-left: 4px solid #b24a4a !important;
    }

    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border: 2px solid #461D7C !important;
        box-shadow: inset 0 0 0 1px rgba(253, 208, 35, 0.16) !important;
    }
    [data-testid="stExpander"] summary {
        color: #2f1e52 !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] summary:focus-visible {
        outline: 3px solid #FDD023 !important;
        outline-offset: 2px !important;
        border-radius: 6px !important;
    }

    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3 {
        color: #2f1e52 !important;
        border-left: 4px solid #FDD023 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #675a81 !important;
    }

    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border: 2px dashed #461D7C !important;
    }
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] [class*="uploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
    }
    [data-testid="stFileUploader"] * {
        color: #461D7C !important;
    }
    [data-testid="stFileUploader"] button {
        background: #f7f1ff !important;
        border: 1px solid #461D7C !important;
        color: #461D7C !important;
    }
    [data-testid="stFileUploader"] button * {
        color: #461D7C !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #FDD023 !important;
    }

    button[data-baseweb="tab"] {
        color: #461D7C !important;
        border: 1px solid rgba(70, 29, 124, 0.28) !important;
        border-bottom: 0 !important;
        background: #ffffff !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 0.58rem 0.9rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2f1e52 !important;
        border-color: #461D7C !important;
        background: #f7f1ff !important;
        box-shadow: inset 0 -3px 0 #FDD023 !important;
    }
    button[data-baseweb="tab"]:focus-visible {
        outline: 3px solid #FDD023 !important;
        outline-offset: 2px !important;
    }

    ::-webkit-scrollbar-track { background: #eee8f7 !important; }
    ::-webkit-scrollbar-thumb { background: #b8abd5 !important; }
    ::-webkit-scrollbar-thumb:hover { background: #5f3e98 !important; }

    .lsu-banner-wrapper {
        background: linear-gradient(90deg, #ffffff 0%, #f4eefc 100%) !important;
        border: 2px solid #461D7C !important;
        box-shadow: 0 4px 14px rgba(70, 29, 124, 0.08), inset 0 0 0 1px rgba(253, 208, 35, 0.18) !important;
    }
    .lsu-banner-wrapper::after {
        background: linear-gradient(90deg, #5f3e98 0%, #fdd023 50%, #5f3e98 100%) !important;
    }
    .lsu-banner-title {
        color: #4a2c7f !important;
    }
    .lsu-banner-subtitle {
        color: #6e5f8d !important;
    }
    </style>
    """, unsafe_allow_html=True)

DEFAULT_SITE_HEALTH_PATH = r"C:\Users\stephenson\Documents\camera-health-tool\LSU Public Safety Surveillance.csv"
NOTES_PATH = os.path.join("data", "notes.csv")
TRACKING_PATH = os.path.join("data", "device_tracking.csv")
TICKETS_PATH = os.path.join("data", "tickets.csv")
TRANSITIONS_PATH = os.path.join("data", "state_transitions.csv")
TDX_HELPDESK_EMAIL = "helpdesk@lsu.edu"
RETENTION_POLICY_DAYS = 20


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
    header_idx = None
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for i, line in enumerate(f):
            if "Server Name" in line and "Device Name" in line:
                header_idx = i
                break

    if header_idx is None:
        raise ValueError("Could not find device table header row containing 'Server Name' and 'Device Name'.")

    df = pd.read_csv(path, skiprows=header_idx, engine="python", on_bad_lines="skip")
    df = normalize_avigilon_headers(df)
    return df


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
        s.astype(str)
        .str.strip()
        .replace({"nan": "", "None": "", "none": ""})
    )


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
    if devices_df.empty:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    prior_map: dict[str, str] = {}
    if not prior_tracking_df.empty and {"key", "current_health_state"}.issubset(prior_tracking_df.columns):
        prior_map: dict[str, str] = (
            prior_tracking_df[["key", "current_health_state"]]
            .drop_duplicates(subset=["key"], keep="last")
            .set_index("key")["current_health_state"]
            .fillna("")
            .astype(str)
            .to_dict()
        )

    ts_iso = format_timestamp(observed_at)
    rows: list[dict[str, str]] = []
    for _, row in devices_df.iterrows():
        key = str(row.get("key", "")).strip()
        if not key:
            continue
        prior_state = str(prior_map.get(key, "")).strip()
        current_state = str(row.get("Health State", "")).strip()
        if prior_state and current_state and prior_state != current_state:
            rows.append({
                "timestamp_utc": ts_iso,
                "key": key,
                "from_state": prior_state,
                "to_state": current_state,
                "device_name": str(row.get("Device Name Base", "")),
                "location": str(row.get("Location", "")),
            })

    if not rows:
        return

    append_df = pd.DataFrame(rows)
    needs_header = (not os.path.exists(path)) or os.path.getsize(path) == 0
    append_df.to_csv(path, mode="a", header=needs_header, index=False)


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
    error_flags = out.get("Error Flags", pd.Series([""] * len(out), index=out.index)).fillna("").astype(str).str.strip()
    has_error_flags = error_flags.replace({"nan": "", "none": "","None": ""}).ne("")
    offline_hours = pd.to_numeric(out.get("Offline For (hrs)", 0.0), errors="coerce").fillna(0.0).clip(lower=0)
    missing_ip = out.get("IP Address", pd.Series([""] * len(out), index=out.index)).fillna("").astype(str).str.strip().eq("")

    offline_mask = health_state.eq("Offline")
    offline_visible_mask = health_state.eq("Offline (but still visible)")
    not_pingable_mask = ping_lower.str.contains("not pingable", na=False)
    ping_error_mask = ping_lower.str.contains("ping error", na=False)

    score = pd.Series(0.0, index=out.index, dtype=float)
    score += offline_mask.astype(float) * 50
    score += offline_visible_mask.astype(float) * 25
    score += has_error_flags.astype(float) * 10
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
        if bool(has_error_flags.loc[idx]):
            reasons.append("Error Flags")
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
        prior = tracking_map[key] if key in tracking_map else {}
        is_offline = row.get("Health State", "Online") != "Online"
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
            is_offline
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
        status = df["Status"].astype(str).str.strip().str.lower()
        failed_status = status.str.contains("fail", na=False)
    else:
        failed_status = pd.Series(False, index=df.index)

    if "Error Flags" in df.columns:
        err = df["Error Flags"].astype(str).str.strip().replace({"nan": "", "None": "", "none": ""})
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
def build_devices_table(df_views: pd.DataFrame) -> pd.DataFrame:
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
        vals = series.fillna("").astype(str).str.strip()
        vals = vals.replace({"nan": "", "None": "", "none": ""})
        vals = [v for v in vals.tolist() if v]
        if not vals:
            return ""
        return " | ".join(sorted(set(vals)))

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

    # Nice ordering
    if "Device Name Base" in devices.columns:
        devices["Device Name Base"] = devices["Device Name Base"].fillna(devices["Device Name"])

    return devices


def apply_global_search(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    if not search_text:
        return df

    terms = search_text.lower().split()

    def row_matches(row) -> bool:
        blob = " ".join(row.astype(str)).lower()
        return all(term in blob for term in terms)

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
    pending: list[str] = list(st.session_state.get("ping_pending_ips", []))
    if not pending:
        return False

    batch = pending[:batch_size]
    remaining = pending[batch_size:]
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


# -----------------------------
# UI
# -----------------------------

st.sidebar.header("Input")
csv_path = st.sidebar.text_input("CSV path", value=DEFAULT_SITE_HEALTH_PATH)
uploaded = st.sidebar.file_uploader("Or upload Site Health CSV", type=["csv"])
load_clicked = st.sidebar.button("Load / Reload")
st.sidebar.caption("For hands-off refreshes, point this at a scheduled Avigilon Site Health CSV export.")

if load_clicked:
    clear_func = getattr(read_site_health_csv, "clear", None)
    if clear_func:
        clear_func()

with st.sidebar.expander("TDX Ticket Automation", expanded=False):
    tdx_email_to = TDX_HELPDESK_EMAIL
    st.caption(f"Help tickets are sent to: {TDX_HELPDESK_EMAIL}")
    smtp_host = st.text_input("SMTP host", value=os.getenv("SMTP_HOST", ""))
    smtp_port = st.number_input("SMTP port", min_value=1, max_value=65535, value=int(os.getenv("SMTP_PORT", "587")))
    smtp_username = st.text_input("SMTP username", value=os.getenv("SMTP_USERNAME", ""))
    smtp_password = st.text_input("SMTP password", value=os.getenv("SMTP_PASSWORD", ""), type="password")
    smtp_from_email = st.text_input("From email", value=os.getenv("SMTP_FROM", ""))
    ticket_threshold_hours = st.number_input(
        "Auto-ticket threshold (hours)",
        min_value=1,
        max_value=168,
        value=24,
        step=1,
        help="Auto-queue a ticket when a device remains offline at or above this threshold.",
    )

generate_weekly_digest_clicked = st.sidebar.button("Generate Weekly Digest")

should_load = load_clicked or (uploaded is not None) or os.path.exists(csv_path)
if not should_load:
    st.info("Set the CSV path (or upload a file) and click **Load / Reload**.")
    st.stop()

# Load view-level CSV
df = pd.DataFrame()
try:
    if uploaded is not None:
        df = pd.read_csv(uploaded, engine="python", on_bad_lines="skip")
        df = normalize_avigilon_headers(df)
        if "Server Name" not in df.columns or "Device Name" not in df.columns:
            st.warning("Upload didn't include expected headers. If this was a Site Health export, use the path load instead.")
            st.stop()
    else:
        df = read_site_health_csv(csv_path, get_file_signature(csv_path))
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# Validate minimum columns
required_cols = {"Server Name", "Device Name"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {sorted(list(missing))}")
    st.stop()

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
df_devices = build_devices_table(df_views)
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

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.button(f"\U0001F4F7 Unique Devices: {df_devices['physical_key'].nunique():,}", on_click=on_metric_click, args=("unique",), use_container_width=True)
with m2:
    st.button(f"\U0001F4CB All Views: {len(df_views):,}", on_click=on_metric_click, args=("export",), use_container_width=True)
with m3:
    st.button(f"Avigilon: {len(df_devices[df_devices['Brand'] == 'Avigilon']):,}", on_click=on_metric_click, args=("avigilon",), use_container_width=True)
with m4:
    st.button(f"Axis: {len(df_devices[df_devices['Brand'] == 'Axis']):,}", on_click=on_metric_click, args=("axis",), use_container_width=True)
with m5:
    st.button(f"Other: {len(df_devices[df_devices['Brand'].isin(['Other', 'Unknown'])]):,}", on_click=on_metric_click, args=("other",), use_container_width=True)

# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Sidebar Filters ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
with st.sidebar.expander("\u2699\uFE0F Advanced Filters", expanded=False):
    st.caption("These filters apply to both tabs.")
    brand_selected = st.multiselect(
        "Brand",
        options=brand_options,
        key="brand_select",
    )
    
    health_options = ["Online", "Offline", "Offline (but still visible)"]
    health_selected = st.multiselect(
        "Health state",
        options=health_options,
        default=[],
        key="health_select",
    )
    
    show_only_issues = st.checkbox(
        "Show only issue rows",
        value=False,
        help="Offline, not visible, failed status, or non-empty Error Flags.",
    )
    
    connected_filter = st.selectbox("Connected", ["Any", "TRUE", "FALSE"], index=0)
    visible_filter = st.selectbox("Visible", ["Any", "TRUE", "FALSE"], index=0)

with st.sidebar.expander("Columns found (views export)"):
    st.write(list(df_views.columns))

# ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ Main Area: Search ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬
search_text = st.session_state.get("search_text", "")

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

has_err = filtered["Error Flags"].astype(str).str.strip().replace({"nan": "", "None": "", "none": ""}).ne("")
failed_status = filtered["Status"].astype(str).str.contains("fail", case=False, na=False)
not_online = filtered["Health State"].ne("Online")
not_connected = ~filtered["Connected_bool"]
not_visible = ~filtered["Visible_bool"]

issues_mask = not_online | not_connected | not_visible | has_err | failed_status

if show_only_issues:
    filtered = filtered[issues_mask]
    issues_mask = pd.Series(True, index=filtered.index)

issues_df = filtered[issues_mask]
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
device_has_err = (
    filtered_devices["Error Flags"]
    .astype(str)
    .str.strip()
    .replace({"nan": "", "None": "", "none": ""})
    .ne("")
)
device_failed_status = filtered_devices["Status"].astype(str).str.contains("fail", case=False, na=False)
device_not_online = filtered_devices["Health State"].ne("Online")
device_not_connected = ~filtered_devices["Connected_bool"]
device_not_visible = ~filtered_devices["Visible_bool"]
device_issues_mask = device_not_online | device_not_connected | device_not_visible | device_has_err | device_failed_status
if show_only_issues:
    filtered_devices = filtered_devices[device_issues_mask]

prioritized_source = add_ping_status_for_issues(filtered_devices)
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
if digest_text:
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

    def _render_snapshot_metric(label: str, value: str) -> None:
        st.markdown(
            f"""
            <div class="ops-snapshot-metric-card">
                <div class="ops-snapshot-metric-label">{label}</div>
                <div class="ops-snapshot-metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
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
            import altair as alt

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
                .mark_arc(innerRadius=46, outerRadius=82, cornerRadius=3)
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
                .properties(width=width, height=height + 36)
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
                    margin-top: 0.08rem;
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

    with st.expander("Operations Snapshot", expanded=True):
        if devices_subset.empty:
            st.info("No devices in the current filtered scope.")
            return

        health_state = devices_subset.get(
            "Health State",
            pd.Series([""] * len(devices_subset), index=devices_subset.index),
        ).fillna("").astype(str)
        has_error = devices_subset.get(
            "Error Flags",
            pd.Series([""] * len(devices_subset), index=devices_subset.index),
        ).fillna("").astype(str).str.strip().replace({"nan": "", "None": "", "none": ""}).ne("")
        failed_status = devices_subset.get(
            "Status",
            pd.Series([""] * len(devices_subset), index=devices_subset.index),
        ).astype(str).str.contains("fail", case=False, na=False)
        connected_bool = devices_subset.get(
            "Connected_bool",
            pd.Series([True] * len(devices_subset), index=devices_subset.index),
        ).fillna(True).astype(bool)
        visible_bool = devices_subset.get(
            "Visible_bool",
            pd.Series([True] * len(devices_subset), index=devices_subset.index),
        ).fillna(True).astype(bool)
        issues_mask_local = (
            health_state.ne("Online")
            | (~connected_bool)
            | (~visible_bool)
            | has_error
            | failed_status
        )

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
        OPS_COLOR_GOOD = "#43C087"
        OPS_COLOR_WARN = "#F59E0B"
        OPS_COLOR_WARN_SOFT = "#F8BB5D"
        OPS_COLOR_UNKNOWN = "#8FA3BF"

        st.markdown(
            """
            <style>
            .ops-snapshot-metric-card {
                background: linear-gradient(180deg, rgba(34, 43, 54, 0.94), rgba(27, 34, 44, 0.96));
                border: 1px solid rgba(214, 178, 76, 0.28);
                border-radius: 12px;
                min-height: 94px;
                padding: 10px 12px 10px 26px;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
            }
            .ops-snapshot-metric-label {
                color: #C9D4E5;
                font-size: 0.86rem;
                font-weight: 650;
                line-height: 1.1;
                margin-bottom: 8px;
            }
            .ops-snapshot-metric-value {
                color: #F4F7FB;
                font-size: 2.0rem;
                font-weight: 700;
                line-height: 1.0;
                padding-left: 4px;
            }
            .ops-snapshot-chart-title {
                color: #C9D4E5;
                font-size: 1rem;
                font-weight: 650;
                line-height: 1.2;
                margin: 0.14rem 0 0.34rem 0;
            }
            .ops-ping-progress-wrap {
                display: flex;
                align-items: flex-start;
                justify-content: center;
                gap: 0.56rem;
                width: fit-content;
                max-width: 100%;
                margin: 0.34rem auto 0 auto;
            }
            .ops-ping-progress-ring {
                width: 168px;
                height: 168px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
            }
            .ops-ping-progress-center {
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
                color: #C9D4E5;
                font-size: 1rem;
                font-weight: 650;
                line-height: 1.2;
                margin: 0 0 0.24rem 0;
            }
            .ops-ping-progress-legend-title {
                color: #B7C5DA;
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
            </style>
            """,
            unsafe_allow_html=True,
        )

        metric_1, metric_2, metric_3, metric_4 = st.columns(4)
        with metric_1:
            _render_snapshot_metric("Filtered Devices", f"{len(devices_subset):,}")
        with metric_2:
            _render_snapshot_metric("Need Attention", f"{int(issues_mask_local.sum()):,}")
        with metric_3:
            _render_snapshot_metric("Open Tickets", f"{int(ticket_state_counts.get('Open', 0)):,}")
        with metric_4:
            if retention_enabled and "Retention OK" in devices_subset.columns:
                retention_violations = int((~devices_subset["Retention OK"].fillna(False)).sum())
                _render_snapshot_metric("Retention Violations", f"{retention_violations:,}")
            else:
                _render_snapshot_metric("Flapping Cameras (7d)", f"{int((flaps_7d > 0).sum()):,}")

        selected_health = None
        selected_location = None

        chart_left, chart_middle, chart_right = st.columns(3, gap="medium")
        with chart_left:
            health_order = ["Offline", "Offline (but still visible)", "Online"]
            health_counts = health_state.value_counts().reindex(health_order, fill_value=0)
            health_display_map = {
                "Offline (but still visible)": "Offline (visible)",
            }
            health_display_reverse = {v: k for k, v in health_display_map.items()}
            health_counts_display = health_counts.rename(index=health_display_map)
            selected_health_display = render_donut_chart(
                data=health_counts_display.rename("Count"),
                center_text=f"{int(health_counts.sum()):,}",
                center_label="Devices",
                panel_title="Health Mix",
                max_slices=6,
                empty_message="No health data in current scope.",
                category_colors={
                    "Offline": OPS_COLOR_WARN,
                    "Offline (visible)": OPS_COLOR_WARN_SOFT,
                    "Online": OPS_COLOR_GOOD,
                },
                chart_key="ops_snapshot_health_chart",
                selection_name="opsHealthSlice",
                legend_columns=1,
                legend_label_limit=220,
                legend_max_width_px=190,
                legend_position="right",
            )
            selected_health = health_display_reverse.get(selected_health_display, selected_health_display) if selected_health_display else None
        with chart_middle:
            issue_locations = devices_subset.loc[issues_mask_local].copy()
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
                selected_location = render_donut_chart(
                    data=location_counts.rename("Count"),
                    center_text=f"{int(location_counts.sum()):,}",
                    center_label="Devices",
                    panel_title="Top Locations Needing Attention",
                    max_slices=6,
                    empty_message="No issue locations in current scope.",
                    category_colors=location_colors,
                    chart_key="ops_snapshot_location_chart",
                    selection_name="opsLocationSlice",
                    legend_columns=1,
                    legend_label_limit=160,
                    legend_max_width_px=200,
                    legend_position="right",
                )
            else:
                st.info("No issue locations in current scope.")
                selected_location = None
        with chart_right:
            action_required_subset = devices_subset.loc[issues_mask_local].copy()
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
                render_ping_progress_visual(
                    ping_counts=ping_counts,
                    total_devices=int(len(action_required_subset)),
                    panel_title="Action Required Ping Check",
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


render_operations_snapshot(
    devices_subset=filtered_devices,
    tickets_subset=tickets_df,
    retention_enabled=retention_available,
)

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
    "Create TDX": "TDX",
}

# Widths tuned for readable defaults while keeping optional columns compact.
CAMERA_GRID_WIDTHS_ALL = {
    "Health": 180,
    "Device Name Base": 275,
    "key": 135,
    "IP Address": 130,
    "Offline For (hrs)": 105,
    "Ticket ID": 105,
    "Error Flags": 360,
    "Ping Status": 120,
    "Flaps (24h)": 95,
    "Flaps (7d)": 95,
    "Retention (days)": 120,
    "Retention Gap": 110,
    "Servers": 355,
    "disposition": 160,
    "notes": 260,
    "Location": 220,
    "Ticket Status": 120,
}

CAMERA_GRID_WIDTHS_ISSUES = {
    "Health": 180,
    "Device Name Base": 275,
    "key": 135,
    "IP Address": 130,
    "Ping Status": 120,
    "Flaps (24h)": 95,
    "Flaps (7d)": 95,
    "Retention (days)": 120,
    "Retention Gap": 110,
    "Offline For (hrs)": 105,
    "Ticket ID": 105,
    "Create TDX": 70,
    "Error Flags": 360,
    "Servers": 355,
    "disposition": 160,
    "notes": 260,
    "Location": 220,
    "Ticket Status": 120,
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
    selected_optional_cols = st.multiselect(
        "Show Additional Columns",
        options=optional_cols,
        default=[],
        key=f"extra_cols_{key_suffix}",
        help="These columns are hidden by default. Select any to add them to the table.",
    )
    display_cols = default_open_cols + [c for c in selected_optional_cols if c in optional_cols]
    if not display_cols:
        display_cols = available_cols

    width_map = CAMERA_GRID_WIDTHS_ISSUES if key_suffix == "issues" else CAMERA_GRID_WIDTHS_ALL
    editable_cols = {"disposition", "notes"}
    if enable_inline_tdx_actions:
        editable_cols.add(inline_tdx_col)

    grid_df = data_subset[available_cols].copy()
    display_df = grid_df[display_cols].copy()

    disposition_options = ["", "Investigating", "Vendor", "ITS/Network", "Construction", "Offline/Expected", "Replaced", "Closed"]

    def editor_width(col_name: str) -> str:
        px = int(width_map.get(col_name, 160))
        if px <= 115:
            return "small"
        if px <= 220:
            return "medium"
        return "large"

    column_config: dict[str, object] = {}
    for col in display_cols:
        header = AGGRID_HEADER_LABELS.get(col, col)
        width = editor_width(col)
        if col == "disposition":
            column_config[col] = st.column_config.SelectboxColumn(
                header,
                options=disposition_options,
                width=width,
            )
        elif col == inline_tdx_col:
            column_config[col] = st.column_config.CheckboxColumn(
                header,
                width="small",
            )
        elif col == "Offline For (hrs)":
            column_config[col] = st.column_config.NumberColumn(
                header,
                format="%.1f",
                width=width,
            )
        else:
            column_config[col] = st.column_config.TextColumn(
                header,
                width=width,
            )

    edited_display = st.data_editor(
        display_df,
        width="stretch",
        height=550,
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
                    skipped_count += 1
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
                    sent_count += 1
                else:
                    failed_count += 1
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

    c1, c2, c3 = st.columns(3)
    with c1:
        all_selected = len(all_keys) > 0 and all_keys.issubset(selected_keys)
        if st.button("Deselect All" if all_selected else "Select All", key="tab2_select_all", use_container_width=True):
            st.session_state.selected_tickets = set() if all_selected else set(all_keys)
            st.rerun()

    with c2:
        if st.button(f"Create Help Ticket ({selected_count})", key="tab2_create_help_ticket", use_container_width=True, disabled=selected_count == 0):
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
                    sent_count += 1
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
        if st.button(f"Acknowledge ({selected_count})", key="tab2_ack_selected", use_container_width=True, disabled=selected_count == 0):
            ack_mask = (
                tickets_df["ticket_key"].astype(str).isin(selected_keys)
                & tickets_df["ticket_state"].eq("Pending Send")
            )
            tickets_df.loc[ack_mask, "ticket_state"] = "Acknowledged"
            save_tickets(TICKETS_PATH, tickets_df)
            st.session_state.selected_tickets.clear()
            st.rerun()
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.caption(
    f"Worklist from current filters: {len(issues_df):,} need attention | "
    f"{len(open_tickets_df):,} open tickets | {len(all_df):,} cameras total."
)
tab_labels = [
    f"All Cameras ({len(all_df)})",
    f"Action Required ({len(issues_df)})",
    f"Open Tickets ({len(open_tickets_df)})",
    f"Prioritized ({len(prioritized_df)})",
]
if retention_available:
    tab_labels.append(f"Retention ({len(retention_violations_df)})")
tab_objects = st.tabs(tab_labels)
tab1 = tab_objects[0]
tab2 = tab_objects[1]
tab3 = tab_objects[2]
tab_prioritized = tab_objects[3]
tab_retention = tab_objects[4] if retention_available else None


def render_tickets_editor(ticket_subset: pd.DataFrame):
    if ticket_subset.empty:
        st.info("No queued or open tickets right now.")
        return

    cols = [
        "ticket_key", "ticket_state", "ticket_id", "device_name", "location",
        "offline_since", "offline_hours_at_creation", "email_to", "created_at",
        "email_sent_at", "resolution", "resolution_notes", "last_error",
    ]
    edited = st.data_editor(
        ticket_subset[cols],
        width="stretch",
        height=420,
        hide_index=True,
        disabled=[c for c in cols if c not in ["ticket_state", "ticket_id", "resolution", "resolution_notes"]],
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

    if st.button("Save Tickets", key="save_tickets"):
        save_tickets_from_editor(edited)


def render_prioritized_tab(prioritized_subset: pd.DataFrame):
    st.subheader("Prioritized Cameras")
    st.caption("Device-level priority ranking from current filters (highest score first).")
    if prioritized_subset.empty:
        st.info("No cameras match the current filters in this view.")
        return

    preferred_cols_priority = [
        "Priority Score",
        "Priority Reason",
        "Health",
        "Health State",
        "Device Name Base",
        "key",
        "IP Address",
        "Ping Status",
        "Offline For (hrs)",
        "Error Flags",
        "Flaps (24h)",
        "Flaps (7d)",
        "Retention (days)",
        "Retention Gap",
        "Location",
        "Ticket Status",
        "Ticket ID",
        "Servers",
    ]
    cols = [c for c in preferred_cols_priority if c in prioritized_subset.columns]
    cols += [c for c in prioritized_subset.columns if c not in cols]
    display_df = prioritized_subset[cols].copy()

    st.data_editor(
        display_df,
        width="stretch",
        height=550,
        hide_index=True,
        disabled=list(display_df.columns),
        key="prioritized_table",
    )


def render_retention_tab(retention_subset: pd.DataFrame):
    st.subheader("Retention")
    st.caption(f"Cameras below {RETENTION_POLICY_DAYS} days retention from current filters.")
    if retention_subset.empty:
        st.info("No retention violations in the current filtered scope.")
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

    st.data_editor(
        display_df,
        width="stretch",
        height=550,
        hide_index=True,
        disabled=list(display_df.columns),
        key="retention_table",
    )


with tab1:
    st.subheader("All Filtered Cameras")
    st.caption("Full filtered inventory for browsing and spot checks.")
    render_data_editor(all_df, "all")

@st.fragment(run_every=1.0)
def render_action_required_tab():
    st.subheader("Cameras Requiring Attention")
    st.caption("Prioritized rows: offline, failed, not visible, disconnected, or with error flags. Offline rows include live ping status.")
    if st.button("Refresh Ping Status", key="refresh_ping_status"):
        st.session_state.ping_status_by_ip = {}
        st.session_state.ping_pending_ips = []
    initialize_ping_queue(issues_df)
    process_ping_batch(batch_size=2)
    issues_with_ping = add_ping_status_for_issues(issues_df)
    issues_display_order = [
        "Health",
        "Device Name Base",
        "key",
        "IP Address",
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
            "Health",
            "Device Name Base",
            "key",
            "IP Address",
            "Ping Status",
            "Offline For (hrs)",
            "Ticket ID",
            "Error Flags",
        ],
    )
    pending_ping_count = len(st.session_state.get("ping_pending_ips", []))
    if pending_ping_count > 0:
        st.caption(f"Pinging cameras... {pending_ping_count} remaining (updating Action Required tab only)")
    st.caption("Create help tickets or acknowledge pending items from this filtered action queue.")
    render_action_required_ticket_queue(pending_issue_tickets_df)


with tab2:
    render_action_required_tab()

with tab3:
    st.subheader("Queued / Open Tickets")
    st.caption("Active ticket queue tracked until resolved, removed, or replaced.")
    render_tickets_editor(tickets_editor_df)

with tab_prioritized:
    render_prioritized_tab(prioritized_df)

if tab_retention is not None:
    with tab_retention:
        render_retention_tab(retention_violations_df)




