#ifndef BUMMSlave_h
#define BUMMSlave_h

#include <Arduino.h>

class BUMMSlave
{
	private:
		// Allmost any character is allowed. 
		// Folowing character is reserved -> _,\n,=
		// Don't use!!! 
		char _moduleID;
		
	public:
		uint8_t _randomSeeds[];

		// constructor
		BUMMSlave(uint8_t revisionNumber, char moduleID, uint8_t numRandomSeeds, uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen, uint8_t digitalPin_busEnable );
		
		
		// ------------------------------------
		// module state properties

		/// setters module arm state
		void rearm();
		void disarm();
		void diarmFail();

		// getters module arm state
		bool isArmed();
		bool isDisarmed();

		// ------------------------------------
		// BUMM global settings
		uint8_t getDifficultyLevel();
		uint16_t getCurrentCountDown();
		uint8_t getGlobalFailureCount();
	
		void loop();
};

#endif
