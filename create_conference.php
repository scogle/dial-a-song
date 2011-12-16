<?php

require_once('/f5/pygmy/public/Services/Twilio.php');
require_once('/f5/pygmy/public/gsAPI.php');

$recipient = $_REQUEST['recipient'];
$initiator = $_REQUEST['from'];
$conferenceID = $recipient . "-conf";

$client = new Services_Twilio('ACf79b8d2f9171466286aa26d19cc0c690', 'fc231f5c1561fde424093c121e91974f');

//Call the recipient of the share
$client->account->calls->create(
  '3522341775', // From this number
  $recipient, // Call this number
  'http://pygmy.nfshost.com/conference.php?conferenceID=' . $conferenceID
);

//Call the initiator
$call = $client->account->calls->create(
  "3522341775", // From this number
  $initiator, // Call this number
  'http://pygmy.nfshost.com/conference.php?conferenceID=' . $conferenceID
);

//Call the conference and point it to pygmy
$client->account->calls->create(
  '3522341775', // From this number
  $conferenceID, // Call this conference
  'http://pygmy.nfshost.com/test.xml'
);
?>
