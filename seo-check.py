"""Structural SEO/AEO checks on index.html.

Google's guidance is not to mark up content the visitor cannot see, so any FAQ schema
present must have a visible counterpart on the page. This asserts that rather than
assuming it.
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf8")

s = io.open("index.html", encoding="utf8").read()
fails = []

m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
assert m, "no JSON-LD block found"
import json
d = json.loads(m.group(1))
nodes = [n["@type"] for n in d["@graph"]]
print("JSON-LD parses OK. nodes:", ", ".join(nodes))

for required in ("ProfilePage", "WebSite", "Person"):
    if required not in nodes:
        fails.append(f"missing {required} node")

import html as _html

body = re.sub(r"<script.*?</script>", "", s, flags=re.S)
# entities must be decoded: the page writes "&amp;" where the schema says "&"
body_text = _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))

# FAQ schema is optional; if present, every question and answer must be visible.
faq = next((x for x in d["@graph"] if x["@type"] == "FAQPage"), None)
if faq is None:
    print("FAQPage: not present (fine — nothing claimed, nothing to verify)")
else:
    print(f"FAQPage: {len(faq['mainEntity'])} questions")
    for q in faq["mainEntity"]:
        probe = " ".join(q["acceptedAnswer"]["text"].split()[:6])
        if probe not in body_text:
            fails.append(f"schema answer not visible on page: {probe}")

# Person facts must also appear on the page.
person = next(x for x in d["@graph"] if x["@type"] == "Person")
print("\nPerson claims vs visible copy")
for field, probe in (
    ("name", person["name"]),
    ("jobTitle", person["jobTitle"]),
):
    ok = probe in body_text
    print(f"  {'ok ' if ok else 'FAIL'} {field}: {probe}")
    if not ok:
        fails.append(f"Person.{field} not visible: {probe}")

for edu in person["alumniOf"]:
    ok = edu["name"] in body_text
    print(f"  {'ok ' if ok else 'FAIL'} alumniOf: {edu['name']}")
    if not ok:
        fails.append(f"alumniOf not visible: {edu['name']}")

heads = re.findall(r"<h([1-3])[^>]*>", body)
print("\nheading sequence:", "".join(heads))
print("  h1 count:", heads.count("1"), "(must be 1)")
if heads.count("1") != 1:
    fails.append(f"h1 count is {heads.count('1')}, must be 1")

print("\ndocument basics")
checks = (
    ("lang attribute", bool(re.search(r'<html lang="[^"]+"', s))),
    ("canonical", 'rel="canonical"' in s),
    ("og:image", 'property="og:image"' in s),
    ("twitter:card", 'name="twitter:card"' in s),
    ("meta description", 'name="description"' in s),
    ("banner alt text", bool(re.search(r'class="banner__img"[^>]*alt="[^"]{40,}"', s, re.S))),
    ("video aria-hidden", bool(re.search(r"<video[^>]*aria-hidden", s))),
    ("skip link", 'class="skip"' in s),
    ("no stale placeholder", "SITE_URL" not in s),
    ("reduced-motion block", "prefers-reduced-motion" in s),
)
for label, ok in checks:
    print(f"  {'ok ' if ok else 'FAIL'} {label}")
    if not ok:
        fails.append(label)

print("\nmotion hooks")
for probe, label in (
    ("reveal-lines", "heading wipes"),
    ("data-words", "word reveals"),
    ("data-stagger", "staggered items"),
    ('class="ticker', "ticker"),
    ('pathLength="1"', "icon stroke draw"),
):
    n = s.count(probe)
    print(f"  {n:>3}x  {label}")
    if n == 0:
        fails.append(f"motion hook missing: {label}")

print()
if fails:
    print("FAILURES")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("All structural checks passed.")
