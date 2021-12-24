# file organization

linux-autosetup.py
    option handling
        option idea: "check_test" script or something, which checks validity of config (not of commands; not sure
                      if that would even be possible)
    script information
    prompt user to set all directory/sub-directory permissions as read-only or pass an option
        to the script to run without these permissions set
    prompt user to run with root permissions if not root when entering autosetup

pack.py
    module that hosts all pack stuff

config_parser.py
    installs yaml if it isn't installed and then imports it
    parses config and provides proper arguments to create pack objects

config.yaml
    yes


# QoL ideas

- print "last updated" config time at beginning

- X how to combine same-based distros?
 using TAGS, associating a distro with others. the list of distros specified can be iterated through in order, to find entries in these other distros instead if the current one does not have an entry.

- strict config reading? if there's an entry not recognized, should it be notified to the user? probably, right?


# X group handling - "groups" should be fine, but how to include in config?

should groups be in a separate config file?

```---``` can be used to technically separate config files somehow - might be useful?

or, should groups be a field in each "app"/"archive" object that
can be added instead? sounds like a decent idea, but don't like
the repetitive nature of having to write group names multiple times - could
be prone to errors which can't really be handled by the script

OR, what if "groups" was a reserved config file entry that holds all the groups!?!?!? genius

HOWEVER, this still kind of has repetitiveness in it, with maybe needing to add an app/archive
to more than one group, BUT still might be preferred due to it being actually possible
to detect and debug



# OLD #


~~# X handling backup methods~~

~~right now backup types are hardcoded enums, which makes it difficult to expand if someone wants to use different methods~~

~~maybe use functional enums?~~

yaml format could look something like:
```yaml
backup_type:
    COPY:
        BACKUP:
        EXTRACT:
    COMPRESS:
        BACKUP:
        EXTRACT:
. . .
pack:
    ubuntu:
        backup_type: COPY
        # OR
        backup_type:
            CUSTOM:
                BACKUP: different command
                EXTRACT: other command
            # overlap with default backup types should probably be disallowed/provide warning to avoid confusion
. . . INSTEAD!!?? how about this -
backup_type:
    COPY:
        . . .
    . . .
    CUSTOM_HERE:
        BACKUP: . . .
```


~~# possibility of expired sudo?~~

if a cmd string contains multiple commands with sudo, sudo might expire without another prompt to enter in.
is this handled by Popen.communicate? is it persisent, or only does it once?

if it's not persistent, maybe have to run the subprocess as root somehow; maybe ```sudo bash ...```
https://stackoverflow.com/questions/61363152/how-to-open-process-with-root-privileges-using-subprocess-popen

OR another way to handle this could be to set sudo timeout to be infinite: 
https://askubuntu.com/questions/155791/how-do-i-sudo-a-command-in-a-script-without-being-asked-for-a-password


~~# X how to tell whether install_cmd should be run?~~

install_cmd could be anything which may or may not run regardless of whether there are apps,
e.g. install_cmd = 'systemctl enable some-thing'
while apps is empty, but this should still be run

WHAT IF - users are forced to specify install_cmd if they want to use it? if apps are given,
automatically insert install_cmd if one isn't given

but... global install_cmd could be some weird thing that user would want applied, although
that case could just be handled by the user

rename install_cmd to app_install_cmd?

then, the app thing is guaranteed, and we can instead use injection or whatever method to work around this
in new install_cmd? or called something else?

```custom_install_cmd``` and ```custom_backup_cmd``` could be used, paired with injection substitution
e.g.
```yaml
app_install_cmd: sudo apt install $apps
custom_install_cmd: |
    do some come command here before app_install_cmd
    some more
    $app_install_cmd <- gets substituted with above
    more commands
```


~~# X how should whitespaces, etc. be handled?~~
need a consistent, clear, and easy system for handling edge cases
e.g. filename ```  file-with-2-spaces-in-front.a``` or ```"fil;'e"```

```shlex``` module will help a lot with creating compatible strings


~~## X big issue to figure out - overall design of objects and organization of data~~

switching config files should be relatively easy, BUT i think
config file switches should be meant for sharing configs
between people if the need arises, not because a different os is going to be used

global options? as in, maybe certain "apps" have file locations that are the
same for most distros, so global will be used if distro-specific
is not provided.

DRAFT OF CONFIG DESIGN
currently written in yaml, which will probably be the one
quite nice
draft can be found in test_config.yaml


~~# sudoing endeavour & running stuff~~

if fed a list with shell=True, Popen treats the first arg as the command and the rest as args to the shell so backup
functions could work very similarly to how the original bash script did it


this time will (partially) ignore minor security concerns, but once again:

