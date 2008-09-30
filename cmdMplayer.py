#!/usr/bin/python2.5
import cgi
import os
import sys
import socket
import time
from threading import Thread
import vpd_core

print "Content-type: text/html\n"
form = cgi.FieldStorage()

conf = dict()

def log(data):
  print data

for line in open("vpd.conf",'r'):
  if len(line.strip()) <=0 or line[0] == "#" or line[0] == "[": continue
  lines = line.split("=")
  if len(lines) != 2: log("Config Error: " + str(len(line)) + line); quit()
  conf[lines[0]] = lines[1]

  
file = conf["directories"] +  form["file"].value.replace("%2f","/")

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



