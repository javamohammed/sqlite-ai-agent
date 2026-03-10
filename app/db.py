import os
from typing import Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shop_database.db")

engine = create_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

def list_tables() -> list[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_schema(table_name: str) -> list[dict[str, Any]]:
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [
        {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "default": str(col.get("default")),
        }
        for col in columns
    ]

def safe_table_exists(table_name: str) -> bool:
    return table_name in list_tables()

def execute_select(query: str, params: dict | None = None) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return [dict(row) for row in result.mappings().all()]

def execute_write(query: str, params: dict | None = None) -> dict[str, Any]:
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        return {"rowcount": result.rowcount}