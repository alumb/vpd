#!/usr/bin/python2.5
import cgi
import cgitb; cgitb.enable()
import re
import os
import urllib
import conf

print "Content-type: text/html\n"
  

def getRequetedDir():
  form = cgi.FieldStorage()
  if form.has_key("dir"): return form["dir"].value.strip()
  else: return ""

def filter(line):
  line = urllib.unquote(line)
  line = re.sub("(?i)\.((avi)|(mov)|(divx)|(mpg)|(mp4)|(bin)|(asf)|(wmv))$","",line)
  line = re.sub("_"," ",line)
  line = re.sub("[ \.]TS"," ",line)
  line = re.sub("\[[^\]]*\]"," ",line)
  line = re.sub("\([^\)]*\)"," ",line)
  line = re.sub(" -[^ ]*"," ",line)
  line = re.sub("(?i)((dvdrip)|(dvdscr)|(internal)|(limited)|(divx)|(xvid)|(eng)|(KVCD))[^ ]*"," ",line)
  
  line = re.sub("  "," ",line)
  line = re.sub("\."," ",line)
  return line
  
def filterFiles(fileName):
  fileName = fileName.lower()
  if fileName.endswith((".cue",".txt",".nfo",".sub",".idx",".pdf",".tar")): return False
  return True
  
def main(): 
  requestedDir = getRequetedDir()
  title = requestedDir.lstrip("/") if len(requestedDir) > 0 else "File Browser"
	
  print """
<html>
	<head>
	<link rel="STYLESHEET" href="main.css" type='text/css' />
	<link media="only screen and (max-device-width: 480px)" href="iPhone.css" type="text/css" rel="stylesheet" />
	<meta name="viewport" content="width=500" />
	<script language="javascript" src="interface.js"></script>
  <script language="javascript" src="quickList.js"></script>
	</head>
<body>
	<div id="container">
		<div id="pageHeader">
			<input type="text" id="fileID" name="fileID" value=""/>
			<span class="header">"""; print title; print """- VPD</span>
		</div>
		<div id="content">
      
  """
  #<span id="outLocation" onclick="javascript:toggleLocal()"><script language="javascript">setLocal(Local);</script></span>
  
  print """<ul id="listing" name="listing">"""
  location = (requestedDir[0:requestedDir[:-1].rfind("/")]).replace("/","%2f")
  if len(requestedDir) > 0: print "<li class='active' data=\"dire|%s\" onclick=\"document.location='?dir=%s'\">back</li>" % (location, location)
  try:
    list = os.listdir(conf.conf["directories"].strip() + requestedDir)
    list.sort(key=str.lower)
    for line in list:
      if filterFiles(line):
        if os.path.isdir(conf.conf["directories"].strip() + requestedDir+os.sep+line):
          location = (requestedDir + "/" + line).replace("//","/").replace("/","%2f")
          print "<li class='active' data=\"dire|%s%%2f\" onclick=\"document.location='?dir=%s\'\">%.54s</li>" % (location, location, filter(line))
        else:
          location = (requestedDir + "/" + line.replace("'","&apos;")).replace("/","%2f")
          if( os.environ.get("SERVER_NAME") == "localhost"):
            print "<li class='active' data=\"file|%s\" onclick='loadFile(\"%s\")'>%.54s</li>" % (location, location, filter(line))
          else:
            print "<li class='active' data=\"file|%s\" onclick=\"document.location='getFile.py?pls=1&file=%s\'\">%.54s</li>" % (location, location, filter(line))
  except OSError, (errno, strerror):
    print "<script language=\"javascript\">setTimeout('setLog(\"" + strerror + "\")',500);</script>"
  print """
      </ul>
		</div>

    
    <div id="status">
    &nbsp;
    </div>
	</div>

  <script language="javascript">
    attachQuickList(document.getElementById("fileID"),document.getElementById("listing"), "/(%1)/i", chLoc, "pageHeader", "status", indexChanged);
    document.getElementById("fileID").focus();
  </script>


</body></html>"""



main()