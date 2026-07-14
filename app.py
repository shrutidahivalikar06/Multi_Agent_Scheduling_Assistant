import streamlit as st
from langchain_core.messages import HumanMessage
from database import initialize_database
from graph import graph
from database import initialize_database


initialize_database()


st.set_page_config(
    page_title="Multi-Agent Scheduling Assistant",
    page_icon="📅",
    layout="centered"
)

st.title("📅 Multi-Agent Scheduling Assistant")
st.caption("Ask me to schedule meetings, check availability, or manage your calendar.")

with st.sidebar:
    st.header("Features")
    st.markdown("""
✅ Book appointments

✅ Check slot availability

✅ View booking details

✅ Relative date understanding

✅ SQLite persistence

✅ Mock notifications
""")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user-1"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    state = {
        "messages": [
            HumanMessage(content=user_input)
        ]
    }

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    try:

        result = graph.invoke(
            state,
            config=config
        )

        assistant_response = result.get(
            "response",
            "Sorry, I couldn't process your request."
        )

    except Exception as e:

        assistant_response = f"❌ Error: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response
        }
    )