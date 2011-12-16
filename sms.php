<?php

/* 

Pygmy Shark, v.1

Written by Scott Ogle (scott.ogle@grooveshark.com)

Library for responding to SMS and streaming over the phone.

*/

require_once('/f5/pygmy/public/Services/Twilio.php');
require_once('/f5/pygmy/public/gsAPI.php');

$gsapi = new gsAPI('scottogle', 'c542cf7bdcee91a5a841c41038589ccd');
$gsapi->startSession();
$gsapi->getCountry($_SERVER['REMOTE_ADDR']);
$tskey = '2b3b6d9af6e38b590b0a2401298e5acf';


$client = new Services_Twilio('ACf79b8d2f9171466286aa26d19cc0c690', 'fc231f5c1561fde424093c121e91974f');

$query = urldecode($_POST['Body']);
$from = '3522341775';
$to = $_POST['From'];

$queryArray = explode(' ', $query); //Splits query into a more manageable array
$action = $queryArray[0];
$arg = implode(' ', array_slice($queryArray, 1));


// Helper functions for common tasks

function createCall($songIDs) {
	global $client, $to, $from;
	$client->account->calls->create(
  		$from, // From this number
  		$to, // Call this number

  		// Read TwiML at this URL when a call connects
  		'http://pygmy.nfshost.com/pygmy.php?songIDs=' . $songIDs
	);
}

function createSMS($string, $recipient=null) { // Since PHP doesn't allow for using globals as arg defaults I'm using null to ensmoothen things.
	global $to, $from;
	if (!isset($recipient)) { $recipient = $to; }
	$response = new Services_Twilio_Twiml;
	$response->sms($string, array(
		'to' => 	$recipient,
		'from' => 	$from
	));
	print $response;
}


function search($query){
	global $tskey;
	
	$endpoint = 'http://tinysong.com/s/';
	$results = file_get_contents($endpoint . urlencode($query) . '?format=json&limit=3&key=' . $tskey);
	
	$responseString = 'Reply';
	
	$results = json_decode($results, true);
	
	if ($results) {
		foreach ($results as $k=>$v) {
			$exploded = explode('/', $v['Url']);
			$token = end($exploded);
			
			if ($k == 0) 		{ $responseString .= "\r\n'" . $token . "' for " . substr($v['SongName'], 0, 45) . "\r\n";}
			else if ($k == 1) 	{ $responseString .= "'" . $token . "' for " . substr($v['SongName'], 0, 45) . "\r\n";}
			else 				{ $responseString .= "'" . $token . "' for " . substr($v['SongName'], 0, 45);}
		}
		
	} else {
		error();
		return;
	}
	
	$responseString .= "\r\n*Sponsored by Grooveshark.com";
		
	createSMS($responseString);
	
}


function play($tokens) {
	global $gsapi;
	
	$IDs = array();
	foreach ($tokens as $t) {
		$IDs[] = $gsapi->getSongIDFromTinysongBase62($t);
	}
	createCall(implode(',', $IDs));
}

function lucky($query) {
	global $tskey;
	
	$endpoint = 'http://tinysong.com/a/';
	$result = file_get_contents($endpoint . urlencode($query) . '?key=' . $tskey);
	
	$exploded = explode('/', $result);
	$token = end($exploded);
	
	play(array($token));
}

function top($query) {
	global $tskey;
	
	$endpoint = 'http://tinysong.com/s/';
	$results = json_decode(file_get_contents($endpoint . urlencode($query) . '?format=json&limit=5&key=' . $tskey), true);
	
	$tokenArray = array();
	
	foreach ($results as $r) {
		$tokenArray[] = end(explode("/", $r['Url']));
	}
	
	play($tokenArray);
}

function share($token, $recipient /* Different from the global $to */) {
	global $to, $gsapi;
	$songID = $gsapi->getSongIDFromTinysongBase62($token);
	//$songInfo = $gsapi->getSongInfo($songID);
	
	createSMS($to . " has shared '" . $songInfo['SongName'] . "' by " . $songInfo['ArtistName'] . " with you! Reply '" . $token . "' to hear it now.", $recipient);
	#createSMS("Success! " . $recipient . " has receieved your song.");
}

function help() {
	createSMS("Text 'search {term}' to search for songs, 'lucky {term}' to automatically play the first result, or 'top5 {term} to play the top 5 songs.");
}

function error(){
	createSMS("Oh snap!  Something broke.  Please check your spelling and try again, or reply 'info' for more info.");
}

function debug($token){
	global $gsapi;
	$id = $gsapi->getSongIDFromTinysongBase62($token);
	$songObj = $gsapi->getStreamKeyStreamServer($id);
	$url = $songObj['url'];
	$dotExplosion = explode('.', $url);
	$justTheServer = end(explode('//', $dotExplosion[0]));
	
	createSMS($token . " : " . $url . " was reported to have failed (" . $id . ")", 9704029786);
}


if (strtolower($action) == 'search' or strtolower($action) == 's') { search($arg); }
else if (strtolower($action) == 'lucky' or strtolower($action) == 'l') { lucky($arg); }
else if (strtolower($action) == 'info' or strtolower($action) == 'i') { help(); }
else if (strtolower($action) == 'top5' or strtolower($action) == 't' or strtolower($action) == 't5') { top($arg); }
else if (strtolower($action) == 'share' or strtolower($action) == 'shr') { 
	if (count($queryArray) != 4) { error(); }
	else {
		$token = $queryArray[1];
		$recipient = $queryArray[2];
		share($token, $recipient);
	} 
}
else if (strtolower($action) == 'debug') { debug($arg); }
else { play($queryArray); }

?>