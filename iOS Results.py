import requests, csv, re
from collections import defaultdict

# add A collection of keywords that have appeared for each app (November 1)
appid_to_keywords = defaultdict(set)

APPSTORE_URL = "https://itunes.apple.com/search"
COUNTRY = "us"  # change country if needed
LIMIT = 200  # App Store search apps max per keyword

# keywords
KEYWORDS = [
    "domestic violence",
    "intimate partner violence",
    "violence prevention",
    "physical violence",
    "battered partner",
    "sexual violence",
    "sexual assault",
    "rape",
    "stalking",
    "emotional abuse",
    "spouse abuse",
    "partner abuse",
    "relationship abuse",
    "relationship violence",
    "strangulation",
    "cyber abuse",
    "cyber harassment",
    "financial abuse",
    "trafficking",
    "coercion",
    "animal abuse",
    "child abuse"

]

# IPV hints from Ashley & Drew (used to FILTER relevant apps)
ASHLEY_HINTS = [
    "Partner", "Marriage", "Family", "Social", "Connection", "Healthy relationship",
    "Toxic", "Support", "Trauma bonds", "Healing", "Interpersonal", "Trauma",
    "Community", "Empowerment", "Woman-centered", "Affirming", "Strength"
]
DREW_HINTS = [
    "abuse help", "abuse helpline", "abuse prevention", "abuse shelter", "abuse survivor",
    "bad relationship", "consent", "consent education", "dating abuse", "dating health",
    "dating violence", "digital abuse", "domestic abuse", "domestic violence", "dv help",
    "dv shelter", "dv survivor", "emotional abuse", "family violence", "gaslighting",
    "good relationship", "happy relationship", "healthy couple", "healthy dating",
    "healthy relationship", "helpline", "partner abuse", "red flags", "relationship abuse",
    "relationship education", "relationship violence", "safe dating", "teen abuse",
    "teen dating violence"]
IPV_HINTS = ASHLEY_HINTS + DREW_HINTS
IPV_RE = re.compile("|".join([re.escape(x) for x in IPV_HINTS]), re.IGNORECASE)


