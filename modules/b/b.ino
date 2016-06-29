#include <BUMMSlave.h>

#include "pin_definitions.h"
#include "autowires.h"

BUMMSlave bs('b',0,1,PIN_STATUS_RED,PIN_STATUS_GREEN);

void setup()
{
	autowires_setup();
	bs.begin();
}

uint8_t table_number_from_serial_number(char serialNumber[])
{
	if(serialNumber[0] < '2')
		return 0;
	else if(serialNumber[0] < '4')
		return 1;
	else if(serialNumber[0] < '6')
		return 2;
	else
		return 3;
}

void loop()
{
	uint8_t was_released = true;
	bs.loop();
	if(bs.isArmed())
	{
		if(digitalRead(PIN_RUN) == HIGH) // using opener as button!
		{
			if(was_released)
			{
				if(input_valid(table_number_from_serial_number(bs.serialNumber), bs.randomSeeds[0], bs.serialNumber))
				{
					bs.disarm();
				}
				else
				{
					bs.disarmFailed();
				}
				was_released = false;
			}
		}
		else
			was_released = true;
	}
}

void onModuleInit()
{
}

void onGameStart()
{
	autowires_setdisplay(bs.randomSeeds[0], bs.serialNumber);
}

void onGameStatusUpdate()
{
}

void onGameEnd(uint8_t result)
{
}


