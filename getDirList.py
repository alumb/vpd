#!/usr/bin/python2.5
import cgi
import cgitb; cgitb.enable()
import os


print "Content-type: text/html\n"

conf = dict()

for line in open("vpd.conf",'r'):
  if len(line.strip()) <=0 or line[0] == "#" or line[0] == "[": continue
  lines = line.split("=")
  if len(lines) != 2: print "Config Error: " + str(len(line)) + line; quit()
  conf[lines[0]] = lines[1]

form = cgi.FieldStorage()
if form.has_key("dir"): 
  directory = form["dir"].value.strip()
  print "<a class='link' onclick='loadDir(\""+ directory[0:directory.rfind("/")] + "\")'>back<a/>"
else: 
  directory = ""
 

for line in os.listdir(conf["directories"] + directory):
  if os.path.isdir(conf["directories"] + directory+os.sep+line):
    print "<li><a class='link' onclick='loadDir(\"%s/%s\")'>%s<a/>" % (directory, line, line)
  else:
    print "<li><a class='link' onclick='loadFile(\"%s/%s\")'>%s<a/>" % (directory, line.replace("'","&apos;"), line)
	

	