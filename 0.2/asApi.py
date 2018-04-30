#!/usr/bin/env python
import os
from flask import Flask,request,render_template,jsonify
from flask import g
from flask_cors import CORS, cross_origin

import json
import string

import cx_Oracle
from dbpool import dbPool
from asSessions import asSessions

import sys
import atexit
import traceback

import pprint

pp = pprint.PrettyPrinter(indent=4)

print "Starting..."

app = Flask("autoscholar-api")

# my own quick-and-dirty db conn pool
class myDbPool(dbPool):
	def makeNewConn(self):
		c = cx_Oracle.connect("ilm","identity01","PRODI04")
		return c

dbpool = myDbPool(3)

# close all the free connections when the app is
# restarted during testing...
def closePoolConns():
	dbpool.closeAllConns()
	
atexit.register(closePoolConns)

#
# manage sessions / auth
sessions = asSessions()

@app.route('/')
def info():
	return "Autoscholar REST API integration service"

@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        print data
        print type(data)
        token = sessions.newSession(data['user'])
        return "OK logged in as ssn_id=",token

@app.route('/dumpsessions')
def dumpSessions():
    print sessions.getSessions()
    return "OK"

@app.route('/session',methods=['POST'])
def dumpMySession():
    data = request.get_json()
    ssn = sessions.findSession(data["token"])
    return ssn.asString()
    
class NotLoggedInError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class NoSuchAction(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


        
def getInstitutionId(data):
    return {'institution':{'institutionCode':111,'institutionLabel':'DUT'}}

def getCollegeId(data):
    return {'colleges': [ \
                {'code':'ACAD','label':'Academic/Subsidy-bearing'},\
                {'code':'CCPE','label':'Centre for Continuing and Professional Education'},\
            ]}




@app.route('/main',methods=['POST'])
def apiMain():
    non_auth_requests = {
        'getInstitutionId' : getInstitutionId
    }

    auth_requests = {
        'getCollegeId' : getCollegeId
    }

    try:
        data = request.get_json()
        action = data['action']
        print "Action=",action
        token = data['token']
        ssn = sessions.findSession(token)
        if action in non_auth_requests:
            rsp = non_auth_requests[action](data)
        elif action in auth_requests:
            if ssn == None:
                raise NotLoggedInError("Not logged in")
            rsp = auth_requests[action](data)
        else:
            raise NoSuchAction(action)
        #
        # clean up and return
        rsp['status'] = 'OK'
        rsp['action'] = action
        return json.dumps(rsp)
    except Exception as x:
        errmsg = x.errmsg
        return json.dumps({'status':'ERR','msg':errmsg})

if __name__ == "__main__":
	app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8100)))

