#include <util/delay.h>
#include <Wire.h>
#include <BUMMSlave.h>
#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>
BUMMSlave bs('!',0,0,2,3);
Adafruit_7segment display = Adafruit_7segment();

//#define PIN_LOCK A3

const uint8_t LED_MASK_PB = (1<<2) | (1<<3) | (1<<4) | (1<<5);
const uint8_t LED_MASK_PC = (1<<3) - 1;

void setLifes(uint8_t lifes)
{
	PORTB &= ~(LED_MASK_PB);
	PORTC &= ~(LED_MASK_PC);
	switch(lifes) // fallthrough
	{
		case 7: PORTB |= (1<<2);
		case 6: PORTB |= (1<<3);
		case 5: PORTB |= (1<<4);
		case 4: PORTB |= (1<<5);
		case 3: PORTC |= (1<<0);
		case 2: PORTC |= (1<<1);
		case 1: PORTC |= (1<<2);
		case 0: ;
		default: ;
	}
}

void setup()
{
	//pinMode(PIN_LOCK, INPUT_PULLUP);
	DDRB |= LED_MASK_PB;
	DDRC |= LED_MASK_PC;

	display.begin(0x70);
	display.printError(); // "----"
	display.writeDisplay();
	bs.begin();
}
void loop()
{
	bs.loop();
	//if( digitalRead(PIN_LOCK) == LOW )
	//	bs.rearm();
}

void onModuleInit()
{
	display.printError(); // "----"
	display.writeDisplay();
}

void onGameStart()
{
	bs.disarm();
}

void onGameStatusUpdate()
{
	uint16_t total_seconds = bs.currentCountDown;
	uint8_t minutes = total_seconds / 60;
	uint8_t seconds = total_seconds % 60;
	
	// leading zeroes
	display.writeDigitNum(0, minutes / 10);
	display.writeDigitNum(1, minutes % 10);
	display.writeDigitNum(3, seconds / 10);
	display.writeDigitNum(4, seconds % 10);
	display.drawColon(total_seconds&0x01);
	display.writeDisplay();

	setLifes(bs.globalLifeCount);
}

void onGameEnd(uint8_t status)
{
	switch(status)
	{
	case GAME_END_DEFUSED:
		// do nothing
	break;
	case GAME_END_TIME:
		for(uint8_t i=0; i<10;i++)
		{
			display.writeDigitNum(0, 0);
			display.writeDigitNum(1, 0);
			display.writeDigitNum(3, 0);
			display.writeDigitNum(4, 0);
			display.writeDisplay();
			_delay_ms(500);

			display.printError();
			display.writeDisplay();
			_delay_ms(500);
		}
	break;
	case GAME_END_FAILURES:
		for(uint8_t i=0; i<10;i++)
		{
			setLifes(0);
			_delay_ms(500);
			setLifes(7);
			_delay_ms(500);
		}
	break;
	case GAME_END_ABORT:
		display.printError();
		display.writeDisplay();
	break;
	}
//	if(status != 0)
//	{
//		display.printError();
//		display.writeDisplay();
//	}
}

