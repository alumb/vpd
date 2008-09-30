#!/usr/bin/python2.5
import cgi
import cgitb; cgitb.enable()
import os
import sys

#print "Content-type:text/plain\n"
#print str(os.environ).replace(",","\n")

def getURL(queryString = None):
  schema, stdport = (('http', '80'), ('https', '443'))[os.environ.get('SSL_PROTOCOL', '') != '']
  host = os.environ.get('HTTP_HOST')
  if not host:
      host = os.environ.get('SERVER_NAME')
      port = os.environ.get('SERVER_PORT', '80')
      if port != stdport: host = host + ":" + port
  requestURI = os.environ.get('SCRIPT_NAME')  
  result = "%s://%s%s" % (schema, host, requestURI)
  if queryString: result += "?" + queryString
  return result


form = cgi.FieldStorage()
if not form.has_key("file"):
  print "Content-type:text/plain\n"
  print "No file specified"
  quit()

  
if form.has_key("pls"):

  print "Content-type:audio/mpegurl\n"
  #print "Content-type:text/plain\n"
  print getURL("file="+form["file"].value.replace("'","&apos;").replace("/","%2f"))

else: 
  conf = dict()  
  
  for line in open("vpd.conf",'r'):
    if len(line.strip()) <=0 or line[0] == "#" or line[0] == "[": continue
    lines = line.split("=")
    if len(lines) != 2: print "Config Error: " + str(len(line)) + line; quit()
    conf[lines[0]] = lines[1]
    
  file = conf["directories"] +  form["file"].value.replace("%2f","/")
  
  print "Content-type:video/mpeg\n"
  input = open(file,'rb')
  data = input.read(4092)
  while len(data) > 0:
    sys.stdout.write(data)
    data = input.read(4092)


