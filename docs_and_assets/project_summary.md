# 🚀 NOC AI Project Summary — Global Overview

> **Last Updated:** March 25, 2026
> **Status:** Phase 1 Complete (Deterministic Agent), Phase 2 Ongoing (Machine Learning)

## 1. Project Mission
NOC-AI is a professional **AIOps (AI for IT Operations)** assistant designed to replace manual alarm monitoring with natural language queries. It translates human questions (e.g., *"How many sites are down in Alex today?"*) into complex API calls and database queries to provide instant, structured operational insights.

---

## 2. Core Components

### 🖥️ Local AI Server (Python Core)
- **Primary Logic**: Replicates the production `n8n` workflow logic for local testing without internet/cloud dependencies.
- **Smart Data Loading**: Supports multiple formats (`3months.txt`, `mega_data.json`) with automated fallback and flexible JSON parsing (handles `result`, `data`, or `records` structures).
- **Deterministic Parsing**: Uses advanced Regex and fuzzy matching for Intent Recognition and Location Resolution (e.g., mapping "Delta" to "East Delta|West Delta").

### 🐧 Linux CLI (New!)
- **Location**: `python_local_server/linux_cli/`
- **Interactive Mode**: A robust command-line interface for terminal-based operations.
- **Automated Setup**: Includes `run_cli.sh` which handles dependency installation and environment setup on any Linux distro.

### 🎨 Frontend Dashboards (V4.2)
- **Location**: `frontend_ui/NOC AI Assistant v4.2.html`
- **Features**: Sidebar "Quick Queries" for 25+ standard operational questions, real-time debug view, and dynamic response formatting.
- **Mobile Responsive**: Designed for use in NOC environments on both desktops and tablets.

### ⚙️ n8n Workflows (V3.5)
- **Location**: `n8n_workflows/NOC AI SQL Agent V3.5 Webhook.json`
- **Intelligence**: Integrated with **Ollama (llama3.2:1b)** for local AI reasoning.
- **SQL Agent**: Uses PostgreSQL `ai_alarm_mappings` to resolve unreliable API headers (like `sitepoweroff`) into specific alarm names.

---

## 3. The Query Pipeline (How it works)
1. **Input**: User asks a question via Chat or Sidebar.
2. **Parsing**: AI Agent (Ollama) extracts 17+ parameters (Location, Tech, Vendor, Start/End Time).
3. **Resolution**: 
    - **Regions**: "Alex" → `Alex`, "Delta" → `East Delta|West Delta`.
    - **Alarms**: "Power" → Queries DB for specific alarm names like "Mains Fail".
4. **API Call**: Builds a high-limit (1000 records) HTTPS POST request with precise headers.
5. **Deduplication**: Tally-based counting ensures accurate reports for multi-technology sites.
6. **Reply**: Returns a human-readable summary + raw debug JSON.

---

## 4. Deployment & Installation
We have automated the deployment for easy distribution across the team:

- **Windows**: Run `python_local_server/scripts/run_gui.bat`.
    - Automatically checks Python/Pip.
    - Sets up a Virtual Environment (`venv`).
    - **Auto-installs Ollama** if missing and pulls the required AI models.
- **Linux**: Run `python_local_server/linux_cli/run_cli.sh`.
- **Stand-alone EXE**: `NOC_AI_Local_Server.exe` (v3.2) is available for zero-config startup.

---

## 5. Current Data Schema
The project relies on standardized context files in `python_local_server/context/`:
- `ai_alarm_mappings_full.sql`: The source of truth for mapping categories to specific alarm names.
- `3months.txt / mega_data.json`: Standardized test datasets (500k+ records available for stress testing).

---

## 6. Next Steps: AIOps Evolution
Moving from **Deterministic Responses** to **Predictive Analytics**:
1. **Predictive Outage**: Forecasting potential site downs 24h in advance using historical trends.
2. **Alarm Correlation**: Grouping multiple related alarms (e.g., 20 battery lows in one area) into a single "Main Fail Incident".
3. **NLP Customization**: Fine-tuning models on local telecom slang and site-specific identifiers.

---
*This summary serves as the primary entry point for understanding the NOC-AI architecture and current progress.*
