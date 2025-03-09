import os
import asyncio
import requests
import streamlit as st
from dotenv import load_dotenv
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain.chains.api.prompt import API_URL_PROMPT
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.messages import BaseMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode

load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

llm = ChatMistralAI(model="mistral-small-latest", api_key=mistral_api_key)

api_spec_url = "http://127.0.0.1:8000/swagger.json"
api_spec = requests.get(api_spec_url).text

toolkit = RequestsToolkit(requests_wrapper=TextRequestsWrapper(headers={}), allow_dangerous_requests=True)
tools = toolkit.get_tools()

api_request_chain = (
    API_URL_PROMPT.partial(api_docs=api_spec)
    | llm.bind_tools(tools, tool_choice="any")
)

class ChainState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

async def acall_request_chain(state: ChainState, config: RunnableConfig):
    last_message = state["messages"][-1]
    response = await api_request_chain.ainvoke({"question": last_message.content}, config)
    return {"messages": [response]}

async def acall_model(state: ChainState, config: RunnableConfig):
    response = await llm.ainvoke(state["messages"], config)
    return {"messages": [response]}

async def process_query(prompt):
    events = chain.astream({"messages": [("user", prompt)]}, stream_mode="values")
    flow = []
    async for event in events:
        flow.append(event["messages"][-1].content)
    return flow[-1]

graph_builder = StateGraph(ChainState)
graph_builder.add_node("call_tool", acall_request_chain)
graph_builder.add_node("execute_tool", ToolNode(tools))
graph_builder.add_node("call_model", acall_model)
graph_builder.set_entry_point("call_tool")
graph_builder.add_edge("call_tool", "execute_tool")
graph_builder.add_edge("execute_tool", "call_model")
graph_builder.add_edge("call_model", END)
chain = graph_builder.compile()

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
        response = asyncio.run(process_query(prompt)) 
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)   
