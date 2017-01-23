#include <BUMMSlave.h>
#include <debounce.h>

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
	bs.loop();
	if(bs.isArmed())
	{
		if(get_debounced_flank(PIN_RUN) == LOW) // using closer as button!
		{
			if(input_valid(table_number_from_serial_number(bs.serialNumber), bs.randomSeeds[0], bs.serialNumber))
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
	autowires_setdisplay(bs.randomSeeds[0], bs.serialNumber);
}

void onGameStatusUpdate()
{
}

void onGameEnd(uint8_t result)
{
}


