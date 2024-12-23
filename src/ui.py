# Outside packages
import subprocess
import os
from tkinter import Tk, ttk, filedialog, IntVar, Canvas

# Local packages
from utils import folder, trimOrPadList
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

        self.root.grid_columnconfigure(0, weight=1)

        # Create the input window
        self.inputWindowFrame = ttk.Frame(self.root)
        self.inputWindowFrame.grid(row=4, column=0, sticky="NSW")  # Add E to allow resizing columns (unsupported for now)

        self.inputGridObj = inputGridClass(self.inputWindowFrame, 0, 0, self.columnsList, self)

        # Configure columns to resize as necessary
        for i in range(len(self.columnsList)):
            self.inputWindowFrame.grid_columnconfigure(i, weight=1)

        # File prompts
        self.exeFileRow = filePromptWithHistory(self.mainWindowFrame, 0, 0, c.EXE_FILE_PROMPT, True, [("Executable files", "*.exe"), ("All files","*.*")], "*.exe", False, self)
        self.dataWinFileRow = filePromptWithHistory(self.mainWindowFrame, 1, 0, c.DATAWIN_FILE_PROMPT, True, [("*.win files", "*.win"), ("All files","*.*")], "*.win", False, self, defaultPath=self.exeFileRow.combobox.get())
        self.movieFileRow = filePromptWithHistory(self.mainWindowFrame, 2, 0, c.MOVIE_FILE_PROMPT, False, [("GMReplay files", "*.gmr"), ("All files","*.*")], "*.gmr", False, self)

        # Record/play buttons, passing the row objects themselves
        self.recordPlayRow = recordPlayRadioButtons(self.mainWindowFrame, 3, 0, c.RECORDING_STRING, c.PLAYBACK_STRING, c.START_STRING, c.STOP_STRING, self)

        # Debug button
        # self.debugButton = ttk.Button(self.mainWindowFrame, text="Test", command=lambda:print("Insert function here."))
        # self.debugButton.grid(column=4, row=3, padx=c.GLOBAL_PADDING, pady=c.GLOBAL_PADDING)

    def areAllFilesSelected(self):
        return self.exeFileRow.combobox.get() != "" and self.dataWinFileRow.combobox.get() != "" and self.movieFileRow.combobox.get() != ""

    def isExeSelectedButNotDataWin(self):
        return self.exeFileRow.combobox.get() != "" and self.dataWinFileRow.combobox.get() == ""

    def loadMovieInputs(self, movieFilePath):
        return self.inputGridObj.loadMovieInputs(movieFilePath)


class inputGridClass:
    ## A class for the input grid

    def __init__(self, inputWindowFrame, rowOffset, columnOffset, columnsList, mainWindowObj, loadedMovieData=[]):
        self.mainWindowObj = mainWindowObj
        self.inputWindowFrame = inputWindowFrame

        # Label row, the top row indicating the name of each column.
        self.labelRow = labelRowClass(inputWindowFrame, rowOffset, columnOffset, columnsList)

        # Get widths of all the labels in pixels
        self.mainWindowObj.root.update_idletasks() # Update the window to render the labels, required to measure widths
        self.widthsList = []
        for i in range(len(self.labelRow.labelsList)):
            self.widthsList += [self.labelRow.labelsList[i].winfo_width()]

        # Add a label in the label row to leave space for the scrollbar
        self.placeholderScrollbar = ttk.Label(inputWindowFrame, width=2)
        self.placeholderScrollbar.grid(row=0, column=len(columnsList))

        # Create a frame within which the input rows will be
        self.inputRowFrame = ttk.Frame(self.inputWindowFrame)
        self.inputRowFrame.grid(row=rowOffset+1, column=columnOffset, sticky="NSEW", columnspan=len(columnsList) + 1)

        # Canvas representing the scrollable area
        self.inputRowCanvas = Canvas(self.inputRowFrame)
        self.inputRowCanvas.grid(row=0, column=0, sticky="nw")
        self.inputRowCanvas.configure(scrollregion=[0, 0, 0, 0], height=c.INPUT_SCROLLABLE_AREA_HEIGHT)

        # Create a vertical scrollbar on the canvas
        self.inputScrollbar = ttk.Scrollbar(self.inputRowFrame, orient="vertical", command=self.inputRowCanvas.yview)
        self.inputScrollbar.grid(row=0, column=1, sticky="NS")
        self.inputScrollbar.grid_rowconfigure(0, weight=1)
        self.inputRowCanvas.configure(yscrollcommand=self.inputScrollbar.set)

        # Inner frame contained within the canvas
        self.inputRowInnerFrame = ttk.Frame(self.inputRowFrame)
        self.inputRowInnerFrame.grid(row=0, column=0, sticky="NSEW")

        # Canvas contained within the inner frame, where the inputs will actually be drawn
        self.inputRowInnerCanvas = Canvas(self.inputRowInnerFrame, width=c.INPUT_CANVAS_WIDTH, height=c.INPUT_CANVAS_HEIGHT)
        self.inputRowInnerCanvas.pack(fill = "both", expand = True)

        # Create the input rows using loaded movie data if present
        self.inputRows = inputRowsClass(self.inputRowInnerCanvas, 0, 0, loadedMovieData, self.widthsList)

        self.inputRowCanvasID = self.inputRowCanvas.create_window((0, 0), window=self.inputRowInnerFrame, anchor="nw")

        # Grid configure. TODO: Remove the unnecessary ones.
        self.inputWindowFrame.grid_rowconfigure(rowOffset+1, weight=1)
        self.inputWindowFrame.grid_columnconfigure(columnOffset, weight=1)
        self.inputRowFrame.grid_rowconfigure(0, weight=1)
        self.inputRowFrame.grid_columnconfigure(0, weight=1)
        self.inputRowInnerFrame.grid_rowconfigure(0, weight=1)
        self.inputRowInnerFrame.grid_columnconfigure(0, weight=1)

    def updateInputGrid(self, loadedMovieData):
        self.inputRows.updateInputGrid(loadedMovieData)

    def updateColumnLabels(self, columnsList):
        self.labelRow.updateLabelText(columnsList)

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
            self.inputRowCanvas.configure(scrollregion=[0, 0, 0, c.DEFAULT_ROW_HEIGHT * min(len(self.loadedMovieData), c.FRAMES_PER_PAGE)])

            # Update the main window and then print the completion message
            self.mainWindowObj.root.update_idletasks()
            self.mainWindowObj.root.update()

            print(c.MOVIE_LOADED_STRING)


