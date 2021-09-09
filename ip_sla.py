import os, re, syslog, time, requests, signal
########## CONFIGURATION ##########
icmp_sla=False
IP_TO_TRACK=['172.23.1.1']
PingInterval=2
FailureCount=3
MaxLatency=300
Http_SLA=True
HttpURI=['https://google.com', 'https://yahoo.com']
prox='http://192.168.101.2:8888'
Httptimeout=0.500
HttpInterval=10
# DO NOT EDIT ANYTHING BELOW THIS LINE ##########

# Handle CTRL+C Interrupt
def keyboardInterruptHandler(signal, frame):
    print("\nAbort Sequence Initiated, Goodbye!")
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

targets = {}
for target in IP_TO_TRACK:
    targets[target] = {'count':0, 'status' : True}
while True:
    if icmp_sla == True:
        for target in targets:
            res = os.popen('ping -c 1 -W 1 %s ' % (target))
            ping_result = res.readlines()
            try:
                rtt = re.findall(r'time=(.*?) ms\\n',str(ping_result))[0]
            except:
                rtt = 9999
            if float(rtt) >= MaxLatency and targets[target]['status']:
                targets[target]['count'] += 1
                if targets[target]['count'] == FailureCount:
                    if all(value['status'] == True for value in targets.values()):
                        syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog( '%IP-SLA-6-CHANGE: Destination host {0} is unreachable via interafce ethernet1/0'.format(target))
                        #syslog.syslog( '%IP-SLA-6-CHANGE: Destination host is unreachable' )
                        targets[target]['status'] = False
                    elif float(rtt) <= MaxLatency and not targets[target]['status']:
                        targets[target]['count'] = 0
                        if not targets[target]['status']:
                            targets[target]['status'] = True
                            if all(value['status'] == True for value in targets.values()):
                                syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                                syslog.syslog( '%IP-SLA-7-CHANGE: Destination host {0} is reachable via interafce ethernet1/0'.format(target) )
                                #syslog.syslog( '%IP-SLA-6-CHANGE: Destination host is reachable' )
        time.sleep(PingInterval)
    if Http_SLA == True:
        for url in HttpURI:
            try:
                proxy = {'http': prox}
                resp = requests.get(url, proxies=proxy)
                if resp.status_code == 200 and resp.elapsed.total_seconds() <= Httptimeout:
                    syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                    syslog.syslog('%IP-SLA-8-CHANGE: {0} {1} URL available'.format(resp.status_code, url))
            except:
                syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                syslog.syslog('%IP-SLA-9-CHANGE: {0} {1} URL unavailable'.format(resp.status_code, url))
        time.sleep(HttpInterval)    
    else:
        ()

