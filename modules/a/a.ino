#include <BUMMSlave.h>

BUMMSlave bs('a',0,0,2,3);

#define PIN_BTN_DISARM 5
#define PIN_BTN_FAIL 4

void setup()
{
	pinMode(PIN_BTN_DISARM, INPUT_PULLUP);
	pinMode(PIN_BTN_FAIL, INPUT_PULLUP);

	Serial.begin(19200);
	bs.begin();
}

void loop()
{
	bs.loop();
	if(bs.isModuleEnabled())
	{
		if(digitalRead(PIN_BTN_DISARM) == LOW)
			bs.disarm();
		if(digitalRead(PIN_BTN_FAIL) == LOW)
			bs.disarmFailed();
	}
}

void onModuleInit()
{
}

void onGameStart()
{
}

void onGameStatusUpdate()
{
}

void onGameEnd(uint8_t result)
{
}


