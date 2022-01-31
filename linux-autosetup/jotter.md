
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
