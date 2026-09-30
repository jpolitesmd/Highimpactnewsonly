"""Shared look for every email (editions and breaking alerts).

Dark by default (inline styles + bgcolor) so the Buttondown web archive is readable and matches the
site's dark charcoal theme. Mail apps that strip <style> still get light text on a dark wrapper via
inline color/bgcolor. On the web archive, a small progressive-enhancement block adds the same
Appearance controls as the site (Auto / Light / Sepia / Dark), stored in localStorage under
pw_theme so a preference set on hinewsdaily.com carries over. Flourishes are mid-tone PNGs that
read on dark; the wordmark is live text. Fonts: Source Serif 4 where the mail app can load it
(Apple Mail, iOS), falling back to Georgia; labels in the system sans. Each HTML block starts on
its own line so Buttondown passes it through untouched.
"""
import html

SITE = "https://hinewsdaily.com"
IMG = f"{SITE}/assets/email"

# Dark palette (aligned with site data-theme="dark" / --bg #15130f)
PAPER = "#1a1814"   # email wrapper background (charcoal/brown)
INK = "#f5f0e8"     # headlines
BODY = "#d9d2c5"    # story text
MUTED = "#b8b0a4"   # labels, captions
RULE = "#3d3831"    # hairlines
ACCENT = "#e08a6f"  # warm accent links / section labels (site dark accent)
BOX = "#262320"     # share box / inset surface
SERIF = "'Source Serif 4','Source Serif Pro',Georgia,'Times New Roman',Times,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
DISPLAY = "'IM Fell English',Georgia,'Times New Roman',serif"

# Light / sepia tokens (match index.html :root / data-theme="sepia")
LIGHT = dict(paper="#faf7f1", ink="#1d1a16", body="#1d1a16", muted="#6b6358",
             rule="#d9d0bf", accent="#8b2a1d", box="#ffffff")
SEPIA = dict(paper="#f4ecd8", ink="#3b2f22", body="#3b2f22", muted="#75644f",
             rule="#d6c7a4", accent="#8b2a1d", box="#fbf5e6")

e = lambda s: html.escape(str(s or ""), quote=True)


def link(text, url, color=ACCENT, underline=False):
    return (f'<a class="hd-accent" href="{e(url)}" style="color:{color};text-decoration:{"underline" if underline else "none"};'
            f'font-weight:600">{e(text)}</a>')


def _theme_css():
    """CSS variables + class overrides for web-archive theme switching; hidden appearance chrome."""
    L, S = LIGHT, SEPIA
    parts = []
    parts.append('.hd-root{color-scheme:dark;background-color:%s}' % PAPER)
    parts.append('.hd-root[data-theme="light"]{color-scheme:light;background-color:%s}' % L['paper'])
    parts.append('.hd-root[data-theme="sepia"]{color-scheme:light;background-color:%s}' % S['paper'])
    parts.append('.hd-root[data-theme="dark"]{color-scheme:dark;background-color:%s}' % PAPER)
    parts.append('@media(prefers-color-scheme:light){.hd-root[data-theme="auto"]{color-scheme:light;background-color:%s}}' % L['paper'])
    parts.append('@media(prefers-color-scheme:dark){.hd-root[data-theme="auto"]{color-scheme:dark;background-color:%s}}' % PAPER)

    def theme_block(sel, T):
        return (
            f'{sel} .hd-wrap,{sel} .hd-body{{background-color:{T["paper"]}!important;color:{T["body"]}!important}}'
            f'{sel} .hd-ink,{sel} .hd-inkrule{{color:{T["ink"]}!important;'
            f'border-top-color:{T["ink"]}!important;border-bottom-color:{T["ink"]}!important}}'
            f'{sel} .hd-muted{{color:{T["muted"]}!important}}'
            f'{sel} .hd-accent{{color:{T["accent"]}!important}}'
            f'{sel} .hd-rule{{border-color:{T["rule"]}!important;'
            f'border-top-color:{T["rule"]}!important;border-bottom-color:{T["rule"]}!important}}'
            f'{sel} .hd-box{{background:{T["box"]}!important;background-color:{T["box"]}!important;'
            f'border-color:{T["rule"]}!important;color:{T["body"]}!important}}'
        )

    parts.append(theme_block('.hd-root[data-theme="light"]', L))
    parts.append(theme_block('.hd-root[data-theme="sepia"]', S))
    parts.append('@media(prefers-color-scheme:light){' + theme_block('.hd-root[data-theme="auto"]', L) + '}')

    parts.append(
        '.hd-appearance{display:none;align-items:center;justify-content:center;flex-wrap:wrap;gap:6px;'
        f'margin:14px 0 0;font:500 12px {SANS};color:{MUTED}' + '}'
    )
    parts.append('.hd-js .hd-appearance{display:flex!important}')
    parts.append(f'.hd-appearance span{{margin-right:4px;color:{MUTED}}}')
    parts.append(
        f'.hd-appearance button{{padding:5px 11px;font:500 12px {SANS};color:{MUTED};background:transparent;'
        f'border:1px solid {RULE};border-radius:999px;cursor:pointer}}'
    )
    parts.append(
        f'.hd-appearance button[aria-pressed="true"]{{color:{PAPER};background:{INK};border-color:{INK}}}'
    )

    def appearance_theme(sel, T):
        return (
            f'{sel} .hd-appearance span,{sel} .hd-appearance button{{color:{T["muted"]};border-color:{T["rule"]}}}'
            f'{sel} .hd-appearance button[aria-pressed="true"]{{color:{T["paper"]};'
            f'background:{T["ink"]};border-color:{T["ink"]}}}'
        )

    parts.append(appearance_theme('.hd-root[data-theme="light"]', L))
    parts.append(appearance_theme('.hd-root[data-theme="sepia"]', S))
    parts.append('@media(prefers-color-scheme:light){' + appearance_theme('.hd-root[data-theme="auto"]', L) + '}')
    return ''.join(parts)


