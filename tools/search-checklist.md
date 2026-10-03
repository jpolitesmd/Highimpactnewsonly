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

## Morning task
- Policies taking effect today: search "takes effect [today's date]" and "effective [today's date]" (tariffs, import bans, rules). Missed 2026-09-29: U.S. ban on Canadian alcohol, whey and motorcycles took effect 12:01 a.m. [seed, 2026-09-29]
- Final rules and executive actions: check https://www.federalregister.gov/public-inspection/current for final rules published today; also search "final rule [today's date]" plus agency news pages (transportation.gov, epa.gov). Missed 2026-09-29: Title IX rule; CAFE fuel-economy rule. [seed, 2026-09-29]

## Evening task
- Supreme Court: open https://www.supremecourt.gov/orders/ordersofthecourt/ each window — emergency mid-afternoon orders AND that day's miscellaneous-order PDFs on non-Monday days (cert grants can land midweek). Orders/decisions count as impact 4. Missed 2026-09-29: third-country deportation stay; missed 2026-10-01: cert in Rhoney (mandatory ICE detention). [audit 2026-10-01]
- Treasury/OFAC: when Iran wartime pressure is active, check home.treasury.gov press releases and ofac.treasury.gov/recent-actions same day; sectoral determinations + SDN dumps are evening Government copy even if abroad. Missed 2026-10-01: Iran auto + rail sectoral sanctions (Operation Economic Outcast). [audit 2026-10-01]
- Sports: on Sundays and weekends search "[event] final day results" (Presidents Cup, Ryder Cup, majors, team championships) and open espn.com/golf or the event's Yahoo Sports wrap; team championships decided in the afternoon count as impact 4. Missed 2026-09-27: U.S. won Presidents Cup 17-13. [audit 2026-09-27]
- Saturday Oct 3 evening: must include the air ambulance disappearance story if it is still the latest confirmed development; do not drop for impact. If later confirmed updates arrive, consider creating an Ongoing thread once there are two items. [seed, 2026-10-03]
- Sunday Oct 4 evening edition (the normal evening run, not a weekend review): must include the France school-burnings / riots story if still the latest confirmed development; do not drop for impact. [seed, 2026-10-02]
