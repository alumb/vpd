
log = ""
logTimerRunning = false

function setContent(value) { document.getElementById("content").innerHTML = value; }
function setStatus(value) { 
  for(var i = 52; i < value.length; i += 52) value = value.substr(0,i) + "&thinsp;" + value.substr(i);
  document.getElementById("status").innerHTML = value; 
}

function setLog(value) {
  if(value == "logTimmer") {
    if(log.indexOf('\n')>=0) log = log.substr(log.toLowerCase().indexOf('\n')+1);
    else log = "";
    logTimerRunning = false;
    value = "";
  }
  if(value.length>0) {
    if (log.length > 0) log += "\n"
    log += value
  }
  if(log.length <=0) { 
    logTimerRunning = false; 
    document.getElementById("status").style.height = "0em";
    document.getElementById("status").innerHTML = "";
  }
  else {
    document.getElementById("status").style.height = "auto";
    document.getElementById("status").innerHTML = log.replace(/<br\/>/g,"\n").replace(/\n\n/g,"\n").replace(/\n/g,"<br>");
    if(!logTimerRunning) {
      logTimerRunning = true;
      setTimeout("setLog('logTimmer');", 4000 );  
    }
  }
}

function loadFile(file) {
  	var xmlHttp = new XMLHttpRequest();
    setLog("Contacting Server");
  	xmlHttp.open("POST", "cmdMplayer.py", false);
    xmlHttp.setRequestHeader('Content-Type','application/x-www-form-urlencoded');
  	xmlHttp.send("file="+escape(file));
    if(xmlHttp.status == 500) {
      setLog("500 Server Error")
    }
    else {
      setLog(xmlHttp.responseText);
    }
}

function chLoc(innerHTML,data,linkObject) {
  if (linkObject && linkObject.attributes['onclick'] && linkObject.attributes['onclick'].value)
    eval(linkObject.attributes['onclick'].value)
  else if(data.substr(0,4) == "file") {
    loadFile(data.substr(5));
  } else {
    document.location = "?dir=" + data.substr(5);  
  }
}

function indexChanged(newListItem) {
  data = newListItem.getAttribute("data").replace(/\%2f/ig,"/");
  status = data.substr(Math.max(data.slice(0,-1).lastIndexOf("/")+1,5));
  if(log.length<=0)  setStatus(status);
  else setLog(status);
}