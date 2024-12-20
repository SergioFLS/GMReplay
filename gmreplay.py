import subprocess
import os
import re
import sys
from tkinter import Tk, ttk, filedialog, IntVar


VERSION_NUMBER = "v0.1.0"
MIN_PYTHON = (3, 12)

RECORD = 1 # Constants for readability
PLAY = 2

GLOBAL_PADDING = 4


def main():
    # Init
    print("GMReplay " + VERSION_NUMBER + " by OceanBagel\n")

    # Enforce a minimum Python version
    if sys.version_info < MIN_PYTHON:
        print("Python %s.%s or later is required.\n" % MIN_PYTHON)
        return

    # Initialize tkinter window
    root, exeFileRow, dataWinFileRow, movieFileRow, recordPlayRow = initWindow()

    # Execute main loop, broken apart to process stdout from the game window
    while True:
        root.update_idletasks()
        root.update()

        # Prevent blocking from the game process
        if recordPlayRow.process != None:
            for line in recordPlayRow.process.stdout:
                print(line.decode('utf-8').strip())


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


class filePromptWithHistory:
    ## Consists of a label, a combo box, and a browse button. Keeps track of history for the session.

    def __init__(self, frame, rowOffset, columnOffset, promptText, fileExists, extensions, defaultExtension, isFolder, defaultPath = os.getcwd(),\
                 exeFilePathObj=None, dataWinFilePathObj=None, movieFilePathObj=None, recordPlayObj=None):
        self.frame = frame
        pad = GLOBAL_PADDING
        self.fileExists = fileExists

        self.exeFilePathObj = exeFilePathObj
        self.dataWinFilePathObj = dataWinFilePathObj
        self.movieFilePathObj = movieFilePathObj
        self.recordPlayObj = recordPlayObj

        self.history = []
        self.isFolder = isFolder

        # Create the label
        self.label = ttk.Label(frame, text=promptText)
        self.label.grid(column=0+columnOffset, row=0+rowOffset, sticky="E", padx=pad, pady=pad)

        # Create the combo box
        self.combobox = ttk.Combobox(frame, values=self.history, width=80)
        self.combobox.grid(column=1+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="EW", columnspan=2)

        # Create the browse button
        self.button = ttk.Button(frame, text="Browse...", command=lambda:self.browseFile(promptText, extensions, defaultExtension))
        self.button.grid(column=3+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="E")

        # Only the combo box should be resizable
        frame.grid_columnconfigure(0+columnOffset, weight=0)
        frame.grid_columnconfigure(1+columnOffset, weight=1)
        frame.grid_columnconfigure(3+columnOffset, weight=0)

    def browseFile(self, promptText, extensions=\
                   [("All files","*.*"), ("GMReplay files", "*.gmr"), ("Executable files", "*.exe"), ("*.win files", "*.win")],\
                   defaultExtension="*.gmr", defaultPath=os.getcwd()):
        ## This searches for a file and adds it to the combo box history
        filePath = filedialog.askopenfilename(parent=self.frame, initialdir=defaultPath, title=promptText, defaultextension=defaultExtension, filetypes=extensions) if self.fileExists else \
            filedialog.asksaveasfilename(parent=self.frame, initialdir=defaultPath, title=promptText, defaultextension=defaultExtension, filetypes=extensions)
        if filePath:
            self.combobox.set(filePath)
            self.addToHistory(filePath)

    def addToHistory(self, filePath):
        ## Add the file path to history if it's not already there, and also run some checks for actions to be completed when a file is selected
        if filePath not in self.history:
            self.history.insert(0, filePath)
            self.combobox["values"] = self.history

            # If the exe was just selected, try to select the data.win by default
            if self.exeFilePathObj.get() != "" and self.dataWinFilePathObj.get() == "":
                dataWinDefaultPath = folder(self.exeFilePathObj.get()) + "/data.win"
                if os.path.isfile(dataWinDefaultPath):
                    # Don't add this to history because the user did not select it!
                    self.dataWinFilePathObj.set(dataWinDefaultPath)

            # If all three files have been selected, enable the record/play buttons
            if self.exeFilePathObj.get() != "" and self.dataWinFilePathObj.get() != "" and self.movieFilePathObj.get() != "":
                self.recordPlayObj.enable()


