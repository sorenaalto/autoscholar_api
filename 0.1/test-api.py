#!/usr/bin/env python
import os
from flask import Flask,request,render_template
import json

import sys
import cx_Oracle

# don't connect to Oracle until we are read
if True:
	c = cx_Oracle.connect("ilm","identity","PRODI04")
	#c = cx_Oracle.connect("ilm/identity@localhost:1521:prodi04.dut.ac.za")
	print c


#app = Flask(__name__)
app = Flask("assmarks")

@app.route('/')
def info():
	return "Assessment Marks"

@app.route('/main')
def main():
	return render_template('appmain.html')

@app.route('/amarks/summary')
def summary():
	qs = """select JCHSUBJ,IALDESC,count(distinct JCHSTNO) as nstud,max(JCHMARKNUMBER) as nmark,count(JCHMARK) as markscap
          from STUD.JCHSTM,STUD.IALSUB
          where JCHSUBJ=IALSUBJ and JCHCYR=IALCYR
          and JCHCYR=2017
          group by JCHSUBJ,IALDESC
    """
	curs = c.cursor()
	curs.execute(qs)

	rows = []
	for row in curs:
		rows.append(row)

	rsp = json.dumps(rows)
	return rsp

app.run(debug=True,host=os.getenv('IP','0.0.0.0'),port=int(os.getenv('PORT',8090)))
