# Parallel beat-bot research runbook

Orchestration for every morning, evening, and Sunday weekend edition research run.
Timezone for all clocks: **America/New_York**. Follow `tools/task-rules.md` and `tools/search-checklist.md` for writing, impact, threads, corrections, and seed checks — do not restate those rules here. Dispatch prompts: `tools/beat-prompts.md`.

## Cadence

| Edition | Research start | Email send | Days | "Since" window (beat bots use this) |
| --- | --- | --- | --- | --- |
| Morning | **5:30 a.m.** | 6:00 a.m. | Mon–Fri only | Yesterday **4:30 p.m.** → now (overnight). Also collect candidates for yesterday's biggest (calendar day yesterday) and this-week-so-far (Mon→now, skip Mondays). |
| Evening | **4:30 p.m.** | 5:00 p.m. | Mon–Fri only | Today **5:30 a.m.** → now. Skip anything already in today's morning archive. |
| Weekend review | **4:30 p.m.** Sunday | 5:00 p.m. | Sunday only | Friday **4:30 p.m.** → now (+ week-ahead upcoming). Sunday also runs the weekly corrections search in task-rules. |

No Saturday/Sunday morning. No Saturday evening. On Sunday the evening routine runs as `weekend` (edition.py remaps automatically).

## Parallel beat bots (exact list)

Dispatch these **in parallel** each research run. Each returns zero or more candidate stories in the beat contract below.

1. **Courts** — SCOTUS orders/opinions, federal appellate merits/stays, major state high-court actions that bind many people.
2. **Congress** — House/Senate floor votes, conference deals, signed or vetoed bills; use Daily Press + congress.gov (senate.gov floor_activity can lag).
3. **Agencies/FR** — Federal Register public inspection + agency final rules / EO / effective-today policies.
4. **War-foreign** — Wars, ceasefires, major diplomatic breaks, UN Security Council binding actions, allied/adversary military moves with strategic stakes.
5. **Markets-trade** — Fed / FOMC, tariffs and trade bans taking effect, major market-moving official actions (not stock tips).
6. **Sports** — **Conditional only**: run when the calendar has a championship final, major team title decided that day, or Sunday/weekend wrap (see search-checklist Sports line). Otherwise skip and report `skipped: no qualifying event`.

## Beat return contract

Each beat returns a JSON array (may be `[]`). Every object:

```json
{
  "id_slug": "short-lowercase-hyphen-suggestion",
  "text": "one-fact lead, ≤25 words",
  "detail": "numbers, tallies, dates, background",
  "why": "one short line on why it matters",
  "impact": 3,
  "time": "2026-09-30T15:30:00-04:00",
  "source": "outlet or primary-doc name",
  "url": "https://...",
  "thread": "existing-thread-id-or-omit",
  "section": "news|money|sports|health|tech|finance",
  "notes": "optional: blocked site, weak source, duplicate suspicion"
}
```

- Prefer primary documents in `url`/`source` when found (task-rules).
- `time` is ISO with Eastern offset (`-04:00` / `-05:00`).
- `id_slug` is a suggestion; the editor assigns the final `YYYY-MM-DD-…` id when merging into `items.json`.
- Omit `thread` unless it clearly continues an active id in `threads.json`.

## Cross-check bot

After beats return (or in parallel if latency allows, then reconcile):

- Open Just Security **Early Edition** (https://www.justsecurity.org/) for government / court / war / foreign-policy actions in the window.
- Cross against a wire (AP or Reuters) for the same window.
- Emit the same beat-contract array for anything beats missed; flag overlaps with `notes: "cross-check only"` or drop exact duplicates.

## Editor merge

One editor pass (not parallel with final write):

1. Dedupe across beats + cross-check (same action = one story; keep best primary URL).
2. Apply **task-rules.md** (leads, impact 1–5, primary sources, threads — morning may create threads) and **search-checklist.md** (seed gaps for this edition).
3. Drop below-threshold noise; do not invent facts.
4. Merge keepers into `items.json` (and `threads.json` / `corrections.json` when rules require). Set `added_at` to now ET.
5. Refresh `upcoming.json` / launches only when the standing cadence calls for it (every ~4 days on morning), not every run.

## Publish path

After merge:

1. From repo root: `python3 tools/edition.py morning` | `evening` | `weekend` as appropriate.
2. Commit as **High Impact News Daily** `<jpolitesmd@users.noreply.github.com>`.
3. Push to **main** (writes `email/today.json` → GitHub Action → Buttondown).
4. **Do not** create or update `email/breaking.json` unless John explicitly reverses the no-breaking policy.

## Failure modes

| Failure | What to do |
| --- | --- |
| **Empty beat** | Return `[]` with a one-line reason in the beat summary. Editor continues; do not pad with weak stories. |
| **Blocked site** | Do not burn lookups on known blockers (e.g. washingtonpost.com 403, nbcnews.com robots — see checklist). Find AP/Reuters/primary-doc version. Note in `notes` if the story is still soft. |
| **Late morning** (>~5:50 a.m. and email at risk) | Shrink to Courts + Congress + Agencies/FR + cross-check only; skip Markets-trade deep dive and Sports unless impact-4+ is obvious. Still run edition.py and push if any keepers exist; if nothing publishable, push nothing for email and report "nothing to send". |
| **Edition.py says no email today** | Stop; do not force Saturday/Sunday morning or Saturday evening. |
| **Push / Actions failure** | Retry pull --rebase once; report blocked send; never invent a manual Buttondown blast unless John asks. |

## Routine wiring

Morning / evening / weekend routines (Hi News Site agent) must open this runbook first, fill `{edition}` and `{since}` from the Cadence table, dispatch `tools/beat-prompts.md`, then follow Editor merge → Publish path. Coverage-audit routines stay on the checklist-only path; they do not replace edition research.

### Suggested schedules (America/New_York via CRON_TZ)

| Routine | Cron | Prompt intent |
| --- | --- | --- |
| Morning edition research | `CRON_TZ=America/New_York 30 5 * * 1-5` | Follow `tools/research-runbook.md` for `morning`. Compute `since` = yesterday 4:30 p.m. ET. Dispatch beat prompts in parallel (Sports conditional), then cross-check, then editor → `python3 tools/edition.py morning` → commit → push main. No `breaking.json`. |
| Evening edition research | `CRON_TZ=America/New_York 30 16 * * 1-5` | Same for `evening`; `since` = today 5:30 a.m. ET. On Friday this is the last weekday evening before the Sunday weekend review. |
| Weekend review research | `CRON_TZ=America/New_York 30 16 * * 0` | Same for `weekend`; `since` = Friday 4:30 p.m. ET. Include Sunday corrections search from task-rules. `edition.py evening` on Sunday remaps to weekend. |

Save prompts as intent (not frozen tool schemas). Work in `/workspace/Highimpactnewsonly`. Committer: High Impact News Daily `<jpolitesmd@users.noreply.github.com>`.
