SELECT id, domain, username, password, seconds, pre_status_code, pre_status_text, post_status_code, post_status_text
FROM
	wb3.web_ntlm_login
WHERE
	(wb3.web_ntlm_login.pre_status_code != wb3.web_ntlm_login.post_status_code)
    OR
	(wb3.web_ntlm_login.post_status_code != 401)