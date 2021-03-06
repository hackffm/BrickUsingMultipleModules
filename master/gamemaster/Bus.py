import serial
import random


BROADCAST_ADDRESS = "_"
CONTROL_MODULE = "!"
RESPONSE_ADDRESS = "="

MODULE_EXISTS = "a"
MODULE_INIT = "b"
GAME_START = "c"
STATUS_POLL = "d"
STATUS_BROADCAST = "e"
GAME_END = "f"

class BusException(RuntimeError):
	def __init__(self, text):
		self.text = text
	def __str__(self):
		return "BusException: " + self.text

def retryOnBusException(func):
	def f(*args, **kwargs):
		while True:
			try:
				return func(*args, **kwargs)
			except BusException as e:
				print("Caught BusException: {}".format(e))
				print("retrying...")
	return f

class Bus(object):
	##
	# usage: Bus(serial_device) for a preexisting serial device or Bus(name_of_serial_device, baudrate) to create a new one
	def __init__(self, device, baudrate=None, debug=False):
		if baudrate is None:
			self.serial = device
		else:
			self.serial = serial.Serial(device, baudrate, timeout=0.1)
		self.debug = debug

	def _write(self, buf):
		if self.debug:
			print(">"+buf)
		self.serial.write(buf+"\n")
		self.serial.flush()

	def _readline(self):
		result = self.serial.readline()
		if len(result) > 0:
			if result[-1] == "\n":
				result = result[:-1]
			if len(result) > 0:
				if result[0] != RESPONSE_ADDRESS: # expected return code
					raise BusException("got response with wrong target ID: '{}' (expected '{}')".format(result[0], RESPONSE_ADDRESS))
			result = result[1:]
		if self.debug:
			print("<"+result)
		return result

	## Drain input buffer (read input until none is left)
	def drain(self):
		while(True):
			if len(self.serial.readline()) == 0:
				break

	def _request(self, buf):
		self._write(buf)
		return self._readline()

	@staticmethod
	def _check_module_id(module_id):
		assert len(module_id) == 1


	## converts int to hex value
	# \param value The integer value to convert
	# \param length number of bytes to use. Value has to fit into length bytes
	@staticmethod
	def _to_hex(value, length):
		assert isinstance(value, int)
		result = hex(value)[2:].upper()
		assert len(result) <= 2*length # value would violate protocol specification
		return "0" * (2*length-len(result)) + result # pad with zeroes

	## Parses and spilts hex string
	# \param value the value to parse
	# \param parameters list of tuples with parameter name and length
	@staticmethod
	def _pick_from_hex(value, parameters):
		assert isinstance(value, str)
		assert isinstance(parameters, list)
		for p in parameters:
			assert isinstance(p, tuple)
			assert len(p) == 2
			assert isinstance(p[0], str)
			assert isinstance(p[1], int)

		expected_len = sum((p[1] for p in parameters))
		if expected_len*2 != len(value):
			raise BusException("'{}' cannot be parsed into {} bytes!".format(value, expected_len))

		pos = 0
		result = {}
		for p in parameters:
			result[p[0]] = int(value[pos : pos+2*p[1]], base=16)
			pos += 2*p[1]
		return result

	## checks whether the module with the given id is connected to the bus
	# \param module_id single-character module id
	# \returns dict(revision, num_random) if present, None otherwise
	def check_for_module(self, module_id):
		Bus._check_module_id(module_id)

		result = self._request(module_id + MODULE_EXISTS)
		if len(result) == 0:
			return None
		return Bus._pick_from_hex(result, [("revision", 1), ("num_random",1)])

	## Initialises module for new game
	# \param module_id single-character module id
	# \param enabled boolean value which determines whether this module will take part in this game
	# \param serial_number 5-char string of bumm serial number
	# \param num_random number of random bytes or list of 1-byte integers
	def init_module(self, module_id, enabled, serial_number, num_random):
		Bus._check_module_id(module_id)
		assert enabled in [True, False]
		assert isinstance(serial_number, str)
		assert len(serial_number) == 5
		assert "1" <= serial_number[0] <= "9"
		assert "0" <= serial_number[1] <= "9"
		assert "0" <= serial_number[2] <= "9"
		assert "0" <= serial_number[3] <= "9"
		assert "A" <= serial_number[4] <= "Z"

		if isinstance(num_random, int):
			random_number = (random.randrange(0, 256) for i in range(num_random))
		elif isinstance(num_random, list):
			for i in num_random:
				assert isinstance(i, int)
				assert 0 <= i < 256
			random_number = num_random
		else:
			raise AssertionError("num_random neither of type int or list")

		mode = 1 if enabled else 0
		random_number = "".join(Bus._to_hex(i, 1) for i in random_number)
		serial_number_encoded = "".join(Bus._to_hex(ord(s), 1) for s in serial_number)

		self._write(module_id + MODULE_INIT + Bus._to_hex(mode, 1) + serial_number_encoded + random_number)

	## Actually start the game
	def start_game(self, module_id):
		Bus._check_module_id(module_id)
		self._write(module_id + GAME_START)

	## Poll module status
	# \param module_id single-character module id
	# \returns tuple (success (boolean), number of failures)
	@retryOnBusException
	def poll_status(self, module_id):
		Bus._check_module_id(module_id)
		response = self._request(module_id + STATUS_POLL)
		result = Bus._pick_from_hex(response, [
			("success", 1),
			("failures", 1)
			])

		return (result["success"], result["failures"])

	## Broadcast the current game state
	# \param remaining_seconds of the countdown
	# \param num_lifes number of lifes left
	def broadcast_status(self, remaining_seconds, num_lifes):
		self._write(BROADCAST_ADDRESS + STATUS_BROADCAST + Bus._to_hex(remaining_seconds, 2) + Bus._to_hex(num_lifes, 1))
	
	## Game finished (bomb exploded or was successfully defused)
	# \param result 0 if defused, 1 if countdown reached, 2 if too many failures
	def end_game(self, result):
		assert result in [0,1,2,3]
		self._write(BROADCAST_ADDRESS + GAME_END + Bus._to_hex(result, 1))
