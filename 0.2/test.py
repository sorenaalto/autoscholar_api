#!/usr/bin/env python

import requests
import json
import sys

data = json.load(sys.stdin)

r = requests.post("http://localhost:8080/main",json=data)

#print r.status_code
print r.text
