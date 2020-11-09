CREATE DATABASE [IF NOT EXISTS] wb3;

CREATE TABLE [IF NOT EXISTS] hosts(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- Hostname or IP
	hostname TEXT NOT NULL
);

CREATE TABLE [IF NOT EXISTS] services(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- wb3.hosts.id
	hid INT NOT NULL,

	-- Service port
	port INT NOT NULL,

	-- Uses SSL
	ssl BOOLEAN NOT NULL,

	-- Service Type: Web
	web BOOLEAN NOT NULL
);

CREATE TABLE [IF NOT EXISTS] web_pages(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- wb3.services.id
	sid INT NOT NULL,

	-- Page URI
	uri TEXT NOT NULL
);

CREATE TABLE [IF NOT EXISTS] web_requests(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- wb3.web_pages.id
	wpid INT NOT NULL,

	-- Web Request's Unique Id
	ruid VARCHAR(32) NOT NULL UNIQUE,

	-- Status Code
	status_code INT NOT NULL,

	-- Status Text
	status_text TEXT NOT NULL,

	-- Request method
	req_method VARCHAR(255) NOT NULL,

	-- Request datetime
	req_datetime DATETIME NOT NULL,

	-- Request headers json blob
	req_headers TEXT,

	-- Request data blob
	req_data TEXT,

	-- Response datetime
	resp_datetime DATETIME NOT NULL,

	-- Response headers json blob
	resp_headers TEXT NOT NULL,

	-- Response data blob
	resp_data TEXT,

	-- NTLM authentication info
	ntlm_info BOOLEAN NOT NULL,

	-- Basic authentication info
	basic_info BOOLEAN NOT NULL,

	-- Digest authentication info
	digest_info BOOLEAN NOT NULL,

	-- Kerberos authentication info
	krb_info BOOLEAN NOT NULL,

	-- Negotiate authentication info
	negotiate_info BOOLEAN NOT NULL,

	-- NTLM authentication login
	ntlm_login BOOLEAN NOT NULL,

	-- Basic authentication login
	basic_login BOOLEAN NOT NULL,

	-- Digest authentication login
	digest_login BOOLEAN NOT NULL,

	-- Kerberos authentication login
	krb_login BOOLEAN NOT NULL,

	-- Negotiate authentication login
	negotiate_login BOOLEAN NOT NULL
);

CREATE TABLE [IF NOT EXISTS] web_ntlm_info(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- wb3.web_requests.id
	wrid INT NOT NULL,

	-- NTLM flags
	flags VARCHAR(255) NOT NULL,

	-- NTLM flag characters
	flag_chars VARCHAR(255) NOT NULL,

	-- Target name
	target_name TEXT NOT NULL,

	-- NetBIOS computer name
	nb_computer_name TEXT NOT NULL,

	-- NetBIOS domain name
	nb_domain_name TEXT NOT NULL,

	-- DNS computer name
	dns_computer_name TEXT NOT NULL,

	-- DNS domain name
	dns_domain_name TEXT NOT NULL
);

CREATE TABLE [IF NOT EXISTS] web_ntlm_login(
	-- Table ID Column
	id INT AUTO_INCREMENT PRIMARY KEY,

	-- wb3.web_requests.id
	wrid INT NOT NULL,

	-- Login domain
	domain TEXT,

	-- Login username
	username TEXT NOT NULL,

	-- Login password
	password TEXT NOT NULL,

	-- Login time in seconds
	seconds DECIMAL(5,3) NOT NULL,

	-- Pre-auth status code
	pre_status_code INT NOT NULL,

	-- Pre-auth status text
	pre_status_text TEXT NOT NULL,

	-- Pre-auth response headers json blob
	pre_resp_headers TEXT NOT NULL,
	
	-- Post-auth status code
	post_status_code INT NOT NULL,
	
	-- Post-auth status text
	post_status_text TEXT NOT NULL,

	-- Post-auth response headers json blob
	post_resp_headers TEXT NOT NULL,
);