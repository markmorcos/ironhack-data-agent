import json
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import os
from  pinecone import Pinecone
from openai import OpenAI
from datetime import datetime, timezone

def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_data_df",
                "description": "Get data from a database and return it as a pandas dataframe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "msg": {"type": "string"},
                        "sql_query": {"type": "string"},
                    },
                    "required": ["msg", "sql_query"]
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "visualize_data",
                "description": "Get data from a database and visualize it with a plot, only return 2 columns, string and number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "msg": {"type": "string"},
                        "sql_query": {"type": "string"},
                        "kind": {"type": "string", "enum": ["bar", "line", "pie", "hist"]},
                        "title": {"type": "string"},
                    },
                    "required": ["msg", "sql_query", "kind", "title"]
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "save_memory",
                "description": "Save what the user likes in a vector database",
                "parameters": {
                    "type": "object",
                    "properties": {"memory": {"type": "string"}},
                    "required": ["memory"]
                }
            }
        },
 {
            "type": "function",
            "function": {
                "name": "export_data",
                "description": "Export data to a csv file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "msg": {"type": "string"},
                        "sql_query": {"type": "string"},
                    },
                    "required": ["msg", "sql_query"]
                }
            }
        },
    ]

def parse_tool_call(message):
    response = {
        "msg": message.content,
        "result": None,
        "type": None
    }

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_call_arguments = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "get_data_df":
                df = get_data_df(tool_call_arguments["sql_query"])
                response["msg"] = tool_call_arguments["msg"]
                response["result"] = df
                response["type"] = "Data"

            if tool_call.function.name == "visualize_data":
                result = visualize_data(tool_call_arguments["sql_query"], tool_call_arguments["kind"], tool_call_arguments["title"])
                response["msg"] = tool_call_arguments["msg"]
                response["result"] = result
                response["type"] = "Visualization"

            if tool_call.function.name == "export_data":
                export_data(tool_call_arguments["sql_query"])
                response["msg"] = "Click the button to download the data"
                response["type"] = "Export"

    return response

def get_data_df(sql_query):
    user = st.secrets["DB_USER"]
    password = st.secrets["DB_PASSWORD"]
    host = st.secrets["DB_HOST"]
    database = st.secrets["DB_DATABASE"]
    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    engine = create_engine(connection_string)

    with engine.connect() as connection:    
        query = text(sql_query)
        result = connection.execute(query)
        df = pd.DataFrame(result.all())

    return df

def visualize_data(sql_query, kind, title):
    df = get_data_df(sql_query)
    return df, kind, title

def save_memory(msg):
    INDEX_NAME = st.secrets["PINECONE_INDEX"]
    PINECONE_NAMESPACE = st.secrets["PINECONE_NAMESPACE"]
    PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

    pc = Pinecone(PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    client = OpenAI()

    embedding = client.embeddings.create(input=msg, model="text-embedding-ada-002")
    vector = embedding.data[0].embedding

    documents = [
        {
            "id": msg,
            "values": vector,
            "metadata": {
                "payload": msg,
                "timestamp": str(datetime.now(tz=timezone.utc)),
                "type": "recall"
            },
        }
    ]

    index.upsert(vectors=documents, namespace=PINECONE_NAMESPACE)

def export_data(sql_query):
    df = get_data_df(sql_query)
    if not os.path.exists("temp"): os.makedirs("temp")
    df.to_csv("temp/data.csv", index=False)
    return df
