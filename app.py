import os

import streamlit as st
from dotenv import load_dotenv

from qa import answer_with_gemini


def main():
    st.set_page_config(page_title="ME Course Chatbot", page_icon="🤖", layout="centered")
    st.title("ME Course Q&A Chatbot")
    st.caption("Answers questions using the provided fictional course catalog (via Gemini).")

    load_dotenv()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.subheader("Setup")
        has_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
        st.write("**Gemini API key**:", "Detected" if has_key else "Missing")
        st.markdown(
            "Add `GEMINI_API_KEY` to a `.env` file (see `.env.example`). "
            "Get a free key from [Google AI Studio](https://aistudio.google.com/)."
        )
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()

    # Render chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask about prerequisites, credits, slot clashes, etc.")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                ans = answer_with_gemini(user_question=prompt, chat_history=st.session_state.messages)
            except Exception as e:
                ans = (
                    "I couldn't reach Gemini right now. "
                    "Double-check that your `GEMINI_API_KEY` is set correctly in `.env`.\n\n"
                    f"Error: `{e}`"
                )
        st.markdown(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})


if __name__ == "__main__":
    main()