class labelRowClass:
    ## The row of labels at the top of the input column

    def __init__(self, frame, rowOffset, columnOffset, labelTextList, reliefType=c.LABEL_RELIEF_TYPE):
        self.frame = frame
        self.rowOffset = rowOffset
        self.columnOffset = columnOffset
        self.labelTextList = labelTextList

        self.columnWidths = c.DEFAULT_COLUMN_WIDTHS
        self.borderWidth = c.INPUT_BORDER_WIDTH
        self.reliefType = reliefType
        pad = 0

        # Iterate over the columns
        self.labelsList = []

        for i in range(len(self.labelTextList)):

            self.labelsList += [ttk.Label(self.frame, text=self.labelTextList[i], width=self.columnWidths[i],\
                                          borderwidth = self.borderWidth, relief=self.reliefType, anchor="center")]
            self.labelsList[i].grid(column=columnOffset + i, row=rowOffset, padx=pad, pady=pad, sticky="EW")

    def updateLabelText(self, labelTextList):
        for i in range(len(self.labelsList)):
            self.labelsList[i].config(text = labelTextList[i])


class inputRowsClass:
    ## The row of scrollable inputs

    def __init__(self, inputRowCanvas, rowOffset, columnOffset, loadedMovieData, widthsList=c.DEFAULT_COLUMN_WIDTHS):
        self.inputRowCanvas = inputRowCanvas
        self.rowOffset = rowOffset
        self.columnOffset = columnOffset
        self.widthsList = widthsList
        self.inputGridRows = []
        self.borderWidth = c.INPUT_BORDER_WIDTH

    def updateInputGrid(self, loadedMovieData):
        previousLength = len(self.inputGridRows)

        # Remove the frames that should no longer be shown
        if previousLength > len(loadedMovieData):
            for i in range(len(loadedMovieData), previousLength):
                self.inputGridRows[i].delete()

        # Trim or pad the input grid rows to the proper length
        self.inputGridRows = trimOrPadList(self.inputGridRows, len(loadedMovieData))

        # Iterate over each frame of the movie, edit any rows that already exist
        # TODO: Improve performance here. Multiprocessing is possible because each row is independent of the others.
        for frameIndex in range(min(len(loadedMovieData), c.FRAMES_PER_PAGE)): # We can only store up to 1000 frames in the canvas right now. TODO: Expand this.
            if self.inputGridRows[frameIndex] != None: # If this row was already created
                self.inputGridRows[frameIndex].updateLabelText(([frameIndex] + loadedMovieData[frameIndex]))
            else: # otherwise, create new labels
                self.inputGridRows[frameIndex] = canvasTextboxRow(self.inputRowCanvas, self.rowOffset + frameIndex, self.columnOffset,\
                                                          [frameIndex] + loadedMovieData[frameIndex], self.widthsList)


class canvasTextboxRow:
    ## This creates a row of textboxes on the canvas

    def __init__(self, canvas, rowOffset, columnOffset, labelTextList, columnWidthList = c.DEFAULT_COLUMN_WIDTHS):
        self.canvas = canvas
        self.rowOffset = rowOffset
        self.columnOffset = columnOffset
        self.labelTextList = labelTextList
        self.columnWidthList = columnWidthList
        self.rowHeight = c.DEFAULT_ROW_HEIGHT
        self.textItems = []
        self.borderItems = []

        # Create text
        self.createText(columnWidthList, labelTextList)

    def createText(self, columnWidthList, labelTextList):
        currentOrigin = 0
        widthRatio = 1 # Hardcoded for now, the ratio between the column widths (in characters) and rectangle widths (in pixels)
        self.borderItems = trimOrPadList(self.borderItems, len(columnWidthList))
        self.textItems = trimOrPadList(self.textItems, len(labelTextList))
        bg_color = self.canvas.cget("background")
        for i in range(len(labelTextList)):
            self.borderItems[i] = self.canvas.create_rectangle(currentOrigin, self.rowOffset * self.rowHeight,\
                                         currentOrigin + (columnWidthList[i] * widthRatio), self.rowHeight + (self.rowOffset * self.rowHeight),\
                                         fill=bg_color, outline="black", width=2)
            self.textItems[i] = self.canvas.create_text(currentOrigin + 5, self.rowOffset * self.rowHeight, text=labelTextList[i], anchor="nw")
            currentOrigin = currentOrigin + (columnWidthList[i] * widthRatio)

    def updateLabelText(self, labelTextList):
        for i in range(len(self.textItems)):
            self.canvas.itemconfig(self.textItems[i], text=labelTextList[i])

    def delete(self):
        # Delete all elements in the row
        for element in self.borderItems:
            self.canvas.delete(element)
        for element in self.textItems:
            self.canvas.delete(element)
