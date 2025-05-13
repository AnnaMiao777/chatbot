import streamlit as st
import openai

# Show title and description.

import os
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Privacy Assistant Chatbot")
st.write("Ask questions about how your health data is used.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a privacy assistant in a mobile health app. "
            "Only respond to user questions about data privacy, storage, and usage. "
            "Do not ask the user questions or prompt for data."
        )}
    ]

# User input
user_input = st.text_input("Your question:")

# If user enters a question
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Query OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages
    )

    assistant_reply = response["choices"][0]["message"]["content"]
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# Display chat history
for msg in st.session_state.messages[1:]:  # skip system message
    if msg["role"] == "user":
        st.write(f"**You:** {msg['content']}")
    else:
        st.write(f"**Assistant:** {msg['content']}")
