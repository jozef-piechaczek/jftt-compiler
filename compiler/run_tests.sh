#!/bin/bash
FILES=../vm/tests/*.imp
RESULTS=../vm/tests/results/
for f in $FILES
do
    name=$(basename -- $f)
    python3 kompilator.py $f "${RESULTS}$name.mr"
done
