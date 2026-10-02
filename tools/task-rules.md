# Task rules

Rules every news task (morning, evening) follows in addition to its own instructions.
Edit by hand only; the coverage audit does not change this file.

## Ongoing stories (threads.json, "thread" field on items)
- threads.json holds {"updated", "threads": [{"id", "title", "summary", "status"}]}. The site's Ongoing tab shows each active thread with all its stories, and story cards link to it.
- When you add a story that continues one of the active threads, set the story's "thread" to that thread's id. Also tag closely related existing stories from the last two weeks if they are untagged.
- Morning task only: create a new thread when a story has at least two items and is likely to keep developing for days (a war, a court case moving up, a funding deadline, a trade dispute, an election). id = short lowercase-hyphen slug; title = plain name (no adjectives); summary = one plain sentence on what the story is. Set "status" to "closed" when a thread has had no new story for 14 days. Keep at most 12 active threads. Set "updated" to today.

## Bundling related stories (all runs)
- If 2+ items in the same edition are the same kind of action on the same day (e.g. two Senate bills that failed to advance, two related court rulings, two parts of one agency action), **combine them into one story** instead of separate cards. That frees an edition slot for something else. Do not bundle unrelated topics; same actor + same kind of outcome the same day is the test.
- **Similar impact (within ~1 point):** lead can name both; detail covers each briefly; rate the bundle at the higher of the two (or their shared level).
- **Uneven impact (e.g. a 4 and a 2):** make the higher-impact item the brunt of the lead and detail; add **one short sentence** on the smaller item (often at the end of detail). Rate the story for the main item; do not inflate impact because of the aside.

## Writing and sourcing (all runs)
- Lead ("text"): one fact, at most about 25 words. Put the named thing first (the bill, the rule, the mission), then what happened to it — so a reader knows the subject before the verb. Prefer plain language a 10th grader gets without sounding dumbed down: say a bill "failed in the Senate" or "did not get enough votes to advance," not "failed to invoke cloture." Put vote tallies, procedural terms, dissents, effective dates and background in "detail," not the lead.
- Source ("url"/"source"): when the primary document is available, cite it first: the court's order or opinion (supremecourt.gov), the Federal Register or agency release for rules, congress.gov or the Senate/House roll call for votes, whitehouse.gov for executive actions, the agency or journal for health and data releases. Otherwise use a wire service (AP, Reuters) or a major national outlet. Use trade press only for context, never as the main source for a national rule or ruling. Do not spend extra lookups only to swap a source: use the primary document when your searches reach it.

## Impact ratings (all runs)
- 4 and 5 are for actions that are binding, take effect now or on a set date, and reach a large population (a final nationwide rule, a law signed, a final Supreme Court merits decision, a Fed rate change, a major war development).
- Use 3 when the action is real but temporary, stayed, delayed, only procedural, passed one chamber, or mostly formalizes an earlier court loss. Court orders that pause or allow something while a case continues are 3 unless they immediately change rights or obligations for millions of people.
- Thin days: confirmed impact ~2–3 stories that pass the workplace-gossip test (would coworkers discuss this?) are a valid fill — primary/wire facts only, no invention.
- Same story in a later edition: only if something new happened, and the lead says what moved.




## Health tab (general audience, not specialty-only)
- Health is for a broad reader (and clinicians of any field), not a pulmonary/critical-care journal club.
- Prefer: major FDA approvals or safety actions; CDC/outbreak/vaccine news; Medicare/Medicaid/HHS payment or coverage rules; large or practice-changing trials and guidelines that affect many patients.
- Skip or deprioritize: narrow specialty Phase 2/3 updates, single-center studies, and disease-niche results unless they are widely covered and clearly change care for a large population.
- Set "health_beat" on section:"health" items: policy | drugs | public | research.
  - policy: CMS/HHS/insurance/hospital payment and coverage.
  - drugs: FDA approvals, labeling, recalls, major device actions.
  - public: CDC, outbreaks, vaccines, population health.
  - research: landmark trials/guidelines with broad impact.
- Still not medical advice; facts only.


## World tab regions (world_region on region:"World" news items)
- World subtabs: europe | mideast | asia | americas | africa (plus All).
- europe: Europe/EU including Ukraine–Russia fighting in Europe.
- mideast: Middle East and North Africa.
- asia: Asia and the Pacific (including China trade when the story is bilateral/abroad-centered).
- americas: Canada, Latin America, Caribbean.
- africa: Sub-Saharan Africa.
- Set world_region when you tag a story World. U.S.-doer foreign policy stays region U.S. (no world_region).

## Region tagging (U.S. vs World)
- **World** = the story’s center of gravity is outside the United States: another country’s government or courts, a foreign election, fighting or disasters abroad, or a multinational event that is not primarily a U.S. agency action.
- **U.S.** = the main actor is the U.S. president, Congress, courts, or federal agencies — including foreign-policy tools (sanctions, State Department orders, defense-trade rules, aid decisions, U.S. troop movements ordered from Washington). Those belong on Government (and Today), not World.
- If both apply, prefer the primary *doer*. Example: Russian strikes on Kyiv → World. A U.S. Treasury Iran sanctions package → U.S. A ceasefire signed in Tehran or a foreign election result → World.
- Do not use region World just because a U.S. story mentions a foreign country.

## Money tab beats (money_beat on section:"money" items)
- Money tab subtabs filter on "money_beat": jobs | prices | rates | markets | taxes. Crypto stories (UI label **Crypto**) stay section:"finance" (no money_beat). The filter value remains `finance` so existing items keep working.
- Crypto (`section: finance`) covers ISO 20022 / “ISO 20022 coin” market news **and** crypto markets / SEC crypto regulation / major crypto market-structure actions. Prefer this tab (with tags like `crypto`) for SEC crypto rules and big crypto structure stories; ISO20022 items still go here.
- jobs: payrolls, unemployment, wages, hiring/layoffs, labor rules.
- prices: CPI/PCE, inflation, rent, household energy/food costs, tariffs that hit consumers.
- rates: Fed, interest rates, mortgages, yields, credit rules.
- markets: major index/commodity moves and market-structure news (facts only, not tips). Do not put SEC crypto rules here when they belong in Crypto (`section: finance`).
- taxes: IRS, tax law changes, and major benefits programs that move money (e.g. new savings accounts).
- Set money_beat when you add a money story. The site can guess from the lead if it’s missing, but an explicit beat is better.

## Corrections log (corrections.json; shown on the site's Corrections tab)
- Whenever you change a published story because it was factually wrong, or because later reporting contradicts or materially changes it (a number revised, a ruling reversed, a claim retracted), update the story and append to "corrections": {"date": now ISO, "item_id", "was": what the story said, "now": what we know now, "why": one short line (e.g. "Official count revised by the ministry" or "We misstated the vote")}; set "updated". Do not log routine new developments that the story never got wrong; those are new stories.
- Weekly check (Sunday evening run only): one search for corrections, retractions or revisions to the past week's biggest stories (for example "correction OR retraction OR revised [the week's 3-4 biggest story topics]"). Compare with items.json and log anything that changes a story we published.
