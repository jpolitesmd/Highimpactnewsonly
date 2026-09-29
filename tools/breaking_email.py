#!/usr/bin/env python3
"""Write email/breaking.json: a BREAKING alert email for one impact-5 item, sent at once by the
send-email workflow when pushed. Only impact 5, and only once per event.

Usage (from the repo root): python3 tools/breaking_email.py <item id>
"""
import html, json, os, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edition import ET, SITE, lv, shorten  # noqa: E402
from next_edition import next_edition  # noqa: E402


def main():
    if len(sys.argv) < 2: sys.exit("usage: breaking_email.py <item id>")
    iid = sys.argv[1]
    items = json.load(open("items.json"))["items"]
    it = next((i for i in items if i.get("id") == iid), None)
    if not it: sys.exit(f"No item with id {iid}")
    if lv(it) < 5: sys.exit(f"{iid} is impact {lv(it)}; breaking emails are for impact 5 only. Nothing written.")
    key = f"breaking-{iid}"
    sent = open("email/sent.txt").read().split() if os.path.exists("email/sent.txt") else []
    if key in sent: sys.exit(f"{key} was already emailed. Nothing written.")
    now = datetime.datetime.now(ET)
    nxt = next_edition(now)
    img = f"{SITE}/assets/email"
    head_css = ("font-family:Georgia,'Times New Roman',Times,serif;font-size:23px;line-height:1.3;"
                "font-weight:bold;color:#1d1a16;margin:20px 0 8px")
    label_css = ("display:inline-block;font-family:Arial,Helvetica,sans-serif;font-size:12px;font-weight:bold;"
                 "letter-spacing:2px;color:#ffffff;background:#b3261e;padding:5px 10px;border-radius:4px")
    src = f" [{it.get('source', 'Source')}]({it['url']})" if it.get("url") else ""
    meter = (f'<img src="{img}/impact-5.png" alt="" width="50" height="16" '
             f'style="width:50px;height:16px;vertical-align:middle;border:0"> ')
    when = f"{nxt.strftime('%A')} at {nxt.strftime('%-I %p').replace('AM', 'a.m.').replace('PM', 'p.m.')}"
    lines = [f'<a href="{SITE}/"><img src="{img}/masthead.png" alt="High Impact News Daily" width="560" '
             f'style="display:block;width:100%;max-width:560px;height:auto;border:0"></a>', "",
             f'<span style="{label_css}">BREAKING · HIGH IMPACT EVENT</span>', "",
             f"*{now.strftime('%A, %B')} {now.day}, {now.strftime('%-I:%M %p')} ET*", "",
             f'<h3 style="{head_css}">{html.escape(it.get("text", ""), quote=False)}</h3>', ""]
    if it.get("detail"): lines += [it["detail"], ""]
    lines += [f"{meter}**Impact 5/5.** {it.get('why', '')}{src}".strip(), "",
              f"We'll post confirmed updates at [hinewsdaily.com]({SITE}/) and cover it in full in the next "
              f"edition, {when} ET.", "",
              "---", "",
              "*You get a breaking alert only for events we rate 5 out of 5, which is rare. "
              "[Choose which emails you get]({{ manage_subscription_url }}).*"]
    out = {"key": key, "item": iid, "created": now.isoformat(timespec="seconds"),
           "subject": "BREAKING: " + shorten(it.get("text", ""), 90), "body": "\n".join(lines)}
    os.makedirs("email", exist_ok=True)
    json.dump(out, open("email/breaking.json", "w"), indent=1, ensure_ascii=False)
    print(f"email/breaking.json written for {iid}; subject: {out['subject']}")


if __name__ == "__main__":
    main()
