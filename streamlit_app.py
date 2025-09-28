import streamlit as st
import openai
import os
from PyPDF2 import PdfReader

# Set page title
st.set_page_config(page_title="Privacy Assistant Chatbot", layout="centered")
st.title("🔒 Privacy Assistant Chatbot")
st.write("Ask any question about WellTrack+ Privacy Policy, data use, Privacy Concerns etc.")

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
    f"{policy_text}"
)

FEW_SHOT = [
    {"role":"user","content":"Why do you need my location?"},
    {"role":"assistant","content":"According to the policy, location is used only when you enable features like activity routes or safety checks. It isn’t shared without your permission and you can turn it off any time. Want details about storage or who can see it?"},
    {"role":"user","content":"Will you sell my health data?"},
    {"role":"assistant","content":"No. The policy states your health data is not sold or used for advertising. Sharing with others occurs only if you authorize it, and you can revoke access."}
]

# --- Initialize conversation history ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system","content": system_prompt}] + FEW_SHOT.copy()
    
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
