# 📋 Sidebar Quick Queries — Full Walkthrough

## How It Works (The Pipeline)

Every sidebar button sends a **text message** to the n8n Webhook. The message goes through this pipeline:

```
User clicks button
  → sends {"message": "How many site down in alex today?"}
  → Webhook receives it
  → Extract Message (gets the text)
  → AI Agent (Ollama qwen2.5:14b) parses text → outputs 17 key=value lines
  → Parse Agent Output (normalizes values)
  → Is Free Chat? (checks: if intent=unknown AND no alarm fields → free chat, else → alarm query)
  → Route IF (true=Free Chat Handler, false=continue)
  → Resolve Location (maps "alex" → "Alex", "delta" → "East Delta|West Delta")
  → Build SQL (decides what SQL to run on ai_alarm_mappings DB table)
  → Get Alarm Names From Mapping (runs SQL on PostgreSQL)
  → Build Time Range (sets starttime/endtime + type=1 or 3)
  → Build API Payload (builds HTTP headers for the API call)
  → Call Alarm API (HTTPS POST to alarm system)
  → Normalize And Post Filter (cleans response + post-filters)
  → Deduplicate And Format Reply (formats the reply text)
  → Build Debug Response (adds debug JSON)
  → Respond to Webhook (returns {reply, total, debug} to frontend)
```

---

## 🔑 Key API Parameters (HTTP Headers)

The alarm API accepts these as **HTTP headers** in `Call Alarm API` node:

