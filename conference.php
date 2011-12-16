<?php
	$conferenceID = $_REQUEST["conferenceID"];
	header('Content-type: text/xml');
?>

<Response>
	<Dial>
		<Conference><?php echo $conferenceID;?></Conference>
	</Dial>
</Response>
