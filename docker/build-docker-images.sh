#! /usr/bin/bash

files=$(find "$PWD"/docker -name "handin-*")

for f in $files; do
  f=$(basename $f)
  docker build -f "$PWD/docker/$f/Dockerfile" -t "$f" "$PWD/docker/$f"
done
