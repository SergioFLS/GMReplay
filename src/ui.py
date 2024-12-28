# Outside packages
import subprocess
import os
from tkinter import Tk, ttk, filedialog, IntVar
from tksheet import Sheet

# Local packages
from utils import folder
from patching import genPatchedExe
from movieparsing import loadMovie, getColumnsList

# Constants
import constants as c


class filePromptWithHistory:
    ## Consists of a label, a combo box, and a browse button. Keeps track of history for the session.

    def __init__(self, frame, rowOffset, columnOffset, promptText, fileExists, extensions, defaultExtension, isFolder, mainWindowObj, defaultPath = os.getcwd()):
        self.frame = frame
        self.mainWindowObj = mainWindowObj
        pad = c.GLOBAL_PADDING
        self.fileExists = fileExists

        self.history = []
        self.isFolder = isFolder

        # Create the label
        self.label = ttk.Label(frame, text=promptText)
        self.label.grid(column=0+columnOffset, row=0+rowOffset, sticky="E", padx=pad, pady=pad)

        # Create the combo box
        self.combobox = ttk.Combobox(frame, values=self.history, width=80)
        self.combobox.grid(column=1+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="EW", columnspan=10)

        # Create the browse button
        self.button = ttk.Button(frame, text="Browse...", command=lambda:self.browseFile(promptText, extensions, defaultExtension))
        self.button.grid(column=11+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="E")

        # Only the combo box should be resizable
        frame.grid_columnconfigure(0+columnOffset, weight=0)
        frame.grid_columnconfigure(10+columnOffset, weight=1)
        frame.grid_columnconfigure(11+columnOffset, weight=0)

    def browseFile(self, promptText, extensions=\
                   [("All files","*.*"), ("GMReplay files", "*.gmr"), ("Executable files", "*.exe"), ("*.win files", "*.win")],\
                   defaultExtension="*.gmr", defaultPath=os.getcwd()):
        ## This searches for a file and adds it to the combo box history
        filePath = filedialog.askopenfilename(parent=self.frame, title=promptText, initialdir=defaultPath, defaultextension=defaultExtension, filetypes=extensions) if self.fileExists else \
            filedialog.asksaveasfilename(parent=self.frame, title=promptText, initialdir=defaultPath, defaultextension=defaultExtension, filetypes=extensions)
        if filePath:
            self.combobox.set(filePath)
            self.addToHistory(filePath)
            if promptText == c.MOVIE_FILE_PROMPT:
                self.mainWindowObj.loadMovieInputs(filePath)

    def addToHistory(self, filePath):
        ## Add the file path to history if it's not already there, and also run some checks for actions to be completed when a file is selected
        if filePath not in self.history:
            self.history.insert(0, filePath)
            self.combobox["values"] = self.history

            # If the exe was just selected, try to select the data.win by default
            if self.mainWindowObj.isExeSelectedButNotDataWin():
                dataWinDefaultPath = folder(self.mainWindowObj.exeFileRow.combobox.get()) + "/data.win"
                if os.path.isfile(dataWinDefaultPath):
                    # Don't add this to history because the user did not select it!
                    self.mainWindowObj.dataWinFileRow.combobox.set(dataWinDefaultPath)

            # If all three files have been selected, enable the start buttons
            if self.mainWindowObj.areAllFilesSelected():
                self.mainWindowObj.recordPlayRow.enableStart()


