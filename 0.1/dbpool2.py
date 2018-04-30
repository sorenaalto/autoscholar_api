#
# DB pool with idle connection timeout and closure...
#

import Queue
#import cx_Oracle

class dbPool:
	def __init__(self,maxconn):
		self.dbqueue = Queue.LifoQueue(maxconn)
		self.maxconn = maxconn
		self.numconn = 0
	
	def makeNewConn(self):
		print "Pleeeeze override..."
		return None

	def createNewConn(self):
		if self.numconn >= self.maxconn:
			print "have reached maxconns"
			return None
		c = self.makeNewConn()
		self.numconn = self.numconn+1
		print "allocated new conn",self.numconn
		return c
	
	def getConn(self):
		print "getConn..."
		if self.dbqueue.empty():
			return self.createNewConn()
		else:
			return self.dbqueue.get()
	
	def freeConn(self,c):
		print "freeConn..."
		if c != None:
			self.dbqueue.put(c)
		else:
			print "can't free None!"
		
	def closeAllConns(self):
		print "closeAllConns"
		while not self.dbqueue.empty():
			c = self.dbqueue.get()
			print "...close"
			c.close()

