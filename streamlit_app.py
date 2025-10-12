import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
import csv
from uuid import uuid4
from datetime import datetime, timezone


# Set page title
st.set_page_config(page_title="Privacy Assistant Chatbot", layout="centered")
st.title("🔒 Privacy Assistant Chatbot")
st.write("Ask any question about WellTrack+ Privacy Policy, data use, Privacy Concerns etc.")

# ====== LOGGING CONFIG ======
LOG_DIR = os.environ.get("CHAT_LOG_DIR", "./logs")
CSV_FIELDS = ["timestamp", "session_id", "turn_index", "role", "content"]

def today_log_path() -> str:
    """Return the daily CSV log path like logs/chat_YYYY-MM-DD.csv (UTC date)."""
    os.makedirs(LOG_DIR, exist_ok=True)
    day_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"chat_{day_str}.csv")

def ensure_csv_header(path: str):
    """Create CSV with header if missing."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

def log_message(session_id: str, turn_index: int, role: str, content: str):
    """Append single message row to today's CSV log."""
    path = today_log_path()
    ensure_csv_header(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "turn_index": turn_index,
            "role": role,
            "content": content
        })


# --- Load and preprocess privacy policy PDF ---
@st.cache_data(show_spinner=False)
def load_policy_text(file_path="WellTrack policy.pdf", max_chars=20000):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text[:max_chars]
    except Exception as e:
        return f"Error reading PDF: {e}"

policy_text = load_policy_text()

# --- Create system prompt with policy content ---
system_prompt = (
    "You are a helpful, warm, conversational and accurate privacy assistant embedded in a mobile health app-WellTrack+.\n"
    "Use the following privacy policy as your main reference. Always respond in a natural, user-friendly way.\n\n"
    "avoiding repetition. If the question is unclear, ask for clarification.\n\n"
    "1. Fatigue handling\n"
    "   - If the user says they feel tired, confused, overwhelmed, or asks for less detail:\n"
    "       • Switch to TL;DR mode immediately.\n"
    "       • Provide only TWO options (safer vs. convenient).\n"
    "       • Add ONE short risk line if Medium/High.\n"
    "       • Keep steps to ONE key instruction for each option.\n\n"
    "2. Risk-sensitive guidance\n"
    "   - For each disclosure decision, classify the risk as Low / Medium / High using the policy.\n"
    "   - If Medium/High:\n"
    "       • Add ONE short consequence line (why it matters).\n"
    "       • Suggest a safer alternative aligned with the user’s goal.\n"
    "       • Provide a simple step to undo if they change their mind later.\n\n"
    "Here are examples of how you should answer:\n"
    "- User: Why does the app need my location?\n"
    "- Assistant: The app uses your location to provide more accurate activity tracking "
    "and recommendations. Your location is never shared without your consent.\n\n"
    "- User: Will my health data be sold to others?\n"
    "- Assistant: No, your health data is not sold. It is only used to improve your "
    "experience, and you can control sharing in your settings.\n\n"
    "Now continue the conversation using the privacy policy below as reference:\n\n"
    f"{policy_text}"
)


# --- Initialize conversation history ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content": system_prompt}]
    
# --- Input from user ---
user_input = st.text_input("💬 Your question:", placeholder="e.g., Why do you need my location?")

if user_input:
    # Append user's question to the chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call OpenAI API
    try:
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            assistant_reply = response["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        assistant_reply = None

# --- Display chat history ---
if st.session_state.messages:
    for msg in st.session_state.messages[1:]:  # Skip system prompt
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Assistant:** {msg['content']}")
