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
		print "create new db pool connection"
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
        ssn = sessions.newSession(data['user'])
        return json.dumps({"status":"OK","token":ssn.token,\
                "user":ssn.username,\
                "created":ssn.created_at})

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

class RequestParameterError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DBQueryError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

        
# cache request db conn inthe "app" context
def get_db():
	if not hasattr(g,"oracledb"):
		#g.oracledb = cx_Oracle.connect("ilm","identity","PRODI04")
		g.oracledb = dbpool.getConn()
		app.logger.info("get db conn from pool")
	return g.oracledb


class wrapResponse:
    def __init__(self,c):
#        app.logger.info("wrapResponse.__init__")
#        app.logger.info("colinfo="+str(c.description))
        self.colnames = []
        for x in c.description:
            self.colnames.append(x[0])
        app.logger.info("columns="+str(self.colnames))
#        self.colndx = {}
#        for i in range(0,len(self.colnames)):
#            self.colndx[self.colnames[i]]=i
#        app.logger.info("colndx="+self.colndx)
        self.rows = []
        for r in c:
#            app.logger.info("r="+str(r))
            self.rows.append(r)
        app.logger.info("DbQuery returned %d rows" % (len(self.rows)))

    def __iter__(self):
#        app.logger.info("__iter__")
        self.currndx = 0
        return self
        
    def next(self):
#        app.logger.info("next: %d" % (self.currndx,))
        if self.currndx < len(self.rows):
            r = self.rows[self.currndx]
            self.currndx = self.currndx+1
            return dict(zip(self.colnames,r))
        else:
            raise StopIteration

#
# query handler with exception handling...
def doQuery(qs,plist=None):
	try:
		db = get_db()
		curs = db.cursor()
		app.logger.info(qs)
		if plist != None:
			print "execute with plist=",plist
			curs.execute(qs,plist)
		else:
			curs.execute(qs)
		app.logger.info("query returns...")
		rlist = []
		rsp = wrapResponse(curs)
		app.logger.info("response wrapped")
		dbpool.freeConn(db)
		return rsp
	except:
	    app.logger.info("caught db exception...")
	    app.logger.info(str(sys.exc_info()))
	    raise DBQueryError("dbQuery exception")


        
def getInstitutionId(data):
    return {'institution':{'institutionCode':111,'institutionLabel':'DUT'}}

def getCollegeId(data):
    return {'colleges': [ \
                {'code':'ACAD','label':'Academic/Subsidy-bearing'},\
                {'code':'CCPE','label':'Centre for Continuing and Professional Education'},\
            ]}

def getCollegeFacultiesId(data):
    app.logger.info("getCollegeFacultiesId"+json.dumps(data))
    code = data['collegeCode']
    if code in ['ACAD']:
        qs = "select * from GEN.GAEFAC where GAECODE in ('31','32','33','34','35','36')"
        rs = doQuery(qs)
        rlist = []
        for r in rs:
            app.logger.info("r="+str(r))
            rr = {'code':r['GAECODE'],'label':r['GAENAME']}
            rlist.append(rr)
        rsp = {'faculties':rlist}
        return rsp
    else:
        raise RequestParameterError("collegeCode %s is not known" % (code,))

def getFacultyDisciplinesId(data):
    app.logger.info("getFacultyDisciplnesId"+json.dumps(data))
    code = data['facultyCode']
    qs = "select * from GEN.GACDPT where GACFACT=:1"
    rs = doQuery(qs,(code,))
#    qs = "select * from GEN.GACDPT where GACFACT='%s'" % (code,)
#    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        rr = {'code':r['GACCODE'],'label':r['GACNAME']}
        rlist.append(rr)
    rsp = {'faculties':rlist}
    return rsp

def getDisciplineProgrammesId(data):
    app.logger.info("getDisciplineProgrammesId"+json.dumps(data))
    code = data['disciplineCode']
    aYear = '2018'
    qs = "select * from STUD.IAIQAL where IAIDEPT=:1 and IAICYR=:2"
    rs = doQuery(qs,(code,aYear))
#    qs = "select * from GEN.GACDPT where GACFACT='%s'" % (code,)
#    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        rr = {'programmeCode':r['IAIQUAL'],'programmeLabel':r['IAIDESC'],
                'majorCode':'???','majorLabel':'???'
        }
        rlist.append(rr)
    rsp = {'programmes':rlist}
    return rsp

def getProgrammeStudents(data):
    app.logger.info("getProgrammeStudents"+json.dumps(data))
    programmeCode = data['programmeCode']
    year = data['year']
    session = data['session']
    #
    # map to IAGBC
    if session == '0':
        bclist = "('11','21')" # check for ET / PG blocks
    if session == '1':
        bclist = "('11','22')"
    else:
        bclist = "('11')"
    
    qs = """select IAGSTNO,IADSURN,IADNAMES 
            from STUD.IAGENR, STUD.IADBIO
            where IAGSTNO=IADSTNO
            and IAGQUAL=:1
            and IAGCYR=:2
            and IAGBC in %s""" % (bclist,)
    rs = doQuery(qs,(programmeCode,year))
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        rr = {'studentNumber':r['IAGSTNO'],'majorCode':'???',\
                'lastName':r['IADSURN'],'firstNames':r['IADNAMES']}
        rlist.append(rr)
    rsp = {'students':rlist}
    return rsp
    
