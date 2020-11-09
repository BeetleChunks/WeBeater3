SELECT wb3.web_requests.id, dt2.hostname, dt2.port, dt2.ssl, dt2.uri, wb3.web_requests.status_code,
	wb3.web_requests.status_text, wb3.web_requests.resp_headers FROM wb3.web_requests
JOIN
	(SELECT wb3.web_pages.id, dt1.hostname, dt1.port, dt1.ssl, wb3.web_pages.uri FROM wb3.web_pages
	JOIN
		(SELECT wb3.services.id, wb3.hosts.hostname, wb3.services.port, wb3.services.ssl, wb3.services.web
		FROM wb3.hosts
		JOIN
			wb3.services
		ON wb3.hosts.id = wb3.services.hid) dt1
	ON dt1.id = wb3.web_pages.sid) dt2
ON dt2.id = wb3.web_requests.wpid;