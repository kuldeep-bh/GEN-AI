import streamlit as st
import time
from langchain_groq import ChatGroq
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# -------------------------
# Groq API setup
# -------------------------
groq_api_key = 'gs.............................kg'  # Replace with your actual key
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-It")

# -------------------------
# State definition
# -------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]
    sentiment: str

# -------------------------
# Node functions
# -------------------------
def preprocess(state: State) -> State:
    cleaned = state["messages"][-1].content.strip()
    state["messages"][-1].content = cleaned
    return state

def analyze_sentiment(state: State) -> State:
    msg = state["messages"][-1].content.lower()
    if "good" in msg or "happy" in msg or "great" in msg:
        state["sentiment"] = "positive"
    elif "bad" in msg or "sad" in msg or "angry" in msg:
        state["sentiment"] = "negative"
    else:
        state["sentiment"] = "neutral"
    return state

def chatbot(state: State) -> State:
    return {"messages": llm.invoke(state['messages'])}

def logger(state: State) -> State:
    print(f"LOG: {state['messages'][-1].content}, Sentiment: {state.get('sentiment')}")
    return state

# -------------------------
# Build the state graph
# -------------------------
builder = StateGraph(State)
builder.add_node("preprocess", preprocess)
builder.add_node("analyze_sentiment", analyze_sentiment)
builder.add_node("chatbot", chatbot)
builder.add_node("logger", logger)

builder.add_edge(START, "preprocess")
builder.add_edge("preprocess", "analyze_sentiment")
builder.add_edge("analyze_sentiment", "chatbot")
builder.add_edge("chatbot", "logger")
builder.add_edge("logger", END)

graph = builder.compile()

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for background and chat style
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: linear-gradient(to bottom right, #e0f7fa, #ffe0b2);
    }
    /* Chat container */
    .user-message {
        background-color: #FFD700;
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 5px;
        text-align: right;
        font-weight: bold;
    }
    .bot-message {
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 5px;
        font-weight: bold;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center; color: #4B0082;'>🤖 LangGraph + Groq Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: #555;'>A colorful chat with background, emojis, and sentiment highlights!</p>", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("Your Message:")

def get_sentiment_color_emoji(sentiment):
    if sentiment == "positive":
        return "#32CD32", "😄"
    elif sentiment == "negative":
        return "#FF6347", "😟"
    else:
        return "#A9A9A9", "😐"

if st.button("Send") and user_input.strip() != "":
    # Append user message first
    st.session_state.chat_history.append({"user": user_input, "bot": None, "sentiment": None})

    # Simulate bot typing
    with st.spinner("Bot is typing..."):
        time.sleep(1)
        state = graph.invoke({"messages": ("user", user_input)})
        response = state['messages'][-1].content
        sentiment = state['sentiment']

        # Update chat history
        st.session_state.chat_history[-1]["bot"] = response
        st.session_state.chat_history[-1]["sentiment"] = sentiment

        logger(state)

# Display chat history with modern bubbles
for chat in st.session_state.chat_history:
    user_col, bot_col = st.columns([1, 3])
    with user_col:
        st.markdown(f"<div class='user-message'>👤 {chat['user']}</div>", unsafe_allow_html=True)
    with bot_col:
        if chat["bot"]:
            color, emoji = get_sentiment_color_emoji(chat["sentiment"])
            st.markdown(f"<div class='bot-message' style='background-color:{color};'>🤖 {chat['bot']} {emoji}<br><small>Sentiment: {chat['sentiment']}</small></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='bot-message' style='background-color:#888;'>🤖 ...</div>", unsafe_allow_html=True)
