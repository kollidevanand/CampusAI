import streamlit as st
import streamlit.components.v1 as components
from rag_engine import RAGEngine
from auth import signup_user, login_user
from chat_storage import get_user_chats, save_user_chats
import uuid
import time
import json

try:
    from auth import change_password_user
except ImportError:
    change_password_user = None

try:
    from auth import delete_user_account
except ImportError:
    delete_user_account = None


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE INIT
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "Devanand Kolli"
if "user_email" not in st.session_state:
    st.session_state.user_email = "devanand@gmail.com"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "settings" not in st.session_state:
    st.session_state.settings = {
        "theme": "dark",
        "font_size": "medium",
        "response_style": "detailed"
    }
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "current_view" not in st.session_state:
    st.session_state.current_view = "chat"  # chat | help | settings_general | settings_personalization | settings_profile | settings_data_privacy | settings_account
if "settings_nav_expanded" not in st.session_state:
    st.session_state.settings_nav_expanded = False
if "recents_nav_expanded" not in st.session_state:
    st.session_state.recents_nav_expanded = True
if "confirm_clear_chat" not in st.session_state:
    st.session_state.confirm_clear_chat = False
if "confirm_delete_account" not in st.session_state:
    st.session_state.confirm_delete_account = False
if "profile_menu_open" not in st.session_state:
    st.session_state.profile_menu_open = False

if "personalization" not in st.session_state:
    st.session_state.personalization = {
        "enabled": False,
        "nickname": "",
        "about_you": "",
        "department": "Computer Science",
        "year": "1st Year"
    }


# ============================================================
# THEME HELPERS
# ============================================================
def get_theme_colors():
    if st.session_state.settings["theme"] == "light":
        return {
            "bg": "#f5f5f5",
            "text": "#111111",
            "card_bg": "rgba(255,255,255,0.9)",
            "border": "#dddddd",
            "input_bg": "#ffffff",
            "muted": "#666666",
            "sidebar_hover": "#e5e5e5",
        }
    return {
        "bg": "#0d1117",
        "text": "#ffffff",
        "card_bg": "rgba(23,23,23,0.88)",
        "border": "#2a2a2a",
        "input_bg": "rgba(38,38,38,0.9)",
        "muted": "#999999",
        "sidebar_hover": "#1c1c1c",
    }


def get_font_size():
    return {"small": "14px", "medium": "16px", "large": "18px"}[
        st.session_state.settings["font_size"]
    ]


# ============================================================
# AUTH PAGE CSS
# ============================================================
def show_auth_css():
    colors = get_theme_colors()
    st.markdown(f"""
        <style>
        html {{ font-size: {get_font_size()}; }}
        .stApp {{ background-color: {colors['bg']}; }}

        #MainMenu {{ visibility: hidden !important; }}
        footer {{ visibility: hidden !important; }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            height: 0px !important;
            visibility: hidden !important;
        }}
        div[data-testid="stToolbar"] {{ display: none !important; }}
        div[data-testid="stDecoration"] {{ display: none !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        .stAppDeployButton {{ display: none !important; }}

        .block-container {{
            padding-top: 1rem !important;
        }}

        .cube-bg-wrapper {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 0;
            pointer-events: none;
        }}
        .cube-scene {{
            width: 340px;
            height: 340px;
            perspective: 1200px;
            opacity: 0.35;
        }}
        .cube {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            animation: rotateCube 40s infinite linear;
        }}
        .cube-face {{
            position: absolute;
            width: 340px;
            height: 340px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 100px;
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            background: linear-gradient(135deg, #1d4ed8aa, #0d0d0d);
            box-shadow: 0 0 60px rgba(37, 99, 235, 0.3);
        }}
        .face-front  {{ transform: translateZ(170px); }}
        .face-back   {{ transform: rotateY(180deg) translateZ(170px); }}
        .face-right  {{ transform: rotateY(90deg) translateZ(170px); }}
        .face-left   {{ transform: rotateY(-90deg) translateZ(170px); }}
        .face-top    {{ transform: rotateX(90deg) translateZ(170px); }}
        .face-bottom {{ transform: rotateX(-90deg) translateZ(170px); }}

        @keyframes rotateCube {{
            from {{ transform: rotateX(0deg) rotateY(0deg); }}
            to   {{ transform: rotateX(360deg) rotateY(360deg); }}
        }}

        .cube-glow-bg {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 500px;
            height: 500px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(37,99,235,0.20) 0%, transparent 70%);
            filter: blur(50px);
            z-index: 0;
            pointer-events: none;
            animation: pulseGlow 8s infinite ease-in-out;
        }}
        @keyframes pulseGlow {{
            0%, 100% {{ opacity: 0.5; transform: translate(-50%, -50%) scale(1); }}
            50% {{ opacity: 0.75; transform: translate(-50%, -50%) scale(1.08); }}
        }}

        .auth-foreground {{
            position: relative;
            z-index: 1;
            padding-top: 40px;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {colors['card_bg']} !important;
            backdrop-filter: blur(10px);
            padding: 10px !important;
            border-radius: 18px !important;
            box-shadow: 0 0 40px rgba(0,0,0,0.7) !important;
            border: 1px solid {colors['border']} !important;
        }}

        .auth-title {{
            color: {colors['text']};
            text-align: center;
            font-size: 27px;
            font-weight: 700;
            margin-bottom: 6px;
            margin-top: 10px;
        }}
        .auth-sub {{
            color: {colors['muted']};
            text-align: center;
            margin-bottom: 28px;
            font-size: 14px;
        }}
        .stTextInput>div>div>input {{
            background-color: {colors['input_bg']} !important;
            color: {colors['text']} !important;
            border-radius: 8px !important;
            border: 1px solid {colors['border']} !important;
            padding: 10px 14px !important;
        }}
        .stTextInput label {{
            color: {colors['muted']} !important;
            font-size: 13.5px !important;
        }}
        div[data-testid="stFormSubmitButton"] button {{
            width: 100%;
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-weight: 600 !important;
            border: none !important;
            margin-top: 8px;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: #1d4ed8 !important;
        }}
        .switch-text {{
            text-align: center;
            color: {colors['muted']};
            font-size: 13.5px;
            margin-top: 18px;
        }}

        @media (max-width: 900px) {{
            .cube-scene {{ width: 220px; height: 220px; opacity: 0.2; }}
            .cube-face {{ width: 220px; height: 220px; font-size: 65px; }}
            .face-front, .face-back, .face-right, .face-left, .face-top, .face-bottom {{
                transform: translateZ(110px);
            }}
        }}
        </style>
    """, unsafe_allow_html=True)


