import os
import sys
import json
import csv
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Add current dir to path to import noc_server
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import noc_server

class LocalAIServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Local AI Server - Testing Interface")
        self.root.geometry("850x650")
        
        self.username = ""
        self.log_file_path = ""
        
        # Support PyInstaller Frozen EXE
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            p1 = os.path.join(base_path, 'python_local_server', 'context', 'mega_data.json')
            p2 = os.path.join(base_path, '..', 'context', 'mega_data.json')
            if os.path.exists(p1):
                self.current_data_source = p1
            elif os.path.exists(p2):
                self.current_data_source = p2
            else:
                self.current_data_source = os.path.join(base_path, 'mega_data.json')
        else:
            self.current_data_source = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'context', 'mega_data.json'))
        
        # Load data initially
        try:
            noc_server.load_data(self.current_data_source)
            self.data_status = f"Loaded: {os.path.basename(self.current_data_source)} ({len(noc_server.DATA):,} records)"
        except Exception as e:
            self.data_status = f"Error loading default data: {e}"

        # Setup modern styles
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except:
            pass
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground='#2C3E50')
        
        self.create_welcome_screen()

    def create_welcome_screen(self):
        self.welcome_frame = ttk.Frame(self.root, padding=30)
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.welcome_frame, text="👋 Welcome to Local AI Server", style='Title.TLabel').pack(pady=(50, 20))
        ttk.Label(self.welcome_frame, text="Please enter your name to start testing and create your log file:").pack(pady=10)
        
        self.name_entry = ttk.Entry(self.welcome_frame, font=('Helvetica', 14), width=30)
        self.name_entry.pack(pady=10)
        self.name_entry.bind('<Return>', lambda e: self.start_test())
        self.name_entry.focus()
        
        ttk.Button(self.welcome_frame, text="▶ Start Test Session", command=self.start_test).pack(pady=30)

    def start_test(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter your name.")
            return
            
        self.username = name
        
        # Create user log folder and file
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            if os.path.exists(os.path.join(base_path, 'python_local_server')):
                log_dir = os.path.join(base_path, 'logs')
            else:
                log_dir = os.path.join(base_path, '..', '..', 'logs')
        else:
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
            
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(log_dir, f"{self.username}_{timestamp}_test_log.txt")
        
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"--- Local AI Test Log for {self.username} ---\n")
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Source: {self.current_data_source}\n")
            f.write("="*60 + "\n\n")
            
        self.welcome_frame.destroy()
        self.create_main_screen()

    def create_main_screen(self):
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header / Status / Tools
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text=f"👤 Tester: {self.username}", font=('Helvetica', 11, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="   |   ", foreground="gray").pack(side=tk.LEFT)
        self.lbl_source = ttk.Label(header_frame, text=f"📊 Source: {self.data_status}", foreground="#27AE60")
        self.lbl_source.pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="🔄 Change Source", command=self.change_data_source).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(header_frame, text="📁 Convert JSON to CSV", command=self.convert_json_to_csv).pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Question Input Area
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="💬 Ask a question about the alarms:", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0,5))
        
        query_frame = ttk.Frame(input_frame)
        query_frame.pack(fill=tk.X)
        
        self.question_entry = ttk.Entry(query_frame, font=('Helvetica', 14))
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.question_entry.bind('<Return>', lambda e: self.process_question())
        
        ttk.Button(query_frame, text="Send", command=self.process_question).pack(side=tk.RIGHT)
        
        # Result Details Label
        ttk.Label(self.main_frame, text="📝 AI Reply & API Payload Details:", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(15, 5))
        
        # Response Area
        text_frame = ttk.Frame(self.main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(text_frame, font=('Consolas', 11), wrap=tk.WORD, bg="#1E1E1E", fg="#D4D4D4", padx=10, pady=10)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.insert(tk.END, f"Welcome {self.username}! Your session is active.\nAll questions and payloads will be logged securely in:\n{self.log_file_path}\n\nWaiting for query...\n")

    def change_data_source(self):
        file_path = filedialog.askopenfilename(
            title="Select Data Source",
            filetypes=[("JSON/Text Files", "*.txt *.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            noc_server.load_data(file_path)
            self.current_data_source = file_path
            self.data_status = f"Loaded: {os.path.basename(file_path)} ({len(noc_server.DATA):,} records)"
            
            self.lbl_source.config(text=f"📊 Source: {self.data_status}")
            
            # Log the change
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] Switched Data Source to: {file_path}\n")
                f.write("=" * 60 + "\n\n")
                
            self.result_text.insert(tk.END, f"\n[INFO] Successfully switched data source to: {os.path.basename(file_path)} ({len(noc_server.DATA):,} records)\n\n")
            self.result_text.see(tk.END)
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data from {os.path.basename(file_path)}.\nError: {e}")

    def convert_json_to_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select Source JSON/TXT File",
            filetypes=[("JSON/Text Files", "*.txt *.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            records = raw.get('result', raw.get('data', raw))
            
            if not isinstance(records, list) or not records:
                messagebox.showinfo("Empty/Invalid", "No records found or file is not a valid JSON array.")
                return
                
            headers = set()
            for r in records:
                if isinstance(r, dict):
                    headers.update(r.keys())
            headers = list(headers)
            
            save_path = filedialog.asksaveasfilename(
                title="Save Target CSV As",
                defaultextension=".csv",
                initialfile="converted_data.csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not save_path:
                return
                
            with open(save_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for r in records:
                    if not isinstance(r, dict): continue
                    clean_rec = {}
                    for k in headers:
                        val = r.get(k, '')
                        if isinstance(val, (dict, list)):
                            val = json.dumps(val, ensure_ascii=False)
                        clean_rec[k] = val
                    writer.writerow(clean_rec)
                    
            messagebox.showinfo("Success", f"Target CSV exported successfully!\n\nRows: {len(records)}\nSaved to: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file:\n{str(e)}")

    def process_question(self):
        q = self.question_entry.get().strip()
        if not q:
            return
            
        self.question_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Analyzing: '{q}'...\n\n")
        self.root.update()
        
        params = noc_server.parse_question(q)
        
        if params['intent'] == 'unknown':
            reply = "🤖 I could not understand the alarm query. Free Chat logic is active."
            total = 0
            api_params = {"Warning": "Intent could not be parsed as an alarm filter."}
        else:
            locations, label = noc_server.resolve_location(params['region_input'])
            filtered, filter_steps = noc_server.filter_records(noc_server.DATA, params, locations)
            unique = noc_server.deduplicate(filtered)
            reply, total = noc_server.format_reply(unique, params, label, filter_steps)
            
            # Formulate the strict API payload with unix time
            now = datetime.now()
            start_date = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59)
            
            api_params = {
                "start": 0,
                "limit": 1000,
                "starttime": int(start_date.timestamp() * 1000),
                "endtime": int(end_date.timestamp() * 1000),
                "type": 1,
                "sitedownflag": params["sitedownflag"],
                "sitepoweroff": params["sitepoweroff"],
                "vendor": params["vendor"],
                "networktype": params["networktype"],
                "domain": params["domain"],
                "severity": params["severity"],
                "standardalarmseverity": params["severity"],  # API typically expects this
                "sitepriority": params["sitepriority"],
                "isvip": params["isvip"],
                "isrootne": params["isrootne"],
                "location": label
            }
            # Remove empty to accurately show what API receives natively
            api_params = {k: v for k, v in api_params.items() if v != ""}
            
        output = ""
        output += "╔════════════════════════════════════════════════════════╗\n"
        output += "║ 🌐 API PAYLOAD (SENT TO NOC ENDPOINT)                  ║\n"
        output += "╚════════════════════════════════════════════════════════╝\n"
        output += json.dumps(api_params, indent=4, ensure_ascii=False) + "\n\n"
        
        output += "╔════════════════════════════════════════════════════════╗\n"
        output += "║ 🤖 AI AGENT REPLY                                      ║\n"
        output += "╚════════════════════════════════════════════════════════╝\n"
        output += reply + "\n"
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, output)
        
        # Log to file appended beautifully
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] QUESTION: {q}\n")
            f.write(f"--- API PARAMS SENT ---\n")
            f.write(json.dumps(api_params, ensure_ascii=False) + "\n")
            f.write(f"--- REPLY (Matches: {total}) ---\n")
            f.write(reply + "\n")
            f.write("=" * 60 + "\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LocalAIServerGUI(root)
    root.mainloop()
