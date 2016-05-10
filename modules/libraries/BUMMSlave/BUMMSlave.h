#ifndef BUMMSlave_h
#define BUMMSlave_h

#include <Arduino.h>

class BUMMSlave
{
	private:
		// Allmost any character is allowed. 
		// Folowing character is reserved -> _,\n,=
		// Don't use!!! 
		char moduleID; 
		
		uint8_t[] randomSeeds;
		uint8_t moduleState();
	public:
		// constructor
		BUMMSlave(uint8_t __digitalPin_LEDRed, uint8_t __digitalPin_LEDGreen, uint8_t __digitalPin_busEnable );
		
		// ------------------------------------
		// module init setters
		void setRevisionNumber(uint8_t __revisionNumber);
		void setModuleID(char __moduleID);
		void setRequiredRandomSeeds(uint8_t __numRandomSeeds);

		// ------------------------------------
		// module state properties

		bool isModuleEnabled(); // getter for determine module is enabled

		// setters module arm state
		void disarm();
		void arm();

		// getters module arm state
		bool isArmed();
		bool isDisarmed();

		// ------------------------------------
		// BUMM global settings
		uint8_t difficultyLevel();
		uint16_t getCurrentCountDown();
		uint8_t getGlobalFailureCount();

};

#endif
