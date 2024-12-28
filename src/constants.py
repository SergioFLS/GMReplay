# Constants to be used globally
MIN_PYTHON = (3, 12)
RECORD = 1
PLAY = 2
GLOBAL_PADDING = 4
DEFAULT_COLUMN_WIDTHS = [8, 8, 30, 7, 9, 8, 11, 10, 10, 12, 15, 15, 15, 10, 10, 10, 10, 10]
INPUT_BORDER_WIDTH = 2
LABEL_RELIEF_TYPE = "ridge"
INPUT_RELIEF_TYPE = "groove"
SCROLLBAR_WIDTH = 10
DEFAULT_ROW_HEIGHT = 20
INPUT_SCROLLABLE_AREA_HEIGHT = 800
INPUT_CANVAS_WIDTH = 1525
INPUT_CANVAS_HEIGHT = 20000
FRAMES_PER_PAGE = 1000

# Strings

# Main program strings
VERSION_NUMBER = "v0.1.3"
STARTUP_STRING = "GMReplay " + VERSION_NUMBER + " by OceanBagel\n"
MIN_PYTHON_STRING = "Python %s.%s or later is required.\n" % MIN_PYTHON

# Patching strings
PATCH_FILE_NAME = "__temp_GMR_patched_runner.exe"
PATCH_START_STRING = "Patching mouse inputs..."
PATCH_MOUSE_FAIL_STRING = "WARNING: Patching encountered an issue. Mouse inputs will not work."
PATCH_MOUSE_SUCCESS_STRING = "Mouse inputs patched successfully."
PATCH_KEYDIRECT_STRING = "Patching keyboard_check_direct()..."
PATCH_KEYDIRECT_FAIL_STRING = "WARNING: Patching encountered an issue. Direct keyboard input will not work."
PATCH_KEYDIRECT_SUCCESS_STRING = "keyboard_check_direct() patched successfully."
PATCH_RANDOMIZE_STRING = "Patching randomize()..."
PATCH_RANDOMIZE_FAIL_STRING = "WARNING: Patching encountered an issue. Randomness will not be deterministic."
PATCH_RANDOMIZE_SUCCESS_STRING = "randomize() patched successfully."
PATCH_SUCCESS_STRING = "Runner patched successfully."

# UI strings
WINDOW_TITLE = "GMReplay " + VERSION_NUMBER
INPUT_WINDOW_SUFFIX = " - Input Editor"
EXE_FILE_PROMPT = "Game executable:"
DATAWIN_FILE_PROMPT = "Game data.win file:"
MOVIE_FILE_PROMPT = "Movie file:"
RECORDING_STRING = "Recording"
PLAYBACK_STRING = "Playback"
START_STRING = "Start"
STOP_STRING = "Stop"
GAME_START_STRING = "Starting the game..."
GAME_STOP_STRING = "Stopping the game..."
GAME_CLOSED_STRING = "Game was closed."
DEFAULT_COLUMNS_LIST = ["lastChar", "inputString", "lastKey", "currentKey", "keyDown", "keyReleased", "keyPressed",\
                       "lastButton", "currentButton", "buttonDown", "buttonReleased", "buttonPressed",\
                       "wheelUp", "wheelDown", "mousePos", "mouseX", "mouseY"]
LOADING_MOVIE_STRING = "Loading movie data..."
UPDATE_INPUT_EDITOR_STRING = "Updating input editor..."
MOVIE_LOADED_STRING = "Movie file loaded."
