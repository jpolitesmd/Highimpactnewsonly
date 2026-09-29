#!/usr/bin/env python3
"""Build an edition of High Impact News Daily from items.json.

Usage (run from the repo root):
  python3 tools/edition.py morning            # writes email/today.json and archives the edition
  python3 tools/edition.py evening
  python3 tools/edition.py evening --archive-only   # archive without writing the email

Morning edition: the front-page selection (top 10 of the last 36 h, widening to 72 h / 168 h).
Evening edition: today's stories (Eastern), top 8.
Every edition is saved to archive/YYYY-MM-DD-<edition>.json and listed in archive/index.json,
then tools/pages.py rebuilds the permanent web pages in editions/ and sitemap.xml.
"""
import json, os, sys, datetime
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


FRESH = datetime.timedelta(hours=12)  # "new" = happened or was added in the last 12 hours
FRESH_SLOTS, TOP_N = 4, 10


def seen(it):
    """Latest of when it happened and when it was added, so overnight additions count as new."""
    ts = [x for x in (t(it),) if x]
    try: ts.append(datetime.datetime.fromisoformat(it["added_at"]).astimezone(ET))
    except Exception: pass
    return max(ts) if ts else None
def fresh(it, now): return seen(it) is not None and now - seen(it) <= FRESH
def fresh_ok(it): return lv(it) >= (2 if sec(it) in ("news", "money", "finance", "tech") else 3)


def select(items, edition, now):
    if edition == "morning":
        # Same rule as the Today tab: the 10 most important stories of the last 36 hours, but up to 4
        # spots always go to the most important new stories, so each edition has what's new.
        for hours in (36, 72, 168):
            pool = [i for i in items if t(i) and now - t(i) <= datetime.timedelta(hours=hours) and eligible(i)]
            if len(pool) >= 5: break
        main, pick, ids = rank(pool), [], set()
        def add(i):
            if i["id"] not in ids: ids.add(i["id"]); pick.append(i)
        for i in main[:TOP_N]:
            if fresh(i, now): add(i)
        for i in rank([i for i in items if fresh(i, now) and fresh_ok(i)]):
            if len(pick) >= FRESH_SLOTS: break
            add(i)
        for i in main:
            if len(pick) >= TOP_N: break
            add(i)
        return rank(pick), datetime.timedelta(hours=36)
    today = now.date()
    pool = [i for i in items if t(i) and t(i).date() == today and eligible(i)]
    if len(pool) < 3:
        ids = {i["id"] for i in pool}
        extra = [i for i in items if t(i) and now - t(i) <= datetime.timedelta(hours=24) and lv(i) >= 2 and i["id"] not in ids]
        pool += rank(extra)[: 3 - len(pool)]
    return rank(pool)[:8], now - datetime.datetime.combine(today, datetime.time(0), ET)


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

    top, window = select(items, edition, now)
    listed = {i["id"] for i in top}
    also = []
    for s in ("health", "sports", "tech", "finance"):
        c = rank([i for i in items if sec(i) == s and i["id"] not in listed and t(i) and now - t(i) <= window])
        if c: also.append(c[0])
    nxt = sorted([e for e in upcoming if e.get("date", "") >= date], key=lambda e: e["date"])[:3]

    label = "Morning edition" if edition == "morning" else "Evening edition"
    head = f"{label}, {now.strftime('%A, %b')} {now.day}"
    subject = f"{head}: {shorten(top[0]['text'], max(20, 90 - len(head)))}" if top else head

    lines = ["*The day's most important news. Five minutes. No spin.*" if edition == "morning"
             else "*What happened today. Five minutes. No spin.*", ""]
    for i in top:
        lines += ["### " + i.get("text", ""), ""]
        if i.get("detail"): lines += [i["detail"], ""]
        src = f" [{i.get('source', 'Source')}]({i['url']})" if i.get("url") else ""
        lines += [f"**Impact {lv(i)}/5.** {i.get('why', '')}{src}".strip(), ""]
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
               "also": [{k: i[k] for k in keep if k in i} for i in also],
               "upcoming": nxt},
              open(f"archive/{key}.json", "w"), indent=1, ensure_ascii=False)
    idx_path = "archive/index.json"
    idx = json.load(open(idx_path)) if os.path.exists(idx_path) else {"editions": []}
    idx["editions"] = [e for e in idx["editions"] if e.get("key") != key]
    idx["editions"].append({"key": key, "date": date, "edition": edition, "count": len(top),
                            "lead": top[0]["text"] if top else ""})
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
