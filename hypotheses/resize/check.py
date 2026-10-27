#!/usr/bin/env python3
"""Start probe.zy on a real pty, change the window's size, press nothing, and say
whether the program blocked in `<<|` hears of it.

    python3 hypotheses/resize/check.py

ZYMBOL_BIN chooses the binary. The probe prints a line for every key it reads, so that
line appearing after the resize, with no key sent, means the program was woken.

Exit status: 0 the program is told of the resize (fixed), 1 it hears nothing (the state
on the day this was written), 2 the program could not be run, 3 the engines disagree.

(A first version also counted keys "lost" when sent with the resize: 3 of 8 delivered.
That was the check's own race, a key written before the program had left line mode, and
it does not reproduce: 16 of 16 arrive. It is not a finding.)

This file is Python for the reason DIS-ZYE-005 gives.
"""
import fcntl, os, pty, select, signal, struct, sys, termios, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "probe.zy")
ENGINES = [("zyvm", ["run"]), ("zytw", ["run", "--tw"])]
ENTER = b"\x1b[?1049h"


def drive(args):
    """(entered the block, heard of the resize)"""
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
                    chunk = os.read(fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                out += chunk
        return out

    started = read_for(1.5)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 12, 60, 0, 0))
    heard = b"key " in read_for(0.6)     # the probe's own line, not an error message
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass
    return ENTER in started, heard


def main():
    answers = {}
    for name, args in ENGINES:
        entered, heard = drive(args)
        if not entered:
            print(f"resize: {name} did not enter the `>>|` block")
            return 2
        answers[name] = heard
    if len(set(answers.values())) != 1:
        for name, heard in answers.items():
            print(f"{name}: told of the resize {heard}")
        print("the engines disagree")
        return 3
    heard = next(iter(answers.values()))
    engines = ", ".join(name for name, _ in ENGINES)
    print(f"resize: {engines} agree; a program waiting in `<<|` is "
          f"{'told' if heard else 'not told'} that the window changed size")
    print(f"  GAP-ZYE-012  {'FIXED' if heard else 'HOLDS'}")
    return 0 if heard else 1


if __name__ == "__main__":
    sys.exit(main())
