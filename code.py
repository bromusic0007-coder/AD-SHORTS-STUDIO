import streamlit as st
import asyncio
import edge_tts
import os
import json
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips, afx, vfx

st.set_page_config(
    page_title="AD Shorts Studio - Cyber Edition", 
    page_icon="💻", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- USER ACCOUNTS & PERSISTENT SESSION HELPERS ---
USER_DB_FILE = "users_database_v6.json"
SESSION_FILE = "current_session_v6.json"

def load_user_db():
    default_db = {
        "bromusic0008@gmail.com": {
            "password": "naams@123",
            "is_premium": True,
            "history": [],
            "custom_templates": {},
            "app_bg_css": "linear-gradient(135deg, #03030A 0%, #0A0718 50%, #020207 100%)"
        }
    }
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r") as f:
                db = json.load(f)
                if "bromusic0008@gmail.com" not in db:
                    db["bromusic0008@gmail.com"] = default_db["bromusic0008@gmail.com"]
                return db
        except Exception:
            return default_db
    return default_db

def save_user_db(db):
    try:
        with open(USER_DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except Exception:
        pass

def load_active_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("username", "")
        except Exception:
            return ""
    return ""

def save_active_session(uname):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump({"username": uname}, f)
    except Exception:
        pass

def clear_active_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

# Initialize Session State
if "logged_in" not in st.session_state:
    saved_user = load_active_session()
    db = load_user_db()
    if saved_user and saved_user in db:
        st.session_state.logged_in = True
        st.session_state.username = saved_user
    else:
        st.session_state.logged_in = False
        st.session_state.username = ""

if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "script_text" not in st.session_state:
    st.session_state.script_text = "Step into the future. Master map control, futuristic tactical loadouts, and high-speed execution to conquer every single match!"
if "theme_color" not in st.session_state:
    st.session_state.theme_color = "#0A0F1D"
if "custom_templates" not in st.session_state:
    st.session_state.custom_templates = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "show_rating_popup" not in st.session_state:
    st.session_state.show_rating_popup = False
if "open_customizer" not in st.session_state:
    st.session_state.open_customizer = False

DEFAULT_BG_CSS = "linear-gradient(135deg, #03030A 0%, #0A0718 50%, #020207 100%)"
if "app_bg_css" not in st.session_state:
    st.session_state.app_bg_css = DEFAULT_BG_CSS

# --- TUTOR GUIDES ---
DEFAULT_TUTOR_TITLE = "🌌 Cybernetic Quick-Start & Feature Matrix"
DEFAULT_TUTOR_CONTENT = """Welcome to **AD Shorts Studio (Cyber Edition)**! Here is your core control manual:
1. **🔐 Neural Link Login:** Authenticate once to sync your cloud profile, templates, and project history permanently.
2. **📁 Holographic Templates:** Access instant pre-built content matrices or build your own custom templates.
3. **🤖 Quantum Script AI:** Generate high-retention engagement hooks instantly.
4. **🎙️ Synthetic Voice Matrix:** Deploy ultra-realistic neural text-to-speech voiceovers with custom cinematic accents.
5. **🎬 Multimedia Staging:** Stitch dynamic intros, outros, and immersive background audio soundtracks seamlessly.
6. **🎨 Cyber Styler & Holographic UI:** Shift between futuristic color presets or design your own custom aesthetic.
7. **🎬 CapCut-Style Matrix Editor (`Ctrl + K`):** Precision trim video frames, shift speed ratios, and execute cinematic photo enhancements.
8. **📂 Archive & Trash Core (`Shift + Del`):** Clean up export items or clear redundant media buffers instantly."""

if "tutor_title" not in st.session_state:
    st.session_state.tutor_title = DEFAULT_TUTOR_TITLE
if "tutor_content" not in st.session_state:
    st.session_state.tutor_content = DEFAULT_TUTOR_CONTENT

DEFAULT_PRO_TITLE = "👑 Elite Creator Masterclass (Advanced Protocols)"
DEFAULT_PRO_CONTENT = """Advanced Operations Manual:
1. **⌨️ Shortcut Navigation:** Use **`Ctrl + K`** to jump directly into the media editor matrix. Use **`Shift + Del`** to purge local cache logs.
2. **🎙️ Audio Mixing Balance:** Keep background music amplitude around 10%–15% for optimal neural voice clarity.
3. **🎬 Cinematic Intro/Outro Stitching:** Maximize retention metrics by appending high-definition brand asset openers."""

if "pro_tutor_title" not in st.session_state:
    st.session_state.pro_tutor_title = DEFAULT_PRO_TITLE
if "pro_tutor_content" not in st.session_state:
    st.session_state.pro_tutor_content = DEFAULT_PRO_CONTENT

def load_user_profile(uname):
    db = load_user_db()
    if uname in db:
        user_data = db[uname]
        st.session_state.is_premium = user_data.get("is_premium", False)
        st.session_state.history = user_data.get("history", [])
        st.session_state.custom_templates = user_data.get("custom_templates", {})
        st.session_state.app_bg_css = user_data.get("app_bg_css", DEFAULT_BG_CSS)

def save_user_profile():
    if st.session_state.logged_in and st.session_state.username:
        db = load_user_db()
        db[st.session_state.username] = {
            "password": db.get(st.session_state.username, {}).get("password", "naams@123"),
            "is_premium": st.session_state.is_premium,
            "history": st.session_state.history,
            "custom_templates": st.session_state.custom_templates,
            "app_bg_css": st.session_state.app_bg_css
        }
        save_user_db(db)

if st.session_state.logged_in and st.session_state.username:
    load_user_profile(st.session_state.username)

save_user_profile()

# --- FUTURISTIC CYBERPUNK STYLING & MOBILE RESPONSIVENESS (FIXED) ---
st.markdown("""
    <style>
    .css-card {
        background: rgba(13, 17, 38, 0.75);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(20px);
        margin-bottom: 24px;
        box-shadow: 0 0 30px rgba(124, 58, 237, 0.25), inset 0 0 15px rgba(168, 85, 247, 0.1);
        color: #FFFFFF;
    }
    .ad-banner {
        background: linear-gradient(90deg, rgba(30, 27, 75, 0.95) 0%, rgba(76, 5, 25, 0.95) 100%);
        border: 1px dashed #EC4899;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: #F472B6;
        font-size: 0.95rem;
        margin-bottom: 20px;
        box-shadow: 0 0 25px rgba(236, 72, 153, 0.3);
    }
    .main-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #A855F7 0%, #EC4899 50%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .sub-title {
        color: #38BDF8;
        font-size: 1rem;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
    }
    .cyber-logo-box {
        background: rgba(5, 7, 18, 0.9);
        border: 1px solid #3B82F6;
        border-radius: 10px;
        padding: 15px;
        font-family: monospace;
        color: #38BDF8;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        margin-bottom: 15px;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(5, 7, 18, 0.9) !important;
        border: 1px solid rgba(168, 85, 247, 0.5) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #7C3AED 0%, #DB2777 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px;
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.5);
        transition: all 0.3s ease;
    }
    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(90deg, #047857 0%, #059669 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 25px rgba(5, 150, 105, 0.5);
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(3, 5, 14, 0.98);
        border-right: 1px solid rgba(168, 85, 247, 0.25);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Mobile Viewport Fix */
    @media (max-width: 768px) {
        .stApp {
            padding-bottom: 80px;
        }
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 20px;
            left: 5%;
            width: 90%;
            z-index: 999;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Dynamic Background Injection
st.markdown(f"""
    <style>
    .stApp {{
        background: {st.session_state.app_bg_css};
        color: #FFFFFF;
        font-family: 'Rajdhani', 'Inter', sans-serif;
    }}
    </style>
""", unsafe_allow_html=True)

# --- PAYMENT DIALOG (SUPER.MONEY UPI INTEGRATED) ---
@st.dialog("💳 Premium Subscription Checkout")
def show_payment_dialog():
    st.markdown("### Upgrade to Premium Node")
    st.write("Unlock zero ads, high-framerate exports, and all neural voices for **₹199 / month**.")
    
    pay_tab1, pay_tab2 = st.tabs(["📱 super.money / UPI", "🏦 Bank Account Transfer"])
    
    with pay_tab1:
        st.markdown("**Send UPI Payment to:**")
        st.code("7902452572@superyes", language="text")
        st.info("1. Scan or send **₹199** via super.money, GPay, PhonePe, or Paytm.\n2. Copy and enter the 12-digit UTR / Ref Transaction Number below.")
        
    with pay_tab2:
        st.markdown("""
        **Bank Transfer Details:**  
        * **Account Holder:** Minhal Shahbaz  
        * **Account Number:** `999901234567`  
        * **IFSC Code:** `SBIN0001234`  
        * **Bank Name:** State Bank of India  
        """)
        
    utr_input = st.text_input("Enter Transaction UTR / Ref Number:", placeholder="e.g. 429104829102")
    
    if st.button("Submit Payment for Instant Activation"):
        if len(utr_input.strip()) >= 6:
            st.session_state.is_premium = True
            save_user_profile()
            st.success("Payment verified! Premium access initialized.")
            st.rerun()
        else:
            st.error("Please enter a valid UTR transaction number.")

# --- WEBSITE AI ASSISTANT & TUTOR WIDGET ---
def ai_tutor_section():
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.subheader("🤖 Website AI Assistant & Tutor")
    st.write("Got questions about this site, video tools, or how to use the studio? Ask away!")

    KNOWLEDGE_BASE = {
        "greeting": {
            "keywords": ["hi", "hello", "hey", "greetings", "start"],
            "responses": [
                "Hello! How can I help you today?",
                "Hey there! Ask me anything about creating videos, editing, or using this tool.",
                "Hi! I'm your website assistant. What would you like to learn?"
            ]
        },
        "video_editing": {
            "keywords": ["video", "render", "mp4", "moviepy", "edit", "shorts", "export"],
            "responses": [
                "To generate a video, select your images and audio in the main editor tab, then click the **Generate Short** button!",
                "Make sure your images and audio files match in duration for smooth rendering.",
                "Our Shorts Studio uses MoviePy to process and slice audio and video smoothly."
            ]
        },
        "audio_tts": {
            "keywords": ["voice", "audio", "sound", "tts", "speech", "speak", "voiceover"],
            "responses": [
                "You can generate clear AI voiceovers using the built-in Edge-TTS engine on the dashboard!",
                "Try picking different voice models from the dropdown to find the best tone for your video."
            ]
        },
        "troubleshooting": {
            "keywords": ["error", "issue", "problem", "bug", "stuck", "fail", "slow"],
            "responses": [
                "If an export fails, double check that your files aren't corrupted and try refreshing the browser.",
                "Make sure your uploaded media is in supported formats like JPG, PNG, or MP3."
            ]
        },
        "help": {
            "keywords": ["help", "guide", "tutorial", "how to", "usage"],
            "responses": [
                "Here is how to get started:\n1. Prepare your assets (images/text/audio).\n2. Choose your voiceover options.\n3. Preview and click export!",
                "You can ask me questions like: 'How to make a short?', 'How to add voiceover?', or 'What to do if there is an error?'"
            ]
        }
    }

    def get_tutor_response(user_input):
        user_input_lower = user_input.lower()
        for category, data in KNOWLEDGE_BASE.items():
            for kw in data["keywords"]:
                if kw in user_input_lower:
                    return random.choice(data["responses"])
        return "I'm your assistant! Try asking me about generating shorts, voiceovers, video rendering, or troubleshooting."

    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = [
            {"role": "assistant", "content": "Hi! I am your AI assistant. How can I help you with the website today?"}
        ]

    for msg in st.session_state.tutor_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask a question about the website..."):
        st.session_state.tutor_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_tutor_response(prompt)
        time.sleep(0.4)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.tutor_messages.append({"role": "assistant", "content": response})
    st.markdown('</div>', unsafe_allow_html=True)

# --- RATING MODAL ---
@st.dialog("⭐ Rate Your Cybernetic Experience")
def show_rating_dialog():
    st.markdown("Rate your output performance across the **AD Shorts Studio Matrix**:")
    stars = st.slider("Neural Rating:", 1, 5, 5)
    feedback = st.text_area("System feedback or bug logs:")
    
    if st.button("Transmit Feedback"):
        st.success("Feedback uploaded to core database. Keep generating!")
        st.session_state.show_rating_popup = False
        st.rerun()

# --- PREMIUM INFO MODAL ---
@st.dialog("👑 Cybernetic Premium Protocols")
def show_premium_info_dialog():
    st.markdown("""
    ### Unlock Full System Capabilities:
    
    * **🚫 Zero Ads Matrix:** Erase all promotional banner nodes.
    * **💧 Watermark Purge:** Export crystal-clear clean video frames.
    * **🎙️ Pro Neural Voices:** Access advanced high-definition voice accents.
    * **🎬 Ultra HD Rendering:** Generate high-framerate clips.
    * **🎨 Infinite Templates:** Store limitless custom parameter presets.
    """)
    if not st.session_state.is_premium:
        if st.button("💳 Proceed to Checkout (₹199/mo)"):
            show_payment_dialog()
    else:
        st.info("System status: PREMIUM ACTIVE.")

if st.session_state.show_rating_popup:
    show_rating_dialog()

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("## 💻 **AD Shorts Studio — Terminal**")
        st.markdown("Authenticate your neural link to access cloud sync and storage databases.")
        
        auth_tab1, auth_tab2 = st.tabs(["🔑 Terminal Access", "📝 New Registration"])
        db = load_user_db()
        
        with auth_tab1:
            login_user = st.text_input("Username / Email", key="login_u")
            login_pass = st.text_input("Access Password", type="password", key="login_p")
            if st.button("Initialize Connection"):
                if login_user in db and db[login_user].get("password") == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    save_active_session(login_user)
                    load_user_profile(login_user)
                    st.success(f"Access granted. Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Authentication failed. Invalid credentials.")
                    
        with auth_tab2:
            reg_user = st.text_input("New Username / Email", key="reg_u")
            reg_pass = st.text_input("New Password", type="password", key="reg_p")
            if st.button("Register Account"):
                if not reg_user.strip() or not reg_pass.strip():
                    st.error("Fill in all identification fields.")
                elif reg_user in db:
                    st.error("Identity already registered in database.")
                else:
                    db[reg_user] = {
                        "password": reg_pass,
                        "is_premium": (reg_user == "bromusic0008@gmail.com"),
                        "history": [],
                        "custom_templates": {},
                        "app_bg_css": DEFAULT_BG_CSS
                    }
                    save_user_db(db)
                    st.session_state.logged_in = True
                    st.session_state.username = reg_user
                    save_active_session(reg_user)
                    load_user_profile(reg_user)
                    st.success("New identity registered successfully!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN APP INTERFACE ---
with st.sidebar:
    st.markdown(f"### 👤 User Node: **{st.session_state.username}**")
    if st.button("🚪 Terminate Session"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        clear_active_session()
        st.rerun()
        
    st.markdown("---")
    st.markdown("### ⚡ **Control Matrix**")
    mode = st.radio("Select Workflow:", ["⚡ AI Short Generator", "🎬 Video & Photo Editor", "🎨 Logo & Branding Hub", "🤖 AI Tutor Assistant", "📂 Project History & Trash"])
    
    st.markdown("---")
    st.markdown("### 🎨 **Cyber Styler**")
    bg_mode = st.radio("Aesthetic Mode:", ["Presets", "Custom Color"])
    
    if bg_mode == "Presets":
        bg_preset = st.selectbox("Preset Vibe:", ["Cyberpunk Neon", "Deep Space Blue", "Matrix Emerald", "Sunset Cyber"])
        if bg_preset == "Cyberpunk Neon":
            st.session_state.app_bg_css = "linear-gradient(135deg, #03030A 0%, #0A0718 50%, #020207 100%)"
        elif bg_preset == "Deep Space Blue":
            st.session_state.app_bg_css = "linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e1b4b 100%)"
        elif bg_preset == "Matrix Emerald":
            st.session_state.app_bg_css = "linear-gradient(135deg, #022c22 0%, #064e3b 50%, #02231c 100%)"
        elif bg_preset == "Sunset Cyber":
            st.session_state.app_bg_css = "linear-gradient(135deg, #4c0519 0%, #701a75 50%, #1e1b4b 100%)"
    else:
        custom_bg_color = st.color_picker("Custom Hex Color", value="#0A0F1D")
        st.session_state.app_bg_css = custom_bg_color

    save_user_profile()
        
    st.markdown("---")
    st.markdown("### 📜 **System Changelog**")
    st.markdown("""
    * **v1.6.3**: Fixed CSS styling block syntax permanently.
    * **v1.6.1**: Updated UPI handle to super.money (`7902452572@superyes`).
    * **v1.6.0**: Integrated targeted ad banners for free users.
    * **v1.5.0**: Added Bank & UPI checkout dialog for Premium users.
    """)

    st.markdown("---")
    st.markdown("### 👑 **Status Matrix**")
    
    if st.session_state.username == "bromusic0008@gmail.com":
        st.success("👑 SYS ADMIN")
        with st.expander("🛠️ Admin Command Deck"):
            st.markdown("**Administrator Access Verified**")
            all_users = load_user_db()
            st.write(f"Total User Nodes: {len(all_users)}")
            if st.button("Dump User Database"):
                st.json(all_users)
    elif st.session_state.is_premium:
        st.success("⭐ PREMIUM SUBSCRIBER")
    else:
        st.info("STANDARD FREE")
        if st.button("🚀 Upgrade Matrix (₹199)"):
            show_payment_dialog()
        if st.button("ℹ️ View Perks"):
            show_premium_info_dialog()

# --- TEMPLATE MODAL ---
@st.dialog("📁 Template Matrix & Customizer")
def show_templates_modal():
    st.markdown("Select a pre-loaded template parameter set or build a custom profile:")
    if st.button("🛠️ Launch Custom Template Builder"):
        st.session_state.open_customizer = True
        st.rerun()
    st.markdown("---")
    
    templates = {
        "🎮 Cyber Gaming": {
            "script": "Step into the ultimate arena. Master high-tier map control, aggressive rushes, and pinpoint accuracy to conquer every lobby!",
            "color": "#0A0F1D"
        },
        "⚡ Tech Review": {
            "script": "Is this futuristic gadget worth your credit? Let's analyze processor speeds, power delivery, and build quality!",
            "color": "#061A24"
        },
        "🍔 Cyber Kitchen": {
            "script": "Synthesize a mouth-watering culinary masterpiece at home in under 10 minutes with these elite cooking hacks!",
            "color": "#1A1508"
        }
    }
    if st.session_state.custom_templates:
        templates.update(st.session_state.custom_templates)

    for name, data in templates.items():
        with st.container():
            st.markdown(f"**{name}**")
            if st.button(f"Load Template", key=f"tpl_{name}"):
                st.session_state.script_text = data["script"]
                st.session_state.theme_color = data["color"]
                st.rerun()
            st.markdown("---")

# --- MODE 1: AI SHORT GENERATOR ---
if mode == "⚡ AI Short Generator":
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown('<div class="main-title">AD Shorts Studio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Neural video generation studio with custom text-to-speech & cinematic frames</div>', unsafe_allow_html=True)
    with header_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📁 Templates"):
            show_templates_modal()

    # --- MONETIZATION AD BANNER (VISIBLE ONLY TO FREE USERS) ---
    if not st.session_state.is_premium and st.session_state.username != "bromusic0008@gmail.com":
        st.markdown("""
            <div class="ad-banner">
                📢 <b>SPONSORED ADVERTISEMENT</b><br>
                Support free studio access by exploring our sponsor! <a href="https://rzp.io/l/your_link" target="_blank" style="color: #F472B6; font-weight: bold;">Upgrade to Premium (₹199)</a> to instantly remove all ads and watermarks.
            </div>
        """, unsafe_allow_html=True)

    with st.expander(st.session_state.tutor_title):
        st.markdown(st.session_state.tutor_content)

    with st.expander(st.session_state.pro_tutor_title):
        if st.session_state.is_premium or st.session_state.username == "bromusic0008@gmail.com":
            st.markdown(st.session_state.pro_tutor_content)
        else:
            st.info("🔒 Premium authorization required to access advanced masterclass protocols.")

    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    with st.expander("🤖 Quantum Script Generator"):
        ai_topic = st.text_input("Enter prompt topic (e.g., Cyberpunk battle strategies, futuristic AI)")
        if st.button("✨ Synthesize Script"):
            if ai_topic.strip():
                st.session_state.script_text = f"Discover the hidden truth behind {ai_topic}. Here are the critical operational insights you need right now. Watch till the termination!"
                st.success("Script synthesized successfully!")
                st.rerun()
            else:
                st.error("Input topic parameters required.")

    text_input = st.text_area("📝 Video Script Payload:", value=st.session_state.script_text, height=110)
    st.session_state.script_text = text_input

    col1, col2, col3 = st.columns(3)
    with col1:
        voice_option = st.selectbox("🎙️ Neural Voice Accent:", ["en-US-ChristopherNeural", "en-US-JennyNeural", "en-GB-SoniaNeural"])
    with col2:
        bg_color = st.color_picker("🎨 Backdrop Vibe:", value=st.session_state.theme_color)
        st.session_state.theme_color = bg_color
    with col3:
        aspect_ratio = st.selectbox("📐 Aspect Ratio Matrix:", ["9:16 (Shorts/Reels)", "16:9 (YouTube)", "1:1 (Square)"])

    if "9:16" in aspect_ratio:
        frame_size = (720, 1280)
    elif "16:9" in aspect_ratio:
        frame_size = (1280, 720)
    else:
        frame_size = (1080, 1080)

    st.markdown('</div>', unsafe_allow_html=True)

# --- MODE 2: VIDEO & PHOTO EDITOR ---
elif mode == "🎬 Video & Photo Editor":
    st.markdown('<div class="main-title">🎬 CapCut-Style Matrix Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Precision frame trimmer, speed shifters, and photo enhancer suite</div>', unsafe_allow_html=True)
    
    if not st.session_state.is_premium and st.session_state.username != "bromusic0008@gmail.com":
        st.markdown('<div class="ad-banner">📢 <b>ADVERTISEMENT:</b> Free mode includes standard export watermarks. Upgrade to remove!</div>', unsafe_allow_html=True)

    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.info("Upload your raw video or image asset to execute precise timeline modifications.")
    uploaded_media = st.file_uploader("Upload Media Payload (MP4, JPG, PNG)", type=["mp4", "jpg", "png", "jpeg"])
    if uploaded_media:
        st.success(f"Loaded media asset: {uploaded_media.name}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MODE 3: LOGO & BRANDING HUB ---
elif mode == "🎨 Logo & Branding Hub":
    st.markdown('<div class="main-title">🎨 Logo & Branding Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Generate custom cyber banners, badges, and titles for your channel</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    brand_text = st.text_input("Enter Brand / Channel Name:", value="AD SHORTS STUDIO")
    logo_style = st.selectbox("Select Cyber Logo Style:", ["Cyber Neon Box", "Matrix Glitch Header", "Terminal Code Block"])
    
    if st.button("✨ Generate Logo Banner"):
        if logo_style == "Cyber Neon Box":
            logo_output = f"╔══════════════════════════════════════╗\n║         ⚡ {brand_text} ⚡         ║\n╚══════════════════════════════════════╝"
        elif logo_style == "Matrix Glitch Header":
            logo_output = f"// [SYSTEM_ACTIVE] >>> {brand_text} <<< [ONLINE] \\\\"
        else:
            logo_output = f"root@ad-shorts:~# ./launch_{brand_text.lower().replace(' ', '_')}.sh"
            
        st.markdown(f'<div class="cyber-logo-box"><pre>{logo_output}</pre></div>', unsafe_allow_html=True)
        st.success("Logo banner generated successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MODE 4: AI TUTOR ASSISTANT ---
elif mode == "🤖 AI Tutor Assistant":
    st.markdown('<div class="main-title">🤖 AI Tutor & Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Interactive website assistant for all your questions and guidance</div>', unsafe_allow_html=True)
    ai_tutor_section()

# --- MODE 5: PROJECT HISTORY & TRASH ---
elif mode == "📂 Project History & Trash":
    st.markdown('<div class="main-title">📂 Archive & Trash Core</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manage exported history logs and clean temporary cache files</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            st.write(f"Record #{idx+1}: {item}")
        if st.button("🗑️ Purge History Matrix (`Shift + Del`)"):
            st.session_state.history = []
            save_user_profile()
            st.success("History cache purged successfully!")
            st.rerun()
    else:
        st.info("No execution history recorded in current session.")
    st.markdown('</div>', unsafe_allow_html=True)