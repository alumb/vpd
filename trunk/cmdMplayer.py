#!/usr/bin/python2.5
#this file generates the command to play the given file and sends it to the vpd server
import cgi
import os
import sys
import socket
import time
from threading import Thread
import vpd_core
import conf

print "Content-type: text/html\n"
form = cgi.FieldStorage()


def log(data):
  print data
 
file = conf.conf["directories"].strip() +  form["file"].value.replace("%2f","/")

client = vpd_core.Client()
client.log = log
try: 
  client.connect(host="localhost", port=50001)
except socket.gaierror, error:
  log(error[1])
  client.close()

  
t = Thread(target=vpd_core.loop)
t.setDaemon(True)
t.start()  
  
if not client.connected:
  log("Connecting...")
  attempts = 5
while not client.connected and attempts:
  time.sleep(0.5)
  attempts -= 1
  
try:
  if not t.isAlive():
    log("Could not connect to server.")
    client.close()
  else:
    log("Connected")        
    client.send_command("play " + file)
    time.sleep(2)
    client.close()

except socket.error, msg:
  log(str(msg))
  client.close()