def show_3d_cube_background():
    st.markdown("""
        <div class="cube-glow-bg"></div>
        <div class="cube-bg-wrapper">
            <div class="cube-scene">
                <div class="cube">
                    <div class="cube-face face-front">🎓</div>
                    <div class="cube-face face-back">🤖</div>
                    <div class="cube-face face-right">💬</div>
                    <div class="cube-face face-left">📚</div>
                    <div class="cube-face face-top">✨</div>
                    <div class="cube-face face-bottom">🎯</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# LOAD USER'S SAVED CHATS AFTER LOGIN
# ============================================================
def load_chats_for_user(email):
    saved_chats = get_user_chats(email)
    if saved_chats:
        st.session_state.all_chats = saved_chats
        st.session_state.current_chat_id = list(saved_chats.keys())[-1]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.all_chats = {new_id: {"title": None, "messages": []}}
        st.session_state.current_chat_id = new_id


# ============================================================
# LOGIN PAGE — 3D rotating cube background, no photo/image assets
# ============================================================
def show_login_page():
    show_auth_css()
    show_3d_cube_background()

    st.markdown('<div class="auth-foreground">', unsafe_allow_html=True)

    spacer_l, content, spacer_r = st.columns([1.3, 1, 1.3])

    with content:
        with st.container(border=True):
            st.markdown('<div class="auth-title">Welcome Back 👋</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Log in to continue to CampusAI</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Log In")

            if submitted:
                success, message, uname = login_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = uname
                    st.session_state.user_email = email.strip().lower()
                    load_chats_for_user(st.session_state.user_email)
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

            st.markdown('<div class="switch-text">Don\'t have an account?</div>', unsafe_allow_html=True)
            if st.button("Create an account", use_container_width=True, key="go_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SIGNUP PAGE
# ============================================================
def show_signup_page():

    show_auth_css()
    show_3d_cube_background()

    st.markdown('<div class="auth-foreground">', unsafe_allow_html=True)

    spacer_l, content, spacer_r = st.columns([1.3, 1, 1.3])

    with content:
        with st.container(border=True):
            st.markdown('<div class="auth-title">Create Account ✨</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Sign up to start using CampusAI</div>', unsafe_allow_html=True)

            with st.form("signup_form"):
                sname = st.text_input("Full Name", placeholder="Enter your name")
                email = st.text_input("Gmail", placeholder="yourname@gmail.com")
                password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                submitted = st.form_submit_button("Sign Up")

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = signup_user(sname, email, password)
                    if success:
                        st.success(message)
                        time.sleep(1.5)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown('<div class="switch-text">Already have an account?</div>', unsafe_allow_html=True)
            if st.button("Log In instead", use_container_width=True, key="go_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# LOGIN TEMPORARILY DISABLED
# ============================================================
# Login/signup pages are kept in this file but are bypassed for now.
# The app opens directly into CampusAI using the demo profile above.


# ============================================================
# ================  MAIN CHATBOT APP  =======================
# ============================================================

@st.cache_resource
def get_rag_engine():
    return RAGEngine()

with st.spinner("Loading knowledge base... please wait ⏳"):
    rag = get_rag_engine()

if "all_chats" not in st.session_state:
    load_chats_for_user(st.session_state.user_email)

name = st.session_state.username
initials = "".join([w[0] for w in name.split()[:2]]).upper()

current_id = st.session_state.current_chat_id
current_chat = st.session_state.all_chats[current_id]
is_empty_chat = len(current_chat["messages"]) == 0

# ============================================================
# CUSTOM CSS
# ============================================================
colors = get_theme_colors()
font_size = get_font_size()

base_css = f"""
    <style>
    html {{ font-size: {font_size}; }}
    .stApp {{ background-color: {colors['bg']}; color: {colors['text']}; }}

    #MainMenu, footer {{ visibility: hidden !important; }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0px !important;
        visibility: hidden !important;
    }}
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    .stAppDeployButton {{
        display: none !important;
    }}
    .block-container {{
        padding-top: 1rem !important;
    }}

    /* ===================== FIX: force "position: fixed" to anchor to the
       real browser viewport, not a nested Streamlit container ===================== */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    .block-container {{
        transform: none !important;
        filter: none !important;
        contain: none !important;
        perspective: none !important;
        will-change: auto !important;
    }}

    /* ===================== SIDEBAR TOGGLE (hamburger) ===================== */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}

    div[data-testid="element-container"]:has(#sidebar-toggle-marker) + div[data-testid="element-container"] div[data-testid="stButton"] {{
        position: fixed !important;
        top: 38px !important;
        left: {{"260px" if st.session_state.sidebar_open else "-58px"}} !important;
        right: auto !important;
        z-index: 1000005 !important;
        width: 40px !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;
        transition: left 0.18s ease !important;
    }}
    div[data-testid="element-container"]:has(#sidebar-toggle-marker) + div[data-testid="element-container"] div[data-testid="stButton"] > button {{
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        background-color: {colors['card_bg']} !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
        font-size: 18px !important;
        line-height: 1 !important;
    }}
    div[data-testid="element-container"]:has(#sidebar-toggle-marker) + div[data-testid="element-container"] div[data-testid="stButton"] > button:hover {{
        background-color: {colors['sidebar_hover']} !important;
    }}

    /* ===================== SIDEBAR FIX (IMPORTANT) =====================
       Streamlit has its OWN native collapse mechanism that toggles
       aria-expanded="false" on the sidebar and slides it off-screen via
       a CSS transform — completely separate from our
       st.session_state.sidebar_open flag. Since we hide Streamlit's own
       re-expand arrow above, if the native collapse ever fires, the
       sidebar becomes permanently invisible with NO way to bring it
       back. We force it to always stay visible/un-transformed here;
       our own sidebar_open flag is the ONLY thing allowed to hide it. */
    section[data-testid="stSidebar"] {{
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        background-color: #0a0e18 !important;
        border-right: 1px solid #1e2636 !important;
        transform: none !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin-left: 0px !important;
        position: relative !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        transform: none !important;
        margin-left: 0px !important;
        visibility: visible !important;
        display: block !important;
    }}
    div[data-testid="stSidebarContent"],
    div[data-testid="stSidebarUserContent"] {{
        visibility: visible !important;
        opacity: 1 !important;
        /* Leave room at the bottom so the fixed profile card (see
           render_nav_sidebar) never overlaps the last nav item. */
        padding-bottom: 84px !important;
    }}
    @media (max-width: 640px) {{
        section[data-testid="stSidebar"] {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            z-index: 999998 !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.6) !important;
        }}
    }}
    [data-testid="stSidebarResizeHandle"] {{
        display: none !important;
        pointer-events: none !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: #0a0e18 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {colors['border']} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        background-color: transparent !important;
        border: 1px solid {colors['border']} !important;
        color: {colors['text']} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background-color: {colors['sidebar_hover']} !important;
        border-color: {colors['sidebar_hover']} !important;
    }}
    section[data-testid="stSidebar"] h2 {{
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-bottom: 2px !important;
    }}

    .avatar-circle-lg {{
        width: 32px; height: 32px; min-width: 32px; border-radius: 50%;
        background-color: #f59e0b; color: white !important;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 13px;
    }}
    .menu-header-name {{ color: {colors['text']} !important; font-weight: 600; font-size: 15px; margin: 0; }}
    .menu-header-sub {{ color: {colors['muted']} !important; font-size: 13px; margin: 0; }}
    .menu-btn div[data-testid="stButton"] button {{
        background-color: transparent !important; border: none !important;
        color: {colors['text']} !important; text-align: left !important; width: 100% !important;
        padding: 10px 12px !important; font-size: 20px !important; border-radius: 8px !important;
        display: block !important; min-height: unset !important;
    }}
    .menu-btn div[data-testid="stButton"] button::before {{ content: none !important; }}
    .menu-btn div[data-testid="stButton"] button:hover {{ background-color: {colors['sidebar_hover']} !important; }}

    .user-msg {{
        background-color: #2563eb; color: white !important; padding: 10px 16px;
        border-radius: 16px; max-width: 70%; margin-left: auto; margin-bottom: 10px;
    }}
    .bot-msg {{
        background-color: {colors['input_bg']}; color: {colors['text']} !important; padding: 10px 16px;
        border-radius: 16px; max-width: 70%; margin-bottom: 10px;
    }}
    .source-tag {{
        color: {colors['muted']} !important; font-size: 12px; margin-top: -4px; margin-bottom: 12px;
    }}

    .center-wrapper {{
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; min-height: 12vh; text-align: center; margin-top: 40px;
    }}
    .welcome-heading {{ font-size: 28px; font-weight: 600; color: {colors['text']}; margin-bottom: 8px; }}
    .welcome-sub {{ color: {colors['muted']}; font-size: 15px; }}
    .feature-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: {colors['card_bg']};
        border: 1px solid {colors['border']};
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        color: {colors['text']};
        font-weight: 500;
    }}

    .search-form-wrapper {{ max-width: 700px; margin: 25px auto 0 auto; position: relative; }}
    .search-form-wrapper div[data-testid="stForm"] {{ border: none; background: transparent; padding: 0; }}
    .search-form-wrapper div[data-testid="stTextInput"] input {{
        background-color: {colors['input_bg']} !important; color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important; border-radius: 10px !important;
        padding: 16px 60px 16px 22px !important; font-size: 15px !important; height: 54px !important;
    }}
    .search-form-wrapper div[data-testid="stTextInput"] input::placeholder {{ color: {colors['muted']} !important; }}
    .search-form-wrapper div[data-testid="stTextInput"] {{ margin-bottom: 0 !important; }}
    .search-form-wrapper div[data-testid="stFormSubmitButton"] button {{
        background-color: #565869 !important; color: white !important; border-radius: 8px !important;
        width: 38px !important; height: 38px !important; padding: 0 !important; border: none !important;
        position: relative; top: -54px; left: calc(100% - 50px); margin-bottom: -38px;
        transition: background-color 0.15s ease;
    }}
    .search-form-wrapper div[data-testid="stFormSubmitButton"] button.btn-active {{
        background-color: #2563eb !important;
    }}

    div[data-testid="stChatInput"] {{
        background-color: {colors['input_bg']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        border: none !important;
        color: {colors['text']} !important;
        box-shadow: none !important;
    }}
    div[data-testid="stChatInput"] button {{
        background-color: #565869 !important;
        border-radius: 8px !important;
        border: none !important;
        transition: background-color 0.15s ease;
    }}
    div[data-testid="stChatInput"] button.btn-active {{
        background-color: #2563eb !important;
    }}
    div[data-testid="stChatInput"] button svg {{
        fill: white !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        gap: 0.15rem !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="element-container"] {{
        margin-bottom: 0 !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        margin: 0 !important;
        min-height: 30px !important;
        padding: 6px 10px !important;
    }}

    /* ===================== DIALOGS (general) ===================== */
    div[data-testid="stDialog"] [data-testid="stDialogCloseButton"],
    div[data-testid="stDialog"] button[aria-label="Close"] {{
        display: none !important;
    }}
    div[data-testid="stDialog"] {{
        pointer-events: none !important;
    }}
    div[data-testid="stDialog"] > div {{
        pointer-events: auto !important;
    }}
    div[data-testid="stDialog"] > div {{
        background-color: {"#141414" if st.session_state.settings["theme"] == "dark" else "#ffffff"} !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6) !important;
    }}
    div[data-testid="stDialog"] {{
        background-color: rgba(0,0,0,0.55) !important;
    }}
    div[data-testid="stDialog"] input,
    div[data-testid="stDialog"] textarea {{
        background-color: {colors['input_bg']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
    }}
    div[data-testid="stDialog"] label {{
        color: {colors['muted']} !important;
        font-size: 13.5px !important;
    }}
    div[data-testid="stDialog"] p, 
    div[data-testid="stDialog"] h1,
    div[data-testid="stDialog"] h2,
    div[data-testid="stDialog"] h3,
    div[data-testid="stDialog"] .stMarkdown {{
        color: {colors['text']} !important;
    }}
    div[data-testid="stDialog"] .stExpander {{
        background-color: {colors['input_bg']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stDialog"] input[type="radio"] {{
        accent-color: #2563eb !important;
        width: 16px !important;
        height: 16px !important;
    }}
    div[data-testid="stDialog"] [data-testid="stRadio"] > div {{
        gap: 6px !important;
    }}
    div[data-testid="stDialog"] [data-testid="stRadio"] label {{
        padding: 6px 12px !important;
        border-radius: 20px !important;
        transition: background-color 0.15s ease;
    }}
    div[data-testid="stDialog"] [data-testid="stRadio"] label:hover {{
        background-color: {colors['sidebar_hover']} !important;
    }}
    div[data-testid="stDialog"] [data-testid="stRadio"] label p {{
        font-size: 20px !important;
        font-weight: 500 !important;
    }}
    .edit-profile-avatar-wrapper {{
        display: flex;
        justify-content: center;
        margin-bottom: 24px;
        margin-top: 6px;
    }}
    .edit-profile-avatar {{
        position: relative;
        width: 100px;
        height: 100px;
    }}
    .avatar-circle-xl {{
        width: 100px; height: 100px;
        border-radius: 50%;
        background-color: #f59e0b;
        color: white !important;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; font-weight: bold;
    }}
    .camera-badge {{
        position: absolute;
        bottom: 0; right: 0;
        width: 32px; height: 32px;
        background-color: {colors['border']};
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px;
        border: 2px solid {colors['card_bg']};
    }}

    /* ===================== SETTINGS: ChatGPT-style layout ===================== */
    .settings-header-title {{
        color: {colors['text']};
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 4px;
    }}
    div[data-testid="stVerticalBlock"]:has(#settings-nav-marker) {{
        gap: 2px !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#settings-nav-marker) div[data-testid="stButton"] {{
        margin: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#settings-nav-marker) div[data-testid="stButton"] > button {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors['muted']} !important;
        text-align: left !important;
        width: 100% !important;
        padding: 7px 10px !important;
        margin: 0 !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        justify-content: flex-start !important;
        min-height: unset !important;
        line-height: 1.4 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#settings-nav-marker) div[data-testid="stButton"] > button:hover {{
        background-color: {colors['sidebar_hover']} !important;
        color: {colors['text']} !important;
    }}
    div[data-testid="stVerticalBlock"]:has(#settings-nav-marker) div[data-testid="stButton"]:has(button[kind="primary"]) > button {{
        background-color: {colors['sidebar_hover']} !important;
        color: {colors['text']} !important;
        font-weight: 600 !important;
    }}
    .settings-section-title {{
        color: {colors['text']};
        font-weight: 700;
        font-size: 15px;
        margin-top: 4px;
        margin-bottom: 10px;
    }}
    .settings-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid {colors['border']};
    }}
    .settings-row-label {{
        color: {colors['text']};
        font-size: 14px;
        font-weight: 500;
    }}
    .settings-divider {{
        border: none;
        border-top: 1px solid {colors['border']};
        margin: 10px 0;
    }}
    .danger-zone {{
        border: 1px solid #7f1d1d;
        background-color: rgba(127,29,29,0.15);
        border-radius: 10px;
        padding: 12px;
        margin-top: 8px;
    }}
    .settings-content-scroll {{
        max-height: 460px;
        overflow-y: auto;
        padding-right: 8px;
    }}
    .help-contact-row {{
        color: {colors['text']};
        font-size: 14px;
        margin-bottom: 6px;
    }}
    .app-version-tag {{
        color: {colors['muted']};
        font-size: 12px;
        text-align: center;
        margin-top: 10px;
    }}
    </style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# If the sidebar is toggled closed via OUR OWN flag, hide it completely.
