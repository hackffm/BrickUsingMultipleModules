#include <BUMMSlave.h>

#define BROADCAST_ID '_'
#define MESSAGE_DELIMITER '\n'
#define RESPONSE_ID '='

#define TARGET_BYTE 0
#define COMMAND_BYTE 1
#define PARAMETER_START 2
#define EXPECT_LENGTH(count) if(_BytesReceived != (count+PARAMETER_START) ) return

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

uint8_t getNibbleFromHex(const char hex)
{
	uint8_t ret = 0;
	if((b >= '0') && (b <= '9'))
	{
		ret = b - '0';
	}
	else if((b >= 'a') && (b <= 'f'))
	{
		ret = b - 'a' + 10;
	}
	else if((b >= 'A') && (b <= 'F'))
	{
		ret = b - 'A' + 10;
	}
	return ret;
}


BUMMSlave::BUMMSlave(char moduleID, char revisionNumber,  uint8_t numRandomSeeds, uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen, uint8_t digitalPin_busEnable )
{
	_moduleID = moduleID;
	_revisionNumber = revisionNumber;
	_numRandomSeeds = numRandomSeeds;
	// TODO initialise randomSeeds
	_digitalPin_LEDRed = digitalPin_LEDRed;
	_digitalPin_LEDGreen = digitalPin_LEDGreen;
	_digitalPin_busEnable = digitalPin_busEnable;
}

// ----------------------------------------------------------
// private methods


// ----------------------------------------------------------
// public methods


// ------------------------------------
// module state properties

/// setters module arm state
void BUMMSlave::disarm()
{
	_moduleArmed = false;
	// TODO set LEDs
}

void BUMMSlave::disarmFailed()
{
	_moduleArmed = true;
	_failCount++;
	// TODO set LEDs
}

uint8_t BUMMSlave::disarmFailCount()
{
	return _failCount;
}

void BUMMSlave::rearm()
{
	_moduleArmed = true;
	// TODO set LEDs
}

// getters module arm state
bool BUMMSlave::isModuleEnabled()
{
	return _moduleEnabled;
}

bool BUMMSlave::isArmed()
{
	return _moduleArmed;
}

bool BUMMSlave::isDisarmed()
{
	return !_moduleArmed;
}

void BUMMSlave::loop()
{
	receive();
}

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
	}
}

uint8_t BUMMSlave::getBufferByte(uint8_t number)
{
	uint8_t ret = 0;
	ret = getNibbleFromHex(_receiveBuffer[PARAMETER_START+2*number]);
	ret <<= 4;
	ret |= getNibbleFromHex(_receiveBuffer[PARAMETER_START+2*number+2]);
	return ret;
}
uint16_t BUMMSlave::getTwoBufferBytes(uint8_t number_of_first_byte)
{
	uint16_t result = 0;
	uint8_t *ptr = _receiveBuffer + PARAMETER_START + 2*number_of_first_byte;
	uint8_t *end = ptr+4;
	for(uint8_t *end=ptr+4 ; ptr<end ; ptr++)
	{
		ret |= getNibbleFromHex(*ptr);
		ret <<= 4;
	}
	return result;
}

void BUMMSlave::parseModuleExists()
{
	EXPECT_LENGTH(0);
	Serial.print(RESPONSE_ID);
	Serial.print(_revisionNumber, HEX);
	Serial.print(_numRandomSeeds, HEX);
}

void BUMMSlave::parseModuleInit()
{
	EXPECT_LENGTH(2+_numRandomSeeds);
	
	uint8_t mode = getBufferByte(0)
	_moduleEnabled = mode & 0x01;

	difficultyLevel = getByteFromHex(1);

	for(uint8_t i=0;i<_numRandomSeeds;i++)
		randomSeeds[i] = getByteFromHex(2+i);

	// TODO reset internal logic (armed, failure counter, ...)

	onModuleInit();
}

void BUMMSlave::parseGameStart()
{
	EXPECT_LENGTH(0);
	onGameStart();
}

void BUMMSlave::parseStatusPoll()
{
	EXPECT_LENGTH(0);
	Serial.print(RESPONSE_ID);
	Serial.print(_moduleArmed ? 0 : 1, HEX);
	Serial.print(_failCount, HEX);
}

void BUMMSlave::parseStatusBroadcast()
{
	EXPECT_LENGTH(3);
	currentCountDown = getTwoBufferBytes(0);
	globalFailureCount = getBufferByte(2);
	onGameStatusUpdate();
}

void BUMMSlave::parseGameEnd()
{
	EXPECT_LENGTH(1);
	uint8_t gameEndStatus = getBufferByte(1); // TODO propagate this variable?
	onGameEnd();
}
