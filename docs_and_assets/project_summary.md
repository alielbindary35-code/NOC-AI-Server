# NOC AI Project Implementation Summary

## 1. Core Architecture
The system is built as a **Deterministic AI Agent**. It uses a Python-based server (`noc_server.py`) that replicates the exact logic of the production `n8n` workflow:
- **Intent Recognition**: Regex-based parsing of natural language into structured API parameters.
- **Location Resolution**: Mapping regional inputs (Alex, Delta, Upper Egypt) to specific site locations.
- **Intelligent Filtering**: Multi-stage filtering process (Vendor -> Technology -> Power/Down Flags).
- **Graceful Fallbacks**: If explicit SQL/JSON flags (`sitepoweroff`, `sitedownflag`) are missing, the server uses a keyword-based ranking system (Search for "Mains", "Rectifier", "OML", etc.) within the `alarmname` field.

## 2. Tools & Automation
### 🖥️ Local AI Server GUI
- Built with Python `Tkinter` (Zero Dependencies).
- Compiles into a single `NOC_AI_Local_Server.exe` for easy distribution.
- **Features**: User logging, Dynamic Data Source switching, JSON-to-CSV converter.
- **API Simulation**: Generates payloads with `start=0`, `limit=1000`, and `Unix Millisecond` timestamps.

### 📈 Data Expansion Engine
- `expand_data_mega.py`: Generates 500,000 unique records by randomizing existing patterns to prevent deduplication from wiping test data.
- Ensures distinct `alarmid` and site identifiers for realistic stress-testing.

## 3. Deployment & Version Control
- **GitHub**: `alielbindary35-code/NOC-AI-Server.git`
- **Exclusions**: Large datasets (>100MB) like `mega_data.json` are ignored via `.gitignore`.
- **Organization**: Seperated into `python_local_server`, `n8n_workflows`, `frontend_ui`, and `docs_and_assets`.

## 4. Testing Status
- Verified 25+ hardcoded questions from the HTML dashboards.
- Parameters sent to API are verified as correct (e.g., `sitedownflag: Yes`, `location: Alex`).
- Count-only questions provide detailed breakdowns; "Show" questions provide site lists.

## 5. Next Phase: Machine Learning (AIOps)
Transitioning to **Predictive Maintenance**:
1. Clean 3-5 years of raw CSV data on Google Colab.
2. Train a specialized NLP model (Telecom-BERT) on local slang.
3. Implement Predictive Analytics for 24h-outage forecasting.
4. Build Alarm Correlation to reduce operational noise.

---
*Summary generated on March 23, 2026.*
