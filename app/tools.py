from typing import Any
from sqlalchemy import text
from app.db import engine, list_tables, get_table_schema, safe_table_exists

def list_tables_tool() -> dict[str, Any]:
    return {
        "success": True,
        "action": "list_tables",
        "tables": list_tables()
    }

def get_schema_tool(table_name: str) -> dict[str, Any]:
    if not safe_table_exists(table_name):
        return {"success": False, "error": f"Table '{table_name}' does not exist."}

    schema = get_table_schema(table_name)
    return {
        "success": True,
        "action": "get_schema",
        "table": table_name,
        "schema": schema
    }

def select_rows_tool(
    table_name: str,
    columns: list[str] | None = None,
    where: dict[str, Any] | None = None,
    limit: int = 20
) -> dict[str, Any]:
    if not safe_table_exists(table_name):
        return {"success": False, "error": f"Table '{table_name}' does not exist."}

    cols = ", ".join(columns) if columns else "*"
    query = f"SELECT {cols} FROM {table_name}"
    params = {}

    if where:
        clauses = []
        for i, (key, value) in enumerate(where.items()):
            p = f"w_{i}"
            clauses.append(f"{key} = :{p}")
            params[p] = value
        query += " WHERE " + " AND ".join(clauses)

    query += " LIMIT :limit_value"
    params["limit_value"] = max(1, min(limit, 200))

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        rows = [dict(r) for r in result.mappings().all()]

    columns_out = list(rows[0].keys()) if rows else (columns or [])

    return {
        "success": True,
        "action": "select",
        "table": table_name,
        "columns": columns_out,
        "rows": rows,
        "count": len(rows)
    }

def insert_row_tool(table_name: str, values: dict[str, Any]) -> dict[str, Any]:
    if not safe_table_exists(table_name):
        return {"success": False, "error": f"Table '{table_name}' does not exist."}
    if not values:
        return {"success": False, "error": "No values provided."}

    cols = ", ".join(values.keys())
    placeholders = ", ".join(f":{k}" for k in values.keys())
    query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    with engine.begin() as conn:
        result = conn.execute(text(query), values)

    return {
        "success": True,
        "action": "insert",
        "table": table_name,
        "message": "Insert executed successfully.",
        "rowcount": result.rowcount
    }

def update_rows_tool(
    table_name: str,
    values: dict[str, Any],
    where: dict[str, Any]
) -> dict[str, Any]:
    if not safe_table_exists(table_name):
        return {"success": False, "error": f"Table '{table_name}' does not exist."}
    if not values:
        return {"success": False, "error": "No values provided for update."}
    if not where:
        return {"success": False, "error": "WHERE clause is required for update."}

    params = {}
    set_parts = []
    where_parts = []

    for key, value in values.items():
        p = f"set_{key}"
        set_parts.append(f"{key} = :{p}")
        params[p] = value

    for key, value in where.items():
        p = f"where_{key}"
        where_parts.append(f"{key} = :{p}")
        params[p] = value

    query = f"""
    UPDATE {table_name}
    SET {", ".join(set_parts)}
    WHERE {" AND ".join(where_parts)}
    """

    with engine.begin() as conn:
        result = conn.execute(text(query), params)

    return {
        "success": True,
        "action": "update",
        "table": table_name,
        "message": "Update executed successfully.",
        "rowcount": result.rowcount
    }

def delete_rows_tool(table_name: str, where: dict[str, Any]) -> dict[str, Any]:
    if not safe_table_exists(table_name):
        return {"success": False, "error": f"Table '{table_name}' does not exist."}
    if not where:
        return {"success": False, "error": "WHERE clause is required for delete."}

    params = {}
    where_parts = []

    for key, value in where.items():
        p = f"where_{key}"
        where_parts.append(f"{key} = :{p}")
        params[p] = value

    query = f"DELETE FROM {table_name} WHERE {' AND '.join(where_parts)}"

    with engine.begin() as conn:
        result = conn.execute(text(query), params)

    return {
        "success": True,
        "action": "delete",
        "table": table_name,
        "message": "Delete executed successfully.",
        "rowcount": result.rowcount
    }

def list_tables_with_counts_tool() -> dict[str, Any]:
    tables = list_tables()
    results = []

    with engine.connect() as conn:
        for table_name in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) AS count FROM {table_name}"))
                row_count = result.scalar_one()
            except Exception:
                row_count = None

            results.append({
                "name": table_name,
                "row_count": row_count
            })

    return {
        "success": True,
        "action": "list_tables_with_counts",
        "tables": results
    }