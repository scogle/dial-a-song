<?php
require_once('/f5/pygmy/public/Services/Twilio.php');

$accountSid = "ACf79b8d2f9171466286aa26d19cc0c690";

$authToken = "fc231f5c1561fde424093c121e91974f";

$appSid = "AP013e248ecd4c4ab6975de01a158b5434"; // YOUR APPLICATION SID!

$clientName = $_GET["client"]; // The client name for incoming connections
$capability = new Services_Twilio_Capability($accountSid, $authToken);

// This allows incoming connections as $clientName:
$capability->allowClientIncoming($clientName);

// This allows outgoing connections to $appSid with the "From" parameter being $clientName
$capability->allowClientOutgoing($appSid, array(), $clientName);

// This returns a token to use with Twilio based on
// the account and capabilities defined above
$token = $capability->generateToken();

echo $token;
?>