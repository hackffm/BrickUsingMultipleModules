# Protocol

## Message anatomy

### Gamemaster -> module
* First byte: target ID (module)
 * starting with "a"
 * "_" is broadcast
* Second byte: Command
* Following bytes: command parameters
* Ended with "\n"

### Module response
* First byte: "=" (response)
* Return values from slave to master

### a: Module exists?

Parameter: none
Return:
* 1 byte module-specific revision number
* 1 byte number of random bytes requested on gamestart

### b: Module init

Parameter
* 1 byte mode:
 * bit 0: is enabled?
* 5 bytes serial number, each byte an ascii value for a digit/letter
 * first two digits are decimal digits. Higher number repesents a higher difficulty and modules should choose difficulty accordingly
 * the following two digits are decimal digits which just carry some entropy
 * the last digit should be an uppercase letter
 * example: "2410H" would be difficulty 24
* N bytes random number (according to module description)

Result:
* Reset logic
* Reset hardware
* Reset failure counter

### c: Game start (broadcast)
Enables displays and countdown

### d: Status poll

Parameter: none
Return
* 1 byte success state (1 if defused, 0 if not defused yet)
* 1 byte failure counter (gets incremented each failure)

### e: Game status broadcast

Parameter
* 2 byte: remaining seconds
* 1 byte: failure counter

### f: Game end

Parameter
* 1 byte: game result (0: defused, 1: timeout, 2: too many failures)
