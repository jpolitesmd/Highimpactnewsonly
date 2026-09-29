#!/usr/bin/env python3
"""Send pending emails through Buttondown (run by .github/workflows/send-email.yml).

email/today.json     the day's edition (morning, evening or weekend), scheduled for its send_at time.
email/breaking.json  a BREAKING alert for an impact-5 event, sent immediately.
Each email is sent once: its key is recorded in email/sent.txt.

Subscribers choose what they get with Buttondown tags (subscriber-editable in the Portal, and set by the
sign-up form). The tags are opt-outs, so everyone gets everything unless they tick one (SKIP_TAG below).
"""
import json, os, sys, urllib.request, urllib.error, datetime, zoneinfo

SKIP_TAG = {
    "morning": "Skip morning edition",
    "evening": "Skip evening edition",
    "weekend": "Skip Sunday weekend review",
    "breaking": "Skip breaking alerts",
}
ET = zoneinfo.ZoneInfo("America/New_York")
SENT = "email/sent.txt"


def post(key, payload):
    req = urllib.request.Request(
        "https://api.buttondown.com/v1/emails", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Token {key}", "Content-Type": "application/json",
                 "X-Buttondown-Live-Dangerously": "true"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return r.status, r.read()[:300]


def tag_ids(key):
    """Buttondown filters need tag IDs, not names: map each tag name to its ID."""
    req = urllib.request.Request("https://api.buttondown.com/v1/tags?page_size=100",
                                 headers={"Authorization": f"Token {key}"})
    try:
        with urllib.request.urlopen(req) as r:
            return {t.get("name"): t.get("id") for t in json.loads(r.read()).get("results", [])}
    except Exception as err:
        print(f"PROBLEM: could not list Buttondown tags ({err}); emails go to all subscribers.")
        return {}


def audience(kind, ids):
    tid = ids.get(SKIP_TAG[kind])
    if not tid:
        print(f"PROBLEM: Buttondown tag '{SKIP_TAG[kind]}' not found; this email goes to all subscribers.")
        return None
    return {"predicate": "and", "groups": [],
            "filters": [{"field": "subscriber.tags", "operator": "not_contains", "value": tid}]}


def main():
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if not key:
        print("No BUTTONDOWN_API_KEY secret set; skipping."); return 0
    now = datetime.datetime.now(ET)
    today = now.date().isoformat()
    sent = open(SENT).read().split() if os.path.exists(SENT) else []
    failed = 0
    jobs = []
    if os.path.exists("email/today.json"):
        e = json.load(open("email/today.json"))
        edition = e.get("edition", "morning")
        tag = f"{today}-{edition}"
        if e.get("date") != today:
            print(f"email/today.json is dated {e.get('date')}, not {today}; skipping.")
        elif tag in sent or (edition == "morning" and today in sent):
            print(f"{tag} already sent; skipping.")
        else:
            jobs.append((tag, edition, e))
    if os.path.exists("email/breaking.json"):
        b = json.load(open("email/breaking.json"))
        tag = b.get("key", "")
        made = datetime.datetime.fromisoformat(b["created"]) if b.get("created") else None
        if not tag or tag in sent:
            print(f"breaking {tag or '(no key)'} already sent; skipping.")
        elif not made or now - made > datetime.timedelta(hours=3):
            print(f"breaking {tag} is more than 3 hours old; not sending.")
        else:
            jobs.append((tag, "breaking", b))
    ids = tag_ids(key) if jobs else {}
    for tag, kind, e in jobs:
        payload = {"subject": e["subject"], "body": e["body"], "status": "about_to_send"}
        flt = audience(kind, ids)
        if flt: payload["filters"] = flt
        when = datetime.datetime.fromisoformat(e["send_at"]) if e.get("send_at") else None
        if when and when > now + datetime.timedelta(minutes=2):
            payload["status"] = "scheduled"
            payload["publish_date"] = when.astimezone(datetime.timezone.utc).isoformat()
        try:
            try:
                st, body = post(key, payload)
            except urllib.error.HTTPError as err:
                if err.code not in (400, 422) or "filters" not in payload: raise
                # Never let the preference filter stop an email: if Buttondown rejects it, send to everyone.
                print(f"PROBLEM: Buttondown rejected the '{SKIP_TAG[kind]}' filter ({err.read().decode()[:500]}); "
                      "sending to all subscribers instead.")
                payload.pop("filters", None)
                st, body = post(key, payload)
            print("Buttondown:", tag, st, payload["status"], payload.get("publish_date", "now"),
                  "filtered" if "filters" in payload else "unfiltered", body)
            with open(SENT, "a") as f: f.write(tag + "\n")
        except urllib.error.HTTPError as err:
            print("Buttondown error:", tag, err.code, err.read().decode()[:1000]); failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
