import pymysql
from pymysql.cursors import DictCursor

def get_database_schema(host: str, user: str, password: str, database: str) -> str:
    """
    Fetches database schema information from MySQL information_schema
    and formats it for the system prompt.
    """
    conn = None
    cursor = None
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            cursorclass=DictCursor
        )
        cursor = conn.cursor()

        # Get tables and their columns
        cursor.execute("""
            SELECT 
                t.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.COLUMN_KEY,
                c.ORDINAL_POSITION
            FROM information_schema.TABLES t
            JOIN information_schema.COLUMNS c 
                ON t.TABLE_NAME = c.TABLE_NAME 
                AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
            WHERE t.TABLE_SCHEMA = %s
            ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """, (database,))
        
        # Organize columns by table
        tables = {}
        for row in cursor.fetchall():
            table_name = row['TABLE_NAME']
            if table_name not in tables:
                tables[table_name] = []
            tables[table_name].append(
                f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})"
                + (" [PK]" if row['COLUMN_KEY'] == 'PRI' else "")
            )

        # Get foreign key relationships
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_SCHEMA = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME, COLUMN_NAME
        """, (database,))
        
        relationships = cursor.fetchall()

        # Format the output
        schema_text = "Database Schema:\n\n"
        
        # Add tables and columns
        for table_name, columns in tables.items():
            schema_text += f"Table: {table_name}\n"
            schema_text += f"Columns: {', '.join(columns)}\n\n"

        # Add relationships
        if relationships:
            schema_text += "Foreign Key Relationships:\n"
            for rel in relationships:
                schema_text += (
                    f"- {rel['TABLE_NAME']}.{rel['COLUMN_NAME']} → "
                    f"{rel['REFERENCED_TABLE_NAME']}.{rel['REFERENCED_COLUMN_NAME']}\n"
                )

        return schema_text

    except pymysql.Error as err:
        print(f"Database Error: {err}")
        return ""
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 