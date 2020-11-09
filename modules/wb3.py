import json

from copy import deepcopy

# Local project imports
from configs import settings

from modules.authentication import WebNTLM
from modules.authentication import NtlmInfoResponseFailure
from modules.authentication import NtlmInfoHttpRequestFailed
from modules.authentication import PreAuthResponseFailure
from modules.authentication import PreAuthHttpRequestFailed

from modules.database import WeB3Db
from modules.database import DuplicateHost
from modules.database import DuplicateService
from modules.database import DuplicateWebPage

def web_ntlm_enum(host_dict, uris=None):
	assert (isinstance(uris, list)) or (uris == None)

	# Create list of URIs for enumeration
	if uris == None:
		uri_list = settings.web["ntlm"]["uris"]
	else:
		uri_list = uris

	w3db    = WeB3Db()
	webNtlm = WebNTLM()

	# Init and verify target host information
	host = host_dict["host"]
	port = host_dict["port"]
	ssl  = host_dict["ssl"]

	# Configure database connection settings
	w3db.host = settings.wb3["db"]["host"]
	w3db.port = settings.wb3["db"]["port"]
	w3db.user = settings.wb3["db"]["user"]
	w3db.passwd = settings.wb3["db"]["password"]

	# Connect to database
	if(w3db.connect() != True):
		print("[ERROR] Database connection failed")
		os._exit(1)

	# Configure target connection settings
	webNtlm.host = host
	webNtlm.port = port
	webNtlm.ssl  = ssl

	# Insert host into database
	try:
		w3db.insert_host({"host": host})
	
	except DuplicateHost:
		pass

	# Get host id from database
	hid = w3db.get_host_id(host)
	if hid == None:
		print("[!] Failed to get host id from database")
		return

	# Insert service into database
	try:
		w3db.insert_service({
				"hid": hid,
				"port": port,
				"ssl": ssl,
				"web": True
			})
	
	except DuplicateService:
		pass

	# Get service id from database
	sid = w3db.get_service_id(hid, port)
	if sid == None:
		print("[!] Failed to get service id from database")
		return

	for uri in uri_list:
		# Set current URI
		webNtlm.uri = uri
		
		# Extract NTLM Info Json
		try:
			ntlm_info = webNtlm.ntlm_info()

		except NtlmInfoResponseFailure:
			print(f"[!] Host {host}:{port} seems to be down")
			break

		except NtlmInfoHttpRequestFailed:
			print(f"[!] Host {host}:{port} seems to be down")
			break

		# Index web page URI
		try:
			w3db.insert_web_page({
					"sid": sid,
					"uri": uri
				})

		except DuplicateWebPage:
			pass

		# Get web page id
		wpid = w3db.get_web_page_id(sid, uri)
		if wpid == None:
			print(f"[!] Failed to get web page id for sid {sid} and uri {uri}")
			continue

		# Index web request
		ntlm_info_dict = json.loads(ntlm_info)

		if ntlm_info_dict["result"]["ntlm.info"] == None:
			auth_ntlm_info = False
		else:
			auth_ntlm_info = True

		resp_headers = json.dumps(ntlm_info_dict["result"]["headers"])

		ruid = w3db.insert_web_request({
				"wpid": wpid,
				"status_code": ntlm_info_dict["result"]["status.code"],
				"status_text": ntlm_info_dict["result"]["status.text"],
				"req_method": "GET",
				"req_datetime": ntlm_info_dict["result"]["req_datetime"],
				"req_headers": None,
				"req_data": None,
				"resp_datetime": ntlm_info_dict["result"]["resp_datetime"],
				"resp_headers": resp_headers,
				"resp_data": None,
				"ntlm_info": auth_ntlm_info,
				"basic_info": False,
				"digest_info": False,
				"krb_info": False,
				"negotiate_info": False,
				"ntlm_login": False,
				"basic_login": False,
				"digest_login": False,
				"krb_login": False,
				"negotiate_login": False
			})

		if (auth_ntlm_info == True) and (ntlm_info_dict["result"]["ntlm.info"] != None):
			# Get web request id
			wrid = w3db.get_web_request_id(wpid, ruid)
			if wrid == None:
				print(f"[!] Failed to get web request id for wpid {wpid} and ruid {ruid}")
				continue
			
			# Index NTLM info
			w3db.insert_web_ntlm_info({
					"wrid": wrid,
					"flags": ntlm_info_dict["result"]["ntlm.info"]["flags"],
					"flag_chars": ntlm_info_dict["result"]["ntlm.info"]["flagChars"],
					"target_name": ntlm_info_dict["result"]["ntlm.info"]["targetName"],
					"nb_computer_name": ntlm_info_dict["result"]["ntlm.info"]["netBiosComputerName"],
					"nb_domain_name": ntlm_info_dict["result"]["ntlm.info"]["netBiosDomainName"],
					"dns_computer_name": ntlm_info_dict["result"]["ntlm.info"]["dnsComputerName"],
					"dns_domain_name": ntlm_info_dict["result"]["ntlm.info"]["dnsDomainName"]
				})

	# Disconnect from database
	w3db.disconnect()

