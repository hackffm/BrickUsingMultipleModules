#include <BUMMSlave.h>


void onModuleInit();
void onGameStart();
void onGameStatusUpdate();
void onGameEnd();


BUMMSlave::BUMMSlave(uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen, uint8_t digitalPin_busEnable) 
{
}

// ----------------------------------------------------------
// private methods
uint8_t BUMMSlave::moduleState() {
    return 0;
}



// ----------------------------------------------------------
// public methods

// ------------------------------------
// module init setters
void BUMMSlave::setRevisionNumber(uint8_t revisionNumber) 
{
}

void BUMMSlave::setModuleID(char moduleID) 
{
}

void BUMMSlave::setRequiredRandomSeeds(uint8_t numRandomSeeds) 
{
}

// ------------------------------------
// module state properties

bool BUMMSlave::isModuleEnabled() // getter for determine module is enabled
{
}
/// setters module arm state
void BUMMSlave::disarm()
{
}

void BUMMSlave::diarmFail()
{
}

void BUMMSlave::arm()
{
}

// getters module arm state
bool BUMMSlave::isArmed()
{
}

bool BUMMSlave::isDisarmed()
{
}

// ------------------------------------
// BUMM global settings
uint8_t BUMMSlave::difficultyLevel()
{
}

uint16_t BUMMSlave::getCurrentCountDown()
{
}

uint8_t BUMMSlave::getGlobalFailureCount()
{
}

void BUMMSlave::loop()
{
}


