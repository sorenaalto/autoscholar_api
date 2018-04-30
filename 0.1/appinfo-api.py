#!/usr/bin/env python
import os
from flask import Flask,request,render_template,jsonify
import json
import string

import sys
import cx_Oracle

print "Starting..."

# don't connect to Oracle until we are read
if True:
	c = cx_Oracle.connect("ilm","identity","PRODI04")
	#c = cx_Oracle.connect("ilm/identity@localhost:1521:prodi04.dut.ac.za")
	print c


#app = Flask(__name__)
app = Flask("appinfo-api")

@app.route('/')
def info():
	return "Assessment Marks"

@app.route('/main')
def main():
	return render_template('appmain.html')
	
@app.route('/test/listparm')
def listtest():
	listvals = json.loads(request.args.get("lvals"))
	# convert list to a string as OracleCX driver won't deal with this
	slist = "("+string.join([str(x) for x in listvals],",")+")"
	# now use these in a query...
	qs = """select IADSTNO,IADSURN,IADINIT,IADIDNO,IADCAONUM
			from STUD.IADBIO
			where IADSTNO in %s""" % (slist)
	curs = c.cursor()
	curs.execute(qs)
	rows = []
	for row in curs:
		rows.append(row)

#	rsp = json.dumps(rows)
#	return rsp
	return jsonify(rows)

@app.route('/applications/testq')
def testq():

	qs = """select IERSTNO,IERCYR,IERBC,IEROT,IERPERSTUDY,IERADMITS,
        	IAIQUAL,IAIFAC,IAIFAC,IAIDEPT,IAIDESC
			from STUD.IERAAD,STUD.IAIQAL
			where IERQUAL=IAIQUAL and IERCYR=IAICYR
			and rownum<20
			and IERCYR=2018"""	
	curs = c.cursor()
	curs.execute(qs)

	rows = []
	for row in curs:
		rows.append(row)

#	rsp = json.dumps(rows)
#	return rsp
	return jsonify(rows)

def updateDict(d,k,N,subd):
	if not k in d:
		d['counts'][k] = N
		# create subdictionary
		if subd != None:
			d[subd] = {'counts':{}}			
	else:
		d[k] = d[k]+N

