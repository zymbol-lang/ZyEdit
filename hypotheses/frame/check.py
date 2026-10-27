#!/usr/bin/env python3
"""Start probe.zy on a real pty, press a key, and count the write calls the engine makes to
draw the frame that follows: a clear and 23 rows, each with `>>~`.

    python3 hypotheses/frame/check.py

ZYMBOL_BIN chooses the binary. The count comes from /proc/<pid>/io (`syscw`), so this runs on
Linux only. A frame shown at once is one write; until then the terminal is free to show every
state in between, the cleared screen first.

Exit status: 0 the frame reaches the terminal in one write (fixed), 1 it takes more (the
state on the day this was written), 2 the program could not be run, 3 the engines disagree.

This file is Python for the reason DIS-ZYE-005 gives.
"""
import fcntl, os, pty, select, signal, struct, sys, termios, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "probe.zy")
ENGINES = [("zyvm", ["run"]), ("zytw", ["run", "--tw"])]


def writes(pid):
    with open(f"/proc/{pid}/io") as f:
        for line in f:
            if line.startswith("syscw:"):
                return int(line.split()[1])


def drive(args):
    """(rows drawn, write calls for the frame), or None when it could not be run"""
    binary = os.environ.get("ZYMBOL_BIN", "zymbol")
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(binary, [binary, *args, PROGRAM])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))

    def read_for(seconds):
        out = b""
        end = time.time() + seconds
        while time.time() < end:
            ready, _, _ = select.select([fd], [], [], 0.05)
            if ready:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                out += chunk
        return out

    try:
        read_for(1.5)
        before = writes(pid)
        os.write(fd, b"x")
        drawn = read_for(0.8)
        count = writes(pid) - before
    except OSError:
        return None
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass
    return drawn.count(b"after key"), count


def main():
    answers = {}
    for name, args in ENGINES:
        got = drive(args)
        if got is None or got[0] != 23:
            print(f"frame: {name} did not draw the 23 rows: {got}")
            return 2
        answers[name] = got[1]
    if len(set(answers.values())) != 1:
        for name, count in answers.items():
            print(f"{name}: {count} writes for one frame")
        print("the engines disagree")
        return 3
    count = next(iter(answers.values()))
    engines = ", ".join(name for name, _ in ENGINES)
    print(f"frame: {engines} agree; a clear and 23 `>>~` reach the terminal in {count} writes")
    print(f"  GAP-ZYE-015  {'FIXED' if count == 1 else 'HOLDS'}")
    return 0 if count == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
