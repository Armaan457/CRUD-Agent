import os
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain.chains.api.prompt import API_URL_PROMPT
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_mistralai import ChatMistralAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode
from dotenv import load_dotenv

load_dotenv()


def build_agent_graph(api_spec):
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    llm = ChatMistralAI(model="mistral-small-2506", api_key=mistral_api_key)
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

    graph_builder = StateGraph(ChainState)
    graph_builder.add_node("call_tool", acall_request_chain)
    graph_builder.add_node("execute_tool", ToolNode(tools))
    graph_builder.add_node("call_model", acall_model)
    graph_builder.set_entry_point("call_tool")
    graph_builder.add_edge("call_tool", "execute_tool")
    graph_builder.add_edge("execute_tool", "call_model")
    graph_builder.add_edge("call_model", END)
    chain = graph_builder.compile()
    return chain, ChainState
