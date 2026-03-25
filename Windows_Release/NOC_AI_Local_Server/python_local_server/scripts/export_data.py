import json
import csv
import os

def export_to_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, '..', 'context', 'expanded_data.txt')
    output_path = os.path.join(base_dir, '..', 'context', 'expanded_data.csv')
    
    print(f"Reading {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    records = raw.get('result', raw.get('data', []))
    if not records:
        print("No records to export.")
        return
        
    # Find all unique columns across all dicts to make the CSV header
    headers = set()
    for r in records:
        headers.update(r.keys())
    
    headers = list(headers)
    # Put important columns first
    important = ['location', 'sitename', 'sitecode', 'vendor', 'networktype', 'domain', 'sitedownflag', 'sitepoweroff', 'isvip', 'isrootne', 'standardalarmseverity', 'sitepriority']
    final_headers = [h for h in important if h in headers] + [h for h in headers if h not in important]
    
    print(f"Exporting {len(records)} records to CSV for Excel...")
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=final_headers)
        writer.writeheader()
        
        # Clean dicts for CSV
        for r in records:
            clean_rec = {}
            for k in final_headers:
                val = r.get(k, '')
                if isinstance(val, (dict, list)):
                    val = json.dumps(val, ensure_ascii=False)
                clean_rec[k] = val
            writer.writerow(clean_rec)
            
    print(f"Done! Saved CSV to {output_path}")

if __name__ == '__main__':
    export_to_csv()
