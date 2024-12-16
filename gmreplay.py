import subprocess


VERSION_NUMBER = "v0.0.1"


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
            case 1 | 2:
                recordOrPlayMovie(selection)
            case 3:
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
    # Ask for a path to the game first
    pathToExe = input("Enter the path to the game's exe file:\n")

    # Ask for a path to the recording next
    pathToRecording = input("Enter the path to the movie file:\n")

    # Run the game with the record command
    subprocess.run([pathToExe, ("-record" if selection == 1 else "-playback"), pathToRecording])


if __name__ == '__main__':
    main()
