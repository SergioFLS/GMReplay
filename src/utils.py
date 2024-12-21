# Outside packages
import re

# Local packages
import constants as c


def folder(filePath):
    ## Returns the folder that contains the given file
    return "/".join(re.split(r'/|\\', filePath)[:-1]) # get stickbugged lol


def intToBytes(integer):
    ## Returns the bytes representation of a positive integer
    if integer < 0:
        return b"\x00"

    hexStr = hex(integer).removeprefix("0x")
    hexStr = hexStr.zfill(len(hexStr) + len(hexStr) % 2)

    return bytes.fromhex(hexStr)
