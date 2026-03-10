const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const chatBox = document.getElementById("chatBox");
const clearChatBtn = document.getElementById("clearChatBtn");
const refreshTablesBtn = document.getElementById("refreshTablesBtn");
const tableSearchInput = document.getElementById("tableSearchInput");
const tablesList = document.getElementById("tablesList");
const schemaContainer = document.getElementById("schemaContainer");
const previewContainer = document.getElementById("previewContainer");
const selectedTableInfo = document.getElementById("selectedTableInfo");

const STORAGE_KEY = "sqlite_ai_agent_chat_history";

let activeTableName = null;
let allTables = [];
let tableSearchTerm = "";

function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatCellValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") {
    return escapeHtml(JSON.stringify(value, null, 2));
  }
  return escapeHtml(String(value));
}

function createTable(columns, rows) {
  if (!columns || !columns.length) {
    return `<div class="muted-text">No columns available.</div>`;
  }

  const thead = `
    <thead>
      <tr>
        ${columns.map(col => `<th>${escapeHtml(col)}</th>`).join("")}
      </tr>
    </thead>
  `;

  const tbody = `
    <tbody>
      ${rows.length ? rows.map(row => `
        <tr>
          ${columns.map(col => `<td>${formatCellValue(row[col])}</td>`).join("")}
        </tr>
      `).join("") : `
        <tr>
          <td colspan="${columns.length}" class="muted-text">No rows found.</td>
        </tr>
      `}
    </tbody>
  `;

  return `
    <div class="table-wrapper">
      <table class="result-table">
        ${thead}
        ${tbody}
      </table>
    </div>
  `;
}

function buildMetaLine(meta, resultType, rows) {
  if (resultType === "table") {
    const count = meta?.count ?? rows?.length ?? 0;
    const table = meta?.table ? `Table: ${meta.table} · ` : "";
    return `<div class="meta-line">${table}Rows: ${count}</div>`;
  }

  if (meta?.rowcount !== undefined) {
    const action = meta?.action ? `${meta.action} · ` : "";
    const table = meta?.table ? `${meta.table} · ` : "";
    return `<div class="meta-line">${action}${table}Affected rows: ${meta.rowcount}</div>`;
  }

  return "";
}

