#include <BUMMSlave.h>

#include "pin_definitions.h"
#include "autowires.h"

BUMMSlave bs('b',0,0,2,3);

void setup()
{
	autowires_setup();
	bs.begin();
}

uint8_t table_number_from_difficulty(uint8_t difficulty)
{
	return 0; // TODO
}

void loop()
{
	bs.loop();
	if(bs.isArmed())
	{
		if(digitalRead(PIN_RUN) == LOW)
		{
			if(input_valid(table_number_from_difficulty(bs.difficultyLevel), bs.randomSeeds[0]))
			{
				bs.disarm();
			}
			else
			{
				bs.disarmFailed();
			}
		}
	}
}

void onModuleInit()
{
}

void onGameStart()
{
	autowires_setdisplay(bs.randomSeeds[0]);
}

void onGameStatusUpdate()
{
}

void onGameEnd(uint8_t result)
{
}


