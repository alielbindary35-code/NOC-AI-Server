"""
NOC AI Operations Center — Local Test Server
Mirrors the n8n workflow exactly using 3-month alarm data.
Run: python noc_server.py
Then open NOC AI Assistant v4.1.html (pointing to localhost:5000)
"""

import sys, io
# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, re, time, os
from datetime import datetime, timedelta
from collections import Counter, OrderedDict
from urllib.parse import urlparse

# ═══════════════════════════════════════════════════════════
# 1. DATA LOADER
# ═══════════════════════════════════════════════════════════
DATA = []

def load_data(custom_path=None):
    global DATA
    
    if custom_path:
        path = custom_path
    else:
        path = os.path.join(os.path.dirname(__file__), '..', 'context', '3months.txt')
        
    print(f"[DATA] Loading data from: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    DATA = raw.get('result', raw.get('data', []))
    
    # Normalize key fields to ensure consistent filtering
    for r in DATA:
        # sitedownflag: could be "Yes"/"No" or 0/1
        sdf = r.get('sitedownflag', '')
        if sdf in (1, '1', True): r['sitedownflag'] = 'Yes'
        elif sdf in (0, '0', False, None): r['sitedownflag'] = 'No'
        
        # sitepoweroff
        spo = r.get('sitepoweroff', '')
        if spo in (1, '1', True): r['sitepoweroff'] = 'Yes'
        elif spo in (0, '0', False, None): r['sitepoweroff'] = 'No'
        
        # isrootne
        irn = r.get('isrootne', '')
        if irn in (1, '1', True): r['isrootne'] = 'Yes'
        elif irn in (0, '0', False, None): r['isrootne'] = 'No'
        
        # isvip — may live in originalValues only
        iv = r.get('isvip', r.get('originalValues', {}).get('isvip', ''))
        if iv in (1, '1', True, 'Yes'): r['isvip'] = 'Yes'
        else: r['isvip'] = 'No'
        
        # acknowledged — may be in originalValues
        ack = r.get('acknowledged', '')
        if ack == '' or ack is None:
            ack = r.get('originalValues', {}).get('acknowledged', '')
        if ack in (1, '1', True, 'Y', 'Yes'): r['acknowledged'] = 'Y'
        elif ack in (0, '0', False, 'N', 'No', '', None): r['acknowledged'] = 'N'
        
        # Ensure string fields
        for k in ['location','vendor','networktype','alarmname','domain',
                   'sitepriority','standardalarmseverity','severity',
                   'sitename','sitecode','city']:
            if r.get(k) is None: r[k] = ''
            else: r[k] = str(r[k])
        
        # firstoccurrence as int (ms timestamp)
        fo = r.get('firstoccurrence', 0)
        try: r['_ts'] = int(fo)
        except: r['_ts'] = 0

    # Stats
    locations = Counter(r['location'] for r in DATA if r['location'])
    vendors = Counter(r['vendor'] for r in DATA if r['vendor'])
    down = sum(1 for r in DATA if r['sitedownflag'] == 'Yes')
    power = sum(1 for r in DATA if r['sitepoweroff'] == 'Yes')
    
    print(f"[OK] Loaded {len(DATA):,} records")
    print(f"   Locations: {dict(locations)}")
    print(f"   Vendors:   {dict(vendors)}")
    print(f"   Site Down: {down}")
    print(f"   Power Off: {power}")
    print(f"   Root NE:   {sum(1 for r in DATA if r['isrootne']=='Yes')}")
    print(f"   VIP:       {sum(1 for r in DATA if r['isvip']=='Yes')}")
    print()


# ═══════════════════════════════════════════════════════════
# 2. REGEX QUERY PARSER (replaces Ollama AI Agent)
# ═══════════════════════════════════════════════════════════
def parse_question(msg):
    q = msg.lower().strip()
    p = {
        'intent': 'alarm_count',
        'category': '',
        'vendor': '',
        'region_input': '',
        'networktype': '',
        'severity': '',
        'sitedownflag': '',
        'sitepoweroff': '',
        'acknowledged': '',
        'isvip': '',
        'domain': '',
        'sitepriority': '',
        'city': '',
        'isrootne': '',
        'sitecode': '',
        'count_only': True,
        'user_question': msg,
    }

    # ── Intent ──
    if any(w in q for w in ['show', 'list', 'display', 'give me']):
        p['intent'] = 'list_alarms'
        p['count_only'] = False

    # ── Category ──
    if re.search(r'site.?down|down.?site|sites?.?down', q):
        p['category'] = 'SITE_DOWN'
        p['sitedownflag'] = 'Yes'
    elif re.search(r'power|بور', q):
        p['category'] = 'POWER'
        p['sitepoweroff'] = 'Yes'
    elif re.search(r'cell.?down', q):
        p['category'] = 'CELL_DOWN'

    # ── Vendor ──
    for v, canonical in [('huawei','Huawei'), ('nokia','Nokia'), ('zte','ZTE'), ('ericsson','Ericsson')]:
        if v in q:
            p['vendor'] = canonical
            break

    # ── Region ──
    if 'upper egypt' in q or 'upper' in q and 'egypt' in q:
        p['region_input'] = 'upper egypt'
    elif 'alex' in q:
        p['region_input'] = 'alex'
    elif 'cairo' in q or 'القاهر' in q:
        p['region_input'] = 'cairo'
    elif 'delta' in q or 'الدلتا' in q:
        p['region_input'] = 'delta'
    elif 'sinai' in q or 'سينا' in q:
        p['region_input'] = 'sinai'

    # ── Network Type ──
    m = re.search(r'\b(2g|3g|4g|5g)\b', q)
    if m:
        p['networktype'] = m.group(1).upper()

    # ── VIP ──
    if 'vip' in q:
        p['isvip'] = 'Yes'

    # ── Root NE ──
    if 'root' in q:
        p['isrootne'] = 'Yes'

    # ── Site Priority ──
    prio_match = re.search(r'(critical|hotspot|major|minor)\s*priority|priority\s*(critical|hotspot|major|minor)', q)
    if prio_match:
        pv = (prio_match.group(1) or prio_match.group(2)).capitalize()
        p['sitepriority'] = pv

    # ── Severity (alarm severity, not site priority) ──
    if not prio_match:  # avoid conflict
        for sv in ['critical', 'major', 'minor', 'warning']:
            if sv in q:
                p['severity'] = sv.capitalize()
                break

    # ── Acknowledged ──
    if 'unacknowledged' in q or 'not ack' in q or 'unack' in q:
        p['acknowledged'] = 'N'

    # ── Domain ──
    if re.search(r'\btx\b', q):
        p['domain'] = 'TX'
    elif re.search(r'\bmw\b|microwave', q):
        p['domain'] = 'MW'

    # ── Fallback: if nothing extracted, it's free chat ──
    has_context = any([p['category'], p['vendor'], p['region_input'],
                       p['networktype'], p['severity'], p['sitedownflag'],
                       p['sitepoweroff'], p['isvip'], p['domain'],
                       p['sitepriority'], p['isrootne'], p['acknowledged']])
    
    if not has_context:
        p['intent'] = 'unknown'

    return p


# ═══════════════════════════════════════════════════════════
# 3. LOCATION RESOLVER (same as n8n Resolve Location node)
# ═══════════════════════════════════════════════════════════
GEO_MAP = {
    'alex':        ['Alex'],
    'cairo':       ['Cairo'],
    'delta':       ['East Delta', 'West Delta'],
    'upper egypt': ['North Upper', 'South Upper'],
    'sinai':       ['Sinai'],
}

def resolve_location(region_input):
    if not region_input:
        return [], ''
    ri = region_input.lower().strip()
    if ri in GEO_MAP:
        locs = GEO_MAP[ri]
        return locs, ' | '.join(locs)
    return [region_input], region_input


# ═══════════════════════════════════════════════════════════
# 4. DATA FILTER (replaces API call + Normalize And Post Filter)
# ═══════════════════════════════════════════════════════════
def filter_records(records, params, locations):
    result = records
    steps = []

    # sitedownflag
    if params['sitedownflag'] == 'Yes':
        before = len(result)
        result = [r for r in result if r['sitedownflag'] == 'Yes']
        steps.append(f"sitedownflag=Yes: {before} -> {len(result)}")

    # sitepoweroff
    if params['sitepoweroff'] == 'Yes':
        before = len(result)
        result = [r for r in result if r['sitepoweroff'] == 'Yes']
        steps.append(f"sitepoweroff=Yes: {before} -> {len(result)}")

    # location
    if locations:
        before = len(result)
        result = [r for r in result if r.get('location', '') in locations]
        steps.append(f"location in {locations}: {before} -> {len(result)}")

    # vendor
    if params['vendor']:
        before = len(result)
        v = params['vendor'].lower()
        result = [r for r in result if r.get('vendor', '').lower() == v]
        steps.append(f"vendor={params['vendor']}: {before} -> {len(result)}")

    # networktype
    if params['networktype']:
        before = len(result)
        nt = params['networktype'].upper()
        result = [r for r in result if r.get('networktype', '').upper() == nt]
        steps.append(f"networktype={nt}: {before} -> {len(result)}")

    # isvip
    if params['isvip'] == 'Yes':
        before = len(result)
        result = [r for r in result if r.get('isvip') == 'Yes']
        steps.append(f"isvip=Yes: {before} -> {len(result)}")

    # isrootne
    if params['isrootne'] == 'Yes':
        before = len(result)
        result = [r for r in result if r.get('isrootne') == 'Yes']
        steps.append(f"isrootne=Yes: {before} -> {len(result)}")

    # sitepriority
    if params['sitepriority']:
        before = len(result)
        sp = params['sitepriority'].lower()
        result = [r for r in result if sp in r.get('sitepriority', '').lower()]
        steps.append(f"sitepriority={params['sitepriority']}: {before} -> {len(result)}")

    # severity
    if params['severity']:
        before = len(result)
        sv = params['severity'].lower()
        result = [r for r in result if sv in r.get('standardalarmseverity', '').lower()]
        steps.append(f"severity={params['severity']}: {before} -> {len(result)}")

    # acknowledged
    if params['acknowledged'] == 'N':
        before = len(result)
        result = [r for r in result if r.get('acknowledged') == 'N']
        steps.append(f"acknowledged=N: {before} -> {len(result)}")

    # domain
    if params['domain']:
        before = len(result)
        d = params['domain'].upper()
        result = [r for r in result if d in r.get('domain', '').upper()]
        steps.append(f"domain={d}: {before} -> {len(result)}")

    return result, steps


# ═══════════════════════════════════════════════════════════
# 5. DEDUPLICATE (same logic as n8n node)
# ═══════════════════════════════════════════════════════════
def deduplicate(records):
    seen = set()
    unique = []
    for r in records:
        key = r.get('alarmid') or r.get('identifierfromprobe') or r.get('identifier', '')
        if not key:
            key = f"{r.get('sitename','')}-{r.get('alarmname','')}-{r.get('networktype','')}"
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# ═══════════════════════════════════════════════════════════
# 6. REPLY FORMATTER (same as n8n Deduplicate And Format Reply)
# ═══════════════════════════════════════════════════════════
def format_reply(records, params, location_label, filter_steps):
    now = datetime.now()
    isSiteDown = params['sitedownflag'] == 'Yes' or params['category'] == 'SITE_DOWN'
    isPower = params['category'] == 'POWER'
    count_only = params['count_only']
    
    total = len(records)
    W = 46
    SEP = '━' * W
    hr  = '─' * W

    # Header
    reply = f"📡 NOC Report — {now.strftime('%Y-%m-%d')}\n"
    reply += f"   Period  : 00:00:00 → 23:59:59\n"
    reply += SEP + "\n"

    # Filters
    fl = []
    if location_label:       fl.append(f"  📍 Location  : {location_label}")
    if params['category']:   fl.append(f"  📂 Category  : {params['category']}")
    if isSiteDown:           fl.append(f"  🔴 Site Down : Yes")
    if isPower:              fl.append(f"  ⚡ Power Off : Yes")
    if params['isvip']=='Yes': fl.append(f"  ⭐ VIP Only  : Yes")
    if params['vendor']:     fl.append(f"  🏭 Vendor    : {params['vendor']}")
    if params['networktype']:fl.append(f"  📡 Network   : {params['networktype']}")
    if params['domain']:     fl.append(f"  🌐 Domain    : {params['domain']}")
    if params['sitepriority']: fl.append(f"  🎯 Priority  : {params['sitepriority']}")
    if params['severity']:   fl.append(f"  🔔 Severity  : {params['severity']}")
    if params['acknowledged']=='N': fl.append(f"  ✅ Ack       : No")
    if params['isrootne']=='Yes': fl.append(f"  🌳 Root NE   : Yes")

    if fl:
        reply += "🔎 Filters:\n" + "\n".join(fl) + "\n"
        reply += hr + "\n"

    reply += f"📊 TOTAL  : {total} alarm{'s' if total != 1 else ''}\n"
    reply += hr + "\n"

    # Breakdown
    if records:
        # Group by alarm name
        groups = Counter()
        for r in records:
            name = r.get('alarmname') or r.get('rawalarmname', '') or 'Unknown'
            tally = 1
            try: tally = int(r.get('tally', 1))
            except: pass
            groups[name] += tally

        sorted_groups = groups.most_common()
        group_total = sum(v for _, v in sorted_groups)

        if isSiteDown and not count_only:
            # Site list mode
            top = min(15, len(records))
            reply += f"🏗️  Top {top} Affected Sites:\n\n"
            reply += "  #   Code           Tech   Vendor\n"
            reply += "  " + "─" * 38 + "\n"
            for i in range(top):
                r = records[i]
                n = str(i + 1).rjust(2)
                sc = (r.get('sitename') or r.get('sitecode') or '?')[:14].ljust(14)
                tc = (r.get('networktype') or '?')[:6].ljust(6)
                vn = r.get('vendor') or '?'
                reply += f"  {n}. {sc} {tc}  {vn}\n"
            if total > top:
                reply += f"\n  ... and {total - top} more sites\n"
        else:
            # Breakdown by alarm name
            label = "⚡ By Alarm Type:" if isPower else "📋 By Alarm Name:"
            reply += label + "\n"
            maxV = sorted_groups[0][1] if sorted_groups else 1
            for name, count in sorted_groups[:20]:
                lb = (name[:27] + '…') if len(name) > 28 else name.ljust(28)
                cn = str(count).rjust(5)
                barLen = round((count / maxV) * 10) if maxV > 0 else 0
                bar = '█' * barLen + '░' * (10 - barLen)
                reply += f"  {lb} {cn}  {bar}\n"
            
            if len(sorted_groups) > 20:
                reply += f"\n  ... and {len(sorted_groups) - 20} more types\n"
            
            if group_total != total:
                reply += f"\n  ℹ️  Based on {len(records)} of {group_total} records\n"

    reply += SEP
    return reply, total


# ═══════════════════════════════════════════════════════════
# 7. FREE CHAT HANDLER (same as n8n Free Chat Handler)
# ═══════════════════════════════════════════════════════════
def free_chat_reply(question):
    q = question.lower().strip()
    greetings = ['hi','hello','hey','howdy','هاي','سلام','مرحبا','اهلا','أهلا','ازيك','هلو']
    thanks = ['thanks','thank you','شكرا','شكراً','تسلم','مشكور']

    if any(q == g or q.startswith(g + ' ') for g in greetings):
        return ("👋 Hello! I'm the NOC Operations AI Assistant for e& Egypt.\n\n"
                "I can help you with:\n"
                "  📊 Alarm counts & breakdowns\n"
                "  📍 Site down status by region\n"
                "  ⚡ Power alarm queries\n"
                "  🏢 FM Office / Region analysis\n"
                "  📡 Vendor & network type filtering\n\n"
                "Example questions:\n"
                "  'How many sites are down in Alex?'\n"
                "  'Show Critical alarms in Cairo'\n"
                "  'Count 4G Nokia power alarms'\n"
                "  'How many down sites in Delta?'")
    
    if any(t in q for t in thanks):
        return ("😊 You're welcome! I'm always here to help with NOC alarm queries.\n\n"
                "Feel free to ask anything else about alarms, sites, or regions!")

    return ("🤖 I'm specialized in NOC alarm analysis.\n\n"
            "I can answer questions like:\n"
            "  'How many sites are down today?'\n"
            "  'Show power alarms in Sinai'\n"
            "  'Count Major Nokia alarms in Delta'\n"
            "  'How many Critical 4G alarms in Alex?'\n\n"
            "Please ask an alarm-related question and I'll do my best!")


# ═══════════════════════════════════════════════════════════
# 8. HTTP SERVER (replaces n8n Webhook + Respond to Webhook)
# ═══════════════════════════════════════════════════════════
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend_ui'))

from urllib.parse import unquote

class NocHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve HTML/CSS/JS files so browser can access via http://"""
        path = unquote(self.path.strip('/'))
        if path == '' or path == '/':
            path = 'NOC AI Assistant v4.1.html'
        
        filepath = os.path.join(STATIC_DIR, path.replace('/', os.sep))
        if not os.path.isfile(filepath):
            self.send_error(404, f'File not found: {path}')
            return
        
        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.json': 'application/json; charset=utf-8',
        }
        ct = content_types.get(ext, 'application/octet-stream')
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()
    
    def do_POST(self):
        t0 = time.time()
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        msg = body.get('message', '').strip()

        if not msg:
            self._respond({'reply': '⚠️ Empty message', 'total': 0, 'debug': {}})
            return

        # Step 1: Parse question (replaces AI Agent + Parse Agent Output)
        params = parse_question(msg)

        # Step 2: Free Chat check (replaces Is Free Chat? + Route IF)
        if params['intent'] == 'unknown':
            reply = free_chat_reply(msg)
            self._respond({
                'reply': reply,
                'total': 0,
                'debug': {
                    'type': 'free_chat',
                    'question': msg,
                    'parsed_params': params,
                    'timestamp': datetime.now().isoformat()
                }
            })
            return

        # Step 3: Resolve Location (same as n8n node)
        locations, location_label = resolve_location(params['region_input'])

        # Step 4: Filter data (replaces Build SQL + API Call + Normalize)
        filtered, filter_steps = filter_records(DATA, params, locations)

        # Step 5: Deduplicate
        unique = deduplicate(filtered)

        # Step 6: Format reply (same as n8n Deduplicate And Format Reply)
        reply, total = format_reply(unique, params, location_label, filter_steps)

        elapsed = round((time.time() - t0) * 1000, 1)

        # Step 7: Build debug (same as n8n Build Debug Response)
        debug = {
            'type': 'alarm_query',
            '1_user_request': {
                'question': msg,
                'intent_interpreted': params['intent']
            },
            '2_parsed_params': {
                'category': params['category'],
                'vendor': params['vendor'],
                'networktype': params['networktype'],
                'sitedownflag': params['sitedownflag'],
                'sitepoweroff': params['sitepoweroff'],
                'isvip': params['isvip'],
                'isrootne': params['isrootne'],
                'sitepriority': params['sitepriority'],
                'severity': params['severity'],
                'acknowledged': params['acknowledged'],
                'domain': params['domain'],
            },
            '3_geography': {
                'raw_input': params['region_input'],
                'resolved_locations': locations,
                'label': location_label
            },
            '4_filter_pipeline': filter_steps,
            '5_results': {
                'total_data': len(DATA),
                'after_filter': len(filtered),
                'after_dedup': len(unique),
                'final_total': total
            },
            '6_performance': {
                'response_time_ms': elapsed
            }
        }

        self._respond({
            'reply': reply,
            'total': total,
            'debug': debug
        })

        # Console log
        print(f"  [OK] [{elapsed}ms] \"{msg}\" -> {total} results ({len(filter_steps)} filters)")

    def _respond(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):
        pass  # Suppress default log


# ═══════════════════════════════════════════════════════════
# 9. STARTUP
# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  NOC AI Local Test Server")
    print("=" * 50)
    
    custom_data_file = None
    if len(sys.argv) > 1:
        custom_data_file = sys.argv[1]
        
    load_data(custom_data_file)
    
    port = 5000
    server = HTTPServer(('0.0.0.0', port), NocHandler)
    print(f"[READY] Server running on http://localhost:{port}/webhook/chat")
    print(f"   Open NOC AI Assistant v4.1.html in your browser")
    print(f"   Press Ctrl+C to stop")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
