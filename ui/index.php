<!DOCTYPE html>
<html lang="en-US">
<head>
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
	<link rel="stylesheet" type="text/css" href="css/mystyle.css">
	<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
	<div id="all-ntlm-auth"></div>
	<button type="button" onclick="loadDoc()">Change Content</button>

	<script>
	function loadDoc() {
		var xhttp = new XMLHttpRequest();
		
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				document.getElementById("all-ntlm-auth").innerHTML = this.responseText;
			}
		};
		
		xhttp.open("GET", "NtlmAuthTable.php", true);
		xhttp.send();
	}
	</script>
</body>
</html>