if not st.session_state.sidebar_open:
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================
# HAMBURGER (☰) SIDEBAR TOGGLE
# ============================================================
st.markdown('<div id="sidebar-toggle-marker"></div>', unsafe_allow_html=True)
toggle_clicked = st.button("☰", key="sidebar_toggle_btn")

if toggle_clicked:
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()


# Turn the send button blue only once the user has typed something
if "send_btn_color_script_injected" not in st.session_state:
    st.session_state.send_btn_color_script_injected = True

    components.html("""
        <script>
        (function() {
            const doc = window.parent.document;

            function wire(inputSelector, buttonSelector) {
                const inputEl = doc.querySelector(inputSelector);
                const btnEl = doc.querySelector(buttonSelector);
                if (!inputEl || !btnEl || inputEl.dataset.colorWired) return;
                inputEl.dataset.colorWired = 'true';

                function update() {
                    if (inputEl.value && inputEl.value.trim().length > 0) {
                        btnEl.classList.add('btn-active');
                    } else {
                        btnEl.classList.remove('btn-active');
                    }
                }
                inputEl.addEventListener('input', update);
                update();
            }

            function attach() {
                wire(
                    '.search-form-wrapper div[data-testid="stTextInput"] input',
                    '.search-form-wrapper div[data-testid="stFormSubmitButton"] button'
                );
                wire(
                    'div[data-testid="stChatInput"] textarea',
                    'div[data-testid="stChatInput"] button'
                );
            }

            attach();
            const observer = new MutationObserver(attach);
            observer.observe(doc.body, { childList: true, subtree: true });
        })();
        </script>
    """, height=0, width=0)


