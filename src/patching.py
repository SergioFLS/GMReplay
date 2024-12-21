# Outside packages
import re

# Local packages
from utils import intToBytes

# Constants
import constants as c


def genPatchedExe(exePath, patchedName="__temp_GMR_patched_runner.exe"):
    ## Apply patches to the chosen exe and save it into the current working directory. Returns a path to the patched exe.

    exeModified = False

    # Read the exe into memory
    with open(exePath, 'rb') as fid:
        exeData = fid.read()

    # Mutable version to write the patched exe
    newExeData = bytearray(exeData)

    # Search for the mouse input offsets
    mousePattern1 = b"\x6A\x01\x6A\x04\x68.{18}\x6A\x01\x6A\x04\x68"
    mousePattern2 = b"\x6A\x01\x6A\x04\x68.{19}\x6A\x01\x6A\x04\x68"
    patternOffset = 0
    mouseRegex = re.compile(mousePattern1)

    # Run the regex search. Two matches expected.
    mouseOffsets = []
    for match_obj in mouseRegex.finditer(exeData):
        mouseOffsets += [match_obj.start()]

    # If there are not two matches, we don't know what to do, so print the error and return the original exe path
    if len(mouseOffsets) != 2:
        if len(mouseOffsets) == 1: # Match to pattern 2 for the second one
            patternOffset = 1
            mouseRegex = re.compile(mousePattern2)
            for match_obj in mouseRegex.finditer(exeData):
                mouseOffsets += [match_obj.start()]

    if len(mouseOffsets) != 2: # if it's still not 2 after we ran the second check
        print("WARNING: Patching encountered an issue. Mouse inputs will not work.")

    else: # Keep going if there is no issue, otherwise skip ahead to the next patch
        # If there are exactly two matches, we have g_MouseX and g_MouseY offsets and values
        g_MouseX_offsets = 2*[0]
        g_MouseY_offsets = 2*[0]

        g_MouseX_offsets[0] = mouseOffsets[0] + 5
        g_MouseX_offsets[1] = mouseOffsets[1] + 5

        g_MouseY_offsets[0] = mouseOffsets[0] + 28
        g_MouseY_offsets[1] = mouseOffsets[1] + 28 + patternOffset

        g_MouseX = exeData[g_MouseX_offsets[0]:g_MouseX_offsets[0] + 4]
        g_MouseY = exeData[g_MouseY_offsets[0]:g_MouseY_offsets[0] + 4]

        # Next we search forward past g_MouseY_offsets[1] to find the last pattern for g_MouseX
        mouseXUpdateOffset = exeData.find(g_MouseX, max(g_MouseY_offsets[0], g_MouseY_offsets[1]))
        mouseYUpdateOffset = exeData.find(g_MouseY, mouseXUpdateOffset-64) # it could also be before mouseX on older versions

        # Take the last bytes of g_MouseX/Y for search terms
        g_MousePosX_offset = exeData.rfind(g_MouseX[-1], mouseXUpdateOffset - 8, mouseXUpdateOffset) - 3
        g_MousePosY_offset = exeData.rfind(g_MouseY[-1], mouseYUpdateOffset - 8, mouseYUpdateOffset) - 3

        # We now have g_MousePosX/Y
        g_MousePosX = exeData[g_MousePosX_offset:g_MousePosX_offset + 4]
        g_MousePosY = exeData[g_MousePosY_offset:g_MousePosY_offset + 4]

        # Finally, we overwrite g_MouseX/Y with g_MousePosX/Y
        newExeData[g_MouseX_offsets[0]:g_MouseX_offsets[0] + 4] = g_MousePosX
        newExeData[g_MouseX_offsets[1]:g_MouseX_offsets[1] + 4] = g_MousePosX
        newExeData[g_MouseY_offsets[0]:g_MouseY_offsets[0] + 4] = g_MousePosY
        newExeData[g_MouseY_offsets[1]:g_MouseY_offsets[1] + 4] = g_MousePosY
        exeModified = True


    # Patch keyboard_check_direct next
    newExeData = replaceFunction(exeData, "keyboard_check", "keyboard_check_direct", newExeData,\
                                 "WARNING: Patching encountered an issue. Direct keyboard input will not work.")


    # Patch randomize
    newExeData = replaceFunction(exeData, "random_get_seed", "randomize", newExeData,\
                                 "WARNING: Patching encountered an issue. Randomness will not be deterministic.")


    # Done with the patched exe, now write it to the working directory
    if exeModified == True:
        with open(patchedName, 'wb') as fid:
            fid.write(newExeData)
        return patchedName

    else:
        return exePath


def replaceFunction(exeData, sourceFuncName, destFuncName, newExeData, failureMessage):
    ## Replaces one function by overwriting its definition with another function

    global exeModified # for indicating to the calling function whether the patch was successful

    # Find the offsets to the string names
    destStringOffset = exeData.find(bytes(destFuncName, "utf-8") + b"\x00")
    sourceStringOffset = exeData.find(bytes(sourceFuncName, "utf-8") + b"\x00")

    destFuncDefOffset = -1
    sourceFuncDefOffset = -1

    # Find the magic word representing the start of the image optional header
    imgOptHeadrAddr = exeData.find(b"\x0b\x01", 0x0, 0x200) # It should be at the beginning, otherwise oopsies

    if imgOptHeadrAddr != -1: # If it does equal -1, that's a failure and we'll kick back out to the warning below
        baseOfDataAddr = imgOptHeadrAddr + 0x18
        baseOfData = int.from_bytes(exeData[baseOfDataAddr:baseOfDataAddr+4][::-1]) # Reverse it and interpret it as an int

        imageBaseAddr = imgOptHeadrAddr + 0x1C
        imageBase = int.from_bytes(exeData[imageBaseAddr:imageBaseAddr+4][::-1]) # Reverse it and interpret it as an int

        # The baseOfData represents the offset in the file to the data section, but it overshoots (due to padding?)
        # So we need to find the true start addr of the data section and record the difference
        padLength = 0x60
        dataStartAddr = exeData.rfind(bytes(padLength), 0, baseOfData) + padLength
        dataBaseDiff = baseOfData - dataStartAddr

        # The total pointer offset is the sum of this difference and the image base address
        dataPtrOffset = dataBaseDiff + imageBase

        # Now we have what we need to find the function definitions
        destFuncDefOffset = exeData.find(b"\x68" + intToBytes(destStringOffset + dataPtrOffset)[::-1])
        sourceFuncDefOffset = exeData.find(b"\x68" + intToBytes(sourceStringOffset + dataPtrOffset)[::-1])

    if imgOptHeadrAddr == -1 or destFuncDefOffset == -1 or sourceFuncDefOffset == -1: # We couldn't do the patch
        print(failureMessage)
        return newExeData

    # The function itself starts 4 bytes earlier
    sourceFunction = exeData[sourceFuncDefOffset-4:sourceFuncDefOffset]

    # Overwrite the function
    newExeData[destFuncDefOffset-4:destFuncDefOffset] = sourceFunction
    exeModified = True

    return newExeData
