from db_schema_fetcher import get_database_schema


HOST = "localhost"
USER = "root"
PASSWORD = "password"
DATABASE = "sakila"

schema = get_database_schema(HOST, USER, PASSWORD, DATABASE)

SYSTEM_PROMPT = """
You are a helpful assistant that can answer questions about the database.

Tables, columns and relationships are:

{schema}
"""

def get_prompt() -> str:
    """
    Returns the system prompt with the current database schema.
    """
    return SYSTEM_PROMPT.format(schema=schema)