<?php

require('/f5/pygmy/public/Services/Twilio.php');
require('/f5/pygmy/public/gsAPI.php');

$gsapi = new gsAPI('scottogle', 'c542cf7bdcee91a5a841c41038589ccd');
$gsapi->startSession();
$gsapi->getCountry($_SERVER['REMOTE_ADDR']);

$ongURL = $gsapi->getStreamKeyStreamServer(24539127);

$response = new Services_Twilio_Twiml();

# ToDo - Get caller's country from $_GET for stream region

$response->play($ongURL['url']);

$response->say('Rick Roll');

print $response;

?>