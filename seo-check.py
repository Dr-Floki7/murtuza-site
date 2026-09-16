import io, json, re, sys, os
sys.stdout.reconfigure(encoding="utf8")

s = io.open("index.html", encoding="utf8").read()

m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
assert m, "no JSON-LD block found"
d = json.loads(m.group(1))
print("JSON-LD parses OK. nodes:", ", ".join(n["@type"] for n in d["@graph"]))

# Google: do not mark up content that is not visible to the user.
body = re.sub(r"<script.*?</script>", "", s, flags=re.S)
body_text = re.sub(r"<[^>]+>", " ", body)
body_text = re.sub(r"\s+", " ", body_text)

faq = [x for x in d["@graph"] if x["@type"] == "FAQPage"][0]
print("FAQ questions in schema:", len(faq["mainEntity"]))

bad = []
for q in faq["mainEntity"]:
    # the visible page phrases these in second person; compare on a distinctive fragment
    frag = q["name"].replace("Murtuza Bharmal ", "").replace("did a dentist", "did a dentist")
    key = re.sub(r"^(Why|Which|What|Is|Are)\s+", "", frag).rstrip("?")
    key = key.replace("has ", "").replace("you ", "")
    probe = key.split()[:4]
    if not all(w.strip(",.?") in body_text for w in probe):
        bad.append(q["name"])
print("schema questions with no visible counterpart:", bad if bad else "none")

# answers must also appear on the page
missing_ans = []
for q in faq["mainEntity"]:
    a = q["acceptedAnswer"]["text"]
    probe = " ".join(a.split()[:6])
    if probe not in body_text:
        missing_ans.append(probe)
print("schema answers not found verbatim on page:", missing_ans if missing_ans else "none")

# heading order sanity
heads = re.findall(r"<h([1-3])[^>]*>", body)
print("heading sequence:", "".join(heads))
print("  h1 count:", heads.count("1"), "(must be 1)")

print()
for f in ("robots.txt", "sitemap.xml", "llms.txt", "index.html"):
    n = io.open(f, encoding="utf8").read().count("SITE_URL")
    print(f"{f}: {n} SITE_URL placeholder(s) to swap at deploy")

print()
print("alt/aria on the video:", "aria-hidden" in re.search(r"<video[^>]*>", s).group(0))
print("lang attribute:", re.search(r'<html lang="([^"]+)"', s).group(1))
print("canonical:", bool(re.search(r'rel="canonical"', s)))
print("og:image declared:", bool(re.search(r'property="og:image"', s)))
