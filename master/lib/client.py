from connection import Connection

class Client(Connection):
	def __init__(self, targetHostname):
		Connection.__init__(self, targetHostname)

	def send_abort(self):
		self._SendJson({"abort": None})

	def send_start(self, info):
		self._SendJson({"start": info})
