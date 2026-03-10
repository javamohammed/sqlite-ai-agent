import os
import json
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from app.tools import (
    list_tables_tool,
    get_schema_tool,
    select_rows_tool,
    insert_row_tool,
    update_rows_tool,
    delete_rows_tool,
)

load_dotenv()

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

@tool
def list_tables() -> str:
    """Return all database table names."""
    return json.dumps(list_tables_tool())

@tool
def get_schema(table_name: str) -> str:
    """Return schema for a given table name."""
    return json.dumps(get_schema_tool(table_name))

@tool
def select_rows(
    table_name: str,
    columns: list[str] | None = None,
    where: dict | None = None,
    limit: int = 20
) -> str:
    """Read rows from a table."""
    return json.dumps(select_rows_tool(table_name, columns, where, limit))

@tool
def insert_row(table_name: str, values: dict) -> str:
    """Insert one row into a table."""
    return json.dumps(insert_row_tool(table_name, values))

@tool
def update_rows(table_name: str, values: dict, where: dict) -> str:
    """Update rows in a table. WHERE is required."""
    return json.dumps(update_rows_tool(table_name, values, where))

@tool
def delete_rows(table_name: str, where: dict) -> str:
    """Delete rows from a table. WHERE is required."""
    return json.dumps(delete_rows_tool(table_name, where))

tools = [list_tables, get_schema, select_rows, insert_row, update_rows, delete_rows]

system_prompt = """
You are an English database assistant for a local SQLite database.

Rules:
1. All final user-facing replies must be in English.
2. You may read, insert, update, and delete records.
3. Inspect table names and schema whenever needed.
4. Never invent table or column names.
5. If the request is ambiguous, explain what is missing.
6. For UPDATE and DELETE, execute directly if enough information is available.
7. Keep final answers concise and clear.
8. When returning results from SELECT, summarize them briefly in English.
"""

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

def _extract_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return "\n".join(text_parts).strip()

    return str(content)

def _try_parse_json(value: str):
    try:
        return json.loads(value)
    except Exception:
        return None

def ask_agent(user_message: str) -> dict:
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )

    messages = response.get("messages", [])
    final_text = ""
    tool_payload = None

    for msg in messages:
        msg_type = getattr(msg, "type", "")
        content = getattr(msg, "content", None)

        if msg_type == "tool":
            parsed = _try_parse_json(content)
            if isinstance(parsed, dict):
                tool_payload = parsed

    if messages:
        final_text = _extract_text(getattr(messages[-1], "content", "")) or "Done."

    if not tool_payload:
        return {
            "response": final_text,
            "result_type": "message",
            "columns": [],
            "rows": [],
            "meta": {}
        }

    if tool_payload.get("success") is False:
        return {
            "response": tool_payload.get("error", "An error occurred."),
            "result_type": "message",
            "columns": [],
            "rows": [],
            "meta": tool_payload
        }

    action = tool_payload.get("action")

    if action == "select":
        return {
            "response": final_text or f"Found {tool_payload.get('count', 0)} rows.",
            "result_type": "table",
            "columns": tool_payload.get("columns", []),
            "rows": tool_payload.get("rows", []),
            "meta": {
                "table": tool_payload.get("table"),
                "count": tool_payload.get("count", 0)
            }
        }

    if action == "get_schema":
        schema_rows = tool_payload.get("schema", [])
        columns = ["name", "type", "nullable", "default"]
        return {
            "response": final_text or f"Schema for table {tool_payload.get('table')}.",
            "result_type": "table",
            "columns": columns,
            "rows": schema_rows,
            "meta": {
                "table": tool_payload.get("table"),
                "count": len(schema_rows)
            }
        }

    if action == "list_tables":
        table_rows = [{"table_name": name} for name in tool_payload.get("tables", [])]
        return {
            "response": final_text or "Here are the available tables.",
            "result_type": "table",
            "columns": ["table_name"],
            "rows": table_rows,
            "meta": {
                "count": len(table_rows)
            }
        }

    return {
        "response": final_text or tool_payload.get("message", "Operation completed."),
        "result_type": "message",
        "columns": [],
        "rows": [],
        "meta": {
            "action": action,
            "table": tool_payload.get("table"),
            "rowcount": tool_payload.get("rowcount", 0),
            "message": tool_payload.get("message", "")
        }
    }