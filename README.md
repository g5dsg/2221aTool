# 2221aTool

A simple script using Linux/pyusb to perform basic configuration of MCP2221a USB-serial chips via their HID interface.
This chip is found in many projects including the NinoTNC. 

Windows users see the official [MCP utility](https://www.microchip.com/en-us/product/mcp2221a).

## Overview

`2221aTool enum-serial 1`
Enables enumeration of the device serial number, this makes it possible for udev to identify the TNC uniquely when multiple devices are attached to the same computer. 0 disables enumeration

`2221aTool set-serial 0123456789`
Set a new serial number - up to 30 (unicode) characters. Must disconnect/reconnect after this command.
All devices have a unique factory default serial, so this is not required for connecting multiple TNCs.

`2221aTool set-description NinoTNC `
Set a new serial number - up to 30 (unicode) characters. Must disconnect/reconnect after this command.

    Bus 003 Device 094: ID 04d8:00dd Microchip Technology, Inc. 📶📻💻-Nino_TNC-💻📻📶

`2221aTool dump-flash <file>`
Dumps the current flash config to <file>. This is useful if you break it.

`2221aTool restore-flash <file>`
Restores flash settings from <file>
A default flash config is inclued in data/.

## Requirements

* MPC2221a device attached via USB
* Python 3.7+ (tested on 3.8)
* click
* pyusb
* Linux system with root access *or* a udev rule set to allow you write access to the HID (not serial...) device


## known issues
Its possible to zero out the flash config bytes. This will reassign the device vendor/product ids of 0x000. 
A quick hack of the code to use these and `restore-flash` will recover you from this situation.
To-do: stop this happening, and make vendor/product ids passable by params


## to-do:
* implement commands to
  * set manufacturer string (note udev seems to ignore this...)
* general code tidy
* better status/error checking
* document udev rule to make the HID device user-writeable (might be a bad idea given potential to corrupt config?).