# ============================================================
# SHARED CSS for the new full-page account/settings/help screens
# ============================================================
def show_account_pages_css():
    colors = get_theme_colors()
    st.markdown(f"""
        <style>
        .acct-page-topbar {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 12px;
            padding: 6px 0 18px 0;
        }}
        .acct-theme-toggle {{
            width: 38px; height: 38px;
            border-radius: 50%;
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border']};
            display: flex; align-items: center; justify-content: center;
            font-size: 16px;
        }}
        .acct-back-home {{
            display: flex; align-items: center; gap: 8px;
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border']};
            border-radius: 10px;
            padding: 8px 16px;
            color: {colors['text']};
            font-weight: 600;
            font-size: 14px;
        }}
        .acct-page-title {{
            font-size: 30px;
            font-weight: 800;
            color: {colors['text']};
            margin: 0 0 4px 0;
        }}
        .acct-page-sub {{
            color: {colors['muted']};
            font-size: 15px;
            margin: 0 0 22px 0;
        }}
        .acct-card {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['border']};
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 18px;
        }}
        .acct-card-header {{
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 4px;
        }}
        .acct-icon-badge {{
            width: 42px; height: 42px; min-width: 42px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
            color: white;
        }}
        .acct-card-title {{
            font-size: 16px;
            font-weight: 700;
            color: {colors['text']};
            margin: 0;
        }}
        .acct-card-desc {{
            font-size: 13.5px;
            color: {colors['muted']};
            margin: 2px 0 0 0;
        }}
        .acct-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 13px 0;
            border-bottom: 1px solid {colors['border']};
        }}
        .acct-row:last-child {{ border-bottom: none; }}
        .acct-row-label {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: {colors['text']};
            font-size: 14.5px;
            font-weight: 500;
        }}
        .acct-row-value {{
            color: {colors['muted']};
            font-size: 14px;
        }}
        .acct-field-label {{
            color: {colors['text']};
            font-size: 13.5px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .acct-profile-banner {{
            background: linear-gradient(120deg, #1e3a8a, #1d4ed8);
            border-radius: 16px;
            padding: 24px 26px;
            display: flex;
            align-items: center;
            gap: 18px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }}
        .acct-profile-avatar-xl {{
            width: 74px; height: 74px;
            border-radius: 50%;
            background-color: #f59e0b;
            color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 26px; font-weight: 800;
            flex-shrink: 0;
        }}
        .acct-profile-name {{ color: white; font-size: 21px; font-weight: 800; margin: 0; }}
        .acct-profile-email {{ color: #cbd5e1; font-size: 14px; margin: 2px 0 8px 0; }}
        .acct-profile-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            background-color: rgba(255,255,255,0.15);
            color: white; font-size: 12.5px; font-weight: 600;
            padding: 4px 12px; border-radius: 20px;
        }}
        .acct-profile-quote {{
            margin-left: auto;
            color: #dbeafe;
            font-style: italic;
            text-align: right;
            font-size: 13.5px;
            max-width: 220px;
        }}
        .acct-upload-box {{
            border: 1.5px dashed {colors['border']};
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            color: {colors['muted']};
            font-size: 14px;
        }}
        .acct-char-counter {{
            text-align: right;
            color: {colors['muted']};
            font-size: 12px;
            margin-top: -8px;
        }}
        .acct-card [data-testid="stButton"] button,
        .acct-card [data-testid="stDownloadButton"] button {{
            border-radius: 10px !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_page_topbar(back_view="chat"):
    col_spacer, col_theme, col_back = st.columns([6, 1, 2])
    with col_theme:
        icon = "🌙" if st.session_state.settings["theme"] == "dark" else "☀️"
        if st.button(icon, key="acct_theme_toggle", help="Toggle theme"):
            st.session_state.settings["theme"] = "light" if st.session_state.settings["theme"] == "dark" else "dark"
            st.rerun()
    with col_back:
        if st.button("🏠  Back to Home", key="acct_back_home", use_container_width=True):
            st.session_state.current_view = "chat"
            st.rerun()


# ============================================================
# PROFILE PAGE
# ============================================================
if "display_name" not in st.session_state:
    st.session_state.display_name = name
if "username_handle" not in st.session_state:
    st.session_state.username_handle = name.lower().replace(" ", "")


def render_profile_page():
    show_account_pages_css()
    render_page_topbar()

    st.markdown('<div class="acct-page-title">My Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="acct-page-sub">Manage your profile information and personal details.</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="acct-profile-banner">
            <div class="acct-profile-avatar-xl">{initials}</div>
            <div>
                <p class="acct-profile-name">{st.session_state.display_name}</p>
                <p class="acct-profile-email">{st.session_state.user_email}</p>
                <span class="acct-profile-badge">🎓 Student</span>
            </div>
            <div class="acct-profile-quote">"Learn today for a brighter tomorrow."</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">👤</div>
            <div>
                <p class="acct-card-title">Basic Information</p>
                <p class="acct-card-desc">This information will be used to personalize your experience.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown('<div class="acct-field-label">Display name</div>', unsafe_allow_html=True)
        new_display_name = st.text_input("Display name", value=st.session_state.display_name, label_visibility="collapsed", key="profile_display_name")
    with pc2:
        st.markdown('<div class="acct-field-label">Username</div>', unsafe_allow_html=True)
        new_username = st.text_input("Username", value=st.session_state.username_handle, label_visibility="collapsed", key="profile_username")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">✉️</div>
            <div>
                <p class="acct-card-title">Email</p>
                <p class="acct-card-desc">Your email is used for account login and important notifications.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.text_input("Email address", value=st.session_state.user_email, disabled=True, label_visibility="visible", key="profile_email_display")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">🖼️</div>
            <div>
                <p class="acct-card-title">Profile Photo</p>
                <p class="acct-card-desc">Upload a profile picture to personalize your account.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    uploaded_photo = st.file_uploader(
        "Profile photo", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed", key="profile_photo_upload"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col_cancel, col_save = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="profile_cancel_btn"):
            st.session_state.current_view = "chat"
            st.rerun()
    with col_save:
        if st.button("💾  Save Changes", use_container_width=True, type="primary", key="profile_save_btn"):
            st.session_state.display_name = new_display_name
            st.session_state.username_handle = new_username
            st.session_state.username = new_display_name
            st.toast("Profile updated ✅")
            st.rerun()


# ============================================================
# PERSONALIZATION PAGE
# ============================================================
DEPARTMENTS = [
    "Computer Science", "Information Technology", "Mechanical",
    "Electrical", "Electronics & Communication", "Civil",
    "Business Administration", "Other"
]
YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Alumni", "Faculty/Staff"]


def render_personalization_page():
    show_account_pages_css()
    render_page_topbar()

    st.markdown('<div class="acct-page-title">Personalization</div>', unsafe_allow_html=True)
    st.markdown('<div class="acct-page-sub">Make CampusAI more helpful by telling us about yourself.</div>', unsafe_allow_html=True)

    pz = st.session_state.personalization

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">👤</div>
            <div>
                <p class="acct-card-title">Add Your Photo</p>
                <p class="acct-card-desc">This helps personalize your experience. JPG, PNG (Max 2MB)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.file_uploader("Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="pz_photo_upload")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">👤</div>
            <div>
                <p class="acct-card-title">Personal Information</p>
                <p class="acct-card-desc">Tell us a bit about yourself.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown('<div class="acct-field-label">What should we call you? *</div>', unsafe_allow_html=True)
        nickname = st.text_input("Nickname", value=pz["nickname"], placeholder="e.g. Manoj", label_visibility="collapsed", key="pz_nickname")
    with pcol2:
        st.markdown('<div class="acct-field-label">Your email</div>', unsafe_allow_html=True)
        st.text_input("Email", value=st.session_state.user_email, disabled=True, label_visibility="collapsed", key="pz_email_display")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">🎓</div>
            <div>
                <p class="acct-card-title">Academic Details</p>
                <p class="acct-card-desc">Help us give you more relevant answers.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    acol1, acol2 = st.columns(2)
    with acol1:
        st.markdown('<div class="acct-field-label">Your department *</div>', unsafe_allow_html=True)
        dept_index = DEPARTMENTS.index(pz["department"]) if pz["department"] in DEPARTMENTS else 0
        department = st.selectbox("Department", DEPARTMENTS, index=dept_index, label_visibility="collapsed", key="pz_department")
    with acol2:
        st.markdown('<div class="acct-field-label">Your year *</div>', unsafe_allow_html=True)
        year_index = YEARS.index(pz["year"]) if pz["year"] in YEARS else 0
        year = st.selectbox("Year", YEARS, index=year_index, label_visibility="collapsed", key="pz_year")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#0ea5e9;">📄</div>
            <div>
                <p class="acct-card-title">Additional Information</p>
                <p class="acct-card-desc">Let us know anything else (optional).</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    about_you = st.text_area(
        "About you", value=pz["about_you"],
        placeholder="e.g. I'm interested in placements, internships, scholarships, or specific courses...",
        max_chars=300, label_visibility="collapsed", key="pz_about_you"
    )
    st.markdown(f'<div class="acct-char-counter">{len(about_you)}/300</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    tcol1, tcol2 = st.columns([1, 8])
    with tcol1:
        enabled = st.toggle("Enable", value=pz["enabled"], label_visibility="collapsed", key="pz_enabled_toggle")
    with tcol2:
        st.markdown("""
            <p class="acct-card-title" style="margin-bottom:2px;">Enable personalization</p>
            <p class="acct-card-desc">Use this information to give more relevant answers about admissions, courses, college life, and more.</p>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col_cancel, col_save = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="pz_cancel_btn"):
            st.session_state.current_view = "chat"
            st.rerun()
    with col_save:
        if st.button("💾  Save Changes", use_container_width=True, type="primary", key="pz_save_btn"):
            st.session_state.personalization = {
                "enabled": enabled,
                "nickname": nickname.strip(),
                "about_you": about_you.strip(),
                "department": department,
                "year": year
            }
            st.toast("Personalization saved ✅")
            st.rerun()