class recordPlayRadioButtons:
    ## The record and play radio buttons and the start button.

    def __init__(self, frame, rowOffset, columnOffset, exeFileRow, dataWinFileRow, movieFileRow, recordText, playbackText, startText):

        self.process = None
        self.exeFileRow = exeFileRow
        self.dataWinFileRow = dataWinFileRow
        self.movieFileRow = movieFileRow

        self.recordPlayVar = IntVar(frame, RECORD)

        pad = GLOBAL_PADDING

        self.recordRadioButton = ttk.Radiobutton(frame, text=recordText, value=RECORD, variable=self.recordPlayVar, command=self.radioButtonInteract)
        self.recordRadioButton.grid(column=0+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="NW")

        self.playRadioButton = ttk.Radiobutton(frame, text=playbackText, value=PLAY, variable=self.recordPlayVar, command=self.radioButtonInteract)
        self.playRadioButton.grid(column=0+columnOffset, row=1+rowOffset, padx=pad, pady=pad, sticky="NW")

        self.startButton = ttk.Button(frame, text=startText, command=lambda:self.recordOrPlayMovie(self.recordPlayVar.get()))
        self.startButton.grid(column=0+columnOffset, row=2+rowOffset, padx=pad, pady=pad, sticky="NW")

        # Disable after creating the buttons
        self.disable()

    def recordOrPlayMovie(self, selection):
        ## Handles recording (selection is 1 aka RECORD) or playback (selection is 2 aka PLAY)

        # Attempt to patch the exe file
        pathToExe = genPatchedExe(self.exeFileRow.combobox.get())

        # Run the game with the record command
        self.process = subprocess.Popen([pathToExe, ("-record" if selection == RECORD else "-playback"), self.movieFileRow.combobox.get(),\
                        "-game", self.dataWinFileRow.combobox.get(), "-debugoutput", os.getcwd() + "\\debugoutput.log", "|", "cat"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Prevent blocking of the game process
        os.set_blocking(self.process.stdout.fileno(), False)

    def enable(self): # Enable the buttons
        self.startButton.config(state="enabled")

    def disable(self): # Disable the buttons
        self.startButton.config(state="disabled")

    def radioButtonInteract(self): # Make it prompt for opening or saving based on the button
        self.movieFileRow.fileExists = self.recordPlayVar.get() == PLAY


def initWindow():
    ## Creates the base window

    root = Tk()
    root.title("GMReplay " + VERSION_NUMBER)

    frm = ttk.Frame(root)
    frm.grid(row=0, column=0, sticky="NSEW")

    root.grid_columnconfigure(0, weight=1)

    # File prompts
    exeFileRow = filePromptWithHistory(frm, 0, 0, "Game executable:", True, [("Executable files", "*.exe"), ("All files","*.*")], "*.exe", False)
    dataWinFileRow = filePromptWithHistory(frm, 1, 0, "Game data.win file:", True, [("*.win files", "*.win"), ("All files","*.*")], "*.win", False, defaultPath=exeFileRow.combobox.get())
    movieFileRow = filePromptWithHistory(frm, 2, 0, "Movie file:", False, [("GMReplay files", "*.gmr"), ("All files","*.*")], "*.gmr", False)

    # Record/play buttons, passing the row objects themselves
    recordPlayRow = recordPlayRadioButtons(frm, 3, 0, exeFileRow, dataWinFileRow, movieFileRow, "Record", "Playback", "Start")

    # Now that the objects are all created, update each one with links to the others' combo boxes. TODO: find a better way to do this
    exeFileRow.exeFilePathObj = exeFileRow.combobox
    exeFileRow.dataWinFilePathObj = dataWinFileRow.combobox
    exeFileRow.movieFilePathObj = movieFileRow.combobox
    exeFileRow.recordPlayObj = recordPlayRow

    dataWinFileRow.exeFilePathObj = exeFileRow.combobox
    dataWinFileRow.dataWinFilePathObj = dataWinFileRow.combobox
    dataWinFileRow.movieFilePathObj = movieFileRow.combobox
    dataWinFileRow.recordPlayObj = recordPlayRow

    movieFileRow.exeFilePathObj = exeFileRow.combobox
    movieFileRow.dataWinFilePathObj = dataWinFileRow.combobox
    movieFileRow.movieFilePathObj = movieFileRow.combobox
    movieFileRow.recordPlayObj = recordPlayRow

    return root, exeFileRow, dataWinFileRow, movieFileRow, recordPlayRow


if __name__ == '__main__':
    main()
