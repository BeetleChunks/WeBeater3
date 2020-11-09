SELECT wb3.hosts.id, wb3.hosts.hostname, dt3.uri, dt3.status_code, dt3.status_text, dt3.resp_headers,
		dt3.nb_domain_name, dt3.dns_domain_name, dt3.dns_computer_name
FROM wb3.hosts
JOIN
	(SELECT wb3.services.hid, dt2.uri, dt2.status_code, dt2.status_text, dt2.resp_headers,
		dt2.nb_domain_name, dt2.dns_domain_name, dt2.dns_computer_name
	FROM wb3.services
	JOIN
		(SELECT wb3.web_pages.sid, wb3.web_pages.uri, dt1.status_code, dt1.status_text, dt1.resp_headers,
			dt1.nb_domain_name, dt1.dns_domain_name, dt1.dns_computer_name
		FROM wb3.web_pages
		JOIN
			(SELECT wb3.web_requests.wpid, wb3.web_requests.status_code, wb3.web_requests.status_text,
				wb3.web_requests.resp_headers, wb3.web_ntlm_info.nb_domain_name, wb3.web_ntlm_info.dns_domain_name,
				wb3.web_ntlm_info.dns_computer_name
			FROM wb3.web_ntlm_info
			JOIN wb3.web_requests
			ON wb3.web_ntlm_info.wrid = wb3.web_requests.id) dt1
		ON dt1.wpid = wb3.web_pages.id) dt2
	ON dt2.sid = wb3.services.id) dt3
ON dt3.hid = wb3.hosts.id;