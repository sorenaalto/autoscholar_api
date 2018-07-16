#!/usr/bin/env python

import uuid
import time

class aSession:
    def __init__(self,user):
        self.token = str(uuid.uuid4())
        self.username = user
        self.created_at = time.time()
        self.last_check = self.created_at
        self.access_count = 1
        self.membertype = 0
        self.ldapres = None
        
    def asString(self):
        return ",".join([self.token,self.username,str(self.created_at),\
                str(self.last_check),str(self.access_count),str(self.ldapres)])
    

class asSessions:
    def __init__(self):
        self.session_map = {}
        
    def newSession(self,username):
        ssn = aSession(username)
        self.session_map[ssn.token] = ssn
        #
        # hack...record last session under known token
        self.session_map["1234567890"] = ssn
        print ssn
        return ssn
    
    def findSession(self,token):
        if token in self.session_map:
            ssn = self.session_map[token]
            ssn.access_count = ssn.access_count+1
            return ssn
        else:
            return None
        
    def deleteSession(self,token):
        if token in self.session_map:
            del self.session_map[token]
            
    def getSessions(self):
        return self.session_map

import ldap
import sys
import traceback

class authSessions(asSessions):
    def setLogger(self,logger):
        self.logger = logger
        
    def loginSession(self,username,passwd):
        self.logger.info("loginSession(%s,%s)" % (username,passwd))
        ldap_server="ldap://127.0.0.1:3389"
        username = username.lower()
        if "dut.ac.za" in username:
            base_dn="OU=Users,OU=DUT Resources,DC=dut,DC=ac,DC=za"
            mtype = 4
        elif "dut4life.ac.za" in username:
            base_dn="OU=DUT External Resources,DC=dut,DC=ac,DC=za"
            mtype = 0
        try:
            ldap_client=ldap.initialize(ldap_server)
            rc = ldap_client.simple_bind_s(username,passwd)
            self.logger.info("simple_bind_s, rc="+str(rc))
            filter = "mail=%s" % (username)
            rs = ldap_client.search_s(base_dn,ldap.SCOPE_SUBTREE,filter,None)
            self.logger.info("rs="+str(rs))
            newssn =  self.newSession(username)            
            newssn.ldapres = rs[0]
            newssn.membertype = mtype
            return newssn
        except:
            (xtype,xvalue,xtback) = sys.exc_info()
            tbfmt = traceback.format_exception(xtype,xvalue,xtback)
            self.logger.info("exception"+"\n...".join(tbfmt))
            return None
