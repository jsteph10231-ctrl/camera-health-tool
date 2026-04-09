from __future__ import annotations

from html import escape as html_escape
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-untyped]

from ui_helpers import render_html


OVERVIEW_GREENS = [
    "#5B8A72",
    "#77A68C",
    "#95BAA4",
    "#ADC9B5",
    "#C6D9C9",
    "#7E9989",
    "#688A7A",
    "#89A894",
    "#B6CCBC",
    "#D4E4D5",
]


def render_overview_theme() -> None:
    is_uni_theme = str(st.session_state.get("app_theme_variant", "Sage")) == "Uni"
    overview_scope_vars = ""
    if not is_uni_theme:
        overview_scope_vars = """
        [data-testid="stAppViewContainer"]:has(.overview-page) {
            --overview-page-bg-top: #f6f4ea;
            --overview-page-bg-bottom: #e6ebdf;
            --overview-card-top: #ffffff;
            --overview-card-bottom: #eef2e8;
            --overview-card-border: rgba(84, 108, 89, 0.30);
            --overview-card-shadow: rgba(60, 80, 66, 0.18);
            --overview-panel-top: #fdfefd;
            --overview-panel-bottom: #e3eadf;
            --overview-panel-border: rgba(84, 108, 89, 0.38);
            --overview-panel-shadow: rgba(60, 80, 66, 0.20);
            --overview-soft-tint: #e7ddd5;
            --overview-strong-accent: #b08a72;
            --overview-strong-accent-2: #96725d;
            --overview-quiet-button-top: #ffffff;
            --overview-quiet-button-bottom: #f1e8e1;
        }
        """
    render_html(
        """
        <style>
        """
        + overview_scope_vars
        + """
        [data-testid="stAppViewContainer"]:has(.overview-page) {
            background:
                radial-gradient(circle at top right, rgba(110, 132, 115, 0.08), transparent 24%),
                radial-gradient(circle at top left, rgba(214, 222, 206, 0.55), transparent 26%),
                linear-gradient(180deg, var(--overview-page-bg-top, var(--app-green-bg, #f7f7f2)) 0%, var(--overview-page-bg-bottom, var(--app-green-bg-soft, #f1f3ee)) 100%);
        }
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-testid="stMain"] {
            background: transparent;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page),
        [data-testid="stAppViewBlockContainer"]:has(.overview-page),
        .block-container:has(.overview-page) {
            padding-top: 1rem !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) hr,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) hr,
        .block-container:has(.overview-page) hr {
            display: none !important;
        }
        .overview-page {
            margin: 0 0 0.35rem 0;
            padding: 0.1rem 0 0 0;
        }
        .overview-page-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.7rem;
            padding: 1rem 1.05rem;
            border: 1px solid var(--overview-card-border, var(--app-green-border, rgba(100, 113, 102, 0.12)));
            border-radius: 20px;
            background: linear-gradient(180deg, var(--overview-card-top, var(--app-green-surface, rgba(255,255,255,0.96))), var(--overview-card-bottom, var(--app-green-surface-3, rgba(244,245,240,0.96))));
            box-shadow: 0 14px 30px var(--overview-card-shadow, rgba(74, 92, 79, 0.05));
            backdrop-filter: blur(2px);
        }
        .overview-page-title {
            margin: 0;
            color: var(--app-green-text, #23372b);
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.15;
        }
        .overview-page-subtitle {
            margin: 0.3rem 0 0 0;
            max-width: 48rem;
            color: var(--app-green-muted, #5f7265);
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .overview-page-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 0.45rem;
        }
        .overview-page-chip {
            padding: 0.5rem 0.7rem;
            border-radius: 999px;
            border: 1px solid var(--overview-card-border, var(--app-green-border, rgba(100, 113, 102, 0.14)));
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface-3, rgba(246, 247, 243, 0.98))), var(--overview-soft-tint, rgba(234, 239, 232, 0.98)));
            color: var(--app-green-accent-text, #4d5f53);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            white-space: nowrap;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.72);
        }
        .overview-metric-card {
            display: block;
            min-height: 96px;
            padding: 0.8rem 0.9rem 0.78rem 0.9rem;
            border-radius: 18px;
            border: 1px solid var(--overview-card-border, var(--app-green-border, rgba(100, 113, 102, 0.12)));
            background: linear-gradient(180deg, var(--overview-card-top, var(--app-green-surface, rgba(255,255,255,0.98))), var(--overview-card-bottom, var(--app-green-surface-3, rgba(244,245,240,0.96))));
            box-shadow: 0 12px 26px var(--overview-card-shadow, rgba(74, 92, 79, 0.05));
            text-decoration: none !important;
            position: relative;
            overflow: hidden;
        }
        .overview-metric-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 4px;
            background: linear-gradient(90deg, var(--overview-strong-accent, #466852), rgba(143, 171, 151, 0.36));
        }
        .overview-metric-card.is-clickable {
            cursor: pointer;
        }
        .overview-metric-card.is-clickable:hover {
            border-color: var(--overview-panel-border, rgba(98, 122, 104, 0.22));
            box-shadow: 0 16px 30px var(--overview-panel-shadow, rgba(74, 92, 79, 0.08));
            transform: translateY(-1px);
        }
        .overview-metric-card.is-priority {
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface-3, #f3f5f0)), var(--overview-soft-tint, var(--app-green-accent-soft, #ebeee7)));
            border-color: var(--overview-panel-border, var(--app-green-border-strong, rgba(98, 122, 104, 0.18)));
        }
        .overview-metric-label {
            color: var(--app-green-muted, #647867);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .overview-metric-value {
            margin-top: 0.38rem;
            color: var(--app-green-text, #203229);
            font-size: 1.5rem;
            font-weight: 700;
            line-height: 1;
        }
        .overview-metric-note {
            margin-top: 0.42rem;
            color: var(--app-green-muted, #5f7363);
            font-size: 0.8rem;
            line-height: 1.25;
        }
        .overview-section-kicker {
            margin: 0.65rem 0 0.32rem 0.1rem;
            color: var(--app-green-muted, #627566);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }
        .overview-shortcuts-row {
            margin: 0.2rem 0 0.35rem 0;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] {
            padding: 0.22rem 0.12rem 0.08rem 0.12rem;
            border-radius: 22px;
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface-2, rgba(247,249,245,0.92))), var(--overview-soft-tint, var(--app-green-accent-soft, rgba(236,241,234,0.92))));
            border: 1px solid var(--overview-panel-border, var(--app-green-border, rgba(102, 122, 106, 0.14)));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.86), 0 14px 28px var(--overview-card-shadow, rgba(74, 92, 79, 0.05));
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
            min-height: 36px !important;
            padding: 0.42rem 0.82rem !important;
            border-radius: 999px !important;
            font-size: 0.83rem !important;
            font-weight: 750 !important;
            letter-spacing: 0.01em !important;
            transform: translateY(0) !important;
            transition: background 140ms ease, border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(180deg, var(--overview-strong-accent, var(--app-green-accent, #64896f)), var(--overview-strong-accent-2, var(--app-green-accent-strong, #4f7359))) !important;
            border: 1px solid var(--overview-strong-accent-2, var(--app-green-accent-strong, #4b6e54)) !important;
            color: #f6fbf6 !important;
            box-shadow: 0 12px 24px rgba(63, 92, 71, 0.24) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] * {
            color: #f6fbf6 !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: linear-gradient(180deg, var(--overview-strong-accent, var(--app-green-accent, #6c9176)), var(--overview-strong-accent-2, var(--app-green-accent-strong, #54795e))) !important;
            border-color: var(--overview-strong-accent-2, var(--app-green-accent-strong, #54795e)) !important;
            box-shadow: 0 14px 26px rgba(63, 92, 71, 0.28) !important;
            transform: translateY(-1px) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: linear-gradient(180deg, var(--overview-quiet-button-top, var(--app-green-surface, #ffffff)), var(--overview-quiet-button-bottom, var(--app-green-surface-3, #f4f7f1))) !important;
            border: 1px solid var(--overview-panel-border, var(--app-green-border-strong, rgba(89, 112, 95, 0.34))) !important;
            color: var(--app-green-accent-text, #33463b) !important;
            box-shadow: 0 10px 20px var(--overview-card-shadow, rgba(74, 92, 79, 0.11)) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"] * {
            color: var(--app-green-accent-text, #33463b) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface-2, #f5f9f2)), var(--overview-soft-tint, var(--app-green-hover, #e7efe4))) !important;
            border-color: var(--overview-panel-border, var(--app-green-border-strong, rgba(89, 112, 95, 0.46))) !important;
            box-shadow: 0 12px 22px var(--overview-panel-shadow, rgba(74, 92, 79, 0.15)) !important;
            transform: translateY(-1px) !important;
        }
        .overview-chart-card {
            padding: 0.9rem 0.95rem 0.75rem 0.95rem;
            border-radius: 18px;
            border: 1px solid var(--overview-panel-border, var(--app-green-border, rgba(100, 113, 102, 0.12)));
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface, rgba(255,255,255,0.98))), var(--overview-panel-bottom, var(--app-green-surface-3, rgba(244,245,240,0.96))));
            box-shadow: 0 14px 28px var(--overview-card-shadow, rgba(74, 92, 79, 0.05));
            position: relative;
            overflow: hidden;
        }
        .overview-chart-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 3px;
            background: linear-gradient(90deg, var(--overview-strong-accent, #466852), rgba(143, 171, 151, 0.28));
        }
        .overview-chart-title {
            margin: 0;
            color: var(--app-green-text, #284033);
            font-size: 0.96rem;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: 0.01em;
        }
        .overview-chart-subtitle {
            margin: 0.2rem 0 0.65rem 0;
            color: var(--app-green-muted, #637766);
            font-size: 0.8rem;
            line-height: 1.35;
        }
        .overview-table-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.85rem;
            margin: 0.8rem 0 0.45rem 0;
        }
        .overview-table-title {
            margin: 0;
            color: var(--app-green-text, #284033);
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .overview-table-subtitle {
            margin: 0.18rem 0 0 0;
            color: var(--app-green-muted, #647867);
            font-size: 0.82rem;
            line-height: 1.35;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button,
        .block-container:has(.overview-page) div[data-testid="stButton"] > button {
            border-radius: 999px !important;
            min-height: 30px !important;
            padding-top: 0.32rem !important;
            padding-bottom: 0.32rem !important;
            font-size: 0.82rem !important;
            box-shadow: none !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"],
        .block-container:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(180deg, var(--overview-strong-accent, var(--app-green-accent, #627a69)), var(--overview-strong-accent-2, var(--app-green-accent-strong, #627a69))) !important;
            border: 1px solid var(--overview-strong-accent-2, var(--app-green-accent-strong, #627a69)) !important;
            color: #f7fbf7 !important;
            box-shadow: 0 10px 20px rgba(54, 87, 66, 0.22) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"],
        .block-container:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"] {
            background: linear-gradient(180deg, var(--overview-quiet-button-top, var(--app-green-surface, #ffffff)), var(--overview-quiet-button-bottom, var(--app-green-surface-3, #f4f5f1))) !important;
            border: 1px solid var(--overview-panel-border, var(--app-green-border, rgba(100, 113, 102, 0.14))) !important;
            color: var(--app-green-accent-text, #45584b) !important;
            box-shadow: 0 8px 18px var(--overview-card-shadow, rgba(74, 92, 79, 0.09)) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button:hover,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button:hover,
        .block-container:has(.overview-page) div[data-testid="stButton"] > button:hover {
            border-color: var(--overview-strong-accent, var(--app-green-accent, #627a69)) !important;
            color: var(--app-green-accent-hover, #274231) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        .block-container:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        .block-container:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] [role="dialog"] {
            background: var(--app-green-surface, #fffefb) !important;
            color: var(--app-green-text, #21352a) !important;
            border: 1px solid var(--app-green-border, rgba(100, 113, 102, 0.16)) !important;
            box-shadow: none !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        .block-container:has(.overview-page) div[data-testid="stTextInput"] input {
            border-radius: 14px !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        .block-container:has(.overview-page) div[data-testid="stPopover"] button {
            border-radius: 14px !important;
        }
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] label,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] p,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] span,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] div {
            color: var(--app-green-text, #2a4433) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"],
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"],
        .block-container:has(.overview-page) [data-testid="stDataFrame"] > div {
            background: var(--app-green-cell-shell, #e7ebe3) !important;
            border-radius: 18px !important;
            border: 1px solid var(--app-green-border, rgba(100, 113, 102, 0.16)) !important;
            box-shadow: 0 12px 24px rgba(74, 92, 79, 0.06) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div > div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div > div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] > div > div {
            background: var(--app-green-cell, #fffef8) !important;
            border-radius: 16px !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] th,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] th,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] th {
            background: linear-gradient(180deg, var(--app-green-accent, #456a4e), var(--app-green-accent-strong, #35573f)) !important;
            color: #eef6ee !important;
            border-bottom: 1px solid var(--app-green-border, rgba(196, 220, 195, 0.18)) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] td,
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] td,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] td,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] div {
            color: var(--app-green-text, #274231) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even),
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even),
        .block-container:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even) {
            background: var(--app-green-cell-alt, #f7f8f4) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:hover,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:hover,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] tr:hover {
            background: var(--app-green-cell-hover, #eff2ec) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"],
        .block-container:has(.overview-page) [data-testid="stVegaLiteChart"] {
            padding: 0.35rem 0.65rem 0.2rem 0.5rem;
            border-radius: 0 0 18px 18px;
            background: linear-gradient(180deg, var(--overview-panel-top, var(--app-green-surface, rgba(255,255,255,0.98))), var(--overview-panel-bottom, var(--app-green-surface-3, rgba(244,245,240,0.96))));
            border: 1px solid var(--overview-panel-border, var(--app-green-border, rgba(100, 113, 102, 0.12)));
            border-top: none;
            box-shadow: 0 10px 24px var(--overview-card-shadow, rgba(74, 92, 79, 0.05));
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"] canvas,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"] canvas,
        .block-container:has(.overview-page) [data-testid="stVegaLiteChart"] canvas {
            border-radius: 12px !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) .stCaption,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .stCaption,
        .block-container:has(.overview-page) .stCaption {
            color: var(--app-green-muted, #66796b) !important;
        }
        </style>
        """
    )


