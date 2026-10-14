# Notes for working on this project

@AGENTS.md

`AGENTS.md` (imported above) holds the hardware facts, the rules and the
upload workflow. The skills in `.opencode/skills/` cover the details: touch
sensing, strips, sound and errors. Read the relevant one before changing that
part. Keep facts in those files, not here, so they do not drift apart.

`AGENTS.md` is written for an agent helping the artist. In Claude Code you are
usually working with the developer, so code and technical detail are fine.

Developer-only notes:

- Before using a serial port, check that it really is the board (USB vendor
  id 0x303A). A WCH-Link programmer can also show up as `/dev/ttyACM0`.
  `tools/board.py` checks this itself. `tools/ibserial.py` (copied from
  circuitpython-ideaboard) needs `--port`, because it only finds IdeaBoard
  CH340 ports by itself.
- When you change how the program works, update the matching skill and
  `AGENTS.md` too, because the artist's agent relies on them.
