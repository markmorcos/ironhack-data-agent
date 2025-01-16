import json
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

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

    return response

def get_data_df(sql_query):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_DATABASE")
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
