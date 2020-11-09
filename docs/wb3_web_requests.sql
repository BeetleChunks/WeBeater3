SELECT * FROM wb3.web_requests WHERE
status_code != 404 AND
status_code != 302 AND
status_code != 200 AND
status_code != 503 AND
status_code != 500;