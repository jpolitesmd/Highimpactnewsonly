# Task rules

Rules every news task (morning, evening, hourly) follows in addition to its own instructions.
Edit by hand only; the coverage audit does not change this file.

## Ongoing stories (threads.json, "thread" field on items)
- threads.json holds {"updated", "threads": [{"id", "title", "summary", "status"}]}. The site's Ongoing tab shows each active thread with all its stories, and story cards link to it.
- When you add a story that continues one of the active threads, set the story's "thread" to that thread's id. Also tag closely related existing stories from the last two weeks if they are untagged.
- Morning task only: create a new thread when a story has at least two items and is likely to keep developing for days (a war, a court case moving up, a funding deadline, a trade dispute, an election). id = short lowercase-hyphen slug; title = plain name (no adjectives); summary = one plain sentence on what the story is. Set "status" to "closed" when a thread has had no new story for 14 days. Keep at most 12 active threads. Set "updated" to today.

## Corrections log (corrections.json)
- When you change a published story because it was factually wrong (a wrong number, name, date, vote tally, outcome or source), append {"date": now ISO, "item_id", "was": the wrong statement, "now": the corrected statement, "why": one short line on how it was found} to "corrections" and set "updated". The site lists these on its Corrections page.
- Do not log new developments, added detail, reworded text or a changed impact rating; only factual errors.

## Elections (elections.json) — morning task only
- While "active" is true, the site shows an Elections tab: what is on the ballot, party control, races to watch, key dates, election news (stories with thread "midterms-2026") and results.
- Each morning use 1-2 lookups for election news from the last day (court rulings on voting rules or maps, candidate changes, official actions, major polling-place or ballot issues) and add stories with thread "midterms-2026". Only facts; never characterize candidates or parties.
- Keep "dates" current with confirmed dates only. "watch" lists only races that nonpartisan forecasters rate as competitive; update it if their lists change.
- After Election Day (Nov. 3, 2026), fill "results" with races called by the Associated Press, as {"race": "Senate · Pennsylvania", "text": "Name (Party) won, X% to Y% (AP)."}; start with control of the Senate and House, then the watched races. Add a new result only when it is called.
- About a week after the new Congress is sworn in (Jan. 3, 2027), set "active" to false.
