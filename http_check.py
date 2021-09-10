#!/usr/bin/env python3

import time, requests, syslog, subprocess


def Main():
    info=[{'url': 'http://google.com', 'source': '172.17.101.50', 'failscript': 'fail_commands', 'primaryscript': 'primary_commands'}, 
            {'url': 'http://yahoo.com', 'source': '172.17.101.50', 'failscript': 'fail_commands', 'primaryscript': 'primary_commands'}]
    prox=''
    Httptimeout=0.500
    HttpInterval=10
    status=0

    while True:
        for url in info:
            try:
                s = Source(url['source'])
                if prox != '':
                    proxy = {'http': prox}
                    resp = s.get(url['url'], proxies=proxy, timeout=5)
                else:
                    resp = s.get(url['url'], timeout=5)
                if resp.status_code == 200 and resp.elapsed.total_seconds() <= Httptimeout:
                    if status == 0:
                        ()
                    else:
                        status = Failback(url['primaryscript'])
                        syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-8-CHANGE: {0} {1} URL now available'.format(resp.status_code, url['url']))
                else:
                    if status == 1:
                        ()
                    elif status == 0:
                        status = Failure(url['failscript'])
                        syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-9-CHANGE: {0} {1} URL unavailable'.format(resp.status_code, url['url']))
            except:
                if status == 1:
                    ()
                else:
                    status = Failure(url['failscript'])
                    syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                    syslog.syslog('%IP-SLA-9-CHANGE: Error with connection.')
        time.sleep(HttpInterval)    

def Failure(failscript):
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (failscript),shell=True)
    return 1

def Failback(primaryscript):
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (primaryscript),shell=True)
    return 0    

def Source(source) -> requests.Session:
    session = requests.Session()
    for prefix in ('http://', 'https://'):
        session.get_adapter(prefix).init_poolmanager(
            connections=requests.adapters.DEFAULT_POOLSIZE,
            maxsize=requests.adapters.DEFAULT_POOLSIZE,
            source_address=(source, 0),
        )
        return session


if __name__ == '__main__':
   Main()