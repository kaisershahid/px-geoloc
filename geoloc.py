import urllib
import urllib2
import json
import re
import sys

# Pings set of geolocation services, stopping after first successful response
class Geoloc:
	def __init__(self, servers):
		self.servers = servers
	
	def lookup(self, address):
		addr = urllib.quote_plus(address)
		lat = None
		lng = None

		for server in self.servers:
			url = re.sub("\$\{address\}", addr, server['url'])
			try:
				rsp = urllib2.urlopen(url)
				if rsp.getcode() == 200:
					data = json.loads(rsp.read())
					ptr = data

					for key in server['root']:
						if (isinstance(ptr, list) and isinstance(key, int) and key < len(ptr)) or (key in ptr):
							ptr = ptr[key]
						else:
							ptr = None
							break

					if ptr:
						lat = ptr[server['lat']]
						lng = ptr[server['lng']]
			except urllib2.HTTPError:
				print "XX http error fetching %s: %s" % (url, str(sys.exc_info()[1]))
					
			if lat:
				break

		if lat:
			return {'status': 'success', 'lat': lat, 'lng': lng}
		else:
			return {'status': 'error', 'message': 'could not resolve address'}
