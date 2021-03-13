<?php
$test_case = random_int(0, 4);
if (in_array($test_case, array(0,1))) {
	$time_to_wait=random_int(0, 50);
	sleep($time_to_wait/10);
	echo "<html><body>200 but waiting ", $time_to_wait, "</body></html>";
} else {
    header('HTTP/1.1 500 Internal Server Error');
}

?>