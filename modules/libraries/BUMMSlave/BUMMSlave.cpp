#include <BUMMSlave.h>

BUMMSlave *BUMMSlave::first;

#define NO_ANGLE (0xff)

BUMMSlave::BUMMSlave() : pin(0),angle(NO_ANGLE),pulse0(0),min16(34),max16(150),next(0)
{}

void BUMMSlave::setMinimumPulse(uint16_t t)
{
    min16 = t/16;
}

void BUMMSlave::setMaximumPulse(uint16_t t)
{
    max16 = t/16;
}

uint8_t BUMMSlave::attach(int pinArg)
{
    pin = pinArg;
    angle = NO_ANGLE;
    pulse0 = 0;
    next = first;
    first = this;
    digitalWrite(pin,0);
    pinMode(pin,OUTPUT);
    return 1;
}

void BUMMSlave::detach()
{
    for ( BUMMSlave **p = &first; *p != 0; p = &((*p)->next) ) {
	if ( *p == this) {
	    *p = this->next;
	    this->next = 0;
	    return;
	}
    }
}

void BUMMSlave::write(int angleArg)
{
    if ( angleArg < 0) angleArg = 0;
    if ( angleArg > 180) angleArg = 180;
    angle = angleArg;
    // bleh, have to use longs to prevent overflow, could be tricky if always a 16MHz clock, but not true
    // That 64L on the end is the TCNT0 prescaler, it will need to change if the clock's prescaler changes,
    // but then there will likely be an overflow problem, so it will have to be handled by a human.
    pulse0 = (min16*16L*clockCyclesPerMicrosecond() + (max16-min16)*(16L*clockCyclesPerMicrosecond())*angle/180L)/64L;
}

uint8_t BUMMSlave::read()
{
    return angle;
}

uint8_t BUMMSlave::attached()
{
    for ( BUMMSlave *p = first; p != 0; p = p->next ) {
	if ( p == this) return 1;
    }
    return 0;
}

void BUMMSlave::refresh()
{
    uint8_t count = 0, i = 0;
    uint16_t base = 0;
    BUMMSlave *p;
    static unsigned long lastRefresh = 0;
    unsigned long m = millis();

    // if we haven't wrapped millis, and 20ms have not passed, then don't do anything
    if ( m >= lastRefresh && m < lastRefresh + 20) return;
    lastRefresh = m;

    for ( p = first; p != 0; p = p->next ) if ( p->pulse0) count++;
    if ( count == 0) return;

    // gather all the BUMMs in an array
    BUMMSlave *s[count];
    for ( p = first; p != 0; p = p->next ) if ( p->pulse0) s[i++] = p;

    // bubblesort the BUMMs by pulse time, ascending order
    for(;;) {
	uint8_t moved = 0;
	for ( i = 1; i < count; i++) {
	    if ( s[i]->pulse0 < s[i-1]->pulse0) {
		BUMMSlave *t = s[i];
		s[i] = s[i-1];
		s[i-1] = t;
		moved = 1;
	    }
	}
	if ( !moved) break;
    }

    // turn on all the pins
    // Note the timing error here... when you have many BUMMs going, the
    // ones at the front will get a pulse that is a few microseconds too long.
    // Figure about 4uS/BUMMSlave after them. This could be compensated, but I feel
    // it is within the margin of error of software BUMMs that could catch
    // an extra interrupt handler at any time.
    for ( i = 0; i < count; i++) digitalWrite( s[i]->pin, 1);

    uint8_t start = TCNT0;
    uint8_t now = start;
    uint8_t last = now;

    // Now wait for each pin's time in turn..
    for ( i = 0; i < count; i++) {
	uint16_t go = start + s[i]->pulse0;

	// loop until we reach or pass 'go' time
	for (;;) {
	    now = TCNT0;
	    if ( now < last) base += 256;
	    last = now;

	    if ( base+now > go) {
		digitalWrite( s[i]->pin,0);
		break;
	    }
	}
    }
}
