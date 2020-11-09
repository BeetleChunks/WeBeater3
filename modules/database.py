import pymysql
import uuid

from configs import settings

class InvalidHostId(Exception):
	pass

class InvalidServiceId(Exception):
	pass

class InvalidWebPageId(Exception):
	pass

class InvalidWebRequestId(Exception):
	pass

class DuplicateHost(Exception):
	pass

class DuplicateService(Exception):
	pass

class DuplicateWebPage(Exception):
	pass

class DuplicateNtlmInfo(Exception):
	pass

class DuplicateNtlmLogin(Exception):
	pass

class WeB3Db:
	def __init__(self):
		self.debug  = settings.general["debug"]["db"]
		self.host   = None
		self.port   = None
		self.user   = None
		self.passwd = None

	# +----------------------+
	# | Private DB Functions |
	# +----------------------+
	def _create_db_wb3(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create database
		cursor.execute('''CREATE DATABASE IF NOT EXISTS `wb3`''')

		cursor.close()

	def _create_table_hosts(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`hosts` (`id` INT AUTO_INCREMENT PRIMARY KEY, `hostname` TEXT NOT NULL)''')

		cursor.close()

	def _create_table_services(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`services` (`id` INT AUTO_INCREMENT PRIMARY KEY, `hid` INT NOT NULL, `port` INT NOT NULL, `ssl` BOOLEAN NOT NULL, `web` BOOLEAN NOT NULL)''')

		cursor.close()

	def _create_table_web_pages(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`web_pages` (`id` INT AUTO_INCREMENT PRIMARY KEY, `sid` INT NOT NULL, `uri` TEXT NOT NULL)''')

		cursor.close()

	def _create_table_web_requests(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`web_requests` (`id` INT AUTO_INCREMENT PRIMARY KEY, `wpid` INT NOT NULL, `ruid` VARCHAR(32) NOT NULL UNIQUE, `status_code` INT NOT NULL, `status_text` TEXT NOT NULL, `req_method` VARCHAR(255) NOT NULL, `req_datetime` DATETIME NOT NULL, `req_headers` TEXT, `req_data` TEXT, `resp_datetime` DATETIME NOT NULL, `resp_headers` TEXT NOT NULL, `resp_data` TEXT, `ntlm_info` BOOLEAN NOT NULL, `basic_info` BOOLEAN NOT NULL, `digest_info` BOOLEAN NOT NULL, `krb_info` BOOLEAN NOT NULL, `negotiate_info` BOOLEAN NOT NULL, `ntlm_login` BOOLEAN NOT NULL, `basic_login` BOOLEAN NOT NULL, `digest_login` BOOLEAN NOT NULL, `krb_login` BOOLEAN NOT NULL, `negotiate_login` BOOLEAN NOT NULL)''')

		cursor.close()

	def _create_table_web_ntlm_info(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`web_ntlm_info` (`id` INT AUTO_INCREMENT PRIMARY KEY, `wrid` INT NOT NULL, `flags` VARCHAR(255) NOT NULL, `flag_chars` VARCHAR(255) NOT NULL, `target_name` TEXT NOT NULL, `nb_computer_name` TEXT NOT NULL, `nb_domain_name` TEXT NOT NULL, `dns_computer_name` TEXT NOT NULL, `dns_domain_name` TEXT NOT NULL)''')

		cursor.close()

	def _create_table_web_ntlm_login(self, warn=False):
		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()
		if warn != True:
			cursor._defer_warnings = True

		# Create table
		cursor.execute('''CREATE TABLE IF NOT EXISTS `wb3`.`web_ntlm_login` (`id` INT AUTO_INCREMENT PRIMARY KEY, `wrid` INT NOT NULL, `domain` TEXT, `username` TEXT NOT NULL, `password` TEXT NOT NULL, `seconds` DECIMAL(5,3) NOT NULL, `pre_status_code` INT NOT NULL, `pre_status_text` TEXT NOT NULL, `pre_resp_headers` TEXT NOT NULL, `post_status_code` INT NOT NULL, `post_status_text` TEXT NOT NULL, `post_resp_headers` TEXT NOT NULL)''')

		cursor.close()

	
	# +------------------------+
	# | Connectivity Functions |
	# +------------------------+
	def connect(self):
		try:
			assert isinstance(self.host, str)
			assert (self.port >= 0) and (self.port <= 65535)
			assert isinstance(self.user, str)
			assert isinstance(self.passwd, str)

			self.conn = pymysql.connect(
				host=self.host, port=self.port,
				user=self.user, passwd=self.passwd
			)

			status = True

		except:
			status = False

		if status == True:
			self._create_db_wb3()
			self._create_table_hosts()
			self._create_table_services()
			self._create_table_web_pages()
			self._create_table_web_requests()
			self._create_table_web_ntlm_info()
			self._create_table_web_ntlm_login()

		return status

	def disconnect(self):
		try:
			self.conn.close()
		except:
			pass

	
	# +------------------+
	# | Insert Functions |
	# +------------------+
	def insert_host(self, host_dict):
		hostname = host_dict["host"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify host doesnt exist
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`hosts` WHERE `hostname` = %s COLLATE utf8mb4_bin''', (hostname,))

		# Fetch results
		data = cursor.fetchall()

		if int(data[0][0]) == 0:
			# Insert host if it doesnt exist
			cursor.execute('''INSERT INTO `wb3`.`hosts` (`hostname`) VALUES (%s)''', (hostname,))

			# Commit changes
			self.conn.commit()

		else:
			if self.debug == True:
				print(f"[DEBUG] Duplicate host detected. Host not inserted.")

			# Close database cursor
			cursor.close()

			raise DuplicateHost

		# Close database cursor
		cursor.close()

	def insert_service(self, service_dict):
		hid  = service_dict["hid"]
		port = service_dict["port"]
		ssl  = service_dict["ssl"]
		web  = service_dict["web"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify host id 'hid' is valid
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`hosts` WHERE `id` = %s''', (hid,))

		# Fetch results
		host_data = cursor.fetchall()

		if int(host_data[0][0]) != 0:
			# Verify service doesnt exist
			cursor.execute('''SELECT COUNT(*) FROM `wb3`.`services` WHERE `hid` = %s AND `port` = %s''', (hid, port))

			# Fetch results
			service_data = cursor.fetchall()

			if int(service_data[0][0]) == 0:
				# Insert service if it doesnt exist
				cursor.execute('''INSERT INTO `wb3`.`services` (`hid`, `port`, `ssl`, `web`) VALUES (%s, %s, %s, %s)''', (hid, port, ssl, web))

				# Commit changes
				self.conn.commit()

			else:
				if self.debug == True:
					print(f"[DEBUG] Duplicate service detected. Service not inserted.")

				# Close database cursor
				cursor.close()

				raise DuplicateService

		else:
			if self.debug == True:
				print(f"[DEBUG] Host Id '{hid}' doesn't exist. Service not inserted.")

			# Close database cursor
			cursor.close()

			raise InvalidHostId

		# Close database cursor
		cursor.close()

	def insert_web_page(self, page_dict):
		sid = page_dict["sid"]
		uri = page_dict["uri"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify service id 'sid' is valid and service type is web
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`services` WHERE `id` = %s AND `web` = TRUE''', (sid,))

		# Fetch results
		service_data = cursor.fetchall()

		if int(service_data[0][0]) != 0:
			# Verify web_page doesnt exist for the given service
			cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_pages` WHERE `sid` = %s AND `uri` = %s COLLATE utf8mb4_bin''', (sid, uri,))

			# Fetch results
			page_data = cursor.fetchall()

			if int(page_data[0][0]) == 0:
				# Insert web page if it doesnt exist
				cursor.execute('''INSERT INTO `wb3`.`web_pages` (`sid`, `uri`) VALUES (%s, %s)''', (sid, uri))

				# Commit changes
				self.conn.commit()

			else:
				if self.debug == True:
					print(f"[DEBUG] Duplicate web page detected. Web page not inserted.")

				# Close database cursor
				cursor.close()

				raise DuplicateWebPage

		else:
			if self.debug == True:
				print(f"[DEBUG] Service Id '{sid}' either doesn't exist or isn't web. Web page not inserted.")

			# Close database cursor
			cursor.close()

			raise InvalidServiceId

		# Close database cursor
		cursor.close()

	def insert_web_request(self, request_dict):
		wpid = request_dict["wpid"]
		ruid = uuid.uuid1().hex
		
		status_code = request_dict["status_code"]
		status_text = request_dict["status_text"]
		
		req_method   = request_dict["req_method"]
		req_datetime = request_dict["req_datetime"]
		req_headers  = request_dict["req_headers"]
		req_data     = request_dict["req_data"]

		resp_datetime = request_dict["resp_datetime"]
		resp_headers  = request_dict["resp_headers"]
		resp_data     = request_dict["resp_data"]

		ntlm_info      = request_dict["ntlm_info"]
		basic_info     = request_dict["basic_info"]
		digest_info    = request_dict["digest_info"]
		krb_info       = request_dict["krb_info"]
		negotiate_info = request_dict["negotiate_info"]

		ntlm_login      = request_dict["ntlm_login"]
		basic_login     = request_dict["basic_login"]
		digest_login    = request_dict["digest_login"]
		krb_login       = request_dict["krb_login"]
		negotiate_login = request_dict["negotiate_login"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify web page id 'wpid' is valid
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_pages` WHERE `id` = %s''', (wpid,))

		# Fetch results
		page_data = cursor.fetchall()

		if int(page_data[0][0]) != 0:
			# Insert web request
			cursor.execute('''INSERT INTO `wb3`.`web_requests` (`wpid`, `ruid`, `status_code`, `status_text`, `req_method`, `req_datetime`, `req_headers`, `req_data`, `resp_datetime`, `resp_headers`, `resp_data`, `ntlm_info`, `basic_info`, `digest_info`, `krb_info`, `negotiate_info`, `ntlm_login`, `basic_login`, `digest_login`, `krb_login`, `negotiate_login`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (wpid, ruid, status_code, status_text, req_method, req_datetime, req_headers, req_data, resp_datetime, resp_headers, resp_data, ntlm_info, basic_info, digest_info, krb_info, negotiate_info, ntlm_login, basic_login, digest_login, krb_login, negotiate_login))

			# Commit changes
			self.conn.commit()

		else:
			if self.debug == True:
				print(f"[DEBUG] Web Page Id '{wpid}' doesn't exist. Web request not inserted.")

			# Close database cursor
			cursor.close()

			raise InvalidWebPageId

		# Close database cursor
		cursor.close()

		return ruid

	def insert_web_ntlm_info(self, ntlm_info_dict):
		wrid = ntlm_info_dict["wrid"]
		
		flags      = ntlm_info_dict["flags"]
		flag_chars = ntlm_info_dict["flag_chars"]
		
		target_name = ntlm_info_dict["target_name"]
		
		nb_computer_name = ntlm_info_dict["nb_computer_name"]
		nb_domain_name   = ntlm_info_dict["nb_domain_name"]
		
		dns_computer_name = ntlm_info_dict["dns_computer_name"]
		dns_domain_name   = ntlm_info_dict["dns_domain_name"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify web request id 'wrid' is valid and that the web
		# request was marked true for 'ntlm_info'
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_requests` WHERE `id` = %s AND `ntlm_info` = TRUE''', (wrid,))

		# Fetch results
		request_data = cursor.fetchall()

		if int(request_data[0][0]) > 0:
			# Verify ntlm info not already inserted for given web request id 'wrid'
			cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_ntlm_info` WHERE `wrid` = %s''', (wrid,))

			# Fetch results
			ntlm_info_data = cursor.fetchall()

			if int(ntlm_info_data[0][0]) == 0:
				# Insert ntlm info
				cursor.execute('''INSERT INTO `wb3`.`web_ntlm_info` (`wrid`, `flags`, `flag_chars`, `target_name`, `nb_computer_name`, `nb_domain_name`, `dns_computer_name`, `dns_domain_name`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (wrid, flags, flag_chars, target_name, nb_computer_name, nb_domain_name, dns_computer_name, dns_domain_name))

				# Commit changes
				self.conn.commit()

			else:
				if self.debug == True:
					print(f"[DEBUG] Duplicate NTLM Info for wrid '{wrid}'. NTLM Info not inserted.")

				# Close database cursor
				cursor.close()

				raise DuplicateNtlmInfo

		else:
			if self.debug == True:
				print(f"[DEBUG] Web Request Id '{wrid}' either doesn't exist or isn't true for ntlm auth. NTLM Info not inserted.")

			# Close database cursor
			cursor.close()

			raise InvalidWebRequestId

		# Close database cursor
		cursor.close()

	def insert_web_ntlm_login(self, ntlm_login_dict):
		wrid = ntlm_login_dict["wrid"]
		
		domain   = ntlm_login_dict["domain"]
		username = ntlm_login_dict["username"]
		password = ntlm_login_dict["password"]
		
		seconds = ntlm_login_dict["seconds"]
		
		pre_status_code  = ntlm_login_dict["pre_status_code"]
		pre_status_text  = ntlm_login_dict["pre_status_text"]
		pre_resp_headers = ntlm_login_dict["pre_resp_headers"]
		
		post_status_code = ntlm_login_dict["post_status_code"]
		post_status_text = ntlm_login_dict["post_status_text"]
		post_resp_headers = ntlm_login_dict["post_resp_headers"]

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Verify web request id 'wrid' is valid and that the web
		# request was marked true for 'ntlm_login'
		cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_requests` WHERE `id` = %s AND `ntlm_login` = TRUE''', (wrid,))

		# Fetch results
		request_data = cursor.fetchall()

		if int(request_data[0][0]) > 0:
			# Verify ntlm login not already inserted for given web request id 'wrid'
			cursor.execute('''SELECT COUNT(*) FROM `wb3`.`web_ntlm_login` WHERE `wrid` = %s''', (wrid,))

			# Fetch results
			ntlm_login_data = cursor.fetchall()

			if int(ntlm_login_data[0][0]) == 0:
				# Insert ntlm info
				cursor.execute('''INSERT INTO `wb3`.`web_ntlm_login` (`wrid`, `domain`, `username`, `password`, `seconds`, `pre_status_code`, `pre_status_text`, `pre_resp_headers`, `post_status_code`, `post_status_text`, `post_resp_headers`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (wrid, domain, username, password, seconds, pre_status_code, pre_status_text, pre_resp_headers, post_status_code, post_status_text, post_resp_headers))

				# Commit changes
				self.conn.commit()

			else:
				if self.debug == True:
					print(f"[DEBUG] Duplicate NTLM Login for wrid '{wrid}'. NTLM Login not inserted.")

				# Close database cursor
				cursor.close()

				raise DuplicateNtlmLogin

		else:
			if self.debug == True:
				print(f"[DEBUG] Web Request Id '{wrid}' either doesn't exist or isn't true for ntlm auth. NTLM Login not inserted.")

			# Close database cursor
			cursor.close()

			raise InvalidWebRequestId

		# Close database cursor
		cursor.close()


	# +----------------+
	# | Find Functions |
	# +----------------+
	def get_host_id(self, hostname):
		assert isinstance(hostname, str)

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Get id for given host if it exists
		cursor.execute('''SELECT `id` FROM `wb3`.`hosts` WHERE `hostname` = %s''', (hostname,))

		# Fetch results
		data = cursor.fetchall()

		# Return id or None if not found
		if len(data) > 0:
			hid = data[0][0]

		else:
			hid = None

		# Close database cursor
		cursor.close()

		return hid

	def get_service_id(self, hid, port):
		assert isinstance(hid, int)
		assert isinstance(port, int)

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Get id for given service port if it exists
		cursor.execute('''SELECT `id` FROM `wb3`.`services` WHERE `hid` = %s AND `port` = %s''', (hid, port))

		# Fetch results
		data = cursor.fetchall()

		# Return id or None if not found
		if len(data) > 0:
			sid = data[0][0]

		else:
			sid = None

		# Close database cursor
		cursor.close()

		return sid

	def get_web_page_id(self, sid, uri):
		assert isinstance(sid, int)
		assert isinstance(uri, str)

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Get id for given service id and uri if it exists
		cursor.execute('''SELECT `id` FROM `wb3`.`web_pages` WHERE `sid` = %s AND `uri` = %s COLLATE utf8mb4_bin''', (sid, uri))

		# Fetch results
		data = cursor.fetchall()

		# Return id or None if not found
		if len(data) > 0:
			wpid = data[0][0]

		else:
			wpid = None

		# Close database cursor
		cursor.close()

		return wpid

	def get_web_request_id(self, wpid, ruid):
		assert isinstance(wpid, int)
		assert isinstance(ruid, str)

		# prepare a cursor object using cursor() method
		cursor = self.conn.cursor()

		# Get id for given web page id and ruid
		cursor.execute('''SELECT `id` FROM `wb3`.`web_requests` WHERE `wpid` = %s AND `ruid` = %s COLLATE utf8mb4_bin''', (wpid, ruid))

		# Fetch results
		data = cursor.fetchall()

		# Return id or None if not found
		if len(data) > 0:
			wrid = data[0][0]

		else:
			wrid = None

		# Close database cursor
		cursor.close()

		return wrid
