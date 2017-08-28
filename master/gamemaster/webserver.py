import SimpleHTTPServer
import SocketServer
import logging
import cgi
import random
import sys

PORT = 8080

game_instance = None

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def serve_main_page(self, post):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()


		state = self.server.state
		md = self.server.module_descriptions

		print(state)
		if state is None:
			d = {"countdown": "--", "lifes": "--"}
		else:
			d = {"countdown": state["seconds"], "lifes": state["lifes"]}
			#{'seconds': 297, 'lifes': 1, 'modules': {'b': {'failures': 0, 'state': 0}, 'd': {'failures': 0, 'state': 5}}}
		
		module_template = """<tr><td>{name}</td><td>{rev}</td><td><input type="checkbox" name="enable_{name}"{checked}/></td><td>{state}</td><td>{fail}</td></tr>\n"""
		d["module_list"] = ""
		for mname, m in md.iteritems():
			checked = """ checked="checked" """ if "enable_"+mname in post else ""
			if state is None:
				st = ""
				fail = "-"
			else:
				style = "check" if state["modules"][mname]["state"] == 1 else "alert"
				st = """<a href="#" class="ui-btn ui-corner-all ui-icon-{} ui-btn-icon-notext">Action Icon</a>""".format(style)
				fail = state["modules"][mname]["failures"]
			d["module_list"] += module_template.format(name=mname, rev=m["revision"], checked=checked, state=st, fail=fail)

		with open("webserver.html", "r") as f:
			self.wfile.write(f.read().format(**d))

	def do_GET(self):
		self.serve_main_page({})

	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile,
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
				'CONTENT_TYPE':self.headers['Content-Type'],
				})
		d = {item.name: item.value for item in form.list}
		self.handle_post(d)
		self.serve_main_page(d)
	
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
	httpd = WebServer(("", PORT), ServerHandler)
	httpd.state = {"countdown": "0", "lives": "1"}

	while True:
		httpd.handle_request()
