
# GENERAL IDEA OF HOW SCRIPT WILL RUN
1. Start script, maybe with options

2. Choose a config to parse. If specified in options, use that. Otherwise? - could search
   ./config and prompt (meant to be portable, so expecting just this dir to be used I think is reasonable).
   If noconfirm, then error out with message that config must be specified.

3. Parse config. May or may not prompt for options like directory stuff. If noconfirm, these options
   are automatically chosen.

4. Start prompting for options: install/backup, packs to perform operations on, etc.? Each
   of these options should have a corresponding script argument that can alternatively be used.
   If --noconfirm, raise error if even one of these options are missing.

5. From here, script will run through modules, and everything should be good...?

6. When finished, we can log any packs that failed to be installed/backed up.

# COLOR
https://www.geeksforgeeks.org/print-colors-python-terminal/
interesting? plausible?
answer is yes. yes it is. decent logging is now implemented, so color can be
somewhat more easily implemented than thought before.

# braintyphoon ideas

- have some kind of note if user runs immediately as sudo: 
  "Avoid directly running the script as root if you
  are not trying to use root environment variables."