function renderMessage(msg, index) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${msg.role}`;

  const roleLabel = msg.role === "user" ? "User" : "Agent";

  let html = `
    <div class="message-header">${roleLabel}</div>
    <div class="message-text">${escapeHtml(msg.text || "")}</div>
  `;

  if (msg.role === "agent" && msg.result_type === "table") {
    html += createTable(msg.columns || [], msg.rows || []);
  }

  if (msg.role === "agent") {
    html += buildMetaLine(msg.meta || {}, msg.result_type, msg.rows || []);
  }

  wrapper.innerHTML = html;
  wrapper.dataset.index = index;
  return wrapper;
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveHistory(history) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

function renderHistory() {
  const history = getHistory();
  chatBox.innerHTML = "";

  if (!history.length) {
    chatBox.innerHTML = `<div class="empty-chat">No messages yet.</div>`;
    return;
  }

  history.forEach((msg, index) => {
    chatBox.appendChild(renderMessage(msg, index));
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}

function appendToHistory(message) {
  const history = getHistory();
  history.push(message);
  saveHistory(history);
  renderHistory();
}

function replaceLastAgentMessage(message) {
  const history = getHistory();
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].role === "agent") {
      history[i] = message;
      break;
    }
  }
  saveHistory(history);
  renderHistory();
}

function addTemporaryThinking() {
  appendToHistory({
    role: "agent",
    text: "Thinking...",
    result_type: "message",
    columns: [],
    rows: [],
    meta: {}
  });
}

function formatBadgeCount(value) {
  if (value === null || value === undefined) return "?";
  return String(value);
}

function getFilteredTables() {
  const term = tableSearchTerm.trim().toLowerCase();
  if (!term) return allTables;

  return allTables.filter(table =>
    (table.name || "").toLowerCase().includes(term)
  );
}

function renderTables() {
  const filteredTables = getFilteredTables();

  if (!filteredTables.length) {
    tablesList.innerHTML = `<div class="sidebar-empty">No matching tables.</div>`;
    return;
  }

  tablesList.innerHTML = "";

  filteredTables.forEach((table) => {
    const item = document.createElement("div");
    item.className = `table-item ${activeTableName === table.name ? "active" : ""}`;

    item.innerHTML = `
      <div class="table-name">${escapeHtml(table.name)}</div>
      <div class="table-badge">${escapeHtml(formatBadgeCount(table.row_count))}</div>
    `;

    item.addEventListener("click", () => selectTable(table.name));
    tablesList.appendChild(item);
  });
}

async function loadTables() {
  tablesList.innerHTML = `<div class="sidebar-empty">Loading tables...</div>`;

  try {
    const res = await fetch("/api/tables-with-counts");
    const data = await res.json();

    allTables = data.tables || [];
    renderTables();
  } catch (error) {
    tablesList.innerHTML = `<div class="sidebar-empty">Failed to load tables.</div>`;
  }
}

async function loadSchema(tableName) {
  schemaContainer.innerHTML = `<div class="muted-text">Loading schema...</div>`;

  try {
    const res = await fetch(`/api/schema/${encodeURIComponent(tableName)}`);
    const data = await res.json();

    if (!data.success) {
      schemaContainer.innerHTML = `<div class="muted-text">${escapeHtml(data.error || "Failed to load schema.")}</div>`;
      return;
    }

    const rows = data.schema || [];
    const columns = ["name", "type", "nullable", "default"];

    schemaContainer.innerHTML = createTable(columns, rows);
  } catch (error) {
    schemaContainer.innerHTML = `<div class="muted-text">Failed to load schema.</div>`;
  }
}

async function loadPreview(tableName) {
  previewContainer.innerHTML = `<div class="muted-text">Loading rows...</div>`;

  try {
    const res = await fetch(`/api/table-preview/${encodeURIComponent(tableName)}`);
    const data = await res.json();

    if (!data.success) {
      previewContainer.innerHTML = `<div class="muted-text">${escapeHtml(data.error || "Failed to load preview.")}</div>`;
      return;
    }

    const columns = data.columns || [];
    const rows = data.rows || [];
    const count = data.count || 0;

    previewContainer.innerHTML = `
      <div class="preview-summary">Showing up to 20 rows. Loaded: ${count}</div>
      ${createTable(columns, rows)}
    `;
  } catch (error) {
    previewContainer.innerHTML = `<div class="muted-text">Failed to load preview.</div>`;
  }
}

async function selectTable(tableName) {
  activeTableName = tableName;
  selectedTableInfo.textContent = tableName;

  renderTables();
  await loadSchema(tableName);
  await loadPreview(tableName);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const message = input.value.trim();
  if (!message) return;

  appendToHistory({
    role: "user",
    text: message
  });

  input.value = "";
  addTemporaryThinking();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await res.json();

    replaceLastAgentMessage({
      role: "agent",
      text: data.response || "Done.",
      result_type: data.result_type || "message",
      columns: data.columns || [],
      rows: data.rows || [],
      meta: data.meta || {}
    });

    await loadTables();

    const actionTable = data?.meta?.table;
    if (actionTable) {
      await selectTable(actionTable);
    } else if (activeTableName) {
      await loadPreview(activeTableName);
    }
  } catch (error) {
    replaceLastAgentMessage({
      role: "agent",
      text: "An error occurred while contacting the server.",
      result_type: "message",
      columns: [],
      rows: [],
      meta: {}
    });
  }
});

clearChatBtn.addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  renderHistory();
});

refreshTablesBtn.addEventListener("click", async () => {
  await loadTables();
});

tableSearchInput.addEventListener("input", (e) => {
  tableSearchTerm = e.target.value || "";
  renderTables();
});

renderHistory();
loadTables();