#!/usr/bin/env python3
"""Build the static, search-engine-readable pages for every archived edition.

Run from the repo root (tools/edition.py calls this automatically after each edition):
  python3 tools/pages.py

Reads archive/index.json and archive/<key>.json, and writes:
  editions/<key>/index.html   one permanent page per edition (hinewsdaily.com/editions/<key>/)
  editions/index.html         the list of every edition
  media-kit.html              sponsor media kit (noindex, unlinked until launch)
  sitemap.xml, robots.txt     so search engines find them
These files are generated: edit this script, not the output. archive/ is never touched.
"""
import json, os, datetime, html
from urllib.parse import quote

SITE = "https://hinewsdaily.com"
NAME = "High Impact News Daily"
SEC_LABEL = {"money": "Money", "finance": "Crypto", "tech": "Tech & Space", "health": "Health", "sports": "Sports"}
e = lambda s: html.escape(str(s or ""), quote=True)


def long_date(d): d = datetime.date.fromisoformat(d); return f"{d.strftime('%A, %B')} {d.day}, {d.year}"
def short_date(d): d = datetime.date.fromisoformat(d); return f"{d.strftime('%a, %b')} {d.day}"
def lv(it):
    try: return max(1, min(5, int(it.get("impact", 1))))
    except Exception: return 1
def label(it):
    if it.get("court"): return it["court"]
    return SEC_LABEL.get(it.get("section")) or ("World" if it.get("region") == "World" else "U.S.")


def pips(n):
    hs = [4, 7, 10, 13, 17]
    return (f'<span class="pips" role="img" aria-label="Impact {n} of 5">'
            + "".join(f'<i style="height:{h}px"{" class=on" if i < n else ""}></i>' for i, h in enumerate(hs))
            + "</span>")


def story(it):
    n = lv(it)
    src = ""
    if str(it.get("url", "")).startswith("https://"):
        src = f'<a href="{e(it["url"])}" rel="noopener" target="_blank">{e(it.get("source") or "Source")} ↗</a>'
    elif it.get("source"):
        src = f"<span>{e(it['source'])}</span>"
    return (f'<li class="item" id="{e(it.get("id",""))}"><div class="meta">{pips(n)}<span>Impact {n}</span></div>'
            f'<p class="hl">{e(it.get("text"))}</p>'
            + (f'<p class="more">{e(it["detail"])}</p>' if it.get("detail") else "")
            + (f'<p class="why"><b>Why impact {n}:</b> {e(it["why"])}</p>' if it.get("why") else "")
            + f'<div class="src"><span>{e(label(it))}</span>{src}</div></li>')


