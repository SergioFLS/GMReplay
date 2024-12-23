# Outside packages
import os

# Local packages
from utils import rotate2DArray, listIndicesThatAreTrue

# Constants
import constants as c

def loadMovie(pathToMovieFile):
    ## Take a path to the movie file, return a list of frames, each frame containing a list of inputs

    loadedMovieData = []

    # Return a blank list if file doesn't exist. Probably a new filename for recording.
    if not os.path.isfile(pathToMovieFile):
        return loadedMovieData

    # File exists, load it for reading
    with open(pathToMovieFile, 'rb') as fid:

        while len(fid.read(1)) == 1: # Check if there are bytes to read
            fid.seek(-1,1) # Move the pointer back one byte after the read from the previous line

            # Catch any decoding errors, discard that frame's data, and break
            try:
                # Start parsing, should be a total of 3034 bytes of data
                lastChar = fid.read(2).decode('utf-16')

                inputString = ['']*1025
                for i in range(1025):
                    inputString[i] = fid.read(2).decode('utf-16')

                lastKey = int.from_bytes(fid.read(4), 'little')

                currentKey = int.from_bytes(fid.read(4), 'little')

                keyDown = [False]*256
                for i in range(256):
                    keyDown[i] = (int.from_bytes(fid.read(1)) != 0)
                keyDown = listIndicesThatAreTrue(keyDown) # This lists all indices where the corresponding elements are true

                keyReleased = [False]*256
                for i in range(256):
                    keyReleased[i] = (int.from_bytes(fid.read(1)) != 0)
                keyReleased = listIndicesThatAreTrue(keyReleased)

                keyPressed = [False]*256
                for i in range(256):
                    keyPressed[i] = (int.from_bytes(fid.read(1)) != 0)
                keyPressed = listIndicesThatAreTrue(keyPressed)

                lastButton = [0]*10
                for i in range(10):
                    lastButton[i] = int.from_bytes(fid.read(4), 'little') != 0
                lastButton = listIndicesThatAreTrue(lastButton)

                currentButton = [0]*10
                for i in range(10):
                    currentButton[i] = int.from_bytes(fid.read(4), 'little') != 0
                currentButton = listIndicesThatAreTrue(currentButton)

                buttonDown = [[False]*3]*10
                for i in range(10):
                    for j in range(3):
                        buttonDown[i][j] = (int.from_bytes(fid.read(1)) != 0)

                buttonReleased = [[False]*3]*10
                for i in range(10):
                    for j in range(3):
                        buttonReleased[i][j] = (int.from_bytes(fid.read(1)) != 0)

                buttonPressed = [[False]*3]*10
                for i in range(10):
                    for j in range(3):
                        buttonPressed[i][j] = (int.from_bytes(fid.read(1)) != 0)

                wheelUp = [False]*10
                for i in range(10):
                    wheelUp[i] = (int.from_bytes(fid.read(1)) != 0)
                wheelUp = listIndicesThatAreTrue(wheelUp)

                wheelDown = [False]*10
                for i in range(10):
                    wheelDown[i] = (int.from_bytes(fid.read(1)) != 0)
                wheelDown = listIndicesThatAreTrue(wheelDown)

                mousePos = fid.read(8).hex() # TODO: is this data actually used?

                mouseX = int.from_bytes(fid.read(4), 'little')

                mouseY = int.from_bytes(fid.read(4), 'little')

                thisFrameData = [lastChar, inputString, lastKey, currentKey, keyDown, keyReleased, keyPressed,\
                                 lastButton, currentButton, buttonDown, buttonReleased, buttonPressed,\
                                 wheelUp, wheelDown, mousePos, mouseX, mouseY]

                loadedMovieData += [thisFrameData]

            except UnicodeDecodeError:
                print("Decode error. Final frame data was incomplete and has been discarded.")
                break

    return loadedMovieData


def saveMovie(pathToMovieFile, loadedMovieData):
    ## Take a path to the movie file and the loaded data from loadMovie(), and save the data into the movie file, overwriting the file

    return 0


def getColumnsList(loadedMovieData):
    ## Returns the columns that are actually used, excluding MousePos

    # First break down lists for each input
    # rotatedMovieData = rotate2DArray(loadedMovieData)

    # inputsList = []
    # for element in rotatedMovieData:
    #     if isinstance(element[0], list):
    #         subelementList = []
    #         for subelement in element:
    #             subelementList += [reduceBitwiseOr(subelement)]
    #         inputsList += [reduceBitwiseOr(subelementList)]
    #     else:
    #         inputsList += [reduceBitwiseOr(element)]

    # return inputsList

    # TODO: Properly parse inputs to remove empty columns
    return c.DEFAULT_COLUMNS_LIST # Just return the default (show every column) for now
