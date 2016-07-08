from connection import Connection

class Server(Connection):
	def __init__(self, targetHostname, module_descriptions):
		Connection.__init__(self, targetHostname)
		self.module_descriptions = module_descriptions

	def _OnConnect(self):
		self._SendJson({"capabilities":
			{
				"modules": self.module_descriptions
			}})

	def send_game_update(self, state):
		self._SendJson({"state": state})

	def send_game_end(self, reason):
		self._SendJson({"end": {"reason": reason}})

