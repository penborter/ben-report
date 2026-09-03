#!/usr/bin/env python3
"""Sync finished books from the Google Sheets books list into _data/reading.yml.

The sheet has one tab per year, named after the year ("2026"). Each tab is
append-ordered (oldest read first) with `Title`, `Author`, `Stars`, `Start`,
`Finish` and `Fiction` columns; reading.yml lists each year newest-first, so
new rows are inserted at the *top* of the year's `books` list in reverse
sheet order. A row is only synced once it has a `Finish` date — rows without
one are still being read.

The sync is additive: entries already in reading.yml are never rewritten, so
hand-written `review:` prose, retitled entries and manual edits all survive.
Two guards stop an entry coming back after it has been edited or deleted:

  1. Every sheet row seen on a successful run is recorded in
     .github/reading-sync-state.json, keyed by year, so a row is only ever
     considered once.
  2. Failing that (state file lost), a row whose normalised title is already
     listed under that year in reading.yml is skipped. Scoped to the one year
     so a re-read still gets an entry in the year it was re-read.

Only `title`, `author` and `star` are written; `review:` stays hand-written.

Pure standard library so it runs on a bare GitHub Actions runner.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READING_FILE = os.path.join(REPO_ROOT, "_data", "reading.yml")
# The bookshelf page prints "last updated in <month>"; keep it honest.
BOOKS_PAGE = os.path.join(REPO_ROOT, "_pages", "books.html")
# Outside _data/ so Jekyll doesn't publish the bookkeeping as site data.
STATE_FILE = os.path.join(REPO_ROOT, ".github", "reading-sync-state.json")

# "Books List" — publicly readable, so no credentials are needed.
DEFAULT_SHEET_ID = "1Idpx-cMFO7R3ujF82r8mymCdrmCAf8JOJU373H-CqOg"

# Sheet stars run 1-4; 4 is what reading.yml renders as a starred favourite.
STAR_THRESHOLD = 4

# reading.yml indents two spaces per level: books sit at 6, their keys at 8.
ENTRY_INDENT = " " * 6
FIELD_INDENT = " " * 8

TITLE_LINE_RE = re.compile(r"^\s*-\s+title:\s*(.+?)\s*$")
YEAR_LINE_RE = re.compile(r"^(\s*)-\s+year:\s*[\"']?(\d{4})[\"']?\s*$")
UPDATED_LINE_RE = re.compile(r"^updated:\s*.*$", re.M)
# Punctuation varies between sheet and yaml ("Philip K Dick" / "Philip K.
# Dick"), so titles are compared on letters and digits alone.
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def sydney_now():
    """Now in Sydney, so the year rolls over when Ben's does."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Australia/Sydney"))
    except Exception:
        # No tzdata: +10 is close enough to pick the right year's tab.
        return datetime.now(timezone(timedelta(hours=10)))


def normalise(title):
    """Collapse a title to a comparison key: lowercase letters and digits."""
    return NON_ALNUM_RE.sub(" ", title.lower()).strip()


def yaml_scalar(value):
    """Emit `value` as a YAML scalar, quoting only when plain style is unsafe."""
    text = str(value).strip()
    unsafe = (
        not text
        or text[0] in "-?:,[]{}#&*!|>'\"%@`"
        or ": " in text
        or " #" in text
        or text.endswith(":")
    )
    if not unsafe:
        return text
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + text.replace("\n", "\\n").replace("\t", "\\t") + '"'


