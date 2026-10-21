# hypotheses/

The programs behind ZyEdit's design findings (`DIS-ZYE-NNN` in [HALLAZGOS.md](../HALLAZGOS.md)).
A design finding is made by probing the language **before** the editor exists, so its evidence
cannot be a line of the editor. It is a program that asks one question, a check that reads the
answer, and the answer as it was on the day the finding was filed.

They stay here after the fix. Before it, they are the evidence; after it, they are how the fix
is confirmed.

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
   `zyquality/tui/` for anything that needs a real terminal (each probe here is written in
   the shape of `tui/keys_control.zy` for that reason), or a ZyDDT cell when the question can
   be asked without one. Only then is the finding closed, and its entry names the case that
   holds it (decalogue point 7).

The directory is **not deleted** after step 4. It keeps the evidence, and it is the one place
that says why the case in `zyquality/` exists.

## The hypotheses

| Directory | Findings | State | Moves to |
|---|---|---|---|
| [`keys/`](keys/) | DIS-ZYE-001, 002, 003 | HOLDS (2026-10-20) | `zyquality/tui/`, beside `keys_control.zy` |
| [`cursor/`](cursor/) | DIS-ZYE-004 | HOLDS (2026-10-20) | `zyquality/tui/` |

DIS-ZYE-005 has no directory of its own, because its evidence is the two `check.py` files
themselves. Both are Python because no Zymbol program can start another program on a
terminal, write keys to it and read what it draws. Its "after" is one of them rewritten in
Zymbol.

## Running them

```bash
bash hypotheses/run.sh            # every hypothesis, both Rust engines
python3 hypotheses/keys/check.py --table
python3 hypotheses/cursor/check.py
```

`ZYMBOL_BIN` chooses the binary. Each check runs both Rust engines and fails (exit 3) when they
disagree, before it gives any verdict. The browser engine has no terminal, so these questions
cannot be put to it.

Exit status of each check: **0** every finding it asks about is fixed, **1** at least one
holds, **2** the program could not be run, **3** the engines disagree, **4** (`keys/` only) a
key that worked has stopped working.
