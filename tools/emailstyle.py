"""Shared look for every email (editions and breaking alerts).

Dark inline styles + bgcolor by default so mail clients that strip <style> stay readable on Mail grey.
On the web archive (and mail apps that keep CSS), Appearance Auto follows prefers-color-scheme
with the same Light/Dark palettes as the manual toggles; Light / Sepia / Dark radios override.
Buttondown forbids <script> and event handlers in email bodies, so theme choice uses radio buttons
+ :has() selectors (session-local; no localStorage). Flourishes are mid-tone PNGs that read on
dark; the wordmark is live text. Fonts: Source Serif 4 where the mail app can load it (Apple Mail,
iOS), falling back to Georgia; labels in the system sans. Each HTML block starts on its own line
so Buttondown passes it through untouched.
"""
import html

SITE = "https://hinewsdaily.com"
IMG = f"{SITE}/assets/email"

# Dark palette for email: paper is John's GIMP-measured Mail grey (site stays #000000)
PAPER = "#2c2c2e"   # email wrapper — measured dark bg in iOS Mail
INK = "#f2f2f7"     # headlines (cool system light, no cream/brown)
BODY = "#d1d1d6"    # story text (cool grey)
MUTED = "#8e8e93"   # labels, captions (systemGray)
RULE = "#48484a"    # hairlines (cool grey, not brown)
ACCENT = "#e08a6f"  # warm accent links / section labels (site dark accent)
BOX = "#3a3a3c"     # share box / inset surface (elevated above paper)
SERIF = "'Source Serif 4','Source Serif Pro',Georgia,'Times New Roman',Times,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
DISPLAY = "'IM Fell English',Georgia,'Times New Roman',serif"

# Light / sepia / dark tokens (match index.html :root / data-theme)
LIGHT = dict(paper="#ffffff", ink="#1d1a16", body="#1d1a16", muted="#6b6358",
             rule="#d9d0bf", accent="#8b2a1d", box="#f5f5f7")
SEPIA = dict(paper="#f4ecd8", ink="#3b2f22", body="#3b2f22", muted="#75644f",
             rule="#d6c7a4", accent="#8b2a1d", box="#fbf5e6")
DARK = dict(paper=PAPER, ink=INK, body=BODY, muted=MUTED, rule=RULE, accent=ACCENT, box=BOX)

e = lambda s: html.escape(str(s or ""), quote=True)


def link(text, url, color=ACCENT, underline=False):
    return (f'<a class="hd-accent" href="{e(url)}" style="color:{color};text-decoration:{"underline" if underline else "none"};'
            f'font-weight:600">{e(text)}</a>')


def _theme_block(sel, T, scheme="light"):
    """Full palette overrides for one Appearance choice (manual or Auto+media)."""
    return (
        f'{sel}{{color-scheme:{scheme};background-color:{T["paper"]}}}'
        f'{sel} .hd-wrap,{sel} .hd-inner,{sel} .hd-body{{background-color:{T["paper"]}!important;color:{T["body"]}!important}}'
        f'{sel} .hd-ink,{sel} .hd-inkrule{{color:{T["ink"]}!important;'
        f'border-top-color:{T["ink"]}!important;border-bottom-color:{T["ink"]}!important}}'
        f'{sel} .hd-muted{{color:{T["muted"]}!important}}'
        f'{sel} .hd-accent{{color:{T["accent"]}!important}}'
        f'{sel} .hd-rule{{border-color:{T["rule"]}!important;'
        f'border-top-color:{T["rule"]}!important;border-bottom-color:{T["rule"]}!important}}'
        f'{sel} .hd-box{{background:{T["box"]}!important;background-color:{T["box"]}!important;'
        f'border-color:{T["rule"]}!important;color:{T["body"]}!important}}'
        f'{sel} .hd-appearance span,{sel} .hd-appearance label{{color:{T["muted"]};border-color:{T["rule"]}}}'
        f'{sel} .hd-appearance input:checked + label{{color:{T["paper"]};background:{T["ink"]};border-color:{T["ink"]}}}'
    )


