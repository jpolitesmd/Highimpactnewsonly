#!/usr/bin/env python3
"""Build an edition of High Impact News Daily from items.json.

Usage (run from the repo root):
  python3 tools/edition.py morning            # writes email/today.json and archives the edition
  python3 tools/edition.py evening
  python3 tools/edition.py evening --archive-only   # archive without writing the email

Morning edition: "Overnight" (top 5 since 5 p.m. Eastern yesterday), then "Yesterday's biggest
stories" (top 5 from yesterday not already listed), plus "This week so far" (3 one-line headlines:
this week's impact 4-5 stories not already in the edition, filled with 3/5 stories; none on Mondays).
Weekends: no Saturday or Sunday morning email and no Saturday evening email. "evening" on a Sunday
builds the Weekend review instead: top 10 stories since the Friday 5 p.m. edition. Monday morning's
recap leaves out stories already in Sunday's Weekend review.
Evening edition (Monday-Friday): top 8 stories that happened since the morning edition (5 a.m. Eastern today);
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
MORNING_SWEEP = datetime.time(5, 30)   # the morning search runs at 5:30 a.m. Eastern: the day block starts here
EVENING_SWEEP = datetime.time(16, 30)  # the evening search runs at 4:30 p.m. Eastern: the overnight block starts here
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
        since = datetime.datetime.combine(yday, EVENING_SWEEP, ET)
        overnight = rank([i for i in items if t(i) and since <= t(i) <= now and fresh_ok(i)])[:5]
        ids = {i["id"] for i in overnight}
        ids |= archived_ids(f"{yday.isoformat()}-weekend")  # Monday: skip what Sunday's review covered
        ylist = [i for i in items if t(i) and t(i).date() == yday and i["id"] not in ids]
        recap = rank([i for i in ylist if eligible(i)])[:5]
        if len(recap) < 3:
            ids2 = {i["id"] for i in recap}
            recap = rank(recap + rank([i for i in ylist if i["id"] not in ids2 and fresh_ok(i)])[:3 - len(recap)])
        if len(overnight) + len(recap) < 3 and now.weekday() != 0:  # very quiet stretch (not Mondays): fall back to the last 72 hours
            ids |= {i["id"] for i in overnight + recap}
            recap += rank([i for i in items if t(i) and now - t(i) <= datetime.timedelta(hours=72)
                           and eligible(i) and i["id"] not in ids])[:5 - len(overnight) - len(recap)]
        groups = []
        if overnight: groups.append(("Overnight", len(overnight)))
        if recap: groups.append(("Yesterday's biggest stories" if overnight else None, len(recap)))
        return overnight + recap, datetime.timedelta(hours=36), groups
    if edition == "weekend":  # Sunday evening: everything since Friday's 5 p.m. edition
        since = datetime.datetime.combine(today - datetime.timedelta(days=2), EVENING_SWEEP, ET)
        top = rank([i for i in items if t(i) and since <= t(i) <= now and fresh_ok(i)])[:10]
        return top, now - since, [(None, len(top))]
    # Evening: only what happened since the morning edition (about 5 a.m. Eastern), nothing from yesterday.
    since = datetime.datetime.combine(today, MORNING_SWEEP, ET)
    morning = archived_ids(f"{today.isoformat()}-morning")
    pool = [i for i in items if t(i) and since <= t(i) <= now and fresh_ok(i) and i["id"] not in morning]
    if len(pool) < 3:  # also allow today's early-morning stories first reported after the morning edition
        ids = {i["id"] for i in pool}
        pool += [i for i in items if i["id"] not in ids and i["id"] not in morning and t(i)
                 and t(i).date() == today and added(i) and added(i) >= since and fresh_ok(i)]
    top = rank(pool)[:8]
    # Quiet evenings: if the ranked pool is still thin, prefer releasing something over nothing.
    # Backfill with lower-bar fresh today's stories not already in this morning's archive
    # (news/money/finance/tech impact ≥2; other sections ≥3 = fresh_ok), still capped at ~8.
    if len(top) < 6:
        ids = {i["id"] for i in top}
        extra = [i for i in items if i["id"] not in ids and i["id"] not in morning and t(i)
                 and t(i).date() == today and fresh_ok(i)]
        top = rank(top + extra)[:8]
    return top, now - since, [(None, len(top))]


def week_so_far(items, now, exclude):
    """Morning only: up to 3 of this week's biggest stories (since Monday, Eastern) not in the edition.
    Impact 4-5 first; if fewer than 3, the highest-rated 3/5 stories fill in. Skipped on Mondays."""
    if now.weekday() == 0: return []
    monday = datetime.datetime.combine(now.date() - datetime.timedelta(days=now.weekday()), datetime.time(0), ET)
    pool = [i for i in items if t(i) and monday <= t(i) <= now and i["id"] not in exclude]
    return (rank([i for i in pool if lv(i) >= 4]) + rank([i for i in pool if lv(i) == 3]))[:3]


def shorten(s, n):
    s = " ".join(s.split())
    if len(s) <= n: return s.rstrip(".")
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def main():
    edition = sys.argv[1] if len(sys.argv) > 1 else "morning"
    assert edition in ("morning", "evening", "weekend")
    archive_only = "--archive-only" in sys.argv
    now = datetime.datetime.now(ET)
    # Weekends: one email only, the Sunday evening Weekend review.
    if (edition == "morning" and now.weekday() >= 5) or (edition == "evening" and now.weekday() == 5):
        print(f"No {edition} email on {now.strftime('%A')}s; the Sunday evening Weekend review covers the weekend. "
              "Nothing written.")
        return
    if edition == "evening" and now.weekday() == 6: edition = "weekend"
    date = now.date().isoformat()
    items = json.load(open("items.json"))["items"]
    # upcoming.json buzz/markets flags guide beat+editor prompts (see beat-prompts.md); edition.py only lists Coming up — stories come from items.json after release.
    upcoming = json.load(open("upcoming.json")).get("events", []) if os.path.exists("upcoming.json") else []

    top, window, groups = select(items, edition, now)
    starts = {}  # index of first story in each group -> heading
    n0 = 0
    for g, (heading, count) in enumerate(groups):
        if heading: starts[n0] = (heading, g > 0)
        n0 += count
    listed = {i["id"] for i in top}
    if edition == "morning":  # Monday: don't repeat what Sunday's Weekend review already covered
        listed |= archived_ids(f"{(now.date() - datetime.timedelta(days=1)).isoformat()}-weekend")
    also = []
    for s in ("health", "sports", "tech", "finance"):
        c = rank([i for i in items if sec(i) == s and i["id"] not in listed and t(i) and now - t(i) <= window])
        if c: also.append(c[0])
    week = week_so_far(items, now, listed | {i["id"] for i in also}) if edition == "morning" else []
    nxt = sorted([e for e in upcoming if e.get("date", "") >= date], key=lambda e: e["date"])
    nxt = ([e for e in nxt if e["date"] <= (now.date() + datetime.timedelta(days=7)).isoformat()][:5] or nxt[:3]) \
        if edition == "weekend" else nxt[:3]  # Weekend review: the week ahead

    label = {"morning": "Morning edition", "evening": "Evening edition", "weekend": "Weekend review"}[edition]
    head = f"{label}, {now.strftime('%A, %b')} {now.day}"
    lead = rank(top)[0]["text"] if top else ""  # subject and archive lead: the most important story
    subject = f"{now.strftime('%A, %b')} {now.day} - {label}"  # e.g. "Tuesday, Sep 29 - Evening edition"

    import emailstyle as es
    key = f"{date}-{edition}"
    ed_url = f"{SITE}/editions/{key}/"
    lines = [es.open_paper(),
             es.kicker(f"{label} · {now.strftime('%A, %B')} {now.day}"),
             es.tagline("What happened overnight, and yesterday's biggest stories. Five minutes. No spin."
                        if edition == "morning" else "The weekend's most important news. Five minutes. No spin."
                        if edition == "weekend" else "What happened since this morning. Five minutes. No spin.")]
    for n, i in enumerate(top):
        first = n == 0
        if n in starts:
            heading, rule = starts[n]
            lines.append(es.section(heading, rule=rule))
            first = True
        lines.append(es.story(i, lv(i), first=first))
    if week:
        lines += [es.section("This week so far"), es.bullets([(None, i.get("text", ""), i.get("url")) for i in week])]
    if also:
        lines += [es.section("Also this weekend" if edition == "weekend" else "Also today"),
                  es.bullets([(SEC_LABEL[sec(i)], i.get("text", ""), i.get("url")) for i in also])]
    if nxt:
        rows = []
        for ev in nxt:
            d = datetime.date.fromisoformat(ev["date"])
            rows.append((ev.get("when") or f"{d.strftime('%b')} {d.day}", ev["text"]))
        lines += [es.section("The week ahead" if edition == "weekend" else "Coming up"), es.dated(rows)]
    lines += [es.signoff("That's the news. Put the phone down and enjoy your day." if edition == "morning"
                         else "That's the weekend. Put the phone down and enjoy your Sunday evening." if edition == "weekend"
                         else "That's the day. Put the phone down and enjoy your evening."),
              es.share_box(ed_url),
              es.footer(f'{es.link("Read it on the web", ed_url)} · {es.link("Past editions", SITE + "/editions/")} · '
                        '<a class="hd-accent" href="{{ manage_subscription_url }}" style="color:' + es.ACCENT + ';text-decoration:none;'
                        'font-weight:600">Choose which emails you get</a>',
                        "You get every weekday morning and evening edition, plus a Sunday weekend review. "
                        "Summaries are written with the help of AI and can contain errors; every story links to its source. "
                        "Not investment or medical advice."),
              es.close_paper()]
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
               "week": [{k: i[k] for k in keep if k in i} for i in week],
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
