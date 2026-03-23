# NOC AI Operations Center - Local Test Server & Workflow

## 🚀 Project Overview
This project provides a complete simulation environment for the NOC AI Assistant. it mirrors the production n8n workflow logic using a high-performance Python local server, a dedicated testing GUI, and automated data expansion tools.

## 📂 Project Structure
- 📂 **`python_local_server/`**: The core simulation logic.
  - 📂 **`scripts/`**: Contains `noc_server.py` (API logic), `local_ai_gui.py` (Testing Tool), and data expansion scripts.
  - 📂 **`context/`**: Source datasets (`3months.txt`, `5month.txt`) and test results.
- 📂 **`n8n_workflows/`**: JSON exports of the AI Agent and SQL formatting workflows.
- 📂 **`frontend_ui/`**: HTML/JS dashboards for the AI Assistant interface.
- 📂 **`docs_and_assets/`**: Project roadmap, internal documentation, and visual assets.
- 📂 **`logs/`**: Automated test logs stored by username and session timestamp.

## 🛠️ Main Tools
### 1. NOC AI Local Server (.exe)
A standalone Windows executable located in the root. Use it to:
- Test natural language queries against real NOC data patterns.
- View exact API Payload parameters (start, limit, unix timestamps).
- Convert raw JSON/TXT exports into Excel-friendly CSVs.

### 2. Auto-Expander
Scripts designed to generate up to 500,000 unique records based on real patterns to stress-test the AI's logic and performance.

## 🔮 Future Roadmap (Phase 2)
The project is moving towards **AIOps** which will include:
- **Predictive Analytics**: Forecasting site outages 24h in advance.
- **Alarm Correlation**: Grouping symptomatic alarms into single Root Cause incidents.
- **Custom NLP Fine-Tuning**: Training an LLM on local telecom slang and raw historical data logs.

---
*Developed for e& Egypt - NOC Operations Intelligence.*
