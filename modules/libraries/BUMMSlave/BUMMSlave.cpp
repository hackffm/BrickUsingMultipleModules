#include <BUMMSlave.h>

#define BROADCAST_ID '_'
#define MESSAGE_DELIMITER '\n'
#define RESPONSE_ID '='

#define TARGET_BYTE 0
#define COMMAND_BYTE 1
#define PARAMETER_START 2
#define EXPECT_LENGTH(count) if(_BytesReceived != (2*count+PARAMETER_START) ) {setErrorStatus(); return;}

#define CMD_MODULE_EXISTS 'a'
#define CMD_MODULE_INIT 'b'
#define CMD_GAME_START 'c'
#define CMD_STATUS_POLL 'd'
#define CMD_STATUS_BROADCAST 'e'
#define CMD_GAME_END 'f'

void onModuleInit();
void onGameStart();
void onGameStatusUpdate();
void onGameEnd();

void setSerialOutputEnabled()
{
	UCSR0B |= (1<<TXEN0);
}
void endSerialCommand()
{
	Serial.write('\n');
	Serial.flush();
	UCSR0B &= ~(1<<TXEN0);
}

uint8_t getNibbleFromHex(const char hex)
{
	uint8_t ret = 0;
	if((hex >= '0') && (hex <= '9'))
	{
		ret = hex - '0';
	}
	else if((hex >= 'a') && (hex <= 'f'))
	{
		ret = hex - 'a' + 10;
	}
	else if((hex >= 'A') && (hex <= 'F'))
	{
		ret = hex - 'A' + 10;
	}
	return ret;
}

void sendHexByte(uint8_t value)
{
	if(value<0x10)
		Serial.print("0");
	Serial.print(value, HEX);
}


BUMMSlave::BUMMSlave(char moduleID, char revisionNumber,  uint8_t numRandomSeeds, uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen)
{
	_moduleID = moduleID;
	_revisionNumber = revisionNumber;
	_numRandomSeeds = numRandomSeeds;
	// TODO initialise randomSeeds
	_digitalPin_LEDRed = digitalPin_LEDRed;
	_digitalPin_LEDGreen = digitalPin_LEDGreen;
	_BytesReceived = 0;

	_moduleStatus = MODULE_STATUS_DISABLED;
	pinMode(_digitalPin_LEDRed, OUTPUT);
	pinMode(_digitalPin_LEDGreen, OUTPUT);

	setLEDs();
}
void BUMMSlave::begin()
{
	UCSR0B &= ~(1<<TXEN0);
}

// ----------------------------------------------------------
// private methods


// ----------------------------------------------------------
// public methods


// ------------------------------------
// module state properties

void BUMMSlave::setLEDs()
{
	switch(_moduleStatus)
	{
		case MODULE_STATUS_DISABLED:
			digitalWrite(_digitalPin_LEDRed, LOW);
			digitalWrite(_digitalPin_LEDGreen, LOW);
			break;
		case MODULE_STATUS_INITIALIZED:
			digitalWrite(_digitalPin_LEDRed, LOW);
			digitalWrite(_digitalPin_LEDGreen, LOW);
			break;
		case MODULE_STATUS_ARMED:
			digitalWrite(_digitalPin_LEDRed, HIGH);
			digitalWrite(_digitalPin_LEDGreen, LOW);
			break;
		case MODULE_STATUS_DEFUSED:
			digitalWrite(_digitalPin_LEDRed, LOW);
			digitalWrite(_digitalPin_LEDGreen, HIGH);
			break;
		case MODULE_STATUS_ERROR:
		default:
			digitalWrite(_digitalPin_LEDRed, HIGH);
			digitalWrite(_digitalPin_LEDGreen, HIGH);
			break;
	}
}
/// setters module arm state
void BUMMSlave::disarm()
{
	if( (_moduleStatus == MODULE_STATUS_ARMED) ||
	    (_moduleStatus == MODULE_STATUS_DEFUSED) )
		_moduleStatus = MODULE_STATUS_DEFUSED;
	else
		setErrorStatus();
	setLEDs();
}

void BUMMSlave::disarmFailed()
{
	_failCount++;
	setLEDs();
	// TODO set LEDs
}

uint8_t BUMMSlave::disarmFailCount()
{
	return _failCount;
}

void BUMMSlave::rearm()
{
	if( (_moduleStatus == MODULE_STATUS_DEFUSED) ||
	    (_moduleStatus == MODULE_STATUS_ARMED) )
		_moduleStatus = MODULE_STATUS_ARMED;
	else
		setErrorStatus();
	setLEDs();
}

// getters module arm state
bool BUMMSlave::isModuleEnabled()
{
	return (_moduleStatus == MODULE_STATUS_DEFUSED) || (_moduleStatus == MODULE_STATUS_ARMED) || (_moduleStatus == MODULE_STATUS_INITIALIZED);
}

bool BUMMSlave::isArmed()
{
	return _moduleStatus==MODULE_STATUS_ARMED;
}

bool BUMMSlave::isDisarmed()
{
	return _moduleStatus==MODULE_STATUS_DEFUSED;
}

void BUMMSlave::loop()
{
	receive();
}

