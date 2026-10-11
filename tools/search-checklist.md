# Search checklist

Edition research orchestration: see research-runbook.md

Extra checks every news task (morning, evening) runs on top of its own instructions.
The coverage audit (audit/log.json) adds a line here whenever it finds an important story we missed,
naming the source or search that would have caught it. Keep it to 20 lines or fewer; merge similar lines.

## All tasks
- Senate votes: the senate.gov floor_activity page can lag by days. Also open https://www.dailypress.senate.gov/ (today's and yesterday's pages; evening votes after 5 p.m. are easy to miss next morning). [seed, 2026-09-29]
- Daily roundup: https://www.justsecurity.org/ "Early Edition" lists the day's government, court, war and foreign-policy actions in one page; use it as a cross-check. [seed, 2026-09-29]
- Sites that block fetching: washingtonpost.com (403), nbcnews.com (robots). Don't spend lookups on them; search for another outlet's version instead. [seed, 2026-09-29]
- Upcoming money calendar: check upcoming.json for same-day buzz:true or markets-tagged official releases (jobs, CPI, PPI, GDP/PCE, FOMC minutes/decision); once BLS/Fed/wire numbers are out, write the money story — do not invent outcomes before the event. [seed, 2026-10-01]
- Crypto / SEC: prefer section:"finance" (Money → Crypto subtab) with crypto tags for SEC crypto rules and major crypto market-structure stories; ISO20022 items still use finance. Check SEC.gov crypto/digital-asset releases same day. [seed, 2026-10-02]
- Pneumonic plague Ongoing (thread `pneumonic-plague`): later editions should update when a new confirmed case count, death, or official action lands (CDC/WHO/health-dept or major wire only; do not invent). [seed, 2026-10-04]
- Federal district courts: search Reuters legal / The Hill court-battles / Democracy Docket for "judge blocks" OR "vacated" + today's date, including Friday-evening rulings for the Saturday editions; nationwide halts of Trump policies (immigration fines, election/voter-data programs) are Government impact 3. Missed 2026-10-05: Boston judge stayed DHS migrant fines. Missed 2026-10-09: Judge Sooknanan vacated DOJ's nationwide voter-roll collection policy. [audit 2026-10-10]

## Morning task
- Policies taking effect today: search "takes effect [today's date]" and "effective [today's date]" (tariffs, import bans, rules). Missed 2026-09-29: U.S. ban on Canadian alcohol, whey and motorcycles took effect 12:01 a.m. [seed, 2026-09-29]
- Final rules and executive actions: check https://www.federalregister.gov/public-inspection/current for final rules published today; also search "final rule [today's date]" plus agency news pages (transportation.gov, epa.gov). Missed 2026-09-29: Title IX rule; CAFE fuel-economy rule. [seed, 2026-09-29]
- Overnight foreign election results: check upcoming.json and search "[country/province] election results" for votes that closed after the evening edition (Canada, Europe, Latin America); a change of government is World impact 3-4 for the next morning. Missed 2026-10-05: Parti Québécois won a Quebec minority government (59 of 127 seats), CAQ wiped out. [audit 2026-10-05]
- European far-right institutional firsts: after AfD/peer election wins, check same-day or next-morning Landtag speaker / premier votes (Just Security Early Edition often flags). Missed 2026-10-06→07 morning: AfD’s Tobias Rausch elected Saxony-Anhalt Landtag president (first for the party / first far-right state legislature head since 1945). [audit 2026-10-07]

## Evening task
- Supreme Court: open https://www.supremecourt.gov/orders/ordersofthecourt/ each window — emergency mid-afternoon orders AND that day's miscellaneous-order PDFs on non-Monday days (cert grants can land midweek). Orders/decisions count as impact 4. Missed 2026-09-29: third-country deportation stay; missed 2026-10-01: cert in Rhoney (mandatory ICE detention). [audit 2026-10-01]
- Treasury/OFAC: when Iran wartime pressure is active, check home.treasury.gov press releases and ofac.treasury.gov/recent-actions same day; sectoral determinations + SDN dumps are evening Government copy even if abroad. Missed 2026-10-01: Iran auto + rail sectoral sanctions (Operation Economic Outcast). [audit 2026-10-01]
- Sports: on Sundays and weekends search "[event] final day results" (Presidents Cup, Ryder Cup, majors, team championships) and open espn.com/golf or the event's Yahoo Sports wrap; team championships decided in the afternoon count as impact 4. Missed 2026-09-27: U.S. won Presidents Cup 17-13. [audit 2026-09-27]
- Gulf/Hormuz wartime: before evening lock, open UKMTO latest warnings for same-afternoon tanker hits with casualties (not only overnight UKMTO). Missed 2026-10-07 evening: Acers struck ~51NM north of Qatar at 1900 UTC / 3:00 p.m. ET. [audit 2026-10-07]
