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
from asSessions import authSessions

import sys
import atexit
import traceback

import pprint

import uuid

pp = pprint.PrettyPrinter(indent=4)

print "Starting..."

app = Flask("autoscholar-api")
CORS(app)

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
logsessions = authSessions()
logsessions.setLogger(app.logger)

@app.route('/')
def info():
	return "Autoscholar REST API integration service"

@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        print data
        print type(data)
        ssn = sessions.newSession(data['userId'])
        return json.dumps({"status":1,"logToken":ssn.token,\
                "userId":ssn.username,\
                "created":ssn.created_at})

#
# backdoor accounts for testing
backdoor_accounts = {
    "aLecturer" : {
        "userId" : "aLecturer",
        "pwd" : "IamLecturer",
        "mtype": 4
    },
    "aStudent" : {
        "userId" : "aStudent",
        "pwd" : "IamStudent",
        "mtype": 0
    }
}

@app.route('/login2',methods=['POST'])
def login2():
    app.logger.info("login2")
    if request.method == 'POST':
        app.logger.info("request.method==POST")
        data = request.get_json()
        print data
        print type(data)
        #
        # backdoor
        userId = data['userId']
        passwd = data['pwd']
        if userId in backdoor_accounts:
            acct_info = backdoor_accounts[userId]
            if passwd == acct_info["pwd"]:
                ssn = sessions.newSession(userId)
                ssn.memberType = acct_info["mtype"]
                return json.dumps({"status":1,"logToken":ssn.token,\
                    "memberType":ssn.memberType,\
                    "userId":ssn.username,\
                    "created":ssn.created_at})
            else:    
                return json.dumps({"status":0,"msg":"invalid login"})
                
        ssn = logsessions.loginSession(data['userId'],data['pwd'])
        if ssn == None:
            return json.dumps({"status":0,"msg":"invalid login"})
        else:
            #
            # try and get staff or student number
            
            return json.dumps({"status":1,"logToken":ssn.token,\
                "memberType":ssn.memberType,\
                "userId":ssn.username,\
                "created":ssn.created_at})


@app.route('/dumpsessions')
def dumpSessions():
    smap = sessions.getSessions()
    ssnlist = {}
    for k in smap:
        ssn = smap[k]
        ssnlist[k] = ssn.asString()
    return json.dumps({ "responseStatus":1,"sessions":ssnlist})

@app.route('/dumpsessions2')
def dumpSessions2():
    smap = logsessions.getSessions()
    ssnlist = {}
    for k in smap:
        ssn = smap[k]
        ssnlist[k] = ssn.asString()
    return json.dumps({ "responseStatus":1,"sessions":ssnlist})



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
	    dbpool.freeConn(db)
	    raise DBQueryError("dbquery exception"+str(sys.exc_info()))
	    

def getInstitutionId(data):
    return {'institution':{'institutionCode':'ZA-DUT','institutionLabel':'Durban University of Technology'}}

def getCollegeId(data):
    return {'colleges': [ \
                {'code':'ACAD','label':'Academic/Subsidy-bearing'},\
                {'code':'CCPE','label':'Centre for Continuing and Professional Education'},\
            ]}

def getCollegeFacultiesId(data):
#    app.logger.info("getCollegeFacultiesId"+json.dumps(data))
    code = data['collegeCode']
    if code in ['ACAD']:
        qs = "select * from GEN.GAEFAC where GAECODE in ('31','32','33','34','35','36')"
        rs = doQuery(qs)
        rlist = []
        for r in rs:
            app.logger.info("r="+str(r))
            rr = {'code':str(r['GAECODE']),'label':r['GAENAME']}
            rlist.append(rr)
        rsp = {'faculties':rlist}
        return rsp
    else:
        raise RequestParameterError("collegeCode %s is not known" % (code,))

def getFacultyDisciplinesId(data):
#    app.logger.info("getFacultyDisciplnesId"+json.dumps(data))
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
    rsp = {'disciplines':rlist}
    return rsp

def getDisciplineProgrammesId(data):
#    app.logger.info("getDisciplineProgrammesId"+json.dumps(data))
    code = data['disciplineCode']
    aYear = '2018'
    qs = "select * from STUD.IAIQAL where IAIDEPT=:1 and IAICYR=:2"
    rs = doQuery(qs,(code,aYear))
#    qs = "select * from GEN.GACDPT where GACFACT='%s'" % (code,)
#    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
        rr = {'programmeCode':r['IAIQUAL'],'programmeLabel':r['IAIDESC'],
                'majorCode':-1,'majorLabel':-1
        }
        rlist.append(rr)
    rsp = {'programmes':rlist}
    return rsp

def getProgrammeStudents(data):
#    app.logger.info("getProgrammeStudents"+json.dumps(data))
    programmeCode = data['programmeCode']
    year = data['year']
    session = data['session']
    #
    # map to IAGBC
    if str(session) == '0':
        bclist = "('11','21')" # check for ET / PG blocks
    if str(session) == '1':
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
#        app.logger.info("r="+str(r))
        rr = {'studentNumber':r['IAGSTNO'],'majorCode':-1,\
                'lastName':r['IADSURN'],'firstNames':r['IADNAMES']}
        rlist.append(rr)
    rsp = {'students':rlist}
    return rsp
    
