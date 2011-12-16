<?php

require_once('/f5/pygmy/public/Services/Twilio.php');
require_once('/f5/pygmy/public/gsAPI.php');

$gsapi = new gsAPI('scottogle', 'c542cf7bdcee91a5a841c41038589ccd');
$gsapi->startSession();
$gsapi->getCountry($_SERVER['REMOTE_ADDR']);


if (!isset($_GET['songIDs'])) { $_GET['songIDs'] = '7321808'; }
$songIDs = explode(',', $_GET['songIDs']);

$response = new Services_Twilio_Twiml;

foreach ($songIDs as $id) {
	$songURL = $gsapi->getStreamKeyStreamServer($id);
	$response->play($songURL['url']);
}

print $response;
?>