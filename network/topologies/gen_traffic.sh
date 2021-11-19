#!/bin/bash

# If no argument supplied
if [ $# -eq 0 ]; then
	echo "usage bash traffic.sh <target_ip>"
else 
	TARGET_IP="$@"
	PIDS=$(ps aux | grep "mininet:h" | cut -c5-16 | tail -n+2)
	N_PIDS=$(echo $PIDS | wc -w)

	mkdir -p /var/run/netns

	trap "exit" INT TERM ERR
	trap "rm -rf /var/run/netns && kill 0" EXIT

	I=1
	while read PID; do
		ln -sf /proc/$PID/ns/net /var/run/netns/$PID
		if [ $I -ge $(($N_PIDS / 2)) ]; then
			ip netns exec $PID bash ./traffic.sh $TARGET_IP &
		else
			ip netns exec $PID bash ./traffic_peak.sh $TARGET_IP &
		fi
		I=$((I+1))
	done <<< "$PIDS"
	wait
fi
