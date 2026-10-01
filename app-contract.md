# High Impact News Daily — app JSON contract

Read-only contract for clients (iOS app, etc.) mirroring [hinewsdaily.com](https://hinewsdaily.com/).  
**Source of truth:** GitHub `main` on `jpolitesmd/Highimpactnewsonly`.  
Site bot owns the edition pipeline; App consumes published JSON only.

Base URL: `https://hinewsdaily.com`  
Optional cache-bust: `?t=<epoch>` (same pattern as the website).

When you change item fields or deep links, update this file in the same PR/commit.

---

## Public JSON paths

| Path | Shape | Use |
|------|--------|-----|
| `/items.json` | `{ updated, items[] }` | Primary story store |
| `/threads.json` | `{ updated, threads[] }` | Ongoing stories |
| `/history.json` | `{ year, updated, events[] }` | History tab |
| `/corrections.json` | `{ updated, corrections[] }` | Corrections tab |
| `/upcoming.json` | `{ updated, events[] }` | Government “coming up” |
| `/launches.json` | `{ updated, source?, launches[] }` | Tech launches |
| `/archive/index.json` | `{ updated?, editions[] }` | Edition index |
| `/archive/{key}.json` | edition object | Full edition (`key` = `YYYY-MM-DD-morning\|evening\|weekend`) |
| `/email/today.json` | newsletter payload | Optional; not required for UI parity |
| `/assets/commute.json` | art list | Optional commute illustrations |

Prefer JSON over scraping HTML. Shareable HTML for an edition: `/editions/{key}/`.

---

## `items[]` fields

### Required (always present for rendering)

| Field | Type | Notes |
|-------|------|--------|
| `id` | string | Stable slug |
| `text` | string | Lead (one fact) |
| `detail` | string | Context / numbers |
| `why` | string | Why it earned its impact |
| `impact` | number | Integer 1–5 |
| `topic` | string | Icon / art key |
| `region` | string | `"US"` or `"World"` |
| `time` | string | ISO 8601 with offset |
| `time_known` | boolean | |
| `source` | string | Display label |
| `url` | string | `https://…` primary source |
| `added_at` | string | ISO 8601 when added to the store |

### Optional (omit = OK; clients must not break)

| Field | Type | Notes |
|-------|------|--------|
| `section` | string | `news` \| `money` \| `finance` \| `tech` \| `health` \| `sports`. Missing ≈ `news` for Government/World filters |
| `branch` | string **or** string[] | Government subtabs: `executive`, `legislative`, `judicial` |
| `judicial` | boolean | Court story flag |
| `court` | string | e.g. court name for labeling |
| `thread` | string | `threads.json` id → Ongoing |
| `money_beat` | string | Only if `section` = `money`: `jobs` \| `prices` \| `rates` \| `markets` \| `taxes` |
| `health_beat` | string | Only if `section` = `health`: `policy` \| `drugs` \| `public` \| `research` |
| `world_region` | string | Only if `region` = `World` (news): `europe` \| `mideast` \| `asia` \| `americas` \| `africa` |

### Tab filters (match website)

- **Government:** `(section` missing or `news`) and `region` ≠ `World` (+ optional `branch` subtabs)
- **World:** `(section` missing or `news`) and `region` = `World` (+ `world_region` subtabs)
- **Money:** `section` `money` or `finance` (`finance` → ISO20022; `money` → `money_beat`)
- **Tech / Health / Sports:** `section` equals tab name
- **Ongoing:** join `thread` → `threads.json`
- **History / Corrections / Archive:** dedicated files above

**Region rule:** `World` = center of gravity abroad. U.S. foreign-policy tools (sanctions, State/DoD orders, aid, Washington-led moves) stay `region: "US"` (Government), not World.

---

## Other file shapes

### `threads[]`

Required: `id`, `title`, `summary`, `status` (`active` \| `closed`). Hide `closed` in the main Ongoing list.

### `history.events[]`

Required: `date` (`YYYY-MM-DD`), `impact`, `topic`, `text`, `url`.

### `upcoming.events[]`

Required: `date`, `text`. Optional: `when`, `branch`, `detail`, `buzz`, `tags`.

### `launches[]`

Required: `date`, `sort`, `time`, `rocket`, `mission`, `site`.

### `archive/index.json` → `editions[]`

Required: `key`, `date`, `edition` (`morning`\|`evening`\|`weekend`), `count`, `lead`.

### `archive/{key}.json`

Required: `date`, `edition`, `subject`, `published`, `items[]`.  
May also include `groups`, `also`, `week`, `upcoming` (same item-like objects as elsewhere).

### `corrections[]`

When present: factual fix log entries (see `tools/task-rules.md`). Empty array is valid.

---

## Canonical deep links

Mirror these so shares open the right in-app screen.

| URL | Screen |
|-----|--------|
| `https://hinewsdaily.com/` | Today |
| `https://hinewsdaily.com/#subscribe` | Today + email signup |
| `https://hinewsdaily.com/#about` | About |
| `https://hinewsdaily.com/#privacy` | Privacy |
| `https://hinewsdaily.com/#terms` | Terms |
| `https://hinewsdaily.com/#sponsors` | Sponsor policy |
| `https://hinewsdaily.com/#ongoing` | Ongoing list |
| `https://hinewsdaily.com/#ongoing/{threadId}` | One ongoing story |
| `https://hinewsdaily.com/#archive` | Archive list |
| `https://hinewsdaily.com/#archive/{key}` | One edition (in-app archive) |
| `https://hinewsdaily.com/editions/{key}/` | Same edition (preferred share URL) |
| `https://hinewsdaily.com/editions/` | Past editions index |
| `https://hinewsdaily.com/stories/` | Ongoing (HTML); map to `#ongoing` |

Website tab choice without a hash is localStorage-only; for app shares prefer the hashes / `/editions/` paths above.

---

## Compatibility promise

- Additive optional fields are OK without a major version bump; document them here.
- Renames/removals of required fields, or changes to enum values clients filter on, should be noted in this file in the same commit and coordinated with App.
- Clients should treat unknown fields as ignore.
