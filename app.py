import os
import streamlit as st
from datetime import datetime
from services import FDAClient, AITranslator
from models import Medication

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="PillSpeak | NCAIR Patient Medication Translator",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM ELEGANT CSS STYLING ---
st.markdown("""
    <style>
    /* Main Background Accent */
    .main {
        background-color: #FAFAFA;
    }

    /* Hero Header Card */
    .ncair-header {
        background: linear-gradient(135deg, #0A2540 0%, #0052CC 100%);
        padding: 2rem;
        border-radius: 12px;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    .ncair-header h1 {
        color: #FFFFFF !important;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .ncair-sub {
        font-size: 1.1rem;
        color: #E2E8F0;
        margin-bottom: 1rem;
    }
    .ncair-badge {
        background-color: rgba(255, 255, 255, 0.15);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* Output Section Card */
    .translation-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-top: 1.5rem;
    }

    /* Primary Action Button Customization */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0052CC 0%, #0747A6 100%);
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,82,204,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []


# Initialize Services
@st.cache_resource
def load_services():
    return FDAClient(), AITranslator()


fda_client, ai_translator = load_services()

# --- HERO BRANDING HEADER ---
st.markdown("""
    <div class="ncair-header">
        <span class="ncair-badge">NCAIR ADVANCED PYTHON PROJECT</span>
        <h1>💊 PillSpeak</h1>
        <p class="ncair-sub">AI-Powered Patient Medication & Clinical Data Translator</p>
        <p style="font-size: 0.9rem; margin-bottom: 0; opacity: 0.9;">
            Translating complex FDA pharmaceutical label data into clear, accessible 5th-grade plain English.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR: HISTORY & CONTROLS ---
st.sidebar.title("📜 Search History")

if st.session_state.history:
    if st.sidebar.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.sidebar.markdown("---")

    for idx, record in enumerate(reversed(st.session_state.history)):
        # Safe extraction of timestamp
        raw_timestamp = record.get("timestamp", "")
        if "T" in str(raw_timestamp):
            date_part = raw_timestamp.split("T")[0]
        else:
            date_part = raw_timestamp or "N/A"

        med_name = record.get("name", "Unknown Medication").capitalize()
        recalled = record.get("is_recalled", False)

        badge_icon = "⚠️" if recalled else "✅"

        with st.sidebar.expander(f"{badge_icon} {med_name} ({date_part})"):
            if recalled:
                st.error(f"**Recall Warning:** {record.get('recall_reason', 'N/A')}")
            st.markdown(record.get("summary", "No summary available."))
else:
    st.sidebar.info("No past searches recorded yet. Search for a medication to start.")

# --- MAIN CONTROLS ---
st.subheader("🔍 Medication Lookup")

col_search, col_btn = st.columns([4, 1], vertical_alignment="bottom")

with col_search:
    med_input = st.text_input(
        "Enter Drug or Generic Brand Name:",
        placeholder="e.g., Paracetamol, Amoxicillin, Aspirin, Metformin...",
        label_visibility="visible"
    )

with col_btn:
    search_clicked = st.button("Translate", type="primary", use_container_width=True)

if search_clicked:
    if not med_input.strip():
        st.warning("Please enter a valid medication name before searching.")
    else:
        med_name = med_input.strip()

        with st.spinner(f"Querying FDA database and generating plain-English summary for '{med_name}'..."):
            # 1. Fetch FDA Data & Recalls
            is_recalled, recall_reason = fda_client.check_recalls(med_name)
            fda_data = fda_client.fetch_drug_info(med_name)

            # 2. Translate via Gemini API
            summary = ai_translator.translate(
                med_name=med_name,
                usage=fda_data.get("usage", ""),
                warnings=fda_data.get("warnings", ""),
                side_effects=fda_data.get("side_effects", ""),
                found_in_fda=fda_data.get("found_in_fda", False),
            )

            # 3. Create Record and save to History
            med_record = Medication(
                name=med_name,
                summary=summary,
                is_recalled=is_recalled,
                recall_reason=recall_reason if is_recalled else "",
            )

            record_dict = med_record.to_dict()
            record_dict["timestamp"] = datetime.now().isoformat()
            st.session_state.history.append(record_dict)

        st.markdown("---")

        # --- METRIC STATUS INDICATORS ---
        m_col1, m_col2, m_col3 = st.columns(3)

        with m_col1:
            st.metric(label="Selected Medication", value=med_name.capitalize())

        with m_col2:
            if fda_data.get("found_in_fda"):
                st.metric(label="openFDA Database", value="Matched", delta="Verified Data")
            else:
                st.metric(label="openFDA Database", value="Offline / General", delta="- Fallback Mode",
                          delta_color="off")

        with m_col3:
            if is_recalled:
                st.metric(label="FDA Recall Status", value="RECALLED", delta="- Active Notice", delta_color="inverse")
            else:
                st.metric(label="FDA Recall Status", value="Clear", delta="No Recalls")

        # Recall Banner Alert
        if is_recalled:
            st.error(f"⚠️ **ACTIVE FDA RECALL ALERT:** {recall_reason}")

        # --- TRANSLATED CARD RESULT ---
        st.markdown('<div class="translation-card">', unsafe_allow_html=True)
        st.markdown(summary)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download Result Option
        st.write("")
        st.download_button(
            label="📥 Download Translation Record (.txt)",
            data=f"PillSpeak Translation Record for {med_name.capitalize()}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{summary}",
            file_name=f"PillSpeak_{med_name.lower()}.txt",
            mime="text/plain"
        )

# --- FOOTER ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption(
    "⚠️ **Disclaimer:** PillSpeak is an AI educational assistant developed for NCAIR project demonstrations. Always verify clinical advice with a licensed healthcare professional.")
