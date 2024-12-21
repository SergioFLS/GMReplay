# Outside packages
import sys

# Local packages
from ui import mainWindowClass

# Constants
import constants as c


def main():
    # Init
    print("GMReplay " + c.VERSION_NUMBER + " by OceanBagel\n")

    # Enforce a minimum Python version
    if sys.version_info < c.MIN_PYTHON:
        print("Python %s.%s or later is required.\n" % c.MIN_PYTHON)
        return

    # Initialize tkinter window
    mainWindowObj = mainWindowClass()

    # Execute main loop, broken apart to process stdout from the game window
    while True:
        mainWindowObj.root.update_idletasks()
        mainWindowObj.root.update()

        # Prevent blocking from the game process and print game's stdout to the console
        if mainWindowObj.gameProcess != None:
            for line in mainWindowObj.gameProcess.stdout:
                print(line.decode('utf-8').strip())

            if mainWindowObj.gameProcess.poll() != None: # If it is not none, the game was closed
                mainWindowObj.gameProcess = None # Clear the variable until it's used again
                mainWindowObj.recordPlayRow.movieEnd() # Enable buttons


if __name__ == '__main__':
    main()
