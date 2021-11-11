#!/bin/bash

# If no argument supplied
if [ $# -eq 0 ]
  then
    echo "usage bash traffic.sh <target_ip>"
else 
	TARGET_IP="$@"
	echo $TARGET_IP
  	while true; do
	    N_PACKETS=$(shuf -i 10-20 -n 1)
	    N_BYTES=$(shuf -i 150-200 -n 1)
	    PAUSE=$(shuf -i 1-10 -n 1)
	    ping -c 1 "$TARGET_IP"
	    sudo hping3 -c $N_PACKETS -d $N_BYTES --icmp "$TARGET_IP"
	    sleep $PAUSE
	    echo "ok"
	done
fi
