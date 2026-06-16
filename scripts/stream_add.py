#!/usr/bin/env python3
"""Append entries to _data/stream.yml.

Two modes:

  collection <file> [<file> ...]
      Each file is a newly-added collection document (_posts/_notes/
      _photos/_reviews). The entry stores the document's type, a `ref`
      (its repo-relative path) and its `title`. The layout renders a
      colour-coded type tag then the title, and resolves the live URL
      from `ref` so slugs can never drift.

  inbox <file> [<file> ...]
      Each file is a mobile-capture note from stream_inbox/. It is
      converted into a `_thoughts/<date>-<stem>.md` collection document
      and the inbox file is deleted; the new paths print to stdout so
      the workflow can pipe them into the subsequent `collection` step.
      `type: quote` shorthand composes the body into a
      `{% include quote.html %}` call; `comment:` becomes prose above it.

Dates: a YYYY-MM-DD filename prefix wins (matches how Jekyll dates
posts/notes); otherwise the file's first-commit date; otherwise now.

Pure standard library so it runs on a bare GitHub Actions runner.
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREAM_FILE = os.path.join(REPO_ROOT, "_data", "stream.yml")

# collection directory -> stream entry type. The layout renders a
# colour-coded tag from the type, then the document's title.
COLLECTION_TYPES = {
    "_posts": "post",
    "_notes": "note",
    "_photos": "photo",
    "_reviews": "review",
}
# Thoughts intentionally NOT in COLLECTION_TYPES: the stream layout
# reads `site.thoughts` directly, so they don't need stream.yml entries.
THOUGHTS_DIR = os.path.join(REPO_ROOT, "_thoughts")

DATE_PREFIX_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})-")
SYDNEY_NOON = "T12:00:00+10:00"


def yaml_quote(value):
    """Emit a YAML double-quoted scalar; newlines become \\n."""
    text = str(value)
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return '"' + text + '"'


def parse_front_matter(path):
    """Return (front_matter_dict, body_str). Tolerates a missing block."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    fm, body = {}, raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            body = parts[2].strip()
            for line in parts[1].splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    fm[key.strip()] = val.strip().strip("'\"")
    return fm, body


# A Kramdown Inline Attribute List on its own line, e.g. `{: .blurb}`
# or `{: .blurb #id .other}`. It renders normally on the page (just
# adds the class) and marks the paragraph directly above it as the
# stream blurb — no commenting-out, no duplication.
IAL_RE = re.compile(r"^\{:.*\}$")
BLURB_CLASS_RE = re.compile(r"\.blurb(?![\w-])")


def extract_blurb(body, is_photo):
    """Stream content for a collection item, or None.

    A paragraph tagged with a `{: .blurb}` Kramdown IAL wins for any
    type. Photo pages have no tag but a reliable prose intro, so fall
    back to their first paragraph (skipped if it opens with Liquid/HTML).
    """
    lines = body.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if IAL_RE.match(stripped) and BLURB_CLASS_RE.search(stripped):
            # The blurb is the contiguous block of non-blank lines
            # directly above the IAL (Kramdown applies an IAL to the
            # block it immediately follows).
            para = []
            j = i - 1
            while j >= 0 and lines[j].strip():
                para.insert(0, lines[j].rstrip())
                j -= 1
            text = "\n".join(para).strip()
            if text:
                return text
    if is_photo:
        first = body.strip().split("\n\n", 1)[0].strip()
        if first and not first.startswith(("{%", "{{", "<")):
            return first
    return None


# A `<!-- stream-quote -->` line directly above a `{% include
# quote.html ... %}` marks that quote for the stream. The include
# still renders normally on the page; the comment shows nothing.
QUOTE_MARK_RE = re.compile(
    r"<!--\s*stream-quote\s*-->\s*"
    r"\{%-?\s*include\s+quote\.html\b(.*?)-?%\}",
    re.S | re.I)
QUOTE_ARG_RE = re.compile(
    r"""(\w+)\s*=\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')""",
    re.S)


def extract_quote(body):
    """Lift a marked `quote.html` include into a stream quote map.

    Maps the include's args to the stream schema: content->text,
    title->source, author/link/book unchanged. None if no marker.
    """
    m = QUOTE_MARK_RE.search(body)
    if not m:
        return None
    args = {}
    for am in QUOTE_ARG_RE.finditer(m.group(1)):
        raw = am.group(2) if am.group(2) is not None else am.group(3)
        raw = (raw.replace('\\"', '"').replace("\\'", "'")
                  .replace("\\\\", "\\"))
        args[am.group(1)] = raw.strip()
    if not args.get("content"):
        return None
    quote = {"text": args["content"]}
    if args.get("author"):
        quote["author"] = args["author"]
    if args.get("title"):
        quote["source"] = args["title"]
    if args.get("link"):
        quote["link"] = args["link"]
    if args.get("book"):
        quote["book"] = args["book"]
    return quote


def git_added_date(rel_path):
    """First-commit ISO date for a tracked file, or None."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow",
             "--format=%aI", "-1", "--", rel_path],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def published_date(value):
    """Parse a review's `published:` field, e.g. '13 April 2025'."""
    try:
        d = datetime.strptime(value.strip(), "%d %B %Y")
        return f"{d:%Y-%m-%d}{SYDNEY_NOON}"
    except (ValueError, AttributeError):
        return None


def resolve_date(rel_path, fm=None):
    # A review's authoritative date is its `published:` field; the
    # filename has no date prefix and git dates were rewritten.
    if fm and fm.get("published"):
        from_published = published_date(fm["published"])
        if from_published:
            return from_published
    base = os.path.basename(rel_path)
    m = DATE_PREFIX_RE.match(base)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}{SYDNEY_NOON}"
    return git_added_date(rel_path) or datetime.now(timezone.utc).isoformat()


