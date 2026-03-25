import json
import random
import os

def expand_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, '..', 'context', '5month.txt')
    output_path = os.path.join(base_dir, '..', 'context', 'mega_data.json')
    
    print(f"Reading from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    records = raw.get('result', raw.get('data', []))

    # Keep only essential fields to avoid memory limits when expanding to 500,000
    essential_keys = ['location', 'sitename', 'sitecode', 'vendor', 'networktype', 'domain', 'sitedownflag', 'sitepoweroff', 'isvip', 'isrootne', 'standardalarmseverity', 'sitepriority', 'alarmname', 'acknowledged']
    
    template_records = []
    for r in records:
        clean_r = {k: r.get(k, '') for k in essential_keys}
        template_records.append(clean_r)
        
    expanded = []
    locations = ['Alex', 'Cairo', 'East Delta', 'West Delta', 'North Upper', 'South Upper', 'Sinai']
    vendors = ['Huawei', 'Ericsson', 'Nokia', 'ZTE']
    networks = ['2G', '3G', '4G', '5G']
    severities = ['Critical', 'Major', 'Minor', 'Warning']
    priorities = ['Critical', 'Hotspot', 'Major', 'Minor']
    domains = ['TX', 'MW', 'RAN', 'CORE']

    NUM_RECORDS = 500000
    print(f"Generating {NUM_RECORDS} massive randomized records...")

    for i in range(NUM_RECORDS):
        new_rec = dict(random.choice(template_records))
        new_rec['alarmid'] = f"ALM_MEGA_{i}"
        
        # Modify fields completely randomly so Deduplication doesn't wipe them
        new_rec['location'] = random.choice(locations)
        new_rec['vendor'] = random.choice(vendors)
        new_rec['networktype'] = random.choice(networks)
        new_rec['standardalarmseverity'] = random.choice(severities)
        new_rec['sitepriority'] = random.choice(priorities)
        new_rec['domain'] = random.choice(domains)
        
        site_id = f"SITE_{random.randint(10000, 99999)}"
        new_rec['sitename'] = f"{new_rec['location']}_{site_id}"
        new_rec['sitecode'] = site_id
        
        # Add flags
        new_rec['sitedownflag'] = 'Yes' if random.random() < 0.10 else 'No' 
        new_rec['sitepoweroff'] = 'Yes' if random.random() < 0.10 else 'No'
        new_rec['isvip'] = 'Yes' if random.random() < 0.05 else 'No'
        new_rec['isrootne'] = 'Yes' if random.random() < 0.05 else 'No'
        new_rec['acknowledged'] = 'Y' if random.random() < 0.50 else 'N'
        
        expanded.append(new_rec)
        
    print(f"Writing {len(expanded)} MEGA records to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({'result': expanded}, f, ensure_ascii=False)
        
    print("Done! You now have half a million distinct records.")

if __name__ == '__main__':
    expand_data()