statmap = {
	'WD' : 'Waiting', #	WAITING FOR DECISION
#	ET	ENTRANCE TEST/INTERVIEW/PORTFO
	'SL' : 'Pending',	# SHORTLISTED
	'SB' : 'Pending',	# STANDBY
	'RF' : 'Reject', #	REGRET PROGRAMME FULL
#	LA	LATE APPLICATION
#	AW	APPLICATION WITHDRAWN
#	DE	DATA CAPTURE ERROR
#	IH	INTERNATIONAL - SUPPLY HESA
#	IS	INTERNATIONAL - SUPPLY SAQA
	'AC' : 'CondOffer', #	ACCEPT DEPOSIT PAID - COND OFF
	'DP' : 'Reject',	 # APPLICANT DECLINED PLACE
	'AF' : 'FirmOffer', #	APPLICANT: FIRM ACC FIRM OFFER
	'NC' : 'Reject', #	NOT CONSIDERED
	'OW' : 'Reject', #	OFFER WITHDRAWN BY INST.
	'RP' : 'Reject', #	REGRET PROGRAM WILL NOT RUN
	'AA' : 'Admitted', #	ADMITTED FOR WEB REGISTRATION
	'AE' : 'Waitlist', #	PASSED ELIGIBILITY TEST
	'RC' : 'Reject', #	UNSUCCESSFUL-NOT IST CHOICE
	'AR' : 'Pending', #	AWAITING RESULTS
	'PE' : 'Pending', #	PENDING
#	IN	INTERVIEW/AUDITION/PORTFOLIO
	'FO' : 'FirmOffer', #	FIRM OFFER
	'RU' : 'Reject', #	REGRET UNSUCCESSFUL
	'CO' : 'CondOffer', #	COND OFFER (MUST MEET REQUIRE)
	'MA' :	'Reject', #FAILED MINIMUM AGE RESTRICTION
	'MS' :	'Reject', #FAILED MIN REQUIRED SCORE
	'RS' :	'Reject', #FAILED SUBJECT REQUIREMENTS
	'RG' :	'Reject', #FAILED GENERAL RULES
	'RQ' :	'Reject', #FAILED QUALIFICAT REQUIREMENTS
	'AD' :	'FirmOffer',#ACCEPT DEPOSIT PAID - FIRM OFF
	'AB' :	'FirmOffer',#ACCEPT DEP PAID-FIRM OFF FAID
	'AG' :	'FirmOffer',#ACCEPT DEP PAID-FIRM OFF RES
	'AH' :	'FirmOffer',#ACCPT DEP PD-FIRM OFF RES FAID
	'CF' :	'CondOffer',#COND OFFER - FINAID & RES
	'CR' :	'CondOffer',#COND OFFER - RES
	'DF' :	'Reject', #DECLINED - FUNDING
	'DH' :	'Reject', #DECLINED - HOUSING
	'OC' :	'Reject', #OFFER WITHDRAWN APPL NOT CONT
	'UP' :	'Reject', #UNSUCCESSFUL - INTERVIEW/TEST
#	'AS' :	APPLICATION SUSPENDED - CO HOD
	'CP' :	'CondOffer',#COND OFF DEP PD - MISSING DOC
	'CN' :	'CondOffer',#COND OFF DEP NPD - MISSING DOC
	'FP' :	'FirmOffer',#FIRM OFF DEP PD - MISSING DOC
	'CD' :	'CondOffer',#ACC COND OFF DEPOSIT NOT PAID
	'FN' :	'FirmOffer',#FIRM OFF DEP NPD - MISSING DOC
	'FD' : 'FirmOffer',#	ACC FIRM OFF DEPOSIT NOT PAID
#	AP	APPL ACCEPT FOR DIFF PROG
#	MT	MATURE AGE APPLICATION
	'PR' : 'Reject',	#NOT MET PROG RANKING CRITERIA
	'FR' : 'FirmOffer',#	FIRM OFFER - RES UNSUCCESSFUL
	'CU' : 'CondOffer',#	COND OFFER - RES UNSUCCESSFUL
#	CA	CONSIDERED FOR ALT PROG
	'RN' : 'Reject',#	REGRET PROG NO LONGER AVAIL
	'FF' : 'FirmOffer',#	FIRM OFFER - FINANCIAL AID
	'FA' : 'FirmOffer',#	ACC FIRM OFF DEPOSIT NOT PD FA
	'FB' : 'FirmOffer',#	FIRM OFF DEP PD -MISS DOC FA
	'FC' : 'FirmOffer',#	FIRM OFF DEP NPD -MISS DOC FA
	'FE' : 'CondOffer',#	COND OFFER - FINANCIAL AID
	'FG' : 'CondOffer',#	COND OFF DEP PD - FIN AID
	'FH' : 'CondOffer',#	COND OFF DEP NOT PD - FIN AID
	'FI' : 'CondOffer',#	COND OFF DEP PD -MISS DOC FA
	'FJ' : 'CondOffer',#	COND OFF DEP NPD -MISS DOC FA
	'WA' : 'Admitted',	#WALKIN STUDENT ACCEPTED
	'AN' : 'Admitted'	#ADMITTED BY ADMISSIONS DEPT
#	83	Entrance Test/Interview/Portfo
#	EI	ENTRANCE TEST/INTERVIEW/PORTFO
}

def mapStat(k,d):
	if k in statmap:
		return statmap[k]
	else:
		return "%s:%s" % (k,d)

def classifyStat(k):
	if k in statmap:
		return statmap[k]
	else:
		return "Other"

def tally(d,k,n):
	if k in d:
		d[k] = d[k]+n
	else:
		d[k] = n

def classTally(d,kc,ks,sn,N):
	if not kc in d:
		d[kc] = {}
		d[kc][ks] = [N,sn]
	else:
		if ks in d[kc]:
			N0 = d[kc][ks][0]
			d[kc][ks] = [N0+N,sn]
		else:
			d[kc] = {ks:[N,sn]}

			
		
def updateHierarchy(hdict,pnames,pdescs,pvalues,k,d,N):
	parent = hdict
	mk = mapStat(k,d)
#	mk = k
	for (p,d,n) in zip(pnames,pdescs,pvalues):
		if not n in parent:
			parent[n] = {p:[n,d],'counts':{}}
			#parent[n]['counts'][mk] = N
#			tally(parent[n]['counts'],mk,N)
			tclass = classifyStat(k)
			classTally(parent[n]['counts'],tclass,k,d,N)
			tally(parent[n]['counts'],'TOTAL',N)
		else:
#			tally(parent[n]['counts'],mk,N)
			tclass = classifyStat(k)
			classTally(parent[n]['counts'],tclass,k,d,N)
			tally(parent[n]['counts'],'TOTAL',N)
#			if k in parent[n]['counts']:
#				parent[n]['counts'][mk] = parent[n]['counts'][mk]+N
#			else:
#				parent[n]['counts'][mk] = N
		# next level in hierarchy
		parent = parent[n]

