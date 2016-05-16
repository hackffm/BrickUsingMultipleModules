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

void onModuleInit()
{
	// this function are called if the gamemaster do a init call
}

void onGameStart() 
{

}
void onGameStatusUpdate();
void onGameEnd();