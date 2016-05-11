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
		
		uint8_t _randomSeeds[];
		uint8_t moduleState();



	public:
		// constructor
		BUMMSlave(uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen, uint8_t digitalPin_busEnable );
		
		// ------------------------------------
		// module init setters
		void setRevisionNumber(uint8_t revisionNumber);
		void setModuleID(char moduleID);
		void setRequiredRandomSeeds(uint8_t numRandomSeeds);

		// ------------------------------------
		// module state properties

		bool isModuleEnabled(); // getter for determine module is enabled

		/// setters module arm state
		void disarm();
		void diarmFail();
		void arm();


		// getters module arm state
		bool isArmed();
		bool isDisarmed();

		// ------------------------------------
		// BUMM global settings
		uint8_t difficultyLevel();
		uint16_t getCurrentCountDown();
		uint8_t getGlobalFailureCount();

		void loop();
};

#endif
