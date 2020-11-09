import json
import time
import chilkat2

from datetime import datetime
from copy import deepcopy

from configs import settings

class PreAuthResponseFailure(Exception):
	pass

class PreAuthHttpRequestFailed(Exception):
	pass

class NtlmInfoResponseFailure(Exception):
	pass

class NtlmInfoHttpRequestFailed(Exception):
	pass

class _NtlmClient:
	def __init__(self):
		self.debug  = settings.general["debug"]["auth"]
		self.client = chilkat2.Ntlm()
		self.workstation  = "BROWSER"
		self.conn_timeout = 5
		self.read_timeout = 10

	def _build_type1(self, domain=None):
		try:
			# The NTLM protocol begins by the client sending the server
			# a Type1 message.
			if domain != None:
				self.client.Domain = domain

			self.client.Workstation = self.workstation
			type1Msg = self.client.GenType1()

			return type1Msg

		except Exception as e:
			print(f"[EXCEPTION] {__name__}._build_type1(): {e}")
			return None

	def _build_type3(self, user, password, type2Msg):
		try:
			# The client will now generate the final Type3
			# message to be sent to the server.
			self.client.UserName = user
			self.client.Password = password

			type3Msg = self.client.GenType3(type2Msg)
			
			if (self.client.LastMethodSuccess != True):
				if self.debug == True:
					print(f"[DEBUG] {self.client.LastErrorText}")
				
				return None

			return type3Msg

		except Exception as e:
			print(f"[EXCEPTION] {__name__}._build_type3(): {e}")
			return None

	def _get_type2_json(self, type2Msg):
		xml   = chilkat2.Xml()
		sbXml = chilkat2.StringBuilder()

		try:
			# The client may examine the information embedded in the Type2 message
			# by calling ParseType2, which returns XML.  This is only for informational purposes
			# and is not required.
			type2Info = self.client.ParseType2(type2Msg)

			sbXml.Append(type2Info)

			# Load the XML contained in sbXml
			success = xml.LoadSb(sbXml, True)

			if (success == False):
				print(f"[EXCEPTION] parsing type2 message to json {type2Msg}: {repr(xml.LastErrorText)}")
				return None

			flags = xml.GetChildContent("flags")
			flagChars = xml.GetChildContent("flagChars")
			targetName = xml.GetChildContent("targetName")
			netBiosComputerName = xml.GetChildContent("netBiosComputerName")
			netBiosDomainName = xml.GetChildContent("netBiosDomainName")
			dnsComputerName = xml.GetChildContent("dnsComputerName")
			dnsDomainName = xml.GetChildContent("dnsDomainName")
			# serverChallenge = xml.GetChildContent("serverChallenge")
			# targetInfo = xml.GetChildContent("targetInfo")

			type2_json = {
				"flags": flags,
				"flagChars": flagChars,
				"targetName": targetName,
				"netBiosComputerName": netBiosComputerName,
				"netBiosDomainName": netBiosDomainName,
				"dnsComputerName": dnsComputerName,
				"dnsDomainName": dnsDomainName,
				# "serverChallenge": serverChallenge,
				# "targetInfo": targetInfo,
				# "msgType2": type2Msg
			}

			if self.debug == True:
				print(f"[DEBUG] {json.dumps(type2_json)}")

			return type2_json

		except Exception as e:
			print(f"[EXCEPTION] {__name__}._get_type2_json(): {e}")
			return None

	def http_ntlm_info(self, url):
		# Make the HTTP(S) Request
		result = {
			"status.code": None,
			"status.text": None,
			"headers": {},
			"ntlm.info": None,
		}

		chl_http = chilkat2.Http()

		chl_http.ConnectTimeout       = self.conn_timeout
		chl_http.ReadTimeout          = self.read_timeout
		chl_http.RequireSslCertVerify = False
		chl_http.FetchFromCache       = False
		chl_http.FollowRedirects      = False
		chl_http.MimicFireFox         = True
		chl_http.NtlmAuth             = False

		# Request page to get default response status and headers
		result["req_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		resp_obj = chl_http.QuickGetObj(url)
		result["resp_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		# Check if the last get request succeeded
		if chl_http.LastMethodSuccess == False:
			if self.debug == True:
				print(f"[DEBUG] Last method success was False 'resp_obj': {chl_http.LastErrorText}")
	
			raise NtlmInfoHttpRequestFailed

		# Verify the response object is not None
		if resp_obj == None:
			if self.debug == True:
				print(f"[DEBUG] HTTP response object 'resp_obj' was 'None'")
			
			raise NtlmInfoResponseFailure

		# Save status code and header information
		result["status.code"] = resp_obj.StatusCode
		result["status.text"] = f"{resp_obj.StatusText}"
		
		num_headers = resp_obj.NumHeaderFields
		for i in range(0, num_headers):
			k = resp_obj.GetHeaderName(i)
			result["headers"][k] = resp_obj.GetHeaderField(k)
		
		# Send type1 message
		chl_http.SetRequestHeader("Authorization", f"NTLM {self._build_type1()}")
		resp_obj = chl_http.QuickGetObj(url)

		# Check if the last get request succeeded
		if chl_http.LastMethodSuccess == False:
			if self.debug == True:
				print(f"[DEBUG] HTTP NTLM type1 request failed: {chl_http.LastErrorText}")
			
			result["ntlm.info"] = None
			return result

		# Verify the response object is not None
		if resp_obj == None:
			if self.debug == True:
				print(f"[DEBUG] HTTP NTLM type1 response object was 'None'")
			
			result["ntlm.info"] = None
			return result

		try:
			type2_msg = resp_obj.GetHeaderField("WWW-Authenticate").split('NTLM ')[1].split(',')[0]
		
		except:
			if self.debug == True:
				print(f"[DEBUG] Failed to extract NTLM type2 message from HTTP response.")
			
			result["ntlm.info"] = None
			return result

		try:
			type2_json = self._get_type2_json(type2_msg)
			result["ntlm.info"] = type2_json
		
		except:
			if self.debug == True:
				print(f"[DEBUG] Failed to parse NTLM type2 message from HTTP response.")
			
			result["ntlm.info"] = None
			return result
		
		return result

	def http_ntlm_login(self, url, user, password, domain=None):
		# Make the HTTP(S) Request
		result = {
			"pre.auth": {
				"status.code": None,
				"status.text": None,
				"headers": {}
			},
			"post.auth": {
				"status.code": None,
				"status.text": None,
				"headers": {}
			}
		}

		chl_http = chilkat2.Http()

		chl_http.ConnectTimeout       = self.conn_timeout
		chl_http.ReadTimeout          = self.read_timeout
		chl_http.RequireSslCertVerify = False
		chl_http.FetchFromCache       = False
		chl_http.FollowRedirects      = False
		chl_http.MimicFireFox         = True
		chl_http.NtlmAuth             = False

		# Send type1 message
		chl_http.SetRequestHeader("Authorization", f"NTLM {self._build_type1(domain=domain)}")
		result["req_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		preAuthRespObj = chl_http.QuickGetObj(url)

		# Check if the last get request succeeded
		if chl_http.LastMethodSuccess == False:
			if self.debug == True:
				print(f"[DEBUG] Last method success was False 'preAuthRespObj': {chl_http.LastErrorText}")
			
			raise PreAuthHttpRequestFailed

		# Verify the response object is not None
		if preAuthRespObj == None:
			if self.debug == True:
				print(f"[DEBUG] HTTP response object 'preAuthRespObj' was 'None'")
			
			raise PreAuthResponseFailure

		# Save pre-authentication information
		result["pre.auth"]["status.code"] = preAuthRespObj.StatusCode
		result["pre.auth"]["status.text"] = f"{preAuthRespObj.StatusText}"
		result["status.code"] = preAuthRespObj.StatusCode
		result["status.text"] = f"{preAuthRespObj.StatusText}"

		num_headers = preAuthRespObj.NumHeaderFields
		for i in range(0, num_headers):
			k = preAuthRespObj.GetHeaderName(i)
			result["pre.auth"]["headers"][k] = preAuthRespObj.GetHeaderField(k)

		result["headers"] = deepcopy(result["pre.auth"]["headers"])

		try:
			type2_msg = preAuthRespObj.GetHeaderField("WWW-Authenticate").split('NTLM ')[1].split(',')[0]
		
		except:
			if self.debug == True:
				print(f"[DEBUG] Failed to extract NTLM type2 message from HTTP response.")
			
			result["resp_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			result["post.auth"] = None
			return result

		try:
			type3_msg = self._build_type3(user, password, type2_msg)

		except:
			if self.debug == True:
				print(f"[DEBUG] Failed to build NTLM type3 message from type2 message.")
			
			result["resp_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			result["post.auth"] = None
			return result

		# Send type3 message
		start_time = time.time()
		chl_http.SetRequestHeader("Authorization", f"NTLM {type3_msg}")
		postAuthRespObj = chl_http.QuickGetObj(url)
		result["seconds"] = round(time.time() - start_time, 3)
		result["resp_datetime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		# Check if the last get request succeeded
		if chl_http.LastMethodSuccess == False:
			if self.debug == True:
				print(f"[DEBUG] Last method success was False 'postAuthRespObj': {chl_http.LastErrorText}")
			
			result["post.auth"] = None
			return result

		# Verify the response object is not None
		if preAuthRespObj == None:
			if self.debug == True:
				print(f"[DEBUG] HTTP response object 'postAuthRespObj' was 'None'")
			
			result["post.auth"] = None
			return result

		# Save post-authentication information
		result["post.auth"]["status.code"] = postAuthRespObj.StatusCode
		result["post.auth"]["status.text"] = f"{postAuthRespObj.StatusText}"
		result["status.code"] = postAuthRespObj.StatusCode
		result["status.text"] = f"{postAuthRespObj.StatusText}"
		
		num_headers = postAuthRespObj.NumHeaderFields
		for i in range(0, num_headers):
			k = postAuthRespObj.GetHeaderName(i)
			result["post.auth"]["headers"][k] = postAuthRespObj.GetHeaderField(k)

		result["headers"] = deepcopy(result["post.auth"]["headers"])

		return result

class WebNTLM:
	def __init__(self):
		self.debug = settings.general["debug"]["auth"]
		self.host  = None
		self.port  = None
		self.uri   = None
		self.ssl   = False

	# Return format: http(s)://{host}(:{port})(/<uri>)
	def _format_url(self, uri=None):
		# Validate SSL settings
		assert isinstance(self.ssl, bool)
		
		# Validate host settings
		assert isinstance(self.host, str)
		assert self.host != ""

		# Validate port settings
		assert isinstance(self.port, int)
		assert self.port <= 65535
		assert self.port >= 0

		# Validate URI settings
		assert (isinstance(uri, str)) or (uri == None)

		if self.ssl == True:
			if self.port == 443:
				url = f"https://{self.host}"

			else:
				url = f"https://{self.host}:{self.port}"

		else:
			if self.port == 80:
				url = f"http://{self.host}"

			else:
				url = f"http://{self.host}:{self.port}"

		if (uri != None) and (uri != ""):
			if uri == "/":
				url += "/"

			elif uri[0] == "/":
				url += uri

			else:
				url += f"/{uri}"

		return url

	# Returns Json
	def ntlm_info(self):
		url    = self._format_url(uri=self.uri)
		client = _NtlmClient()
		result = client.http_ntlm_info(url)

		ntlm_info = {
			"host": self.host,
			"port": self.port,
			"ssl": self.ssl,
			"uri": self.uri,
			"url": url,
			"result": result
		}

		return json.dumps(ntlm_info)

	# Returns Json
	def ntlm_login(self, user, password, domain=None):
		assert (isinstance(domain, str)) or (domain == None)
		assert isinstance(user, str)
		assert isinstance(password, str)

		url    = self._format_url(uri=self.uri)
		client = _NtlmClient()

		result = client.http_ntlm_login(url, user, password, domain=domain)

		ntlm_login = {
			"host": self.host,
			"port": self.port,
			"ssl": self.ssl,
			"uri": self.uri,
			"url": url,
			"domain": domain,
			"user": user,
			"password": password,
			"result": result
		}

		return json.dumps(ntlm_login)
