import os
import chilkat2
import argparse
import threading
import queue

from copy import deepcopy
from netaddr import IPNetwork

# Local project imports
from configs import settings
from modules import wb3

from modules.threadfort import ThreadFort

def get_args_dict():
	args_dict = {
		"arg_action": None,
		"arg_threads": None,
		"arg_target": None,
		"arg_target_range": None,
		"arg_targets_file": None,
		"arg_port": None,
		"arg_uri": None,
		"arg_uris_file": None,
		"ssl": None,
		"arg_user": None,
		"arg_users_file": None,
		"arg_passwd": None,
		"arg_passwds_file": None,
		"arg_domain": None,
		"arg_domains_file": None,
		"arg_userpass_file": None
	}

	# Get command-line arguments
	parser = argparse.ArgumentParser()

	# Action specific parameters
	parser.add_argument('-a', action="store", dest="arg_action", default=None,
		help="[REQUIRED] Action to carry out", choices=["brute", "enum"], required=True)

	parser.add_argument('-t', action="store", dest="arg_threads", type=int, default=1,
		help="Number of worker threads")
	
	# Host specific parameters
	parser.add_argument('-s', action="store", dest="arg_target", default=None,
		help="Target server")

	parser.add_argument('-sR', action="store", dest="arg_target_range", default=None,
		help="Target network CIDR range")
	
	parser.add_argument('-sL', action="store", dest="arg_targets_file", default=None,
		help="Line delimited list of target servers.")
	
	parser.add_argument('-P', action="store", dest="arg_port", type=int, default=443,
		help="Target port")
	
	parser.add_argument('-U', action="store", dest="arg_uri", default=None,
		help="Target URI (Default uses internal list for enumeration)")
	
	parser.add_argument('-UL', action="store", dest="arg_uris_file", default=None,
		help="Line delimited list of target URIs.")
	
	parser.add_argument('--ssl', action='store_true', dest="arg_ssl", default=False,
		help="Target host uses SSL. (Overrides port defaults)")
	
	parser.add_argument('--no-ssl', action='store_true', dest="arg_no_ssl", default=False,
		help="Target host doesn't use SSL. (Overrides port defaults)")
	
	# Credential specific parameters
	parser.add_argument('-u', action="store", dest="arg_user", default=None,
		help="Authentication user")
	
	parser.add_argument('-uL', action="store", dest="arg_users_file", default=None,
		help="Line delimited list of target users.")
	
	parser.add_argument('-p', action="store", dest="arg_passwd", default=None,
		help="Authentication password")
	
	parser.add_argument('-pL', action="store", dest="arg_passwds_file", default=None,
		help="Line delimited list of target passwords.")
	
	parser.add_argument('-d', action="store", dest="arg_domain", default=None,
		help="Authentication domain")
	
	parser.add_argument('-dL', action="store", dest="arg_domains_file", default=None,
		help="Line delimited list of target domains.")

	parser.add_argument('-uP', action="store", dest="arg_userpass_file", default=None,
		help="Line delimited list of user:password format combinations")

	args = parser.parse_args()

	if (args.arg_ssl == False) and (args.arg_no_ssl == False):
		ssl = None # Will use default port SSL settings

	elif (args.arg_ssl == True) and (args.arg_no_ssl == True):
		ssl = None # Will use default port SSL settings

	elif (args.arg_ssl == True):
		ssl = True # Will use SSL, overriding setting defaults

	elif (args.arg_no_ssl == True):
		ssl = False # Will NOT use SSL, overriding setting defaults

	args_dict["arg_action"]        = args.arg_action
	args_dict["arg_threads"]       = args.arg_threads
	args_dict["arg_target"]        = args.arg_target
	args_dict["arg_target_range"]  = args.arg_target_range
	args_dict["arg_targets_file"]  = args.arg_targets_file
	args_dict["arg_port"]          = args.arg_port
	args_dict["arg_uri"]           = args.arg_uri
	args_dict["arg_uris_file"]     = args.arg_uris_file
	args_dict["ssl"]               = ssl
	args_dict["arg_user"]          = args.arg_user
	args_dict["arg_users_file"]    = args.arg_users_file
	args_dict["arg_passwd"]        = args.arg_passwd
	args_dict["arg_passwds_file"]  = args.arg_passwds_file
	args_dict["arg_domain"]        = args.arg_domain
	args_dict["arg_domains_file"]  = args.arg_domains_file
	args_dict["arg_userpass_file"] = args.arg_userpass_file
	
	return args_dict

'''
	Helpers for NTLM Enumeration
'''
def get_target_list(args_dict):
	target_list = []

	if args_dict["arg_target"] != None:
		target_list.append(args_dict["arg_target"].lower())

	if args_dict["arg_target_range"] != None:
		for ip in IPNetwork(args_dict["arg_target_range"]):
			target_list.append(f"{ip}")

	if args_dict["arg_targets_file"] != None:
		with open(args_dict["arg_targets_file"], "r", encoding="utf-8") as hTargets:
			for t in hTargets.read().split('\n'):
				t = t.strip().lower()

				if t != '':
					target_list.append(t)

	target_list = list(set(target_list))

	if len(target_list) > 0:
		return target_list[::]

	else:
		return None

