#!/usr/bin/env python3
"""Add a correct URL for rows whose "html link" starts with "papers/".

Usage: python3 fix_links.py papers.csv papers_with_urls.csv
"""
import csv
import difflib
import re
import sys
import time
import xml.etree.ElementTree as ET

import requests

MAILTO = "juan.garrahan@nottingham.ac.uk"   # your email, for Crossref's polite pool
THRESHOLD = 0.90             # title similarity needed to accept a match
REPLACE = False              # True: overwrite "html link"; False: add a "url" column
ATOM = "{http://www.w3.org/2005/Atom}"


def norm(s):
    return " ".join(re.sub(r"[^\w\s]", " ", s.lower()).split())


def score(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def year_of(reference):
    years = re.findall(r"\b(?:19|20)\d{2}\b", reference)
    return years[-1] if years else ""


def crossref(title, authors, year):
    r = requests.get(
        "https://api.crossref.org/works",
        params={
            "query.bibliographic": f"{title} {year}".strip(),
            "query.author": authors,
            "rows": 5,
            "select": "DOI,title",
            "mailto": MAILTO,
        },
        timeout=30,
    )
    r.raise_for_status()
    best = ("", "", 0.0)
    for item in r.json()["message"]["items"]:
        cand = (item.get("title") or [""])[0]
        s = score(title, cand)
        if s > best[2]:
            best = (f"https://doi.org/{item['DOI']}", cand, s)
    return best


def arxiv(title):
    r = requests.get(
        "http://export.arxiv.org/api/query",
        params={"search_query": f'ti:"{norm(title)}"', "max_results": 3},
        timeout=30,
    )
    r.raise_for_status()
    best = ("", "", 0.0)
    for entry in ET.fromstring(r.text).findall(f"{ATOM}entry"):
        cand = " ".join(entry.find(f"{ATOM}title").text.split())
        url = re.sub(r"v\d+$", "", entry.find(f"{ATOM}id").text.strip())
        s = score(title, cand)
        if s > best[2]:
            best = (url.replace("http://", "https://"), cand, s)
    return best


def main(src, dst):
    with open(src, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames)

    new_cols = ["url", "url_source", "match_score", "matched_title"]
    fields += [c for c in new_cols if c not in fields]

    todo = [r for r in rows if r["html link"].strip().startswith("papers/")]
    print(f"{len(todo)} of {len(rows)} rows need a new URL")

    for n, row in enumerate(todo, 1):
        title, authors = row["title"].strip(), row["authors"].strip()
        year = year_of(row["reference"])
        url, source, matched, s = "", "", "", 0.0

        try:
            u, m, sc = crossref(title, authors, year)
            matched, s = m, sc
            if sc >= THRESHOLD:
                url, source = u, "crossref"
        except requests.RequestException as e:
            print(f"  crossref error: {e}", file=sys.stderr)

        if not url:
            try:
                time.sleep(3)      # arXiv asks for ~3 s between requests
                u, m, sc = arxiv(title)
                if sc >= THRESHOLD:
                    url, source, matched, s = u, "arxiv", m, sc
                elif sc > s:
                    matched, s = m, sc
            except (requests.RequestException, ET.ParseError) as e:
                print(f"  arxiv error: {e}", file=sys.stderr)

        row.update(url=url, url_source=source,
                   match_score=f"{s:.2f}", matched_title=matched)
        if REPLACE and url:
            row["html link"] = url
        print(f"[{n}/{len(todo)}] {source or 'none':8} {s:.2f}  {title[:60]}")
        time.sleep(0.2)

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])