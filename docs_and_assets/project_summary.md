# 🚀 NOC AI Project Summary — Global Overview

> **Last Updated:** April 2026
> **Status:** 🚨 PRODUCTION LIVE — V3.9 Phase1 Hardened
> **⚠️ CRITICAL:** This is a live Production system. DO NOT test on the active n8n workflow without reviewing changes first.

## 1. Project Mission
NOC-AI is a professional **AIOps (AI for IT Operations)** assistant designed to replace manual alarm monitoring with natural language queries. It translates human questions (e.g., *"How many sites are down in Alex today?"*) into complex API calls and database queries to provide instant, structured operational insights.

---

## 2. Core Components

### 🖥️ Local AI Server (Python Core)
- **Primary Logic**: Replicates the production `n8n` workflow logic for local testing without internet/cloud dependencies.
- **Smart Data Loading**: Supports multiple formats (`3months.txt`, `mega_data.json`) with automated fallback and flexible JSON parsing (handles `result`, `data`, or `records` structures).
- **Deterministic Parsing**: Uses advanced Regex and fuzzy matching for Intent Recognition and Location Resolution (e.g., mapping "Delta" to "East Delta|West Delta").

### 🐧 Linux/Windows CLI & GUI Debuggers
- **Live API Studio**: `docs_and_assets/analyzer_tools/noc_debug_windows_gui.py` allows direct extraction of n8n payload to execute exact identical requests against the backend API natively via Postgres-like GUI studio, enabling precise troubleshooting of missing headers or `0` record responses.

### 🎨 Frontend Dashboards (V4.2)
- **Location**: `frontend_ui/NOC AI Assistant v4.2.html`
- **Features**: Sidebar "Quick Queries" for standard operational questions, real-time modal debug view, dynamic theme switcher (Dark/Light), auto-send functionality, and dynamic response formatting.
- **Mobile Responsive**: Designed for use in NOC environments on both desktops and tablets.

### ⚙️ n8n Workflows (V3.9 Phase1 Hardened — PRODUCTION)
- **Active Workflow**: `n8n_workflows/NOC_AI_SQL_Agent_V3.9_Phase1_Hardened.json` ← **USE THIS**
- **AI Model**: **Ollama `qwen2.5:14b`** with JSON Mode forced (`format: json`, `numPredict: 250`).
- **Memory**: Window Buffer Memory **DISABLED** (was causing 60s+ latency).
- **SQL Agent**: Uses PostgreSQL `ai_alarm_mappings` to resolve unreliable API headers into specific alarm names.

#### 🔴 Critical API Protocol (DO NOT CHANGE)
- The backend Java API **ONLY** accepts parameters via **HTTP Headers** (NOT Query Params).
- Sending parameters as Query Params returns `0` records or breaks JSON response entirely.
- The `Call Alarm API` n8n node must ALWAYS use `sendHeaders: true` with all parameters listed under `headerParameters`.

---

## 3. The Query Pipeline (How it works)
1. **Input**: User asks a question via Chat or Sidebar.
2. **Parsing**: AI Agent (Ollama) extracts 17+ parameters (Location, Tech, Vendor, Start/End Time).
3. **Guardrails (V3.9)**: Centralized logic strictly enforces category overrides and fallback intents before downstream execution.
4. **Resolution**: 
    - **Regions**: "Alex" → `Alex`, "Delta" → `East Delta|West Delta`.
    - **Alarms**: "Power" → Queries DB for specific alarm names like "Mains Fail".
5. **API Call**: Builds paginated HTTPS POST requests (up to 25 parallel pages).
6. **Deduplication**: Tally-based counting ensures accurate reports for multi-technology sites. Detects any pagination errors.
7. **Reply**: Returns a human-readable summary + raw debug JSON.

---

## 4. Current Data Schema
The project relies on standardized context files in `python_local_server/context/`:
- `ai_alarm_mappings_full.sql`: The source of truth for mapping categories to specific alarm names.
- `3months.txt / mega_data.json`: Standardized test datasets (500k+ records available for stress testing).

---

## 5. 🚨 Optimization Roadmap & Log

### Phase 1: Stability & Reliability (✅ COMPLETED in V3.9)
| # | Issue | Root Cause | Fix Applied (V3.9 Phase1 Hardened) |
|---|-------|-----------|-------------|
| 1 | Logic discrepancies | Guardrails duplicated across 3 nodes | **Centralized Guardrails** in `INT_Operational Guardrails` only |
| 2 | Timezone instability | `toLocaleString` is environment-dependent | **Safer Timezone Handling** using `Intl.DateTimeFormat.formatToParts` |
| 3 | Silent API failures | Pagination fails went undetected | **Pagination Error Tracking** in `ENGINE_Normalize` added |

### Phase 2: Performance & UX (🚧 UP NEXT)
1. **Fast Path Before LLM**: Implement a pre-LLM keyword matcher to reduce 5-8s latency to <1s for common queries.
2. **Better Empty-Result Messages**: Explain *why* a query returned 0 records by showing the applied filters.
3. **Dashboard Auto-Population**: Populate dashboard graphs on all queries, not just when the word "dashboard" is used.

### Phase 3: Product Polish (🔮 FUTURE)
1. **Intent Caching**: Hash and cache exact queries for 5 minutes (instant response).
2. **Node Naming Cleanup**: Enforce standard prefixing notation correctly.
3. **Streaming Responses**: Progressive updates for long queries (requires SSE on frontend).

---
*This summary serves as the primary entry point for understanding the NOC-AI architecture and current production status.*
