#!/usr/bin/env bash

while true
do
  ps -aux | grep xunhui | grep python | grep -v grep | awk '{print $2}' | xargs kill -9
  nohup python -u ci_results.py > ci_results.log 2>&1 &
  sleep 10000
done