#!/usr/bin/env python3
"""Ask both engines what `<<|` hands back for each key, through a real pty, and
say whether each hypothesis still holds.

    python3 hypotheses/keys/check.py            # verdicts
    python3 hypotheses/keys/check.py --table    # and the value of every key

ZYMBOL_BIN chooses the binary. The bytes sent are xterm's, which is what most
terminal emulators send.

Exit status: 0 every finding is fixed, 1 at least one still holds (the state on
the day this was written), 2 the program could not be run, 3 the engines
disagree, 4 a key that worked has stopped working.

This file is Python, and that is a finding of its own: DIS-ZYE-005.
"""
import fcntl, os, pty, re, select, signal, struct, sys, termios, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "keys.zy")
ENGINES = [("zyvm", ["run"]), ("zytw", ["run", "--tw"])]

# (name, bytes sent, what it must keep being — None if it is under question)
KEYS = [
    ("Ctrl+Z",      b"\x1a",          26),
    ("Ctrl+S",      b"\x13",          19),
    ("Ctrl+C",      b"\x03",           3),
    ("Ctrl+Q",      b"\x11",          17),
    ("Ctrl+V",      b"\x16",          22),
    ("Ctrl+H",      b"\x08",           8),
    ("Ctrl+I",      b"\x09",           9),   # the terminal sends Tab's byte
    ("Home",        b"\x1b[H",       None),
    ("End",         b"\x1b[F",       None),
    ("Delete",      b"\x1b[3~",      None),
    ("PageUp",      b"\x1b[5~",      None),
    ("PageDown",    b"\x1b[6~",      None),
    ("F1",          b"\x1bOP",       None),
    ("Shift+Tab",   b"\x1b[Z",       None),
    ("Shift+Right", b"\x1b[1;2C",    None),
    ("Ctrl+Right",  b"\x1b[1;5C",    None),
    ("Ctrl+/",      b"\x1f",         None),
    ("Ctrl+Space",  b"\x00",         None),
    ("Alt+x",       b"\x1bx",        None),
]

RIGHT = 0x2192          # what a plain → arrives as


def drive(args):
    """Run keys.zy under one engine, one key at a time, and return the codes."""
    binary = os.environ.get("ZYMBOL_BIN", "zymbol")
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(binary, [binary, *args, PROGRAM])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
    out = b""

    def read_for(seconds):
        nonlocal out
        end = time.time() + seconds
        while time.time() < end:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    return
                if not chunk:
                    return
                out += chunk

    read_for(1.0)                     # let it reach raw mode before any key
    for _, sent, _ in KEYS:
        os.write(fd, sent)
        read_for(0.35)
    read_for(0.8)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass
    text = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", out.decode("utf-8", "replace"))
    return [int(n) for n in re.findall(r"\d+", text)]


def main():
    results = {}
    for name, args in ENGINES:
        codes = drive(args)
        if len(codes) != len(KEYS):
            print(f"{name}: expected {len(KEYS)} codes, read {len(codes)}: {codes}")
            return 2
        results[name] = codes
    first = results[ENGINES[0][0]]
    if any(codes != first for codes in results.values()):
        for name, codes in results.items():
            print(f"{name}: {codes}")
        print("the engines disagree")
        return 3
    got = {name: code for (name, _, _), code in zip(KEYS, first)}

    if "--table" in sys.argv:
        for name, sent, _ in KEYS:
            print(f"  {name:12} {sent.hex(' '):20} -> {got[name]}")
        print()

    regressions = [n for n, _, keep in KEYS if keep is not None and got[n] != keep]
    nav = ["Home", "End", "Delete", "PageUp", "PageDown", "F1", "Shift+Tab"]
    others = [got[n] for n, _, _ in KEYS if n not in nav]
    nav_codes = [got[n] for n in nav]
    verdicts = {
        # Each navigation key arrives as a value of its own: not 0d0 (which is
        # also `<<|?`'s "no key"), not another navigation key's, not any other key's.
        "DIS-ZYE-001": 0 in nav_codes
                       or len(set(nav_codes)) != len(nav_codes)
                       or bool(set(nav_codes) & set(others)),
        # A modifier on an arrow is not lost: neither arrives as a plain →, and
        # Shift and Ctrl are told apart.
        "DIS-ZYE-002": RIGHT in (got["Shift+Right"], got["Ctrl+Right"])
                       or got["Shift+Right"] == got["Ctrl+Right"],
        # A combination never arrives as the printable key it would type.
        "DIS-ZYE-003": got["Ctrl+/"] in (ord("7"), ord("/"))
                       or got["Ctrl+Space"] == ord(" ")
                       or got["Alt+x"] == ord("x"),
    }
    engines = ", ".join(name for name, _ in ENGINES)
    print(f"keys: {len(KEYS)} keys through a pty, {engines} agree")
    for finding, holds in verdicts.items():
        print(f"  {finding}  {'HOLDS' if holds else 'FIXED'}")
    if regressions:
        print(f"  REGRESSION  {', '.join(regressions)} no longer arrive as before")
        return 4
    return 1 if any(verdicts.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
