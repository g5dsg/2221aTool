import click
import code
import sys
import usb.core
import lib.commands as cmds
from lib.utils import get_bit


# to-do enable finding of specific device via /dev/ttyACMX command instead of USB ids
config = {"idVendor": 0x04D8, "idProduct": 0x00DD, "hidDevice": 2}

# to-do pass these via optional command line
# until then, in case of emergency...
# config = {"idVendor": 0x0000, "idProduct": 0x0000, "hidDevice": 2}

dev = usb.core.find(idVendor=config["idVendor"], idProduct=config["idProduct"])

try:
    dev.detach_kernel_driver(config["hidDevice"])
except usb.core.USBError:
    pass  # its already detached...

# pick the first matching device we find
# to-do: detect specific nino by its /dev/ node
d = dev[0]
dev.reset()
hid = d[(2, 0)]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename", type=click.Path(exists=False))
def dump_flash(filename):
    """Dump the current flash config to a file for 'emergencies'."""
    hid.endpoints()[1].write(cmds.dumpFlash)
    response = hid.endpoints()[0].read(64)
    # to-do - verify good response...

    if response[0] == 0xB0 and response[1] == 0:
        print(f"Flash config bytes: {response[4:14]}")
        with open(filename, "wb") as f:
            f.write(response[4:14])
            f.close()
        click.secho(f"Dumped to {filename}")
    else:
        raise ValueError("bad response to flash read command")
    dev.reset()


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
def restore_flash(filename):
    with open(filename, "rb") as f:
        config = f.read()
        f.close()
    print(f"loaded flash config {config}")
    newConfig = config + bytes([0] * 8)
    hid.endpoints()[1].write(cmds.writeFlash + newConfig)
    ## to-do - check response
    click.secho("done")
    dev.reset()


@cli.command()
@click.argument("state", type=click.Choice(["0", "1"]))
def enum_serial(state):
    """Toggle serial number enumeration."""
    state = int(state)
    hid.endpoints()[1].write(cmds.dumpFlash)
    response = hid.endpoints()[0].read(64)

    if not response[0] == 0xB0 and response[1] == 0:
        raise ValueError("error reading flash data?")

    current_state = get_bit(response[4], 7)

    if current_state == state:
        click.secho(f"current state already {current_state}")
    else:
        response[4] = response[4] ^ 0b10000000
        newConfig = bytes(response[4:14]) + bytes([0] * 8)
        hid.endpoints()[1].write(cmds.writeFlash + newConfig)
        # to-do - check response
        click.secho("done")
    dev.reset()


@cli.command()
@click.argument("serial")
def set_serial(serial):
    """Sets the device serial number.
    Any unicode string of <=30 chars
    """
    if len(serial) > 30:
        raise ValueError

    serialBytes = serial.encode("utf-16-le")
    serialLen = len(serialBytes) + 2
    hid.endpoints()[1].write(cmds.setSerial + bytes([serialLen, 0x03]) + serialBytes)
    click.secho("done, please disconnect/reconnect the device to see changes")


if __name__ == "__main__":
    cli()
