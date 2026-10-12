#!/usr/bin/env python3
"""Consistency check for the static site in public/. Run: python3 scripts/check-site.py

Exits 1 if any page's head metadata, JSON-LD, sitemap, llms.txt or manifest has
drifted out of step with the site content. Safe to run any time; changes nothing.
"""
import glob, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
os.chdir(ROOT)
BASE = "https://certonymity.com"
COMPANY_NUMBER = "16871742"
problems = []


def bad(where, msg):
    problems.append(f"{where}: {msg}")


def meta(s, attr, val):
    m = re.search(r'<meta[^>]+%s="%s"[^>]+content="([^"]*)"' % (attr, re.escape(val)), s)
    return m.group(1) if m else None


def page_url(path):
    if path == "index.html":
        return BASE + "/"
    if path.endswith("/index.html"):
        return BASE + "/" + path[: -len("index.html")]
    return BASE + "/" + path[: -len(".html")]  # clean URL via _redirects


sitemap = open("sitemap.xml").read()
sitemap_urls = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
llms = open("llms.txt").read()
pages = sorted(glob.glob("**/*.html", recursive=True))
canonicals = set()

for p in pages:
    s = open(p).read()
    title = (re.search(r"<title>(.*?)</title>", s) or [None, None])[1]
    desc = meta(s, "name", "description")
    canon = (re.search(r'rel="canonical" href="([^"]*)"', s) or [None, None])[1]
    og = {k: meta(s, "property", k) for k in ("og:title", "og:description", "og:url", "og:image")}
    tw = {k: meta(s, "name", k) for k in ("twitter:card", "twitter:title", "twitter:description", "twitter:image")}

    if not title: bad(p, "missing <title>")
    if not desc: bad(p, "missing meta description")
    elif len(desc) > 160: bad(p, f"meta description is {len(desc)} chars (max 160)")
    if not canon: bad(p, "missing canonical")
    else:
        canonicals.add(canon)
        if canon != page_url(p): bad(p, f"canonical {canon} != expected {page_url(p)}")
        if canon not in sitemap_urls: bad(p, "canonical not in sitemap.xml")
        if og["og:url"] != canon: bad(p, "og:url != canonical")
    for k, v in {**og, **tw}.items():
        if not v: bad(p, f"missing {k}")
    if title and og["og:title"] != title: bad(p, "og:title != <title>")
    if title and tw["twitter:title"] != title: bad(p, "twitter:title != <title>")
    if desc and og["og:description"] != desc: bad(p, "og:description != meta description")
    if desc and tw["twitter:description"] != desc: bad(p, "twitter:description != meta description")
    if not re.search(r"<html lang=", s): bad(p, "missing html lang")
    if len(re.findall(r"<h1\b", s)) != 1: bad(p, f"expected exactly one <h1>, found {len(re.findall(r'<h1', s))}")
    blocks = re.findall(r'ld\+json">(.*?)</script>', s, re.S)
    if not blocks: bad(p, "missing JSON-LD")
    for b in blocks:
        try: json.loads(b)
        except Exception as e: bad(p, f"invalid JSON-LD ({e})")
    # wrong brand capitalisation in visible copy
    visible = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", s, flags=re.S)
    for wrong in ("C.Email", "Cdot", "CDot", "cdot "):
        if re.search(r"(?<![\w.])%s(?!\w)" % re.escape(wrong.strip()), visible) and wrong.strip() != "cdot":
            bad(p, f"brand capitalisation: found '{wrong.strip()}' (use c.Email / cDot)")
    # internal links resolve
    for href in re.findall(r'href="([^"#?]+)', s):
        if re.match(r"(https?:|mailto:|tel:|//)", href): continue
        target = os.path.normpath(os.path.join(os.path.dirname(p), href.lstrip("/") if href.startswith("/") else href)) if not href.startswith("/") else href.lstrip("/")
        if href.startswith("/") and href == "/": continue
        cands = [target, target + ".html", os.path.join(target, "index.html")]
        if href in ("../", "./") or target in ("", "."): continue
        if not any(os.path.exists(c) for c in cands): bad(p, f"broken internal link {href}")

# sitemap entries must exist as pages
for u in sitemap_urls:
    if u not in {page_url(p) for p in pages}: bad("sitemap.xml", f"{u} has no matching page")

# llms.txt: every sitemap URL is linked, and company number matches
for u in sitemap_urls:
    if u not in llms: bad("llms.txt", f"does not mention {u}")
for u in ("https://c.email/llms.txt", "https://cdot.world/llms.txt"):
    if u not in llms: bad("llms.txt", f"missing link to {u}")
if COMPANY_NUMBER not in llms: bad("llms.txt", "company number missing/different")
if not os.path.exists("robots.txt") or "Sitemap:" not in open("robots.txt").read(): bad("robots.txt", "missing or no Sitemap line")

# company facts present where expected
for p in ("contact/index.html",):
    if COMPANY_NUMBER not in open(p).read(): bad(p, "company number missing/different")

# manifest
mf = json.load(open("site.webmanifest"))
if mf.get("name") != "Certonymity": bad("site.webmanifest", f"name is {mf.get('name')!r}, expected 'Certonymity'")

# redirects point at real things
for line in open("_redirects"):
    parts = line.split()
    if len(parts) >= 3 and parts[2] == "200" and not parts[1].startswith(("http", "/well-known", "/index")) and parts[0] != "/*":
        if not os.path.exists(parts[1].lstrip("/")): bad("_redirects", f"{parts[1]} does not exist")

if problems:
    print(f"{len(problems)} problem(s):")
    for x in problems: print("  -", x)
    sys.exit(1)
print(f"OK: {len(pages)} pages, {len(sitemap_urls)} sitemap URLs, llms.txt, robots.txt, manifest all consistent.")
