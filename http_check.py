#!/usr/bin/env python3

import time, requests, syslog, subprocess


def Main():
    ###############################
    #   Modify This Section       #
    ###############################
    info=[{'url': 'http://google.com', 'source': '172.16.50.1', 'prox': '', 'failscript': 'fail_commands', 'primaryscript': 'primary_commands'}, 
            {'url': 'http://yahoo.com', 'source': '172.16.51.1', 'prox': '', 'failscript': 'fail_commands2', 'primaryscript': 'primary_commands2'}]
    Httptimeout=0.500
    HttpInterval=5
    ###############################
    #                             #
    ###############################

    failed = []
    while True:
        for url in info:
            try:
                # specify the source ip to use in the request
                s = Source(url['source'])
                # check if a proxy is required and if so make the request using the proper proxy
                if url['prox'] != '':
                    proxy = {'http': url['prox']}
                    resp = s.get(url['url'], proxies=proxy, timeout=5)
                else:
                    # If no proxy is required then make the request without a proxy
                    resp = s.get(url['url'], timeout=5)
                # Check the response code for a 200 ok and make sure it was returned within the desired timeout
                if resp.status_code == 200 and resp.elapsed.total_seconds() <= Httptimeout:
                    # Determine if a failback is required by checking if the current url is in the failed list due to a failure
                    if url['source'] in failed:
                        Failback(url['primaryscript'], url['url'])
                        failed.remove(url['source'])
                    else:
                        ()
                # If the response code is anything other than 200 ok connection has failed and we need to run the failscript
                else:
                    # Keeps the failscript from running if it has already run 
                    if url['source'] in failed:
                        ()
                    else:
                        Failure(url['failscript'], url['url'])
                        failed.append(url['source'])
            # If there is an error trying to connect to url that is unhandled then fail
            except:
                if url['source'] in failed:
                    ()
                else:
                    Failure(url['failscript'], url['url'])
                    failed.append(url['source'])
        time.sleep(HttpInterval)    

# Failscript execution
def Failure(failscript, url):
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (failscript),shell=True)
    syslog.openlog('IP SLA', 0, syslog.LOG_LOCAL4 )
    syslog.syslog('%IP-SLA-3-CHANGE: {0} URL unavailable'.format(url))

# Failback execution
def Failback(primaryscript, url):
    subprocess.check_output('sudo ip netns exec default FastCli /mnt/flash/%s' % (primaryscript),shell=True)
    syslog.openlog( 'IP SLA', 0, syslog.LOG_LOCAL4 )
    syslog.syslog('%IP-SLA-3-CHANGE: {0} URL now available'.format(url))  

# Set source IP binding for requests
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