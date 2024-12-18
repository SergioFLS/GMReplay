# GMReplay
## A program for creating tool-assisted replays of Windows-based GameMaker games from GameMaker: Studio 1 or later.

GMReplay is a program for creating tool-assisted replays of Windows GameMaker games, intended for games that cannot be run on Linux. For GameMaker games that have native Linux versions or VM GameMaker games that can be ported to Linux, check out [libTAS](https://github.com/clementgallet/libTAS).

GMReplay relies on the built-in playback and recording features present in GameMaker games for frame-accurate input playback regardless of the Windows timing inaccuracies that otherwise cause difficulty with building conventional TAS tools for Windows games.

GMReplay is currently in development. See the below roadmap for future plans.

## Roadmap
**Phase 1 - Minimum implementation (Currently in development)**
- [X] Realtime recording and playback
- [X] Interactive command-line interface
- [X] Support for keyboard_check_direct and mouse inputs
- [ ] Patch out randomize() for deterministic RNG

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
