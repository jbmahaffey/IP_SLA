import pprint
import requests
import re
import sys
import ssl
from jsonrpclib import Server
from xml.etree import ElementTree

# Pull Data from Firewall
data = {
  'type': 'op',
  'key': 'LUFRPT0wbFZwNnVMLzhhb3J3ZDlVRmFtMVBRaGRLWnM9VTJUckZ4NWZBYWlDRmlUNXQ4M3FSNFlTK3pZWmJyOFdOUlNxUWE1aEwrRURqUFBhbi9xYVlCTjhycnN2NzNoSA==',
  'cmd': '<show><arp><entry name=\'all\'/></arp></show>'
}

response = requests.post('https://192.168.0.34/api/', data=data, verify=False)
table = response.content

# Unordered dictionaries
panArpDict = {}
localArpDict = {}
testDict = {}
srsaDict = {}

tree = ElementTree.XML(table)
for child in tree:
    for entry in child.iter('entry') :
        for ip in entry.iter('ip'):
            ip = (ip.text)
        for mac in entry.iter('mac'):
            mac = (mac.text)
        panArpDict[ip] = mac

# EOS connection
ssl._create_default_https_context = ssl._create_unverified_context
username = "arista"
password = "arista"
hostname = "127.0.0.1"

switch = Server('https://{}:{}@{}/command-api'.format(username, password, hostname))

# Show running-config section arp on swithc
srsa = switch.runCmds(1 , [ "show running-config section arp" ], "text" )

## show run sec arp Dict

for x in srsa[0]['output'].split("\\n"):
  srsaDict = x

# Split method
srsaDict.split()

try:
  localArpDict[srsaDict.split()[1]] = srsaDict.split()[2]
  localArpDict[srsaDict.split()[5]] = srsaDict.split()[6]
  localArpDict[srsaDict.split()[9]] = srsaDict.split()[10]
except:
  print "Nothing to split"

addcmd = []
rmvcmd = []

#conf_mode = ("enable", "configure")

## Execute arp additions to switch
for arpIP in panArpDict:
  if arpIP in localArpDict:
    localArpDict.pop(arpIP)
  else:
    addcmd = [ "enable", "configure", "arp %s %s arpa" %(arpIP,panArpDict[arpIP]) ]
    response = switch.runCmds ( 1, addcmd )

## Remove non-matching arp entries
for arpIP in localArpDict:
  if arpIP not in panArpDict:
    rmvcmd = [ "enable", "configure", "no arp %s %s arpa" %(arpIP,localArpDict[arpIP]) ]
    response = switch.runCmds ( 1, rmvcmd )

exit()

