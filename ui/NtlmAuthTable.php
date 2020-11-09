<?php
	require_once('utils/db_queries.php');

	// DB authentication variables
	$servername = "localhost";
	$username   = "";
	$password   = "";

	// Results display variables
	$rows_per_page = 10;
	
	if(isset($_GET["page"])) {
		$page = $_GET["page"];
	}
	else {
		$page = 1;
	}

	$start = ($page-1)*$rows_per_page;
	$total_rows  = get_ntlm_auth_count($servername, $username, $password);
	$total_pages = ceil($total_rows/$rows_per_page);

	$res_rows  = get_ntlm_auth_results($servername, $username, $password, $start, $rows_per_page);

	echo '<table>';

	// Header row
	echo '<tr>';
	for ($i = 0; $i < count($res_rows[0]); $i++) {
		echo '<th style="width:50%">' . htmlspecialchars($res_rows[0][$i], ENT_QUOTES, 'UTF-8') . '</th>';
	}
	echo '</tr>';

	// Data rows
	for ($x = 1; $x < count($res_rows); $x++) {
		echo '<tr>';
		
		for ($y = 0; $y < count($res_rows[$x]); $y++) {
			echo '<td>' . htmlspecialchars($res_rows[$x][$y], ENT_QUOTES, 'UTF-8') . '</td>';
		}

		echo '</tr>';
	}
	echo '</table>';

	// Page selection
	echo '<div align="center">';
	if ($total_pages <= 5) {
		for ($i = 1; $i <= $total_pages; $i++) {
			echo ' <a href="index.php?page='.$i.'">['.$i.']</a> ';
		}
	}
	else {
		if ($page >= 5) {
			echo '<a href="index.php?page=1">Start</a>';

			if ($page < $total_pages-4) {
				for ($i = $page; $i <= $page+5; $i++) {
					echo ' <a href="index.php?page='.$i.'">['.$i.']</a> ';
				}

				echo '<a href="index.php?page='.$total_pages.'">End</a>';
			}
			else {
				for ($i = $total_pages-4; $i <= $total_pages; $i++) {
					echo ' <a href="index.php?page='.$i.'">['.$i.']</a> ';
				}
			}
		}
		else {
			for ($i = 1; $i <= 5; $i++) {
				echo ' <a href="index.php?page='.$i.'">['.$i.']</a> ';
			}

			echo '<a href="index.php?page='.$total_pages.'">End</a>';
		}
	}
	echo '</div>';
?>