def get_uri_list(args_dict):
	uri_list = []

	if args_dict["arg_uri"] != None:
		uri_list.append(args_dict["arg_uri"])

	if args_dict["arg_uris_file"] != None:
		with open(args_dict["arg_uris_file"], "r", encoding="utf-8") as hUris:
			for u in hUris.read().split('\n'):
				u = u.strip()

				if u != '':
					uri_list.append(u)

	uri_list = list(set(uri_list))

	if len(uri_list) > 0:
		return uri_list[::]

	else:
		return list(set(settings.web["ntlm"]["uris"]))

def generate_hosts(targets, port, ssl):
	template = {
		"host": None,
		"port": port,
		"ssl": None
	}

	if ssl != None:
		template["ssl"] = ssl
	
	else:
		if port in settings.web["ports"]["ssl.true"]:
			template["ssl"] = True

		elif port in settings.web["ports"]["ssl.false"]:
			template["ssl"] = False

		else:
			template["ssl"] = settings.web["ports"]["ssl.default"]

	for target in targets:
		host_dict = deepcopy(template)
		host_dict["host"] = target

		yield host_dict

'''
	Helpers for NTLM Login
'''
def get_user_list(args_dict):
	user_list = []

	if args_dict["arg_user"] != None:
		user_list.append(args_dict["arg_user"].lower())

	if args_dict["arg_users_file"] != None:
		with open(args_dict["arg_users_file"], "r", encoding="utf-8") as hUsers:
			for u in hUsers.read().split('\n'):
				u = u.strip().lower()

				if u != '':
					user_list.append(u)

	user_list = list(set(user_list))

	if len(user_list) > 0:
		return user_list[::]

	else:
		return None

def get_userpass_list(args_dict):
	dup_track = []
	userpass_list = []

	if args_dict["arg_userpass_file"] != None:
		with open(args_dict["arg_userpass_file"], "r", encoding="utf-8") as hUserpass:
			for upass in hUserpass.read().split('\n'):
				u = upass.split(':')[0].lower()
				p = upass.split(':')[1].replace('\n', '').replace('\r', '')

				if (u != '') and (p != ''):
					if f"{u}:{p}" not in dup_track:
						up_set = (u, p)
						userpass_list.append(up_set)
						dup_track.append(f"{u}:{p}")

	if len(userpass_list) > 0:
		return userpass_list[::]

	else:
		return None

def get_auth_host(args_dict):
	auth_host = {
		"host": args_dict["arg_target"],
		"port": args_dict["arg_port"],
		"ssl": None,
		"uri": args_dict["arg_uri"]
	}

	if auth_host["uri"] == None:
		auth_host["uri"] = "/"

	if args_dict["ssl"] != None:
		auth_host["ssl"] = args_dict["ssl"]
	
	else:
		if args_dict["arg_port"] in settings.web["ports"]["ssl.true"]:
			auth_host["ssl"] = True

		elif args_dict["arg_port"] in settings.web["ports"]["ssl.false"]:
			auth_host["ssl"] = False

		else:
			auth_host["ssl"] = settings.web["ports"]["ssl.default"]

	return auth_host

def generate_from_users(users, password, domain):
	template = {
		"user": None,
		"password": password,
		"domain": domain
	}

	for user in users:
		cred_dict = deepcopy(template)
		cred_dict["user"] = user

		yield cred_dict

def generate_from_userpass(user_pass, domain):
	template = {
		"user": None,
		"password": None,
		"domain": domain
	}

	for up_set in user_pass:
		cred_dict = deepcopy(template)
		cred_dict["user"]     = up_set[0]
		cred_dict["password"] = up_set[1]

		yield cred_dict

def main():
	args_dict = get_args_dict()
	tfort     = ThreadFort()

	if args_dict["arg_action"] == "brute":
		cred_q = queue.Queue()

		if args_dict["arg_userpass_file"] == None:
			users     = get_user_list(args_dict)
			password  = args_dict["arg_passwd"]
			domain    = args_dict["arg_domain"]
			auth_host = get_auth_host(args_dict)

			for cred_dict in generate_from_users(users, password, domain):
				cred_q.put(cred_dict)

		else:
			user_pass = get_userpass_list(args_dict)
			domain    = args_dict["arg_domain"]
			auth_host = get_auth_host(args_dict)

			for cred_dict in generate_from_userpass(user_pass, domain):
				cred_q.put(cred_dict)

		for i in range(0, args_dict["arg_threads"]):
			t = threading.Thread(target=wb3.web_ntlm_brute, args=(tfort, auth_host, cred_q))
			t.start()
			tfort.threads.append(t)

	elif args_dict["arg_action"] == "enum":
		host_q  = queue.Queue()
		
		targets = get_target_list(args_dict)
		uris    = get_uri_list(args_dict)
		port    = args_dict["arg_port"]
		ssl     = args_dict["ssl"]

		for host_dict in generate_hosts(targets, port, ssl):
			host_q.put(host_dict)
		
		for i in range(0, args_dict["arg_threads"]):
			t = threading.Thread(target=wb3.web_ntlm_enum, args=(tfort, host_q, uris))
			t.start()
			tfort.threads.append(t)

	else:
		tfort.tprint(f"[!] Invalid action argument recieved.")
		os._exit(1)

	# Wait for action threads to finish
	while len(tfort.threads) > 0:
		for t in tfort.threads:
			if not t.is_alive():
				tfort.threads.remove(t)

if __name__ == '__main__':
	# Unlock chilkat globally
	chilkatGlob = chilkat2.Global()
	success = chilkatGlob.UnlockBundle(settings.chilkat["api.key"])
	if (success != True):
		print(chilkatGlob.LastErrorText)
		os._exit(1)

	main()