def getStudentProgrammeRegistrations(data):
#    app.logger.info("getStudentProgrammeRegistrations"+json.dumps(data))
    studentList = data['studentList']
    if len(studentList)<1:
        raise RequestParameterError("studentList must not be empty")
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select IAGSTNO,IAGCYR,IAGBC,IAGQUAL from STUD.IAGENR
            where IAGSTNO in (%s)
            order by IAGSTNO,IAGCYR,IAGBC""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
        bc = r['IAGBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rr = {'studentNumber':r['IAGSTNO'],'year':r['IAGCYR'],'session':session,'programmeCode':r['IAGQUAL'],'majorCode':-1}
        rlist.append(rr)
    rsp = {'registrations':rlist}
    return rsp
    
def getStudentFinalCourseResults(data):
#    app.logger.info("getStudentFinalCourseResults"+json.dumps(data))
    studentList = data['studentList']
    if len(studentList)<1:
        raise RequestParameterError("studentList must not be empty")
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES 
            from STUD.IAHSUB
            where IAHSTNO in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % slistS
            
    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES,IAKCREDIT*128 as SAPSECREDIT
            from STUD.IAHSUB,STUD.IAKSUB
            where IAHCYR=IAKCYR and IAHSUBJ=IAKSUBJ and IAHQUAL=IAKQUAL and IAHOT=IAKOT
            and IAHSTNO in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % slistS
    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
        bc = r['IAHBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rcode = r['IAHERES']  #TODO -- fix mapping of result code
        rr = {'studentNumber':r['IAHSTNO'],'year':r['IAHCYR'],'session':session,\
                'courseCode':r['IAHSUBJ'],'courseCredits':r['SAPSECREDIT'],'programmeCode':r['IAHQUAL'],\
                'result':r['IAHFMARK'],'resultCode':rcode}
        rlist.append(rr)
    rsp = {'finalResults':rlist}
    return rsp
    
def squote(x):
    return "'%s'" % (x,)

def getStudentSessionResults(data):
#    app.logger.info("getStudentFinalCourseResults"+json.dumps(data))
    studentList = data['studentList']
    if len(studentList)<1:
        raise RequestParameterError("studentList must not be empty")
    #
    # TODO: will need paged queries for long lists
    slistS = ",".join([str(x) for x in studentList])
    qyear = data['year']
    session = data['session']
    
    # check these lists -- and refactor into a utility function
    if session == 0:
        bclist = ['11','21']
    else:
        bclist = ['22']

    bclistS = ",".join([squote(x) for x in bclist])

    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES 
            from STUD.IAHSUB
            where IAHSTNO in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % slistS
            
    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES,IAKCREDIT*128 as SAPSECREDIT
            from STUD.IAHSUB,STUD.IAKSUB
            where IAHCYR=IAKCYR and IAHSUBJ=IAKSUBJ and IAHQUAL=IAKQUAL and IAHOT=IAKOT
            and IAHSTNO in (%s)
            and IAHCYR=%s
            and IAHBC in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % (slistS,qyear,bclistS)
    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
        bc = r['IAHBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rcode = r['IAHERES']  #TODO -- fix mapping of result code
        rr = {'studentNumber':r['IAHSTNO'],'year':r['IAHCYR'],'session':session,\
                'courseCode':r['IAHSUBJ'],'courseCredits':r['SAPSECREDIT'],'programmeCode':r['IAHQUAL'],\
                'result':r['IAHFMARK'],'resultCode':rcode}
        rlist.append(rr)
    rsp = {'finalResults':rlist}
    return rsp


def getStudentFinalCourseResultsMulti(data):
#    app.logger.info("getStudentFinalCourseResultsMulti"+json.dumps(data))
    courseList = data['courseList']
    yearList = data['yearList']
    if len(courseList)<1:
        raise RequestParameterError("courseList must not be empty")
    if len(yearList)<1:
        raise RequestParameterError("yearList must not be empty")
    #
    # TODO: will need paged queries for long lists
    clistS = ",".join(["'%s'" % (str(x),) for x in courseList])
    ylistS = ",".join(["'%s'" % (str(x),) for x in yearList])

    qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IAHQUAL,IAHFMARK,IAHERES,IAKCREDIT*128 as SAPSECREDIT
            from STUD.IAHSUB,STUD.IAKSUB
            where IAHCYR=IAKCYR and IAHSUBJ=IAKSUBJ and IAHQUAL=IAKQUAL and IAHOT=IAKOT
            and IAHSUBJ in (%s)
            and IAHCYR in (%s)
            order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ""" % (clistS,ylistS)
            
    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
        bc = r['IAHBC']
        if bc in ['11','21']:
            session = 0
        if bc in ['22']:
            session = 1
        else:
            session = 0
        rcode = r['IAHERES']  #TODO -- fix mapping of result code
        rr = {'studentNumber':r['IAHSTNO'],'year':r['IAHCYR'],'session':session,\
                'courseCode':r['IAHSUBJ'],'courseCredits':r['SAPSECREDIT'],'programmeCode':r['IAHQUAL'],\
                'result':r['IAHFMARK'],'resultCode':rcode}
        rlist.append(rr)
    rsp = {'finalResults':rlist}
    return rsp

    
def getAssessmentResults(data):
#    app.logger.info("getAssessmentResults"+json.dumps(data))
    studentList = data['studentList']
    if len(studentList)<1:
        raise RequestParameterError("studentList must not be empty")

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
#        app.logger.info("r="+str(r))
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

def getAssessmentResultsMulti(data):
#    app.logger.info("getAssessmentResultsMulti"+json.dumps(data))
    courseList = data['courseList']
    yearList = data['yearList']
    if len(courseList)<1:
        raise RequestParameterError("courseList must not be empty")
    if len(yearList)<1:
        raise RequestParameterError("yearList must not be empty")
    #
    # TODO: will need paged queries for long lists
    clistS = ",".join(["'%s'" % (str(x),) for x in courseList])
    ylistS = ",".join(["'%s'" % (str(x),) for x in yearList])

    qs = """select JCHSTNO,JCHCYR,'??' as BC,JCHSUBJ,JCHMARKTYPE,JCHMARKNUMBER,JCHMARK 
            from STUD.JCHSTM
            where JCHSUBJ in (%s)
            and JCHCYR in (%s)
            order by JCHSTNO,JCHCYR,JCHSUBJ""" % (clistS,ylistS)
    rs = doQuery(qs)
    rlist = []
    for r in rs:
#        app.logger.info("r="+str(r))
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
#    app.logger.info("getStudentBioData"+json.dumps(data))
    studentList = data['studentList']
    if len(studentList)<1:
        raise RequestParameterError("studentList must not be empty")

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
#        app.logger.info("r="+str(r))
        if r['IADSEX'] == 'M':
            isMale = True
        else:
            isMale = False
        rr = {'studentNumber':r['IADSTNO'],\
                'lastName':r['IADSURN'],'firstNames':r['IADNAMES'],\
                'dateOfBirth':r['UTIME'],\
                'genderIsMale':isMale,'ethnicity':r['IADETHN'],\
                'parentHighestAcademicQualification':-1,\
                'highSchoolFinalResult':-1
        }
        rlist.append(rr)
    rsp = {'studentBioData':rlist}
    return rsp



@app.route('/main',methods=['POST'])
def apiMain():
    g.reqid = str(uuid.uuid4())
    non_auth_requests = {
        'getInstitutionId' : getInstitutionId,
        'getCollegeFacultiesId' : getCollegeFacultiesId,
        'getFacultyDisciplinesId' : getFacultyDisciplinesId,
        'getDisciplineProgrammesId': getDisciplineProgrammesId,
        'getProgrammeStudents':getProgrammeStudents,
        'getStudentProgrammeRegistrations':getStudentProgrammeRegistrations,
        'getStudentFinalCourseResults':getStudentFinalCourseResults,
        'getStudentFinalCourseResultsMulti':getStudentFinalCourseResultsMulti,
        'getStudentSessionResults':getStudentSessionResults,
        'getAssessmentResults':getAssessmentResults,
        'getAssessmentResultsMulti':getAssessmentResultsMulti,
        'getStudentBioData':getStudentBioData
    }

    auth_requests = {
        'getCollegeId' : getCollegeId
    }

    try:
        xff = request.headers.get("X-Forwarded-for")
        app.logger.info("/main: X-Forwarded-for "+xff)
        data = request.get_json()
        if data == None:
            raise NoSuchAction('Empty JSON request body')
        app.logger.info("/main: "+json.dumps(data))
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
        rsp['responseStatus'] = 1
        rsp['action'] = action
        rsp['reqId'] = g.reqid
        return json.dumps(rsp)
    except NotLoggedInError as x:
        errmsg = x.value
        return json.dumps({'responseStatus':0,'reqId':g.reqid,'msg':errmsg})
    except NoSuchAction as x:
        errmsg = x.value
        return json.dumps({'responseStatus':0,'reqId':g.reqid,'msg':errmsg})
    except RequestParameterError as x:
        errmsg = x.value
        return json.dumps({'responseStatus':0,'reqId':g.reqid,'msg':errmsg})
    except KeyError as x:
        errmsg = "missing property "+x.message
        return json.dumps({'responseStatus':0,'reqId':g.reqid,'msg':errmsg})
    except:
        traceback.print_exc()
        errmsg = str(sys.exc_info())
        return json.dumps({'responseStatus':0,'reqId':g.reqid,'msg':errmsg})

if __name__ == "__main__":
	app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8100)))