def fetch_ios(term, country=COUNTRY, limit=LIMIT):
    """Return (total_resultCount, list_of_app_items limited to 200)."""
    params = {"term": term, "entity": "software", "country": country, "limit": limit}
    r = requests.get(APPSTORE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    total = data.get("resultCount", 0)
    results = [x for x in data.get("results", []) if x.get("kind") == "software"]
    return total, results


def matches_ipv_hints(app):
    """True if any Ashley/Drew hint appears in title or description."""
    name = (app.get("trackName") or "")
    desc = (app.get("description") or "")
    return IPV_RE.search(name) or IPV_RE.search(desc)


def summarize(app):
    return {
        "Name of each app": app.get("trackName"),
        "App description or overview": app.get("description"),
        "App rating": app.get("averageUserRating"),
        "Number of reviews": app.get("userRatingCount"),
        "Category (as listed in the app store)": app.get("primaryGenreName"),
        "App developer name": app.get("sellerName") or app.get("artistName"),
        "Store link": app.get("trackViewUrl"),
        "App id (internal)": app.get("trackId"),
    }


per_keyword_rows = []
appid_count = defaultdict(int)
appid_cache = {}

for kw in KEYWORDS:
    total, results = fetch_ios(kw)
    filtered = [app for app in results if matches_ipv_hints(app)]

    if not filtered:
        # still record the total for the keyword even if no filtered apps
        per_keyword_rows.append({
            "Keyword(s)": kw,
            "Operating system": "iOS",
            "Total number of search results": total,
            "Name of each app": "(no app matched IPV hints)",
            "App description or overview": "",
            "App rating": "",
            "Number of reviews": "",
            "Category (as listed in the app store)": "",
            "App developer name": "",
            "Store link": "",
        })
        continue

    for i, app in enumerate(filtered):
        s = summarize(app)
        appid = s.get("App id (internal)")
        if appid:
            appid_count[appid] += 1
            if appid not in appid_cache:
                appid_cache[appid] = s
                # Record keywords (Novenmber 1)
                appid_to_keywords[appid].add(kw)

        per_keyword_rows.append({
            "Keyword(s)": kw if i == 0 else "",
            "Operating system": "iOS" if i == 0 else "",
            "Total number of search results": total if i == 0 else "",
            **{k: s[k] for k in [
                "Name of each app", "App description or overview", "App rating",
                "Number of reviews", "Category (as listed in the app store)",
                "App developer name", "Store link"
            ]}
        })

# CSV (current step)
per_kw_file = "ipv_ios_per_keyword.csv"
with open(per_kw_file, "w", newline="", encoding="utf-8") as f:
    cols = [
        "Keyword(s)", "Operating system", "Total number of search results",
        "Name of each app", "App description or overview", "App rating",
        "Number of reviews", "Category (as listed in the app store)",
        "App developer name", "Store link"
    ]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for row in per_keyword_rows:
        w.writerow(row)

# frequency summary for next step (It is just an simple example to show the possibly expected result for the next step)
freq_file = "ipv_ios_frequency_summary.csv"
with open(freq_file, "w", newline="", encoding="utf-8") as f:
    cols = [
        "App id (internal)", "Appearances across keywords",
        "Name of each app", "App description or overview", "App rating",
        "Number of reviews", "Category (as listed in the app store)",
        "App developer name", "Store link"
    ]
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for appid, cnt in sorted(appid_count.items(), key=lambda kv: kv[1], reverse=True):
        s = appid_cache.get(appid, {})
        w.writerow({
            "App id (internal)": appid,
            "Appearances across keywords": cnt,
            **{k: s.get(k, "") for k in cols[2:]}
        })

print(f"Pilot_completed.\n - Per keyword: {per_kw_file}\n - Frequency: {freq_file}")

# a) A shortlist with a frequency of ≥2 (including keywords that have appeared)
freq_threshold = 2  # if you want to change the threshold
shortlist_file = "ipv_ios_shortlist_ge2.csv"

with open(shortlist_file, "w", newline="", encoding="utf-8") as f:
    cols = [
        "App id (internal)", "Appearances across keywords", "Appeared keywords",
        "Name of each app", "App description or overview", "App rating",
        "Number of reviews", "Category (as listed in the app store)",
        "App developer name", "Store link"
    ]
w = csv.DictWriter(f, fieldnames=cols)
w.writeheader()
for appid, cnt in sorted(appid_count.items(), key=lambda kv: kv[1], reverse=True):
    if cnt >= freq_threshold:
        s = appid_cache.get(appid, {})
        w.writerow({
        "App id (internal)": appid,
        "Appearances across keywords": cnt,
     "Appeared keywords": ", ".join(sorted(appid_to_keywords.get(appid, []))),
    **{k: s.get(k, "") for k in cols[3:]}
})

print(f" Shortlist saved → {shortlist_file}")

# b) Manual screening template (for Paige's Title/Description review)
screen_file = "ipv_ios_screening_template.csv"

with open(shortlist_file, "r", encoding="utf-8") as fin, \
        open(screen_file, "w", newline="", encoding="utf-8") as fout:
    reader = csv.DictReader(fin)
cols = reader.fieldnames + [
    "Decision (Keep/Exclude/Unsure)",
    "Reason (why relevant or not)",
    "IPV scope tag (e.g., DV/IPV/Teen dating/Trafficking)",
    "Red flags (ads, paywall, misinformation?)",
    "Reviewer", "Review date"
]
w = csv.DictWriter(fout, fieldnames=cols)
w.writeheader()
for row in reader:
    row.update({
        "Decision (Keep/Exclude/Unsure)": "",
        "Reason (why relevant or not)": "",
        "IPV scope tag (e.g., DV/IPV/Teen dating/Trafficking)": "",
        "Red flags (ads, paywall, misinformation?)": "",
        "Reviewer": "",
        "Review date": ""
    })
w.writerow(row)

print(f" Screening template saved → {screen_file}")