def render_overview_header(scope_label: str, device_count: int, issue_count: int, view_mode: str) -> None:
    render_html(
        f"""
        <section class="overview-page">
            <div class="overview-page-header">
                <div>
                    <h1 class="overview-page-title">Health Overview</h1>
                    <p class="overview-page-subtitle">
                        Monitor camera health, spot attention hotspots, and work from a cleaner inventory view built for fast internal ops checks.
                    </p>
                </div>
                <div class="overview-page-meta">
                    <div class="overview-page-chip">Scope: {html_escape(scope_label)}</div>
                    <div class="overview-page-chip">{device_count:,} devices</div>
                    <div class="overview-page-chip">{issue_count:,} need attention</div>
                    <div class="overview-page-chip">Mode: {html_escape(view_mode.title())}</div>
                </div>
            </div>
        </section>
        """
    )


def render_overview_metric_cards(metrics: list[dict[str, Any]]) -> None:
    columns = st.columns(len(metrics), gap="small")
    for column, metric in zip(columns, metrics):
        variant = " is-priority" if metric.get("priority") else ""
        action_href = str(metric.get("href", "") or "")
        tag_name = "a" if action_href else "div"
        extra_attrs = f' href="{html_escape(action_href)}"' if action_href else ""
        if action_href:
            variant += " is-clickable"
        with column:
            render_html(
                f"""
                <{tag_name} class="overview-metric-card{variant}"{extra_attrs}>
                    <div class="overview-metric-label">{html_escape(str(metric.get("label", "")))}</div>
                    <div class="overview-metric-value">{html_escape(str(metric.get("value", "")))}</div>
                    <div class="overview-metric-note">{html_escape(str(metric.get("note", "")))}</div>
                </{tag_name}>
                """
            )


