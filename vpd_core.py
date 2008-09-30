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

"""

Constants:

PORT -- default port used by Client and Server
MAX_CMD_LEN -- maximum length of a command

"""

import time
import socket
import asyncore
import select
import asynchat
import os
from subprocess import Popen, PIPE
from threading import Thread

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode


__version__ = '0.0.1'
__author__ = 'Andy Lumb <andy.lumb@gmail.com>'

PORT = 50001
MAX_CMD_LEN = 256

# added error handeling
def loop(log=None, timeout=30.0, use_poll=False, map=None, count=None): 
  flag = True
  while flag:
    try:
      asyncore.loop(timeout, use_poll, map, count)
    except select.error:
      flag = False
      for fileID in map.copy():
        try:
          os.fstat(fileID)
        except OSError:
          del map[fileID]
          if log: log("FILE ERROR: removed fileID: " + str(fileID))
          flag = True
    except socket.error, errstr:
      if log: log("Error: " + str(errstr))
      else: print "Error: " + str(errstr)
      break
    if log: log("Loping after File Removed")
    else: print "Loping after File Removed"
        

class Server(asyncore.dispatcher):
    """Server(host='', port=pymplayer.PORT, max_conn=1)
    """

    def __init__(self, host='', port=PORT, max_conn=1):
        # Use own socket map
        self._map = {}
        # TODO: remove reference to self in self._map to avoid circular reference.
        # Probably move the socket map out of self?
        asyncore.dispatcher.__init__(self, map=self._map)
        self.max_conn = max_conn
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(self.max_conn)
        self.mplayer = {}

    @staticmethod
    def writable():
        return False

    def handle_close(self):
        self.log("Server closed.")
        self.close()

    def handle_accept(self):
        conn, addr = self.accept()
        self.log("Connection accepted: %s" % (addr, ))
        # Dispatch connection to a _ClientHandler
        _ClientHandler(conn, self._map, self.log, self.mplayer)
            
    def start(self, timeout=30.0, use_poll=False):
        """Start the server.

        @param timeout=30.0: timeout parameter for select() or poll()
        @param use_poll=False: use poll() instead of select()

        Starts the MPlayer process, then calls asyncore.loop (blocking)

        """
        self.log("Server started.")
        loop(timeout=timeout, use_poll=use_poll, map=self._map, log=self.log)
            
    def stop(self):
        """Stop the server.

        Closes all the channels found in self._map (including itself)

        """
        for name in self.mplayer:
          self.mplayer[name].stop()
        for channel in self._map.values():
            channel.handle_close()
        self._map.clear()

