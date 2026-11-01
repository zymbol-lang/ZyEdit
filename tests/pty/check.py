#!/usr/bin/env python3
"""ZyEdit through a real pty: what `--keys` cannot see.

`--keys` hands the program keys that are already decoded, draws on a virtual screen, and
writes the last frame without styles. This starts the editor on a terminal, sends the bytes a
terminal sends (xterm's), rebuilds the screen from what comes back — including the styles —
and resizes the window while it runs. It is Python for the reason DIS-ZYE-005 gives.

  python3 tests/pty/check.py [engine flag, e.g. --tw]
ZYMBOL_BIN chooses the binary. Exit status: 0 all checks held, 1 one did not.
"""
import os, pty, re, select, signal, struct, sys, tempfile, time, fcntl, termios

ZY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "zyedit.zy")
ENGINE = sys.argv[1:] or []

class Screen:
    """Just enough of a terminal for what ZyEdit emits: cursor moves, clears and SGR."""
    def __init__(self, rows, cols):
        self.resize(rows, cols)
    def resize(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.text = [[" "] * cols for _ in range(rows)]
        self.rev = [[False] * cols for _ in range(rows)]
        self.r = self.c = 0
        self.reverse = False
    def feed(self, data):
        i = 0
        while i < len(data):
            ch = data[i]
            if ch == "\x1b" and data[i + 1:i + 2] == "[":
                m = re.match(r"\x1b\[([0-9;?]*)([A-Za-z])", data[i:])
                if not m:
                    i += 1; continue
                arg, cmd = m.group(1), m.group(2)
                nums = [int(x) if x.isdigit() else 0 for x in arg.lstrip("?").split(";")]
                if cmd in "Hf":
                    self.r = max(nums[0] - 1, 0) if nums else 0
                    self.c = max(nums[1] - 1, 0) if len(nums) > 1 else 0
                elif cmd == "J" and (nums[0] if nums else 0) == 2:
                    self.text = [[" "] * self.cols for _ in range(self.rows)]
                    self.rev = [[False] * self.cols for _ in range(self.rows)]
                elif cmd == "m":
                    for n in nums or [0]:
                        if n == 0: self.reverse = False
                        elif n == 7: self.reverse = True
                        elif 40 <= n <= 47 or n == 48: self.reverse = True   # a background colour
                i += m.end()
            elif ch == "\x1b":
                i += 2
            elif ch == "\r": self.c = 0; i += 1
            elif ch == "\n": self.r += 1; i += 1
            elif ord(ch) < 32: i += 1
            else:
                if 0 <= self.r < self.rows and 0 <= self.c < self.cols:
                    self.text[self.r][self.c] = ch
                    self.rev[self.r][self.c] = self.reverse
                self.c += 1; i += 1
    def line(self, n): return "".join(self.text[n]).rstrip()
    def reversed_text(self, n):
        return "".join(ch for ch, r in zip(self.text[n], self.rev[n]) if r)

def start(path, rows=24, cols=80):
    pid, fd = pty.fork()
    if pid == 0:
        binary = os.environ.get("ZYMBOL_BIN", "zymbol")
        os.execvp(binary, [binary, "run"] + ENGINE + [ZY, path])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    return pid, fd, Screen(rows, cols)

def pump(fd, scr, secs=0.6):
    """Feeds what the program writes to the screen, and returns it as it came."""
    seen = ""
    end = time.time() + secs
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try: chunk = os.read(fd, 65536)
            except OSError: return seen
            if not chunk: return seen
            text = chunk.decode("utf-8", "replace")
            scr.feed(text); seen += text
    return seen

def send(fd, scr, data, secs=0.25):
    os.write(fd, data); return pump(fd, scr, secs)

def stop(pid):
    try: os.kill(pid, signal.SIGKILL)
    except ProcessLookupError: pass
    try: os.waitpid(pid, 0)
    except ChildProcessError: pass

failures = []
def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  " + detail))
    if not ok: failures.append(name)

d = tempfile.mkdtemp()
path = os.path.join(d, "f.txt")
open(path, "w").write("hello\nworld\n")
os.chdir(d)

pid, fd, scr = start("f.txt")
pump(fd, scr, 1.5)
check("starts and shows the file", "hello" in scr.line(0) and "world" in scr.line(1), scr.line(0))
check("the status bar is on the last row", "f.txt" in scr.line(23), scr.line(23))
check("the caret is drawn reversed on the first character", scr.reversed_text(0).strip().startswith("h"),
      repr(scr.reversed_text(0)))

send(fd, scr, b"X")
check("a printable key is inserted", "Xhello" in scr.line(0), scr.line(0))
drawn = send(fd, scr, b"\x1b[B")              # xterm's Down
check("the arrow decodes to a move", " 2:2" in scr.line(23) or "2:2/" in scr.line(23), scr.line(23))
# Only the rows that changed are drawn (GAP-ZYE-015): a move clears nothing, and draws the
# two rows the caret left and reached, and the status line.
rows = {int(m) for m in re.findall(r"\x1b\[(\d+);\d+H", drawn)}
check("moving the caret draws only what changed", "\x1b[2J" not in drawn and rows == {1, 2, 24},
      f"clear: {'yes' if chr(27) + '[2J' in drawn else 'no'}, rows drawn: {sorted(rows)}")
send(fd, scr, b"\x02"); send(fd, scr, b"\x1b[C"); send(fd, scr, b"\x1b[C")        # Ctrl+B, Right, Right
check("the selection is drawn reversed", len(scr.reversed_text(1).strip()) >= 2 and "SEL" in scr.line(23),
      repr(scr.reversed_text(1)) + " | " + scr.line(23))
send(fd, scr, b"\x1b")                        # Esc, alone
send(fd, scr, b"\x13")                        # Ctrl+S
check("Ctrl+S writes the file", open(path).read() == "Xhello\nworld\n", repr(open(path).read()))

# the window changes size while the editor waits on a key (the kernel sends SIGWINCH itself)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 12, 60, 0, 0))
scr.resize(12, 60)
pump(fd, scr, 0.5)
check("a resize with no key after it is redrawn at the new size", "f.txt" in scr.line(11), " | ".join(scr.line(n) for n in range(12)))
send(fd, scr, b"\x1b[A", 0.4)
check("after a resize the status bar moves to the new last row", "f.txt" in scr.line(11),
      " | ".join(scr.line(n) for n in range(12)))
send(fd, scr, b"\x11")                        # Ctrl+Q
pump(fd, scr, 0.5); stop(pid)

sys.exit(1 if failures else 0)
