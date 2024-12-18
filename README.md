# GMReplay
## A program for creating tool-assisted replays of Windows-based GameMaker games from GameMaker: Studio 1 or later.

GMReplay is a program for creating tool-assisted replays of Windows GameMaker games, intended for games that cannot be run on Linux. For GameMaker games that have native Linux versions or VM GameMaker games that can be ported to Linux, check out [libTAS](https://github.com/clementgallet/libTAS).

GMReplay relies on the built-in playback and recording features present in GameMaker games for frame-accurate input playback regardless of the Windows timing inaccuracies that otherwise cause difficulty with building conventional TAS tools for Windows games.

GMReplay is currently in development. See the below roadmap for future plans.

## Roadmap
**Phase 1 - Minimum implementation (Complete)**
- [X] Realtime recording and playback
- [X] Interactive command-line interface
- [X] Support for keyboard_check_direct and mouse inputs
- [X] Patch out randomize() for deterministic RNG

**Phase 2 - Piano roll interface (Not started)**
- [ ] Piano roll interface
- [ ] Custom input file parsing

**Phase 3 - Function hooking (Not started)**
- [ ] randomize hooking
- [ ] keyboard_check_direct hooking
- [ ] Mouse controls via function hooking
- [ ] Switch between recording and playback

**Phase 4 - Game loop hooking (Not started)**
- [ ] Frame advance
- [ ] Fast forward
- [ ] Time-based rng seeding

**Phase 5 - Tool-assisted replay minimum feature set from [TASVideos](https://tasvideos.org/Emulatorresources/Requirements) (Not started)**
- [ ] Savestates
- [ ] Encoding
- [ ] Time measurement
- [ ] Rerecord count
- [ ] Audio hooking and sync

**Phase 6 - Functional parity with libTAS (Not started)**
- [ ] Annotations/authors/subtitles
- [ ] System time modification
- [ ] On-screen display of inputs, frames, etc.

## How to use

Because this is in early development, it may not be feature-complete or user-friendly yet. To run GMReplay, you first need Python (3.10 or higher version).

Then, download and run gmreplay.py. This will open a command-line interface, where you can either start a recording or play back a recording.

After selecting an option, GMReplay will prompt you to choose the exe file for the game (GameMaker Studio 1 games or later), the data.win (if applicable), and the .gmr replay file.

Once your selections have been made, GMReplay will attempt to create a patched version of the exe file. This is stored separately from the exe file you selected. The patch enables mouse inputs, fixes an issue with certain keyboard functions, and forces deterministic RNG.

After the patching process, the game will open and recording or playback will begin. There are currently no speed controls, so the recordings are all done in realtime.

## Issues

If you encounter any issues, please submit an issue on Github with the **game's name and version**, **GMReplay's version**, and **steps to reproduce** the issue.
