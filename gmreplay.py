import subprocess
import tkinter.filedialog
import os
import re


VERSION_NUMBER = "v0.0.3"


def main():
    # Init
    print("GMReplay " + VERSION_NUMBER + " by OceanBagel\n")
    selection = 0

    # Main menu loop
    while selection != 3:
        selection = makeSelection(['1', '2', '3'], "\nPlease select from the following options:\
        \n1. Record a movie\
        \n2. Playback a movie\
        \n3. Exit\n")

        # Perform the requested operation
        match selection:
            case 1 | 2: # Record a movie or Playback a movie
                recordOrPlayMovie(selection)
            case 3: # Exit
                pass # Maybe do something different later, but for now we pass here and break out of the next loop iteration


def folder(filePath):
    ## Returns the folder that contains the given file
    return "/".join(re.split(r'/|\\', filePath)[:-1]) # get stickbugged lol


def makeSelection(validOptions, inputText = ""):
    ## Returns the integer entered provided it's included in the valid options. If a blank string is allowed, it will return 0.
    selection = 0
    selection = input(inputText)
    while selection not in validOptions:
        selection = input("Invalid input\n")
    if selection == '':
        selection = 0
    return int(selection)


def recordOrPlayMovie(selection):
    ## Handles recording (selection is 1) or playback (selection is 2)

    # Ask for a path to the game first
    exePrompt = "Please select the game's exe file"
    print(exePrompt)
    pathToExe = browseFile(exePrompt, True, extensions=[("Executable files", "*.exe"), ("All files","*.*")], defaultExtension="*.exe")

    # Assume the data.win, or prompt if it's not found
    pathToDataWin = folder(pathToExe) + "/data.win"

    # Does the data.win exist here?
    if not os.path.isfile(pathToDataWin):
        # If not, prompt for it
        dataWinPrompt = "Please select the game's data.win file"
        print(dataWinPrompt)
        pathToDataWin = browseFile(dataWinPrompt, True, extensions=[("*.win files", "*.win"), ("All files","*.*")], defaultExtension="*.win",\
                                   defaultPath=pathToDataWin.strip("data.win"))

    # Ask for a path to the recording next
    moviePrompt = "Please select the movie file"
    print(moviePrompt)
    pathToRecording = browseFile(moviePrompt, selection == 2, extensions=[("GMReplay files", "*.gmr"), ("All files","*.*")], defaultExtension="*.gmr")

    # Attempt to patch the exe file
    pathToExe = genPatchedExe(pathToExe)

    # Run the game with the record command
    subprocess.run([pathToExe, ("-record" if selection == 1 else "-playback"), pathToRecording, "-game", pathToDataWin, "-debugoutput", "gmrdebug.txt"])


def browseFile(promptText, fileExists, extensions=[("All files","*.*"), ("GMReplay files", "*.gmr"), ("Executable files", "*.exe")], defaultExtension="*.gmr", defaultPath=os.getcwd()):
    ## Wrapper for tkinter filedialog

    # Create a fake window (replace with real window when GUI is implemented)
    root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window

    # Get the file path, starting in the working directory
    ret = tkinter.filedialog.askopenfilename(parent=root, initialdir=defaultPath, title=promptText, defaultextension=defaultExtension, filetypes=extensions) if fileExists else \
        tkinter.filedialog.asksaveasfilename(parent=root, initialdir=defaultPath, title=promptText, defaultextension=defaultExtension, filetypes=extensions)

    # Destroy the tkinter window
    root.destroy()

    return ret


def genPatchedExe(exePath, patchedName="__temp_GMR_patched_runner.exe"):
    ## Apply patches to the chosen exe and save it into the current working directory. Returns a path to the patched exe.

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
            print("WARNING: Patching was unsuccessful. Mouse inputs and direct keyboard inputs will not work.\n"+\
                  "Falling back on the unpatched exe file...")
            return exePath

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


    # Patch keyboard_check_direct next
    kcdStringOffset = bytes(hex(exeData.find(b"keyboard_check_direct\x00")), 'utf-8')
    kcStringOffset = bytes(hex(exeData.find(b"keyboard_check\x00")), 'utf-8')

    # Actual offsets are always at least 0x400000 away and multiples of 0x100 away
    # TODO: find a better way to get this number
    kcdFuncDefOffset = -1
    kcFuncDefOffset = -1
    for i in range(0x400C00, 0x402000, 0x100):

        # First write out the address in hex
        hexVal = hex(int(kcStringOffset, 16) + i)[2:]
        if len(hexVal) % 2 != 0:
            hexVal = "0" + hexVal

        # Search for the address, but flip the address's bytes around
        kcFuncDefOffset = exeData.find(b"\x68" + bytes.fromhex(hexVal)[::-1])

        if kcFuncDefOffset != -1: # There was a hit

            # Try the same number on the other one
            hexVal = hex(int(kcdStringOffset, 16) + i)[2:]
            if len(hexVal) % 2 != 0:
                hexVal = "0" + hexVal
            kcdFuncDefOffset = exeData.find(b"\x68" + bytes.fromhex(hexVal)[::-1])
            break

    # If the same number didn't work, try this again
    if kcdFuncDefOffset == -1:
        for i in range(0x400C00, 0x402000, 0x100):
            hexVal = hex(int(kcdStringOffset, 16) + i)[2:]
            if len(hexVal) % 2 != 0:
                hexVal = "0" + hexVal
            kcdFuncDefOffset = exeData.find(b"\x68" + bytes.fromhex(hexVal)[::-1])
            if kcdFuncDefOffset != -1:
                break

    if kcFuncDefOffset == -1 or kcdFuncDefOffset == -1: # We couldn't do the patch
        print("WARNING: Patching was partially successful. Mouse inputs will work, but direct keyboard input will not.")

        # Patch the mouse changes
        with open(patchedName, 'wb') as fid:
            fid.write(newExeData)
        return patchedName

    # The function itself starts 4 bytes earlier
    kcFunction = exeData[kcFuncDefOffset-4:kcFuncDefOffset]

    # Overwrite the function
    newExeData[kcdFuncDefOffset-4:kcdFuncDefOffset] = kcFunction


    # Done with the patched exe, now write it to the working directory
    with open(patchedName, 'wb') as fid:
        fid.write(newExeData)

    return patchedName


if __name__ == '__main__':
    main()
