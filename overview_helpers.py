from __future__ import annotations

from html import escape as html_escape
from typing import Any

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st  # type: ignore[import-untyped]

from ui_helpers import render_html


OVERVIEW_GREENS = [
    "#546E7A",
    "#668392",
    "#7897A6",
    "#8AAAB5",
    "#9DBDC4",
    "#B1CDD2",
    "#C2DBDE",
    "#D1E5E7",
    "#DFECEC",
    "#ECF4F3",
]


def render_overview_theme() -> None:
    overview_scope_vars = """
        [data-testid="stAppViewContainer"]:has(.overview-page) {
            --overview-font-stack: Inter, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            --overview-page-bg-top: #f8fafc;
            --overview-page-bg-mid: #f3f7fa;
            --overview-page-bg-bottom: #eef3f7;
            --overview-page-radial-a: rgba(84, 110, 122, 0.08);
            --overview-page-radial-b: rgba(214, 226, 233, 0.64);
            --overview-page-radial-c: rgba(225, 233, 239, 0.46);
            --overview-surface: #ffffff;
            --overview-surface-soft: #f8fafc;
            --overview-surface-tint: #f1f5f9;
            --overview-surface-nest: #e6edf2;
            --overview-card-shadow: rgba(15, 23, 42, 0.06);
            --overview-card-shadow-strong: rgba(15, 23, 42, 0.10);
            --overview-stroke: rgba(148, 163, 184, 0.14);
            --overview-stroke-strong: rgba(84, 110, 122, 0.22);
            --overview-title: #1e293b;
            --overview-text: #334155;
            --overview-muted: #64748b;
            --overview-accent: #546e7a;
            --overview-accent-strong: #3f5966;
            --overview-accent-soft: #d9e4ea;
            --overview-calm-cyan: #0f766e;
            --overview-live: #0d9488;
            --overview-attention: #e11d48;
            --overview-attention-soft: #fde8ee;
            --overview-warning: #d97706;
            --overview-warning-soft: #fff3e4;
            --overview-track: #e2e8f0;
            --overview-quiet-button-top: #ffffff;
            --overview-quiet-button-bottom: #f8fafc;
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
                radial-gradient(circle at top right, var(--overview-page-radial-a), transparent 26%),
                radial-gradient(circle at top left, var(--overview-page-radial-b), transparent 28%),
                radial-gradient(circle at bottom center, var(--overview-page-radial-c), transparent 42%),
                linear-gradient(180deg, var(--overview-page-bg-top) 0%, var(--overview-page-bg-mid) 54%, var(--overview-page-bg-bottom) 100%);
            background-attachment: fixed !important;
            min-height: 100vh !important;
        }
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-testid="stMain"] {
            background: transparent;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page),
        [data-testid="stMainBlockContainer"]:has(.overview-page) *,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page),
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) *,
        .block-container:has(.overview-page),
        .block-container:has(.overview-page) * {
            font-family: var(--overview-font-stack);
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stIconMaterial"],
        [data-testid="stMainBlockContainer"]:has(.overview-page) .material-symbols-rounded,
        [data-testid="stMainBlockContainer"]:has(.overview-page) .material-symbols-outlined,
        [data-testid="stMainBlockContainer"]:has(.overview-page) .material-icons,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stIconMaterial"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .material-symbols-rounded,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .material-symbols-outlined,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .material-icons,
        .block-container:has(.overview-page) [data-testid="stIconMaterial"],
        .block-container:has(.overview-page) .material-symbols-rounded,
        .block-container:has(.overview-page) .material-symbols-outlined,
        .block-container:has(.overview-page) .material-icons {
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
            font-weight: normal !important;
            font-style: normal !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            line-height: 1 !important;
            -webkit-font-smoothing: antialiased !important;
            font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page),
        [data-testid="stAppViewBlockContainer"]:has(.overview-page),
        .block-container:has(.overview-page) {
            padding-top: 1.05rem !important;
            padding-bottom: 4.5rem !important;
            min-height: calc(100vh - 4rem) !important;
            background: transparent !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) hr,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) hr,
        .block-container:has(.overview-page) hr {
            display: none !important;
        }
        .overview-page {
            margin: 0 0 0.5rem 0;
            padding: 0.1rem 0 0 0;
        }
        .overview-page-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1.2rem;
            margin-bottom: 1rem;
            padding: 1.35rem 1.35rem 1.2rem 1.35rem;
            border-radius: 20px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.95));
            box-shadow: 0 10px 28px var(--overview-card-shadow);
        }
        .overview-page-title {
            margin: 0;
            color: var(--overview-title);
            font-size: 1.78rem;
            font-weight: 750;
            line-height: 1.08;
            letter-spacing: -0.025em;
        }
        .overview-page-meta {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 0.5rem;
        }
        .overview-page-chip {
            padding: 0.56rem 0.82rem;
            border-radius: 999px;
            background: linear-gradient(180deg, var(--overview-surface), var(--overview-surface-soft));
            color: var(--overview-text);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            white-space: nowrap;
            box-shadow: inset 0 0 0 1px var(--overview-stroke), 0 4px 14px rgba(15, 23, 42, 0.04);
        }
        .overview-page-chip.is-live {
            background: rgba(13, 148, 136, 0.10);
            color: #0f766e;
            box-shadow: none;
        }
        .overview-page-chip.is-cluster {
            background: rgba(84, 110, 122, 0.10);
            color: var(--overview-accent-strong);
            box-shadow: none;
        }
        .overview-metric-card {
            display: block;
            min-height: 118px;
            padding: 1rem 1.02rem 0.95rem 1.02rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));
            box-shadow: 0 10px 28px var(--overview-card-shadow);
            text-decoration: none !important;
            position: relative;
            overflow: hidden;
        }
        .overview-metric-card::before {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, var(--overview-accent-soft), rgba(148, 163, 184, 0));
        }
        .overview-metric-card.is-clickable {
            cursor: pointer;
        }
        .overview-metric-card.is-clickable:hover {
            box-shadow: 0 14px 32px var(--overview-card-shadow-strong);
            transform: translateY(-1px);
        }
        .overview-metric-card.is-priority {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(244,248,251,0.98));
        }
        .overview-metric-card.is-priority::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(224, 122, 95, 0.07), rgba(62, 160, 183, 0.02) 62%);
            pointer-events: none;
        }
        .overview-metric-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            position: relative;
            z-index: 1;
        }
        .overview-metric-label {
            color: var(--overview-muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .overview-metric-status {
            display: inline-flex;
            align-items: center;
            gap: 0.38rem;
            color: var(--overview-muted);
            font-size: 0.72rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .overview-metric-status-dot {
            width: 0.52rem;
            height: 0.52rem;
            border-radius: 999px;
            background: var(--overview-track);
            box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.08);
            flex: 0 0 auto;
        }
        .overview-metric-status.is-live .overview-metric-status-dot {
            background: var(--overview-live);
            box-shadow: 0 0 0 4px rgba(31, 157, 143, 0.12);
        }
        .overview-metric-status.is-attention .overview-metric-status-dot {
            background: var(--overview-attention);
            box-shadow: 0 0 0 4px rgba(224, 122, 95, 0.12);
        }
        .overview-metric-status.is-neutral .overview-metric-status-dot {
            background: var(--overview-accent);
            box-shadow: 0 0 0 4px rgba(84, 110, 122, 0.10);
        }
        .overview-metric-value {
            margin-top: 0.9rem;
            color: var(--overview-title);
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.03em;
        }
        .overview-metric-bottomline {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 0.8rem;
            margin-top: 0.82rem;
        }
        .overview-metric-note {
            color: var(--overview-muted);
            font-size: 0.8rem;
            line-height: 1.25;
            max-width: 14rem;
        }
        .overview-metric-trend {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.3rem 0.52rem;
            border-radius: 999px;
            background: var(--overview-surface-tint);
            color: var(--overview-accent-strong);
            font-size: 0.74rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .overview-metric-trend.is-live {
            background: rgba(31, 157, 143, 0.10);
            color: #18786d;
        }
        .overview-metric-trend.is-attention {
            background: var(--overview-attention-soft);
            color: #a55d48;
        }
        .overview-section-kicker {
            margin: 0.18rem 0 0.12rem 0.1rem;
            color: var(--overview-muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }
        .overview-shortcuts-row {
            margin: 0 0 0.08rem 0;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0.06rem !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] {
            padding: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] + div[data-testid="stHorizontalBlock"] {
            margin-top: 0 !important;
            margin-bottom: 0.06rem !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
            min-height: 44px !important;
            padding: 0.78rem 1rem !important;
            border-radius: 12px !important;
            font-size: 0.83rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            transform: translateY(0) !important;
            transition: background 140ms ease, border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stMainBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"],
        .block-container:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(180deg, #4588a3, #367c98) !important;
            border: none !important;
            color: #ffffff !important;
            box-shadow: 0 6px 14px rgba(53, 126, 155, 0.16) !important;
            font-weight: 700 !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] *,
        [data-testid="stMainBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] *,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] *,
        .block-container:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"] * {
            color: #ffffff !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"]:hover,
        [data-testid="stMainBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"]:hover,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"]:hover,
        .block-container:has(.overview-page) .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="primary"]:hover {
            background: linear-gradient(180deg, #4b8ea8, #3b819d) !important;
            border-color: transparent !important;
            box-shadow: 0 6px 14px rgba(53, 126, 155, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"] {
            background: #FFFFFF !important;
            border: 1px solid rgba(101, 122, 132, 0.18) !important;
            color: #546E7A !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"] * {
            color: #546E7A !important;
        }
        .overview-shortcuts-row + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background: #F8FAFC !important;
            border-color: transparent !important;
            box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08) !important;
            transform: translateY(-1px) !important;
        }
        .overview-chart-card {
            padding: 1rem 1.02rem 0.75rem 1.02rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.96));
            box-shadow: 0 10px 28px var(--overview-card-shadow);
            position: relative;
            overflow: hidden;
        }
        .overview-chart-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 1px;
            background: linear-gradient(90deg, var(--overview-accent-soft), rgba(148, 163, 184, 0));
        }
        .overview-chart-title {
            margin: 0;
            color: var(--overview-title);
            font-size: 0.96rem;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }
        .overview-chart-subtitle {
            margin: 0.24rem 0 0.72rem 0;
            color: var(--overview-muted);
            font-size: 0.8rem;
            line-height: 1.45;
        }
        .overview-chart-shell [data-testid="stVegaLiteChart"] {
            padding: 0.2rem 0.1rem 0 0.1rem;
        }
        .overview-chart-shell [data-testid="stVegaLiteChart"] > div {
            background: transparent !important;
        }
        .overview-chart-empty {
            margin: 0.35rem 0 0.2rem 0.1rem;
            color: var(--overview-muted) !important;
        }
        .overview-table-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.85rem;
            margin: 0.14rem 0 0.24rem 0;
        }
        .overview-table-title {
            margin: 0;
            color: var(--overview-title);
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .overview-table-subtitle {
            margin: 0.18rem 0 0 0;
            color: var(--overview-muted);
            font-size: 0.82rem;
            line-height: 1.45;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button,
        .block-container:has(.overview-page) div[data-testid="stButton"] > button {
            border-radius: 12px !important;
            min-height: 44px !important;
            padding-top: 0.78rem !important;
            padding-bottom: 0.78rem !important;
            font-size: 0.83rem !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"],
        .block-container:has(.overview-page) div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(180deg, #4588a3, #367c98) !important;
            border: none !important;
            color: #ffffff !important;
            box-shadow: 0 6px 14px rgba(53, 126, 155, 0.16) !important;
            font-weight: 700 !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"],
        .block-container:has(.overview-page) div[data-testid="stButton"] > button[kind="secondary"] {
            background: #FFFFFF !important;
            border: 1px solid rgba(101, 122, 132, 0.18) !important;
            color: #546E7A !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
            font-weight: 600 !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button:hover,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stButton"] > button:hover,
        .block-container:has(.overview-page) div[data-testid="stButton"] > button:hover {
            background: #F8FAFC !important;
            border-color: transparent !important;
            color: #546E7A !important;
            box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        .block-container:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        .block-container:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] [role="dialog"] {
            background: var(--overview-surface) !important;
            color: var(--overview-title) !important;
            border: 1px solid rgba(148, 163, 184, 0.20) !important;
            box-shadow: 0 14px 32px rgba(15, 23, 42, 0.10) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stTextInput"] input,
        .block-container:has(.overview-page) div[data-testid="stTextInput"] input {
            border-radius: 14px !important;
            min-height: 42px !important;
            padding-left: 0.95rem !important;
            background: linear-gradient(180deg, var(--overview-surface), var(--overview-surface-soft)) !important;
            color: var(--overview-title) !important;
            border: 1px solid rgba(84, 110, 122, 0.26) !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.8), 0 8px 18px rgba(15, 23, 42, 0.05) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) div[data-testid="stPopover"] button,
        .block-container:has(.overview-page) div[data-testid="stPopover"] button {
            border-radius: 14px !important;
            min-height: 42px !important;
            background: linear-gradient(180deg, var(--overview-surface), var(--overview-surface-soft)) !important;
            border: 1px solid rgba(148, 163, 184, 0.20) !important;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05) !important;
        }
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] label,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] p,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] span,
        [data-testid="stAppViewContainer"]:has(.overview-page) [data-baseweb="popover"] div {
            color: var(--overview-title) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"],
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"],
        .block-container:has(.overview-page) [data-testid="stDataFrame"] > div {
            background: linear-gradient(180deg, var(--overview-surface), var(--overview-surface-soft)) !important;
            border-radius: 20px !important;
            border: none !important;
            box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div > div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] > div > div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] > div > div {
            background: linear-gradient(180deg, var(--overview-surface), #fbfdff) !important;
            border-radius: 16px !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] th,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] th,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] th {
            background: linear-gradient(180deg, #607b88, var(--overview-accent-strong)) !important;
            color: #f8fafc !important;
            border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] td,
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] div,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] td,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] div,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] td,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] div {
            color: var(--overview-text) !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even),
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even),
        .block-container:has(.overview-page) [data-testid="stDataFrame"] tr:nth-child(even) {
            background: #f8fafc !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:hover,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stDataFrame"] tr:hover,
        .block-container:has(.overview-page) [data-testid="stDataFrame"] tr:hover {
            background: #f1f5f9 !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"],
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"],
        .block-container:has(.overview-page) [data-testid="stVegaLiteChart"] {
            padding: 0.15rem 0.2rem 0 0.15rem;
            border-radius: 0 0 18px 18px;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"] canvas,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) [data-testid="stVegaLiteChart"] canvas,
        .block-container:has(.overview-page) [data-testid="stVegaLiteChart"] canvas {
            border-radius: 12px !important;
        }
        [data-testid="stMainBlockContainer"]:has(.overview-page) .stCaption,
        [data-testid="stAppViewBlockContainer"]:has(.overview-page) .stCaption,
        .block-container:has(.overview-page) .stCaption {
            color: var(--overview-muted) !important;
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
                    <h1 class="overview-page-title">System Pulse</h1>
                </div>
                <div class="overview-page-meta">
                    <div class="overview-page-chip is-live">Live Telemetry</div>
                    <div class="overview-page-chip is-cluster">Cluster: US-East-1</div>
                    <div class="overview-page-chip">Scope: {html_escape(scope_label)}</div>
                    <div class="overview-page-chip">{device_count:,} active nodes</div>
                    <div class="overview-page-chip">{issue_count:,} flagged events</div>
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
        extra_attrs = f' href="{html_escape(action_href)}" target="_top"' if action_href else ""
        if action_href:
            variant += " is-clickable"
        status_label = str(metric.get("status_label", "") or "")
        status_tone = str(metric.get("status_tone", "neutral") or "neutral")
        status_markup = ""
        if status_label:
            status_markup = (
                f'<div class="overview-metric-status is-{html_escape(status_tone)}">'
                '<span class="overview-metric-status-dot"></span>'
                f"<span>{html_escape(status_label)}</span>"
                "</div>"
            )
        trend_text = str(metric.get("trend", "") or "")
        trend_tone = str(metric.get("trend_tone", "neutral") or "neutral")
        trend_markup = ""
        if trend_text:
            trend_markup = (
                f'<div class="overview-metric-trend is-{html_escape(trend_tone)}">'
                f"{html_escape(trend_text)}"
                "</div>"
            )
        with column:
            render_html(
                f"""
                <{tag_name} class="overview-metric-card{variant}"{extra_attrs}>
                    <div class="overview-metric-topline">
                        <div class="overview-metric-label">{html_escape(str(metric.get("label", "")))}</div>
                        {status_markup}
                    </div>
                    <div class="overview-metric-value">{html_escape(str(metric.get("value", "")))}</div>
                    <div class="overview-metric-bottomline">
                        <div class="overview-metric-note">{html_escape(str(metric.get("note", "")))}</div>
                        {trend_markup}
                    </div>
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

    axis_label = "#475569"
    axis_tick = "#64748b"
    grid_color = "#dde6e8"
    value_label = "#1e293b"
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
        ranked_df = chart_df.sort_values(["value", "category"], ascending=[False, True]).reset_index(drop=True)
        ranked_palette = [
            "#546E7A",
            "#668392",
            "#7897A6",
            "#8AAAB5",
            "#9DBDC4",
            "#B1CDD2",
            "#C7D9DC",
            "#DEE9EA",
        ]
        ranked_df["color"] = [
            ranked_palette[min(index, len(ranked_palette) - 1)]
            for index in range(len(ranked_df))
        ]
        chart_df = ranked_df
    else:
        chart_df["color"] = chart_df["category"].map(color_map).fillna("#7897A6")
    max_value = int(chart_df["value"].max())
    domain_max = max_value + max(1, int(round(max_value * 0.18)))

    bars = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusEnd=7, cornerRadiusTopRight=7, cornerRadiusBottomRight=7, size=20)
        .encode(
            y=alt.Y("category:N", sort="-x", title=None, axis=alt.Axis(labelColor=axis_label, labelFontSize=12, ticks=False, domain=False)),
            x=alt.X(
                "value:Q",
                title=None,
                scale=alt.Scale(domain=[0, domain_max], nice=False),
                axis=alt.Axis(labelColor=axis_tick, labelFontSize=11, gridColor=grid_color, domain=False, tickCount=5),
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
        .mark_text(align="left", baseline="middle", dx=8, color=value_label, fontSize=12, fontWeight=700)
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


def _build_overview_donut_chart(data: pd.Series, color_map: dict[str, str], height: int = 240):
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
    chart_df["color"] = chart_df["category"].map(color_map).fillna("#94a3b8")
    chart_df["label"] = chart_df["category"] + ": " + chart_df["value"].astype(str)

    arc = (
        alt.Chart(chart_df)
        .mark_arc(innerRadius=58, outerRadius=88, cornerRadius=6)
        .encode(
            theta=alt.Theta("value:Q"),
            color=alt.Color("color:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("value:Q", title="Count"),
            ],
        )
    )

    legend = (
        alt.Chart(chart_df)
        .mark_text(align="left", baseline="middle", dx=18, fontSize=12, fontWeight=600, color="#475569")
        .encode(
            y=alt.Y("category:N", axis=None, sort=None),
            text=alt.Text("label:N"),
        )
    )

    legend_dots = (
        alt.Chart(chart_df)
        .mark_circle(size=130)
        .encode(
            y=alt.Y("category:N", axis=None, sort=None),
            color=alt.Color("color:N", scale=None, legend=None),
        )
    )

    donut = arc.properties(width=220, height=height)
    legend_group = (legend_dots + legend).properties(width=180, height=height)
    return (
        alt.hconcat(donut, legend_group, spacing=18)
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
    chart_kind: str = "bar",
) -> None:
    with st.container():
        render_html(
            f"""
            <div class="overview-chart-card overview-chart-shell">
                <h3 class="overview-chart-title">{html_escape(title)}</h3>
                <p class="overview-chart-subtitle">{html_escape(subtitle)}</p>
            </div>
            """
        )
        if chart_kind == "donut":
            chart = _build_overview_donut_chart(data, color_map=color_map)
        else:
            chart = _build_overview_bar_chart(data, color_map=color_map, shade_by_value=shade_by_value)
        if chart is None:
            render_html(f'<div class="overview-chart-empty">{html_escape(empty_message)}</div>')
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
