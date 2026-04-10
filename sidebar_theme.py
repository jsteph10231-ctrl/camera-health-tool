from __future__ import annotations

from textwrap import dedent


def build_sidebar_theme_css(theme: dict[str, str]) -> str:
    sidebar_css_vars = "\n".join(
        [
            f'--app-sidebar-bg-top: {theme["sidebar_bg_top"]};',
            f'--app-sidebar-bg-bottom: {theme["sidebar_bg_bottom"]};',
            f'--app-sidebar-hover: {theme["sidebar_hover"]};',
            f'--app-sidebar-selected: {theme["sidebar_selected"]};',
            f'--app-sidebar-button-top: {theme["sidebar_button_top"]};',
            f'--app-sidebar-button-bottom: {theme["sidebar_button_bottom"]};',
            f'--app-sidebar-button-border: {theme["sidebar_button_border"]};',
            f'--app-sidebar-button-text: {theme["sidebar_button_text"]};',
            f'--app-sidebar-button-hover-top: {theme["sidebar_button_hover_top"]};',
            f'--app-sidebar-button-hover-bottom: {theme["sidebar_button_hover_bottom"]};',
            f'--app-sidebar-text: {theme["sidebar_text"]};',
            f'--app-sidebar-text-muted: {theme["sidebar_text_muted"]};',
            f'--app-sidebar-accent: {theme["sidebar_accent"]};',
            f'--app-sidebar-accent-strong: {theme["sidebar_accent_strong"]};',
            f'--app-sidebar-panel-top: {theme["sidebar_panel_top"]};',
            f'--app-sidebar-panel-bottom: {theme["sidebar_panel_bottom"]};',
            f'--app-sidebar-panel-border: {theme["sidebar_panel_border"]};',
            f'--app-sidebar-shadow: {theme["sidebar_shadow"]};',
            f'--app-sidebar-shadow-strong: {theme["sidebar_shadow_strong"]};',
            f'--app-sidebar-overlay-top: {theme["sidebar_overlay_top"]};',
            f'--app-sidebar-overlay-bottom: {theme["sidebar_overlay_bottom"]};',
        ]
    )
    return dedent(
        f"""
        <style>
        :root {{
        {sidebar_css_vars}
        }}

        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {{
            position: relative !important;
            background: linear-gradient(180deg, var(--app-sidebar-bg-top) 0%, var(--app-sidebar-bg-bottom) 100%) !important;
            border-right: 1px solid var(--app-sidebar-panel-border) !important;
            box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.62), 10px 0 24px var(--app-sidebar-shadow) !important;
        }}

        section[data-testid="stSidebar"]::before,
        [data-testid="stSidebar"]::before,
        [data-testid="stSidebarContent"]::before {{
            content: "" !important;
            position: absolute !important;
            inset: 0 !important;
            background: linear-gradient(180deg, var(--app-sidebar-overlay-top) 0%, var(--app-sidebar-overlay-bottom) 100%) !important;
            pointer-events: none !important;
            z-index: 0 !important;
        }}

        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"] > div:first-child > div:first-child {{
            position: relative !important;
            z-index: 1 !important;
            background: linear-gradient(180deg, var(--app-sidebar-bg-top) 0%, var(--app-sidebar-bg-bottom) 100%) !important;
        }}

        [data-testid="stSidebarContent"] {{
            border-right: 1px solid var(--app-sidebar-panel-border) !important;
            box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.48) !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] {{
            background: transparent !important;
            position: relative !important;
            z-index: 1 !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] {{
            gap: 0.08rem !important;
            padding: 0.42rem !important;
            border-radius: 12px !important;
            background: rgba(217, 225, 230, 0.72) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.55) !important;
            margin: 0.25rem 0 0.95rem 0 !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label {{
            margin: 0 !important;
            padding: 0.52rem 0.8rem !important;
            border-radius: 10px !important;
            border: 1px solid transparent !important;
            background: transparent !important;
            box-shadow: none !important;
            transition: background 140ms ease, border-color 140ms ease, box-shadow 140ms ease !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            cursor: pointer !important;
        }}

        /* Hide native radio circle and its container */
        [data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {{
            display: none !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {{
            background: rgba(255,255,255,0.34) !important;
            border-color: transparent !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label[data-checked="true"] {{
            background: #ffffff !important;
            border-color: rgba(148, 163, 184, 0.18) !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
            outline: none !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label p {{
            color: #4b5563 !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            width: 100% !important;
            line-height: 1.15 !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label[data-checked="true"] p,
        [data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {{
            color: #0f4f73 !important;
        }}

        .workspace-button-group-marker {{
            display: block !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            line-height: 0 !important;
            font-size: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(.workspace-button-group-marker),
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(.workspace-button-group-marker) {{
            gap: 0.01rem !important;
            padding: 0.12rem !important;
            border-radius: 10px !important;
            background: #D9E1E6 !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.4), 0 2px 8px rgba(15, 23, 42, 0.03) !important;
            margin: 0 0 0.95rem 0 !important;
            border: 1px solid rgba(101, 122, 132, 0.14) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(.workspace-button-group-marker) > div,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(.workspace-button-group-marker) > div[data-testid="stButton"] {{
            margin: 0 0 0.12rem 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(.workspace-button-group-marker) > div:last-child,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(.workspace-button-group-marker) > div[data-testid="stButton"]:last-child {{
            margin-bottom: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(.workspace-button-group-marker) .stButton > button,
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(.workspace-button-group-marker) .stButton > button {{
            min-height: 38px !important;
            padding-top: 0.52rem !important;
            padding-bottom: 0.52rem !important;
            border-radius: 12px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stIconMaterial"],
        [data-testid="stSidebar"] .material-symbols-rounded,
        [data-testid="stSidebar"] .material-symbols-outlined,
        [data-testid="stSidebar"] .material-icons,
        section[data-testid="stSidebar"] [data-testid="stIconMaterial"],
        section[data-testid="stSidebar"] .material-symbols-rounded,
        section[data-testid="stSidebar"] .material-symbols-outlined,
        section[data-testid="stSidebar"] .material-icons {{
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
        }}

        [data-testid="stSidebar"] [role="radiogroup"] > label [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] .stCaption {{
            color: var(--app-sidebar-text-muted) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: var(--app-sidebar-text) !important;
        }}

        [data-testid="stSidebar"] input[type="radio"],
        [data-testid="stSidebar"] input[type="radio"] + div,
        [data-testid="stSidebar"] [role="radiogroup"] svg {{
            accent-color: var(--app-sidebar-accent) !important;
            color: var(--app-sidebar-accent) !important;
            fill: var(--app-sidebar-accent) !important;
            stroke: var(--app-sidebar-accent) !important;
        }}

        [data-testid="stSidebar"] .stButton > button {{
            background: rgba(255, 255, 255, 0.72) !important;
            color: #546E7A !important;
            border: none !important;
            border-radius: 12px !important;
            min-height: 44px !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 0.75rem !important;
            padding: 0.78rem 1rem !important;
            text-align: left !important;
            transition: background 140ms ease, color 140ms ease, box-shadow 140ms ease, transform 140ms ease !important;
        }}

        [data-testid="stSidebar"] .stButton > button *,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] button * {{
            color: #546E7A !important;
        }}

        [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] > p,
        [data-testid="stSidebar"] .stButton > button p {{
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            width: 100% !important;
            margin: 0 !important;
            font-weight: 600 !important;
            line-height: 1.15 !important;
        }}

        [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] span.material-symbols-rounded,
        [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] span.material-symbols-outlined,
        [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] span.material-icons {{
            font-size: 20px !important;
            width: 20px !important;
            min-width: 20px !important;
            height: 20px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #546E7A !important;
            fill: #546E7A !important;
            stroke: #546E7A !important;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            background: #F8FAFC !important;
            color: #546E7A !important;
            border-color: transparent !important;
            box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08) !important;
            transform: translateY(-1px) !important;
        }}

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: #FFFFFF !important;
            color: #546E7A !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1) !important;
            font-weight: 700 !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding-left: 1rem !important;
        }}

        [data-testid="stSidebar"] .stButton > button[kind="primary"] * {{
            color: #546E7A !important;
        }}

        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background: rgba(255, 255, 255, 0.5) !important;
            color: #546E7A !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05) !important;
            justify-content: flex-start !important;
            text-align: left !important;
            font-weight: 600 !important;
            padding-left: 1rem !important;
        }}

        [data-testid="stSidebar"] .stButton > button[kind="secondary"] * {{
            color: #546E7A !important;
        }}

        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background: rgba(248, 250, 252, 0.96) !important;
            border-color: transparent !important;
            box-shadow: 0 6px 14px rgba(15, 23, 42, 0.07) !important;
        }}

        [data-testid="stSidebar"] .stButton > button:hover * {{
            color: var(--app-sidebar-button-text) !important;
        }}

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {{
            background: #dfe7ee !important;
            color: var(--app-sidebar-text) !important;
            border: 1px solid rgba(148, 163, 184, 0.10) !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {{
            color: var(--app-green-placeholder) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploader"] *,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] [class*="uploadDropzone"] {{
            background: transparent !important;
            color: var(--app-sidebar-text) !important;
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
            padding: 0.1rem 0 !important;
            line-height: 1.25 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] [class*="uploadDropzone"] {{
            border-radius: 12px !important;
            border-style: dashed !important;
            border-width: 1.5px !important;
            border-color: rgba(148, 163, 184, 0.34) !important;
            min-height: 92px !important;
        }}

        [data-testid="stSidebar"] [data-testid="stFileUploader"] button {{
            background: #ffffff !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            color: var(--app-sidebar-button-text) !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebar"] hr {{
            margin: 0.8rem 0 !important;
            border-color: rgba(148, 163, 184, 0.18) !important;
        }}

        .sidebar-brand-card,
        .sidebar-surface-card,
        .sidebar-upload-card,
        .sidebar-bottom-shell {{
            border-radius: 12px;
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,251,0.96));
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
        }}

        .sidebar-brand-card {{
            padding: 0.7rem 0.2rem 0.34rem 0.1rem;
            margin: 0.05rem 0 0.3rem 0;
            background: transparent;
            box-shadow: none;
        }}

        .sidebar-brand-row {{
            display: flex;
            align-items: center;
            gap: 0.95rem;
        }}

        .sidebar-brand-icon {{
            width: 2.2rem;
            height: 2.2rem;
            min-width: 2.2rem;
            border-radius: 0.7rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(180deg, #357E9B, #2E708B);
            box-shadow: 0 6px 14px rgba(53, 126, 155, 0.16);
        }}

        .sidebar-brand-icon svg {{
            font-size: 1.15rem !important;
            width: 1.15rem !important;
            height: 1.15rem !important;
            display: block !important;
            overflow: visible;
        }}

        .sidebar-brand-icon svg * {{
            stroke: #ffffff;
            stroke-width: 1.8;
            stroke-linecap: round;
            stroke-linejoin: round;
            fill: none;
        }}

        .sidebar-brand-title {{
            color: #2f738e;
            font-size: 1.42rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.02;
            margin: 0;
            font-family: Inter, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }}

        .sidebar-brand-subtitle {{
            color: #51606a;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            line-height: 1.05;
            margin-top: 0.42rem;
            font-family: Inter, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        }}

        .sidebar-section-label {{
            color: #475569;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin: 1.2rem 0 0.42rem 0.08rem;
        }}

        .sidebar-muted-copy {{
            color: var(--app-sidebar-text-muted);
            font-size: 0.78rem;
            line-height: 1.45;
            margin: 0.12rem 0 0.55rem 0.08rem;
        }}

        .sidebar-source-note {{
            color: var(--app-sidebar-text-muted);
            font-size: 0.76rem;
            line-height: 1.45;
            padding: 0.7rem 0.8rem;
            margin: 0.35rem 0 0.2rem 0;
        }}

        .sidebar-bottom-shell {{
            padding: 0.78rem 0.78rem 0.82rem 0.78rem;
            margin-top: 1.35rem;
            box-shadow: none;
            background: transparent;
        }}

        .sidebar-bottom-meta {{
            margin-bottom: 0.55rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(148, 163, 184, 0.18);
        }}

        [data-testid="stSidebar"] .stDownloadButton > button {{
            background: #2f7289 !important;
            color: #ffffff !important;
            border: 1px solid #2f7289 !important;
            border-radius: 999px !important;
            min-height: 40px !important;
            box-shadow: none !important;
            font-weight: 700 !important;
        }}

        [data-testid="stSidebar"] .stDownloadButton > button * {{
            color: #ffffff !important;
        }}

        [data-testid="stSidebar"] .stDownloadButton > button:hover {{
            background: #29667a !important;
            border-color: #29667a !important;
        }}
        </style>
        """
    )
