#!/usr/bin/env python3
"""Print the send time of the next email edition that will include an event happening now (ISO, Eastern), e.g. for a BREAKING item's breaking_until.

Editions: Monday-Friday 6:00 a.m. and 5:00 p.m.; Sunday 5:00 p.m. (Weekend review); none on Saturday
or Sunday morning. Usage: python3 tools/next_edition.py [ISO time; default now]
"""
import sys, datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BUILD_LEAD = datetime.timedelta(minutes=30)  # editions are built from searches at 5:30 a.m. (sent 6:00) and 4:30 p.m. (sent 5:00)


def next_edition(now):
    for d in range(0, 8):
        day = now.date() + datetime.timedelta(days=d)
        wd = day.weekday()  # Monday = 0 ... Sunday = 6
        hours = (6, 17) if wd <= 4 else (17,) if wd == 6 else ()
        for h in hours:
            t = datetime.datetime.combine(day, datetime.time(h), ET)
            if t - BUILD_LEAD > now:  # the edition must be built after the event to include it
                return t


if __name__ == "__main__":
    now = datetime.datetime.fromisoformat(sys.argv[1]).astimezone(ET) if len(sys.argv) > 1 else datetime.datetime.now(ET)
    print(next_edition(now).isoformat())
