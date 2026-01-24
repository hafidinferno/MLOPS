$remoteport = bash.exe -c "ifconfig eth0 | grep 'inet ' | awk '{print `$2}'"
$found = $remoteport -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}';

if( $found ){
  $remoteport = $matches[0];
} else {
  echo "The Script Exited, the ip address of WSL 2 cannot be found";
  exit;
}

$ports=@(8080, 8501, 8000, 5678);

echo "WSL IP Address is: $remoteport"

for( $i = 0; $i -lt $ports.count; $i++ ){
  $port = $ports[$i];
  echo "Forwarding Port: $port";
  iex "netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0";
  iex "netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$remoteport";
}

echo "Ports forwarded successfully. Try accessing http://localhost:8501 now.";
