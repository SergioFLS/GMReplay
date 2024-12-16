import subprocess
import tkinter.filedialog
import os


VERSION_NUMBER = "v0.0.2"


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

    # Ask for a path to the recording next
    moviePrompt = "Please select the movie file"
    print(moviePrompt)
    pathToRecording = browseFile(moviePrompt, selection == 2, extensions=[("GMReplay files", "*.gmr"), ("All files","*.*")], defaultExtension="*.gmr")

    # Run the game with the record command
    subprocess.run([pathToExe, ("-record" if selection == 1 else "-playback"), pathToRecording])


def browseFile(promptText, fileExists, extensions=[("All files","*.*"), ("GMReplay files", "*.gmr"), ("Executable files", "*.exe")], defaultExtension="*.gmr"):
    ## Wrapper for tkinter filedialog

    # Create a fake window (replace with real window when GUI is implemented)
    root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window

    # Get the file path, starting in the working directory
    cwd = os.getcwd()
    ret = tkinter.filedialog.askopenfilename(parent=root, initialdir=cwd, title=promptText, defaultextension=defaultExtension, filetypes=extensions) if fileExists else \
        tkinter.filedialog.asksaveasfilename(parent=root, initialdir=cwd, title=promptText, defaultextension=defaultExtension, filetypes=extensions)

    # Destroy the tkinter window
    root.destroy()

    return ret


if __name__ == '__main__':
    main()
