dumpFlash = bytes([0xB0, 0x00])
writeFlash = bytes([0xB1, 0x00])
setSerial = bytes([0xB1, 0x04])

# deprecated - Configure GPIO power status - all pins as output / low at startup
setupGPIO = bytes([0xb1, 0x01, 0x00, 0x00, 0x00, 0x00])

# new commands to-do...
setGPIO_perm = bytes([0xb1, 0x01])
setGPIO_temp = bytes([0x50, 0x00])

# to-do - implement these:
getFactorySerial = bytes([0xB0, 0x05])
setDescription = bytes([0xB1, 0x03])
