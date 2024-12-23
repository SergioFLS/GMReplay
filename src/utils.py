# Outside packages
import re
from functools import reduce
from pickle import dumps

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


def rotate2DArray(array):
    return list(zip(*array[::]))


def reduceBitwiseOr(array):
    return reduce(lambda x, y: x | int.from_bytes(dumps(y)), array, 0)


def trimOrPadList(array, length, padValue=None):
    if len(array) < length:
        return array + [padValue] * (length - len(array))
    else:
        return array[:length]


def listIndicesThatAreTrue(array):
    ## Returns a list of indices corresponding to elements that evaluate to true
    return [index for index, element in enumerate(array) if element]
