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
                        "sql_query": {"type": "string"}
                    },
                    "required": ["sql_query"]
                },
            },
        }
    ]

def parse_tool_call(message):
    response = {
        "msg": message.content,
        "df": None
    }

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_call_arguments = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "get_data_df":
                df = get_data_df(tool_call_arguments["sql_query"])
                response["msg"] = "Find the results in the dataframe"
                response["df"] = df
    
    return response

def get_data_df(sql_query):
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    connection_string = f"mysql+pymysql://{user}:{password}@localhost/sakila"
    engine = create_engine(connection_string)

    with engine.connect() as connection:    
        query = text(sql_query)
        result = connection.execute(query)
        df = pd.DataFrame(result.all())

    return df