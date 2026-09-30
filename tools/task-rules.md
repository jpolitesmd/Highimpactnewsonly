# Task rules

Rules every news task (morning, evening, hourly) follows in addition to its own instructions.
Edit by hand only; the coverage audit does not change this file.

## Ongoing stories (threads.json, "thread" field on items)
- threads.json holds {"updated", "threads": [{"id", "title", "summary", "status"}]}. The site's Ongoing tab shows each active thread with all its stories, and story cards link to it.
- When you add a story that continues one of the active threads, set the story's "thread" to that thread's id. Also tag closely related existing stories from the last two weeks if they are untagged.
- Morning task only: create a new thread when a story has at least two items and is likely to keep developing for days (a war, a court case moving up, a funding deadline, a trade dispute, an election). id = short lowercase-hyphen slug; title = plain name (no adjectives); summary = one plain sentence on what the story is. Set "status" to "closed" when a thread has had no new story for 14 days. Keep at most 12 active threads. Set "updated" to today.