def getStudentProgrammeRegistrations(data):
    app.logger.info("getStudentProgrammeRegistrations"+json.dumps(data))
    studentList = data['studentList']
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select IAGSTNO,IAGCYR,IAGBC,IAGQUAL from STUD.IAGENR
            where IAGSTNO in (%s)
            order by IAGSTNO,IAGCYR,IAGBC""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        bc = r['IAGBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rr = {'studentNumber':r['IAGSTNO'],'year':r['IAGCYR'],'session':session,'programmeCode':r['IAGQUAL'],'majorCode':'???'}
        rlist.append(rr)
    rsp = {'registrations':rlist}
    return rsp
    
def getStudentFinalCourseResults(data):
    app.logger.info("getStudentFinalCourseResults"+json.dumps(data))
    studentList = data['studentList']
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES 
            from STUD.IAHSUB
            where IAHSTNO in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        bc = r['IAHBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rcode = r['IAHERES']  #TODO -- fix mapping of result code
        rr = {'studentNumber':r['IAHSTNO'],'year':r['IAHCYR'],'session':session,\
                'courseCode':r['IAHSUBJ'],'programmeCode':r['IAHQUAL'],\
                'result':r['IAHFMARK'],'resultCode':rcode}
        rlist.append(rr)
    rsp = {'finalResults':rlist}
    return rsp
    
def getAssessmentResults(data):
    app.logger.info("getAssessmentResults"+json.dumps(data))
    studentList = data['studentList']
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select JCHSTNO,JCHCYR,'??' as BC,JCHSUBJ,JCHMARKTYPE,JCHMARKNUMBER,JCHMARK 
            from STUD.JCHSTM
            where JCHSTNO in (%s)
            order by JCHSTNO,JCHCYR,JCHSUBJ""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        bc = r['BC']  # TODO -- figure out how to fix this!
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        assessmentCode = "%s.%d" % (r['JCHMARKTYPE'],r['JCHMARKNUMBER'])
        rr = {'studentNumber':r['JCHSTNO'],'year':r['JCHCYR'],'session':session,\
                'courseCode':r['JCHSUBJ'],\
                'assessmentCode':assessmentCode,'result':r['JCHMARK']}
        rlist.append(rr)
    rsp = {'assessmentResults':rlist}
    return rsp

def getStudentBioData(data):
    app.logger.info("getStudentBioData"+json.dumps(data))
    studentList = data['studentList']
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select IADSTNO,IADSURN,IADNAMES,IADBIRDAT,
                (IADBIRDAT-TO_DATE('01-01-1970 00:00:00', 'DD-MM-YYYY HH24:MI:SS'))*24*60*60 AS UTIME,
                IADSEX,IADETHN
            from STUD.IADBIO where IADSTNO in (%s)""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
        app.logger.info("r="+str(r))
        if r['IADSEX'] == 'M':
            isMale = True
        else:
            isMale = False
        rr = {'studentNumber':r['IADSTNO'],\
                'lastName':r['IADSURN'],'firstNames':r['IADNAMES'],\
                'dateOfBirth':r['UTIME'],\
                'genderIsMale':isMale,'ethnicity':r['IADETHN'],\
                'parentHighestAcademicQualification':'?',\
                'highSchoolFinalResult':'?'
        }
        rlist.append(rr)
    rsp = {'assessmentResults':rlist}
    return rsp



@app.route('/main',methods=['POST'])
def apiMain():
    non_auth_requests = {
        'getInstitutionId' : getInstitutionId,
        'getCollegeFacultiesId' : getCollegeFacultiesId,
        'getFacultyDisciplinesId' : getFacultyDisciplinesId,
        'getDisciplineProgrammesId': getDisciplineProgrammesId,
        'getProgrammeStudents':getProgrammeStudents,
        'getStudentProgrammeRegistrations':getStudentProgrammeRegistrations,
        'getStudentFinalCourseResults':getStudentFinalCourseResults,
        'getAssessmentResults':getAssessmentResults,
        'getStudentBioData':getStudentBioData
    }

    auth_requests = {
        'getCollegeId' : getCollegeId
    }

    try:
        data = request.get_json()
        print "/main, data=",data
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
            raise NoSuchAction("No handler found for action="+action)
        #
        # clean up and return
        rsp['status'] = 'OK'
        rsp['action'] = action
        return json.dumps(rsp)
    except NotLoggedInError as x:
        errmsg = x.value
        return json.dumps({'status':'ERR','msg':errmsg})
    except NoSuchAction as x:
        errmsg = x.value
        return json.dumps({'status':'ERR','msg':errmsg})
    except KeyError as x:
        errmsg = "missing property "+x.message
        return json.dumps({'status':'ERR','msg':errmsg})
    except:
        traceback.print_exc()
        msg = str(sys.exc_info())
        return json.dumps({'status':'ERR','msg':msg})

if __name__ == "__main__":
	app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8100)))

