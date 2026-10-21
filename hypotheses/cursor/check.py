#!/usr/bin/env python3
"""Read what each engine writes to a real pty while cursor.zy runs, and say
whether the terminal's cursor is ever shown inside the `>>|` block.

    python3 hypotheses/cursor/check.py

ZYMBOL_BIN chooses the binary. The answer is in the escape sequences:
`ESC [ ? 25 l` hides the cursor, `ESC [ ? 25 h` shows it, and the block is what
lies between entering the alternate screen (`ESC [ ? 1049 h`) and leaving it
(`ESC [ ? 1049 l`).

Exit status: 0 the cursor is shown inside the block (fixed), 1 it never is (the
state on the day this was written), 2 the program could not be run, 3 the
engines disagree.

This file is Python, and that is a finding of its own: DIS-ZYE-005.
"""
import fcntl, os, pty, select, signal, struct, sys, termios, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "cursor.zy")
ENGINES = [("zyvm", ["run"]), ("zytw", ["run", "--tw"])]

ENTER, LEAVE = b"\x1b[?1049h", b"\x1b[?1049l"
HIDE, SHOW = b"\x1b[?25l", b"\x1b[?25h"


def drive(args):
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

    read_for(1.0)
    os.write(fd, b"x")
    read_for(0.8)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass
    return out


def main():
    answers = {}
    for name, args in ENGINES:
        out = drive(args)
        if ENTER not in out or LEAVE not in out:
            print(f"{name}: the block was not entered and left: {out!r}")
            return 2
        block = out[out.index(ENTER):out.rindex(LEAVE)]
        answers[name] = (HIDE in block, SHOW in block)
    if len(set(answers.values())) != 1:
        for name, (hidden, shown) in answers.items():
            print(f"{name}: hidden {hidden}, shown {shown}")
        print("the engines disagree")
        return 3
    hidden, shown = next(iter(answers.values()))
    engines = ", ".join(name for name, _ in ENGINES)
    print(f"cursor: {engines} agree; inside `>>|` the cursor is "
          f"{'hidden' if hidden else 'not hidden'} and "
          f"{'shown' if shown else 'never shown'}")
    print(f"  DIS-ZYE-004  {'FIXED' if shown else 'HOLDS'}")
    return 0 if shown else 1


if __name__ == "__main__":
    sys.exit(main())