def render_overview_section_kicker(text: str) -> None:
    render_html(f'<div class="overview-section-kicker">{html_escape(text)}</div>')


def _build_overview_bar_chart(
    data: pd.Series,
    color_map: dict[str, str],
    height: int = 240,
    shade_by_value: bool = False,
):
    import altair as alt  # type: ignore[import-untyped]

    chart_df = pd.DataFrame(
        {
            "category": data.index.astype(str).tolist(),
            "value": pd.to_numeric(pd.Series(data.values), errors="coerce").fillna(0).astype(int).tolist(),
        }
    )
    chart_df = chart_df[chart_df["value"] > 0].copy()
    if chart_df.empty:
        return None
    if shade_by_value:
        is_uni_theme = str(st.session_state.get("app_theme_variant", "Sage")) == "Uni"
        ranked_df = chart_df.sort_values(["value", "category"], ascending=[False, True]).reset_index(drop=True)
        ranked_palette = (
            [
                "#1D2B46",
                "#31476F",
                "#476088",
                "#60779D",
                "#7A90B1",
                "#95A8C4",
                "#B2C0D6",
                "#D0D9E6",
            ]
            if is_uni_theme else
            [
                "#5E8A72",
                "#739A82",
                "#88AA93",
                "#9BB8A3",
                "#ADC6B2",
                "#BFD2C1",
                "#D0DECF",
                "#E0E9DF",
            ]
        )
        ranked_df["color"] = [
            ranked_palette[min(index, len(ranked_palette) - 1)]
            for index in range(len(ranked_df))
        ]
        chart_df = ranked_df
    else:
        chart_df["color"] = chart_df["category"].map(color_map).fillna("#7E9989")
    max_value = int(chart_df["value"].max())
    domain_max = max_value + max(1, int(round(max_value * 0.18)))

    bars = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusEnd=6, cornerRadiusTopRight=6, cornerRadiusBottomRight=6, size=20)
        .encode(
            y=alt.Y("category:N", sort="-x", title=None, axis=alt.Axis(labelColor="#4c6351", labelFontSize=12, ticks=False, domain=False)),
            x=alt.X(
                "value:Q",
                title=None,
                scale=alt.Scale(domain=[0, domain_max], nice=False),
                axis=alt.Axis(labelColor="#6b7f6f", labelFontSize=11, gridColor="#deeadf", domain=False, tickCount=5),
            ),
            color=alt.Color("color:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q", title="Count"),
            ],
        )
    )

    labels = (
        alt.Chart(chart_df)
        .mark_text(align="left", baseline="middle", dx=8, color="#355240", fontSize=12, fontWeight=700)
        .encode(
            y=alt.Y("category:N", sort="-x", title=None),
            x=alt.X("value:Q", scale=alt.Scale(domain=[0, domain_max], nice=False)),
            text=alt.Text("value:Q"),
        )
    )

    return (
        (bars + labels)
        .properties(height=height, padding={"left": 8, "right": 28, "top": 6, "bottom": 0})
        .configure_view(stroke=None)
        .configure(background="transparent")
    )


def render_overview_chart_card(
    title: str,
    subtitle: str,
    data: pd.Series,
    color_map: dict[str, str],
    empty_message: str,
    shade_by_value: bool = False,
) -> None:
    with st.container():
        render_html(
            f"""
            <div class="overview-chart-card">
                <h3 class="overview-chart-title">{html_escape(title)}</h3>
                <p class="overview-chart-subtitle">{html_escape(subtitle)}</p>
            </div>
            """
        )
        chart = _build_overview_bar_chart(data, color_map=color_map, shade_by_value=shade_by_value)
        if chart is None:
            st.caption(empty_message)
        else:
            st.altair_chart(chart, use_container_width=True)


def render_overview_table_header(total_rows: int, extra_text: str = "") -> None:
    meta_parts = [f"{total_rows:,} rows"]
    if extra_text:
        meta_parts.append(str(extra_text))
    meta_text = " | ".join(meta_parts)
    render_html(
        f"""
        <div class="overview-table-header">
            <div>
                <h3 class="overview-table-title">Inventory</h3>
                <p class="overview-table-subtitle">
                    Search the current scope, inspect camera records, and add or remove columns without leaving Overview. {html_escape(meta_text)}
                </p>
            </div>
        </div>
        """
    )
