#!/bin/bash
# BUG-ZYE-013: what each engine makes of "\r" inside a string.
#
#   bash hypotheses/string_cr/check.sh
#
# ZYMBOL_BIN chooses the binary for the two Rust engines, ZYJS_HARNESS the browser
# engine's driver (web/ beside this checkout by default).
#
# Exit status: 0 the three engines agree (fixed), 1 the browser engine differs from the
# two Rust ones (the state on the day this was written), 2 an engine could not be run,
# 3 the two Rust engines disagree.
cd "$(dirname "$0")"
Z="${ZYMBOL_BIN:-zymbol}"
JS="${ZYJS_HARNESS:-../../../web/tests/run_one.mjs}"
command -v node >/dev/null && [ -f "$JS" ] || { echo "string_cr: no node, or no $JS"; exit 2; }

vm=$("$Z" run probe.zy 2>&1) || { echo "string_cr: zyvm could not run the probe"; exit 2; }
tw=$("$Z" run --tw probe.zy 2>&1) || { echo "string_cr: zytw could not run the probe"; exit 2; }
js=$(node "$JS" probe.zy < /dev/null 2>&1) || { echo "string_cr: zyjs could not run the probe"; exit 2; }
[ "$vm" = "$tw" ] || { echo "string_cr: zyvm and zytw disagree"; exit 3; }
echo "string_cr: zyvm, zytw: $(echo $vm)   zyjs: $(echo $js)"
[ "$vm" = "$js" ] && { echo "  BUG-ZYE-013  FIXED"; exit 0; }
echo "  BUG-ZYE-013  HOLDS"; exit 1
