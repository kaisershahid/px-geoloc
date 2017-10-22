# Postmates X Geolocator

Simple HTTP server that takes an address input and returns latitude and longitude from 1 or more configured geolocation services.

## Running Server

Run
	python px-geoloc.py

to start the server on `localhost:8081` and using `config.json`. To change host/port/config, run

	python px-geoloc.py [host=hostname] [port=portnum] [conf=config.json]

### Config File Structure

Each server configuration is an object with the following 4 keys:

- `url`: The full URL of the service, with the address parameter encoded as `${address}`.
- `root`: The root object location of latitude and longitude. Separate each level with a comma
-- e.g. `top,key` on `{"top": {"key": {"k1":1, "k2":2}}}` would resolve to `{"k1":1, "k2":2}`
- `lat`, `lng`: The latitude and longtitude keys object resolved by `root`

Currently, only services that return JSON are supported.

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