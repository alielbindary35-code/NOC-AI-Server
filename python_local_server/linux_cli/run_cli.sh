#!/usr/bin/env bash
# =============================================================
#  run_cli.sh  –  NOC AI Local Test CLI  (Linux launcher)
#  Handles: venv creation → activation → deps → launch
# =============================================================

set -e   # exit on any unexpected error

# ── Colours ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;96m'
YELLOW='\033[0;93m'; GRAY='\033[0;90m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Paths ─────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(cd "${SCRIPT_DIR}/../scripts" && pwd)"
VENV_DIR="${SCRIPTS_DIR}/venv"
CLI_SCRIPT="${SCRIPT_DIR}/local_ai_cli.py"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"

# ── Header ───────────────────────────────────────────────────
echo -e "\n${BOLD}${CYAN}=================================================${NC}"
echo -e "${BOLD}${CYAN}   NOC AI  –  Local Test CLI  (Linux)${NC}"
echo -e "${BOLD}${CYAN}=================================================${NC}\n"

# ── 1. Check Python ───────────────────────────────────────────
info "Checking Python 3..."
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    success "Found  ${PY_VER}"
    PYTHON="python3"
else
    error "python3 not found. Install it with: sudo apt install python3"
fi

# ── 2. Create venv (if missing) ───────────────────────────────
if [ ! -d "${VENV_DIR}" ]; then
    info "Creating virtual environment at: ${VENV_DIR}"
    ${PYTHON} -m venv "${VENV_DIR}" || error "Failed to create venv. Try: sudo apt install python3-venv"
    success "Virtual environment created."
else
    success "Virtual environment already exists."
fi

# ── 3. Activate venv ──────────────────────────────────────────
info "Activating virtual environment..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
success "Activated."

# ── 4. Install / update dependencies ─────────────────────────
if [ -f "${REQUIREMENTS}" ]; then
    # Only install non-comment, non-empty lines
    DEPS=$(grep -v '^\s*#' "${REQUIREMENTS}" | grep -v '^\s*$' || true)
    if [ -n "${DEPS}" ]; then
        info "Installing dependencies from requirements.txt..."
        pip install --quiet --upgrade pip
        pip install --quiet -r "${REQUIREMENTS}"
        success "Dependencies up to date."
    else
        info "No third-party dependencies (all standard library). Skipping pip install."
    fi
fi

# ── 5. Verify CLI script exists ───────────────────────────────
if [ ! -f "${CLI_SCRIPT}" ]; then
    error "CLI script not found: ${CLI_SCRIPT}"
fi

# ── 6. Add scripts dir to PYTHONPATH ──────────────────────────
export PYTHONPATH="${SCRIPTS_DIR}:${PYTHONPATH}"

# ── 7. Check and Setup Ollama (AI Agent) ──────────────────────
OLLAMA_MODEL="llama3.2:1b"
info "Checking AI Agent Engine (Ollama)..."

if ! command -v ollama &>/dev/null; then
    echo -e "\n${YELLOW}🤖 Notice: Ollama is NOT installed.${NC}"
    echo -e "Ollama is required to give your Local Server the EXACT same AI intelligence as the Production n8n server."
    echo -e "Without it, the server will fallback to basic word-matching (Regex)."
    read -p "$(echo -e ${CYAN}"Do you want to install Ollama automatically now? [y/N]: "${NC})" INSTALL_CHOICE
    
    if [[ "$INSTALL_CHOICE" =~ ^[Yy]$ ]]; then
        info "Installing Ollama... (this may ask for sudo password)"
        curl -fsSL https://ollama.com/install.sh | sh
        success "Ollama installed successfully."
    else
        warn "Skipping Ollama installation. Local Server will use Regex Fallback."
    fi
fi

# If installed (or just installed), make sure it's running and has the model
if command -v ollama &>/dev/null; then
    # Start ollama quietly in background if not already running
    if ! pgrep -x "ollama" >/dev/null; then
        ollama serve >/dev/null 2>&1 &
        sleep 2
    fi
    
    # Check if we have the model
    if ! ollama list | grep -q "${OLLAMA_MODEL}"; then
        info "Pulling the lightweight AI model '${OLLAMA_MODEL}' for fast local reasoning..."
        ollama pull "${OLLAMA_MODEL}"
        success "Model ready!"
    else
        success "AI Model '${OLLAMA_MODEL}' is ready."
    fi
fi

# ── 8. Launch the CLI ─────────────────────────────────────────
echo -e "\n${GRAY}─────────────────────────────────────────────────${NC}"
info "Launching NOC AI CLI…  (press Ctrl+C to stop)"
echo -e "${GRAY}─────────────────────────────────────────────────${NC}\n"

python "${CLI_SCRIPT}" "$@"
