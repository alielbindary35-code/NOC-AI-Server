#!/usr/bin/env python3
"""
local_ai_cli.py
===============
Terminal (CLI) version of local_ai_gui.py
Works on Linux without tkinter / any GUI dependency.

Usage:
    python local_ai_cli.py
    python local_ai_cli.py --data /path/to/custom_data.json
    python local_ai_cli.py --convert /path/to/file.json  (convert JSON → CSV)
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime

# Add current dir to path to import noc_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import noc_server

# ──────────────────────────────────────────────
# Colour helpers (ANSI, safe fallback)
# ──────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"

def c(text, colour):
    return f"{colour}{text}{RESET}"

def banner(title, char="═", width=60):
    bar = char * width
    print(f"\n{c(bar, CYAN)}")
    print(c(f"  {title}", BOLD))
    print(c(bar, CYAN))

def divider(width=60):
    print(c("─" * width, GRAY))


# ──────────────────────────────────────────────
# Locate default data source
# ──────────────────────────────────────────────
def context_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base, '..', 'context'))

def list_context_files():
    """Return sorted list of .txt/.json files in the context folder."""
    d = context_dir()
    if not os.path.isdir(d):
        return []
    return sorted(
        os.path.join(d, f) for f in os.listdir(d)
        if f.endswith(('.txt', '.json'))
    )

def default_data_path():
    preferred = ('mega_data.json', '3months.txt', '5month.txt')
    d = context_dir()
    for name in preferred:
        candidate = os.path.join(d, name)
        if os.path.exists(candidate):
            return candidate
    files = list_context_files()
    return files[0] if files else os.path.join(d, 'mega_data.json')

def pick_data_source(current=None):
    """
    Show a numbered menu of available context files.
    Returns the chosen absolute path, or None if cancelled.
    """
    files = list_context_files()
    if not files:
        print(c("  [WARN] No data files found in context/ folder.", YELLOW))
        return None

    print(c("\n  📂 Available data files:", CYAN))
    for i, fp in enumerate(files, 1):
        marker = c(" ◀ current", GREEN) if fp == current else ""
        size_kb = os.path.getsize(fp) // 1024
        print(c(f"    [{i}]", BOLD) + f" {os.path.basename(fp)}"  +
              c(f"  ({size_kb:,} KB)", GRAY) + marker)
    print(c("    [0]  Enter custom path", GRAY))

    while True:
        try:
            choice = input(c("\n  Choose [1-{n}] or 0 for custom path: ".format(n=len(files)), CYAN)).strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if choice == "":
            # Enter → keep current / use default
            return current or default_data_path()

        if choice == "0":
            try:
                custom = input(c("  Enter full path: ", CYAN)).strip()
            except (KeyboardInterrupt, EOFError):
                return None
            if os.path.exists(custom):
                return custom
            print(c(f"  [ERROR] File not found: {custom}", RED))
            continue

        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]

        print(c(f"  Invalid choice. Enter a number between 0 and {len(files)}.", RED))


# ──────────────────────────────────────────────
# Log file helpers
# ──────────────────────────────────────────────
def create_log_file(username, data_source):
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(log_dir, f"{username}_{timestamp}_test_log.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"--- Local AI Test Log for {username} ---\n")
        f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Source: {data_source}\n")
        f.write("=" * 60 + "\n\n")
    return path

def log_entry(log_path, question, api_params, reply, total):
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] QUESTION: {question}\n")
        f.write("--- API PARAMS SENT ---\n")
        f.write(json.dumps(api_params, ensure_ascii=False) + "\n")
        f.write(f"--- REPLY (Matches: {total}) ---\n")
        f.write(reply + "\n")
        f.write("=" * 60 + "\n\n")

def log_source_change(log_path, new_path):
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Switched Data Source to: {new_path}\n")
        f.write("=" * 60 + "\n\n")


# ──────────────────────────────────────────────
# Core: process a single question
# ──────────────────────────────────────────────
def process_question(question):
    params = noc_server.parse_question(question)

    if params['intent'] == 'unknown':
        reply = "🤖 I could not understand the alarm query. Free Chat logic is active."
        total = 0
        api_params = {"Warning": "Intent could not be parsed as an alarm filter."}
    else:
        locations, label = noc_server.resolve_location(params['region_input'])
        filtered, filter_steps = noc_server.filter_records(noc_server.DATA, params, locations)
        unique = noc_server.deduplicate(filtered)
        reply, total = noc_server.format_reply(unique, params, label, filter_steps)

        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
        end_date   = datetime(now.year, now.month, now.day, 23, 59, 59)

        api_params = {
            "start":                 0,
            "limit":                 1000,
            "starttime":             int(start_date.timestamp() * 1000),
            "endtime":               int(end_date.timestamp() * 1000),
            "type":                  1,
            "sitedownflag":          params["sitedownflag"],
            "sitepoweroff":          params["sitepoweroff"],
            "vendor":                params["vendor"],
            "networktype":           params["networktype"],
            "domain":                params["domain"],
            "severity":              params["severity"],
            "standardalarmseverity": params["severity"],
            "sitepriority":          params["sitepriority"],
            "isvip":                 params["isvip"],
            "isrootne":              params["isrootne"],
            "location":              label,
        }
        api_params = {k: v for k, v in api_params.items() if v != ""}

    return api_params, reply, total


# ──────────────────────────────────────────────
# Convert JSON → CSV (CLI version)
# ──────────────────────────────────────────────
def convert_json_to_csv(src_path, dest_path=None):
    if not os.path.exists(src_path):
        print(c(f"[ERROR] File not found: {src_path}", RED))
        return

    try:
        with open(src_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        print(c(f"[ERROR] Cannot read JSON: {e}", RED))
        return

    records = raw.get('result', raw.get('data', raw))
    if not isinstance(records, list) or not records:
        print(c("[ERROR] No valid record list found in JSON.", RED))
        return

    headers = set()
    for r in records:
        if isinstance(r, dict):
            headers.update(r.keys())
    headers = list(headers)

    if dest_path is None:
        base = os.path.splitext(src_path)[0]
        dest_path = base + "_converted.csv"

    with open(dest_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in records:
            if not isinstance(r, dict):
                continue
            clean = {}
            for k in headers:
                val = r.get(k, '')
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, ensure_ascii=False)
                clean[k] = val
            writer.writerow(clean)

    print(c(f"[OK] Converted {len(records):,} records → {dest_path}", GREEN))


# ──────────────────────────────────────────────
# Interactive session
# ──────────────────────────────────────────────
def run_interactive(data_source):
    banner("NOC AI – Local Test CLI", width=60)
    print(c("Type your question and press Enter.", GRAY))
    print(c("Commands: :source  :convert  :help  :exit\n", GRAY))

    # --- ask for username ---
    while True:
        username = input(c("👤 Enter your name to start: ", CYAN)).strip()
        if username:
            break
        print(c("  Name cannot be empty.", RED))

    # --- pick data source interactively (unless passed via --data flag) ---
    chosen = pick_data_source(current=data_source)
    if chosen:
        data_source = chosen
    print(c(f"\n  ✅ Using: {os.path.basename(data_source)}", GREEN))

    # --- load data ---
    try:
        noc_server.load_data(data_source)
        record_count = len(noc_server.DATA)
        print(c(f"\n[OK] Loaded: {os.path.basename(data_source)}  ({record_count:,} records)", GREEN))
    except Exception as e:
        print(c(f"[ERROR] Could not load data: {e}", RED))
        # Show available files to help the user
        context_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'context'))
        if os.path.isdir(context_dir):
            files = [f for f in os.listdir(context_dir) if f.endswith(('.txt', '.json'))]
            if files:
                print(c(f"\n  Available data files in context/:", CYAN))
                for f in sorted(files):
                    print(c(f"    {f}", GRAY))
                print(c(f"\n  Run with:  bash run_cli.sh --data <path>", YELLOW))
        sys.exit(1)

    log_path = create_log_file(username, data_source)
    print(c(f"[LOG] Session log → {log_path}\n", GRAY))
    divider()

    # --- main loop ---
    while True:
        try:
            question = input(c("\n💬 Question: ", YELLOW)).strip()
        except (KeyboardInterrupt, EOFError):
            print(c("\n\n[INFO] Session ended. Bye!", CYAN))
            break

        if not question:
            continue

        # ── built-in commands ──
        if question.lower() in (":exit", ":quit", "exit", "quit"):
            print(c("\n[INFO] Session ended. Bye!", CYAN))
            break

        if question.lower() == ":help":
            print(c("""
  :source          – switch data source file
  :convert         – convert a JSON file to CSV
  :exit / :quit    – exit the CLI
  Any other text   – ask the AI a question
