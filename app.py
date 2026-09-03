import streamlit as st

from models import Medication
from services import FDAClient, AITranslator
from storage import HistoryManager
from utils import TextSanitizer


st.set_page_config(
    page_title="PillSpeak - Medication Translator",
    page_icon="💊",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Font & Dynamic Base Styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Primary Action Buttons (Search & Download) */
    div.stButton > button:first-child {
        background-color: #0284c7;
        color: #ffffff !important;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #0369a1;
        color: #ffffff !important;
        border: none;
    }

    /* Input Field & Sidebar Border Tweaks */
    .stTextInput input {
        border-radius: 8px;
    }

    /* Theme-Adaptive Card Containers */
    div[data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid var(--border-color, rgba(128, 128, 128, 0.2));
    }
    </style>
""",
    unsafe_allow_html=True,
)
# Minimal, deliberate styling on top of Streamlit's defaults



@st.cache_resource
def load_services():
    fda_client = FDAClient()
    storage = HistoryManager("history.json")
    try:
        translator = AITranslator()
    except ValueError:
        translator = None
    return fda_client, storage, translator


fda_client, storage, translator = load_services()

# --- SIDEBAR: Search History ---
with st.sidebar:
    st.header("Search History")
    records = storage.load_history()

    if records:
        for rec in reversed(records):
            status = "🚨 Recalled" if rec.get("is_recalled") else "✅ No recall"
            with st.expander(f"{rec['name']} — {status}"):
                st.caption(rec.get("timestamp", ""))
                if rec.get("is_recalled"):
                    st.warning(rec.get("recall_reason", ""))
                st.markdown(rec.get("summary", ""))

        st.divider()
        if st.button("Clear History", use_container_width=True):
            storage.clear_history()
            st.rerun()
    else:
        st.caption("No searches yet. Look up a medication to get started.")

# --- MAIN ---
st.title("💊 PillSpeak")
st.caption(
    "Look up a medication, check for FDA recalls, and get its official "
    "label information translated into plain, everyday language."
)

if translator is None:
    st.warning(
        "AI translation is unavailable — no Gemini API key was found. "
        "Set the `GEMINI_API_KEY` (or `PillSpeak`) environment variable and restart the app.",
        icon="⚠️",
    )

st.divider()

col1, col2 = st.columns([4, 1])
with col1:
    raw_name = st.text_input(
        "Medication name",
        placeholder="e.g. Paracetamol, Amoxicillin, Aspirin",
        label_visibility="collapsed",
    )
with col2:
    search_clicked = st.button("Search", use_container_width=True)

if search_clicked:
    try:
        med_name = TextSanitizer.validate_med_name(raw_name)
    except ValueError as ve:
        st.warning(str(ve))
        med_name = None

    if med_name:
        with st.spinner(f"Looking up '{med_name}'..."):
            try:
                raw_data = fda_client.fetch_drug_info(med_name)
                is_recalled, recall_msg = fda_client.check_recalls(med_name)

                if is_recalled:
                    st.error(f"🚨 **Active recall notice found:** {recall_msg}")
                else:
                    st.success("✅ No active FDA recall notices found.")

                if translator:
                    with st.spinner("Translating into plain language..."):
                        summary = translator.translate(
                            med_name=med_name,
                            usage=raw_data["usage"],
                            warnings=raw_data["warnings"],
                            side_effects=raw_data["side_effects"],
                            found_in_fda=raw_data["found_in_fda"],
                        )
                else:
                    summary = "AI translation unavailable (missing API key)."

                if not raw_data["found_in_fda"]:
                    st.caption(
                        "This medication wasn't found in the FDA label database — "
                        "the summary below is from general AI knowledge instead."
                    )

                st.subheader(f"Patient Guide: {med_name}")
                st.markdown(summary)

                storage.save_medication(
                    Medication(
                        name=med_name,
                        summary=summary,
                        is_recalled=is_recalled,
                        recall_reason=recall_msg,
                    )
                )
                st.toast("Saved to search history", icon="💾")

            except ConnectionError as conn_err:
                st.error(f"Network error: {conn_err}")
            except Exception as err:
                st.error(f"Something went wrong: {err}")

st.divider()
st.caption(
    "⚠️ PillSpeak is an informational tool, not medical advice. "
    "Always consult a doctor or pharmacist about your medications."
)