# ============================================================
# HELP & SUPPORT PAGE
# ============================================================
FAQ_ITEMS = [
    ("🎓", "How do I ask about admissions?",
     "Just type your question, e.g. 'What is the admission process for B.Tech?' and CampusAI will search the knowledge base for you."),
    ("💳", "Can CampusAI help with fee details?",
     "Yes! Ask things like 'What is the semester fee for CSE?' and it will try to find relevant info from official documents."),
    ("ℹ️", "Why did CampusAI say it doesn't know?",
     "CampusAI only answers from the college's uploaded documents. If the info isn't in the knowledge base, it will let you know instead of guessing."),
    ("🕐", "How do I clear my chat history?",
     "Go to Settings → Data & Privacy → Clear Chat History."),
    ("🔒", "How do I change my password?",
     "Go to Settings → Account → Change Password."),
    ("👤", "How do I personalize my experience?",
     "Go to Settings → Personalization to update your preferences."),
]


def render_help_page():
    show_account_pages_css()
    render_page_topbar()

    st.markdown('<div style="color:#3b82f6;font-weight:700;font-size:13px;letter-spacing:1px;">SUPPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="acct-page-title">Help & Support</div>', unsafe_allow_html=True)
    st.markdown('<div class="acct-page-sub">We\'re here to help! Find answers, get support, or share your feedback.</div>', unsafe_allow_html=True)

    search_query = st.text_input(
        "Search help", placeholder="Search for help (e.g. admissions, password, chat history...)",
        label_visibility="collapsed", key="help_search_query"
    )

    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">💬</div>
            <div>
                <p class="acct-card-title">Frequently Asked Questions</p>
                <p class="acct-card-desc">Find quick answers to common questions.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    q = search_query.strip().lower()
    shown_any = False
    for icon, question, answer in FAQ_ITEMS:
        if q and q not in question.lower() and q not in answer.lower():
            continue
        shown_any = True
        with st.expander(f"{icon}  {question}"):
            st.write(answer)
    if not shown_any:
        st.caption("No matching questions found — try a different search term.")
    st.markdown('</div>', unsafe_allow_html=True)

    ccol, fcol = st.columns(2)
    with ccol:
        st.markdown('<div class="acct-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="acct-card-header">
                <div class="acct-icon-badge" style="background-color:#2563eb;">🎧</div>
                <div>
                    <p class="acct-card-title">Contact Support</p>
                    <p class="acct-card-desc">Need more help? Reach out to our support team.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div class="acct-row"><span class="acct-row-label">✉️ support@college.edu</span></div>
            <div class="acct-row"><span class="acct-row-label">📞 +91-XXXXXXXXXX</span></div>
            <div class="acct-row"><span class="acct-row-label">🕐 Mon – Fri, 9 AM – 5 PM</span></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with fcol:
        st.markdown('<div class="acct-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="acct-card-header">
                <div class="acct-icon-badge" style="background-color:#2563eb;">💬</div>
                <div>
                    <p class="acct-card-title">Send Feedback</p>
                    <p class="acct-card-desc">Help us improve! Share your suggestions or report an issue.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        feedback = st.text_area(
            "Feedback", placeholder="Tell us what you think...",
            max_chars=500, label_visibility="collapsed", key="help_feedback_text"
        )
        st.markdown(f'<div class="acct-char-counter">{len(feedback)}/500</div>', unsafe_allow_html=True)
        if st.button("📤  Send Feedback", use_container_width=True, type="primary", key="submit_feedback_btn"):
            if feedback.strip():
                st.toast("Thanks for your feedback! 🙏")
            else:
                st.warning("Please write something before submitting.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="acct-card" style="display:flex;justify-content:space-between;align-items:center;">
            <span>❤️ Thank you for being a part of CampusAI!</span>
            <span>🎓 Together for a Smarter Future</span>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# SETTINGS PAGE
# ============================================================
def render_settings_page():
    show_account_pages_css()
    render_page_topbar()

    st.markdown('<div class="acct-page-title">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="acct-page-sub">Customize your CampusAI experience</div>', unsafe_allow_html=True)

    # ---- Appearance ----
    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#2563eb;">🎨</div>
            <div>
                <p class="acct-card-title">Appearance</p>
                <p class="acct-card-desc">Choose how CampusAI looks</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    theme_choice = st.radio(
        "Theme", options=["dark", "light"],
        index=0 if st.session_state.settings["theme"] == "dark" else 1,
        horizontal=True, format_func=lambda x: "🌙 Dark" if x == "dark" else "☀️ Light",
        key="settings_theme_radio"
    )
    if theme_choice != st.session_state.settings["theme"]:
        st.session_state.settings["theme"] = theme_choice
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Font & Display ----
    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#14b8a6;">Aa</div>
            <div>
                <p class="acct-card-title">Font & Display</p>
                <p class="acct-card-desc">Adjust the text size for better readability</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    font_choice = st.radio(
        "Font size", options=["small", "medium", "large"],
        index=["small", "medium", "large"].index(st.session_state.settings["font_size"]),
        horizontal=True, format_func=lambda x: x.capitalize(),
        key="settings_font_radio"
    )
    if font_choice != st.session_state.settings["font_size"]:
        st.session_state.settings["font_size"] = font_choice
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Chat Preferences ----
    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#8b5cf6;">💬</div>
            <div>
                <p class="acct-card-title">Chat Preferences</p>
                <p class="acct-card-desc">Choose how you want answers</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    style_choice = st.radio(
        "Response style", options=["concise", "detailed"],
        index=0 if st.session_state.settings["response_style"] == "concise" else 1,
        horizontal=True, format_func=lambda x: x.capitalize(),
        key="settings_style_radio"
    )
    if style_choice != st.session_state.settings["response_style"]:
        st.session_state.settings["response_style"] = style_choice
        st.toast(f"Response style set to {style_choice.capitalize()}")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Account ----
    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#f59e0b;">👤</div>
            <div>
                <p class="acct-card-title">Account</p>
                <p class="acct-card-desc">Manage your account settings</p>
            </div>
        </div>
        <div class="acct-row">
            <span class="acct-row-label">✉️ Email</span>
            <span class="acct-row-value">{st.session_state.user_email}</span>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("🔒  Change Password"):
        with st.form("change_password_form"):
            current_pw = st.text_input("Current password", type="password")
            new_pw = st.text_input("New password", type="password")
            confirm_pw = st.text_input("Confirm new password", type="password")
            pw_submitted = st.form_submit_button("Update Password", use_container_width=True)

        if pw_submitted:
            if not current_pw or not new_pw or not confirm_pw:
                st.error("Please fill in all password fields.")
            elif new_pw != confirm_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            elif change_password_user is None:
                st.warning("⚠️ change_password_user() not found in auth.py.")
            else:
                success, message = change_password_user(st.session_state.user_email, current_pw, new_pw)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with st.expander("🗑️  Delete Account"):
        st.error("This action is permanent and cannot be undone.")
        if not st.session_state.confirm_delete_account:
            if st.button("Delete My Account", use_container_width=True, key="delete_account_btn"):
                st.session_state.confirm_delete_account = True
                st.rerun()
        else:
            confirm_text = st.text_input("Type DELETE to confirm", key="delete_confirm_text")
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("Cancel", use_container_width=True, key="cancel_delete_account"):
                    st.session_state.confirm_delete_account = False
                    st.rerun()
            with dc2:
                if st.button("Confirm Delete", use_container_width=True, type="primary", key="confirm_delete_account_btn"):
                    if confirm_text.strip().upper() != "DELETE":
                        st.error("Please type DELETE exactly to confirm.")
                    elif delete_user_account is None:
                        st.warning("⚠️ delete_user_account() not found in auth.py.")
                    else:
                        success, message = delete_user_account(st.session_state.user_email)
                        if success:
                            st.toast("Account deleted.")
                            st.session_state.logged_in = False
                            st.session_state.username = ""
                            st.session_state.user_email = ""
                            st.session_state.pop("all_chats", None)
                            st.session_state.pop("current_chat_id", None)
                            st.session_state.confirm_delete_account = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Data & Privacy ----
    st.markdown('<div class="acct-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="acct-card-header">
            <div class="acct-icon-badge" style="background-color:#ef4444;">🛡️</div>
            <div>
                <p class="acct-card-title">Data & Privacy</p>
                <p class="acct-card-desc">Control your data and privacy</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    export_data = json.dumps(st.session_state.all_chats, indent=2, ensure_ascii=False)
    st.download_button(
        "📥  Export Chat History", data=export_data,
        file_name=f"chat_history_{st.session_state.user_email}.json",
        mime="application/json", use_container_width=True, key="export_chats_btn"
    )

    with st.expander("🗄️  Clear Chat History"):
        if not st.session_state.confirm_clear_chat:
            if st.button("Clear All Chat History", use_container_width=True, key="clear_chat_btn"):
                st.session_state.confirm_clear_chat = True
                st.rerun()
        else:
            st.warning("Are you sure? This will permanently delete all your chats.")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Cancel", use_container_width=True, key="cancel_clear_chat"):
                    st.session_state.confirm_clear_chat = False
                    st.rerun()
            with cc2:
                if st.button("Yes, Clear All", use_container_width=True, type="primary", key="confirm_clear_chat_btn"):
                    new_id = str(uuid.uuid4())
                    st.session_state.all_chats = {new_id: {"title": None, "messages": []}}
                    st.session_state.current_chat_id = new_id
                    save_user_chats(st.session_state.user_email, st.session_state.all_chats)
                    st.session_state.confirm_clear_chat = False
                    st.toast("All chat history cleared 🗑️")
                    st.rerun()

    st.markdown("""
        <div class="acct-row"><span class="acct-row-label">👁️ Privacy Policy</span></div>
        <div class="acct-row"><span class="acct-row-label">📄 Terms of Use</span></div>
    """, unsafe_allow_html=True)
    st.caption("Privacy Policy and Terms of Use pages aren't built yet — placeholders only.")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# NAV SIDEBAR — restyled to match the clean/minimal reference:
# CampusAI logo (unchanged) + one-line tagline, bordered "New Chat"
# button, plain-text "Recents", and a clickable bottom profile card
# with a ChatGPT-style popover menu.
# ============================================================
def render_nav_sidebar(active_view):
    """Render the clean CampusAI sidebar.

    Only the website branding, New Chat, Recents, and the bottom
    clickable profile card are rendered in the sidebar.
    """
    st.markdown("""
    <style>
    /* ==========================================================
       CAMPUSAI SIDEBAR — REFERENCE DESIGN
       ========================================================== */

    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        background: #272831 !important;
        border-right: 1px solid #1d1d24 !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        background: #272831 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding: 18px 10px 80px 10px !important;
        min-height: 100vh !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    section[data-testid="stSidebar"] [data-testid="element-container"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Hide legacy sidebar pieces completely. */
    .compact-divider,
    .compact-knowledge,
    .compact-rag,
    .compact-profile-menu,
    .compact-profile-menu *,
    .compact-profile-wrap,
    .compact-profile-visible,
    .compact-profile-arrow-html,
    .compact-profile-area,
    .side-nav,
    .sidebar-spacer,
    .nav-sidebar-profile-card,
    .nav-sidebar-profile-avatar,
    .side-tagline:not(.reference-tagline),
    .reference-profile-button-wrap,
    .reference-profile-trigger,
    #profile_marker,
    #profile_button_marker {
        display: none !important;
    }

    /* ==========================================================
       WEBSITE BRANDING — TOP
       ========================================================== */

    .reference-brand {
        margin: 0 0 18px 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    .reference-brand-title {
        display: flex !important;
        align-items: center !important;
        gap: 7px !important;
        color: #f5f5f7 !important;
        font-size: 25px !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
        white-space: nowrap !important;
    }

    .reference-brand-title .cap {
        font-size: 20px !important;
        line-height: 1 !important;
    }

    .reference-brand-title .ai {
        color: #168cff !important;
    }

    .reference-tagline {
        display: block !important;
        color: #9aa0b0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
        margin-top: 6px !important;
        white-space: nowrap !important;
    }

    /* ==========================================================
       NEW CHAT — MATCH REFERENCE
       ========================================================== */

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-new-chat-marker) {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-new-chat-marker)
    div[data-testid="stButton"] {
        width: 220px !important;
        margin: 0 0 18px 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-new-chat-marker)
    div[data-testid="stButton"] > button {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;

        height: 32px !important;
        min-height: 32px !important;

        margin: 0 !important;
        padding: 0 !important;

        background: #272831 !important;
        border: 1px solid #4a4b56 !important;
        border-radius: 6px !important;

        color: #f0f0f3 !important;
        font-size: 12px !important;
        font-weight: 600 !important;

        line-height: 32px !important;
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-new-chat-marker)
    div[data-testid="stButton"] > button:hover {
        background: #30313b !important;
        border-color: #5a5b67 !important;
    }

    /* ==========================================================
       RECENTS — MATCH REFERENCE
       ========================================================== */

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-recents-marker) {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .exact-recents-title {
        color: #f4f4f6 !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        line-height: 19px !important;

        margin: 0 !important;
        padding: 0 !important;

        text-align: left !important;
        letter-spacing: 0 !important;
    }

    .exact-empty-history {
        color: #dedfe5 !important;
        font-size: 12px !important;
        font-style: italic !important;

        line-height: 16px !important;
        text-align: left !important;

        margin: 0 !important;
        padding: 0 !important;
    }

    /* Recent chat cards when history exists. */
    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-recents-marker)
    div[data-testid="stButton"] {
        width: 220px !important;
        margin: 0 0 6px 0 !important;
        padding: 0 !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-recents-marker)
    div[data-testid="stButton"] > button {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;

        min-height: 44px !important;
        height: auto !important;

        margin: 12px 0 6px 0 !important;
        padding: 7px 10px !important;

        background: #272831 !important;
        border: 1px solid #3e404b !important;
        border-radius: 7px !important;

        color: #e5e6eb !important;
        font-size: 12px !important;
        line-height: 1.35 !important;

        text-align: left !important;
        justify-content: flex-start !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-testid="stVerticalBlock"]:has(#exact-recents-marker)
    div[data-testid="stButton"] > button:hover {
        background: #30313b !important;
        border-color: #555763 !important;
    }

    /* ==========================================================
       BOTTOM PROFILE CARD — CLICKABLE + POPOVER MENU
       FIX: position the trigger itself, not its Streamlit wrapper.
       This prevents the invisible popover trigger from appearing at
       the top of the sidebar and covering CampusAI/New Chat/Recents.
       ========================================================== */

    /* Visible card: fixed directly to the sidebar viewport. */
    section[data-testid="stSidebar"] .reference-profile-card {
        position: fixed !important;
        left: 10px !important;
        bottom: 10px !important;
        width: 240px !important;
        height: 54px !important;
        box-sizing: border-box !important;

        border: 1px solid #4a4c57 !important;
        border-radius: 9px !important;
        background: #282a33 !important;
        overflow: hidden !important;

        z-index: 1000000 !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"] .reference-profile-card .profile-avatar {
        position: absolute !important;
        left: 10px !important;
        top: 8px !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: #f59e0b !important;
        color: #ffffff !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 11px !important;
        font-weight: 800 !important;
    }

    section[data-testid="stSidebar"] .reference-profile-card .profile-text {
        position: absolute !important;
        left: 58px !important;
        top: 6px !important;
        right: 8px !important;
        text-align: left !important;
        line-height: 1.2 !important;
    }

    section[data-testid="stSidebar"] .reference-profile-card .profile-name {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        line-height: 18px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    section[data-testid="stSidebar"] .reference-profile-card .profile-email {
        color: #c4c6cc !important;
        font-size: 12px !important;
        line-height: 16px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* Popover trigger: fixed over the visible card and completely invisible.
       No arrow, no border, no background, no visible label. */
    section[data-testid="stSidebar"] div[data-testid="stPopover"] {
        position: fixed !important;
        left: 10px !important;
        bottom: 10px !important;
        width: 240px !important;
        height: 54px !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 1000005 !important;
        overflow: visible !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button {
        position: absolute !important;
        inset: 0 !important;
        width: 240px !important;
        height: 54px !important;
        min-height: 54px !important;
        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
        border: none !important;
        border-radius: 9px !important;
        box-shadow: none !important;

        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
        opacity: 0 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:hover,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:focus,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button:active {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button svg,
    section[data-testid="stSidebar"] div[data-testid="stPopover"] > button [data-testid="stPopoverIcon"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* ==========================================================
       PROFILE POPOVER — MATCH THE REFERENCE MENU
       ========================================================== */

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker) {
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
        padding: 12px 14px 14px 14px !important;
        background: #282a33 !important;
        border: 1px solid #4a4c57 !important;
        border-radius: 15px !important;
        box-shadow: 0 18px 45px rgba(0,0,0,0.55) !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-header {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 4px 0 10px 0 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-avatar {
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        border-radius: 50% !important;
        background: #f59e0b !important;
        color: #ffffff !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 11px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-name {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        line-height: 17px !important;
        margin: 0 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-email {
        color: #c4c6cc !important;
        font-size: 11.5px !important;
        line-height: 15px !important;
        margin: 1px 0 0 0 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-divider {
        height: 1px !important;
        width: 100% !important;
        background: #444650 !important;
        margin: 7px 0 14px 0 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    div[data-testid="stButton"] {
        margin: 0 0 9px 0 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    div[data-testid="stButton"] > button {
        width: 100% !important;
        min-height: 40px !important;
        height: 40px !important;
        margin: 0 !important;
        padding: 0 10px !important;
        background: #282a33 !important;
        border: 1px solid #565864 !important;
        border-radius: 8px !important;
        color: #ececf0 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: none !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    div[data-testid="stButton"] > button:hover {
        background: #31333d !important;
        border-color: #696b77 !important;
    }

    div[data-testid="stPopoverBody"]:has(#profile-popover-content-marker)
    .profile-popover-logout-divider {
        height: 1px !important;
        width: 100% !important;
        background: #444650 !important;
        margin: 17px 0 14px 0 !important;
    }

    /* Keep the same hamburger used by the app; no second hamburger. */
    section[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] {
        display: flex !important;
    }

    @media (max-width: 640px) {
        section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
            max-width: 260px !important;
        }

        .reference-profile-zone {
            left: 10px !important;
            width: 240px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # ------------------------------------------------------
        # WEBSITE NAME
        # ------------------------------------------------------
        st.markdown("""
            <div class="reference-brand">
                <div class="reference-brand-title">
                    <span class="cap">🎓</span>
                    <span>Campus <span class="ai">AI</span></span>
                </div>
                <div class="reference-tagline">
                    Campus Knowledge, One Chat Away
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ------------------------------------------------------
        # NEW CHAT
        # ------------------------------------------------------
        with st.container():
            st.markdown(
                '<div id="exact-new-chat-marker"></div>',
                unsafe_allow_html=True
            )

            if st.button(
                "+ New Chat",
                key="reference_new_chat",
                use_container_width=False
            ):
                new_id = str(uuid.uuid4())

                st.session_state.all_chats[new_id] = {
                    "title": None,
                    "messages": []
                }

                st.session_state.current_chat_id = new_id
                st.session_state.current_view = "chat"

                st.rerun()

        # ------------------------------------------------------
        # RECENTS
        # ------------------------------------------------------
        with st.container():
            st.markdown(
                '<div id="exact-recents-marker"></div>'
                '<div class="exact-recents-title">Recents</div>',
                unsafe_allow_html=True
            )

            # Force a visible gap between the Recents heading and its first item.
            # Using a real spacer element avoids Streamlit's vertical-block margin reset.
            st.markdown(
                '<div style="height: 0px; width: 1px;"></div>',
                unsafe_allow_html=True
            )

            recent_items = [
                (cid, data)
                for cid, data in st.session_state.all_chats.items()
                if data.get("title")
            ]
            recent_items.reverse()

            if recent_items:
                for cid, data in recent_items[:5]:
                    title = data.get("title") or "New Chat"

                    if len(title) > 26:
                        title = title[:26] + "..."

                    if st.button(
                        title,
                        key=f"reference_recent_{cid}",
                        use_container_width=False
                    ):
                        st.session_state.current_chat_id = cid
                        st.session_state.current_view = "chat"
                        st.rerun()
            else:
                st.markdown(
                    '<div class="exact-empty-history">'
                    '(chat history will appear here)'
                    '</div>',
                    unsafe_allow_html=True
                )

        # ------------------------------------------------------
        # BOTTOM PROFILE — CLICKABLE POPOVER
        # ------------------------------------------------------
        sidebar_name = st.session_state.username or "Devanand Kolli"
        sidebar_email = st.session_state.user_email or "devanand@gmail.com"
        sidebar_initials = "".join(
            w[0] for w in sidebar_name.split()[:2]
        ).upper() or "DK"

        with st.container():
            st.markdown(
                '<div id="profile-popover-marker"></div>',
                unsafe_allow_html=True
            )

            # The visible card is HTML; the transparent popover trigger
            # sits directly over the full card, so clicking anywhere on
            # DK / name / Gmail opens the menu.
            st.markdown(f"""
                <div class="reference-profile-card">
                    <div class="profile-avatar">{sidebar_initials}</div>
                    <div class="profile-text">
                        <div class="profile-name">{sidebar_name}</div>
                        <div class="profile-email">{sidebar_email}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.popover(" ", use_container_width=True):
                st.markdown(
                    '<div id="profile-popover-content-marker"></div>',
                    unsafe_allow_html=True
                )

                st.markdown(f"""
                    <div class="profile-popover-header">
                        <div class="profile-popover-avatar">{sidebar_initials}</div>
                        <div>
                            <div class="profile-popover-name">{sidebar_name}</div>
                            <div class="profile-popover-email">{sidebar_email}</div>
                        </div>
                    </div>
                    <div class="profile-popover-divider"></div>
                """, unsafe_allow_html=True)

                if st.button("🎨  Personalization",
                             use_container_width=True,
                             key="profile_popover_personalization"):
                    st.session_state.current_view = "settings_personalization"
                    st.rerun()

                if st.button("👤  Profile",
                             use_container_width=True,
                             key="profile_popover_profile"):
                    st.session_state.current_view = "settings_profile"
                    st.rerun()

                if st.button("⚙️  Settings",
                             use_container_width=True,
                             key="profile_popover_settings"):
                    st.session_state.current_view = "settings_general"
                    st.rerun()

                if st.button("❓  Help",
                             use_container_width=True,
                             key="profile_popover_help"):
                    st.session_state.current_view = "help"
                    st.rerun()

                st.markdown(
                    '<div class="profile-popover-logout-divider"></div>',
                    unsafe_allow_html=True
                )

                if st.button("↪️  Log out",
                             use_container_width=True,
                             key="profile_popover_logout"):
                    st.session_state.logged_in = False
                    st.session_state.auth_mode = "login"
                    st.session_state.current_view = "chat"
                    st.toast("Logged out.")
                    st.rerun()


st.markdown("""
<style>

/* ==========================================================
   REMOVE POPOVER ARROW COMPLETELY
   ========================================================== */

section[data-testid="stSidebar"]
div[data-testid="stPopover"] > button,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] button[data-testid="stPopoverButton"] {

    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;

    outline: none !important;
}

/* Remove Streamlit chevron / pseudo elements */
section[data-testid="stSidebar"]
div[data-testid="stPopover"] > button::before,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] > button::after,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] button[data-testid="stPopoverButton"]::before,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] button[data-testid="stPopoverButton"]::after {

    content: none !important;
    display: none !important;
    visibility: hidden !important;
}

/* Remove every possible icon/span inside trigger */
section[data-testid="stSidebar"]
div[data-testid="stPopover"] > button svg,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] > button span,
section[data-testid="stSidebar"]
div[data-testid="stPopover"] [data-testid="stPopoverIcon"],
section[data-testid="stSidebar"]
div[data-testid="stPopover"] [data-testid="stPopoverIcon"] svg {

    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
}

/* Keep the trigger clickable but completely invisible */
section[data-testid="stSidebar"]
div[data-testid="stPopover"] {

    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)

def render_chat_view():
    current_id = st.session_state.current_chat_id
    current_chat = st.session_state.all_chats[current_id]
    is_empty = len(current_chat["messages"]) == 0

    user_input = None

    if is_empty:
        st.markdown(f"""
            <div class="center-wrapper">
                <div class="welcome-heading">👋 Hello, {name}</div>
                <div class="welcome-sub">Welcome to CampusAI — Ask me anything about the college — admissions, courses, fees, and more.</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="search-form-wrapper">', unsafe_allow_html=True)
        with st.form(key=f"center_search_form_{current_id}", clear_on_submit=True):
            col1, col2 = st.columns([9, 1])
            with col1:
                typed_text = st.text_input(
                    "search",
                    placeholder="Ask anything about the college...",
                    label_visibility="collapsed",
                    key=f"center_input_{current_id}"
                )
            with col2:
                submitted = st.form_submit_button("↑")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <div style="display:flex; gap:10px; justify-content:center; margin-top:20px; flex-wrap:wrap;">
                <span class="feature-pill">⚡ Instant Answers</span>
                <span class="feature-pill">🛡️ Reliable Information</span>
                <span class="feature-pill">🕐 Always Available</span>
                <span class="feature-pill">👥 Student Friendly</span>
            </div>
        """, unsafe_allow_html=True)

        if submitted and typed_text.strip():
            user_input = typed_text.strip()

    else:
        st.title("🎓 CampusAI")
        for msg in current_chat["messages"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg">{msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("sources"):
                    sources_str = ", ".join(msg["sources"])
                    st.markdown(f'<div class="source-tag">📄 Sources: {sources_str}</div>', unsafe_allow_html=True)

        user_input_from_chat = st.chat_input("Ask anything about the college...")
        if user_input_from_chat:
            user_input = user_input_from_chat

    if user_input:
        if current_chat["title"] is None:
            title = user_input.strip()
            current_chat["title"] = title[:60]

        current_chat["messages"].append({"role": "user", "content": user_input})

        # Build personalization context string, if enabled
        user_context = None
        pz = st.session_state.personalization
        if pz.get("enabled"):
            parts = []
            if pz.get("nickname"):
                parts.append(f"Call the user {pz['nickname']}.")
            if pz.get("department"):
                parts.append(f"They are from the {pz['department']} department.")
            if pz.get("year"):
                parts.append(f"They are in {pz['year']}.")
            if pz.get("about_you"):
                parts.append(f"Additional info: {pz['about_you']}")
            if parts:
                user_context = " ".join(parts)

        with st.spinner("Thinking..."):
            try:
                try:
                    result = rag.answer(
                        question=user_input,
                        chat_history=current_chat["messages"][:-1],
                        response_style=st.session_state.settings["response_style"],
                        user_context=user_context
                    )
                except TypeError:
                    try:
                        result = rag.answer(
                            question=user_input,
                            chat_history=current_chat["messages"][:-1],
                            response_style=st.session_state.settings["response_style"]
                        )
                    except TypeError:
                        result = rag.answer(
                            question=user_input,
                            chat_history=current_chat["messages"][:-1]
                        )
                bot_response = result["answer"]
                bot_sources = result.get("sources", [])
            except Exception as e:
                bot_response = f"⚠️ Error: {str(e)}"
                bot_sources = []

        current_chat["messages"].append({
            "role": "assistant",
            "content": bot_response,
            "sources": bot_sources
        })

        save_user_chats(st.session_state.user_email, st.session_state.all_chats)
        st.rerun()


def show_chat_app():
    render_nav_sidebar(st.session_state.current_view)

    view = st.session_state.current_view
    if view == "help":
        render_help_page()
    elif view == "settings_personalization":
        render_personalization_page()
    elif view == "settings_profile":
        render_profile_page()
    elif view in ("settings_general", "settings_data_privacy", "settings_account"):
        render_settings_page()
    else:
        render_chat_view()


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    show_chat_app()

if __name__ == "__main__":
    main()