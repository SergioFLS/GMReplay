# Outside packages
import re
from functools import reduce
import webbrowser

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
    ## Rotates the 2d array, e.g. [[1, 2], [3, 4]] -> [[1, 3], [2, 4]]
    return list(list(thisTuple) for thisTuple in zip(*array[::]))


def reduceBitwiseOr(array):
    ## Takes a 2+d array and returns which subarrays have any nonzero bytes in them, e.g. [[b'\x00', b'\x01'], [b'\x00', b'\x00']] -> [True, False]
    if isinstance(array, list) or isinstance(array, tuple): # Operate recursively on any subarrays
        return [bool(reduce(lambda x, y: x | y, reduceBitwiseOr(subarray), 0)) for subarray in array]
    elif isinstance(array, str): # Make it not a string if it's a string
        return [0] if array.strip().strip('\x00').strip("0") == '' else [1]
    elif isinstance(array, bytes): # Make it not a string if it's a string
        return [0] if array.strip(b'\x00') == b'' else [1]
    else: # Return single-element array if not an array
        return [array]


def trimOrPadList(array, length, padValue=None):
    if len(array) < length:
        return array + [padValue] * (length - len(array))
    else:
        return array[:length]


def listIndicesThatAreTrue(array):
    ## Returns a list of indices corresponding to elements that evaluate to true
    return [index for index, element in enumerate(array) if element]


def keyName(keycode):
    ## Returns the name corresponding to a given key code, or the keycode itself if the key is not present in the dict
    return c.VK_NAMES.get(keycode, keycode)


def keyCodes(keyName):
    return next(key for key, value in c.VK_NAMES.items() if value == keyName)


def stringify(twoDimList):
    ## Takes a 2d list and turns each sub-sub-element into a string, returning a new list in the same structure as the original
    stringified2dList = []
    for row in twoDimList:
        thisRow = []
        for element in row:
            thisRow += [str(element)]
        stringified2dList += [thisRow]
    return stringified2dList


def openURL(url):
    webbrowser.open_new_tab(url)
