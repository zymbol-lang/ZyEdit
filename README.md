# ZyEdit

A terminal text editor written in [Zymbol](https://zymbol-lang.org).

> **Status: not started.** This README is the plan. There is no editor code and no suite
> yet. Everything below that describes the program says what it *will* do. The findings log,
> [HALLAZGOS.md](HALLAZGOS.md), opened on 2026-10-20 with five **design findings**, found by
> probing the language before writing the editor. Their programs and evidence are in
> [`hypotheses/`](hypotheses/), where they stay to confirm each fix.

---

## Why this exists

ZyEdit is a Language-Driven Validation project (`zymbol-design/LDV.md`), the eleventh, opened
on 2026-10-21. The editor is the instrument, and what it measures is **Zymbol**. Each time the language cannot
say what an editor needs, or says it and gets it wrong, that goes in the log as a finding.

LDV § 6 says the method *"scales with domain distance, not with size"*: a sixth grid game
would teach almost nothing. So the question for a new project is what it asks that the
earlier ones did not. Those ten projects are a go engine, a chaturanga engine, two arcade
games, a neural network library, a code auditor, a ledger, the Game of Life, a Brainf***
interpreter and an AI command line. An editor adds:

| Distance | What no earlier application asked of the language |
|---|---|
| **Text is the data** | Every other application keeps its state in numbers, grids or records, and text is only what it prints. Here the state *is* the text: long-lived, and edited at any position, one keystroke at a time. |
| **The cost of an edit** | Inserting one character into the middle of a 10 000-line file has to cost about one character, not a copy of the file. That is exactly the shape `zyquality/cost/` watches (GLB-139, ZYTW-016 and PERF-05 b are open on it today). |
| **A byte-exact round trip** | Opening a file and saving it without touching it must give back the same bytes: line endings, the final newline or its absence, tabs, a byte-order mark, and text that is not valid UTF-8. No earlier application wrote back a file a person owns. |
| **Three units of position** | A cursor moves in grapheme clusters, the screen lays out in terminal columns, and the language indexes in code points (a `Char` is a code point). An editor has to keep all three straight, on every line, in every script. |
| **History as data** | Undo and redo: a record of edits that can be replayed in both directions. |
| **A tokenizer in Zymbol** | Highlighting (stage 3) means a lexer written in the language, driven by a format of ZyEdit's own. |
| **Talking to another process** | The LSP client (stage 4) needs a long-lived child process to exchange JSON-RPC with over stdin and stdout. |
| **A terminal inside the program** | The terminal panel (stage 5) needs a pseudo-terminal and a VT parser. |

The first five rows are what stage 1 and stage 2 test. The last three come later, and each of
them may need the language to change before it can be written at all.

## ZyEdit and zedit

[zedit](https://github.com/Zenith-Lang-Org/zedit) (`~/github/zedit`) is the same idea written
in Rust: a modern console editor with Ctrl+C/V/X/S/Z, multiple buffers, TextMate
highlighting, an LSP client and an integrated terminal. It is about 42 000 lines with no
external crates.

ZyEdit is **not a port**. zedit is where it looks for reference: the keybindings, the order
its features were built in (`docs/editor-plan*.md`), and how its parts were split up. What it
does not copy is the TextMate format. Reading TextMate grammars took zedit a JSON parser and
1 644 lines of regex engine (`src/syntax/regex.rs`). Writing an Oniguruma subset in Zymbol
would be a separate project, and it would measure the regex engine rather than the editor. So
ZyEdit defines a highlight format of its own (stage 3).

## Stages

Each stage closes the LDV way: the editor works **and** its findings are closed, deferred or
rejected, each with its reason. The author decides when to start the next one.

### Stage 1 — edit text

Open a file, or start an empty buffer, then move around, type, delete, save and quit:

- a buffer of lines, with the cursor moved by arrows, line start/end and page up/down
- inserting a character, Enter (split a line), Backspace and Delete (join lines at the edges),
  Tab
- vertical and horizontal scrolling, and a status line showing the file name, a modified mark
  and the line and column
- Ctrl+S saves and Ctrl+Q quits, asking first when there are unsaved changes
- the round trip: a file opened and saved untouched comes back byte for byte
- wide and combining characters: the cursor never lands inside a cluster, and the column it
  shows is the one the terminal draws

**Done when** a person can edit a real file in it, and its suite (below) holds a screen golden
for every item above.

### Stage 2 — an editor, not a text field

Undo and redo, a selection with an internal clipboard (copy, cut, paste), search, go to line,
and several buffers.

### Stage 3 — highlighting, in a format of its own

A declarative description of a language's tokens, read from a file, and a tokenizer written in
Zymbol that applies it one line at a time, carrying state across lines for strings and
comments. **Zymbol is the first language it describes.** The VS Code grammar and the
playground's highlighter already describe Zymbol, so a third description can be checked
against both on the corpus. ZyDDT's `surfaces` does this for the first two today.

The format itself (its name, its shape, how it says *"a string that may span lines"* without
regular expressions) is a design decision for the author, taken when the stage begins.

### Stage 4 — the Zymbol language server

ZyEdit becomes a client of `zymbol lsp`: diagnostics in the gutter, hover, go to definition.
**This stage probably cannot start in today's language.** `<\ cmd \>` runs a command to
completion and returns its output, and a language server is a process that stays alive and
talks back. DIS-ZYE-005 already records this, found before any editor code by the
hypotheses' own checks. The stage begins with the language change that closes it.

### Stage 5 — a terminal panel, in the style of VS Code

A shell running inside a panel of the editor. This needs a pseudo-terminal, a child process
whose output arrives while the editor keeps running, and a VT100 parser. The parser can be
written in Zymbol, and zedit's `src/vterm.rs` (1 310 lines) is the reference for its size.
The pseudo-terminal itself is outside the language today: that is DIS-ZYE-005 again, and
`hypotheses/*/check.py` is a small version of this panel, written in Python because it could
not be written in Zymbol.

## What we expect to find

These were written down **before** any code, so they can be checked one by one and not
mistaken later for things that were found. Each one becomes a finding only when a program
shows it.

The first two were checked on 2026-10-20 with `hypotheses/keys/` and `hypotheses/cursor/`,
driven through a real pty in both engines, and are now design findings (`DIS`, a type the author added for findings made
while designing, before the application exists):

- **Keys** — confirmed, in three parts:
  - Home, End, Page Up, Page Down, Delete, F1–F12 and Shift+Tab all arrive as `0d0`, the value
    `<<|?` already uses for "no key" (DIS-ZYE-001);
  - Shift and Ctrl on an arrow are dropped, so Shift+→ arrives as → (DIS-ZYE-002);
  - Ctrl+/, Ctrl+Space and Alt+*letter* arrive as a printable character (DIS-ZYE-003).

  Ctrl+*letter* is fine: Ctrl+Z, Ctrl+S, Ctrl+C, Ctrl+Q and Ctrl+V all arrive as their
  control characters.
- **The caret** — confirmed: `>>|` hides the terminal's cursor and nothing shows it
  (DIS-ZYE-004). ZyEdit can draw its own caret in the meantime.
- **Resizing.** `>>?` answers the size when it is asked. A window that changes size while the
  editor waits on `<<|` may not be noticed.
- **Bytes.** Whether `std/io` can read and write a file whose bytes are not valid UTF-8, keep
  `\r\n` as written, and tell "ends with a newline" apart from "does not".
- **Cost.** Whether an edit in the middle of a long line, or of a long file, costs what it
  changes. GLB-139 (`s[i]` and a slice walk the text) is open today and lies directly in this
  path.
- **Processes** — confirmed sooner than expected, by the hypotheses' own checks. They had to
  be written in Python, because no Zymbol program can start another on a terminal, write keys
  to it and read what it draws (DIS-ZYE-005). That is the same capability stage 5 needs, and
  most of what stage 4 needs.

## Rules of the project

- **Written in English:** identifiers, module names, the interface and this README. This
  repeats a language: ZethyCLI (v0.0.3) was written in English, and decalogue point 9 counts
  each new natural language as a test of its own. That is accepted on purpose, because the
  distance this project measures is the domain, not the script. Translating the interface
  (`zymbol-design/USERAPPI18N.md`) is out of scope until the author decides otherwise.
- **The findings log is `HALLAZGOS.md`, in Spanish**, like every findings log in the workspace
  (`LDV.md` § 5). Each entry has an ID scoped `ZYE` and numbered in one sequence, a type
  (`GAP` for something the language cannot say, `BUG` for a wrong answer, and `DIS` for a
  design finding made by probing before the application exists), a minimal reproduction and
  a status.
- **A workaround counts as red** (decalogue point 4). A shell call, a hand-written table or a
  duplicated block that stands in for something the language should say is logged, not
  hidden.
- **No finding lives only here** (decalogue point 7). It is closed when a minimal case is in
  `zyquality/` or ZyDDT.

## Testing

A full-screen program can be tested without a terminal: `zymbol run --keys` draws on a
virtual 24×80 screen, reads its keys from a script, and writes the last frame as text
(`GUIDE.md` § 3b). Each editing behaviour therefore gets a key script and a screen golden,
and the suite can join `zyquality/project/apps.toml` and run inside `zyq suite`, as the other
applications' suites do. Byte-exact saving is checked by comparing files, not screens. The
cost of an edit is measured with `zymbol run --count`, which is exact and does not depend on
the machine, never by timing it.

## Planned use

```bash
zymbol run zyedit.zy notes.txt     # open a file
zymbol run zyedit.zy               # an empty buffer
```

ZyEdit behaves like a desktop editor that happens to run in a terminal, not like vi or nano:
there are no modes, and the shortcuts are the ones a GUI editor uses, as far as a terminal
lets them through. The **Today** column is what `<<|` delivers on 2026-10-20.

| Key | Action | Stage | Today |
|---|---|---|---|
| `↑ ↓ ← →` | move | 1 | ✅ |
| `Enter` / `Backspace` / `Tab` | split a line / delete back / insert a tab | 1 | ✅ |
| `Ctrl+S` | save | 1 | ✅ |
| `Ctrl+Q` | quit, asking first if there are unsaved changes | 1 | ✅ |
| `Delete` | delete forward | 1 | ❌ DIS-ZYE-001 |
| `Home` / `End` | start / end of the line | 1 | ❌ DIS-ZYE-001 |
| `Page Up` / `Page Down` | one screen up / down | 1 | ❌ DIS-ZYE-001 |
| `Ctrl+Z` / `Ctrl+Y` | undo / redo | 2 | ✅ |
| `Ctrl+C` / `Ctrl+X` / `Ctrl+V` | copy / cut / paste (internal clipboard) | 2 | ✅ |
| `Ctrl+A` | select all | 2 | ✅ |
| `Shift+arrows` | select | 2 | ❌ DIS-ZYE-002 |
| `Ctrl+← / →` | move by word | 2 | ❌ DIS-ZYE-002 |
| `Ctrl+F` / `Ctrl+G` | find / go to line | 2 | ✅ |
| `Ctrl+O` / `Ctrl+N` / `Ctrl+W` | open / new buffer / close buffer | 2 | ✅ |
| `Ctrl+/` | toggle a line comment | 3 | ❌ DIS-ZYE-003 |
| `Ctrl+Space` | ask the language server for completions | 4 | ❌ DIS-ZYE-003 |

Redo is `Ctrl+Y` and not `Ctrl+Shift+Z`, because a terminal sends the same byte for Ctrl+Shift+Z
as for Ctrl+Z. That limit, and the shortcuts terminal emulators keep for themselves, are listed
at the end of [HALLAZGOS.md](HALLAZGOS.md) so that nobody files them as findings.

## Decisions

**Taken.** The repository is **`zymbol-lang/ZyEdit`**, public, following ZyBank, ZyGoL and ZyBF.
It was published on 2026-10-21, before any editor code, so that the design findings and their
evidence are public from the start.

**Open (the author's), each with a recommendation:**

1. **The buffer.** Recommended: **an array of lines, one string per line.** Editing line *i*
   is `lines[i]$~ new`, and an edit with one owner costs one element, not the collection
   (ZYVM-003, ZYVM-013). A gap buffer would need a mutable array of characters and gap
   arithmetic, which would measure the workaround rather than the editor. The LSP speaks in
   (line, character), and highlighting keeps its state per line. The known risk is GLB-139:
   an edit costs the length of its line. To be accepted with `--count` on the first
   prototype: inserting one character in the middle of a 10 000-line file costs the same as
   in a 100-line one.
2. **The highlight format.** Recommended: **a declarative text format of ZyEdit's own, with
   no regular expressions**, built from three pieces:
   - symbol and word lists matched longest first (Zymbol is mostly operators, so this is the
     main piece);
   - delimited spans (start, end, escape, and whether they cross lines);
   - character classes for numbers and identifiers.

   Token classes are named like TextMate scopes (`comment`, `string`, `keyword.operator`) so
   VS Code themes can be reused. Two alternatives were set aside. A grammar written as a
   Zymbol module would need a dynamic import to be chosen by file extension at run time. JSON
   read with `std/json` would not be a format of its own. The name and the extension can wait
   for stage 3; the no-regex principle is worth fixing now.
3. **Which engines the suite holds.** Recommended: **split the logic from the screen.** The
   pure modules (buffer, history, tokenizer) never touch the terminal: hold them with plain
   goldens in **all three engines**, as GoL does. Hold the screen with `--keys` in **zytw and
   zyvm**.

---

## Authorship

Written with [Claude Code](https://claude.ai/code) under the author's direction, as the
interpreter and the LDV applications are (`interpreter/README.md` § Authorship & AI
Collaboration).
