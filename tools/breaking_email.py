#!/usr/bin/env python3
"""Write email/breaking.json: a BREAKING alert email for one impact-5 item, sent at once by the
send-email workflow when pushed. Only impact 5, and only once per event.

Usage (from the repo root): python3 tools/breaking_email.py <item id>
"""
import json, os, sys, datetime

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
    import emailstyle as es
    when = f"{nxt.strftime('%A')} at {nxt.strftime('%-I %p').replace('AM', 'a.m.').replace('PM', 'p.m.')}"
    lines = [es.open_paper(),
             es.badge("BREAKING · HIGH IMPACT EVENT"),
             es.tagline(f"{now.strftime('%A, %B')} {now.day}, {now.strftime('%-I:%M %p')} ET"),
             es.story(it, 5, first=True, size=23),
             es.note(f"We'll post confirmed updates at {es.link('hinewsdaily.com', SITE + '/')} and cover it in full "
                     f"in the next edition, {es.e(when)} ET."),
             es.footer('<a href="{{ manage_subscription_url }}" style="color:' + es.ACCENT + ';text-decoration:none;'
                       'font-weight:600">Choose which emails you get</a>',
                       "You get a breaking alert only for events we rate 5 out of 5, which is rare."),
             es.close_paper()]
    out = {"key": key, "item": iid, "created": now.isoformat(timespec="seconds"),
           "subject": "BREAKING: " + shorten(it.get("text", ""), 90), "body": "\n".join(lines)}
    os.makedirs("email", exist_ok=True)
    json.dump(out, open("email/breaking.json", "w"), indent=1, ensure_ascii=False)
    print(f"email/breaking.json written for {iid}; subject: {out['subject']}")


if __name__ == "__main__":
    main()
