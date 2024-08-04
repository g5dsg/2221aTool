import click
import re
import sys
import usb.core
import lib.commands as cmds
from lib.utils import get_bit


@click.group()
@click.option("--serial", "-s", default=None, help="Device USB serial number")
@click.option("--vendor", default="0x04D8")
@click.option("--product", default="0x00DD")
@click.pass_context
def cli(ctx, serial, vendor, product):
    ctx.obj = dict()
    ctx.obj["serial"] = serial
    ctx.obj["vendor"] = int(vendor[-4:], 16)
    ctx.obj["product"] = int(product[-4:], 16)
    ctx.obj["hid_dev"] = 2
    ctx.obj["dev"], ctx.obj["hid"] = init_usb(
        ctx.obj["serial"], ctx.obj["vendor"], ctx.obj["product"], ctx.obj["hid_dev"]
    )


def init_usb(serial, vendor, product, hid_dev):
    if serial:
        dev = usb.core.find(idVendor=vendor, idProduct=product, serial_number=serial)
    else:
        dev = usb.core.find(idVendor=vendor, idProduct=product)

    try:
        dev.detach_kernel_driver(hid_dev)
    except usb.core.USBError:
        pass  # its already detached...
    except AttributeError:
        sys.exit("Device not found?")

    d = dev[0]
    dev.reset()
    hid = d[(2, 0)]
    return dev, hid


@cli.command()
@click.argument("filename", type=click.Path(exists=False))
@click.pass_context
def dump_flash(ctx, filename):
    """Dump the current flash config to a file for 'emergencies'."""
    hid = ctx.obj["hid"]
    dev = ctx.obj["dev"]
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
@click.pass_context
def restore_flash(ctx, filename):
    """Upload save flash config file to device."""
    hid = ctx.obj["hid"]
    dev = ctx.obj["dev"]
    with open(filename, "rb") as f:
        config = f.read()
        f.close()
    print(f"loaded flash config {config}")
    new_config = config + bytes([0] * 8)
    hid.endpoints()[1].write(cmds.writeFlash + new_config)
    # to-do - check response
    click.secho("done")
    dev.reset()


@cli.command()
@click.argument("state", type=click.Choice(["0", "1"]))
@click.pass_context
def enum_serial(ctx, state):
    """Toggle serial number enumeration."""
    hid = ctx.obj["hid"]
    dev = ctx.obj["dev"]
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
        new_config = bytes(response[4:14]) + bytes([0] * 8)
        hid.endpoints()[1].write(cmds.writeFlash + new_config)
        # to-do - check response
        click.secho("done")
    dev.reset()


@cli.command()
@click.argument("new_serial")
@click.pass_context
def set_serial(ctx, new_serial):
    """Sets the device serial number.
    Any unicode string of <=30 chars
    """
    hid = ctx.obj["hid"]
    if len(new_serial) > 30:
        raise ValueError

    serial_bytes = new_serial.encode("utf-16-le")
    serial_len = len(serial_bytes) + 2
    hid.endpoints()[1].write(cmds.setSerial + bytes([serial_len, 0x03]) + serial_bytes)
    click.secho("done, please disconnect/reconnect the device to see changes")


@cli.command()
@click.argument("desc")
@click.pass_context
def set_description(ctx, desc):
    """Sets the device description.
    Any unicode string of <=30 chars
    """
    hid = ctx.obj["hid"]
    if len(desc) > 30:
        raise ValueError

    desc_bytes = desc.encode("utf-16-le")
    desc_len = len(desc_bytes) + 2
    hid.endpoints()[1].write(cmds.setDescription + bytes([desc_len, 0x03]) + desc_bytes)
    click.secho("done, please disconnect/reconnect the device to see changes")


@cli.command()
#@click.argument("state", default="0000")
@click.pass_context
def setup_gpio(ctx):
    """Set all GPIO pins"""
    hid = ctx.obj["hid"]
    hid.endpoints()[1].write(cmds.setupGPIO)
    response = hid.endpoints()[0].read(64)
    click.secho("ok")


@cli.command()
@click.argument("state")
@click.pass_context
def set_gpio(ctx, state):
    """Set GPIO state"""
    hid = ctx.obj["hid"]

    if not re.match(r"^[01][01][01][01]$", state):
        raise ValueError
    cmd = cmds.setGPIO_temp
    for b in state:
        if b == "1":
            cmd = cmd + bytes([0x01, 0x01, 0x00, 0x00])
        else:
            cmd = cmd + bytes([0x01, 0x00, 0x00, 0x00])

    hid.endpoints()[1].write(cmd)
    response = hid.endpoints()[0].read(64)
    print(response)


if __name__ == "__main__":
    cli(obj={})
