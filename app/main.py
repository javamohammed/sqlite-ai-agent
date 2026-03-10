from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.agent import ask_agent
from app.schemas import ChatRequest, ChatResponse
from app.tools import (
    list_tables_tool,
    list_tables_with_counts_tool,
    get_schema_tool,
    select_rows_tool,
)

app = FastAPI(title="SQLite AI Agent")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = ask_agent(req.message)
    return ChatResponse(**result)

@app.get("/api/tables")
def get_tables():
    return list_tables_tool()

@app.get("/api/tables-with-counts")
def get_tables_with_counts():
    return list_tables_with_counts_tool()

@app.get("/api/schema/{table_name}")
def get_schema(table_name: str):
    return get_schema_tool(table_name)

@app.get("/api/table-preview/{table_name}")
def get_table_preview(table_name: str):
    return select_rows_tool(table_name=table_name, limit=20)