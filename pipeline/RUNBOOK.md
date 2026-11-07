# Yarden Social Pipeline — Runbook

Daily photo-carousel posts for TikTok, Facebook, Instagram via Buffer. Single goal: registrations for the free in-person class at learnwithyarden.com.

## The class (describe it exactly like this)
- Free. In person. Every two weeks. Taught by Jason, a master gardener. At Makerfarm in Alameda, CA.
- Attendees learn the fundamentals — soil, water, sunlight, what to plant and when — and leave with a plan for their own yard, balcony, or raised bed.
- Live Q&A about the attendee's specific space and our local climate. Not a pre-recorded course.
- Do NOT invent other curriculum details. Do NOT mention: prices, the e-book, 1:1 coaching, the masterclass, discount codes.

## Audience & tone
Home gardeners and would-be gardeners, 25–65, in/around Alameda (zone 10a): first-time homeowners, renters with balconies, parents, retirees. Many are overwhelmed by conflicting advice, embarrassed about dead plants, or suspicious that "free" means a pitch.
Voice: warm, encouraging, down-to-earth, practical — a knowledgeable neighbor, not a lecturer. Write to **you**, from **we**, with contractions. Never shame, never gatekeep, never imply you need expensive gear or a big yard. No promises; say "most beginners find…" / "a simple rule that helps…".

## Pillars (rotate; max 2 days in a row per pillar; no topic/hook repeats within 30 days)
1. **tips** — soil, watering, sunlight, containers vs in-ground, raised beds, common mistakes, cheap starter setups
2. **seasonal** — what to sow / transplant / harvest THIS month in zone 10a (use config/calendar; say "in our area"; never state planting dates as universal)
3. **pov** — relatable hooks gardeners recognize
4. **myth** — quick diagnosis of a common problem + the real fix (identification + organic/cultural fixes only)
5. **class-preview** — what the class is, who it's for, what you leave with (use class/Jason photos + supplied testimonials)

## Slide rules
- 5–7 slides, 1080×1920. Slide 1 = hook that works with no caption. Last slide = soft CTA. The template prints "Save your spot — it's free" and "learnwithyarden.com" on the CTA slide, so the CTA body must NOT repeat the URL, "link in bio", or "register at…" — it describes the class in 1–2 sentences and stops. (Captions still say "link in bio".)
- Large type, high contrast, content inside the safe zone (template handles it). Nothing that looks tappable — no buttons.
- The swipe cue "(SWIPE LEFT TO WATCH)" appears centered on slide 1 only; no cue on any other slide (template enforces this).
- Slide text must never overlap the swipe cue. The template reserves a strip above it; keep hook text under ~90 characters and bodies under ~240 so nothing overflows into that strip. After rendering, check slide 1 and any dense slide.
- No "Free in-person class · Alameda, CA" pill/badge on any slide. Mention the class in slide text or on the CTA slide instead.
- The Yarden wordmark appears ONLY on the CTA (last) slide. Middle slides carry no logo; a class mention in the text is fine.
- Library photos appear ONLY on the first slide (as a full-bleed "photo-hook") or the CTA slide — never on middle slides.
- DEFAULT TO PHOTOS: slide 1 should be a "photo-hook" using a library photo whenever any photo plausibly fits the topic (match on tags, crops, season, or just "a real Yarden bed/harvest"); use the plain gradient hook only when nothing in the library suits. The CTA slide should normally carry a "Gardening Instructor" photo of Jason (rotate among the four). Aim for photos on roughly 4 out of 5 posts; vary which photos are used across days.
- Photos: only from assets/photos (photos.json). Caption a photo only as its "subject" says. stockLike photos are never "our garden". Never generate or pull images and present them as ours.

## Accuracy guardrails
- No made-up statistics, testimonials, student quotes, or harvest results.
- Seasonal advice must be correct for today's date in zone 10a / Alameda; flag region-dependence.
- No pesticide, herbicide, or fertilizer dosing; no product-specific chemical recommendations.
- No claims about foraging, medicinal uses, or edibility of wild/ornamental plants.

## Supplied testimonials (verbatim; attribute as shown; use only these)
- "Thank you so much for sharing your gift with us yesterday. Yesterday to my surprise when I got home from class, my husband surprised me with raised beds and all the tools I need to start my outdoor garden." — Katrina L., class attendee
- "This is a great class. You will learn a lot. How do I know, you ask? Because I took the class and so delighted that I did. I have pages of notes and a much better understanding of how to transplant, feed and water my plants." — JWebb Fotos, class attendee (may be trimmed with an ellipsis, never reworded)
- "This class is just incredible. The whole time I've been mind-blown, taking tons of notes. What an inspiration, knowledge, kindness and a beautiful journey." — Valerie H., class attendee (omit the "yard visit" sentence — it refers to a paid service)

## Caption format (per platform)
Hook line → 1–3 short sentences of value → CTA: register for the free class, link in bio → 3–5 hashtags (broad + local: #alamedaca #bayareagardening #zone10agardening #eastbaygardening). Facebook may include the URL in text. TikTok caption short.

## Files
- `template.html` — brand template (tokens from the Yarden design system). `render_slides.py` — JSON spec → PNGs. `publish_buffer.py` — Buffer GraphQL publisher (`--check`, `--dry-run`). `assets/photos/photos.json` — photo library. `samples/` — approved sample specs.
- State lives in the pipeline artifact's database: `config/settings`, `config/calendar`, `backlog/*`, `posts/*`, `errors/*`.
