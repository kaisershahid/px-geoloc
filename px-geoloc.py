# python px-geoloc.py [host=localhost] [port=8080] [config=geoservers.json]
import socket
import json
import io
import os
import re
import sys

import http
import geoloc

host = 'localhost'
port = 8081
fileconf = 'config.json'

for i in range(1, len(sys.argv)):
	kv = sys.argv[i].split('=', 1)
	if len(kv) > 1:
		if kv[0] == 'host':
			host = kv[1]
		elif kv[0] == 'port':
			port = int(kv[1])
		elif kv[0] == 'config':
			fileconf = kv[1]

print "-> loading '%s'" % fileconf

cfg = None
if os.path.isfile(fileconf):
	f = io.open(fileconf)
	cfg = json.loads(f.read())
	f.close()
	if 'servers' in cfg:
		# expand the root keys to access lat/long of json response from geocoder. assume numeric string is number.
		# see README.md for more information.
		for sinf in cfg['servers']:
			print "-> server config for %s" % sinf['url']
			root = sinf['root'].split(',')
			i = 0
			for rkey in root:
				if re.match('^\d+$', rkey):
					root[i] = int(rkey)
				i += 1
			sinf['root'] = root
else:
	print "!! WARNING: '%s' found" % fileconf
	cfg = {'servers': []}

locator = geoloc.Geoloc(cfg['servers'])

print "-> binding to %s:%s" % (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))
sock.listen(10)
print "-> done. waiting!"

try:
	while 1:
		(conn, addr) = sock.accept()
		s = http.Http(conn)
		print "<< conn = ", conn, ", addr = ", addr

		s.do_recv()
		results = {}
		address = None
		if 'address' in s.params:
			address = s.params['address'][0]

		if address == '' or address == None:
			results['status'] = 'error'
			results['message'] = 'address not supplied'
		else:
			results = locator.lookup(address)

		results['address'] = address
		js = json.dumps(results)
		s.response_headers['Content-Type'] = 'application/json'
		s.response_headers['Content-Length'] = len(js)
		s.do_send(js)

		conn.shutdown(socket.SHUT_RDWR)
		conn.close()
except KeyboardInterrupt:
	sock.close()
	print "exiting..."