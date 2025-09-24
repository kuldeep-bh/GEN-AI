import streamlit as st
from langchain_groq import ChatGroq
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.schema import HumanMessage, AIMessage

# -------------------------
# API keys & LLM setup
# -------------------------
groq_api_key = 'g.................kg'
langsmith = 'ls.................dc'

llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-It")

# -------------------------
# Define State
# -------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Node function
def chatbot_node(state: State):
    return {"messages": llm.invoke(state['messages'])}

# Add node & edges
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# -------------------------
# Streamlit UI
# -------------------------
st.title("Single-Agent Chatbot ")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []  # Stores LangChain Message objects

# User input
user_input = st.text_input("You:", key="input")

if st.button("Send") and user_input:
    # Convert user input to HumanMessage and append
    st.session_state.history.append(HumanMessage(content=user_input))

    # Get bot response from graph
    bot_response = None
    for event in graph.stream({'messages': st.session_state.history}):
        for value in event.values():
            bot_response = value["messages"]  # This is an AIMessage

    if bot_response:
        st.session_state.history.append(bot_response)

# Display chat history
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        st.markdown(f"**You:** {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"**Assistant:** {msg.content}")
