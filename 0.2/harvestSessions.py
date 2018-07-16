#!/usr/bin/env python

import primeAPI
import time
import json
import csv
import sys

api = primeAPI.ciscoPrime()

#@displayName,@id,anchorIpAddress,apMacAddress,authenticationAlgorithm,
# bytesReceived,bytesSent,clientInterface,connectionType,
# deviceIpAddress,deviceName,eapType,encryptionCypher,
# ipAddress,ipType,location,macAddress,
# packetsReceived,packetsSent,
# policyTypeStatus,portSpeed,postureStatus,profileName,
# protocol,rssi,securityPolicy,sessionEndTime,sessionStartTime,
# snr,ssid,throughput,userName,vlan,webSecurity,wgbMacAddress,wgbStatus

skeys = ['@id','ipAddress','macAddress','userName',\
        'deviceIpAdress','deviceName','apMacAddress','clientInterface',\
        'location','connectionType','ssid','vlan','portSpeed',\
        'eapType','snr','rssi','protocol',\
		'sessionStartTime','sessionEndTime',\
		'packetsReceived','packetsSent','bytesReceived','bytesSent','throughput'\
]

def dumpSessions(start,end):
    slist = api.getSessionListPaged(start,end)
#    skeys = set()
#    for ssn in slist:
#        for k in ssn:
#            skeys.add(k)
    #
    # flatten the ssn items
#    klist = sorted(skeys)
    rows = [skeys]
    for ssn in slist:
        row = []
        for k in skeys:
            if k in ssn:
                row.append(ssn[k])
            else:
                row.append(None)
        rows.append(row)
    return rows

unixts = int(time.time())
print "current TS=",unixts


end = unixts
interval = 300
N = 86400/interval
for n in range(0,N):
    start = (end-interval)
    print "interval",start,end
    try:
        dump = dumpSessions(start*1000,end*1000)
        csvfilename = "output/ssn-%d.csv" % (start,)
        print "writing",len(dump),"rows to",csvfilename
        if len(dump)<2:
            continue
        with open(csvfilename,'w') as f:
            csvout = csv.writer(f)
            csvout.writerows(dump)
    except:
        print "Exception",sys.exc_info()
    end = start
    start = start-interval



