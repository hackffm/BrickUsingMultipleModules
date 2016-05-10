import serial
import random

BROADCAST_ADDRESS = "_"

MODULE_EXISTS = "a"
MODULE_INIT = "b"
GAME_START = "c"
STATUS_POLL = "d"
STATUS_BROADCAST = "e"

class BusException(RuntimeError):
	def __init__(self, text):
		self.text = text

class Bus(object):
	##
	# usage: Bus(serial_device) for a preexisting serial device or Bus(name_of_serial_device, baudrate) to create a new one
	def __init__(self, device, baudrate=None):
		if baudrate is None:
			self.serial = device
		else:
			self.serial = serial.Serial(device, baudrate, timeout=0.1)

	def _write(self, buf):
		self.serial.write(bytes(buf+"\n", "utf8"))
		self.serial.flush()

	def _readline(self):
		result = self.serial.readline().decode()
		if len(result) > 0 and result[-1] == "\n":
			result = result[:-1]
		return result

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
			raise BusException("{} cannot be parsed into {} bytes!".format(value, expected_len))

		pos = 0
		result = {}
		for p in parameters:
			result[p[0]] = int(value[pos : pos+2*p[1]], base=16)
			pos += 2*p[1]
		return result

	## checks whether the module with the given id is connected to the bus
	# \param module_id single-character module id
	# \returns revision_id (0-255) if present, None otherwise
	def check_for_module(self, module_id):
		Bus._check_module_id(module_id)

		result = self._request(module_id + MODULE_EXISTS)
		if len(result) == 0:
			return None
		return Bus._pick_from_hex(result, [("revision", 1)])["revision"]

	## Initialises module for new game
	# \param module_id single-character module id
	# \param enabled boolean value which determines whether this module will take part in this game
	# \param difficulty value from 0-255 (0 being easiest)
	def init_module(self, module_id, enabled, difficulty):
		Bus._check_module_id(module_id)
		assert enabled in [True, False]
		assert isinstance(difficulty, int)
		assert 0 <= difficulty <= 255

		mode = 1 if enabled else 0
		random_number = random.randrange(0, 65536)

		self._write(module_id + MODULE_INIT + Bus._to_hex(mode, 1) + Bus._to_hex(difficulty, 1) + Bus._to_hex(random_number, 2))

	## Actually start the game
	def start_game(self):
		self._write(BROADCAST_ADDRESS + GAME_START)

	## Poll module status
	# \param module_id single-character module id
	# \returns tuple (success (boolean), number of failures)
	def poll_status(self, module_id):
		Bus._check_module_id(module_id)
		response = self._request(module_id + STATUS_POLL)
		result = Bus._pick_from_hex(response, [
			("success", 1),
			("failures", 1)
			])

		return (result["success"] != 0, result["failures"])

	## Broadcast the current game state
	# \param remaining_seconds of the countdown
	# \param num_failures number of failures occurred so far
	def broadcast_status(self, remaining_seconds, num_failures):
		self._write(BROADCAST_ADDRESS + STATUS_BROADCAST + Bus._to_hex(remaining_seconds, 2) + Bus._to_hex(num_failures, 1))