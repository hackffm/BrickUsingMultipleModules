#include <BUMMSlave.h>

BUMMSlave bs(1,2,3);


void setup()
{  
	bs.setRevisionNumber(8);
}

void loop()
{  
	bs.loop();
}