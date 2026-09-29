#!/usr/bin/env python3
"""Turn a CSV of old links and new URLs into a batch-replacer text file.

For each row with a non-empty "url", writes:

    replace "[html link]"
    with "[url]"
    <blank line>

Usage: python for_batch_replacer.py papers_with_urls.csv replacements.txt
"""
import csv
import sys


def main(src, dst):
    written = skipped = 0

    with open(src, newline="", encoding="utf-8-sig") as f, \
         open(dst, "w", encoding="utf-8", newline="\n") as out:
        for row in csv.DictReader(f):
            old = row["html link"].strip()
            new = row["url"].strip()
            if not old or not new:
                skipped += 1
                continue
            out.write(f'replace "{old}"\n')
            out.write(f'with "{new}"\n')
            out.write("\n")
            written += 1

    print(f"{written} replacements written to {dst}; {skipped} rows skipped (no url or no html link)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])