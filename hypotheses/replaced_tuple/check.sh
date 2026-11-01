#!/bin/bash
# BUG-ZYE-011: how much each engine copies, under --count, when a tuple taken out of an
# array has its slot replaced and what was inside it is then edited.
#
#   bash hypotheses/replaced_tuple/check.sh
#
# ZYMBOL_BIN chooses the binary. probe.zy is the minimal case and through_function.zy the
# shape the editor has it in; both must copy nothing for the finding to be FIXED. The two
# control_*.zy copy nothing in either engine today, and they must go on doing so.
#
# Exit status: 0 fixed, 1 holds (the VM copies, the tree-walker does not: the state on the
# day this was written), 2 a program could not be run, 4 something that copied nothing has
# started to copy (a control, or the tree-walker).
cd "$(dirname "$0")"
Z="${ZYMBOL_BIN:-zymbol}"

copied() {   # engine flag, file -> the number after copied=, or nothing
    "$Z" run $1 --count "$2" 2>&1 | grep -o 'copied=[0-9]*' | cut -d= -f2
}

echo "replaced_tuple: what each engine copies under --count"
status=0
for f in control_arrays.zy control_reassign.zy probe.zy through_function.zy; do
    vm=$(copied "" "$f"); tw=$(copied --tw "$f")
    if [ -z "$vm" ] || [ -z "$tw" ]; then
        echo "replaced_tuple: $f could not be run"; exit 2
    fi
    echo "  $f  zyvm copied=$vm  zytw copied=$tw"
    case "$f" in
        control_*) { [ "$vm" != 0 ] || [ "$tw" != 0 ]; } && status=4 ;;
        *)         [ "$tw" != 0 ] && status=4
                   [ "$vm" != 0 ] && [ "$status" = 0 ] && status=1 ;;
    esac
done
case $status in
    0) echo "  BUG-ZYE-011  FIXED" ;;
    1) echo "  BUG-ZYE-011  HOLDS" ;;
    4) echo "  a program that copied nothing now copies: a regression, not this finding" ;;
esac
exit $status