def rel(path):
    return os.path.relpath(os.path.abspath(path), REPO_ROOT)


def collection_entry(path):
    rel_path = rel(path)
    top = rel_path.split(os.sep)[0]
    if top not in COLLECTION_TYPES:
        return None
    item_type = COLLECTION_TYPES[top]
    fm, body = parse_front_matter(path)
    # Redirect posts that just point at a photo gallery or a book review
    # double-count: that gallery/review already has its own stream entry.
    # Skip them. Other redirects (e.g. -> nba.ben.report) still post.
    redirect_to = fm.get("redirect_to") or ""
    if fm.get("layout") == "redirect" and (
            "/photos/" in redirect_to or "/books/" in redirect_to):
        sys.stderr.write(f"skip (gallery/review redirect): {rel_path}\n")
        return None
    # reviews title lives in `book:`; everything else in `title:`
    title = fm.get("title") or fm.get("book")
    if not title:
        sys.stderr.write(f"skip (no title): {rel_path}\n")
        return None
    entry = {
        "date": resolve_date(rel_path, fm),
        "type": item_type,
        "ref": rel_path,
        "title": title,
    }
    content = extract_blurb(body, item_type == "photo")
    if content:
        entry["content"] = content
    quote = extract_quote(body)
    if quote:
        entry["quote"] = quote
    return entry


def liquid_squote(value):
    """Escape a value for use inside a Liquid single-quoted string."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def inbox_to_thought_file(path):
    """Convert one stream_inbox/<x>.md into _thoughts/<date>-<stem>.md.

    Plain thoughts: the body is kept verbatim. `type: quote` shorthand:
    the body is composed into a `{% include quote.html %}` call (with
    any `comment:` rendered as prose above it). The original inbox
    file is deleted. Returns the new repo-relative path.
    """
    fm, body = parse_front_matter(path)
    date_iso = git_added_date(rel(path)) or datetime.now(timezone.utc).isoformat()
    stem = os.path.splitext(os.path.basename(path))[0]
    if not DATE_PREFIX_RE.match(stem):
        stem = f"{date_iso[:10]}-{stem}"
    target = os.path.join(THOUGHTS_DIR, f"{stem}.md")

    if fm.get("type") == "quote":
        # quote.html's content<-body, title<-source; author/link/book pass through.
        include_args = [("content", body.strip())]
        for fk, ik in (("author", "author"), ("source", "title"),
                       ("link", "link"), ("book", "book")):
            if fm.get(fk):
                include_args.append((ik, fm[fk]))
        include = "{% include quote.html\n"
        include += "".join(f"  {k}='{liquid_squote(v)}'\n" for k, v in include_args)
        include += "%}"
        parts = []
        if fm.get("comment"):
            parts.append(fm["comment"].strip())
        parts.append(include)
        out_body = "\n\n".join(parts)
    else:
        out_body = body.strip()

    # Front matter — Jekyll needs the `---` fences to process the doc;
    # carry through `title`/`url` if the inbox file set them.
    fm_lines = ["---"]
    for k in ("title", "url"):
        if fm.get(k):
            fm_lines.append(f"{k}: {yaml_quote(fm[k])}")
    fm_lines.append("---")
    content = "\n".join(fm_lines) + "\n\n" + out_body + "\n"

    os.makedirs(THOUGHTS_DIR, exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(content)
    os.remove(path)
    return rel(target)


# `text` is now only ever a quote sub-key; the entry body is `content`.
ORDER = ["date", "type", "ref", "url", "title", "content", "quote"]
QUOTE_SUBORDER = ["text", "author", "source", "link", "book"]


def render(entry):
    lines = []
    for i, key in enumerate(k for k in ORDER if k in entry):
        prefix = "- " if i == 0 else "  "
        val = entry[key]
        if isinstance(val, dict):
            # nested map (e.g. an attached quote); `key` is never first,
            # so it sits at 2-space indent and sub-keys at 4.
            lines.append(f"{prefix}{key}:")
            for sk in QUOTE_SUBORDER:
                if sk in val:
                    lines.append(f"    {sk}: {yaml_quote(val[sk])}")
        else:
            lines.append(f"{prefix}{key}: {yaml_quote(val)}")
    return "\n".join(lines) + "\n"


def append(entries):
    entries = [e for e in entries if e]
    if not entries:
        return
    os.makedirs(os.path.dirname(STREAM_FILE), exist_ok=True)
    new = not os.path.exists(STREAM_FILE) or os.path.getsize(STREAM_FILE) == 0
    # A hand-edited file may not end in a newline; without this the new
    # entry's `- ` would be glued onto the last line, corrupting both.
    needs_nl = (not new) and not open(
        STREAM_FILE, "rb").read()[-1:] == b"\n"
    with open(STREAM_FILE, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# Activity stream. Append-only; the layout sorts by date.\n")
        elif needs_nl:
            fh.write("\n")
        for entry in entries:
            fh.write(render(entry))
    print(f"Appended {len(entries)} entry(ies) to {rel(STREAM_FILE)}")


def main(argv):
    if len(argv) < 3 or argv[1] not in ("collection", "inbox"):
        sys.exit("usage: stream_add.py {collection|inbox} <file> [<file> ...]")
    mode, files = argv[1], argv[2:]
    if mode == "collection":
        append([collection_entry(f) for f in files])
    else:
        # Convert each inbox file into a _thoughts/*.md doc. Print the
        # new paths to stdout so the workflow can feed them straight
        # into the subsequent `collection` step.
        for f in files:
            print(inbox_to_thought_file(f))


if __name__ == "__main__":
    main(sys.argv)
