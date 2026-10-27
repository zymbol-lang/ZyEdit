#!/bin/bash
# ZyEdit's suite: the pure modules in all three engines, the screen through `--keys` and a
# real pty in both Rust engines, the byte-exact round trip, and the cost of an edit.
#
#   bash tests/run.sh           check
#   bash tests/run.sh --regen   rewrite the goldens from the VM (then read the diff)
#
# ZYMBOL_BIN chooses the binary (an absolute path: the screen tests run in a scratch
# directory); ZYJS_HARNESS the browser engine's driver, `web/` beside this checkout by
# default. Exit status: 0 everything held, 1 something did not.
cd "$(dirname "$0")"
Z="${ZYMBOL_BIN:-zymbol}"
JS="${ZYJS_HARNESS:-../../web/tests/run_one.mjs}"
fail=0; W=$(mktemp -d); trap 'rm -rf "$W"' EXIT

# The pure modules: plain goldens (README, decision 3). They are shared with
# zyquality/project/apps.toml, so they are written the way `zyq expect` writes them: streams
# merged, and warnings, blank lines and lines that start with three spaces dropped
# (zyquality/src/golden.ml, strip_warnings).
zyq_filter() { grep -v -e '^warning:' -e '^  -->' -e '^   ' -e '^  =' -e '^$'; }
for e in "" --tw; do
  mode="${e:-vm}"
  for m in buffer history; do
    "$Z" run $e $m.zy 2>&1 | zyq_filter > "$W/m.out"
    [ "$1" = --regen ] && [ -z "$e" ] && cp "$W/m.out" $m.expected
    diff -q "$W/m.out" $m.expected >/dev/null && echo "ok   $m ($mode)" || { echo "FAIL $m ($mode)"; fail=1; }
  done
done
# ... and the browser engine. buffer.zy writes "\r", which zyjs reads as the letter r
# (BUG-ZYE-013); buffer.zyjs.known is what it prints because of that. KNOWN while
# it prints exactly that, FAIL once it agrees with the golden, so that the finding is closed.
if command -v node >/dev/null && [ -f "$JS" ]; then
  for m in buffer history; do
    node "$JS" $m.zy < /dev/null 2>&1 | zyq_filter > "$W/m.out"
    if diff -q "$W/m.out" $m.expected >/dev/null; then
      [ $m = buffer ] && { echo "FAIL $m (zyjs) agrees now: close BUG-ZYE-013"; fail=1; } || echo "ok   $m (zyjs)"
    elif [ -f $m.zyjs.known ] && diff -q "$W/m.out" $m.zyjs.known >/dev/null; then
      echo "KNOWN $m (zyjs): BUG-ZYE-013"
    else
      echo "FAIL $m (zyjs)"; fail=1
    fi
  done
else
  echo "skip modules (zyjs): no node, or no $JS"
fi

# The screen: a key script per behaviour, the last frame of each SHOW as the golden.
for e in "" --tw; do
  mode="${e:-vm}"
  for k in screen/*.keys; do
    n=$(basename "$k" .keys); D=$(mktemp -d -p "$W"); cp "screen/$n.fixture" "$D/f.txt"; files=f.txt
    [ -f "screen/$n.fixture2" ] && { cp "screen/$n.fixture2" "$D/g.txt"; files="f.txt g.txt"; }
    (cd "$D" && "$Z" run --timeout 30 $e --keys "$OLDPWD/$k" "$OLDPWD/../zyedit.zy" $files > "$W/s.out" 2>&1)
    [ "$1" = --regen ] && [ -z "$e" ] && cp "$W/s.out" "screen/$n.expected"
    [ "$n" = locked ] && ! cmp -s "$D/f.txt" screen/locked.fixture && { echo "FAIL locked: the unreadable file was changed ($mode)"; fail=1; }
    [ "$n" = dirty ] && [ "$(cat "$D/f.txt")" != abx ] && { echo "FAIL dirty: the file does not hold what was saved ($mode)"; fail=1; }
    [ "$n" = crlf ] && ! printf 'aX\r\nY\r\nb\r\n' | cmp -s - "$D/f.txt" && { echo "FAIL crlf: the saved file is not all CRLF ($mode)"; fail=1; }
    diff -q "$W/s.out" "screen/$n.expected" >/dev/null && echo "ok   screen $n ($mode)" || { echo "FAIL screen $n ($mode)"; fail=1; }
  done
done

# A real terminal: the caret and selection styles, resizing (needs python3; ~10 s).
for e in "" --tw; do
  python3 pty/check.py $e > "$W/pty.out" 2>&1 && echo "ok   pty (${e:-vm})" || { echo "FAIL pty (${e:-vm})"; cat "$W/pty.out"; fail=1; }
done

# The byte-exact round trip: open and save untouched.
for e in "" --tw; do
  for f in crlf:'a\r\nb\r\n' crlfnonl:'a\r\nb' mixed:'a\r\nb\nc\r\n' crend:'a\r\nb\r' nonl:'no newline' bom:'\xef\xbb\xbfbom\n' tabs:'tab\there\n\n\n' empty:''; do
    printf "${f#*:}" > "$W/in"; rm -f "$W/out"
    "$Z" run $e roundtrip.zy "$W/in" "$W/out" >/dev/null 2>&1
    cmp -s "$W/in" "$W/out" && echo "ok   round trip ${f%%:*} (${e:-vm})" || { echo "FAIL round trip ${f%%:*} (${e:-vm})"; fail=1; }
  done
done

# The cost of an edit, in both engines.
bash cost.sh || fail=1
exit $fail
