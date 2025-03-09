import os
import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

from tools import create_tool, retrieve_tool, update_tool, delete_tool

from dotenv import load_dotenv
import os
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

llm = ChatMistralAI(model="mistral-large-latest", groq_api_key = mistral_api_key)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an intelligent assistant that helps users manage their database. You can create, read, update, and delete records using the provided REST APIs. Ensure to execute each CRUD operation only once."
            "During the update operation, do not change any other info other than requested by the user, first retrieve info about the item then send the update request with the id and new info"
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

tools = [create_tool, retrieve_tool, update_tool, delete_tool]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

st.title("Database CRUD ChatBot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi I am a chatbot that perform CRUD operations on a db. How can I help you today?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt:= st.chat_input(placeholder="What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False, collapse_completed_thoughts = False)
        response = agent_executor.invoke(
            {"input": prompt}, {"callbacks": [st_cb]}
        )
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        st.write(response["output"])   