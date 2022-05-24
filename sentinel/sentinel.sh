#!/bin/sh


case "$1" in
	start)
		echo "Starting Redis Instances"
		redis-server --port 1111 &
		sleep 3
                redis-server --port 2222 --slaveof 127.0.0.1 1111 &
                sleep 3
		redis-server ./sentinel.conf --port 5001 --sentinel &
                ;;
	stop)
		echo "Stopping.."
		redis-cli -p 1111 shutdown
		sleep 3
                redis-cli -p 2222 shutdown
		sleep 3
                redis-cli -p 5000 shutdown
		;;
	status)
		redis-cli -p 1111 ping
                redis-cli -p 2222 ping
                redis-cli -p 5000 ping
		;;
	*)
		echo "Usage: start, stop, status"
		;;
esac

