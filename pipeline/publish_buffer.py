#!/usr/bin/env python3
"""Publish a rendered Yarden slideshow to TikTok, Facebook and Instagram through Buffer's GraphQL API.

Usage:
  python3 publish_buffer.py spec.json urls.json [--dry-run] [--mode shareNow|addToQueue]
  python3 publish_buffer.py --check            # verify token + list channels, no posting

spec.json  : the slideshow spec (needs "caption": {instagram, facebook, tiktok} and slides[0].text as the hook)
urls.json  : {"urls": ["https://raw.githubusercontent.com/.../slide-01.png", ...]} — public image URLs in slide order

Env: BUFFER_ACCESS_TOKEN (required unless --dry-run).
Exit code 0 = every channel accepted; 2 = at least one channel failed (details in stdout JSON). Never retries.
"""
import json, os, sys, re, time, urllib.request, urllib.error

API = "https://api.buffer.com"
SERVICES = ("tiktok", "facebook", "instagram")

def gql(token, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {token}", "User-Agent": "yarden-social-pipeline/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:500].decode(errors='replace')}")
    if data.get("errors"):
        raise RuntimeError("GraphQL errors: " + json.dumps(data["errors"])[:800])
    return data["data"]

def channels(token):
    orgs = gql(token, "query { account { organizations { id name } } }")["account"]["organizations"]
    out = []
    for o in orgs:
        for c in gql(token, 'query($o: OrganizationId!) { channels(input: { organizationId: $o }) { id name service } }', {"o": o["id"]})["channels"]:
            out.append({**c, "organization": o["name"]})
    return out

def pick_channels(all_channels):
    picked = {}
    for s in SERVICES:
        matches = [c for c in all_channels if str(c.get("service", "")).lower() == s]
        if len(matches) == 1:
            picked[s] = matches[0]
        elif len(matches) > 1:
            wanted = os.environ.get(f"BUFFER_{s.upper()}_CHANNEL_ID")
            m = [c for c in matches if c["id"] == wanted]
            picked[s] = m[0] if m else None
        else:
            picked[s] = None
    return picked

CREATE = """
mutation Create($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt status } }
    ... on MutationError { message }
  }
}"""

def build_input(service, channel_id, spec, urls, mode):
    cap = spec["caption"]
    text = cap.get(service) or cap.get("instagram")
    hook = re.sub(r"<[^>]+>", "", spec["slides"][0]["text"])
    assets = [{"image": {"url": u, "metadata": {"altText": f"Slide {i+1} of a Yarden gardening tip"}}} for i, u in enumerate(urls)]
    inp = {"text": text, "channelId": channel_id, "schedulingType": "automatic", "mode": mode, "assets": assets}
    if service == "instagram":
        inp["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
    elif service == "facebook":
        inp["metadata"] = {"facebook": {"type": "post"}}
    elif service == "tiktok":
        inp["metadata"] = {"tiktok": {"title": hook[:90]}}
    return inp

def main(argv):
    dry = "--dry-run" in argv
    mode = "shareNow"
    if "--mode" in argv:
        mode = argv[argv.index("--mode") + 1]
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if "--check" in argv:
        if not token:
            print(json.dumps({"ok": False, "error": "BUFFER_ACCESS_TOKEN not set"})); return 2
        ch = channels(token)
        print(json.dumps({"ok": True, "channels": ch, "picked": {k: (v or {}).get("id") for k, v in pick_channels(ch).items()}}, indent=2)); return 0
    args = [a for a in argv if not a.startswith("--") and a not in (mode,)]
    spec = json.load(open(args[0])); urls = json.load(open(args[1]))["urls"]
    assert 5 <= len(urls) <= 7, "need 5-7 slide URLs"
    results = {}
    if dry:
        for s in SERVICES:
            results[s] = {"dryRun": True, "input": build_input(s, "<channel>", spec, urls, mode)}
        print(json.dumps({"ok": True, "dryRun": True, "results": results}, indent=2)); return 0
    if not token:
        print(json.dumps({"ok": False, "error": "BUFFER_ACCESS_TOKEN not set"})); return 2
    picked = pick_channels(channels(token))
    ok = True
    for s in SERVICES:
        c = picked.get(s)
        if not c:
            results[s] = {"ok": False, "error": f"no unique {s} channel connected in Buffer (set BUFFER_{s.upper()}_CHANNEL_ID if several)"}; ok = False; continue
        try:
            res = gql(token, CREATE, {"input": build_input(s, c["id"], spec, urls, mode)})["createPost"]
            if res.get("post"):
                results[s] = {"ok": True, "postId": res["post"]["id"], "dueAt": res["post"].get("dueAt"), "status": res["post"].get("status"), "channel": c["name"]}
            else:
                results[s] = {"ok": False, "error": res.get("message", "unknown MutationError"), "channel": c["name"]}; ok = False
        except Exception as e:
            results[s] = {"ok": False, "error": str(e), "channel": c["name"]}; ok = False
        time.sleep(1)
    print(json.dumps({"ok": ok, "results": results}, indent=2))
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
