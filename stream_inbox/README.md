# stream_inbox

Drop folder for capturing thoughts and quotes into the stream from your
phone. Create **one new Markdown file per entry** here (any filename, e.g.
`2026-05-17-1930.md`) — from the GitHub mobile app's "Create new file",
no token needed.

On push, `.github/workflows/stream.yml` converts each file into a
`_thoughts/<YYYY-MM-DD>-<stem>.md` collection doc and deletes the
inbox file. The stream layout reads `site.thoughts` directly, so no
`_data/stream.yml` entry is created — the file IS the source of truth.
The entry's date is the YYYY-MM-DD prefix on the filename (derived
from the file's commit time when written by this workflow). For richer
thoughts (multi-paragraph, several quotes, etc.) you can also just
create the `_thoughts/*.md` file directly and skip the inbox.

### Thought

```markdown
---
type: thought
---
A passing thought, written in **markdown**.
```

### Quote

```markdown
---
type: quote
author: Tyler Cowen
source: EconTalk
link: https://www.econtalk.org/tyler-cowen-on-reading/
comment: Worth keeping in mind when re-reading old favourites.
---
The very best books become very different as you get older.
```

The markdown body is the quotation. `comment` is optional accompanying
text shown above the quote. `link` is optional too — with no `link` but
a `source`, the quote falls back to its usual `/books#...` behaviour,
same as `quote.html` elsewhere on the site.

Everything here is filed as a **thought** (there is no separate quote
type). `type: quote` is just a convenience shorthand: the workflow
composes the body into a `{% include quote.html %}` call in the
resulting `_thoughts/*.md` file, with any `comment:` written as prose
above it. A quote is simply a thought that contains a quote — both show
the **Thought** tag.
