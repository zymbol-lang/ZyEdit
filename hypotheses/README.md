# hypotheses/

The programs behind ZyEdit's findings ([HALLAZGOS.md](../HALLAZGOS.md)). It began with the
design findings (`DIS-ZYE-NNN`), made by probing the language **before** the editor existed,
whose evidence could not be a line of the editor. The findings that came later from writing
the editor and that need more than a few inline lines to show (a pty, a cost under `--count`,
three engines side by side) have a directory here too.

Each directory is a program that asks one question, a check that reads the answer, and the
answer as it was on the day the finding was filed. They stay here after the fix. Before it,
they are the evidence; after it, they are how the fix is confirmed.

## The life of a hypothesis

1. **HOLDS.** The check reports the finding and exits 1. The answer is saved in
   `evidence/<date>.txt` together with the binary and the commit it came from. This is the
   state every hypothesis was filed in.
2. **The language changes.** The author decides the shape of the fix and it is built in the
   engines. Where the fix adds something a program must write (DIS-ZYE-004's cursor is one),
   the probe gains that line at the place its comment marks.
3. **FIXED.** The check is run again, reports FIXED and exits 0. That answer is saved as a
   second evidence file, so the before and the after sit side by side.
4. **Moved to the cheap layer.** The question moves to where it is asked on every commit:
   `zyquality/tui/` for anything that needs a real terminal (each terminal probe here is
   written in the shape of `tui/keys_control.zy` for that reason), `zyquality/cost/` for a
   cost, the corpus for an answer the engines must agree on, or a ZyDDT cell when the
   question can be asked there. Only then is the finding closed, and its entry names the case
   that holds it (decalogue point 7).

The directory is **not deleted** after step 4. It keeps the evidence, and it is the one place
that says why the case in `zyquality/` exists.

## The hypotheses

| Directory | Findings | How | State | Moves to |
|---|---|---|---|---|
| [`keys/`](keys/) | DIS-ZYE-001, 002, 003 | pty | HOLDS (2026-10-20) | `zyquality/tui/`, beside `keys_control.zy` |
| [`cursor/`](cursor/) | DIS-ZYE-004 | pty | HOLDS (2026-10-20) | `zyquality/tui/` |
| [`replaced_tuple/`](replaced_tuple/) | BUG-ZYE-011 | `--count` | HOLDS (2026-10-27) | `zyquality/cost/` |
| [`resize/`](resize/) | GAP-ZYE-012 | pty | HOLDS (2026-10-27) | `zyquality/tui/` |
| [`string_cr/`](string_cr/) | BUG-ZYE-013 | three engines | FIXED (2026-10-30) | `zyquality/corpus/strings/cr_escape_in_text.zy` |
| [`mid_array/`](mid_array/) | BUG-ZYE-014 | `--count` | HOLDS (2026-10-27) | `zyquality/cost/` |
| [`frame/`](frame/) | GAP-ZYE-015 | pty | HOLDS (2026-10-27) | `zyquality/tui/` |

DIS-ZYE-005 has no directory of its own, because its evidence is the terminal checks
themselves. They are Python because no Zymbol program can start another program on a
terminal, write keys to it and read what it draws. Its "after" is one of them rewritten in
Zymbol.

The two cost checks carry **controls**: programs that do the same steps without what the
finding is about, and cost nothing today (`replaced_tuple/control_*.zy`, and `remove` and
`replace` in `mid_array/`). A fix must leave them where they are.

## Running them

```bash
bash hypotheses/run.sh            # every hypothesis
python3 hypotheses/keys/check.py --table
bash hypotheses/mid_array/check.sh
```

`ZYMBOL_BIN` chooses the binary, and `ZYJS_HARNESS` the browser engine's driver for
`string_cr/` (`web/` beside this checkout by default). Each check runs both Rust engines; the
terminal ones fail (exit 3) when the two disagree, before they give any verdict. The browser
engine has no terminal, so only `string_cr/` puts its question to it.

Exit status of each check: **0** every finding it asks about is fixed, **1** at least one
holds, **2** a program could not be run, **3** the engines disagree where they must agree,
**4** something that worked has stopped working: a key in `keys/`, a control in the cost
checks.