def _theme_boot_script():
    """Apply saved pw_theme before paint; reveal controls. Same key as the live site."""
    # Keep this tiny and self-contained; runs in the Buttondown archive page.
    return (
        '<script>(function(){try{var r=document.getElementById("hd-root");if(!r)return;'
        'r.classList.add("hd-js");'
        'var t=null;try{t=localStorage.getItem("pw_theme")}catch(e){}'
        'if(t==="light"||t==="dark"||t==="sepia")r.setAttribute("data-theme",t);'
        'else if(t==="auto")r.setAttribute("data-theme","auto");'
        # else keep the dark default baked into the markup
        'function sync(){var p=r.getAttribute("data-theme")||"dark";'
        'r.querySelectorAll(".hd-appearance button").forEach(function(b){'
        'b.setAttribute("aria-pressed",String(b.getAttribute("data-t")===p));});}'
        'r.addEventListener("click",function(ev){var b=ev.target.closest&&ev.target.closest(".hd-appearance button");'
        'if(!b)return;var v=b.getAttribute("data-t");r.setAttribute("data-theme",v);'
        'try{if(v==="auto")localStorage.removeItem("pw_theme");else localStorage.setItem("pw_theme",v);}catch(e){}'
        'sync();});'
        'sync();'
        'var mq=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)");'
        'if(mq){var f=function(){if((r.getAttribute("data-theme")||"")==="auto")sync();};'
        'mq.addEventListener?mq.addEventListener("change",f):mq.addListener&&mq.addListener(f);}'
        '}catch(e){}})();</script>'
    )


def appearance_bar():
    """Web-archive only (hidden until JS). Mirrors the site's Appearance control group."""
    return (
        '<div class="hd-appearance" role="group" aria-label="Appearance">'
        '<span>Appearance</span>'
        '<button type="button" data-t="auto">Auto</button>'
        '<button type="button" data-t="light">Light</button>'
        '<button type="button" data-t="sepia">Sepia</button>'
        '<button type="button" data-t="dark" aria-pressed="true">Dark</button>'
        '</div>'
    )


