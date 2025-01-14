from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from tools import get_tools, parse_tool_call
from prompts import get_prompt
load_dotenv()

tools = get_tools()
prompt = get_prompt()

openai_api_key = os.getenv("OPENAI_API_KEY")

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": prompt},
        {"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        tools=tools,
    )

    parsed_response = parse_tool_call(response.choices[0].message)
    msg = parsed_response["msg"]
    df = parsed_response["df"]
    
    if df is not None:
        st.dataframe(df)

    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)