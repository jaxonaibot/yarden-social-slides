#!/usr/bin/env python3
"""Render a Yarden slideshow (JSON spec) into 1080x1920 JPEGs using the brand template.
(JPEG on purpose: TikTok photo posts reject PNG.)

Usage:  python3 render_slides.py spec.json out_dir/

Spec format:
{
  "slug": "2026-11-06-leggy-seedlings",
  "slides": [
    {"kind": "hook",  "script": "Hey there!", "text": "Why are my seedlings so <hl>tall and floppy</hl>?", "eyebrow": "Myth-busting"},
    {"kind": "tip",   "num": 1, "heading": "They're <hl>reaching</hl> for light", "body": "..."},
    {"kind": "list",  "heading": "...", "items": ["...", "..."]},
    {"kind": "photo", "photo": "class-01.jpg", "heading": "...", "body": "..."},
    {"kind": "cta"}
  ]
}
RULES: no "Free in-person class · Alameda, CA" pill on any slide (the class is mentioned in text and on the CTA slide instead). The Yarden wordmark appears only on the CTA slide ("brand" flags are ignored). Library photos appear only on slide 1 ("photo-hook") or the CTA slide ("cta" with "photo"); a "photo" on any middle slide is dropped and the slide renders as text.
<hl>…</hl> marks the one highlighted phrase in a heading.
Photos are looked up in ./assets/photos/ ; a missing photo makes the slide fall back to a text card (never a stock image).
"""
import json, os, sys, re, html, base64, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = (HERE / "template.html").read_text()
LOGO_B64 = base64.b64encode((HERE / "assets" / "yarden-logo.png").read_bytes()).decode()
LOGO_SRC = f"data:image/png;base64,{LOGO_B64}"
PHOTOS = HERE / "assets" / "photos"

WAVE = ('<svg class="wave" viewBox="0 0 1080 160" preserveAspectRatio="none">'
        '<path d="M0,80 C270,160 540,0 810,80 C945,120 1012,100 1080,80 L1080,160 L0,160 Z" fill="{fill}"/></svg>')

