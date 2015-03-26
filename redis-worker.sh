#!/bin/bash
LIST_NAME=${LIST_NAME:-repostruct:repos}
BATCH_SIZE=${BATCH_SIZE:-40}

redis-pipe --count $BATCH_SIZE $LIST_NAME | python repostruct.py | redis-pipe $LIST_NAME
