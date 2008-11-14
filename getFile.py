#!/usr/bin/python2.5
#runing this file returns the file either as a mpegurl playlist (if pls=true) or the content of the actual file.
import cgi
import cgitb; cgitb.enable()
import os
import sys
import conf 

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
    
  file = conf.conf["directories"] +  form["file"].value.replace("%2f","/")
  
  print "Content-type:video/mpeg\n"
  input = open(file,'rb')
  data = input.read(4092)
  while len(data) > 0:
    sys.stdout.write(data)
    data = input.read(4092)


