#include <BUMMSlave.h>


void onModuleInit();
void onGameStart();
void onGameStatusUpdate();
void onGameEnd();


BUMMSlave::BUMMSlave(char moduleID, char revisionNumber,  uint8_t numRandomSeeds, uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen, uint8_t digitalPin_busEnable )
{
	_moduleID = moduleID;
	_revisionNumber = revisionNumber;
	_numRandomSeeds = numRandomSeeds;
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
}

void BUMMSlave::disarmFailed()
{
	_moduleArmed = true;
	_failCount++;
}

uint8_t BUMMSlave::disarmFailCount()
{
	return _failCount;
}

void BUMMSlave::rearm()
{
	_moduleArmed = true;
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
}


