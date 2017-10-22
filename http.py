import re
import urlparse

# Lightweight HTTP wrapper to interact with a raw socket. Assumes well-formed request.
# @todo there's some oddity with chunked transfer--the initial byte length of the first chunk never seems to make it back to client
class Http:
	LINE_SPLIT = "\r\n"
	LINE2 = "\r\n\r\n"

	def __init__(self, sock):
		self.sock = sock
		self.headers_in = {'Method': 'GET', 'Path': '/', 'Querystring': '', 'Protocol': 'HTTP/1.1'}
		self.headers_out = {}
		self.status = 200
		self.qs_params = {}
		self.body = ''
		self.commit = False
		self.limit = -1
		self.committed = 0

	# Parses request headers and querystring parameters.
	def do_recv(self):
		# build
		header_buff = []
		chunks = ''
		body = ''
		br = 0
		stop = False

		# collect all headers until LINE2 encountered or empty chunk
		while stop == False:
			chunk = self.sock.recv(512)
			chunks += chunk
			if re.search(Http.LINE2, chunks) or chunk == '':
				stop = True
				break

		head_body = re.split(Http.LINE2, chunks, 1)
		lines = re.split(Http.LINE_SPLIT, head_body[0])
		body = head_body[1]

		# set headers
		hinit = False
		for line in lines:
			# First line of headers, parse out method, path, protocol
			if hinit == False:
				hinit = True
				method, url, proto = line.split(' ', 2)
				urlparts = url.split('?', 1)
				url = urlparts[0]
				qstring = ''

				if len(urlparts) == 2:
					qstring = urlparts[1]

				self.headers_in['Method'] = method
				self.headers_in['Path'] = url
				self.headers_in['Querystring'] = qstring
				self.headers_in['Protocol'] = proto
			else:
				kv = re.split(":\s*", line, 1)
				if len(kv) == 2:
					self.headers_in[kv[0]] = kv[1]

		if self.headers_in['Querystring'] != '':
			self.qs_params = urlparse.parse_qs(self.headers_in['Querystring'], True)

		# @todo process rest of body?
		self.body = body

	@property
	def request_headers(self):
		return self.headers_in

	# Headers to send back to client.
	@property
	def response_headers(self):
		return self.headers_out

	@property
	def params(self):
		return self.qs_params

	# Set status for response.
	def set_status(self, status):
		self.status = status

	# Sends output to client. If this is the first call, headers will be outputted first.
	# Also, if 'Content-Length' is not present or less than 0, assumes chunked transfer.
	def do_send(self, msg = None):
		buff = ""
		if self.commit == False:
			self.commit = True
			self.sock.send("HTTP/1.1 %s\r\n" % (self.status))
			for k, v in self.headers_out.iteritems():
				buff += "%s: %s\r\n" % (k, v)
			if 'Content-Length' in self.headers_out:
				self.limit = int(self.headers_out['Content-Length'])
			if self.limit == -1:
				buff += "Transfer-Encoding: chunked\r\n"
			buff += "\r\n"

		self.raw_send(buff)

		if msg:
			buff = ''
			if self.limit > -1:
				if self.committed < self.limit:
					ds = self.limit - self.committed
					sz = len(msg)
					if sz < ds:
						ds = sz
					buff = msg[0:ds]
			else:
				#print "do_send(%s, %s)" % (len(msg), msg)
				buff = "%s\r\n%s\r\n" % (len(msg), msg)

			self.raw_send(buff)

	# If doing chunked encoding, send terminating chunk
	def do_send_final(self):
		if self.limit == -1:
			self.raw_send("0\r\n\r\n")

	# Sends bytes to connection, making sure to check actual bytes transferred and returning when complete.
	def raw_send(self, msg):
		print "raw_send: %s" %msg
		s0 = 0
		s1 = len(msg)
		while s0 < s1:
			s0 += self.sock.send(msg[s0:s1])

class TestSock:
	def __init__(self):
		print "dsock init"

	def recv(self, sz):
		return "GET / HTTP/1.1\nHost: localhost:8081?x=y&z=0\r\nUser-Agent: curl/7.55.1\r\nAccept: */*\r\nHey: you!\r\nGet: off my\r\nLawn: !!!!!\r\n\r\nQuck"

	def send(self, msg):
		print "send(): ", msg

# http = Http(TestSock())
# http.do_recv()
# print http.request_headers()
# print http.params()