void BUMMSlave::setErrorStatus()
{
	_moduleStatus = MODULE_STATUS_ERROR;
}

/// Fills _receiveBuffer with data and calls parseMessage on complete reception
void BUMMSlave::receive()
{
	uint8_t next_char;
	while(Serial.available())
	{
		next_char = Serial.read();
		if(next_char == MESSAGE_DELIMITER)
		{
			parseMessage();
			_BytesReceived = 0;
		}
		else
		{
			_receiveBuffer[_BytesReceived++] = next_char;
		}
	}
}

/// Parses the target and command parts of the message and invokes the corresponding handler
void BUMMSlave::parseMessage()
{
	if( (_receiveBuffer[TARGET_BYTE] != _moduleID) && (_receiveBuffer[TARGET_BYTE] != BROADCAST_ID) )
		return; // message not intended for us

	switch(_receiveBuffer[COMMAND_BYTE])
	{
		case CMD_MODULE_EXISTS:
			BUMMSlave::parseModuleExists();
			break;
		case CMD_MODULE_INIT:
			BUMMSlave::parseModuleInit();
			break;
		case CMD_GAME_START:
			BUMMSlave::parseGameStart();
			break;
		case CMD_STATUS_POLL:
			BUMMSlave::parseStatusPoll();
			break;
		case CMD_STATUS_BROADCAST:
			BUMMSlave::parseStatusBroadcast();
			break;
		case CMD_GAME_END:
			BUMMSlave::parseGameEnd();
			break;
		default:
			// error?
			break;
	}
}

/// Parse a hex-encoded parameter from the message buffer
// \param number byte-based index of the parameter to parse. 0 corresponds to the first byte in the parameter section
// \returns the parsed value in a range 0-255
uint8_t BUMMSlave::getBufferByte(uint8_t number)
{
	uint8_t ret = 0;
	ret = getNibbleFromHex(_receiveBuffer[PARAMETER_START+2*number]);
	ret <<= 4;
	ret |= getNibbleFromHex(_receiveBuffer[PARAMETER_START+2*number+1]);
	return ret;
}

/// Get two bytes (16 bit) of hex-encoded data from the buffer
// \param number_of_first_byte byte-based index of the parameter to parse. 0 corresponds to the first two bytes in the parameter section
uint16_t BUMMSlave::getTwoBufferBytes(uint8_t number_of_first_byte)
{
	uint16_t result = 0;
	uint8_t *ptr = _receiveBuffer + PARAMETER_START + 2*number_of_first_byte;
	for(uint8_t *end=ptr+4 ; ptr<end ; ptr++)
	{
		result |= getNibbleFromHex(*ptr);
		result <<= 4;
	}
	return result;
}

void BUMMSlave::parseModuleExists()
{
	EXPECT_LENGTH(0)
	setSerialOutputEnabled();
	Serial.print(RESPONSE_ID);
	sendHexByte(_revisionNumber);
	sendHexByte(_numRandomSeeds);
	endSerialCommand();
}

void BUMMSlave::parseModuleInit()
{
	EXPECT_LENGTH(2+_numRandomSeeds)
	
	uint8_t mode = getBufferByte(0);
	if(_moduleStatus == MODULE_STATUS_DISABLED)
	{
		if(mode & 0x01) // enabled
			_moduleStatus = MODULE_STATUS_INITIALIZED;
	}
	else
		setErrorStatus();
	difficultyLevel = getBufferByte(1);

	for(uint8_t i=0;i<_numRandomSeeds;i++)
		randomSeeds[i] = getBufferByte(2+i);

	_failCount = 0;
	// TODO reset internal logic (armed, failure counter, ...)
	setLEDs();

	onModuleInit();
}

void BUMMSlave::parseGameStart()
{
	EXPECT_LENGTH(0)
	if(_moduleStatus == MODULE_STATUS_INITIALIZED)
		_moduleStatus = MODULE_STATUS_ARMED;
	else if(_moduleStatus == MODULE_STATUS_DISABLED)
		;
	else
		setErrorStatus();
	setLEDs();
	onGameStart();
}

void BUMMSlave::parseStatusPoll()
{
	EXPECT_LENGTH(0)
	setSerialOutputEnabled();
	Serial.print(RESPONSE_ID);
	if(_moduleStatus == MODULE_STATUS_ARMED)
		sendHexByte(0);
	else if(_moduleStatus == MODULE_STATUS_DEFUSED)
		sendHexByte(1);
	else
	{
		setErrorStatus();
		setLEDs();
		sendHexByte(0xff);
	}
	sendHexByte(_failCount);
	endSerialCommand();
}

void BUMMSlave::parseStatusBroadcast()
{
	EXPECT_LENGTH(3)
	currentCountDown = getTwoBufferBytes(0);
	globalFailureCount = getBufferByte(2);
	onGameStatusUpdate();
}

void BUMMSlave::parseGameEnd()
{
	EXPECT_LENGTH(1)
	uint8_t gameEndStatus = getBufferByte(1); // TODO propagate this variable?
	_moduleStatus = MODULE_STATUS_DISABLED;
	setLEDs();
	onGameEnd();
}