""", GRAY))
            continue

        if question.lower() == ":source":
            new_path = pick_data_source(current=data_source)
            if not new_path:
                continue
            try:
                noc_server.load_data(new_path)
                data_source = new_path
                print(c(f"\n  [OK] Switched to: {os.path.basename(new_path)}  ({len(noc_server.DATA):,} records)", GREEN))
                log_source_change(log_path, new_path)
            except Exception as e:
                print(c(f"  [ERROR] {e}", RED))
            continue

        if question.lower() == ":convert":
            src = input(c("  Enter full path to JSON/TXT file: ", CYAN)).strip()
            convert_json_to_csv(src)
            continue

        # ── process question ──
        print(c("  Analyzing...", GRAY))
        try:
            api_params, reply, total = process_question(question)
        except Exception as e:
            print(c(f"  [ERROR] {e}", RED))
            continue

        # ── display ──
        banner("🌐 API PAYLOAD (SENT TO NOC ENDPOINT)", width=60)
        print(json.dumps(api_params, indent=4, ensure_ascii=False))

        banner("🤖 AI AGENT REPLY", width=60)
        print(reply)
        divider()

        # ── log ──
        log_entry(log_path, question, api_params, reply, total)
        print(c(f"\n  [LOG] Saved to {os.path.basename(log_path)}", GRAY))


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="NOC AI Local Test CLI – terminal replacement for local_ai_gui.py"
    )
    parser.add_argument(
        "--data", "-d",
        default=None,
        help="Path to data file (JSON/TXT). Defaults to context/mega_data.json"
    )
    parser.add_argument(
        "--convert", "-c",
        default=None,
        metavar="JSON_FILE",
        help="Convert a JSON file to CSV and exit (no interactive session)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        metavar="CSV_FILE",
        help="Output CSV path when using --convert (optional)"
    )
    args = parser.parse_args()

    # --- convert-only mode ---
    if args.convert:
        convert_json_to_csv(args.convert, args.output)
        return

    data_source = args.data if args.data else default_data_path()
    run_interactive(data_source)


if __name__ == "__main__":
    main()
