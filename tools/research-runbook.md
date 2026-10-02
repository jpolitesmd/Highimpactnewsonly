# Parallel beat-bot research runbook

Orchestration for every morning, evening, and Sunday weekend edition research run.
Timezone for all clocks: **America/New_York**. Follow `tools/task-rules.md` and `tools/search-checklist.md` for writing, impact, threads, corrections, and seed checks — do not restate those rules here. Dispatch prompts: `tools/beat-prompts.md`.

## Usage caps (minimize agent cost)

Hard limits for every research run. Beats are fill-in-the-blank (low judgment); editor/merge stays high judgment.

1. **≤3 candidates per beat.** Return at most three objects. Prefer the strongest primary-source hits; drop the rest.
2. **Stop after primary-source hit.** Once you have an official/doc/primary URL for a story, do not keep swapping outlets or "one more confirmation."
3. **Cross-check once.** One Just Security Early Edition pass + one wire (AP *or* Reuters). Do not re-search the same topics inside each beat.
4. **Sports stay conditional.** Skip unless championship/final/Sunday wrap (see Sports beat). Empty Sports must not burn lookups.
5. **Coverage audit is separate.** Tue/Thu/Sat audit updates the checklist; do not redo that hunt inside edition research.
6. **No drive-by redesign.** Between editions, do not regenerate static pages or restyle the site unless stories changed or John asked.

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
4. **War-foreign** — Wars, ceasefires, major diplomatic breaks, UN Security Council binding actions, allied/adversary military moves with strategic stakes. Tag **World** when the center of gravity is abroad (foreign governments, fighting on the ground, elections). Tag **U.S.** when Washington is the main doer (sanctions, State/DoD orders, aid, U.S.-initiated diplomacy framed as an administration action).
5. **Markets-trade** — Fed / FOMC, tariffs and trade bans taking effect, major market-moving official actions (not stock tips).
6. **Sports** — **Conditional only**: run when the calendar has a championship final, major team title decided that day, or Sunday/weekend wrap (see search-checklist Sports line). Otherwise **do not dispatch** (or return immediately `skipped: no qualifying event` with zero lookups).

## Beat return contract

Each beat returns a JSON array of **at most 3** objects (may be `[]`). Every object:

