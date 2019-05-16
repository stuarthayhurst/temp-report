#!/bin/bash
curl -s https://api.github.com/repos/dragon8oy/temp-report/releases/latest | grep "tag_name" | cut -d v -f 2,3 | tr -d \",