def hl(s):
    """Escape text but allow <hl> highlight and <b> bold markers."""
    s = html.escape(s, quote=False)
    return (s.replace("&lt;hl&gt;", '<span class="hl">').replace("&lt;/hl&gt;", "</span>")
             .replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>"))

def brand_corner():
    """Rule: the Yarden wordmark appears only on the CTA slide. Other slides never show it."""
    return ""

def swipe(label="(Swipe left to watch)"):
    """Rule: the swipe cue appears only on slide 1, centered."""
    return f'<div class="swipe">{html.escape(label)}</div>'

def photo_tag(name, cls="photo tall", focus=None):
    p = PHOTOS / name if name else None
    if not p or not p.exists():
        return None
    mime = "image/jpeg" if p.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    b = base64.b64encode(p.read_bytes()).decode()
    style = f' style="object-position:{html.escape(focus)}"' if focus else ""
    return f'<img class="{cls}" src="data:{mime};base64,{b}" alt=""{style}>'

def slide_hook(s, i, n):
    script = f'<div class="script">{hl(s["script"])}</div>' if s.get("script") else ""
    eyebrow = f'<div class="eyebrow">{hl(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    size = "hook sm" if len(s["text"]) > 60 else "hook"
    return f'''<div class="slide ground-hero"><div class="glow-amber"></div><div class="glow-sky"></div>
      <div class="safe"><div class="stack">{eyebrow}{script}<div class="{size}">{hl(s["text"])}</div></div>
      </div>
      {swipe()}</div>'''

def slide_photo_hook(s, i, n):
    img = photo_tag(s.get("photo"), "bg", s.get("focus"))
    if img is None:
        return slide_hook(s, i, n)
    script = f'<div class="script">{hl(s["script"])}</div>' if s.get("script") else ""
    eyebrow = f'<div class="eyebrow">{hl(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    size = "hook sm" if len(s["text"]) > 60 else "hook"
    return f'''<div class="slide photo-hook">{img}<div class="shade"></div>
      <div class="safe"><div class="stack">{eyebrow}{script}<div class="{size}">{hl(s["text"])}</div>
      </div></div>
      {swipe()}</div>'''

def slide_tip(s, i, n):
    num = f'<div class="num">{s["num"]}</div>' if s.get("num") is not None else ""
    body = f'<div class="body">{hl(s["body"])}</div>' if s.get("body") else ""
    ground = s.get("ground", "ground-cream" if i % 2 else "ground-sand")
    return f'''<div class="slide {ground}"><div class="safe vc">{num}
      <div class="stack"><div class="heading">{hl(s["heading"])}</div><div class="divider"></div>{body}</div></div>
      {brand_corner() if s.get("brand") else ""}</div>'''

def slide_list(s, i, n):
    items = "".join(f'<div class="check">{hl(t)}</div>' for t in s["items"])
    ground = s.get("ground", "ground-cream" if i % 2 else "ground-sand")
    return f'''<div class="slide {ground}"><div class="safe vc">
      <div class="stack"><div class="heading">{hl(s["heading"])}</div><div class="divider"></div>
      <div class="card"><div class="stack">{items}</div></div></div></div>
      {brand_corner() if s.get("brand") else ""}</div>'''

def slide_photo(s, i, n):
    if 0 < i < n - 1:   # Rule: library photos only on the first or last slide -> render as a text card
        return slide_tip({k: v for k, v in s.items() if k not in ("photo", "frame", "focus")}, i, n)
    cls = {"tall": "photo tall", "short": "photo short", "banner": "photo banner", "natural": "photo natural"}[s.get("frame", "tall")]
    img = photo_tag(s.get("photo"), cls, s.get("focus"))
    if img is None:            # no photo available -> text card, never a stock/generated image
        return slide_tip({**s, "num": s.get("num")}, i, n)
    body = f'<div class="body">{hl(s["body"])}</div>' if s.get("body") else ""
    return f'''<div class="slide ground-paper"><div class="safe vc">
      <div class="stack"><div class="heading">{hl(s["heading"])}</div>{img}{body}</div></div>
      {brand_corner() if s.get("brand", True) else ""}</div>'''

def slide_quote(s, i, n):
    """A supplied testimonial, verbatim. Only use text Isaac supplied; never invent quotes."""
    heading = s.get("heading", "In Their <hl>Words</hl>")
    return f'''<div class="slide ground-sand"><div class="safe vc">
      <div class="stack"><div class="heading">{hl(heading)}</div>
      <div class="card-warm"><div class="quote-mark">“</div><div class="quote">{hl(s["quote"])}</div>
      <div class="quote-by">— {hl(s["by"])}</div></div></div></div>
      {brand_corner() if s.get("brand", True) else ""}</div>'''

def clean_cta_body(b):
    """The CTA slide already prints the URL; strip any 'learnwithyarden.com' / 'link in bio' / 'register at' phrasing from the body."""
    b = re.sub(r"\s*\(?(link in (our )?bio|link in profile)\)?[.!]?", "", b, flags=re.I)
    b = re.sub(r"\s*(register|sign up|save your spot)( for free| free)?( today)? at (learnwithyarden\.com|the link[^.]*)[.!]?", "", b, flags=re.I)
    b = re.sub(r"\s*\(?(at )?learnwithyarden\.com\)?[.!]?", "", b, flags=re.I)
    return re.sub(r"\s{2,}", " ", b).strip()

def slide_cta(s, i, n):
    img = photo_tag(s.get("photo"), "photo short")
    heading = s.get("heading", "Come Learn With Us <hl>In Person</hl>")
    body = clean_cta_body(s.get("body", "A <b>free</b>, in-person gardening class with Jason, every two weeks at Makerfarm in Alameda. "
                         "Bring your questions about your own yard, balcony or raised bed."))
    return f'''<div class="slide ground-paper"><div class="glow-amber"></div><div class="safe vc">
      <img class="logo" src="{LOGO_SRC}" alt="Yarden" style="align-self:flex-start">
      <div class="stack" style="margin-top:48px"><div class="script">Hey there!</div>
      <div class="heading">{hl(heading)}</div>{img or ""}<div class="body">{hl(body)}</div>
      <div class="cta-line">Save your spot — <span class="hl">it's free</span></div><div class="url">learnwithyarden.com</div></div></div>
      {WAVE.format(fill="#d1fae0")}</div>'''

RENDER = {"hook": slide_hook, "photo-hook": slide_photo_hook, "tip": slide_tip, "list": slide_list, "photo": slide_photo, "quote": slide_quote, "cta": slide_cta}

def render(spec_path, out_dir):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    slides = spec["slides"]
    assert 5 <= len(slides) <= 7, "A slideshow must have 5-7 slides"
    for k, sl in enumerate(slides[1:-1], 1):
        assert sl["kind"] != "photo-hook", f"slide {k+1}: photo-hook is only allowed as slide 1"
        if sl.get("photo"):
            print(f"note: slide {k+1} photo ignored — photos only on first/last slide", file=sys.stderr)
    assert slides[0]["kind"] in ("hook", "photo-hook") and slides[-1]["kind"] == "cta", "Slide 1 must be a hook, last slide the CTA"
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        for i, s in enumerate(slides):
            body = RENDER[s["kind"]](s, i, len(slides))
            page.set_content(TEMPLATE.replace("<!-- SLIDE_CONTENT -->", body), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            # JPEG, not PNG: TikTok's photo-post API accepts only JPEG/WebP (PNG hangs in "processing"); IG/FB take JPEG fine.
            f = out / f"{spec['slug']}-{i+1:02d}.jpg"
            page.screenshot(path=str(f), type="jpeg", quality=92)
            paths.append(str(f))
        browser.close()
    return paths

if __name__ == "__main__":
    for pth in render(sys.argv[1], sys.argv[2]):
        print(pth)
