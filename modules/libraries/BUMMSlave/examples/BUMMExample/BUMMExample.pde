#include <BUMMSlave.h>

BUMMSlave bs('b','a',2,1,2,3);


void setup()
{  
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
	//
}

void onGameStatusUpdate()
{

}

void onGameEnd() 
{

}