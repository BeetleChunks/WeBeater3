# WeBeater3

## Overview
There are three main functions of this tool:

* Enumerate pages configured/misconfigured to allow web NTLM authentication
* Perform multi-threaded web NTLM password guessing/brute forcing
* Maintain a database of detailed and timestamped activity

All web requests and authentication attempts are stored in a SQL database. Within the ```docs``` directory are several example SQL queries to get results and useful information, such as, successful NTLM authentication and overviews of the web applications scanned. There is also a ```ui``` directory, which contains REALLY crappy PHP code to display information from the SQL database. I am a terrible UI developer and really just added that to mess around with.

## Docker
```
docker compose --env-file=.env up -d --build
docker exec -it wb3-client-01 /bin/bash
```

## Usage
```
usage: WeBeater3.py [-h] -a {brute,enum} [-t THREADS] [-s TARGET] [-sL TARGETS_FILE] [-P PORT]
                    [-U URI] [-UL ARG_URIS_FILE] [--ssl] [--no-ssl] [-u ARG_USER] [-uL USERS_FILE]
                    [-p PASSWORD] [-pL PASSWDS_FILE] [-d DOMAIN] [-dL DOMAINS_FILE]
                    [-uP USERPASS_FILE]

optional arguments:
  -h, --help            Show this help message and exit
  -a  {brute,enum}      [REQUIRED] Action to carry out
  -t  THREADS           Number of worker threads
  -s  TARGET            Target server
  -sR TARGET_RANGE      Target network CIDR range
  -sL TARGETS_FILE      Line delimited list of target servers.
  -P  PORT              Target port
  -U  URI               Target URI (Default uses internal list for enumeration)
  -UL URIS_FILE         Line delimited list of target URIs.
  -u  USER              Authentication user
  -uL USERS_FILE        Line delimited list of target users.
  -p  PASSWD            Authentication password
  -pL PASSWDS_FILE      Line delimited list of target passwords.
  -d  DOMAIN            Authentication domain
  -dL DOMAINS_FILE      Line delimited list of target domains.
  -uP USERPASS_FILE     Line delimited list of user:password format combinations
  --ssl                 Target host uses SSL. (Overrides port defaults)
  --no-ssl              Target host doesn't use SSL. (Overrides port defaults)
```

## Example Usage:
#### Enumerate 10.5.1.10 for NTLM authentication
```python .\WeBeater3.py -a enum -s 10.5.1.10 -P 80```

#### Check credentials for ```exchadmin``` in the ```ECORP``` domain
```python .\WeBeater3.py -a brute -s 10.5.1.10 -P 80 -U /rpc/ -d ECORP -u exchadmin -p "Welcome1"```

## Python Requirements
During development Python 3.8 was used.

* chilkat2 (https://www.chilkatsoft.com/chilkat2-python.asp)
* pymysql
* netaddr

## SQL Requirements
During development MySQL was used. I have made it very simple to get up and running. All you need to do is install MySQL and start it up. During installation take note of the user and password you create. If you configure it to run on the non-standard port of ```3306``` then also take note of the port. You can install the MySQL database on your localhost or a remote server, either option is supported, just make sure that if you install it on a remote server that the database port is accessible from wherever you plan to run WeBeater3.

## WeBeater3 Configuration
There is a single configuration file for WeBeater3, located at ```configs/settings.py.dist```. After you download or clone this repository, create a copy of this file and remove the ```.dist``` extention, so you are left with ```configs/settings.py```. Open this file and configure it with your Chilkat API key and the MySQL database parameters. If you do not already have a Chilkat API key, there is a 30day trial key you can use (https://www.chilkatsoft.com/TrialInfo.asp).

As this file contains your Chilkat API key and MySQL database credentials, the configuration template is distributed with the ```.dist``` extention to limit the possiblilty of sensitive information being pushed to Github as ```.gitignore``` is configured to exclude ```configs/settings.py```.

## Disclaimer
This code has been created for academic research and is not intended to be used against systems except where explicitly authorized. The code is provided as is with no guarentees or promises on its execution. I am not responsible or liable for misuse of this code.