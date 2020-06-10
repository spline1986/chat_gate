#!/bin/bash

echo "Waiting for telegram gate..."
./tg_gate.py &
tg_pid=$!
sleep 5
echo "Waiting for xmpp gate..."
./xmpp_gate.py &
xmpp_pid=$!
sleep 5
echo "Waiting dispatcher..."
./dispatcher.py &
dispatcher_pid=$!
echo "Waiting webserver..."
./webserver.py &
webserver_pid=$!
echo "Done!"
echo "Press ENTER for stop gate."
read
kill -9 $tg_pid
kill -9 $xmpp_pid
kill -9 $dispatcher_pid
kill -9 $webserver_pid
rm /tmp/tg*
rm /tmp/xmpp*