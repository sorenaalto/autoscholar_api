#!/usr/bin/env python
import os
from flask import Flask,request,render_template,jsonify
from flask import g
from flask_cors import CORS, cross_origin

import json
import string

import cx_Oracle
from dbpool import dbPool

import sys
import atexit
import traceback

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

# cache request db conn inthe "app" context
def get_db():
	if not hasattr(g,"oracledb"):
		#g.oracledb = cx_Oracle.connect("ilm","identity","PRODI04")
		g.oracledb = dbpool.getConn()
		app.logger.info("get db conn from pool")
	return g.oracledb

# end of request, free the connection when request ends
@app.teardown_appcontext
def close_db(error):
	if hasattr(g,"oracledb"):
#		g.oracledb.close()
		dbpool.freeConn(g.oracledb)
		app.logger.info("teardown: freeing db connection")

#
# canonical db response, stat=OK, cols, rows
def wrapResponse(c):
	cols = [i[0] for i in c.description]
	rows = []
	for row in c:
		rows.append(row)
	app.logger.debug("added %d rows" % (len(rows)))
	return {'stat':'OK','cols':cols,'rows':rows}

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
		rsp = wrapResponse(curs)
	
		return jsonify(rsp)
	except:
		app.logger.warn("doQuery: exception"+str(sys.exc_info()))
		traceback.print_exc()		
		return jsonify({'stat':'ERR','info': str(sys.exc_info())})
	

@app.route('/')
def info():
	return "Autoscholar REST API integration service"

#
# individual queries...

#1.       Return a list of all programmes within a faculty for a given year (year and faculty id can be an input parameter). The result should have rows with the id of the programme and the label of the programme.

@app.route('/QualificationList/<int:year>/<fcode>')
@cross_origin()
def QualList(year,fcode):
	app.logger.info("QualList(%d,%s)" % (year,fcode))
	qs = """select IAIQUAL as Qualcode, IAIDESC as Qualname,
					IAIFAC as Faccode, GAENAME as Facname,
					IAIDEPT as Depcode,GACNAME as Depname 
			from STUD.IAIQAL, GEN.GAEFAC, GEN.GACDPT
			where IAIFAC=GAECODE and IAIDEPT=GACCODE 
			and IAICYR=:1 and IAIFAC=:2
		"""
    	return doQuery(qs,(year,fcode))

#2.       Return a list of all students registered in an academic programme in a particular year (inputs would be year and programme code). The result can be just student numbers.

@app.route('/StudentsRegisteredInQual/<int:year>/<qualcode>')
@cross_origin()
def StudentsInQual(year,qualcode):
	app.logger.info("StudentsInQual(%d,%s)" % (year,qualcode))
	qs = """select IAGSTNO as STUDNUM 
			from STUD.IAGENR
			where IAGCYR=:1 and IAGQUAL=:2 
			and IAGCANCELDATE is NULL and IAGPRIMARY='Y'
		"""
    	return doQuery(qs,(year,qualcode))
    	
#2.5 what about a version of this that returns a JSON list of numbers (which could be
# used directly in the calls taking a list as a parameter)

#3.       Return the biographical data for an array of student numbers

@app.route('/StudentBioList')
@cross_origin()
def StudentBioList():
	listvals = json.loads(request.args.get("snums"))
	# convert list to a string as OracleCX driver won't deal with this
	slist = "("+string.join([str(x) for x in listvals],",")+")"
	# now use these in a query...
	qs = """select IADSTNO,IADSURN,IADINIT,IADIDNO,IADCAONUM
			from STUD.IADBIO
			where IADSTNO in %s""" % (slist)
	return doQuery(qs)

#4.       Return all course final results for an array of student numbers. The list should have student number, course id and final mark.

