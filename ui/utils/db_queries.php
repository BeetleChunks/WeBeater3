<?php

	function get_ntlm_auth_count($servername, $username, $password) {
		// Connect to MySQL database
		$conn = new mysqli($servername, $username, $password);

		if ($conn->connect_error) {
			die("Connection failed: " . $conn->connect_error);
		}

		// Get data from database
		$sql = "SELECT COUNT(*) FROM wb3.web_ntlm_login ORDER BY id DESC";

		$results = $conn->query($sql);
		$row = $results->fetch_assoc();

		// Close connection
		$conn->close();

		return $row["COUNT(*)"];
	}

	function get_ntlm_auth_results($servername, $username, $password, $start, $num_results) {
		// Connect to MySQL database
		$conn = new mysqli($servername, $username, $password);

		if ($conn->connect_error) {
			die("Connection failed: " . $conn->connect_error);
		}

		// Get data from database
		$sql = "SELECT id, domain, username, password, seconds, pre_status_code, pre_status_text, post_status_code, post_status_text FROM wb3.web_ntlm_login ORDER BY id DESC LIMIT " . $start . ", " . $num_results;

		$results = $conn->query($sql);

		$table_array = array(array("id", "domain", "username", "password", "seconds", "pre_status_code", "pre_status_text", "post_status_code", "post_status_text"));

		if ($results->num_rows > 0) {
			$i = 1;
			
			while($row = $results->fetch_array()) {
				$table_array[$i] = $row;
				$i++;
			}
		}

		// Close connection
		$conn->close();

		return $table_array;
	}

?>