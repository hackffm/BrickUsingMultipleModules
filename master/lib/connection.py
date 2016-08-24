import socket
import json
import sys

PORT_NUMBER = 5000

def byteify(val):
	if isinstance(val, dict):
		return {byteify(key): byteify(value) for key, value in (val.items() if sys.version_info.major == 3 else val.iteritems())}
	elif isinstance(val, list):
		return [byteify(element) for element in val]
	elif sys.version_info.major == 2 and isinstance(val, unicode):
		return val.encode('utf-8')
	else:
		return val

class Connection(object):
	## Time to try to establish a new connection
	CONNECTION_TIMEOUT = 0.1

	## Initialises state and sends player information to display.
	# \param targetHostname IP of server to connect to. Use empty string to use server-mode
	def __init__(self, targetHostname):
		self.state = "init"

		self.buffer = ""

		self.server = None
		self.connection = None
		self.targetHostname = targetHostname
		self.port = PORT_NUMBER

		#self._TryConnect()
	
	def _CleanupConnections(self):
		print("disconnect!")
		self.server = None
		self.connection = None

	## Try to connect to remote host.
	# If connection succeeds, internal state is updated accordingly.
	def _TryConnect(self):
		# server mode
		if self.targetHostname is "":
			# if server is not already running, start it
			if self.server is None:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # avoid port block on server failure
				print("server mode: waiting for connection...")
				try:
					s.bind(("", self.port))
				except socket.error: # address already in use?
					if self.port == PORT_NUMBER+10:
						self.port = PORT_NUMBER
					else:
						self.port += 1
				s.listen(1)
				s.settimeout(Connection.CONNECTION_TIMEOUT)
				self.server = s

			# check for new connections on server
			try:
				conn, addr = self.server.accept()
				print("connection from {}".format(addr))
				self.connection = conn
				self.connection.setblocking(0) # non-blocking mode
				self._OnConnect()
			except socket.timeout:
				print("timeout - using port {}".format(self.port))

		# client mode
		else:
			print("connecting to {}...".format(self.targetHostname))
			for port_increment in range(10):
				try:
					s = socket.create_connection((self.targetHostname, PORT_NUMBER+port_increment), Connection.CONNECTION_TIMEOUT)
					self.connection = s
					print("connected")
					self.connection.setblocking(0) # non-blocking mode
					self._OnConnect()
					break
				except socket.timeout:
					print("timeout")
				except ConnectionRefusedError:
					print("refused - using port {}".format(PORT_NUMBER+port_increment))
	
	## Reads buffer until empty or \0
	# \returns True if new message complete available, else False
	# use popMessage to retrieve the message
	def _CheckForMessage(self):
		if self.connection is None:
			self._TryConnect()
			return False
		if len(self.buffer) > 0 and self.buffer[-1] == "\0": # already a message in the buffer
			return True
		try:
			while(True):
				#print(self.connection.gettimeout())
				buf = self.connection.recv(1)
				if len(buf) == 0: # this will only occur on disconnects. if no data is available, a socket.error will be raised and handled below!
					self._CleanupConnections()
					return False
				self.buffer += buf.decode("utf-8") if sys.version_info.major == 3 else buf
				if len(self.buffer) > 0 and self.buffer[-1] == "\0":
					return True
		except socket.error: # no data available
			return False

	## Return currently buffered message and clear the buffer
	def _PopMessage(self):
		j = byteify(json.loads(self.buffer[:-1]))
		self.buffer = ""
		print("got message: {}".format(j))
		return j

	## Internal helper function
	def _SendJson(self, data):
		if self.connection is None:
			self._TryConnect()
		else:
			j = json.dumps(data)+"\0"
			print(j)
			try:
				self.connection.send(j.encode("utf-8") if sys.version_info.major == 3 else j)
				print("sent message: {}".format(j))
			except socket.error:
				self._CleanupConnections()
	
	## Check whether connection is active
	# \returns True on connection failure, False otherwise
	def IsInErrorState(self):
		return self.connection is None

	def _OnConnect(self):
		pass