```json
{
  "id_slug": "short-lowercase-hyphen-suggestion",
  "text": "one-fact lead, ≤25 words; named subject first; plain language (no cloture jargon)",
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

**One pass only** after beats return (or in parallel if latency allows, then reconcile once — never per-beat):

- Open Just Security **Early Edition** (https://www.justsecurity.org/) for government / court / war / foreign-policy actions in the window.
- Cross against **one** wire (AP *or* Reuters, not both) for the same window.
- Emit the same beat-contract array (≤3) for anything beats missed; flag overlaps with `notes: "cross-check only"` or drop exact duplicates.
- Do not re-open sources already covered by a beat that returned a primary URL.

## Editor merge

One editor pass (not parallel with final write):

1. Dedupe across beats + cross-check (same action = one story; keep best primary URL).
2. Apply **task-rules.md** (including **bundling**: merge 2+ same-day same-kind actions into one story; if impacts are uneven, lead on the higher and give the lower one short sentence) (leads, impact 1–5, primary sources, threads — morning may create threads) and **search-checklist.md** (seed gaps for this edition). Respect usage caps: do not send beats back out for more depth.
3. Drop below-threshold noise; do not invent facts.
4. Merge keepers into `items.json` (and `threads.json` / `corrections.json` when rules require). Set `added_at` to now ET.
5. Refresh `upcoming.json` / launches only when the standing cadence calls for it (every ~4 days on morning), not every run.

## Publish path

After merge:

1. From repo root: `python3 tools/edition.py morning` | `evening` | `weekend` as appropriate.
2. Commit as **High Impact News Daily** `<jpolitesmd@users.noreply.github.com>`.
3. Push to **main** (writes `email/today.json` → GitHub Action → Buttondown).
4. **Do not** create or update `email/breaking.json` unless John explicitly reverses the no-breaking policy.


## Popular upcoming watch (buzz list)

Goal: catch dated events that are loud on social (especially X) days/weeks ahead, even when they are not classic impact-4 national news — so evening/morning can run a short blurb when they land.

**File:** `upcoming.json`. Optional fields on an event: `"buzz": true`, `"tags": [...]` (e.g. `crypto`, `markets`). Same date/`text` shape as calendar items; edition.py already surfaces upcoming in the pack.

**Nightly routine (Hi News Site):** one light pass (~9 p.m. ET). Caps:
1. At most **5** new or updated buzz candidates.
2. Prefer events with a clear date in the next 14 days.
3. Sources (in order, stop early): (a) web search for dated popular votes/launches/meetings already in the news; (b) one pass over existing `upcoming.json` to mark `buzz` when chatter is high; (c) optional X peek only for already-dated watch terms — no open-ended timeline scroll.
4. Do **not** invent stories or impact ratings here. Only maintain the list. Commit/push only when `upcoming.json` changed.
5. No edition email from this routine.

**Edition research:** Markets-trade + editor must read same-day and prior-day `buzz: true` items and official `markets`-tagged BLS/Fed calendar releases (jobs, CPI, PPI, GDP, PCE, FOMC minutes/decision) in `upcoming.json`. Buzz + markets calendar releases must become site money stories in the next edition after they land (morning for 8:30 a.m. data; evening for afternoon FOMC minutes / XRPN listing if morning missed). Write a short money/tech blurb (impact often 2–3) citing primary/SEC/wire when available — do not drop solely because it is not nationwide high-impact, and do not invent numbers before the release.

## Failure modes

| Failure | What to do |
| --- | --- |
| **Empty beat** | Return `[]` with a one-line reason in the beat summary. Editor continues; do not pad with weak stories. |
| **Quiet / thin edition** | When the main rank is thin, prefer 1–2 confirmed keepers that pass John's workplace-gossip test — would coworkers discuss this at the office? (example: I-95 SC crash) — over releasing nothing. Impact ~2–3 news/money/etc. is a valid fill; still absolute confirmed facts / primary or wire only — not tips, advice, rumor, or salacious padding. Do not invent. |
| **Blocked site** | Do not burn lookups on known blockers (e.g. washingtonpost.com 403, nbcnews.com robots — see checklist). Find AP/Reuters/primary-doc version. Note in `notes` if the story is still soft. |
| **Late morning** (>~5:50 a.m. and email at risk) | Shrink to Courts + Congress + Agencies/FR + cross-check only; skip Markets-trade deep dive and Sports unless impact-4+ is obvious. Still run edition.py and push if any keepers exist; if nothing publishable, push nothing for email and report "nothing to send". |
| **Edition.py says no email today** | Stop; do not force Saturday/Sunday morning or Saturday evening. |
| **Push / Actions failure** | Retry pull --rebase once; report blocked send; never invent a manual Buttondown blast unless John asks. |

## Routine wiring

Morning / evening / weekend routines (Hi News Site agent) must open this runbook first, fill `{edition}` and `{since}` from the Cadence table, dispatch `tools/beat-prompts.md`, then follow Editor merge → Publish path. Coverage-audit routines stay on the checklist-only path (Tue/Thu/Sat only); they do not replace edition research and edition research must not redo the audit hunt.

### Suggested schedules (America/New_York via CRON_TZ)

| Routine | Cron | Prompt intent |
| --- | --- | --- |
| Morning edition research | `CRON_TZ=America/New_York 30 5 * * 1-5` | Follow `tools/research-runbook.md` for `morning`. Compute `since` = yesterday 4:30 p.m. ET. Dispatch beat prompts in parallel (Sports conditional), then cross-check, then editor → `python3 tools/edition.py morning` → commit → push main. No `breaking.json`. |
| Evening edition research | `CRON_TZ=America/New_York 30 16 * * 1-5` | Same for `evening`; `since` = today 5:30 a.m. ET. On Friday this is the last weekday evening before the Sunday weekend review. |
| Weekend review research | `CRON_TZ=America/New_York 30 16 * * 0` | Same for `weekend`; `since` = Friday 4:30 p.m. ET. Include Sunday corrections search from task-rules. `edition.py evening` on Sunday remaps to weekend. |

Save prompts as intent (not frozen tool schemas). Work in `/workspace/Highimpactnewsonly`. Committer: High Impact News Daily `<jpolitesmd@users.noreply.github.com>`.

- **Health (general audience):** FDA/CDC/HHS and broad practice-changing research — not specialty pulm/crit trial chasing. Tag health_beat: policy | drugs | public | research.