class MyMplayer:

  def __init__(self, map, log, client):
    self._process = None
    self._stdout = 0
    self._stderr = 0
    self._map = map
    self.log = log
    self.client = client # this is a _ClientHandler can be Nothing
    #list of available commands is here:         http://www.mplayerhq.hu/DOCS/tech/slave.txt
    self.cmds = { 
      'play':self.play,
      'stop':self.stop,
      'pause':self.pause,
      'mpcmd':self.mplayer_command
    }

  def play(self, cmdArgs):
    self.log("playing: " + cmdArgs)
    if self.isalive(): self.stop()
    args = ['mplayer', '-slave', '-quiet', '-nortc', '-fs', '-nojoystick', '-nolirc', '-vo', 'xv,x11,', cmdArgs]
    #
    try:
      # Start the MPlayer process (line-buffered)
      self._process = Popen(args=args, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
    except OSError:
      return "OSError: play " + cmdArgs
    else:
      self._stdout = self._process.stdout.fileno()
      _ReadableFile(self._map, self._process.stdout, self.mplayer_data)
      self._stderr = self._process.stderr.fileno()
      _ReadableFile(self._map, self._process.stderr, self.mplayer_error)
      
      return "Playing: " + cmdArgs
      
  def pause(self, cmdArgs): self.command("pause")    
      
  def stop(self, cmdArgs=""):
    self.log("stopping")
    if self.isalive():
      self.mplayer_command("quit")
    if self._stdout in self._map: del self._map[self._stdout]; self._stdout = 0
    if self._stderr in self._map: del self._map[self._stderr]; self._stderr = 0
      
  def mplayer_data(self):
    data = self._process.stdout.readline().rstrip()
    if data:
      self.log(data)
      if data.startswith("Exiting..."): self.stop("")
          
  def mplayer_error(self):
    error = self._process.stderr.readline().rstrip()
    if error:
        self.log("Error: " + error)
        if self.client: self.client.tellClient("Error: "+ error)        

  def mplayer_command(self, cmd):
    if not isinstance(cmd, basestring):
      raise TypeError("command must be a string")
    if self.isalive() and cmd:
      self._process.stdin.write("".join([cmd, '\n']))  
        
  def command(self, cmd):
    cmdArr = cmd.split()
    try:
      fn = self.cmds[cmdArr[0]] 
      returnVal = fn(" ".join(cmdArr[1:]))
      if returnVal: 
        if self.client: self.client.tellClient(returnVal)
        self.log("returned: "+ returnVal)
    except KeyError:
      if self.client: self.client.tellClient("command not found: " + cmd )
      self.log("command not found: " + cmd)
  
  def isalive(self):
    try:
        return (self._process.poll() is None)
    except AttributeError:
        return False  
        
class _ClientHandler(asynchat.async_chat):
    """Handler for Client connections"""

    ac_in_buffer_size = MAX_CMD_LEN
    ac_out_buffer_size = 512
    
    def __init__(self, conn, map, log, mplayer):
        asynchat.async_chat.__init__(self, conn)
        # We're using a custom map so remove self from asyncore.socket_map.
        asyncore.socket_map.pop(self._fileno)
        self._map = map
        self.add_channel()
        self.log = log
        self.buffer = []
        self.set_terminator("\r\n\r\n")
  
        #everyone is local right now...
        self.mplayerName = 'local'
        #either create the mplayer instance by this name if it doesn't exist
        if self.mplayerName not in mplayer: mplayer[self.mplayerName] = MyMplayer(self._map, self.log, self)
        else: mplayer[self.mplayerName].client = self
        self.mplayer = mplayer[self.mplayerName]

    def handle_data(self, data):
        if data.startswith('ANS_'):
            self.tellClient(data)

    def tellClient(self, data) :
      self.log("telling client: " + data)
      try: 
        self.push("".join([data, "\r\n"]))
      except:
        self.log("Lost Client, Trieded to send: " + data)
                
    def handle_close(self):
        self.close()
        self.mplayer.client = None
        self.log("Connection closed: %s" % (self.addr, ))

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        cmd = "".join(self.buffer)
        self.buffer = []
        if not cmd: return
        self.mplayer.command(cmd)
              
   
class _ReadableFile(object):
    """Imitates a readable asyncore.dispatcher class.

    This class serves as a wrapper for stdout and stderr
    so that the polling function of asyncore can check them
    for any pending I/O events. The polling function will
    call the handle_read_event method as soon as there is data
    to read.

    """

    def __init__(self, map_, file, handler):
        # Add self to map
        map_[file.fileno()] = self
        self.handle_read_event = handler

    def __getattr__(self, attr):
        # Always return a callable for non-existent attributes and
        # methods in order to 'fool' asyncore's polling function.
        # (IMO, this is a better approach than defining all
        #  the other asyncore.dispatcher methods)
        return lambda: None

    @staticmethod
    def readable():
        return True

    @staticmethod
    def writable():
        return False
   
class Client(asynchat.async_chat):
    """Client()

    The PyMPlayer Client

    """

    ac_in_buffer_size = 512
    ac_out_buffer_size = MAX_CMD_LEN

    def __init__(self):
        asynchat.async_chat.__init__(self)
        self.buffer = []
        self.set_terminator("\r\n")

    @staticmethod
    def handle_connect():
        return

    def handle_error(self):
        self.close()
        self.connected = False
        raise socket.error("Connection lost.")

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def found_terminator(self):
        data = "".join(self.buffer)
        self.buffer = []
        self.handle_data(data)

    def handle_data(self, data):
        self.log(data)

    def connect(self, host, port=PORT):
        """Connect to a pymplayer.Server

        @param host: host to connect to
        @param port: port to use

        pymplayer.loop should be called (if not called previously)
        after calling this method.

        """
        if self.connected:
            return
        if self.socket:
            self.close()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        asynchat.async_chat.connect(self, (host, port))
        

    def send_command(self, cmd):
        """Send an MPlayer command to the server

        @param cmd: valid  command
        """
        self.push("".join([cmd, "\r\n\r\n"]))
        return True          
          
        