running entire script as sudo:
requires commands that aren't run as sudo to be reduced to not run as sudo.
or not?
option of either:
    requiring sudo -u USER to be specified (which i don't like), OR
    - appending 'sudo -u %s' % os.getlogin() or similar to the start of every line 
      when running commands
      drawback? - how to handle potential lines with commands separated with ';'
        ~~can be handled by (roughly) finding shlex.split() with last ';' and excluding those with quotes after them in cmd~~
        ~~might just require commands be written as multi-line~~
        ~~shlex has a way to make this very easy! puncuation_chars=True will have ';' be an element in list if present~~

NO RUN ENTIRELY AS SUDO!!!
no need for sudo loop, or saving password; nothing like that!
just create```sudo -v``` subprocesses throughout the script to refresh! Runner (name pending?) WILL be another class,
 in which there will be a validate() method that will simply require the coder to guarantee a ```sudo -v```
 at least once every... 5 minutes. if user has to deal with a prompt due to error or something, do a
 validation immediately after instead of refreshing while script waits.
user could also be prompted at beginning for what user they want the script to act as.


~~# Vars~~

probably won't do local inheriting or anything like that with this - unnecessarily complex


~~# SPLIT UP INSTALL/BACKUP settings?~~

allows for enabling/disabling functionalities much easier
faster exiting out of methods, cleaner-looking ```__str__```

where does error_handling go? should it be removed? maybe instead of handling any errors in between,
try to handle all cases at the very beginning or end of functions, e.g. make sure backup functions
are working correctly by testing on test file, and try to scan all things before starting backup/install to
catch any potential errors and notify user beforehand.

verbosity can be solved by...?
problem right now: want to avoid displaying backup/install settings if they are not going to be used - is that possible?

backup settings i think can be solved by this splitting... but what about install? is there a reasonable place
for them to be put?

if i do this, is substitution still reasonable?

this is all because i want to make substitution easier...

substitution should go in this order:
1. check settings?
2. check vars, which should have vars updated locally from global vars

see test_config


~~# X how to handle installing backups in between installation??~~

easiest way would probably be to do string substitution, checking for keyword like INSTALL_BACKUPS
this does mean that some rewriting might have to be done to make this possible, since install_cmd would have to become
a list of lines rather than a single string in order to find the keyword
maybe not much rewriting though, since i can always recombine them with ```'\n'.join(list)```

INJECT dictionary, containing keywords that will be substituted for


~~# X is it necessary to split "apps" and "archives"?~~

answer right now is no; however, i'm not quite sure yet what to name this
entity in that case

~~maybe name them "groups"?~~
media?
entity?
blob?
material?
package??

package or blob might be fitting
leaning towards packages
packs?


~~# X how will config files be used?~~

https://martin-thoma.com/configuration-files-in-python/
above link has some ideas.
json, actual .py with vars and whatnot, yaml?, ini
yaml might be an interesting one
or maybe ini?

~~# X handling sudo - how can this be improved?~~
i want to try as hard as possible to not require running
script as sudo, which should also simplify problems
with commands that should be run as user

IF I HAVE TO run entire script as sudo, some workarounds/solutions are:
after checking running as root etc., check if $SUDO_USER exists - if exists,
set a ```user``` variable as that. if not, set the variable to "root"
then, append every os command with ```"sudo -u " + user```

alternative to ```sudo```? maybe not need to worry about this though

```os.getlogin()``` can be used to find appropriate username
does this handle all cases?
what if user wants to, say, use this as an arch install script? or should that be out of this scope?
i think this case in particular can be ignored, as it can be handled by... other actual install scripts like archinstall.
in that case, i think this should work for a user regardless of whether the user is root or not, as long as the
script is run as root...

CASE 1: run script entirely as sudo
```os.execvpe('sudo', ['sudo', sys.executable] + sys.argv, os.environ)```
```USER = os.getlogin()```
```sudo -u USER```

```
p = Popen('sudo -S -u ' + os.getlogin() + ' ' + args, stdin=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
out, error = p.communicate(PASSWD + '\n')
p.wait()
```

CASE 2: run script as user
```
import getpass
from subprocess import Popen

PASSWD: str
def get_valid_passwd():
    global PASSWD
    if os.getuid() != 0:
        PASSWD = getpass.getpass("Enter a password: ")
        p = Popen('sudo -Slk &> /dev/null <<< "%s"' % PASSWD, shell=True)
        p.communicate(PASSWD + '\n')
        if p.returncode != 0:
            print('error validating password')
            exit(1)


def run(cmd: str) -> int:
    if cmd.split(' ')[0].strip() == 'sudo':
        runner = Popen(cmd.replace('sudo', 'sudo -Sk'), stdin=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        runner.communicate(PASSWD + '\n')
    else:
        runner = Popen(cmd, universal_newlines=True, shell=True)
        runner.wait()
    return runner.returncode
```

it seems... i have found a way to do NOT running with sudo.


~~# X handling passing arguments from python to bash - how to fix bad characters and whitespaces separating strings?~~

mention in documentation that paths in config must be properly escaped and should function normally in bash
arguments should be surrounded in single-quotes, with any apostrophes replaced with ```'\\''```:
    e.g.
    the following would be done in bash:
    ```encrypt "/some/directory here/it's a me"```
    and should look something like this in python:
    ```
    arg1 = "'/some/directory here/it'\\''s a me'"
    os.system("encrypt " + arg1)
    ```


~~# X how will running bash commands from python work?~~

os.system will be helpful

should be as simple as that, as long as handling sudo problem is taken care of

