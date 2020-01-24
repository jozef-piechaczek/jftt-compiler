#!/bin/bash
FILES=../tests/*.imp
RESULTS=../tests/results/
for f in $FILES
do
    name=$(basename -- $f)
    python3 kompilator.py $f "${RESULTS}$name.mr"
done
