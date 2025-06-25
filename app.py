import asyncio
import requests
import streamlit as st
from agent_graph import build_agent_graph


st.title("Database CRUD ChatBot")

if "api_spec" not in st.session_state:
    api_spec_url = st.text_input("Enter API specification URL")
    connect_clicked = st.button("Connect to the API Server")
else:
    api_spec_url = None
    connect_clicked = False

api_spec = None
connection_success = False
connection_error = None

if "api_spec" in st.session_state:
    api_spec = st.session_state["api_spec"]
    connection_success = True

if connect_clicked:
    try:
        response = requests.get(api_spec_url, timeout=5)
        response.raise_for_status()
        api_spec = response.text
        st.session_state["api_spec"] = api_spec
        connection_success = True
        st.success("Connected to API server!")
    except:
        st.session_state.pop("api_spec", None)
        st.error(f"Failed to connect: Check the URL or the server status.")

if connection_success and api_spec:
    chain, ChainState = build_agent_graph(api_spec)

    async def process_query(messages):
        formatted_messages = [(msg["role"], msg["content"]) for msg in messages]
        events = chain.astream({"messages": formatted_messages}, stream_mode="values")
        flow = []
        async for event in events:
            flow.append(event["messages"][-1].content)
        return flow[-1]

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {"role": "assistant", "content": "Hi I am a chatbot that perform CRUD operations on a db. How can I help you today?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt:= st.chat_input(placeholder="What is your question?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            response = asyncio.run(process_query(st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
else:
    if "api_spec" not in st.session_state:
        st.info("Please connect to the API server to start chatting.")
