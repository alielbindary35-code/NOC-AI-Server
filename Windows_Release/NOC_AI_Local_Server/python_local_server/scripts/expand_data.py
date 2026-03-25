import json
import random
import os

def expand_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, '..', 'context', '3months.txt')
    output_path = os.path.join(base_dir, '..', 'context', 'expanded_data.txt')
    
    print(f"Reading from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    records = raw.get('result', raw.get('data', []))
    if not records:
        print("No records found in source file!")
        return

    print(f"Loaded {len(records)} original records.")
    
    locations = ['Alex', 'Cairo', 'East Delta', 'West Delta', 'North Upper', 'South Upper', 'Sinai']
    vendors = ['Huawei', 'Ericsson', 'Nokia', 'ZTE']
    networks = ['2G', '3G', '4G', '5G']
    severities = ['Critical', 'Major', 'Minor', 'Warning']
    priorities = ['Critical', 'High', 'Medium', 'Low']
    domains = ['TX', 'MW', 'RAN', 'CORE']
    
    expanded = []
    
    # Keep original records
    expanded.extend(records)
    
    # Generate 10000 new randomized records to ensure rich data
    for i in range(10000):
        # Pick a random template record to clone
        new_rec = dict(random.choice(records))
        
        # Modify fields to ensure we hit all conditions
        new_rec['location'] = random.choice(locations)
        new_rec['vendor'] = random.choice(vendors)
        new_rec['networktype'] = random.choice(networks)
        new_rec['standardalarmseverity'] = random.choice(severities)
        new_rec['sitepriority'] = random.choice(priorities)
        new_rec['domain'] = random.choice(domains)
        
        # Site identifiers
        site_id = f"SITE_{random.randint(1000, 9999)}"
        new_rec['sitename'] = f"{new_rec['location']}_{site_id}"
        new_rec['sitecode'] = site_id
        
        # Flags (make them frequent enough to test)
        new_rec['sitedownflag'] = 'Yes' if random.random() < 0.15 else 'No'  # 15% sites down
        new_rec['sitepoweroff'] = 'Yes' if random.random() < 0.15 else 'No' # 15% power off
        new_rec['isvip'] = 'Yes' if random.random() < 0.20 else 'No'        # 20% VIP
        new_rec['isrootne'] = 'Yes' if random.random() < 0.10 else 'No'     # 10% Root NE
        new_rec['acknowledged'] = 'Y' if random.random() < 0.50 else 'N'    # 50% Acked
        
        # Special logic to ensure testing edge cases
        # E.g., force a Site Down in Alex
        if i < 50:
            new_rec['location'] = 'Alex'
            new_rec['sitedownflag'] = 'Yes'
            new_rec['sitepoweroff'] = 'Yes'
        elif i < 100:
            new_rec['location'] = 'South Upper'
            new_rec['isvip'] = 'Yes'
            new_rec['sitedownflag'] = 'Yes'
            new_rec['networktype'] = '5G'
            
        expanded.append(new_rec)
        
    # Wrap back into expected json structure
    if 'result' in raw:
        raw['result'] = expanded
    elif 'data' in raw:
        raw['data'] = expanded
    else:
        raw = {'result': expanded}
        
    print(f"Writing {len(expanded)} expanded records to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False)
        
    print("Done! You now have a rich dataset ready for comprehensive testing.")

if __name__ == '__main__':
    expand_data()