def web_ntlm_brute(host_dict, cred_list):
	w3db    = WeB3Db()
	webNtlm = WebNTLM()

	'''
		Error handling - how many errors before quiting
	'''
	# This counter occurs BEFORE authentication is performed
	# so lockout is not a concern
	pre_auth_error_exit_threshold = 5
	pre_auth_error_exit_count     = 0

	# Should function debug messages be displayed
	debug = settings.general["debug"]["wb3"]

	# Init and verify target host information
	host = host_dict["host"]
	port = host_dict["port"]
	ssl  = host_dict["ssl"]
	uri  = host_dict["uri"]

	# Configure database connection settings
	w3db.host = settings.wb3["db"]["host"]
	w3db.port = settings.wb3["db"]["port"]
	w3db.user = settings.wb3["db"]["user"]
	w3db.passwd = settings.wb3["db"]["password"]

	# Connect to database
	if(w3db.connect() != True):
		print("[ERROR] Database connection failed")
		os._exit(1)

	# Configure target connection settings
	webNtlm.host = host
	webNtlm.port = port
	webNtlm.ssl  = ssl
	webNtlm.uri  = uri

	# Insert host into database
	try:
		w3db.insert_host({"host": host})
	
	except DuplicateHost:
		pass

	# Get host id from database
	hid = w3db.get_host_id(host)
	if hid == None:
		print("[!] Failed to get host id from database")
		return

	# Insert service into database
	try:
		w3db.insert_service({
				"hid": hid,
				"port": port,
				"ssl": ssl,
				"web": True
			})
	
	except DuplicateService:
		pass

	# Get service id from database
	sid = w3db.get_service_id(hid, port)
	if sid == None:
		print("[!] Failed to get service id from database")
		return

	# Index web page URI
	try:
		w3db.insert_web_page({
				"sid": sid,
				"uri": uri
			})

	except DuplicateWebPage:
		pass

	# Get web page id
	wpid = w3db.get_web_page_id(sid, uri)
	if wpid == None:
		print(f"[!] Failed to get web page id for sid {sid} and uri {uri}")
		return

	# Perform authentication for each credential
	for cred in cred_list:
		cred_user   = cred["user"]
		cred_pass   = cred["password"]
		cred_domain = cred["domain"]

		try:
			ntlm_login = webNtlm.ntlm_login(cred_user, cred_pass, domain=cred_domain)
		
		except PreAuthResponseFailure:
			pre_auth_error_exit_count += 1
			
			if pre_auth_error_exit_count < pre_auth_error_exit_threshold:
				if debug == True:
					print(f"[DEBUG] Pre-authentication response failure, count is {pre_auth_error_exit_count}")
					print(f"\tCurrent Cred: {cred}")
				
				cred_list.append(deepcopy(cred))
				continue

			else:
				print(f"[!] Host {host}:{port} seems to be down")
				break

		except PreAuthHttpRequestFailed:
			pre_auth_error_exit_count += 1
			
			if pre_auth_error_exit_count < pre_auth_error_exit_threshold:
				if debug == True:
					print(f"[DEBUG] Pre-authentication response failure, count is {pre_auth_error_exit_count}")
					print(f"\tCurrent Cred: {cred}")

				cred_list.append(deepcopy(cred))
				continue

			else:
				print(f"[!] Host {host}:{port} seems to be down")
				break

		ntlm_login_dict = json.loads(ntlm_login)

		resp_headers = json.dumps(ntlm_login_dict["result"]["headers"])

		if (ntlm_login_dict["result"]["post.auth"] != None):
			auth_ntlm_login = True

		else:
			auth_ntlm_login = False

		# Insert web request
		ruid = w3db.insert_web_request({
				"wpid": wpid,
				"status_code": ntlm_login_dict["result"]["status.code"],
				"status_text": ntlm_login_dict["result"]["status.text"],
				"req_method": "GET",
				"req_datetime": ntlm_login_dict["result"]["req_datetime"],
				"req_headers": None,
				"req_data": None,
				"resp_datetime": ntlm_login_dict["result"]["resp_datetime"],
				"resp_headers": resp_headers,
				"resp_data": None,
				"ntlm_info": False,
				"basic_info": False,
				"digest_info": False,
				"krb_info": False,
				"negotiate_info": False,
				"ntlm_login": auth_ntlm_login,
				"basic_login": False,
				"digest_login": False,
				"krb_login": False,
				"negotiate_login": False
			})

		if (auth_ntlm_login == True):
			# Get web request id
			wrid = w3db.get_web_request_id(wpid, ruid)
			if wrid == None:
				print(f"[!] Failed to get web request id for wpid {wpid} and ruid {ruid}")
				break

			pre_headers = json.dumps(ntlm_login_dict["result"]["pre.auth"]["headers"])
			post_headers = json.dumps(ntlm_login_dict["result"]["post.auth"]["headers"])
			
			# Index NTLM info
			w3db.insert_web_ntlm_login({
					"wrid": wrid,
					"domain": ntlm_login_dict["domain"],
					"username": ntlm_login_dict["user"],
					"password": ntlm_login_dict["password"],
					"seconds": ntlm_login_dict["result"]["seconds"],
					"pre_status_code": ntlm_login_dict["result"]["pre.auth"]["status.code"],
					"pre_status_text": ntlm_login_dict["result"]["pre.auth"]["status.text"],
					"pre_resp_headers": pre_headers,
					"post_status_code": ntlm_login_dict["result"]["post.auth"]["status.code"],
					"post_status_text": ntlm_login_dict["result"]["post.auth"]["status.text"],
					"post_resp_headers": post_headers
				})

	# Disconnect from database
	w3db.disconnect()