class recordPlayRadioButtons:
    ## The record and play radio buttons and the start button.

    def __init__(self, frame, rowOffset, columnOffset, recordText, playbackText, startText, stopText, mainWindowObj):

        self.mainWindowObj = mainWindowObj
        self.frame = frame

        self.recordPlayVar = IntVar(frame, c.RECORD)

        pad = c.GLOBAL_PADDING

        self.recordRadioButton = ttk.Radiobutton(frame, text=recordText, value=c.RECORD, variable=self.recordPlayVar, command=self.radioButtonInteract)
        self.recordRadioButton.grid(column=0+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="NE")

        self.playRadioButton = ttk.Radiobutton(frame, text=playbackText, value=c.PLAY, variable=self.recordPlayVar, command=self.radioButtonInteract)
        self.playRadioButton.grid(column=1+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="NE")

        self.startButton = ttk.Button(frame, text=startText, command=lambda:self.recordOrPlayMovie(self.recordPlayVar.get()))
        self.startButton.grid(column=2+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="NE")

        self.stopButton = ttk.Button(frame, text=stopText, command=self.stopButtonInteract)
        self.stopButton.grid(column=3+columnOffset, row=0+rowOffset, padx=pad, pady=pad, sticky="NE")

        frame.grid_columnconfigure(0+columnOffset, weight=0)
        frame.grid_columnconfigure(1+columnOffset, weight=0)
        frame.grid_columnconfigure(2+columnOffset, weight=0)

        # Disable after creating the buttons
        self.disableStart()
        self.disableStop()

    def recordOrPlayMovie(self, selection):
        ## Handles recording (selection is 1 aka RECORD) or playback (selection is 2 aka PLAY)

        # Attempt to patch the exe file
        pathToExe = genPatchedExe(self.mainWindowObj.exeFileRow.combobox.get())

        # Run the game with the record command
        print(c.GAME_START_STRING)
        self.mainWindowObj.gameProcess = subprocess.Popen([pathToExe, ("-record" if selection == c.RECORD else "-playback"), self.mainWindowObj.movieFileRow.combobox.get(),\
                        "-game", self.mainWindowObj.dataWinFileRow.combobox.get(), "-debugoutput", os.getcwd() + "\\debugoutput.log", "|", "cat"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Prevent blocking of the game process
        os.set_blocking(self.mainWindowObj.gameProcess.stdout.fileno(), False)

        # Disable Start, enable Stop, disable radio buttons
        self.movieStart()

    def enableStart(self): # Enable the start button
        self.startButton.config(state="enabled")

    def disableStart(self): # Disable the start button
        self.startButton.config(state="disabled")

    def enableRadio(self): # Enable the radio buttons
        self.recordRadioButton.config(state="enabled")
        self.playRadioButton.config(state="enabled")

    def disableRadio(self): # Disable the radio buttons
        self.recordRadioButton.config(state="disabled")
        self.playRadioButton.config(state="disabled")

    def enableStop(self): # Enable the stop button
        self.stopButton.config(state="enabled")

    def disableStop(self): # Disable the stop button
        self.stopButton.config(state="disabled")

    def movieStart(self): # Commands to run when the movie starts
        self.disableStart()
        self.enableStop()
        self.disableRadio()

    def movieEnd(self): # Commands to run when the movie ends
        if self.mainWindowObj.areAllFilesSelected():
            self.enableStart()
        self.disableStop()
        self.enableRadio()
        if self.recordPlayVar.get() == c.RECORD: # Only reload the movie if we were recording
            self.mainWindowObj.inputGridObj.loadMovieInputs()

    def radioButtonInteract(self): # Make it prompt for opening or saving based on the button
        self.mainWindowObj.movieFileRow.fileExists = self.recordPlayVar.get() == c.PLAY

    def stopButtonInteract(self): # Commands to run when the stop button is pressed
        print(c.GAME_STOP_STRING)
        self.mainWindowObj.gameProcess.terminate()
        self.movieEnd()


class mainWindowClass:
    ## A class to hold variables in the main window

    def __init__(self, columnsList=c.DEFAULT_COLUMNS_LIST):
        self.columnsList = columnsList

        # Create the base window
        self.gameProcess = None
        self.root = Tk()
        self.root.title(c.WINDOW_TITLE)

        self.mainWindowFrame = ttk.Frame(self.root)
        self.mainWindowFrame.grid(row=0, column=0, sticky="NSEW")

        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # File prompts
        self.exeFileRow = filePromptWithHistory(self.mainWindowFrame, 0, 0, c.EXE_FILE_PROMPT, True, [("Executable files", "*.exe"), ("All files","*.*")], "*.exe", False, self)
        self.dataWinFileRow = filePromptWithHistory(self.mainWindowFrame, 1, 0, c.DATAWIN_FILE_PROMPT, True, [("*.win files", "*.win"), ("All files","*.*")], "*.win", False, self, defaultPath=self.exeFileRow.combobox.get())
        self.movieFileRow = filePromptWithHistory(self.mainWindowFrame, 2, 0, c.MOVIE_FILE_PROMPT, False, [("GMReplay files", "*.gmr"), ("All files","*.*")], "*.gmr", False, self)

        # Record/play buttons, passing the row objects themselves
        self.recordPlayRow = recordPlayRadioButtons(self.mainWindowFrame, 3, 0, c.RECORDING_STRING, c.PLAYBACK_STRING, c.START_STRING, c.STOP_STRING, self)

        # Debug button
        # self.debugButton = ttk.Button(self.mainWindowFrame, text="Test", command=lambda:self.loadMovieInputs("C:\\Users\\OceanBagel\\Documents\\_Projects\\GMReplay\\kz_new.gmr"))
        # self.debugButton.grid(column=4, row=3, padx=c.GLOBAL_PADDING, pady=c.GLOBAL_PADDING)

        # Create the input window
        self.inputWindowFrame = ttk.Frame(self.root)
        self.inputWindowFrame.grid(row=4, column=0, sticky="NSEW")

        self.inputGridObj = inputSheetClass(self.inputWindowFrame, 0, 0, self.columnsList, self)

    def areAllFilesSelected(self):
        return self.exeFileRow.combobox.get() != "" and self.dataWinFileRow.combobox.get() != "" and self.movieFileRow.combobox.get() != ""

    def isExeSelectedButNotDataWin(self):
        return self.exeFileRow.combobox.get() != "" and self.dataWinFileRow.combobox.get() == ""

    def loadMovieInputs(self, movieFilePath):
        return self.inputGridObj.loadMovieInputs(movieFilePath)


class inputSheetClass:
    ## A class for using Tksheet for the input display
    def __init__(self, inputWindowFrame, rowOffset, columnOffset, columnLabelList, mainWindowObj, loadedMovieData=[]):
        self.mainWindowObj = mainWindowObj
        self.inputWindowFrame = inputWindowFrame
        self.rowOffset = rowOffset
        self.columnOffset = columnOffset

        # Initialize the sheet object with the column labels
        self.sheet = Sheet(self.inputWindowFrame, headers=columnLabelList, data=self.stringify(loadedMovieData))
        self.sheet.enable_bindings()
        self.sheet.pack(side="top", fill="both", expand=True)

    def stringify(self, twoDimList):
        stringified2dList = []
        for row in twoDimList:
            thisRow = []
            for element in row:
                thisRow += [str(element)]
            stringified2dList += [thisRow]
        return stringified2dList

    def updateInputGrid(self, loadedMovieData):
        self.sheet.set_sheet_data(self.stringify(loadedMovieData))

    def updateColumnLabels(self, columnsList):
        self.sheet.set_header_data(columnsList, range(len(columnsList)))

    def loadMovieInputs(self, movieFilePath=None):
        # If a movie file path wasn't given, use the previous one
        if movieFilePath != None:
            # Assign the movieFilePath to self
            self.movieFilePath = movieFilePath

        # Make sure it's a real path
        if self.movieFilePath != "":
            print(c.LOADING_MOVIE_STRING)
            # Parse the inpts
            self.loadedMovieData = loadMovie(self.movieFilePath)
            self.columnsList = getColumnsList(self.loadedMovieData)

            print(c.UPDATE_INPUT_EDITOR_STRING)
            self.updateInputGrid(self.loadedMovieData)
            self.updateColumnLabels(self.columnsList)

            # Update the main window and then print the completion message
            self.mainWindowObj.root.update_idletasks()
            self.mainWindowObj.root.update()

            print(c.MOVIE_LOADED_STRING)