def _theme_css():
    """Overrides for web-archive theme switching via CSS-only radios (:has).

    Auto follows prefers-color-scheme (same idea as the site: no forced theme until
    Light/Sepia/Dark is chosen). Manual radios override because only one can be checked.
    Inline styles stay dark for clients that strip <style>.
    """
    L, S, D = LIGHT, SEPIA, DARK
    parts = [
        '.hd-root{color-scheme:dark;background-color:%s}' % PAPER,
        '.hd-appearance input{position:absolute;opacity:0;pointer-events:none;width:0;height:0;margin:0}',
        ('.hd-appearance{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:6px;'
         f'margin:14px 0 0;font:500 12px {SANS};color:{MUTED}' + '}'),
        f'.hd-appearance span{{margin-right:4px;color:{MUTED}}}',
        (f'.hd-appearance label{{padding:5px 11px;font:500 12px {SANS};color:{MUTED};background:transparent;'
         f'border:1px solid {RULE};border-radius:999px;cursor:pointer}}'),
        f'.hd-appearance input:checked + label{{color:{PAPER};background:{INK};border-color:{INK}}}',
        # Manual themes (always win over Auto media queries: exclusive radios)
        _theme_block('.hd-root:has(#hd-t-light:checked)', L, 'light'),
        _theme_block('.hd-root:has(#hd-t-sepia:checked)', S, 'light'),
        _theme_block('.hd-root:has(#hd-t-dark:checked)', D, 'dark'),
        # Auto = follow the device (site pw_theme auto / no data-theme)
        '@media(prefers-color-scheme:light){' + _theme_block('.hd-root:has(#hd-t-auto:checked)', L, 'light') + '}',
        '@media(prefers-color-scheme:dark){' + _theme_block('.hd-root:has(#hd-t-auto:checked)', D, 'dark') + '}',
    ]
    return ''.join(parts)


def appearance_bar():
    """Appearance controls for the web archive (CSS-only; Buttondown disallows script tags)."""
    return (
        '<div class="hd-appearance" role="group" aria-label="Appearance">'
        '<span>Appearance</span>'
        '<input type="radio" name="hd-theme" id="hd-t-auto" value="auto" checked>'
        '<label for="hd-t-auto">Auto</label>'
        '<input type="radio" name="hd-theme" id="hd-t-light" value="light">'
        '<label for="hd-t-light">Light</label>'
        '<input type="radio" name="hd-theme" id="hd-t-sepia" value="sepia">'
        '<label for="hd-t-sepia">Sepia</label>'
        '<input type="radio" name="hd-theme" id="hd-t-dark" value="dark">'
        '<label for="hd-t-dark">Dark</label>'
        '</div>'
    )


def open_paper():
    """Opening wrapper and masthead. Explicit dark bgcolor so Buttondown's web archive (and clients
    that ignore <style>) render on measured Mail grey (#2c2c2e) with light text. Theme controls enhance the archive view."""
    return (
        '<style>@import url("https://fonts.googleapis.com/css2?family=IM+Fell+English&family=Pinyon+Script&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap");'
        'a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;'
        'font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}'
        '.hd-wrap,.hd-inner{background-color:' + PAPER + '!important;color:' + BODY + '!important}'
        '.hd-root,.hd-wrap{width:100%!important;min-width:100%!important}'
        '.hd-inner{width:600px;max-width:100%;margin:0 auto!important}'
        '.newsletter-body,.email-content,body{width:100%!important;min-width:100%!important;margin:0!important;padding:0!important}'
        + _theme_css() +
        '</style>\n'
        f'<div class="hd-root" style="width:100%;min-width:100%;margin:0;padding:0;background-color:{PAPER}">\n'
        f'<table role="presentation" class="hd-wrap" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'bgcolor="{PAPER}" style="width:100%;min-width:100%;border-collapse:collapse;background-color:{PAPER}">'
        f'<tr><td align="center" valign="top" bgcolor="{PAPER}" style="padding:0;background-color:{PAPER};text-align:center">'
        '<center>'
        f'<table role="presentation" class="hd-inner" width="600" align="center" cellpadding="0" cellspacing="0" border="0" '
        f'bgcolor="{PAPER}" style="width:600px;max-width:100%;border-collapse:collapse;background-color:{PAPER};margin:0 auto;text-align:left">'
        f'<tr><td class="hd-body" bgcolor="{PAPER}" style="padding:6px 16px 20px;background-color:{PAPER};'
        f'color:{BODY};font-family:{SERIF};font-size:15px;line-height:1.5;text-align:left">\n'
        f'<p class="hd-inkrule hd-ink" style="margin:0;padding:6px 0 5px;border-top:3px double {INK};'
        f'border-bottom:1px solid {INK};text-align:center;font-family:{SANS};font-size:9px;font-weight:600;'
        f'letter-spacing:1.6px;text-transform:uppercase;color:{INK}">Spin-free news · Ranked by impact</p>\n'
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
    return "</td></tr></table></center></td></tr></table>\n</div>"


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
