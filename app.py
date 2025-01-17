from openai import OpenAI
import streamlit as st
import pandas as pd
from src.tools import get_tools, parse_tool_call
from src.prompts import SYSTEM_PROMPT
from src.functions import plot_figure, get_memories

# Initialize constants and configurations
def init_config():
    """Initialize app configuration"""
    
    st.set_page_config(page_title="Sakila Data Agent", page_icon=":robot:")

    return {
        'tools': get_tools(),
        'prompt': SYSTEM_PROMPT,
        'api_key': st.secrets["OPENAI_API_KEY"]
    }

# Session state management
def init_session_state(system_prompt):
    """Initialize or get session state"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": "How can I help you?"}
        ]

# Message display
def display_message_history():
    """Display chat history with results"""
    for msg in st.session_state.messages[1:]:
        st.chat_message(msg["role"]).write(msg["content"])
        if "result" in msg and msg["result"] is not None:
            display_result(msg)

def display_result(msg):
    """Display data or visualization results"""
    match msg["type"]:
        case "Data":
            df = pd.read_json(msg["result"])
            st.dataframe(df)
        case "Visualization":
            df_json, kind, title = msg["result"]
            df = pd.read_json(df_json)
            plot_figure(df, kind, title)
        case "Export":
            df = pd.read_csv("temp/data.csv")
            binary_data = df.to_csv(index=False).encode("utf-8")
            st.dataframe(df)
            st.download_button(label="Download data", data=binary_data, file_name="data.csv", mime="text/csv")

# Chat handling
def handle_chat_input(prompt, client):
    """Process user input and get AI response"""
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    memories = get_memories(prompt)
    memory_list = "\n".join(memories) if memories else "No relevant memories found."

    st.session_state.messages[0]["content"] = SYSTEM_PROMPT.format(memory_list=memory_list)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        tools=config['tools'],
    )
    
    return parse_tool_call(response.choices[0].message)

def process_response(parsed_response):
    """Process and store AI response"""
    msg = parsed_response.get("msg")
    result = parsed_response.get("result")
    result_type = parsed_response.get("type")

    # Display message first
    st.chat_message("assistant").write(msg)
    
    # Then display and serialize the result
    serialized_result = serialize_result(result, result_type)
    
    # Store in session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": msg,
        "result": serialized_result,
        "type": result_type
    })

def serialize_result(result, result_type):
    """Serialize result data for storage"""
    if result_type == "Data":
        st.dataframe(result)
        return result.to_json()
    
    if result_type == "Visualization":
        df, kind, title = result
        plot_figure(df, kind, title)
        df_json = df.to_json()
        return df_json, kind, title
    
    if result_type == "Export":
        df = pd.read_csv("temp/data.csv")
        binary_data = df.to_csv(index=False).encode("utf-8")
        st.dataframe(df)
        st.download_button(label="Download data", data=binary_data, file_name="data.csv", mime="text/csv")
        return df.to_json()

    return None

# Main app
def main():
    st.title("💬 Sakila Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI to answer questions about the Sakila database")

    init_session_state(config['prompt'])
    display_message_history()

    if prompt := st.chat_input():
        if not config['api_key']:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI()
        parsed_response = handle_chat_input(prompt, client)
        process_response(parsed_response)

# Initialize app configuration
config = init_config()

# Run the app
if __name__ == "__main__":
    main()