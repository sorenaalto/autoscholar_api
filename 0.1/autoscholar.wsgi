#!/usr/bin/python
import sys
sys.path.insert(0, '/var/www/html/ide/codiad/workspace/flask-api')
import os
os.environ['LD_LIBRARY_PATH']='/opt/oracle/instantclient_12_1/'
from autoscholar_api import app as application
