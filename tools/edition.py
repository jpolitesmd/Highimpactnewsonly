#!/usr/bin/env python3
"""Build an edition of High Impact News Daily from items.json.

Usage (run from the repo root):
  python3 tools/edition.py morning            # writes email/today.json and archives the edition
  python3 tools/edition.py evening
  python3 tools/edition.py evening --archive-only   # archive without writing the email

Morning edition: "Overnight" (top 5 since 5 p.m. Eastern yesterday), then "Yesterday's biggest
stories" (top 5 from yesterday not already listed).
Evening edition: top 8 stories that happened since the morning edition (5 a.m. Eastern today);
never yesterday's stories or anything already in this morning's edition.
Every edition is saved to archive/YYYY-MM-DD-<edition>.json and listed in archive/index.json,
then tools/pages.py rebuilds the permanent web pages in editions/ and sitemap.xml.
"""
import html, json, os, sys, datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
SITE = "https://hinewsdaily.com"
SEC_LABEL = {"health": "Health", "sports": "Sports", "tech": "Tech & Space", "finance": "ISO20022"}


def sec(it): return it.get("section") or "news"
def lv(it):
    try: return max(1, min(5, int(it.get("impact", 1))))
    except Exception: return 1
def t(it):
    try: return datetime.datetime.fromisoformat(it["time"]).astimezone(ET)
    except Exception: return None
def eligible(it):
    return lv(it) >= (3 if sec(it) in ("news", "money", "finance", "tech") else 4)
def rank(lst): return sorted(lst, key=lambda i: (-lv(i), -(t(i).timestamp() if t(i) else 0)))


FRESH = datetime.timedelta(hours=12)  # "new" = happened or was added in the last 12 hours (Today tab rule)
MORNING_SWEEP = datetime.time(5)       # the morning edition covers news up to about 5 a.m. Eastern
EVENING_SEND = datetime.time(17)       # the evening edition goes out at 5 p.m. Eastern


def seen(it):
    """Latest of when it happened and when it was added, so overnight additions count as new."""
    ts = [x for x in (t(it),) if x]
    try: ts.append(datetime.datetime.fromisoformat(it["added_at"]).astimezone(ET))
    except Exception: pass
    return max(ts) if ts else None
def fresh(it, now): return seen(it) is not None and now - seen(it) <= FRESH
def fresh_ok(it): return lv(it) >= (2 if sec(it) in ("news", "money", "finance", "tech") else 3)
def added(it):
    try: return datetime.datetime.fromisoformat(it["added_at"]).astimezone(ET)
    except Exception: return None


def archived_ids(key):
    try: return {i["id"] for i in json.load(open(f"archive/{key}.json")).get("items", [])}
    except Exception: return set()


def select(items, edition, now):
    """Returns (stories, also-today window, groups); groups = [(heading or None, count), ...]."""
    today = now.date()
    if edition == "morning":
        # 1) Big stories overnight (since yesterday's 5 p.m. evening edition), then
        # 2) a recap of yesterday's biggest events that aren't already listed.
        yday = today - datetime.timedelta(days=1)
        since = datetime.datetime.combine(yday, EVENING_SEND, ET)
        overnight = rank([i for i in items if t(i) and since <= t(i) <= now and fresh_ok(i)])[:5]
        ids = {i["id"] for i in overnight}
        ylist = [i for i in items if t(i) and t(i).date() == yday and i["id"] not in ids]
        recap = rank([i for i in ylist if eligible(i)])[:5]
        if len(recap) < 3:
            ids2 = {i["id"] for i in recap}
            recap = rank(recap + rank([i for i in ylist if i["id"] not in ids2 and fresh_ok(i)])[:3 - len(recap)])
        if len(overnight) + len(recap) < 3:  # very quiet stretch: fall back to the last 72 hours
            ids = {i["id"] for i in overnight + recap}
            recap += rank([i for i in items if t(i) and now - t(i) <= datetime.timedelta(hours=72)
                           and eligible(i) and i["id"] not in ids])[:5 - len(overnight) - len(recap)]
        groups = []
        if overnight: groups.append(("Overnight", len(overnight)))
        if recap: groups.append(("Yesterday's biggest stories" if overnight else None, len(recap)))
        return overnight + recap, datetime.timedelta(hours=36), groups
    # Evening: only what happened since the morning edition (about 5 a.m. Eastern), nothing from yesterday.
    since = datetime.datetime.combine(today, MORNING_SWEEP, ET)
    morning = archived_ids(f"{today.isoformat()}-morning")
    pool = [i for i in items if t(i) and since <= t(i) <= now and fresh_ok(i) and i["id"] not in morning]
    if len(pool) < 3:  # also allow today's early-morning stories first reported after the morning edition
        ids = {i["id"] for i in pool}
        pool += [i for i in items if i["id"] not in ids and i["id"] not in morning and t(i)
                 and t(i).date() == today and added(i) and added(i) >= since and fresh_ok(i)]
    top = rank(pool)[:8]
    return top, now - since, [(None, len(top))]


