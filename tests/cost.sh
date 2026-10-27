#!/bin/bash
# The cost of one edit must not grow with the size of the file (README, decision 1).
# One typed character and one Enter in the middle of a 100-line and a 10 000-line buffer,
# in both engines; an edit's cost is its `--count` minus the count with no edit. It grows
# when its steps differ between the two sizes, or when it copies or allocates for the
# larger one what it does not for the smaller (100 values copied, 50 000 bytes).
#
#   bash tests/cost.sh          -v prints every count
#
# Exit status: 0 the character holds, 1 it does not. The Enter costs the whole buffer
# today (BUG-ZYE-014), which is reported as KNOWN, and as a FAIL once it no longer does,
# so that the finding gets closed.
cd "$(dirname "$0")"
Z="${ZYMBOL_BIN:-zymbol}"

count() {   # engine flag, edit, n, field
    "$Z" run $1 --count cost.zy "$2" "$3" 2>&1 | grep -o "$4=[0-9]*" | cut -d= -f2
}
cost() {    # engine flag, edit, n, field -> the edit's share of the count
    echo $(( $(count "$1" "$2" "$3" "$4") - $(count "$1" none "$3" "$4") ))
}

fail=0
for e in "" --tw; do
    mode="${e:-vm}"
    for edit in char line; do
        s1=$(cost "$e" $edit 100 steps);   s2=$(cost "$e" $edit 10000 steps)
        c1=$(cost "$e" $edit 100 copied);  c2=$(cost "$e" $edit 10000 copied)
        b1=$(cost "$e" $edit 100 bytes);   b2=$(cost "$e" $edit 10000 bytes)
        [ "$1" = -v ] && echo "     $edit ($mode)  steps $s1 / $s2  copied $c1 / $c2  bytes $b1 / $b2"
        grows=no
        { [ "$s1" != "$s2" ] || [ $((c2 - c1)) -ge 100 ] || [ $((b2 - b1)) -ge 50000 ]; } && grows=yes
        if [ $edit = char ]; then
            [ $grows = no ] && echo "ok   cost of a character ($mode)" \
                || { echo "FAIL cost of a character grows with the file ($mode)"; fail=1; }
        else
            [ $grows = yes ] && echo "KNOWN cost of a line grows with the file ($mode): BUG-ZYE-014" \
                || { echo "FAIL cost of a line no longer grows ($mode): close BUG-ZYE-014"; fail=1; }
        fi
    done
done
exit $fail
