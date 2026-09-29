"""Shared look for every email (editions and breaking alerts).

Emails are built as fully inline-styled HTML on a cream "paper" background, so they look like the site
in every mail app, in light and dark mode: the paper and its text colors are set explicitly, so a dark
inbox can't turn the headlines dark-on-dark. Fonts: Source Serif 4 where the mail app can load it
(Apple Mail, iOS), falling back to Georgia; labels in the system sans. Each HTML block starts on its
own line so Buttondown passes it through untouched.
"""
import html

SITE = "https://hinewsdaily.com"
IMG = f"{SITE}/assets/email"

PAPER = "#faf7f1"   # page background (matches the site and the masthead image)
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
    return (f'<a href="{e(url)}" style="color:{color};text-decoration:{"underline" if underline else "none"};'
            f'font-weight:600">{e(text)}</a>')


def open_paper():
    """Opening of the paper wrapper. Everything after it sits on cream until close_paper()."""
    return (
        '<style>@import url("https://fonts.googleapis.com/css2?family=IM+Fell+English&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap");</style>\n'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAPER}" '
        f'style="width:100%;background:{PAPER};background-color:{PAPER};border-radius:6px;border-collapse:separate">'
        f'<tr><td style="padding:22px 22px 28px;background:{PAPER};background-color:{PAPER};color:{BODY};'
        f'font-family:{SERIF};font-size:17px;line-height:1.55">\n'
        f'<a href="{SITE}/" style="text-decoration:none"><img src="{IMG}/masthead.png" alt="High Impact News Daily" '
        f'width="560" style="display:block;width:100%;max-width:560px;height:auto;border:0;margin:0 auto"></a>')


def close_paper():
    return "</td></tr></table>"


def kicker(text):
    """Edition name and date, e.g. EVENING EDITION · TUESDAY, SEPTEMBER 29."""
    return (f'<p style="margin:18px 0 0;text-align:center;font-family:{SANS};font-size:12px;font-weight:700;'
            f'letter-spacing:2px;text-transform:uppercase;color:{ACCENT}">{e(text)}</p>')


def tagline(text):
    return (f'<p style="margin:4px 0 6px;text-align:center;font-family:{SERIF};font-style:italic;font-size:16px;'
            f'color:{MUTED}">{e(text)}</p>')


def badge(text, bg="#b3261e"):
    return (f'<p style="margin:18px 0 0;text-align:center"><span style="display:inline-block;font-family:{SANS};'
            f'font-size:12px;font-weight:700;letter-spacing:2px;color:#ffffff;background:{bg};padding:5px 10px;'
            f'border-radius:4px">{e(text)}</span></p>')


def section(text, rule=True):
    """Group label: NEW SINCE THIS MORNING, ALSO TODAY, COMING UP..."""
    return (f'<p style="margin:{"34px" if rule else "26px"} 0 0;padding:{"14px" if rule else "0"} 0 6px;'
            f'{f"border-top:3px double {RULE};" if rule else ""}border-bottom:1px solid {RULE};font-family:{SANS};'
            f'font-size:12px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:{MUTED}">{e(text)}</p>')


def story(it, n, first=False, size=21):
    """One story: headline, detail, impact meter + why + source."""
    out = []
    if not first:
        out.append(f'<p style="margin:24px auto 0;width:60px;border-top:1px solid {RULE};font-size:1px;line-height:1px">&nbsp;</p>')
    out.append(f'<h3 style="margin:{"20px" if first else "22px"} 0 8px;font-family:{SERIF};font-size:{size}px;'
               f'line-height:1.3;font-weight:600;color:{INK}">{e(it.get("text"))}</h3>')
    if it.get("detail"):
        out.append(f'<p style="margin:0 0 10px;font-family:{SERIF};font-size:17px;line-height:1.55;color:{BODY}">'
                   f'{e(it["detail"])}</p>')
    src = (" " + link((it.get("source") or "Source") + " ↗", it["url"])) if str(it.get("url", "")).startswith("http") else ""
    out.append(f'<p style="margin:0;font-family:{SANS};font-size:14px;line-height:1.5;color:{MUTED}">'
               f'<img src="{IMG}/impact-{n}.png" alt="" width="50" height="16" '
               f'style="width:50px;height:16px;vertical-align:-3px;border:0"> '
               f'<b style="color:{INK}">Impact {n}/5.</b> {e(it.get("why"))}{src}</p>')
    return "\n".join(out)


def bullets(rows):
    """rows: list of (label or None, text, url or None)."""
    lis = []
    for lab, text, url in rows:
        pre = f'<b style="color:{INK}">{e(lab)}:</b> ' if lab else ""
        src = (" " + link("Source ↗", url)) if url and str(url).startswith("http") else ""
        lis.append(f'<tr><td style="padding:9px 0;border-bottom:1px solid {RULE};font-family:{SANS};font-size:15px;'
                   f'line-height:1.45;color:{BODY}">{pre}{e(text)}{src}</td></tr>')
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;border-collapse:collapse">{"".join(lis)}</table>')


def dated(rows):
    """rows: list of (date label, text) for Coming up."""
    trs = "".join(f'<tr><td valign="top" style="width:64px;padding:9px 10px 9px 0;border-bottom:1px solid {RULE};'
                  f'font-family:{SANS};font-size:14px;font-weight:700;color:{ACCENT};white-space:nowrap">{e(d)}</td>'
                  f'<td style="padding:9px 0;border-bottom:1px solid {RULE};font-family:{SANS};font-size:15px;'
                  f'line-height:1.45;color:{BODY}">{e(t)}</td></tr>' for d, t in rows)
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;border-collapse:collapse">{trs}</table>')


def signoff(text):
    return (f'<p style="margin:30px 0 0;text-align:center;font-family:{SERIF};font-style:italic;font-size:17px;'
            f'color:{MUTED}">{e(text)}</p>')


def note(html_text):
    """A centered small paragraph (html_text may contain links)."""
    return (f'<p style="margin:14px 0 0;text-align:center;font-family:{SANS};font-size:14px;line-height:1.5;'
            f'color:{MUTED}">{html_text}</p>')


def share_box(edition_url):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="width:100%;margin-top:26px;border-collapse:separate"><tr><td bgcolor="#ffffff" '
            f'style="padding:18px 16px;background:#ffffff;background-color:#ffffff;border:1px solid {RULE};'
            f'border-radius:12px;text-align:center;font-family:{SANS};font-size:15px;line-height:1.5;color:{BODY}">'
            f'<b style="font-size:17px;color:{INK}">Know someone who’d like this?</b><br>'
            f'Forward this email, or send them {link("a link to this edition", edition_url, underline=True)}.<br>'
            f'<span style="font-size:14px;color:{MUTED}"><i>Forwarded this?</i> '
            f'{link("Subscribe free", SITE + "/#subscribe", underline=True)}.</span></td></tr></table>')


def footer(links_html, fine=""):
    out = [f'<p style="margin:22px 0 0;text-align:center;font-family:{SANS};font-size:13px;line-height:1.6;'
           f'color:{MUTED}">{links_html}</p>']
    if fine:
        out.append(f'<p style="margin:8px 0 0;text-align:center;font-family:{SANS};font-size:12px;line-height:1.5;'
                   f'color:{MUTED}">{fine}</p>')
    out.append(f'<p style="margin:14px 0 0;text-align:center;font-family:{SANS};font-size:12px;letter-spacing:4px;'
               f'color:{MUTED}">— 30 —</p>')
    return "\n".join(out)
