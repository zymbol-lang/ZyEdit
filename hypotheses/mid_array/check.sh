#!/bin/bash
# BUG-ZYE-014: what one edit in the middle of a 10 000-element array costs, under --count.
#
#   bash hypotheses/mid_array/check.sh
#
# ZYMBOL_BIN chooses the binary. Each edit runs once and twice; the difference is one edit.
# It "costs the array" when that difference is a copy of 1 000 values or more (the
# tree-walker's `copied`) or 50 000 bytes or more (the VM, whose `copied` stays 0 because
# it builds a new array rather than copying the old one). insert and remove_range are the
# finding; remove and replace cost one element today, and are the controls.
#
# Exit status: 0 fixed, 1 holds (the state on the day this was written), 2 the probe could
# not be run, 4 a control has started to cost the array.
cd "$(dirname "$0")"
Z="${ZYMBOL_BIN:-zymbol}"

field() {   # engine flag, op, k, field -> its number
    "$Z" run $1 --count probe.zy "$2" "$3" 2>&1 | grep -o "$4=[0-9]*" | cut -d= -f2
}

echo "mid_array: one edit in the middle of 10 000 elements, zyvm and zytw"
status=0
for op in remove replace insert remove_range; do
    b1=$(field "" $op 1 bytes); b2=$(field "" $op 2 bytes)
    c1=$(field --tw $op 1 copied); c2=$(field --tw $op 2 copied)
    if [ -z "$b1" ] || [ -z "$b2" ] || [ -z "$c1" ] || [ -z "$c2" ]; then
        echo "mid_array: $op could not be run"; exit 2
    fi
    bytes=$((b2 - b1)); copied=$((c2 - c1))
    whole=no; { [ $bytes -ge 50000 ] || [ $copied -ge 1000 ]; } && whole=yes
    echo "  $op  zyvm bytes=$bytes  zytw copied=$copied  costs the array: $whole"
    case "$op" in
        remove|replace) [ $whole = yes ] && status=4 ;;
        *)              [ $whole = yes ] && [ $status = 0 ] && status=1 ;;
    esac
done
case $status in
    0) echo "  BUG-ZYE-014  FIXED" ;;
    1) echo "  BUG-ZYE-014  HOLDS" ;;
    4) echo "  an edit that cost one element now costs the array: a regression, not this finding" ;;
esac
exit $status
