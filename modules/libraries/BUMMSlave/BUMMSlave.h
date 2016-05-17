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
		char _revisionNumber;
		uint8_t _numRandomSeeds;
		uint8_t _digitalPin_LEDRed;
		uint8_t _digitalPin_LEDGreen;

		bool _moduleEnabled;
		bool _moduleArmed;
		uint8_t _failCount;
		
		uint8_t _receiveBuffer[32];
		uint8_t _BytesReceived = 0;

		// bus parsing functions
		void receive();
		void parseMessage();
		uint8_t getBufferByte(uint8_t number);
		uint16_t getTwoBufferBytes(uint8_t number_of_first_byte);
		void parseModuleExists();
		void parseModuleInit();
		void parseGameStart();
		void parseStatusPoll();
		void parseStatusBroadcast();
		void parseGameEnd();
	public:
		uint8_t randomSeeds[];
		uint8_t difficultyLevel;
		uint16_t currentCountDown;
		uint8_t globalFailureCount;

		// constructor
		BUMMSlave(char moduleID, char revisionNumber,  uint8_t numRandomSeeds, uint8_t digitalPin_LEDRed, uint8_t digitalPin_LEDGreen);
		
		// ------------------------------------
		// module state properties

		/// setters module arm state
		void rearm(); // call this method to rearm a this module during game
		void disarm(); // call this method to diasarm the module, for example if the user has solved the module riddle.
		void disarmFailed(); // call this method to log a failure. The failure counter will increased.
		

		// ------------------------------------
		// BUMM global settings getters
		bool isModuleEnabled();
		bool isArmed();
		bool isDisarmed();
		uint8_t disarmFailCount();

		void loop();
};

#endif
