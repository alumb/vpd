#!/usr/bin/python2.5
conf = dict()
for line in open("vpd.conf",'r'):
  if len(line.strip()) <=0 or line[0] == "#" or line[0] == "[": continue
  lines = line.split("=")
  if len(lines) != 2: log("Config Error: " + str(len(line)) + line); quit()
  conf[lines[0]] = lines[1]

  