@app.route('/StudentFinalResults')
@cross_origin()
def StudentFinalResults():
	listvals = json.loads(request.args.get("snums"))
	# convert list to a string as OracleCX driver won't deal with this
	slist = "("+string.join([str(x) for x in listvals],",")+")"
	# now use these in a query...
	qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IALDESC,
				IAHYMARK,IAHEMARK,IAHFMARK,IAHERES
			from STUD.IAHSUB,STUD.IALSUB
			where IAHCYR=IALCYR and IAHSUBJ=IALSUBJ 
			and IAHSTNO in %s
			order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ
			""" % (slist)
	return doQuery(qs)

#5.       Return the course meta data when given an array of course ids. The result should have course id, course label, credits, category (normal, mother, sub)

@app.route('/SubjectInfo/<int:year>')
@cross_origin()
def SubjectInfo(year):
	subjcodes = request.args.get("subjcodes")
	print "subjcodes=",subjcodes
	listvals = json.loads(subjcodes)
	# convert list to a string as OracleCX driver won't deal with this
	slist = "("+string.join(["'"+str(x)+"'" for x in listvals],",")+")"
	# now use these in a query...
	qs = """select IAHSTNO,IAHCYR,IAHBC,IAHSUBJ,IALDESC,
				IAHYMARK,IAHEMARK,IAHFMARK,IAHERES
			from STUD.IAHSUB,STUD.IALSUB
			where IAHCYR=IALCYR and IAHSUBJ=IALSUBJ 
			and IAHSTNO in %s
			order by IAHSTNO,IAHCYR,IAHBC,IAHSUBJ
			""" % (slist)
	qs = """select IALSUBJ as Subjcode, IALDESC as Subjname,
					IALFAC as Faccode, GAENAME as Facname,
					IALSCHOOLDEPT as Depcode,GACNAME as Depname,
					IALSTYPE as Subjtype, IALSUBJINV as ParentSubjcode
			from STUD.IALSUB, GEN.GAEFAC, GEN.GACDPT
			where IALFAC=GAECODE and IALSCHOOLDEPT=GACCODE 
			and IALSUBJ in %s
			and IALCYR=:1
		""" % (slist)
	print "qs=",qs

	return doQuery(qs,(year,))

#6.       Return all course assessment data for a list of students. The list should have student number, course id, assessment code, assessment number, and result.

@app.route('/StudentAssessmentResults')
@cross_origin()
def StudentAssessmentResults():
	listvals = json.loads(request.args.get("snums"))
	# convert list to a string as OracleCX driver won't deal with this
	slist = "("+string.join([str(x) for x in listvals],",")+")"
	# now use these in a query...
	qs = """select JCHSTNO,JCHCYR,JCHSUBJ,
				JCHMARKTYPE,JCHMARKNUMBER,JCHMARK,JCHRESULT
			from STUD.JCHSTM
			where JCHSTNO in %s
			order by JCHSTNO,JCHCYR,JCHSUBJ
			""" % (slist)
	return doQuery(qs)


#7.       Return the weightings of assessments toward the class mark of a course. Inputs would be couse id and year.
#8.       Similar to 7, return the weightings between the class mark and the exam for a given course in a given year.
 
@app.route('/NewSubjectsForDept/<int:year>/<dcode>')
@cross_origin()
def NewSubjectsForDept(year,dcode):
	qs = """select IALSUBJ,IALDESC,IAKQUAL,IAIDESC,IALFAC,IALSCHOOLDEPT,IALSTYPE 
			from STUD.IALSUB, STUD.IAKSUB, STUD.IAIQAL
			where  IALCYR=IAKCYR and IALSUBJ=IAKSUBJ
			and IAKCYR=IAICYR and IAKQUAL=IAIQUAL
			and IALCYR=2018 
			and IALSUBJ in
			(select IAKSUBJ from STUD.IAKSUB where IAKACTIVE='Y' group by IAKSUBJ having min(IAKCYR)=2018)
			and IALSCHOOLDEPT=3203
			and rownum<50"""
			
	qs = """select IALSUBJ,IALDESC,IAKQUAL,IAIDESC,
				IIBBC,IIBOT,
				IALFAC,IALSCHOOLDEPT,IALSTYPE 
			from STUD.IALSUB, STUD.IAKSUB, STUD.IAIQAL,STUD.IIBSBC
			where  IALCYR=IAKCYR and IALSUBJ=IAKSUBJ
			and IAKCYR=IAICYR and IAKQUAL=IAIQUAL
			and IAKCYR=IIBCYR and IAKSUBJ=IIBSUBJ
			and IALCYR=:1
			and IIBBC in ('11','21','22')
			and IALSUBJ in
				(select IAKSUBJ from STUD.IAKSUB 
				where IAKACTIVE='Y' 
				group by IAKSUBJ 
				having min(IAKCYR)=:2)
			and IALSCHOOLDEPT=:3
			and rownum<50"""

	return doQuery(qs,(year,year,dcode))
	
@app.route('/LecturersForSubject/<int:year>/<subjcode>')
@cross_origin()
def LecturersForSubject(year,subjcode):
	qs = """select IDDLECT,PAASUR,PAAINT
			from STUD.IDDSCG, PERSON.PAAPR1, PERSON.PAQSAL
			where IDDLECT=PAANUM
			and IDDLECT=PAQNUM and (PAQEDTE is NULL or PAQEDTE>SYSDATE)
			and IDDCYR=:1 and IDDSUBJ=:2
			group by IDDLECT,PAASUR,PAAINT
	"""

	return doQuery(qs,(year,subjcode))
	


	
if __name__ == "__main__":
	app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8100)))
