
# GENERAL IDEA OF HOW SCRIPT WILL RUN
1. Start script, maybe with options

2. Choose a config to parse. If specified in options, use that. Otherwise? - could search
./config and prompt (meant to be portable, so expecting just this dir to be used I think is reasonable).
If noconfirm, then error out with message that config must be specified.

3. Parse config. May or may not prompt for options like directory stuff. If noconfirm, this should be
taken care of.

add an "exceptions" dictionary with the var name and value to assign to. e.g. if --noconfirm was
present, add {'noconfirm': True} to exceptions. while parsing config, if 'noconfirm' key is found,
get overriden with the exception and remove the exception from the exceptions dictionary.

same can be done with other options in the future when needed

4. Start prompting for options: install/backup, packs to perform operations on, etc.? Each
of these options should have a corresponding script argument that can alternatively be used.
If --noconfirm, raise error if even one of these options are missing.

5. Script does its thing! From here everything should be pretty well set.

# get rid of TRY_AGAIN enum - dum?

move error handling enum to system module? since error_handling will still be saved in pack settings,
all it needs is an errorvalue return from calling run() and it'll know what to do from there - if it's PROMPT,
no_confirm could be False, prompting to choose from options. otherwise, return its returnvalue and caller
can handle from there

# COLOR
https://www.geeksforgeeks.org/print-colors-python-terminal/
interesting? plausible?
answer is yes. yes it is. decent logging is now implemented, so color can be
somewhat more easily implemented than thought before.

# braintyphoon ideas

- have some kind of note if user runs immediately as sudo: 
  "Avoid directly running the script as root if you
  are not trying to use root environment variables."
