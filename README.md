# Geolocator

Simple HTTP server that takes an address input and returns latitude and longitude from 1 or more configured geolocation services.

Start the server: `python px-geoloc.py` (will bind to localhost:8081)

Use the service:

	curl localhost:8081?address=425+Market+St+%238%2C+San+Francisco%2C+CA+94105 # or
	curl localhost:8081 -d"address=425 Market St #8, San Francisco, CA 94105" # returns
	
	{"status": "success", "lat": 37.79141, "lng": -122.39831, "address": "425 Market St #8, San Francisco, CA 94105"}

## Running Server

To change host/port/config, run

	python px-geoloc.py [host=hostname] [port=portnum] [conf=config.json]

### Config File Structure

Base configuration:

	{"servers": [ SERVER_CONFIG* ]}

The order of the servers determines the precedence of service. Each server configuration is an object with the following 4 keys:

- `url`: The full URL of the service, with the address parameter encoded as `${address}`.
- `root`: The root object location of latitude and longitude. Separate each level with a comma
-- e.g. `top,key` on `{"top": {"key": {"k1":1, "k2":2}}}` would resolve to `{"k1":1, "k2":2}`
- `lat`, `lng`: The latitude and longtitude keys object resolved by `root`

Currently, only services that return JSON are supported.

`config.json` is pre-populated with MapQuest, Google, and HERE geocoding services -- simply put in your API info to get started.

## Using Geolocator

**Endpoint**

	GET /?address=ADDRESS HTTP/1.1

**Results**

Successful response:

	HTTP/1.1 200
	Content-Length: SZ
	Content-Type: application/json
	
	{"status": "success", "lat": 0.0, "lng": 1.1, "address": "ADDRESS"}


Failed response:

	HTTP/1.1 200
	Content-Length: SZ
	Content-Type: application/json
	
	{"status": "error", "message": "could not resolve address", "address": "ADDRESS"}