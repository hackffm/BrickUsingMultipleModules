#include "Arduino.h"
#include "debounce.h"

#define NUM_PINS 13

uint8_t buffer[NUM_PINS] = {0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}; // 0b01 at end
uint8_t last_state[NUM_PINS] = {UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE, UNSURE};

uint8_t get_debounced_state(uint8_t pinNumber)
{
	if(pinNumber >= NUM_PINS)
		return UNSURE;
	buffer[pinNumber] <<= 1;
	buffer[pinNumber] |= digitalRead(pinNumber);

	if(buffer[pinNumber] == 0x00)
		return LOW;
	if(buffer[pinNumber] == 0xFF)
		return HIGH;
	return UNSURE;
}

uint8_t get_debounced_flank(uint8_t pinNumber)
{
	uint8_t current_state = get_debounced_state(pinNumber);
	if(current_state == UNSURE)
		return UNSURE;
	if(current_state != last_state[pinNumber])
	{
		last_state[pinNumber] = current_state;
		return current_state;
	}
	return UNSURE;
}
