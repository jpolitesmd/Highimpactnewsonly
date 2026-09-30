# Task rules

Rules every news task (morning, evening) follows in addition to its own instructions.
Edit by hand only; the coverage audit does not change this file.

## Ongoing stories (threads.json, "thread" field on items)
- threads.json holds {"updated", "threads": [{"id", "title", "summary", "status"}]}. The site's Ongoing tab shows each active thread with all its stories, and story cards link to it.
- When you add a story that continues one of the active threads, set the story's "thread" to that thread's id. Also tag closely related existing stories from the last two weeks if they are untagged.
- Morning task only: create a new thread when a story has at least two items and is likely to keep developing for days (a war, a court case moving up, a funding deadline, a trade dispute, an election). id = short lowercase-hyphen slug; title = plain name (no adjectives); summary = one plain sentence on what the story is. Set "status" to "closed" when a thread has had no new story for 14 days. Keep at most 12 active threads. Set "updated" to today.

## Writing and sourcing (all runs)
- Lead ("text"): one fact, at most about 25 words: who did what. Put numbers, vote tallies, dissents, effective dates and background in "detail", not the lead.
- Source ("url"/"source"): when the primary document is available, cite it first: the court's order or opinion (supremecourt.gov), the Federal Register or agency release for rules, congress.gov or the Senate/House roll call for votes, whitehouse.gov for executive actions, the agency or journal for health and data releases. Otherwise use a wire service (AP, Reuters) or a major national outlet. Use trade press only for context, never as the main source for a national rule or ruling. Do not spend extra lookups only to swap a source: use the primary document when your searches reach it.

## Impact ratings (all runs)
- 4 and 5 are for actions that are binding, take effect now or on a set date, and reach a large population (a final nationwide rule, a law signed, a final Supreme Court merits decision, a Fed rate change, a major war development).
- Use 3 when the action is real but temporary, stayed, delayed, only procedural, passed one chamber, or mostly formalizes an earlier court loss. Court orders that pause or allow something while a case continues are 3 unless they immediately change rights or obligations for millions of people.
- Same story in a later edition: only if something new happened, and the lead says what moved.

## Corrections log (corrections.json; shown on the site's Corrections tab)
- Whenever you change a published story because it was factually wrong, or because later reporting contradicts or materially changes it (a number revised, a ruling reversed, a claim retracted), update the story and append to "corrections": {"date": now ISO, "item_id", "was": what the story said, "now": what we know now, "why": one short line (e.g. "Official count revised by the ministry" or "We misstated the vote")}; set "updated". Do not log routine new developments that the story never got wrong; those are new stories.
- Weekly check (Sunday evening run only): one search for corrections, retractions or revisions to the past week's biggest stories (for example "correction OR retraction OR revised [the week's 3-4 biggest story topics]"). Compare with items.json and log anything that changes a story we published.