@app.route('/applications/byFac')
def summary():
	qs = """select IAIFAC,GAENAME,IAIDEPT,GACNAME,IERQUAL,IAIDESC,
				IERADMITS,IEUADMITSN,count(*) as N
			from STUD.IERAAD,STUD.IAIQAL,GEN.GACDPT,GEN.GAEFAC,STUD.IEUADM
			where IERQUAL=IAIQUAL and IERCYR=IAICYR
			and IAIFAC=GAECODE and IAIDEPT=GACCODE
			and IERADMITS=IEUADMITS
			and IERCYR=2018
			and IERPERSTUDY=1
			and rownum<1000
			group by IAIFAC,GAENAME,IAIDEPT,GACNAME,
				IERQUAL,IAIDESC,IERADMITS,IEUADMITSN"""	
	app.logger.warn("summary() -- start query"+qs)
	curs = c.cursor()
	curs.execute(qs)
	app.logger.warn("summary() -- query returns")

	col_names = [i[0] for i in curs.description]
	types = [i[1] for i in curs.description]

	rows = []
	facs = {'counts':{}}
	app.logger.warn("summary() -- iterate on row")
	for row in curs:
		rows.append(row)
		fac = row[0]
		fname = row[1]
		dep = row[2]
		dname = row[3]
		qual = row[4]
		qname = row[5]
		stat = row[6]
		sname = row[7]
		N = row[8]
		pnames = ['faculty','department','qual']
		pvalues = [fac,dep,qual]
		pdescs = [fname,dname,qname]
		updateHierarchy(facs,pnames,pdescs,pvalues,stat,sname,N)
#		updateDict(facs,stat,N,'deps')
#		updateDict(facs['deps'],stat,N,qual)
#		updateDict(facs['deps'][qual],stat,N,None)

	rsp = {'columns':col_names,'rows':rows}
#	rsp = json.dumps(rows)
#	return rsp
	return jsonify(facs)

def tallyStatusAndCategory(d,s,sn,N):
	c = classifyStat(s)
	if not c in d:
		d[c] = {'total':0,'stat':{}}
	d[c]['total'] = d[c]['total']+N
	if not s in d[c]['stat']:
		d[c]['stat'][s] = (0,sn)
	(a,b) = d[c]['stat'][s]
	d[c]['stat'][s] = (a + N,b)
#	else:
#		(N0,x) = d[c]['stat'][s]
#		N1 = N0 + N
#		d[c]['stat'][s] = (N1,x)

@app.route('/applications/allFaculties')
def faculties():
	qs = """select IAIFAC,GAENAME,
				IERADMITS,IEUADMITSN,count(*) as N
			from STUD.IERAAD,STUD.IAIQAL,GEN.GACDPT,GEN.GAEFAC,STUD.IEUADM
			where IERQUAL=IAIQUAL and IERCYR=IAICYR
			and IAIFAC=GAECODE and IAIDEPT=GACCODE
			and IERADMITS=IEUADMITS
			and IERCYR=2018
			and IERPERSTUDY=1
--			and rownum<5000
			group by IAIFAC,GAENAME,IERADMITS,IEUADMITSN"""	
	app.logger.warn("summary() -- start query"+qs)
	curs = c.cursor()
	curs.execute(qs)
	app.logger.warn("summary() -- query returns")
	app.logger.warn("summary() -- iterate on row")
	col_names = [i[0] for i in curs.description]
	rows = []
	facs = {'totals':{},'faculties':{}}
	for row in curs:
		rows.append(row)
		[fcode,fname,stat,sname,N] = row
		if not fcode in facs:
			facs['faculties'][fcode] = [fcode,fname,{}]
		tallyStatusAndCategory(facs['totals'],stat,sname,N)
		tallyStatusAndCategory(facs['faculties'][fcode][2],stat,sname,N)

	rsp = {'columns':col_names,'rows':rows}
	return jsonify(facs)

@app.route('/applications/departmentsInFaculty/<fcode>')
def departmentsForFaculty(fcode):
	qs = """select IAIFAC,GAENAME,IAIDEPT,GACNAME,
				IERADMITS,IEUADMITSN,count(*) as N
			from STUD.IERAAD,STUD.IAIQAL,GEN.GACDPT,GEN.GAEFAC,STUD.IEUADM
			where IERQUAL=IAIQUAL and IERCYR=IAICYR
			and IAIFAC=GAECODE and IAIDEPT=GACCODE
			and IERADMITS=IEUADMITS
			and IERCYR=2018
			and IERPERSTUDY=1
			and IAIFAC='%s'
			and rownum<1000
			group by IAIFAC,GAENAME,IAIDEPT,GACNAME,IERADMITS,IEUADMITSN""" % (fcode)	
	app.logger.warn("summary() -- start query"+qs)
	curs = c.cursor()
	curs.execute(qs)
	app.logger.warn("summary() -- query returns")
	app.logger.warn("summary() -- iterate on row")
	col_names = [i[0] for i in curs.description]
	rows = []
	for row in curs:
		rows.append(row)

	rsp = {'columns':col_names,'rows':rows}
	return jsonify(rsp)


app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8090)))