| Header | Values | Description |
|--------|--------|-------------|
| `starttime` | Unix timestamp (ms) | Start of query period |
| `endtime` | Unix timestamp (ms) | End of query period |
| [start](file:///e:/Project%20AI/UC1%20Customer%20AI%20Chat%20Agent/alarm%20sample/AI%20agent%20workflow/producation/NOC%20AI%20Dashboard%20v4.0.html#421-427) | `0` | Pagination offset |
| `limit` | `1000` | Max records to return |
| `type` | `1` = Active only, `2` = Historical, `3` = Both | Query scope |
| `location` | `Alex`, `Cairo`, `East Delta\|West Delta`, etc. | FM office / region (pipe-separated for multi) |
| `sitedownflag` | `Yes` or empty | Filter for down sites |
| `sitepoweroff` | `Yes` or empty | Power off flag (unreliable in API!) |
| `alarmname` | Alarm name string or empty | Specific alarm (from DB mapping) |
| `networktype` | `2G`, `3G`, `4G`, `5G` or empty | Network technology |
| `vendor` | `Huawei`, `Nokia`, `ZTE`, `Ericsson` or empty | Equipment vendor |
| `isvip` | `Yes` or empty | VIP site filter |
| `domain` | `TX`, `MW`, `RAN` or empty | Network domain |
| `sitepriority` | `Critical`, `Hotspot`, `Major`, `Minor` or empty | Site importance |
| `isrootne` | `Yes` or empty | Root NE alarm filter |
| `acknowledged` | `Y`, `N` or empty | Acknowledgment status |
| `standardalarmseverity` | `Critical`, `Major`, `Minor`, `Warning` or empty | Alarm severity |
| `sitecode` | Site code string or empty | Specific site |
| `city` | FM office name or empty | Specific FM office |

---

## 📍 Section 1: Site Down

### Q1: "How many site down today?"
| Step | Value |
|------|-------|
| AI extracts | `intent=alarm_count, category=SITE_DOWN, sitedownflag=Yes, count_only=true` |
| Resolve Location | (empty — no region) |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` (no DB lookup needed — sitedownflag works in API) |
| Build Time Range | `type=1` (active), today 00:00:00 → 23:59:59 |
| **API Headers** | `sitedownflag=Yes`, `type=1`, today's timestamps |
| Expected result | Total count of all sites currently down |

### Q2: "How many site down in alex today?"
| Step | Value |
|------|-------|
| AI extracts | `intent=alarm_count, category=SITE_DOWN, region_input=alex, sitedownflag=Yes, count_only=true` |
| Resolve Location | `alex` → `"Alex"` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` |
| **API Headers** | `sitedownflag=Yes`, `location=Alex`, `type=1` |

### Q3: "How many site down in cairo today?"
| Step | Value |
|------|-------|
| AI extracts | same as Q2 but `region_input=cairo` |
| Resolve Location | `cairo` → `"Cairo"` |
| **API Headers** | `sitedownflag=Yes`, `location=Cairo`, `type=1` |

### Q4: "How many site down in delta today?"
| Step | Value |
|------|-------|
| AI extracts | `region_input=delta` |
| Resolve Location | `delta` → `"East Delta|West Delta"` ⚠️ **pipe-separated** (2 sub-locations) |
| **API Headers** | `sitedownflag=Yes`, `location=East Delta|West Delta`, `type=1` |
| **Note** | API must support pipe-separated locations, or workflow makes 2 calls |

### Q5: "How many site down in upper egypt today?"
| Step | Value |
|------|-------|
| Resolve Location | `upper egypt` → `"North Upper|South Upper"` |
| **API Headers** | `sitedownflag=Yes`, `location=North Upper|South Upper`, `type=1` |

### Q6: "How many site down in sinai today?"
| Step | Value |
|------|-------|
| Resolve Location | `sinai` → `"Sinai"` |
| **API Headers** | `sitedownflag=Yes`, `location=Sinai`, `type=1` |

### Q7: "How many VIP site down today?"
| Step | Value |
|------|-------|
| AI extracts | `category=SITE_DOWN, sitedownflag=Yes, isvip=Yes` |
| Resolve Location | (empty) |
| **API Headers** | `sitedownflag=Yes`, `isvip=Yes`, `type=1` |

---

## ⚡ Section 2: Power Alarms

> **Important:** The `sitepoweroff` API header is **unreliable** — it doesn't filter correctly.
> So for power alarms, the workflow uses **alarm names from the PostgreSQL database** (`ai_alarm_mappings` table).

### Q8: "How many power alarms today?"
| Step | Value |
|------|-------|
| AI extracts | `intent=alarm_count, category=POWER, sitepoweroff=Yes, count_only=true` |
| Build SQL | `SELECT alarm_name FROM ai_alarm_mappings WHERE category = 'POWER' ORDER BY alarm_name;` |
| DB returns | List of alarm names like: `"Mains Fail"`, `"Battery Low"`, `"Rectifier Fail"`, etc. |
| Build API Payload | Makes **separate API call for each alarm name** OR sends them as alarmname header |
| **API Headers** | `alarmname=<each power alarm name>`, `type=1` |
| Reply format | Total count + breakdown by alarm type with tally counts |

### Q9: "How many power alarms in alex today?"
| Step | Value |
|------|-------|
| Same as Q8 but with | `region_input=alex` |
| Resolve Location | `alex` → `"Alex"` |
| **API Headers** | `alarmname=<power alarm names>`, `location=Alex`, `type=1` |

### Q10: "How many power alarms in cairo today?"
| Step | Value |
|------|-------|
| Same as Q8 but | `location=Cairo` |

### Q11: "How many power alarms in delta today?"
| Step | Value |
|------|-------|
| Same as Q8 but | `location=East Delta|West Delta` |

---

## 📶 Section 3: By Network Type

### Q12: "How many 2G site down today?"
| Step | Value |
|------|-------|
| AI extracts | `category=SITE_DOWN, networktype=2G, sitedownflag=Yes` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` (SITE_DOWN → direct) |
| **API Headers** | `sitedownflag=Yes`, `networktype=2G`, `type=1` |

### Q13: "How many 3G site down today?"
| **API Headers** | `sitedownflag=Yes`, `networktype=3G`, `type=1` |

### Q14: "How many 4G site down today?"
| **API Headers** | `sitedownflag=Yes`, `networktype=4G`, `type=1` |

### Q15: "How many 5G site down today?"
| **API Headers** | `sitedownflag=Yes`, `networktype=5G`, `type=1` |

---

## 🏭 Section 4: By Vendor

### Q16: "How many Huawei site down today?"
| Step | Value |
|------|-------|
| AI extracts | `category=SITE_DOWN, vendor=Huawei, sitedownflag=Yes` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` |
| **API Headers** | `sitedownflag=Yes`, `vendor=Huawei`, `type=1` |

### Q17: "How many Nokia site down today?"
| **API Headers** | `sitedownflag=Yes`, `vendor=Nokia`, `type=1` |

### Q18: "How many ZTE site down today?"
| **API Headers** | `sitedownflag=Yes`, `vendor=ZTE`, `type=1` |

### Q19: "How many Ericsson site down today?"
| **API Headers** | `sitedownflag=Yes`, `vendor=Ericsson`, `type=1` |

---

## 🎯 Section 5: Priority (NEW)

### Q20: "How many critical priority site down today?"
| Step | Value |
|------|-------|
| AI extracts | `category=SITE_DOWN, sitedownflag=Yes, sitepriority=Critical` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` |
| **API Headers** | `sitedownflag=Yes`, `sitepriority=Critical`, `type=1` |

### Q21: "How many hotspot priority site down today?"
| **API Headers** | `sitedownflag=Yes`, `sitepriority=Hotspot`, `type=1` |

### Q22: "How many VIP site down in cairo?"
| **API Headers** | `sitedownflag=Yes`, `isvip=Yes`, `location=Cairo`, `type=1` |

---

## ⏳ Section 6: Alarm Aging (NEW)

### Q23: "Show unacknowledged critical alarms today"
| Step | Value |
|------|-------|
| AI extracts | `intent=list_alarms, acknowledged=N, severity=Critical, count_only=false` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` (no category → direct) |
| **API Headers** | `acknowledged=N`, `standardalarmseverity=Critical`, `type=1` |
| Post-filter | Normalize node filters by `acknowledged` field |

### Q24: "How many root alarms today?"
| Step | Value |
|------|-------|
| AI extracts | `intent=alarm_count, isrootne=Yes, count_only=true` |
| Build SQL | `SELECT '__DIRECT__' AS alarm_name` ← **Fixed! Was crashing before** |
| **API Headers** | `isrootne=Yes`, `type=1` |

---

## 📅 Section 7: Historical

### Q25: "How many site down in the last 7 days?"
| Step | Value |
|------|-------|
| AI extracts | `category=SITE_DOWN, sitedownflag=Yes` |
| Build Time Range | **`type=3`** (active+historical), starttime = now-7days, endtime = now |
| **API Headers** | `sitedownflag=Yes`, `type=3`, 7-day timestamps |
| **Note** | `type=3` is critical — `type=1` would only show currently active, missing resolved ones |

### Q26: "How many power alarms yesterday?"
| Step | Value |
|------|-------|
| Build Time Range | yesterday 00:00:00 → 23:59:59, **`type=3`** |
| Build SQL | Power alarm names from DB |
| **API Headers** | `alarmname=<power names>`, `type=3`, yesterday timestamps |

### Q27: "How many site down last 3 days in alex?"
| Step | Value |
|------|-------|
| Resolve Location | `alex` → `Alex` |
| Build Time Range | now-3days → now, **`type=3`** |
| **API Headers** | `sitedownflag=Yes`, `location=Alex`, `type=3` |

---

## ⚠️ Known Issues & Design Decisions

### 1. Power alarms use DB alarm names (not `sitepoweroff` header)
The API's `sitepoweroff` header doesn't reliably filter power alarms. So the workflow:
- Queries PostgreSQL `ai_alarm_mappings` table for `category='POWER'`
- Gets specific alarm names (e.g., "Mains Fail", "Battery Low")
- Sends those as `alarmname` header to the API

### 2. `type` parameter logic
- **Today queries** → `type=1` (active alarms only)
- **Historical queries** (last X days, yesterday) → `type=3` (active + historical)
- This is determined in `Build Time Range` node by checking if the question contains "last", "yesterday", "week"

### 3. Location resolution (pipe-separated)
- `alex` → `Alex` (single location)
- `delta` → `East Delta|West Delta` (pipe = 2 sub-locations)
- `upper egypt` → `North Upper|South Upper`
- `sinai` → `Sinai`
- `cairo` → `Cairo`

### 4. The AI bottleneck
Every single question goes through the Ollama AI model to extract parameters. This takes **3-5 seconds per question**. This is why the dashboard with 22 questions was so slow. The chat interface sends **1 question at a time** so it's not a problem.

### 5. Tally-based counting
The `Deduplicate And Format Reply` node uses the `r.tally` field from API response records for accurate counts (not just counting records). This is critical for power alarm breakdowns where one record might represent multiple occurrences.
