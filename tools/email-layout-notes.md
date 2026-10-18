# Email layout notes

Hand-maintained notes on the email shell in `tools/emailstyle.py` (used by `tools/edition.py` and `tools/breaking_email.py`).
Phone reading is the priority (Apple Mail on iPhone, then the Gmail app); desktop readers mostly use the site.

## Before: fixed 600px column, tuned for Apple Mail (as of commit 1e2b3af, Oct 18 2026)

What it did and why:
- The email is always dark Mail grey (#2c2c2e) with `color-scheme: only dark`, so iOS Mail does not repaint it.
- `open_paper()` wraps everything in a 100%-wide outer table (`.hd-wrap`), a `<center>`, and a **fixed** inner table
  `width="600" align="center"` with `style="width:600px;max-width:100%"`. The `align="center"` attribute and `<center>`
  are there because Apple Mail ignores `margin:auto`. iOS Mail scales a 600px email down to fit the phone, so the fixed
  width looked right there.
- The downside: clients that do not auto-scale (the Gmail app, browsers, Buttondown's web archive) keep a 600px column on a
  390px phone, so text runs off the right edge (seen in headless Chrome at 390px, Oct 18 2026).
- No Outlook/MSO conditional wrapper existed.

Exact code at 1e2b3af, `open_paper()` and `close_paper()`:

```python
def open_paper():
    """Opening wrapper and masthead. Explicit dark bgcolor so Buttondown's web archive (and clients
    that ignore <style>) render on measured Mail grey (#2c2c2e) with light text. Website archive uses its own theme switcher."""
    return (
        '<style>@import url("https://fonts.googleapis.com/css2?family=IM+Fell+English&family=Pinyon+Script&'
        'family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap");'
        'a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;'
        'font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}'
        '.hd-wrap,.hd-inner{background-color:' + PAPER + '!important;color:' + BODY + '!important}'
        '.hd-root,.hd-wrap{width:100%!important;min-width:100%!important}'
        '.hd-inner{width:600px;max-width:100%;margin:0 auto!important}'
        'h3.hd-ink::first-letter{float:left;font-family:\'IM Fell English\',Georgia,\'Times New Roman\',serif;font-weight:400;color:' + ACCENT + ';font-size:2.6em;line-height:.85;padding:.05em .1em 0 0;margin:0 .1em .05em 0}'
        '.newsletter-body,.email-content,body{width:100%!important;min-width:100%!important;margin:0!important;padding:0!important}'
        '@media (max-width:480px){.hd-seal{width:104px!important;height:104px!important;max-width:104px!important}}'
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
        # Eagle seal above the wordmark, as on the site masthead (140px; 104px on phones <=480px).
        # Always the site's dark seal: the email is always Mail grey, and this self-contained black disc
        # also reads on white if a client lightens the background. 2x PNG for retina.
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse">'
        f'<tr><td align="center" style="padding:8px 0 0;text-align:center;line-height:0;font-size:0">'
        f'<a href="{SITE}/" style="text-decoration:none;border:0">'
        f'<img class="hd-seal" src="{IMG}/seal.png" alt="High Impact News Daily" width="140" height="140" border="0" '
        f'style="display:block;margin:0 auto;width:140px;height:140px;max-width:140px;border:0;outline:none;text-decoration:none"></a>'
        f'</td></tr></table>\n'
        f'<p style="margin:12px 0 0;text-align:center;white-space:nowrap;line-height:1.1">'
        f'<a href="{SITE}/" style="text-decoration:none">'
        f'<span class="hd-ink" style="font-family:{DISPLAY};font-size:25px;letter-spacing:1px;color:{INK}">HIGH</span> '
        f'<span class="hd-accent" style="font-family:\'Pinyon Script\',\'Snell Roundhand\',cursive;font-size:31px;'
        f'margin:0 3px;color:{ACCENT}">impact</span> '
        f'<span class="hd-ink" style="font-family:{DISPLAY};font-size:25px;letter-spacing:1px;color:{INK}">NEWS</span> '
        f'<span class="hd-accent" style="font-family:\'Pinyon Script\',\'Snell Roundhand\',cursive;font-size:31px;'
        f'margin:0 3px;color:{ACCENT}">daily</span></a></p>\n'
        f'<p style="margin:8px 0 0;text-align:center;line-height:0"><img src="{IMG}/orn-head.png" alt="" width="260" '
        f'height="20" style="display:inline-block;width:260px;max-width:80%;height:auto;border:0"></p>\n'
    )


def close_paper():
    return "</td></tr></table></center></td></tr></table>\n</div>"
```

Impact meter image inside `story()` at 1e2b3af:

```python
    src = (" " + link((it.get("source") or "Source") + " ↗", it["url"])) if str(it.get("url", "")).startswith("http") else ""
    out.append(f'<p class="hd-muted" style="margin:0;font-family:{SANS};font-size:13px;line-height:1.45;color:{MUTED}">'
               f'<img src="{IMG}/impact-{n}.png" alt="" width="50" height="16" '
               f'style="width:50px;height:16px;vertical-align:-3px;border:0"> '
               f'<b class="hd-ink" style="color:{INK}">Impact {n}/5.</b> {e(it.get("why"))}{src}</p>')
```

## After: fluid column, max 600px (commit "Email layout: fluid column ...")

- CSS: `.hd-inner{width:100%!important;max-width:600px!important;margin:0 auto!important}`, plus `img{max-width:100%;height:auto}`
  and `overflow-wrap:break-word` on `.hd-body`, so long words or URLs wrap instead of widening the column.
- Inner table: `width="100%" align="center"`, `style="width:100%;max-width:600px;..."`. `align="center"` and `<center>` stay
  for Apple Mail.
- Outlook (MSO): a conditional fixed `width="600"` wrapper table opens before the inner table in `open_paper()` and closes
  in `close_paper()` (`<!--[if mso]>...<![endif]-->`). If a client strips the comments, the column is simply fluid.
- Seal `<img>`: `width="140"` attribute kept; style `width:140px;max-width:100%;height:auto`. Phone size (104px at <=480px) unchanged.
- Impact meter `<img>`: `max-width:100%;height:auto` instead of a fixed height.
- Wordmark: phones <=400px get a slightly smaller wordmark (`.hd-wm-p` 21px, `.hd-wm-s` 26px) so the nowrap title fits 360px screens.
- Checked in headless Chrome, rendered inside 360/390/640px iframes: no horizontal overflow, seal centered, 600px max on wide screens.

## How to revert

- One command: `git revert <hash of the "Email layout: fluid column" commit>`. That restores the fixed-600px shell above;
  the seal-spacing commit and the source-link commits are separate and are not affected.
- Or paste the "Before" code back into `open_paper()`/`close_paper()` and the impact `<img>` in `story()`.
- Never run `tools/edition.py` in the real repo to test. It rewrites `email/today.json`, and a push of that file sends to
  subscribers. Test in a scratch copy and render the generated `email/today.json` body in a headless browser.
