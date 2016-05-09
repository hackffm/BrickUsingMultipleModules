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
* First byte: "R" (response)
* random stuff

### a: Module exists?

Parameter: none
Return:
* 1 byte module-specific revision number

### b: Module init

Parameter
* 1 byte mode:
 * bit 0: is enabled?
* 1 byte difficulty level (0-255), module specific implementation
* 2 byte random number seed

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