CSS = """*,*::before,*::after{box-sizing:border-box}
:root{--bg:#faf7f1;--surface:#fff;--fg:#1d1a16;--muted:#6b6358;--faint:#e8e1d4;--rule:#d9d0bf;--accent:#8b2a1d;--bar:#c2571c;
--serif:"Source Serif 4",Georgia,serif;--sans:"Hanken Grotesk",system-ui,-apple-system,"Segoe UI",sans-serif;--reader-scale:1;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]):not([data-theme="sepia"]){--bg:#000000;--surface:#1c1c1e;--fg:#efe9dd;--muted:#a59b8a;--faint:#2c2c2e;--rule:#38383a;--accent:#e08a6f;--bar:#e07b45;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#000000;--surface:#1c1c1e;--fg:#efe9dd;--muted:#a59b8a;--faint:#2c2c2e;--rule:#38383a;--accent:#e08a6f;--bar:#e07b45;color-scheme:dark}
:root[data-theme="sepia"]{--bg:#f4ecd8;--surface:#fbf5e6;--fg:#3b2f22;--muted:#75644f;--faint:#e6dcc3;--rule:#d6c7a4}
html{background:var(--bg)}body{margin:0;background:var(--bg);color:var(--fg);font:400 calc(18px * var(--reader-scale))/1.5 var(--serif)}
:root[data-text-size="small"]{--reader-scale:.9}:root[data-text-size="large"]{--reader-scale:1.12}
.wrap{max-width:720px;margin:0 auto;padding:24px 20px 64px}
a{color:var(--accent)}
.folio{margin-bottom:14px}.folio .r1{height:3px;background:var(--fg)}.folio .r2{height:1px;background:var(--fg);margin-top:3px}.folio .r3{height:1px;background:var(--fg)}
.folio-line{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center;padding:7px 2px;font:600 10.5px var(--sans);letter-spacing:.16em;text-transform:uppercase}
.folio-line>span:last-child{text-align:right}.folio-line .fc{font:italic 400 15px "IM Fell English",Georgia,serif;letter-spacing:.02em;text-transform:none;color:var(--accent)}
@media (max-width:480px){.folio-line{font-size:8.5px;letter-spacing:.1em;gap:6px}.folio-line .fc{font-size:12.5px}}
.logo{display:block;text-align:center;text-decoration:none;color:var(--fg);font-size:clamp(22px,6.4vw,40px);line-height:1.1;white-space:nowrap;margin:8px 0 0}
.logo .lp{font-family:"IM Fell English",Georgia,serif;letter-spacing:.04em}.logo .ls{font-family:"Pinyon Script",cursive;font-size:1.22em;color:var(--accent);margin:0 .12em}
.tagline{margin:10px 0 0;text-align:center;font:500 12px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.nav-top{display:flex;justify-content:center;gap:18px;margin-top:10px;font:500 14px var(--sans)}.nav-top a{text-decoration:none}
h1{margin:36px 0 2px;font:600 13px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.count{margin:0;font:400 14px var(--sans);color:var(--muted)}
h2.sec{margin:40px 0 0;font:600 13px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
ol{list-style:none;margin:0;padding:0}
.item{padding:26px 0;border-bottom:3px double var(--rule)}.item:last-child{border-bottom:0}
.meta{display:flex;align-items:center;gap:8px;font:500 13px var(--sans);color:var(--muted);margin-bottom:8px}
.pips{display:flex;align-items:flex-end;gap:2px;height:17px}.pips i{width:4px;border-radius:1px;background:var(--faint)}.pips i.on{background:var(--bar)}
.hl{margin:0;font-size:calc(20px * var(--reader-scale));line-height:1.35;font-weight:500;text-wrap:pretty}
.hl::first-letter{float:left;font:400 2.9em/.82 "IM Fell English",Georgia,serif;color:var(--accent);padding:.06em .08em 0 0;margin-right:.14em}
.more{margin:12px 0 0;padding-top:12px;border-top:1px solid var(--rule);font-size:calc(17px * var(--reader-scale));line-height:1.55;opacity:.88}
.why{margin:8px 0 0;font:400 14px/1.5 var(--sans);color:var(--muted)}.why b{color:var(--fg);font-weight:600}
.src{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;font:500 13px var(--sans);color:var(--muted)}.src a{text-decoration:none}
.up{list-style:none;margin:8px 0 0;padding:0}.up li{display:grid;grid-template-columns:96px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--faint);font:400 15px/1.45 var(--sans)}.up b{color:var(--accent);font-weight:600}
.share{margin:22px auto 0;padding-top:20px;max-width:440px;text-align:center;border-top:1px solid var(--faint)}
.signup .share p{margin:0 0 12px;max-width:none;font:600 17px var(--sans);color:var(--fg)}
.share-row{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.share-row a,.share-row button{padding:8px 14px;font:600 14px var(--sans);color:var(--accent);background:var(--bg);border:1px solid var(--rule);border-radius:999px;text-decoration:none;cursor:pointer}
.share-row a:hover,.share-row button:hover{border-color:var(--accent)}
.signup{margin-top:24px;padding:26px 20px;text-align:center;background:var(--surface);border:1px solid var(--faint);border-radius:14px}
.signup h2{margin:0;font:600 22px/1.25 var(--serif)}.signup p{margin:8px auto 0;max-width:32em;font-size:16px;color:var(--muted)}
.su-form{display:flex;gap:8px;max-width:440px;margin:16px auto 0}
.su-form input{flex:1;min-width:0;padding:12px 14px;font:400 16px var(--sans);color:var(--fg);background:var(--bg);border:1px solid var(--rule);border-radius:10px}
.su-form button{padding:12px 20px;font:600 15px var(--sans);color:#fff;background:var(--accent);border:0;border-radius:10px;cursor:pointer}
@media (max-width:480px){.su-form{flex-direction:column}}
.su-prefs{max-width:440px;margin:14px auto 0;padding:0;border:0;text-align:left}
.su-prefs legend{padding:0;margin:0 0 6px;font:600 13px var(--sans);color:var(--fg)}
.su-prefs label{display:flex;gap:10px;align-items:baseline;padding:5px 0;font:400 14.5px/1.4 var(--sans);color:var(--fg);cursor:pointer}
.su-prefs input{accent-color:var(--accent);width:16px;height:16px;flex:none;transform:translateY(2px)}
.su-prefs small{color:var(--muted);font-size:13px}
.su-prefs .su-note{margin:8px 0 0;font:400 13px/1.45 var(--sans);color:var(--muted)}
.su-prefs .su-err{color:var(--accent);font:600 13px var(--sans);margin:4px 0 0}
.pn{display:flex;justify-content:space-between;gap:12px;margin-top:32px;font:500 14px var(--sans)}.pn a{text-decoration:none}
.foot{margin-top:40px;text-align:center;font:500 13px var(--sans);color:var(--muted)}.foot a{color:var(--muted)}
.fine{margin-top:14px;font:400 13px/1.5 var(--sans);color:var(--muted);text-align:center}
.thirty{margin-top:14px;text-align:center;font:500 13px var(--sans);letter-spacing:.3em;color:var(--muted)}
.list{list-style:none;margin:16px 0 0;padding:0}.list li{display:grid;grid-template-columns:110px 1fr;gap:12px;padding:14px 0;border-top:1px solid var(--faint)}
.list .d{font:600 14px var(--sans);color:var(--accent)}.list a.ed{font:600 14px var(--sans);text-decoration:none;margin-right:12px}.list p{margin:6px 0 0;font-size:15px;color:var(--muted)}
@media (max-width:480px){.list li{grid-template-columns:1fr;gap:4px}}
.theme-btn{display:inline-flex;align-items:center;gap:5px;padding:0;margin:10px auto 0;background:none;border:0;font:500 14px var(--sans);color:var(--accent);cursor:pointer}
.theme-row{display:flex;justify-content:center}
.theme-btn:hover .tb-label{text-decoration:underline}
.theme-btn svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;display:none}
.theme-btn .ic-moon{fill:currentColor;stroke:none}
.theme-btn[data-show="light"] .ic-sepia,.theme-btn[data-show="sepia"] .ic-moon,.theme-btn[data-show="dark"] .ic-sun,.theme-btn:not([data-show]) .ic-sepia{display:block}
.theme-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.reading-tools{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:8px}.size-control{display:inline-flex;align-items:center;gap:3px;margin-top:0;font:500 14px var(--sans);color:var(--muted)}.size-control .size-label{margin-right:3px}.size-control button{min-width:25px;padding:2px 5px;border:1px solid var(--rule);border-radius:5px;background:var(--surface);color:var(--muted);font:600 12px var(--sans);cursor:pointer}.size-control button[aria-pressed="true"]{background:var(--fg);border-color:var(--fg);color:var(--bg)}.size-control button:hover{border-color:var(--accent);color:var(--accent)}.size-control button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}"""

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>try{{var t=localStorage.getItem("pw_theme");if(t==="light"||t==="dark"||t==="sepia")document.documentElement.setAttribute("data-theme",t);var s=localStorage.getItem("pw_text_size");if(s==="small"||s==="large")document.documentElement.setAttribute("data-text-size",s);}}catch(e){{}}</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{name}"><meta property="og:type" content="{ogtype}"><meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{site}/assets/og-card.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{name}" href="/feed.xml">
<link rel="icon" href="/assets/icon.svg?v=3" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=3">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Pinyon+Script&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Hanken+Grotesk:wght@400;500;600&display=swap">
{jsonld}<style>{css}</style>
</head><body><div class="wrap">
<header>
<div class="folio"><div class="r1"></div><div class="r2"></div><div class="folio-line"><span>{fl}</span><span class="fc">{fc}</span><span>{fr}</span></div><div class="r3"></div></div>
<a class="logo" href="/" aria-label="{name} home"><span class="lp">HIGH</span><span class="ls">impact</span><span class="lp">NEWS</span><span class="ls">daily</span></a>
<p class="tagline">The day’s most important news · five minutes · no spin</p>
<nav class="nav-top"><a href="/">Today’s edition</a><a href="/editions/">All editions</a><a href="/stories/">Ongoing stories</a><a href="/#about">About</a></nav>
<div class="theme-row reading-tools"><button class="theme-btn" id="themeBtn" type="button" aria-label="Switch to Sepia mode"><svg class="ic-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg><svg class="ic-sepia" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h9a3 3 0 0 1 3 3v13H9a3 3 0 0 0-3 3V4z"/><path d="M6 4a3 3 0 0 0-3 3v13"/><path d="M9 8h6M9 12h6M9 16h4"/></svg><svg class="ic-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.6A8.2 8.2 0 0 1 9.4 4a8.2 8.2 0 1 0 10.6 10.6z"/></svg><span class="tb-label">Sepia</span></button><div class="size-control" role="group" aria-label="Text size"><span class="size-label">Text</span><button type="button" data-reader-size="small" aria-label="Small text" aria-pressed="false">S</button><button type="button" data-reader-size="medium" aria-label="Medium text" aria-pressed="true">M</button><button type="button" data-reader-size="large" aria-label="Large text" aria-pressed="false">L</button></div></div>
</header>
"""

SIGNUP = """<section class="signup" aria-labelledby="suT"><h2 id="suT">Get each edition by email</h2>
<p>A morning edition at 6:00 a.m. and an evening edition at 5:00 p.m. Eastern, every day including Saturday and Sunday, plus rare breaking alerts for 5-out-of-5 events. Pick the ones you want. Read it in five minutes, then get on with your day.</p>
<form class="su-wrap" action="https://buttondown.com/api/emails/embed-subscribe/highimpactnewsdaily" method="post" target="_blank"><div class="su-form">
<label class="sr" for="suE">Email address</label><input id="suE" type="email" name="email" placeholder="you@example.com" autocomplete="email" required>
<input type="hidden" name="embed" value="1"><button type="submit">Subscribe</button></div>
<fieldset class="su-prefs"><legend>Choose your emails</legend>
<label><input type="checkbox" checked data-skip="Skip morning edition"> <span>Morning edition <small>· every day, 6 a.m. ET</small></span></label>
<label><input type="checkbox" checked data-skip="Skip evening edition"> <span>Evening edition <small>· every day, 5 p.m. ET</small></span></label>
<label><input type="checkbox" checked data-skip="Skip breaking alerts"> <span>Breaking alerts <small>· only for 5-out-of-5 events, which are rare</small></span></label>
<p class="su-err" hidden>Pick at least one email.</p>
<p class="su-note">Change these any time with the “Choose which emails you get” link at the bottom of every email.</p>
</fieldset></form><script>/* Email choices: each unticked box adds a Buttondown "Skip ..." tag to the sign-up */
document.querySelectorAll("form.su-wrap").forEach(function(f){{f.addEventListener("submit",function(ev){{
  f.querySelectorAll("input[data-added]").forEach(function(x){{x.remove();}});
  var boxes=f.querySelectorAll("input[data-skip]"), on=0, err=f.querySelector(".su-err");
  boxes.forEach(function(b){{if(b.checked){{on++;return;}} var h=document.createElement("input"); h.type="hidden"; h.name="tag"; h.value=b.getAttribute("data-skip"); h.setAttribute("data-added","1"); f.appendChild(h);}});
  if(boxes.length&&!on){{ev.preventDefault(); if(err)err.hidden=false; return;}} if(err)err.hidden=true;
}});}});</script>
<p style="font-size:13px">Free. Unsubscribe any time. We never sell your email. Then confirm using the email from hello@news.hinewsdaily.com; if you don’t see it, check junk or spam, and add that address to your contacts. <a href="/#privacy">Privacy</a></p>{share}</section>"""

FOOT = """<p class="foot"><a href="/">Today</a> · <a href="/editions/">All editions</a> · <a href="/stories/">Ongoing stories</a> · <a href="/#about">About</a> · <a href="/#terms">Terms</a> · <a href="/#privacy">Privacy</a> · <a href="/#sponsors">Sponsor policy</a> · <a href="mailto:hello@hinewsdaily.com">Contact</a></p>
<p class="fine">Summaries and impact ratings are written with the help of AI and can contain errors. Always check the linked source. Not investment or medical advice.</p>
<div class="thirty" aria-hidden="true">— 30 —</div>
</div>
<script>
(function(){var b=document.getElementById("shareBtn"),c=document.getElementById("copyBtn");
if(b&&navigator.share){b.hidden=false;b.addEventListener("click",function(){navigator.share({title:document.title,url:b.dataset.url}).catch(function(){});});}
if(c)c.addEventListener("click",function(){var u=c.dataset.url;function ok(){c.textContent="Link copied";setTimeout(function(){c.textContent="Copy link"},2000);}
if(navigator.clipboard)navigator.clipboard.writeText(u).then(ok,function(){prompt("Copy this link:",u)});else prompt("Copy this link:",u);});})();
(function(){
  var mq=window.matchMedia?matchMedia("(prefers-color-scheme: dark)"):null;
  var THEMES=["light","sepia","dark"], LABEL={light:"Light",sepia:"Sepia",dark:"Dark"};
  function pref(){try{var t=localStorage.getItem("pw_theme");return THEMES.indexOf(t)>=0?t:"auto";}catch(e){return "auto";}}
  function eff(){var p=pref();return p==="auto"?(mq&&mq.matches?"dark":"light"):p;}
  function next(cur){var i=THEMES.indexOf(cur);return THEMES[((i<0?0:i)+1)%3];}
  function apply(){var p=pref(),e=eff(),r=document.documentElement,b=document.getElementById("themeBtn"),n=next(e);
    if(p==="auto")r.removeAttribute("data-theme");else r.setAttribute("data-theme",p);
    if(b){b.dataset.show=THEMES.indexOf(e)>=0?e:"light";var lab=b.querySelector(".tb-label");if(lab)lab.textContent=LABEL[n];b.setAttribute("aria-label","Switch to "+LABEL[n]+" mode");}}
  function set(t){try{localStorage.setItem("pw_theme",t);}catch(e){} apply();}
  var btn=document.getElementById("themeBtn"); if(btn)btn.addEventListener("click",function(){set(next(eff()));});
  if(mq){var f=function(){if(pref()==="auto")apply();}; mq.addEventListener?mq.addEventListener("change",f):mq.addListener&&mq.addListener(f);}
  apply();
})();
(function(){
  var SIZES=["small","medium","large"];
  function pref(){try{var s=localStorage.getItem("pw_text_size");return SIZES.indexOf(s)>=0?s:"medium";}catch(e){return "medium";}}
  function apply(){var s=pref(),r=document.documentElement; if(s==="medium")r.removeAttribute("data-text-size");else r.setAttribute("data-text-size",s); document.querySelectorAll("[data-reader-size]").forEach(function(b){b.setAttribute("aria-pressed",b.getAttribute("data-reader-size")==s?"true":"false");});}
  function set(s){try{localStorage.setItem("pw_text_size",s);}catch(e){}apply();}
  document.querySelectorAll("[data-reader-size]").forEach(function(b){b.addEventListener("click",function(){set(b.getAttribute("data-reader-size"));});});
  apply();
})();
</script>
</body></html>
"""


def share_block(url, subject, lead):
    body = f"I thought you'd find this useful: the day's most important news in five minutes, no spin.\n\n{lead}\n\n{url}"
    mail = f"mailto:?subject={quote(subject)}&body={quote(body)}"
    return (f'<div class="share" aria-label="Share"><p>Know someone who’d like this?</p><div class="share-row">'
            f'<a href="{e(mail)}">Forward to a friend</a>'
            f'<button type="button" id="copyBtn" data-url="{e(url)}">Copy link</button>'
            f'<button type="button" id="shareBtn" data-url="{e(url)}" hidden>Share…</button></div></div>')


def head(**kw):
    kw.setdefault("jsonld", "")
    kw.setdefault("ogtype", "website")
    return HEAD.format(name=NAME, site=SITE, css=CSS, **kw)


def edition_page(ed, no, prev, nxt):
    key = f"{ed['date']}-{ed['edition']}"
    url = f"{SITE}/editions/{key}/"
    edname = ed["edition"].capitalize() + " Edition"
    ld = long_date(ed["date"])
    items = ed.get("items", [])
    lead = items[0]["text"] if items else ""
    d0 = datetime.date.fromisoformat(ed["date"])
    short_lead = lead if len(lead) <= 75 else lead[:72].rsplit(" ", 1)[0] + "…"
    title = f"{edname}, {d0.strftime('%b')} {d0.day}, {d0.year}: {short_lead}" if lead else f"{edname}, {ld} · {NAME}"
    desc = (lead + " " + " ".join(i["text"] for i in items[1:3])).strip()
    if len(desc) > 300: desc = desc[:297].rsplit(" ", 1)[0] + "…"
    jsonld = ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage", "name": f"{edname}, {ld}",
        "url": url, "datePublished": ed.get("published") or ed["date"], "description": desc,
        "isPartOf": {"@type": "WebSite", "name": NAME, "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": NAME, "url": SITE + "/"}}, ensure_ascii=False).replace("</", "<\\/")
        + "</script>\n")
    words = sum(len((i.get("text", "") + " " + i.get("detail", "") + " " + i.get("why", "")).split()) for i in items)
    mins = max(1, round(words / 220))
    out = [head(title=e(title), desc=e(desc), url=url, ogtitle=e(f"{edname}, {ld}"), ogtype="article", jsonld=jsonld,
                fl=edname, fc=e(ld), fr=f"Vol. I · No. {no}")]
    out.append(f'<main><h1>{edname}</h1><p class="count">{e(ld)} · {len(items)} {"story" if len(items) == 1 else "stories"}'
               f' · {mins}-minute read · as published</p><ol>{"".join(story(i) for i in items)}</ol>')
    if ed.get("also"):
        out.append(f'<h2 class="sec">Also that day</h2><ol>{"".join(story(i) for i in ed["also"])}</ol>')
    if ed.get("upcoming"):
        out.append('<h2 class="sec">Coming up (as of this edition)</h2><ul class="up">'
                   + "".join(f'<li><b>{e(u.get("when") or short_date(u["date"]))}</b><span>{e(u["text"])}</span></li>' for u in ed["upcoming"])
                   + "</ul>")
    out.append("</main>")
    out.append(SIGNUP.format(share=share_block(url, f"{edname}, {ld} · {NAME}", lead)))
    pn = '<nav class="pn" aria-label="Other editions">'
    pn += (f'<a href="/editions/{prev["key"]}/" rel="prev">← {prev["edition"].capitalize()}, {short_date(prev["date"])}</a>' if prev else "<span></span>")
    pn += (f'<a href="/editions/{nxt["key"]}/" rel="next">{nxt["edition"].capitalize()}, {short_date(nxt["date"])} →</a>' if nxt else "")
    out.append(pn + "</nav>")
    out.append(FOOT)
    return "".join(out)


def index_page(eds):
    url = f"{SITE}/editions/"
    desc = "Every edition of High Impact News Daily, exactly as it was published: the day's most important news, ranked by impact, with no spin."
    out = [head(title=f"All editions · {NAME}", desc=e(desc), url=url, ogtitle="All editions",
                fl="The Archive", fc="Every edition", fr=f"{len(eds)} published")]
    out.append(f'<main><h1>All editions</h1><p class="count">Every edition we’ve published, exactly as it went out.</p><ul class="list">')
    by_date = {}
    for x in eds: by_date.setdefault(x["date"], []).append(x)
    for d, lst in by_date.items():
        links = "".join(f'<a class="ed" href="/editions/{x["key"]}/">{x["edition"].capitalize()} · {x["count"]} stories</a>'
                        for x in sorted(lst, key=lambda y: y["edition"] != "morning"))
        lead = (next((x for x in lst if x["edition"] == "morning"), lst[0])).get("lead", "")
        out.append(f'<li><span class="d">{e(short_date(d))}</span><div>{links}<p>{e(lead)}</p></div></li>')
    out.append("</ul></main>")
    out.append(SIGNUP.format(share=share_block(SITE + "/", NAME, "The day's most important news in five minutes. No spin.")))
    out.append(FOOT)
    return "".join(out)


def story_page(t, lst):
    url = f"{SITE}/stories/{t['id']}/"
    lst = sorted(lst, key=lambda i: i.get("time", ""), reverse=True)
    latest = lst[0]
    desc = (t.get("summary", "") + " Latest: " + latest.get("text", "")).strip()
    if len(desc) > 300: desc = desc[:297].rsplit(" ", 1)[0] + "…"
    jsonld = ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage", "name": t["title"], "url": url, "description": desc,
        "dateModified": latest.get("time", "")[:10],
        "isPartOf": {"@type": "WebSite", "name": NAME, "url": SITE + "/"},
        "publisher": {"@type": "NewsMediaOrganization", "name": NAME, "url": SITE + "/"}}, ensure_ascii=False).replace("</", "<\\/")
        + "</script>\n")
    status = "Ongoing story" if t.get("status") != "closed" else "Story (no recent updates)"
    out = [head(title=e(f"{t['title']}: every update, ranked by impact · {NAME}"), desc=e(desc), url=url, ogtitle=e(t["title"]),
                jsonld=jsonld, fl=status, fc=e(f"Updated {short_date(latest.get('time','')[:10])}"), fr=f"{len(lst)} updates")]
    out.append(f'<main><h1 style="text-transform:none;letter-spacing:0;font-size:26px;line-height:1.2;font-family:\'Source Serif 4\',Georgia,serif;font-weight:600;color:inherit">{e(t["title"])}</h1><p class="count">{e(t.get("summary",""))}</p>'
               f'<p class="count">{len(lst)} {"update" if len(lst) == 1 else "updates"} · newest first</p><ol>{"".join(story(i) for i in lst)}</ol></main>')
    out.append(SIGNUP.format(share=share_block(url, f"{t['title']} · {NAME}", latest.get("text", ""))))
    out.append(FOOT)
    return "".join(out)


def stories_index(rows):
    url = f"{SITE}/stories/"
    desc = "Stories that are still unfolding, each with every update in order, rated by impact. Catch up in minutes, without the scroll."
    out = [head(title=f"Ongoing stories · {NAME}", desc=e(desc), url=url, ogtitle="Ongoing stories",
                fl="Ongoing stories", fc="Every update in one place", fr=f"{len(rows)} stories")]
    out.append('<main><h1>Ongoing stories</h1><p class="count">Stories that are still unfolding. Open one to catch up on every update in order.</p><ul class="list">')
    for t, lst in rows:
        latest = max(lst, key=lambda i: i.get("time", ""))
        out.append(f'<li><span class="d">{e(short_date(latest.get("time","")[:10]))}</span><div><a class="ed" href="/stories/{t["id"]}/">{e(t["title"])} · {len(lst)} updates</a><p>{e(latest.get("text",""))}</p></div></li>')
    out.append("</ul></main>")
    out.append(SIGNUP.format(share=share_block(url, f"Ongoing stories · {NAME}", desc)))
    out.append(FOOT)
    return "".join(out)


def media_kit(eds):
    """Sponsor media kit. Not linked or indexed until launch. Real audience numbers go in
    assets/media.json, e.g. {"subscribers": 1240, "open_rate": "58%", "as_of": "2027-01-15"};
    until then the page says they're available on request rather than showing made-up figures."""
    m = {}
    if os.path.exists("assets/media.json"):
        try: m = json.load(open("assets/media.json"))
        except Exception: m = {}
    n = len(eds)
    first = long_date(eds[-1]["date"]) if eds else ""
    avg = round(sum(x.get("count", 0) for x in eds) / n, 1) if n else 0

    def stat(v, k):
        small = ' class="sm"' if not any(c.isdigit() for c in str(v)) else ""
        return f'<div class="st"><b{small}>{e(v)}</b><span>{e(k)}</span></div>'
    stats = [stat(m["subscribers"] if m.get("subscribers") else "On request", "email subscribers"),
             stat(m["open_rate"] if m.get("open_rate") else "On request", "average open rate"),
             stat(f"{n:,}", "editions published"), stat(avg, "stories per edition")]
    asof = f"Audience figures as of {long_date(m['as_of'])}. " if m.get("as_of") else ""
    css = (CSS + ".mk h2{margin:36px 0 10px;font:600 13px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}"
           ".mk p,.mk li{font-size:17px;line-height:1.6}.mk ul{padding-left:1.2em}.mk li{margin-bottom:8px}.mk li::marker{color:var(--accent)}"
           ".stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:14px}"
           ".st{padding:16px;background:var(--surface);border:1px solid var(--faint);border-radius:12px}.st b{display:block;font:600 24px var(--sans)}.st b.sm{font-size:17px;padding:5px 0 3px}"
           ".st span{font:400 14px var(--sans);color:var(--muted)}.lede{font-size:20px!important}"
           ".slot{margin-top:12px;padding:16px 18px;border:1.5px dashed var(--rule);border-radius:12px;font:400 15px/1.5 var(--sans);color:var(--muted)}"
           ".slot b{display:block;margin-bottom:4px;font:600 12px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}")
    out = [HEAD.format(name=NAME, site=SITE, css=css, jsonld='<meta name="robots" content="noindex,nofollow">\n', ogtype="website",
                       title=f"Sponsor with us · {NAME}", desc="Sponsorship information for High Impact News Daily.",
                       url=f"{SITE}/media-kit.html", ogtitle="Sponsor High Impact News Daily",
                       fl="Media Kit", fc="Sponsor with us", fr="Vol. I")]
    out.append(f"""<main class="mk">
<h1>Media kit</h1>
<p class="lede">High Impact News Daily is the day’s most important news in five minutes, ranked by impact, with no spin. Readers open it on the way to work and on the way home, get what matters, and get on with their day.</p>

<h2>Who reads it</h2>
<ul>
<li>Busy professionals who want to stay informed without doomscrolling.</li>
<li>Readers who chose calm over outrage: no commentary, no hot takes, and a source link on every story.</li>
<li>People who read the whole thing. A five-minute edition means the last story, and the sponsor, gets seen.</li>
</ul>

<h2>By the numbers</h2>
<div class="stats">{''.join(stats)}</div>
<p style="font-size:14px;color:var(--muted)">{asof}Published every morning and evening, seven days a week, since {e(first)}. Email at 6:00 a.m. and 5:00 p.m. Eastern every day.</p>

<h2>The sponsorship</h2>
<p>One sponsor per edition, never more. Each sponsorship runs in the email and on that edition’s permanent web page:</p>
<div class="slot"><b>Presented by</b>Your company name under the edition’s heading.</div>
<div class="slot"><b>Sponsor message</b>A short message in your words (up to about 60 words) with one link, in its own clearly labeled space after the day’s stories.</div>
<p>We can run a single edition, a week of mornings or evenings, or a full week of both.</p>

<h2>The rules</h2>
<p>Readers trust us because sponsors can’t touch the news. Every sponsorship is clearly labeled, sponsors don’t see editions in advance, and they have no influence on which stories run or how they’re rated. We don’t accept political advertising, and we never share readers’ personal information. Read the full <a href="/#sponsors">sponsor policy</a>.</p>

<h2>Rates and availability</h2>
<p>Write to <a href="mailto:hello@hinewsdaily.com?subject=Sponsorship">hello@hinewsdaily.com</a> for current rates, open dates and audience figures.</p>
</main>""")
    out.append(FOOT)
    return "".join(out)