def open_paper():
    """Opening wrapper and masthead. Explicit dark bgcolor so Buttondown's web archive (and clients
    that ignore <style>) render on charcoal with light text. Theme controls enhance the archive view."""
    return (
        '<style>@import url("https://fonts.googleapis.com/css2?family=IM+Fell+English&family=Pinyon+Script&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap");'
        # Stop iPhone Mail turning dates and times into red underlined links.
        'a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;'
        'font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}'
        # Reinforce dark tokens if a client forces a light canvas around the email.
        '.hd-wrap{background-color:' + PAPER + '!important;color:' + BODY + '!important}'
        + _theme_css() +
        '</style>\n'
        # Wrapper carries data-theme so archive CSS can switch palettes without touching inline defaults.
        '<div class="hd-root" id="hd-root" data-theme="dark">\n'
        f'<table role="presentation" class="hd-wrap" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'bgcolor="{PAPER}" style="width:100%;border-collapse:collapse;background-color:{PAPER}">'
        f'<tr><td class="hd-body" bgcolor="{PAPER}" style="padding:6px 4px 20px;background-color:{PAPER};'
        f'color:{BODY};font-family:{SERIF};font-size:15px;line-height:1.5">\n'
        # Folio: double rule, small caps line, single rule (as on the site)
        f'<p class="hd-inkrule hd-ink" style="margin:0;padding:6px 0 5px;border-top:3px double {INK};'
        f'border-bottom:1px solid {INK};text-align:center;font-family:{SANS};font-size:9px;font-weight:600;'
        f'letter-spacing:1.6px;text-transform:uppercase;color:{INK}">Spin-free news · Ranked by impact</p>\n'
        # Wordmark in the site's fonts (falls back to Georgia where web fonts don't load)
        f'<p style="margin:16px 0 0;text-align:center;white-space:nowrap;line-height:1.1">'
        f'<a href="{SITE}/" style="text-decoration:none">'
        f'<span class="hd-ink" style="font-family:{DISPLAY};font-size:25px;letter-spacing:1px;color:{INK}">HIGH</span> '
        f'<span class="hd-accent" style="font-family:\'Pinyon Script\',\'Snell Roundhand\',cursive;font-size:31px;'
        f'margin:0 3px;color:{ACCENT}">impact</span> '
        f'<span class="hd-ink" style="font-family:{DISPLAY};font-size:25px;letter-spacing:1px;color:{INK}">NEWS</span> '
        f'<span class="hd-accent" style="font-family:\'Pinyon Script\',\'Snell Roundhand\',cursive;font-size:31px;'
        f'margin:0 3px;color:{ACCENT}">daily</span></a></p>\n'
        f'<p style="margin:8px 0 0;text-align:center;line-height:0"><img src="{IMG}/orn-head.png" alt="" width="260" '
        f'height="20" style="display:inline-block;width:260px;max-width:80%;height:auto;border:0"></p>\n'
        + appearance_bar()
    )


def close_paper():
    return _theme_boot_script() + "\n</td></tr></table>\n</div>"


def kicker(text):
    """Edition name and date, e.g. EVENING EDITION · TUESDAY, SEPTEMBER 29."""
    return (f'<p class="hd-accent" style="margin:18px 0 0;text-align:center;font-family:{SANS};font-size:11px;font-weight:700;'
            f'letter-spacing:1.2px;text-transform:uppercase;color:{ACCENT}">{e(text)}</p>')


def tagline(text):
    return (f'<p class="hd-muted" style="margin:4px 0 6px;text-align:center;font-family:{SERIF};font-style:italic;font-size:14px;'
            f'color:{MUTED}">{e(text)}</p>')


def badge(text, bg="#a3231a"):
    return (f'<p style="margin:18px 0 0;text-align:center"><span style="display:inline-block;font-family:{SANS};'
            f'font-size:12px;font-weight:700;letter-spacing:2px;color:#ffffff;background:{bg};padding:5px 10px;'
            f'border-radius:4px">{e(text)}</span></p>')


def section(text, rule=True):
    """Group label: NEW SINCE THIS MORNING, ALSO TODAY, COMING UP..."""
    return (f'<p class="hd-muted hd-rule" style="margin:{"34px" if rule else "26px"} 0 0;padding:{"14px" if rule else "0"} 0 6px;'
            f'{f"border-top:3px double {RULE};" if rule else ""}border-bottom:1px solid {RULE};font-family:{SANS};'
            f'font-size:12px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:{MUTED}">{e(text)}</p>')


