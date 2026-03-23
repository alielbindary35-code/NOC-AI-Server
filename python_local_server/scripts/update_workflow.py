import json
import re

file_path = r'E:\Project AI\UC1 Customer AI Chat Agent\alarm sample\AI agent workflow\producation\NOC AI SQL Agent V3.2 Webhook.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

data['name'] = 'NOC AI SQL Agent V3.3 Webhook'

for node in data['nodes']:
    name = node['name']
    
    if name == 'AI Agent':
        new_prompt = '''You are an advanced AI assistant for a Telecom Network Operations Center (NOC). 
Your role is to understand user requests in English or Arabic, preserve the context, and extract precise parameters for downstream systems.

### RULES:
1. Output MUST be ONLY valid JSON matching the exact schema below. No markdown formatting, no conversational text.
2. Use "(empty)" for any missing field. Do NOT invent or guess values.
3. Interpret semantic meanings:
   - "site down", "disconnected", "offline" -> category: SITE_DOWN, sitedownflag: Yes
   - "power", "AC/DC", "generator" -> category: POWER
   - "4G", "LTE" -> technology: 4G, networktype: 4G
   - "delta", "الدلتا" -> region_input: delta
4. Keep the original user question in `user_question`.
5. If the request is a simple greeting, set intent to "unknown".

### SCHEMA:
{
  "user_question": "Exact original question here",
  "intent": "alarm_count" | "list_alarms" | "unknown",
  "category": "SITE_DOWN" | "POWER" | "CELL_DOWN" | "(empty)",
  "vendor": "Huawei" | "Nokia" | "ZTE" | "(empty)",
  "region_input": "extracted region name or (empty)",
  "location": "(empty)", 
  "fm_offices": "(empty)",
  "technology": "2G" | "3G" | "4G" | "5G" | "(empty)",
  "networktype": "2G" | "3G" | "4G" | "5G" | "(empty)",
  "severity": "Critical" | "Major" | "Minor" | "Warning" | "Cleared" | "(empty)",
  "sitedownflag": "Yes" | "No" | "(empty)",
  "sitepoweroff": "Yes" | "No" | "(empty)",
  "acknowledged": "ack" | "unack" | "(empty)",
  "isvip": "Yes" | "No" | "(empty)",
  "domain": "2G" | "3G" | "4G" | "5G" | "TX" | "MW" | "Power" | "(empty)",
  "sitecode": "extracted site code or (empty)",
  "count_only": true | false
}'''
        if 'parameters' in node and 'text' in node['parameters']:
            node['parameters']['text'] = new_prompt

    elif name == 'Resolve Location':
        js = '''const aiData = $('AI Agent').item.json.output || {};
let normalizedInput = String(aiData.region_input || "").toLowerCase().trim();

const fuzzyMap = {
  "dleta": "delta", "alx": "alex", "alexndria": "alex", "cai": "cairo",
  "sinii": "sinai", "uper": "upper egypt", "upper": "upper egypt"
};
if (fuzzyMap[normalizedInput]) {
  normalizedInput = fuzzyMap[normalizedInput];
}

const geoMap = {
  "alex": "Alex",
  "cairo": "Cairo",
  "delta": "East Delta|West Delta",
  "upper egypt": "North Upper|South Upper",
  "sinai": "Sinai",
  "الاسكندريه": "Alex",
  "القاهره": "Cairo",
  "الدلتا": "East Delta|West Delta",
  "الصعيد": "North Upper|South Upper",
  "سينا": "Sinai",
  "سيناء": "Sinai"
};

let resolvedLocation = "";
if (geoMap[normalizedInput]) {
  resolvedLocation = geoMap[normalizedInput];
} else if (normalizedInput && normalizedInput !== "(empty)") {
  resolvedLocation = aiData.region_input; 
}

return {
  ...aiData,
  location_resolved: resolvedLocation
};'''
        node['parameters']['jsCode'] = js

    elif name == 'Build SQL Query':
        js = '''const data = $input.first().json;
const category = data.category;
const vendor = data.vendor;
const technology = data.technology;

if (!category || category === "(empty)" || category === "DIRECT__") {
  return { query: "SELECT NULL as alarm_name LIMIT 0", category: "DIRECT__" };
}

let query = `SELECT alarm_name FROM ai_alarm_mappings WHERE category = '${category}'`;

if (vendor && vendor !== "(empty)") {
  query += ` AND vendor = '${vendor}'`;
}

if (technology && technology !== "(empty)") {
  query += ` AND (technology = '${technology}' OR technology = '')`;
}

return {
  query: query,
  category: category
};'''
        node['parameters']['jsCode'] = js

    elif name == 'Build Time Range':
        js = node['parameters'].get('jsCode', '')
        js = re.sub(r'limit\s*:\s*\d+', 'limit: 1000', js)
        node['parameters']['jsCode'] = js

    elif name == 'Build API Payload':
        js = '''const aiData = $('Resolve Location').item.json;
const timeData = $('Build Time Range').item.json;
const sqlItems = $items("Execute SQL Query");

let alarmNamesRaw = [];
if (aiData.category === "DIRECT__") {
  alarmNamesRaw.push("__DIRECT__");
} else {
  sqlItems.forEach(item => {
    if (item.json.alarm_name) alarmNamesRaw.push(item.json.alarm_name);
  });
}

let basePayload = {
    "start": timeData.start,
    "limit": timeData.limit,
    "starttime": timeData.starttime,
    "endtime": timeData.endtime,
    "type": timeData.type
};

function addIfValid(key, value) {
    if (value && String(value).toLowerCase() !== "(empty)") {
        basePayload[key] = value;
    }
}

addIfValid("location", aiData.location_resolved);
addIfValid("vendor", aiData.vendor);
addIfValid("networktype", aiData.networktype);
addIfValid("sitedownflag", aiData.sitedownflag);
addIfValid("sitepoweroff", aiData.sitepoweroff);
addIfValid("acknowledged", aiData.acknowledged);
addIfValid("sitecode", aiData.sitecode);
addIfValid("severity", aiData.severity);
addIfValid("isvip", aiData.isvip);
addIfValid("domain", aiData.domain);

if (alarmNamesRaw.length > 0 && !alarmNamesRaw.includes("__DIRECT__")) {
    basePayload["alarmname"] = alarmNamesRaw.join("|");
}

let isCountOnly = aiData.intent === 'alarm_count' || aiData.count_only === true;

return [{ 
  json: { 
    payload: basePayload, 
    metadata: { count_only: isCountOnly } 
  } 
}];'''
        node['parameters']['jsCode'] = js

    elif name == 'Build Debug Response':
        js = '''const aiOutput = $('Resolve Location').item.json || {}; 
const sqlQuery = $('Build SQL Query').item.json ? $('Build SQL Query').item.json.query : "No SQL generated";
const sqlResults = $items("Execute SQL Query").map(i => i.json);
const apiPayload = $('Build API Payload').item.json ? $('Build API Payload').item.json.payload : {};
const finalCount = $items("Deduplicate And Format Reply").length;

let originalApiCount = 0;
try {
  originalApiCount = $items("Normalize And Post Filter").length;
} catch(e) {}

const debugData = {
  "1_user_request": {
    "question": aiOutput.user_question || "unknown",
    "intent_interpreted": aiOutput.intent || "unknown"
  },
  "2_ai_extraction": {
    "category": aiOutput.category,
    "vendor": aiOutput.vendor,
    "technology": aiOutput.technology,
    "networktype": aiOutput.networktype,
    "filters": {
      "isvip": aiOutput.isvip,
      "sitedownflag": aiOutput.sitedownflag,
      "severity": aiOutput.severity
    }
  },
  "3_geography": {
    "raw_input": aiOutput.region_input,
    "resolved_pipe_string": aiOutput.location_resolved
  },
  "4_database_mapping": {
    "sql_executed": sqlQuery,
    "alarms_found_count": sqlResults.length,
    "alarm_names": sqlResults.map(r => r.alarm_name)
  },
  "5_api_execution": {
    "actual_payload_sent": apiPayload,
    "raw_records_returned": originalApiCount
  },
  "6_post_processing": {
    "deduplicated_final_count": finalCount
  }
};

const respItems = $items("Deduplicate And Format Reply");
let finalReplyMsg = "Done";
if (respItems.length > 0 && respItems[0].json && respItems[0].json.reply) {
    finalReplyMsg = respItems[0].json.reply;
}

return {
    reply: finalReplyMsg,
    total: finalCount,
    debug: debugData
};'''
        node['parameters']['jsCode'] = js

out_path = r'E:\Project AI\UC1 Customer AI Chat Agent\alarm sample\AI agent workflow\producation\NOC AI SQL Agent V3.3 Webhook.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
print('SUCCESS: Saved as NOC AI SQL Agent V3.3 Webhook.json')
