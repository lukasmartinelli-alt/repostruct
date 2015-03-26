#!/bin/bash
INPUT_LIST=${INPUT_LIST:-repostruct:repos}
OUTPUT_LIST=${OUTPUT_LIST:-repostruct:results}
BATCH_SIZE=${BATCH_SIZE:-40}

./redis-pipe --count $BATCH_SIZE $INPUT_LIST | ./repostruct.py | ./redis-pipe $OUTPUT_LIST
