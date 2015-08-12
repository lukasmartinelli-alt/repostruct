#!/bin/bash

mkdir -p results
(cd results && python -m http.server $PORT &)
python repostruct/clone-filepaths.py --rabbitmq | tee results/output.txt
