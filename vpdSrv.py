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


import sys
import socket
import signal
import logging
try:
    from vpd_core import Server
except ImportError, msg:
    sys.exit(msg)


def main():
    log = logging.getLogger('vpd.server');
    console = logging.StreamHandler(sys.stdout)
    log.setLevel(logging.INFO)
    # tell the handler to use this format
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
    # add the handler to the root logger
    log.addHandler(console)
    logging.getLogger('vpd.Mplayer').addHandler(console)
    try:
        server = Server(port=50001, max_conn=2)
    except socket.error, msg:
        sys.exit(msg)
    server.args = sys.argv[1:]
    signal.signal(signal.SIGTERM, lambda s, f: server.stop())

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
