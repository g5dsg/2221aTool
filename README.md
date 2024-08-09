# 2221aTool

A simple script using Linux/pyusb to perform low-level configuration of MCP2221a USB-serial chips via their HID 
interface. This chip is found in many projects including the [NinoTNC](https://tarpn.net/t/nino-tnc/nino-tnc.html). 

Windows users see the official [MCP utility](https://www.microchip.com/en-us/product/mcp2221a).

## Overview

`2221aTool enum-serial 1`
Enables enumeration of the device serial number, this makes it possible for udev to identify the device uniquely when 
multiple 2221a chips are attached to the same computer. 0 disables enumeration.

udev rules to create fixed /dev/tnc-XX nodes for 2 attached devices with serials 0123456789 / 9876543210 might look 
something like this:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="00dd", ATTRS{serial}=="0123456789", SYMLINK+="tnc-2m"
SUBSYSTEM=="tty", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="00dd", ATTRS{serial}=="9876543210", SYMLINK+="tnc-4m"
```

`2221aTool set-serial 0123456789`
Set a new serial number - up to 30 (unicode) characters. Must disconnect/reconnect after this command.
All devices have a unique factory default serial, so this is not required for connecting multiple TNCs.

`2221aTool set-description NinoTNC `
Set a new serial number - up to 30 (unicode) characters. Must disconnect/reconnect after this command.

    Bus 003 Device 094: ID 04d8:00dd Microchip Technology, Inc. 📶📻💻-Nino_TNC-💻📻📶

`2221aTool dump-flash <file>`
Dumps the current flash config to *file*. This is useful to back up your flash settings in case of problems.

`2221aTool restore-flash <file>`
Restores flash settings from *file*
A default flash config is included in `data/`.

`2221aTool setup-gpio`
Configures the 4 GPIO pins on the MCP2221a as GPIO outputs. This command modifies the flask configuration (ie it is 
permanent) will be set to start low at power on.

`2221aTool set-gpio 1001`
Sets the GPIO pins to 1001. GPIO output must have been previously enabled using the above command. This command does 
not modify the flash on the chip, and the outputs will be reset to their default on next power up.

## Requirements

* MPC2221a device attached via USB
* Python 3.7+ (tested on 3.8)
* click
* pyusb
* Linux system with root access *or* a udev rule set to allow you to write access to the HID (not serial...) device

## Multiple devices
v0.2.0 now supports multiple attached devices - all commands accept the --serial option to address a specific chip. 
Note that you will need to enable serial enumeration with a single chip connected before this will work. This is not
required with a single 2221a chip attached as the code will address the first 2221a chip found.

## Known issues
It is possible to zero out the flash config, which will give you a device with a vendorId and productID of 0x0000.
You may run `2221aTool.py --vendor 0x0000 --product 0x0000 restore-flash data/default_flash.bin` to undo this.
I recommend this over trying to back out changes, so you know that you have a good flash config installed.

## to-do:
* allow setting of a default power up config on the GPIO pins other than 0000. 
* implement commands to:
  * set manufacturer string (note udev seems to ignore this...)
  * set custom product/vendor ids
  * read existing serial number
* general code tidy
* better status/error checking
* document udev rule to make the HID device user-writeable (might be a bad idea given potential to corrupt config?).

## Further reading 
This utility was written primarily for users of the [NinoTNC](https://tarpn.net/t/nino-tnc/nino-tnc.html). 
With a custom modification it is possible to switch the device mode using this utility. 
For more information see [The OARC Wiki](https://wiki.oarc.uk/packet:ninotnc)

## Finally

This utility is provided as-is and without warranty. I socket all MCP2221a chips I install, and you might wish to do 
the same if you intend to experiment! 

If you do find this utility useful, I'd love to hear what you're using it for!