# Glideline
Optimizes Elytra movement for Celeste. Extremely early beta for the time being. It's a CLI because I can't make tkinter windows. It can still open additional windows when necessary, but nothing extravagant.

# Usage
If you're on windows, simply run the `run.bat` provided. It'll create a python venv (virtual environment) in order to avoid installing the requirements to global.

If you're not on windows, then idk gl ig 

# Roadmap
Make a TKinter interactive application in order to optimize elytra movement. This is solely for *upwards* movement, as downwards movement is extremely simple to optimize. If you are unsure about how to optimize downwards movement or how elytra optimizations work in general, please read [this document](https://docs.google.com/document/d/1xFF6wjdig5k9vOUF3mAvvWh4pF2HBvOw5PJ-aCNNeTo) which covers everything elytra.

The elytra is incredibly complicated to optimize and no definite "guaranteed faster" solutions have been found. If you know of a way to guarantee a fast path, please dm `megamaz` on discord.

### Planned Features
- A small screen to show predicted flight path (and other interesting info)
- Brute-force fine-tuning
- Planned commands:
  - `flight-path` Shows the flight path in a separate window.
  - `optimize` (duh)
  - `copy-inputs` Copies inputs directly to clipboard for insertion into studio.
  - `wiggle-method` Which optimized wiggle method to use. For more info on what this means, [visit the doc.](https://docs.google.com/document/d/1xFF6wjdig5k9vOUF3mAvvWh4pF2HBvOw5PJ-aCNNeTo).
  - `wiggle-settings` Modifies manual wiggle settings.
  - 