"""Shared look for every email (editions and breaking alerts).

Emails have no background of their own: they sit on the mail app's background (white or dark). Text is
inline-styled in the site's light colors (near-black ink, burnt red), and a small stylesheet switches it to
the site's dark colors when the reader's phone or mail app is in dark mode. The masthead is live text in
the site's fonts; the flourishes are transparent images in mid-tones that read on light and dark alike.
Fonts: Source Serif 4 where the mail app can load it
(Apple Mail, iOS), falling back to Georgia; labels in the system sans. Each HTML block starts on its
own line so Buttondown passes it through untouched.
"""
import html

SITE = "https://hinewsdaily.com"
IMG = f"{SITE}/assets/email"

PAPER = "#faf7f1"   # site background (used for the share box in light mode)
INK = "#1d1a16"     # headlines
BODY = "#3a342c"    # story text
MUTED = "#6b6358"   # labels, captions
RULE = "#e2d9c8"    # hairlines
ACCENT = "#8b2a1d"  # burnt red: links, section labels
SERIF = "'Source Serif 4','Source Serif Pro',Georgia,'Times New Roman',Times,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
DISPLAY = "'IM Fell English',Georgia,'Times New Roman',serif"

e = lambda s: html.escape(str(s or ""), quote=True)


def link(text, url, color=ACCENT, underline=False):
    return (f'<a class="hd-accent" href="{e(url)}" style="color:{color};text-decoration:{"underline" if underline else "none"};'
            f'font-weight:600">{e(text)}</a>')


def open_paper():
    """Opening wrapper and masthead. The wrapper has no background of its own, so the email sits on the
    mail app's own background (white or dark); text colors switch with the reader's light/dark setting."""
    return (
        '<style>@import url("https://fonts.googleapis.com/css2?family=IM+Fell+English&family=Pinyon+Script&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap");'
        # Stop iPhone Mail turning dates and times into red underlined links.
        'a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;'
        'font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}'
        '@media (prefers-color-scheme:dark){'
        '.hd-ink{color:#f0ebe2!important}.hd-body{color:#d9d2c5!important}.hd-muted{color:#a59b8a!important}'
        '.hd-accent{color:#eb9d82!important}.hd-rule{border-color:#3d3831!important}'
        '.hd-inkrule{border-color:#f0ebe2!important}'
        '.hd-box{background:#262320!important;background-color:#262320!important;border-color:#3d3831!important}'
        '}</style>\n'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="width:100%;border-collapse:collapse">'
        f'<tr><td class="hd-body" style="padding:6px 4px 20px;color:{BODY};font-family:{SERIF};font-size:15px;'
        f'line-height:1.5">\n'
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
        f'height="20" style="display:inline-block;width:260px;max-width:80%;height:auto;border:0"></p>')


def close_paper():
    return "</td></tr></table>"


def kicker(text):
    """Edition name and date, e.g. EVENING EDITION · TUESDAY, SEPTEMBER 29."""
    return (f'<p class="hd-accent" style="margin:18px 0 0;text-align:center;font-family:{SANS};font-size:11px;font-weight:700;'
            f'letter-spacing:1.2px;text-transform:uppercase;color:{ACCENT}">{e(text)}</p>')


def tagline(text):
    return (f'<p class="hd-muted" style="margin:4px 0 6px;text-align:center;font-family:{SERIF};font-style:italic;font-size:14px;'
            f'color:{MUTED}">{e(text)}</p>')


def badge(text, bg="#b3261e"):
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
            f'style="width:100%;margin-top:26px;border-collapse:separate"><tr><td bgcolor="#faf7f1" class="hd-box hd-body" '
            f'style="padding:18px 16px;background:#faf7f1;background-color:#faf7f1;border:1px solid {RULE};'
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
