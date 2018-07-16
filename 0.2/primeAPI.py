#!/usr/bin/python

import requests
import json
import sys
import csv

class ciscoPrime:
	base_url="https://172.20.0.10/webacs/api/v1/data/"
	session_cookie = None
	auth=("sorena","sorena123")

	def __init__(self):
		print "create API instance"

	def readSessionCookie(self):
		with open("prime.session",'r') as f:
			cookie = f.read()
			cookie = cookie.rstrip()
			self.session_cookie = cookie
			print "read session cookie",cookie
			return cookie

	def persistSessionCookie(self,cset):
		tokens = cset.split(';')
		c = tokens[0]
		self.session_cookie = c
		with open("prime.session",'w') as f:
			print "saving session cookie",c
			f.write(c)
			
	def makeRequest(self,url,start=0,numresult=500):	
		url = url+"&.firstResult=%d&.maxResults=%d" % (start,numresult)
		print "request URL",url
		if self.session_cookie == None:
			self.readSessionCookie()
		headers = {"Cookie":self.session_cookie}
		r = requests.get(url,verify=False,auth=self.auth,headers=headers)
		if "Set-Cookie" in r.headers:
			self.persistSessionCookie(r.headers["Set-Cookie"])
		return r

	def getSessionList(self,starttime,endtime):
		url = self.base_url+"ClientSessions.json?sessionStartTime=between(%s,%s)&.full=true" % (starttime,endtime)
		rsp = self.makeRequest(url,start=0,numresult=1000)
		try:
			rr = json.loads(rsp.text)
			return rr
		except:
			return rsp

	def getSessionListPaged(self,starttime,endtime):
		ssnlist = []
		url = self.base_url+"ClientSessions.json?sessionStartTime=between(%s,%s)&.full=true" % (starttime,endtime)
		enough_results = False
		start = 0
		chunk = 500
		all_responses = []
		while not enough_results:
			rsp = self.makeRequest(url,start,chunk)
			try:
				rr = json.loads(rsp.text)
				rs_size = int(rr['queryResponse']['@count'])
				last_result = int(rr['queryResponse']['@last'])
				print "last_result/rs_size=",last_result,rs_size
				chunk_list = self.rspAsSessionList(rr)
				ssnlist.extend(chunk_list)
				if last_result+1 < rs_size:
					start = last_result+1
				else:
					enough_results = True
			except:
				print "error...",sys.exc_info()
				print rsp.text
				return rsp
		return ssnlist

	def getCurrentSessions(self):
		url = self.base_url+"ClientSessions.json?sessionEndTime=gt(4000000000000)&.full=true"
		rsp = self.makeRequest(url)
		try:
			rr = json.loads(rsp.text)
			return rr
		except:
			return rsp

	def getCurrentSessionsWithPaging(self):
		url = self.base_url+"ClientSessions.json?sessionEndTime=gt(4000000000000)&.full=true"
		enough_results = False
		start = 0
		chunk = 500
		all_responses = []
		while not enough_results:
			rsp = self.makeRequest(url,start,chunk)
			try:
				rr = json.loads(rsp.text)
				rs_size = int(rr['queryResponse']['@count'])
				last_result = int(rr['queryResponse']['@last'])
				print "last_result/rs_size=",last_result,rs_size
				if last_result+1 < rs_size:
					start = last_result+1
				else:
					enough_results = True
				all_responses.append(rr)
			except:
				print "error...",sys.exc_info()
				print rsp.text
				return rsp
		return all_responses

	def getSessionsForIP(self,ip):
		pass

	def rspAsSessionList(self,rsp):
		slist = []
		try:
			elist = rsp['queryResponse']['entity']
			for e in elist:
				vmap = e['clientSessionsDTO']
				slist.append(vmap)
		except:
			print "No sessions in this interval?"
		return slist


if __name__ == "__main__":

	def mapKeys(m,klist):
		row = []
		for k in klist:
			if k in m:
				row.append(m[k])
			else:
				row.append(None)
		return row

	print "Starting..."
	api = ciscoPrime()
	rsp = api.getCurrentSessionsWithPaging()
# testing with only 100
#	r = api.getCurrentSessions()
#	rsp = [r]
	keys = ['macAddress','ipAddress','userName',\
			'location','connectionType','ssid','vlan','apMacAddress','deviceName',\
			'snr','rssi',\
			'sessionStartTime','sessionEndTime',\
			'packetsReceived','packetsSent','bytesReceived','bytesSent','throughput'\
			]			

	rows_out = [keys]

	for rr in rsp:
    	#print json.dumps(rr,indent=4)
		elist = rr['queryResponse']['entity']
		for e in elist:
			vmap = e['clientSessionsDTO']
			r = mapKeys(vmap,keys)
			print r
			rows_out.append(r)

	with open('sessions.csv','w') as f:
		csvout = csv.writer(f)
		csvout.writerows(rows_out)