def main():
    idx = json.load(open("archive/index.json"))
    eds = [x for x in idx.get("editions", []) if os.path.exists(f"archive/{x['key']}.json")]
    eds.sort(key=lambda x: (x["date"], x["edition"] == "evening"), reverse=True)  # newest first
    order = list(reversed(eds))  # oldest first, for edition numbers
    urls = [(SITE + "/", idx.get("updated", "")[:10]), (SITE + "/editions/", idx.get("updated", "")[:10])]
    for n, x in enumerate(order, 1):
        ed = json.load(open(f"archive/{x['key']}.json"))
        prev = order[n - 2] if n > 1 else None
        nxt = order[n] if n < len(order) else None
        os.makedirs(f"editions/{x['key']}", exist_ok=True)
        open(f"editions/{x['key']}/index.html", "w").write(edition_page(ed, n, prev, nxt))
        urls.append((f"{SITE}/editions/{x['key']}/", x["date"]))
    os.makedirs("editions", exist_ok=True)
    open("editions/index.html", "w").write(index_page(eds))
    # Ongoing-story pages: one permanent, crawlable page per thread (threads.json + items tagged "thread")
    try:
        threads = json.load(open("threads.json")).get("threads", [])
        allitems = json.load(open("items.json")).get("items", [])
    except (OSError, ValueError):
        threads, allitems = [], []
    rows = []
    for t in threads:
        lst = [i for i in allitems if i.get("thread") == t.get("id") and i.get("time")]
        if not lst: continue
        os.makedirs(f"stories/{t['id']}", exist_ok=True)
        open(f"stories/{t['id']}/index.html", "w").write(story_page(t, lst))
        rows.append((t, lst))
        urls.append((f"{SITE}/stories/{t['id']}/", max(i["time"] for i in lst)[:10]))
    rows.sort(key=lambda r: max(i["time"] for i in r[1]), reverse=True)
    os.makedirs("stories", exist_ok=True)
    open("stories/index.html", "w").write(stories_index(rows))
    urls.insert(2, (SITE + "/stories/", rows[0][1] and max(i["time"] for i in rows[0][1])[:10] if rows else ""))
    open("media-kit.html", "w").write(media_kit(eds))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc>" + (f"<lastmod>{m}</lastmod>" if m else "") + "</url>" for u, m in urls]
    open("sitemap.xml", "w").write("\n".join(sm + ["</urlset>", ""]))
    # RSS feed of editions (newest 30)
    from email.utils import format_datetime
    rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>',
           f"<title>{NAME}</title><link>{SITE}/</link><description>The day's most important news, ranked by impact. No spin.</description>",
           f'<language>en-us</language><atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>']
    for x in eds[:30]:
        ed = json.load(open(f"archive/{x['key']}.json")); its = ed.get("items", [])
        pub = ed.get("published") or (x["date"] + ("T06:00:00-04:00" if x["edition"] == "morning" else "T17:00:00-04:00"))
        try: pubd = format_datetime(datetime.datetime.fromisoformat(pub))
        except ValueError: pubd = ""
        body = "".join(f"<p><b>{e(i.get('text',''))}</b> {e(i.get('detail',''))}</p>" for i in its)
        rss.append(f"<item><title>{e(x['edition'].capitalize())} Edition, {e(long_date(x['date']))}</title>"
                   f"<link>{SITE}/editions/{x['key']}/</link><guid>{SITE}/editions/{x['key']}/</guid>"
                   + (f"<pubDate>{pubd}</pubDate>" if pubd else "") + f"<description>{e(body)}</description></item>")
    open("feed.xml", "w").write("\n".join(rss + ["</channel></rss>", ""]))
    # Static snapshot of the latest edition inside index.html, so the home page has real content
    # before (or without) JavaScript and if the live data fails to load
    if eds:
        x = eds[0]; ed = json.load(open(f"archive/{x['key']}.json"))
        snap = [f'<!--SNAPSHOT--><div class="snap"><p class="snap-h">{e(x["edition"].capitalize())} Edition · {e(long_date(x["date"]))}</p><ol>']
        for i in ed.get("items", []):
            src = f' <a href="{e(i["url"])}" rel="noopener">{e(i.get("source") or "Source")} ↗</a>' if str(i.get("url","")).startswith("https://") else ""
            snap.append(f'<li><p class="snap-t">{e(i.get("text",""))}</p><p class="snap-d">{e(i.get("detail",""))}{src}</p></li>')
        snap.append(f'</ol><p class="snap-d"><a href="/editions/{x["key"]}/">Read this edition</a> · <a href="/editions/">All editions</a> · <a href="/stories/">Ongoing stories</a></p></div><!--/SNAPSHOT-->')
        try:
            h = open("index.html").read(); a, b = h.index("<!--SNAPSHOT-->"), h.index("<!--/SNAPSHOT-->") + len("<!--/SNAPSHOT-->")
            open("index.html", "w").write(h[:a] + "".join(snap) + h[b:])
        except (OSError, ValueError):
            pass
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"pages: {len(order)} edition pages, editions/index.html, sitemap.xml")


if __name__ == "__main__":
    main()