def fetch_csv(sheet_id, sheet_name):
    """Download one tab of a public sheet as CSV via the gviz endpoint."""
    query = urllib.parse.urlencode(
        {"tqx": "out:csv", "headers": "1", "sheet": sheet_name}
    )
    url = "https://docs.google.com/spreadsheets/d/%s/gviz/tq?%s" % (sheet_id, query)
    request = urllib.request.Request(url, headers={"User-Agent": "ben-report-sync"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise SystemExit(
            "Sheet fetch failed (HTTP %s). Check the sheet is shared as "
            "'Anyone with the link can view' and that a tab named %r exists."
            % (error.code, sheet_name)
        )
    except urllib.error.URLError as error:
        raise SystemExit("Sheet fetch failed: %s" % error.reason)
    # An unshared sheet answers 200 with a sign-in page rather than CSV.
    if body.lstrip().startswith(("<", "/*O_o*/")):
        raise SystemExit(
            "Sheet fetch returned a page, not CSV. The sheet is probably not "
            "shared as 'Anyone with the link can view', or the tab named %r "
            "does not exist." % sheet_name
        )
    return body


def parse_rows(text):
    """Rows of the year tab as dicts, in sheet order (oldest read first)."""
    rows = list(csv.reader(io.StringIO(text)))
    header_index = None
    for index, row in enumerate(rows):
        cells = [cell.strip().lower() for cell in row]
        if "title" in cells and "author" in cells:
            header_index = index
            break
    if header_index is None:
        raise SystemExit("No 'Title'/'Author' header row found in the sheet tab.")

    columns = {}
    for position, cell in enumerate(rows[header_index]):
        name = cell.strip().lower()
        if name and name not in columns:
            columns[name] = position

    def cell(row, name):
        position = columns.get(name)
        if position is None or position >= len(row):
            return ""
        return row[position].strip()

    books = []
    for row in rows[header_index + 1 :]:
        title = cell(row, "title")
        if not title:
            continue
        books.append(
            {
                "title": title,
                "author": cell(row, "author"),
                "stars": cell(row, "stars"),
                "finish": cell(row, "finish"),
            }
        )
    return books


def is_starred(stars):
    try:
        return float(stars) >= STAR_THRESHOLD
    except ValueError:
        return False


def existing_titles(text, year):
    """Normalised titles already listed under `year` in reading.yml.

    Scoped to the one year on purpose: a re-read gets its own entry in the
    year it was re-read (see Anathem, 2025 and 2026), so matching across the
    whole file would silently drop it.
    """
    keys = set()
    current = None
    for line in text.splitlines():
        year_match = YEAR_LINE_RE.match(line)
        if year_match:
            current = year_match.group(2)
            continue
        if current != year:
            continue
        match = TITLE_LINE_RE.match(line)
        if not match:
            continue
        value = match.group(1)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        keys.add(normalise(value))
    return keys


def render_entry(book):
    """One reading.yml book entry; `review:` is left for Ben to write."""
    lines = ["%s- title: %s" % (ENTRY_INDENT, yaml_scalar(book["title"]))]
    if book["author"]:
        lines.append("%sauthor: %s" % (FIELD_INDENT, yaml_scalar(book["author"])))
    if is_starred(book["stars"]):
        lines.append("%sstar: yes" % FIELD_INDENT)
    return lines


def insert_books(text, year, books):
    """Splice entries in at the top of `year`'s list, creating the year if new.

    Text splicing rather than a YAML round-trip: reading.yml is hand-formatted
    (blank lines between older entries, unquoted prose, `link:` fields on
    early years) and re-dumping it would rewrite the whole file.
    """
    if not books:
        return text

    lines = text.splitlines()
    entries = []
    for book in books:
        entries.extend(render_entry(book))

    for index, line in enumerate(lines):
        match = YEAR_LINE_RE.match(line)
        if not match or match.group(2) != year:
            continue
        for offset in range(index + 1, len(lines)):
            if lines[offset].strip() == "books:":
                return "\n".join(
                    lines[: offset + 1] + entries + lines[offset + 1 :]
                ) + "\n"
        raise SystemExit("Year %s in reading.yml has no 'books:' key." % year)

    # New year: reading.yml lists years newest-first, so it goes on top.
    for index, line in enumerate(lines):
        if line.strip() == "years:":
            block = ['  - year: "%s"' % year, "    books:"] + entries
            return "\n".join(lines[: index + 1] + block + lines[index + 1 :]) + "\n"
    raise SystemExit("reading.yml has no top-level 'years:' key.")


def touch_updated(when):
    """Refresh `updated:` in the bookshelf page's front matter."""
    stamp = "%s %d" % (when.strftime("%B"), when.year)
    with open(BOOKS_PAGE, encoding="utf-8") as handle:
        text = handle.read()
    updated, count = UPDATED_LINE_RE.subn("updated: " + stamp, text, count=1)
    if count and updated != text:
        with open(BOOKS_PAGE, "w", encoding="utf-8") as handle:
            handle.write(updated)


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--year", help="Sheet tab to sync (default: the current year in Sydney)."
    )
    parser.add_argument(
        "--sheet-id",
        default=os.environ.get("READING_SHEET_ID", DEFAULT_SHEET_ID),
        help="Google Sheets file id.",
    )
    parser.add_argument(
        "--csv-file", help="Read a saved CSV export instead of fetching the sheet."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be added without writing any files.",
    )
    args = parser.parse_args(argv[1:])

    now = sydney_now()
    year = args.year or str(now.year)

    if args.csv_file:
        with open(args.csv_file, encoding="utf-8") as handle:
            csv_text = handle.read()
    else:
        csv_text = fetch_csv(args.sheet_id, year)

    rows = parse_rows(csv_text)
    finished = [row for row in rows if row["finish"]]
    print(
        "Sheet %s: %d rows, %d finished." % (year, len(rows), len(finished)),
        file=sys.stderr,
    )

    state = load_state()
    synced = set(state.get(year, []))
    with open(READING_FILE, encoding="utf-8") as handle:
        reading_text = handle.read()
    known = existing_titles(reading_text, year)

    new_books = []
    seen = set()
    for row in finished:
        key = normalise(row["title"])
        if key in seen or key in synced or key in known:
            continue
        seen.add(key)
        new_books.append(row)

    if not new_books:
        print("No new books.", file=sys.stderr)
        return 0

    for book in new_books:
        print("Adding: %s — %s" % (book["title"], book["author"] or "?"), file=sys.stderr)

    # Sheet order is oldest-first; reversing puts the most recent read on top.
    updated = insert_books(reading_text, year, list(reversed(new_books)))

    if args.dry_run:
        print("Dry run: %d book(s) not written." % len(new_books), file=sys.stderr)
        return 0

    with open(READING_FILE, "w", encoding="utf-8") as handle:
        handle.write(updated)
    touch_updated(now)

    # Record every finished row, not just the new ones, so the state stays
    # authoritative even if reading.yml is edited by hand afterwards.
    state[year] = sorted(synced | {normalise(row["title"]) for row in finished})
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
