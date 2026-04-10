from __future__ import annotations

import textwrap

import streamlit as st  # type: ignore[import-untyped]


def render_html(markup: str) -> None:
    cleaned_markup = textwrap.dedent(markup).strip()
    if hasattr(st, "html"):
        st.html(cleaned_markup)
        return
    st.markdown(cleaned_markup, unsafe_allow_html=True)


def render_health_section_intro(title: str, subtitle: str, eyebrow: str = "Health Status") -> None:
    render_html(
        f"""
        <style>
        .health-intro-card {{
            margin: 0.02rem 0 0.32rem 0;
            padding: 0.05rem 0 0.18rem 0;
            border: none;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
        }}
        .health-intro-title {{
            color: #1e293b;
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.18;
            margin-bottom: 0;
            letter-spacing: -0.02em;
        }}
        </style>
        <div class="health-intro-card">
            <div class="health-intro-title">{title}</div>
        </div>
        """
    )
