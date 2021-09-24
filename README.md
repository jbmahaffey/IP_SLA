# IP_SLA

The setup.sh script will install the required python3 modules to the /mnt/flash directory to ensure persistance.  Please run this script first to ensure that all required modules are installed.

The info list described below contains a majority of the information required for the check and should be modified to meet your requirements.  You can check multiple URLs from different source IP's by adding more dictionaries to the info list, just make sure you include all required information for each dictionary.  The configuration files define what commands to run when the check fails and then what commands to run when the check recovers.  There is a sample provided for both failed_commands and the primary_commands(recovery commands).  Different commands can be specified per URL check by having different names per check.  

Syslog messages will be generated for a failure event specifying the URL that failed and another message will be generated when the check recovers, again specifying the URL that recovered.


Variables explained below:

            ###############################
            #   Modify This Section       #
            ###############################
            info=[{'url': '***URL***', 'source': '***Source IP***', 'prox': '***Proxy If Required***', 'failscript': '***Commands File if Failed***', 'primaryscript': '***Commands File if Recovered***'}, 
                 {'url': '***URL***', 'source': '***Source IP***', 'prox': '***Proxy If Required***', 'failscript': '***Commands File if Failed***', 'primaryscript': '***Proxy If Required***'}]
            Httptimeout=***Time Out***
            HttpInterval=***Interval Between Check***
            failed = []
            ###############################
            #                             #
            ###############################