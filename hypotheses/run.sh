#!/usr/bin/env bash
# hypotheses/run.sh — every design hypothesis, both Rust engines, one verdict.
#
#   bash hypotheses/run.sh
#
# Exit status: 0 every finding is fixed, 1 at least one holds, 2 or more a
# check could not give a verdict (see hypotheses/README.md).

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

worst=0
for check in "$HERE"/*/check.py; do
    python3 "$check"
    status=$?
    (( status > worst )) && worst=$status
done
exit "$worst"
