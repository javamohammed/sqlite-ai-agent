# SQLite AI Agent 🤖🗄️

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![LangChain](https://img.shields.io/badge/LangChain-AI%20Agent-purple)
![OpenAI](https://img.shields.io/badge/OpenAI-LLM-black)

An **AI-powered database assistant** that lets you interact with a **local SQLite database using natural language**.

This project combines **FastAPI**, **LangChain**, and **OpenAI models** to create a smart interface where users can:

* Browse database tables
* View schemas
* Preview rows
* Query data
* Insert records
* Update records
* Delete records

All directly from a **web interface or chat commands**.

---

# ✨ Features

### AI Database Assistant

* Natural language database queries
* Supports **SELECT / INSERT / UPDATE / DELETE**

### Smart Web Interface

* AI chat interface
* HTML table rendering
* Chat history stored locally
* Clear chat button

### Database Explorer

* Sidebar with all tables
* Search tables instantly
* Row count badges
* View table schema
* Preview first 20 rows
* Auto-select table after AI operations

---

# 🧠 Example Commands

Users can type instructions like:

```
Show me the first 10 users
Show the schema of the orders table
Insert a new user with name John Doe
Update the status to shipped where id is 10
Delete the user where id is 7
```

The AI agent automatically:

1. Inspects the schema
2. Chooses the correct tool
3. Executes the database operation
4. Returns formatted results

---

# 🏗️ Architecture

```
User Interface
      │
      ▼
Frontend (HTML + JS)
      │
      ▼
FastAPI Backend
      │
      ▼
LangChain AI Agent
      │
      ▼
Database Tools Layer
      │
      ▼
SQLite Database
```

---

# 🗂️ Project Structure

```
sqlite-ai-agent/
│
├── app/
│   ├── main.py
│   ├── db.py
│   ├── tools.py
│   ├── agent.py
│   ├── schemas.py
│
│   ├── static/
│   │   ├── style.css
│   │   └── app.js
│
│   └── templates/
│       └── index.html
│
├── .env
├── requirements.txt
└── shop_database.db
```

---

# ⚙️ Installation

## 1️⃣ Clone the repository

```
git clone https://github.com/javamohammed/sqlite-ai-agent.git
cd sqlite-ai-agent
```

---

## 2️⃣ Create a virtual environment

```
python -m venv venv
```

Activate it:

### Windows

```
venv\Scripts\activate
```

### Mac / Linux

```
source venv/bin/activate
```

---

## 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

## 4️⃣ Create `.env`

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./shop_database.db
OPENAI_MODEL=gpt-4.1-mini
```

---

## 5️⃣ Add your SQLite database

Place your database file in the project root.

Example:

```
shop_database.db
```

---

# 🚀 Run the Application

Start the server:

```
uvicorn app.main:app --reload
```

Open the browser:

```
http://127.0.0.1:8000
```

---

# 🌐 API Endpoints

### Chat with AI

```
POST /api/chat
```

Example request:

```json
{
  "message": "Show me the first 10 users"
}
```

---

### List Tables

```
GET /api/tables
```

---

### Tables With Row Counts

```
GET /api/tables-with-counts
```

---

### Table Schema

```
GET /api/schema/{table_name}
```

---

### Table Preview

```
GET /api/table-preview/{table_name}
```

Returns the **first 20 rows**.

---

# 🔐 Safety Notes

This application allows **direct database modification**.

Operations supported:

* INSERT
* UPDATE
* DELETE

To reduce risk:

* UPDATE requires `WHERE`
* DELETE requires `WHERE`

⚠️ Do **not use this on sensitive production databases** without additional protections.

Recommended improvements:

* Authentication
* Authorization
* Audit logs
* Query preview
* Table permissions
* Backups

---

# ⚠️ Limitations

* Designed for **SQLite**
* No built-in authentication
* Large tables may slow down row counts
* Natural language ambiguity may occur

---

# 🧪 Example Prompts

```
Show me all tables
Show the schema of users
Show me the first 20 rows from orders
Insert a new product with name Laptop and price 900
Update the status to delivered where id is 5
Delete the order where id is 2
```

---

# 🔧 Environment Variables

| Variable       | Description              |
| -------------- | ------------------------ |
| OPENAI_API_KEY | Your OpenAI API key      |
| DATABASE_URL   | SQLite connection string |
| OPENAI_MODEL   | OpenAI model             |

---

# 🛠️ Future Improvements

Possible next features:

* Pagination
* Column sorting
* Row filtering
* SQL preview
* CSV export
* Authentication
* Multi-database support
* Dark mode
* Query history

---

# 🤝 Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a branch
3. Commit your changes
4. Open a pull request

---

# 📄 License

You can use the **MIT License** for this project.

Example:

```
MIT License
Copyright (c) 2026
```
## Author

**Mohammed Aoulad Bouchta**

- GitHub: https://github.com/your-username
- Email: java.mohammed@gmail.com
---

# 🙏 Acknowledgements

FastAPI
https://fastapi.tiangolo.com/

LangChain
https://www.langchain.com/

OpenAI
https://platform.openai.com/

SQLAlchemy
https://www.sqlalchemy.org/
