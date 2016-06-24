import unittest
from Bus import Bus, BusException, RESPONSE_ADDRESS

class FakeSerial(object):
	def __init__(self, responses=None):
		self.responses = {} if responses is None else responses
		self.sendbuf = ""
		self.recvbuf = ""

	def write(self, content):
		content = content.decode()
		self.sendbuf += content
		assert content[-1] == "\n", "'{}'".format(content)
		content = content[:-1]
		if content in self.responses:
			self.recvbuf += RESPONSE_ADDRESS + self.responses[content]+"\n"

	def readline(self):
		return bytes(self.recvbuf, "utf8")

	def flush(self):
		pass

def create_bus(bufcontent):
	return Bus(FakeSerial(bufcontent))

class TestBus(unittest.TestCase):
	def test_to_hex(self):
		self.assertEqual(Bus._to_hex(16, 1), "10")
		self.assertEqual(Bus._to_hex(16, 2), "0010")
		self.assertRaises(AssertionError, Bus._to_hex, 500, 1)
		self.assertRaises(AssertionError, Bus._to_hex, "a", 1)
	def test_from_hex(self):
		self.assertRaises(AssertionError, Bus._pick_from_hex, 1, [])
		self.assertRaises(BusException, Bus._pick_from_hex, "", [("x",1)])
		self.assertRaises(BusException, Bus._pick_from_hex, "10", [])

		self.assertEqual(Bus._pick_from_hex("10", [("x", 1)]), {"x":16})
		self.assertEqual(Bus._pick_from_hex("100010", [("x", 1), ("y", 2)]), {"x":16, "y":16})

	def test_module_existence(self):
		self.assertEqual(create_bus({}).check_for_module("a"), None)
		self.assertEqual(create_bus({"aa":"0302"}).check_for_module("a"), {"revision":3, "num_random":2})
		self.assertRaises(BusException, create_bus({"aa":"3"}).check_for_module, "a")

	def test_module_init_0(self):
		serial = FakeSerial()
		bus = Bus(serial)
		bus.init_module("a", False, 16, 1)
		self.assertEqual(serial.sendbuf[:6], "ab0010")
		self.assertEqual(len(serial.sendbuf), 11)

	def test_module_init_1(self):
		serial = FakeSerial()
		bus = Bus(serial)
		bus.init_module("a", True, 16, 1)
		self.assertEqual(serial.sendbuf[:6], "ab0110")
		self.assertEqual(len(serial.sendbuf), 11)

	def test_game_start(self):
		serial = FakeSerial()
		bus = Bus(serial)
		bus.start_game("a")
		self.assertEqual(serial.sendbuf, "ac\n")

	def test_status_poll(self):
		self.assertEqual(create_bus({"ad":"0000"}).poll_status("a"), (False, 0))
		self.assertEqual(create_bus({"ad":"0100"}).poll_status("a"), (True, 0))
		self.assertEqual(create_bus({"ad":"0001"}).poll_status("a"), (False, 1))

	def test_status_broadcast(self):
		serial = FakeSerial()
		bus = Bus(serial)
		bus.broadcast_status(10, 1)
		self.assertEqual(serial.sendbuf, "_e000A01\n")

	def test_game_end(self):
		serial = FakeSerial()
		bus = Bus(serial)
		bus.end_game(1)
		self.assertEqual(serial.sendbuf, "_f01\n")
