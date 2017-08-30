import SimpleHTTPServer
import SocketServer
import logging
import cgi
import random
import sys
import json

PORT = 8080

game_instance = None

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def make_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def serve_main_page(self, post):
		with open("webserver.html", "r") as f:
			self.wfile.write(f.read() % 
				(", ".join('"{}"'.format(m) for m in self.server.module_descriptions))
				)

	def do_GET(self):
		self.make_headers()
		if self.path == "/status":
			state = self.server.state
			if state is None:
				result = {"seconds": -1, "lifes": -1}
				result["modules"] = {m: {"failures": 0, "state": 5} for m in self.server.module_descriptions}
			else:
				result = {
					"seconds": state["seconds"],
					"lifes": state["lifes"],
				}
				result["modules"] = {m: {"failures": state["modules"][m]["failures"], "state": state["modules"][m]["state"]} for m in self.server.module_descriptions}
			self.wfile.write(json.dumps(result))
		else:
			self.serve_main_page({})

	def do_POST(self):
		self.make_headers()
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
				'CONTENT_TYPE':self.headers['Content-Type'],
				})
		params = {item.name: item.value for item in form.list}

		try:
			handler = {
				"/start": self.handle_start,
				"/abort": self.handle_abort,
			}[self.path]
		except KeyError:
			print("unknown path: {}".format(self.path))
			return

		handler(params)

		#self.serve_main_page(d)
	
	def handle_start(self, params):
		md = self.server.module_descriptions
		self.server.last_message = {"start":{
			"seconds": int(params["seconds"]),
			"maxerrors": int(params["maxerrors"]),
			"serial": params["serial"],
			"modules": {m: {"enabled": ("enable_"+m) in params and params["enable_"+m]=="on", "random":[random.randrange(0,256) for i in range(md[m]["num_random"])]} for m in md}
		}}
		self.wfile.write("")
	
	def handle_abort(self, params):
		self.server.last_message = {"abort": {}}

	
	def handle_post(self, d):
		for name, value in d.iteritems():
			print("{}={}".format(name, value))

		md = self.server.module_descriptions

		try:
			if d["btn"] == "start":
				print("sending start")
				self.server.last_message = {"start":{
					"seconds": int(d["new_countdown"]),
					"maxerrors": int(d["new_maxerrors"]),
					"serial": d["serial"],
					"modules": {m: {"enabled": ("enable_"+m) in d and d["enable_"+m]=="on", "random":[random.randrange(0,256) for i in range(md[m]["num_random"])]} for m in md}
				}}
			elif d["btn"] == "abort":
				print("sending abort")
				self.server.last_message = {"abort":{
				}}
		except Exception as e:
			print("error:")
			print(e)

class WebServer(SocketServer.TCPServer):
	allow_reuse_address = True


	def __init__(self, interface, module_descriptions):
		SocketServer.TCPServer.__init__(self, interface, ServerHandler)
		self.module_descriptions = module_descriptions
		self.state = None
		self.last_message = None
		self.timeout = 0.1

	def send_game_update(self, state):
		self.state = state
	
	def send_game_end(self, reason):
		self.state = None
	
	def _PopMessage(self):
		lm = self.last_message
		self.last_message = None
		return lm
	
	def _CheckForMessage(self):
		self.handle_request()
		return self.last_message is not None

if __name__ == "__main__":
	httpd = WebServer(("0.0.0.0", PORT), ServerHandler)
	httpd.state = {"countdown": "0", "lives": "1"}

	while True:
		httpd.handle_request()
