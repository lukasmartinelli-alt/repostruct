#!/bin/bash
RESULT_LIST=${RESULT_LIST:-repostruct:results}
INTERVAL=10
OUTPUT_FILE=${1:-results.txt}

while sleep $INTERVAL; do ./redis-pipe $RESULT_LIST >> $OUTPUT_FILE; done
