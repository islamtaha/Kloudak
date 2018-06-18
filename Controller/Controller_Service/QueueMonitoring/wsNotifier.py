#!/usr/bin/python3.6
import os, sys, pika, json
from websocket import create_connection
import jwt


def sendNotification(ip, port, workspace, tok, message):
	token = jwt.encode(tok, 'secret', algorithm='HS256')
	ws = create_connection("ws://" + ip + ":" + str(port) + "/ws/chat/" + workspace + "/" + token.decode("utf-8"))
	s = json.dumps({"message": message})	
	ws.send(s)
	ws.close()
