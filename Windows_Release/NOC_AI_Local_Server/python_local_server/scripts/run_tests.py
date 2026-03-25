import sys, os
import noc_server
import expand_data

def run_tests():
    print("Preparing MEGA database...")
    import expand_data_mega
    expand_data_mega.expand_data()
    
    # 2. Load the mega data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    expanded_path = os.path.join(base_dir, '..', 'context', 'mega_data.json')
    noc_server.load_data(expanded_path)
    
    test_questions = [
        "How many active alarms right now?",
        "How many site down today?",
        "How many power alarms today?",
        "How many VIP site down today?",
        "How many site down in alex today?",
        "How many site down in cairo today?",
        "How many site down in delta today?",
        "How many site down in upper egypt today?",
        "How many site down in sinai today?",
        "How many 2G site down today?",
        "How many 3G site down today?",
        "How many 4G site down today?",
        "How many 5G site down today?",
        "How many TX alarms today?",
        "How many Huawei site down today?",
        "How many Nokia site down today?",
        "How many ZTE site down today?",
        "How many Ericsson site down today?",
        "How many critical priority site down today?",
        "How many hotspot priority site down today?",
        "How many VIP site down in cairo?",
        "How many root alarms today?",
        "How many uncleared major alarms today?",
        "How many Huawei power alarms today?",
        "How many Nokia power alarms today?"
    ]

    import json
    
    results_out = []
    results_out.append("# NOC AI - Automated Test Results")
    results_out.append("This file contains the output of testing the hardcoded questions from the HTML files.\n")
    
    for q in test_questions:
        results_out.append(f"\n### ❓ QUESTION: {q}")
        params = noc_server.parse_question(q)
        
        if params['intent'] == 'unknown':
            results_out.append("  -> 🤖 Fallback to Free Chat")
            continue
            
        locations, label = noc_server.resolve_location(params['region_input'])
        
        # Build API Parameters representation
        api_params = {
            "sitedownflag": params["sitedownflag"],
            "sitepoweroff": params["sitepoweroff"],
            "vendor": params["vendor"],
            "networktype": params["networktype"],
            "domain": params["domain"],
            "severity": params["severity"],
            "criticality/priority": params["sitepriority"],
            "isVIP": params["isvip"],
            "isRoot": params["isrootne"],
            "location (resolved)": label
        }
        # Filter out empty entries for clarity
        api_params = {k: v for k, v in api_params.items() if v}
        results_out.append(f"  -> ⚙️ API Parameters sent: `{json.dumps(api_params, ensure_ascii=False)}`")
        
        filtered, filter_steps = noc_server.filter_records(noc_server.DATA, params, locations)
        unique = noc_server.deduplicate(filtered)
        reply, total = noc_server.format_reply(unique, params, label, filter_steps)
        
        results_out.append(f"  -> ✅ Total Alarms match: **{total}**")
        if total == 0:
            results_out.append(f"  -> ⚠️ ZERO RESULTS RETURNED!")
            results_out.append(f"     Filters applied: {filter_steps}")
        else:
            # Peek at top 1 result to confirm format
            results_out.append(f"     First matched site: `{unique[0].get('sitename', 'Unknown') if unique else 'N/A'}`")
            
    out_str = "\n".join(results_out)
    out_path = os.path.join(base_dir, '..', 'context', 'test_results.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out_str)
    print(f"Results saved to {out_path}")

if __name__ == '__main__':
    run_tests()
