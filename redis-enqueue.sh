#!/bin/bash
INPUT_FILE=$1
OUTPUT_LIST=${OUTPUT_LIST:-repostruct:results}

cat $INPUT_FILE | ./redis-pipe $OUTPUT_LIST