def story(it, n, first=False, size=18):
    """One story: headline, detail, impact meter + why + source."""
    out = []
    if not first:
        out.append(f'<p style="margin:22px 0 0;text-align:center;line-height:0"><img src="{IMG}/orn-sep.png" alt="" '
                   f'width="180" height="18" style="display:inline-block;width:180px;max-width:60%;height:auto;border:0"></p>')
    out.append(f'<h3 class="hd-ink" style="margin:{"20px" if first else "22px"} 0 8px;font-family:{SERIF};font-size:{size}px;'
               f'line-height:1.3;font-weight:600;color:{INK}">{e(it.get("text"))}</h3>')
    if it.get("detail"):
        out.append(f'<p class="hd-body" style="margin:0 0 10px;font-family:{SERIF};font-size:15px;line-height:1.5;color:{BODY}">'
                   f'{e(it["detail"])}</p>')
    src = (" " + link((it.get("source") or "Source") + " ↗", it["url"])) if str(it.get("url", "")).startswith("http") else ""
    out.append(f'<p class="hd-muted" style="margin:0;font-family:{SANS};font-size:13px;line-height:1.45;color:{MUTED}">'
               f'<img src="{IMG}/impact-{n}.png" alt="" width="50" height="16" '
               f'style="width:50px;height:16px;vertical-align:-3px;border:0"> '
               f'<b class="hd-ink" style="color:{INK}">Impact {n}/5.</b> {e(it.get("why"))}{src}</p>')
    return "\n".join(out)


def bullets(rows):
    """rows: list of (label or None, text, url or None)."""
    lis = []
    for lab, text, url in rows:
        pre = f'<b class="hd-ink" style="color:{INK}">{e(lab)}:</b> ' if lab else ""
        src = (" " + link("Source ↗", url)) if url and str(url).startswith("http") else ""
        lis.append(f'<tr><td class="hd-body hd-rule" style="padding:9px 0;border-bottom:1px solid {RULE};font-family:{SANS};font-size:14px;'
                   f'line-height:1.45;color:{BODY}">{pre}{e(text)}{src}</td></tr>')
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;border-collapse:collapse">{"".join(lis)}</table>')


def dated(rows):
    """rows: list of (date label, text) for Coming up."""
    trs = "".join(f'<tr><td valign="top" class="hd-accent hd-rule" style="width:64px;padding:9px 10px 9px 0;border-bottom:1px solid {RULE};'
                  f'font-family:{SANS};font-size:13px;font-weight:700;color:{ACCENT};white-space:nowrap">{e(d)}</td>'
                  f'<td class="hd-body hd-rule" style="padding:9px 0;border-bottom:1px solid {RULE};font-family:{SANS};font-size:14px;'
                  f'line-height:1.45;color:{BODY}">{e(t)}</td></tr>' for d, t in rows)
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;border-collapse:collapse">{trs}</table>')


def signoff(text):
    return (f'<p class="hd-muted" style="margin:30px 0 0;text-align:center;font-family:{SERIF};font-style:italic;font-size:15px;'
            f'color:{MUTED}">{e(text)}</p>')


def note(html_text):
    """A centered small paragraph (html_text may contain links)."""
    return (f'<p class="hd-muted" style="margin:14px 0 0;text-align:center;font-family:{SANS};font-size:14px;line-height:1.5;'
            f'color:{MUTED}">{html_text}</p>')


def share_box(edition_url):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;margin-top:26px;border-collapse:separate"><tr><td bgcolor="{BOX}" class="hd-box hd-body" '
            f'style="padding:18px 16px;background:{BOX};background-color:{BOX};border:1px solid {RULE};'
            f'border-radius:12px;text-align:center;font-family:{SANS};font-size:14px;line-height:1.5;color:{BODY}">'
            f'<b class="hd-ink" style="font-size:15px;color:{INK}">Know someone who’d like this?</b><br>'
            f'Forward this email, or send them {link("a link to this edition", edition_url, underline=True)}.<br>'
            f'<span class="hd-muted" style="font-size:14px;color:{MUTED}"><i>Forwarded this?</i> '
            f'{link("Subscribe free", SITE + "/#subscribe", underline=True)}.</span></td></tr></table>')


def footer(links_html, fine=""):
    out = [f'<p class="hd-muted" style="margin:22px 0 0;text-align:center;font-family:{SANS};font-size:13px;line-height:1.6;'
           f'color:{MUTED}">{links_html}</p>']
    if fine:
        out.append(f'<p class="hd-muted" style="margin:8px 0 0;text-align:center;font-family:{SANS};font-size:12px;line-height:1.5;'
                   f'color:{MUTED}">{fine}</p>')
    out.append(f'<p style="margin:22px 0 0;text-align:center;line-height:0"><img src="{IMG}/orn-end.png" alt="" '
               f'width="280" height="44" style="display:inline-block;width:280px;max-width:80%;height:auto;border:0"></p>')
    out.append(f'<p class="hd-muted" style="margin:10px 0 0;text-align:center;font-family:{SANS};font-size:12px;letter-spacing:4px;'
               f'color:{MUTED}">— 30 —</p>')
    return "\n".join(out)
