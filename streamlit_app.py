import streamlit as st
from openai import OpenAI

# Show title and description.
openai.api_key = "k-proj-0bpKiXnwdH5uUIUtmCKN9tZ72Y0PWTIVMWLxoN01DkWQbdzoqJpJiHE1z0jDpMCpLHHkLgaqf3T3BlbkFJ21Lb04RAK8CFTYvjaFNLA7XR8mhJJfjIKxtSVlqniIGBvfRwn2TahRwq2pdJQU8e7EIbCIb1sA"

st.title("💬 Privacy Assistant")
st.write("Ask any questions about how your personal health data is collected or used.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a privacy assistant in a mobile health app. "
            "Your job is to clearly explain privacy-related concepts. "
            "Answer questions about how data (e.g., location, health status) is collected, used, or protected. "
            "Do not initiate questions. Only answer the user's input. Keep responses clear, brief, and helpful."
        )}
    ]

user_input = st.text_input("Type your question:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
            messages=st.session_state.messages
        )
        reply = response["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.write(f"**Assistant:** {reply}")


