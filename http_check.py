#!/usr/bin/env python3

import os, re, time, requests, signal, syslog, subprocess, socket


def Main():
    HttpURI=['http://google.com', 'http://yahoo.com']
    prox=''
    Httptimeout=0.500
    HttpInterval=10
    status=0

    while True:
        for url in HttpURI:
            try:
                if prox != '':
                    try:
                        proxy = {'http': prox}
                        resp = requests.get(url, proxies=proxy, timeout=5)
                    except requests.exceptions.RequestException as e:
                        status = Failure()
                        syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-9-CHANGE: Requests error %s.' % (e))
                else:
                    try:
                        resp = requests.get(url, timeout=5)
                    except requests.exceptions.RequestException as e:
                        status = Failure()
                        syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-9-CHANGE: Requests error %s.' % (e))
                if resp.status_code == 200 and resp.elapsed.total_seconds() <= Httptimeout:
                    if status == 0:
                        print(resp.status_code)
                        syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-8-CHANGE: {0} {1} URL available'.format(resp.status_code, url))
                    else:
                        status = Failback()
                else:
                    if status == 1:
                        ()
                        syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-9-CHANGE: {0} {1} URL still unavailable'.format(resp.status_code, url))
                    elif status == 0:
                        status = Failure()
                        syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                        syslog.syslog('%IP-SLA-9-CHANGE: {0} {1} URL unavailable'.format(resp.status_code, url))
            except:
                status = Failure()
                syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
                syslog.syslog('%IP-SLA-9-CHANGE: Error with connection.')
        time.sleep(HttpInterval)    

def Failure():
    print('fail')
    failscript='fail_commands'
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (failscript),shell=True)
    return 1

def Failback():
    print('failback')
    primaryscript='primary_commands'
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (primaryscript),shell=True)
    return 0    

if __name__ == '__main__':
   Main()