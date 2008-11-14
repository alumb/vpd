#!/usr/bin/env python
# notes: Loosly based on pymplayer by Darwin M. Bautista <djclue917@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#this file is a curses based client for vpd

import os
import sys
import time
import socket
from threading import Thread
try:
    import vpd_core
except ImportError, msg:
    sys.exit(msg)
try:
    import curses
except ImportError:
    curses = None
    
   
class vpdCmder:
   
  def init_ui(self, peername):
    self.stdscr = curses.initscr()
    
    curses.cbreak()
    self.stdscr.keypad(1)
    self.stdscr.addstr("VPD!")
    self.stdscr.addstr("Connected to %s at port %d\n" % peername)

    
  def end_ui(self):
    curses.nocbreak()
    self.stdscr.keypad(0)
    curses.endwin()
    
  def logger(self, data):
    spaces = "         ".join(["         " for x in range(10)])
    self.stdscr.addstr(2,0, spaces)
    if data: self.stdscr.addstr(2,0,"data: " + data)
    self.stdscr.move(4,9)
    self.stdscr.refresh()
    
        
  def main(self):
    self.client = vpd_core.Client()
    self.client.log = self.logger
    try:
      self.client.connect(host="localhost", port=50001)
    except socket.gaierror, error:
      self.client.close()
      sys.exit(error[1])
      
    t = Thread(target=vpd_core.loop)
    t.setDaemon(True)
    t.start()
    if not self.client.connected:
        print "Trying to connect..."
        attempts = 5
    while not self.client.connected and attempts:
        time.sleep(0.5)
        attempts -= 1
    try:
        # Check for connectivity by sending a blank string
        # (the Server won't respond to it anyway)
        self.client.send("")
    except socket.error, msg:
        sys.exit(msg[1])

    if True: #run curses
      self.init_ui(self.client.getpeername())
      # Just a string of spaces
      spaces = "         ".join(["         " for x in range(10)])
      
      while True:
        self.stdscr.addstr(4, 0, "".join(['Command: ', spaces]))
        try:
            cmd = self.stdscr.getstr(4, 9, vpd_core.MAX_CMD_LEN)
        except KeyboardInterrupt:
            cmd = ""
        if cmd == "q" or cmd == "quit": break
        
        try:
          if not self.client.send_command(cmd):
             break
          self.client.log("")
        except socket.error, msg:
            break

      self.end_ui()

      self.client.close()

      try:
          print >> sys.stderr, msg
      except NameError:
          pass
        
    else: # run without curses
      def logtemp(data):     print "log: " + data
      self.client.log = logTemp
      
      self.client.log("test output")
      self.client.send_command("test 1")
      vpd_core.loop()  
      self.client.send_command("test 2")
      vpd_core.loop()  
      self.client.close()
        
  
if __name__ == "__main__":
    v = vpdCmder()
    v.main()  