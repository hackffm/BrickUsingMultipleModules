#include <util/delay.h>
#include <Wire.h>
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
#define MESSAGE_DELIMITER '\n'
#define PARAMETER_START 2
#define COMMAND_BYTE 1
#define CMD_MODULE_INIT 'b'
#define SERIAL_NUMBER_LENGTH 5
uint8_t getNibbleFromHex(const char hex)
{
	uint8_t ret = 0;
	if((hex >= '0') && (hex <= '9'))
	{
		ret = hex - '0';
	}
	else if((hex >= 'a') && (hex <= 'f'))
	{
		ret = hex - 'a' + 10;
	}
	else if((hex >= 'A') && (hex <= 'F'))
	{
		ret = hex - 'A' + 10;
	}
	return ret;
}

uint8_t getBufferByte(String buf, uint8_t number)
{
	uint8_t ret = 0;
	ret = getNibbleFromHex(buf[PARAMETER_START+2*number]);
	ret <<= 4;
	ret |= getNibbleFromHex(buf[PARAMETER_START+2*number+1]);
	return ret;
}
void setup()
{
	lcd.begin(16, 2);
	Serial.begin(19200);
	UCSR0B &= ~(1<<TXEN0); // disable TX
	lcd.print("BUMM");
}
void printSerial(uint8_t version, uint8_t number[])
{
	switch(version & 0x03)
	{
	case 0:
		for(uint8_t i=0; i<SERIAL_NUMBER_LENGTH; i++)
			lcd.write(number[i]);
		break;
	case 1:
		for(uint8_t i=0; i<SERIAL_NUMBER_LENGTH; i++)
			lcd.write(number[4-i]);
		break;
	case 2:
		lcd.write(number[0]);
		lcd.write(number[1]);
		lcd.write(number[4]);
		lcd.write(number[3]);
		lcd.write(number[2]);
		break;
	case 3:
		lcd.write(number[2]);
		lcd.write(number[0]);
		lcd.write(number[1]);
		lcd.write(number[4]);
		lcd.write(number[3]);
		break;
	}
}
void loop()
{
	String cmd=Serial.readStringUntil(MESSAGE_DELIMITER);
	uint8_t number[SERIAL_NUMBER_LENGTH];
	if(cmd.charAt(COMMAND_BYTE) == CMD_MODULE_INIT) // somebody got a serial number
	{
		for(uint8_t i=0; i<SERIAL_NUMBER_LENGTH; i++)
			number[i] = getBufferByte(cmd, i+1);

		uint8_t checksum = 0;
		for(uint8_t i=0; i<SERIAL_NUMBER_LENGTH; i++)
			checksum ^= number[i];
		
		lcd.setCursor(0, 0);
		printSerial(checksum+0, number);

		lcd.setCursor(11, 0);
		printSerial(checksum+1, number);

		lcd.setCursor(0, 1);
		printSerial(checksum+2, number);

		lcd.setCursor(11, 1);
		printSerial(checksum+3, number);
	}
}