def shorten(s, n):
    s = " ".join(s.split())
    if len(s) <= n: return s.rstrip(".")
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def main():
    edition = sys.argv[1] if len(sys.argv) > 1 else "morning"
    assert edition in ("morning", "evening")
    archive_only = "--archive-only" in sys.argv
    now = datetime.datetime.now(ET)
    date = now.date().isoformat()
    items = json.load(open("items.json"))["items"]
    upcoming = json.load(open("upcoming.json")).get("events", []) if os.path.exists("upcoming.json") else []

    top, window, groups = select(items, edition, now)
    starts = {}  # index of first story in each group -> heading
    n0 = 0
    for g, (heading, count) in enumerate(groups):
        if heading: starts[n0] = (heading, g > 0)
        n0 += count
    listed = {i["id"] for i in top}
    also = []
    for s in ("health", "sports", "tech", "finance"):
        c = rank([i for i in items if sec(i) == s and i["id"] not in listed and t(i) and now - t(i) <= window])
        if c: also.append(c[0])
    nxt = sorted([e for e in upcoming if e.get("date", "") >= date], key=lambda e: e["date"])[:3]

    label = "Morning edition" if edition == "morning" else "Evening edition"
    head = f"{label}, {now.strftime('%A, %b')} {now.day}"
    lead = rank(top)[0]["text"] if top else ""  # subject and archive lead: the most important story
    subject = f"{head}: {shorten(lead, max(20, 90 - len(head)))}" if top else head

    img = f"{SITE}/assets/email"
    HEAD_CSS = ("font-family:Georgia,'Times New Roman',Times,serif;font-size:21px;line-height:1.3;"
                "font-weight:bold;color:#1d1a16;margin:28px 0 8px")
    lines = [f'<a href="{SITE}/"><img src="{img}/masthead.png" alt="High Impact News Daily" width="560" '
             f'style="display:block;width:100%;max-width:560px;height:auto;border:0"></a>', "",
             f"**{label}, {now.strftime('%A, %B')} {now.day}**", "",
             "*What happened overnight, and yesterday's biggest stories. Five minutes. No spin.*"
             if edition == "morning" else "*What happened since this morning. Five minutes. No spin.*", ""]
    for n, i in enumerate(top):
        if n in starts:
            heading, rule = starts[n]
            lines += (["---", ""] if rule else []) + [f"**{heading}**", ""]
        lines += [f'<h3 style="{HEAD_CSS}">{html.escape(i.get("text", ""), quote=False)}</h3>', ""]
        if i.get("detail"): lines += [i["detail"], ""]
        src = f" [{i.get('source', 'Source')}]({i['url']})" if i.get("url") else ""
        meter = (f'<img src="{img}/impact-{lv(i)}.png" alt="" width="50" height="16" '
                 f'style="width:50px;height:16px;vertical-align:middle;border:0"> ')
        lines += [f"{meter}**Impact {lv(i)}/5.** {i.get('why', '')}{src}".strip(), ""]
    if also:
        lines += ["---", "", "**Also today**", ""]
        lines += [f"- **{SEC_LABEL[sec(i)]}:** {i.get('text', '')}" for i in also] + [""]
    if nxt:
        lines += ["**Coming up**", ""]
        for e in nxt:
            d = datetime.date.fromisoformat(e["date"])
            lines.append(f"- {d.strftime('%b')} {d.day}: {e['text']}")
        lines.append("")
    key = f"{date}-{edition}"
    lines += ["That's the news. Put the phone down and enjoy your day." if edition == "morning"
              else "That's the day. Put the phone down and enjoy your evening.", "",
              "---", "",
              f"**Know someone who'd like this?** Forward this email, or send them "
              f"[a link to this edition]({SITE}/editions/{key}/).", "",
              f"*Forwarded this? [Subscribe free]({SITE}/#subscribe) to get it twice a day.*", "",
              f"[Read it on the web]({SITE}/editions/{key}/) · "
              f"[Past editions]({SITE}/editions/)"]
    body = "\n".join(lines)

    send_at = datetime.datetime.combine(now.date(), datetime.time(6 if edition == "morning" else 17), ET)
    if not archive_only:
        os.makedirs("email", exist_ok=True)
        json.dump({"date": date, "edition": edition, "send_at": send_at.isoformat(),
                   "subject": subject, "body": body}, open("email/today.json", "w"), indent=1, ensure_ascii=False)

    os.makedirs("archive", exist_ok=True)
    keep = ("id", "section", "text", "detail", "why", "impact", "topic", "branch", "judicial", "court",
            "region", "time", "time_known", "source", "url")
    json.dump({"date": date, "edition": edition, "subject": subject, "published": send_at.isoformat(),
               "items": [{k: i[k] for k in keep if k in i} for i in top],
               "groups": [{"heading": h, "count": c} for h, c in groups],
               "also": [{k: i[k] for k in keep if k in i} for i in also],
               "upcoming": nxt},
              open(f"archive/{key}.json", "w"), indent=1, ensure_ascii=False)
    idx_path = "archive/index.json"
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {"editions": []}
    idx["editions"] = [e for e in idx["editions"] if e.get("key") != key]
    idx["editions"].append({"key": key, "date": date, "edition": edition, "count": len(top),
                            "lead": lead})
    idx["editions"].sort(key=lambda e: (e["date"], e["edition"] == "evening"), reverse=True)
    idx["updated"] = now.isoformat(timespec="seconds")
    json.dump(idx, open(idx_path, "w"), indent=1, ensure_ascii=False)
    print(f"{key}: {len(top)} stories, {len(also)} also-today; subject: {subject}")
    # Permanent web pages for every edition, plus the sitemap (see tools/pages.py).
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import pages
        pages.main()
    except Exception as err:  # never let page building block the email
        print(f"PROBLEM: edition pages not rebuilt: {err}")


if __name__ == "__main__":
    main()
