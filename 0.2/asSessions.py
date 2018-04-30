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
        
    def asString(self):
        return ",".join([self.token,self.username,str(self.created_at),\
                str(self.last_check),str(self.access_count)])
    

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
        return ssn.token
    
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

            