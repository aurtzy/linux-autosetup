# SPECS: stowup
specifications for `stowup`, without the junk notes.

temporary for initial development.


## The Store

### Store options

```yaml
.:
    restic: str, root_default = 'restic', default = inherit
        the restic executable to use.
    src: str; root_default = '/', default = inherit + key value
        custom token to use in directory path instgvh  ead of the value of key, 
        with variable expansion applied (use Template logic from older version).
        this option will not used in repository path.
    options: dict[str, dict[str, str | list]]; root_default = {} (?), default = inherit
        can denote a unique set of options to pass to each command
        when running for repository. probably will only support long options.
    encrypt: dict[str, str]; root_default = {root defaults below}, default = inherit
        type: str; root_default = password
            type of key to use for encryption.
            valid types are 'password', 'file', or 'command'
        id: str | None; root_default = None
            if specified, this is the id that will be used in getting the encryption key
            from environment variables (e.g. STOWUP_PASSWORD_id, STOWUP_PASSWORD_FILE_id).
            if the corresponding env var does not exist, it can be lenient and prompt anyways,
            albeit with a warning - otherwise, if noconfirm is enabled, raise an error.
            this, along with the encrypt setting object itself are used as identifiers for associating
            identical keys.
            if two encrypt setting objects are identical or their ids match (and are not None),
            keys can be associated and only require one prompt
        key: str | None; root_default = None
            specifies the key to use. 
            depending on the type, key can mean different things.
            for 'password', key is that password to use.
            for 'file', key is the file path to use (starting from config dir).
            for 'command', key is the command to run.
        if a key is not specified, the script will check for
        the corresponding env var if id exists; 
        else if noconfirm is disabled, prompt the user;
        else raise an error.
    dest: str | list; root_default = ['.'], default = inherit + new
        the store root locations in which to back up to - multiple can be specified. dest inherits,
        which simply adds to the parent dest list or uses the same list if no new dests are given.
        `os.path.join` is used to combine store roots with repo paths in order to properly
        preserve slashes.
    hooks: dict[str, dict[str, str]]; root_default = {root defaults below}, default = {defaults below}
        cmd: 
            before: str; root_default = None, default = None
            after: str; root_default = None, default = None
            commands to run -in the shell-.
        other_cmd: ...
        allows hooks for all commands, before and after running. no inheritance.

```

### Config file

sample:

```yaml

.:
    restic: ./restic
    src: $HOME
    hooks:
        backup:
            option: true/str/list[str]
        restore:
            option: true/str/list[str]
shelf.configs/:
    main: {}  # these are optional, but may look less weird than dangling key -> nothing pairs in yaml.
    kde-desktop: {}
    gnome-laptop: {}
    updater: {}
shelf.games/:
    minecraft: {}
    terraria: {}
shelf.vital/:
    .:
        encrypted: true
    keepass: {}
    firefox-profile1: {}
    firefox-profile2: {}
    thunderbird-profile1: {}
    some-random-encrypted-thing:
        encrypted: true
            
            
---
# in some other config for root...
.:
    restic: ./restic
shelf.system/:
    main: {}
    updater: {}

```

### Interpreting and parsing store values from the config

Keys may consist of more than one path part.

All key names (not including settings) should be valid paths/directory names.
The following keys are invalid:
- '..'
- anything that begins with a '/'

Directories are indicated by keys that end with '/'.
If a directory contains a key that exactly matches '.', it is interpreted as inheritable settings from that directory.

If '/' is not present at the end of a key, it is interpreted as a repository entry.
Any keys inside the repository dictionary are interpreted as settings for that particular repository.

The store should have zero knowledge on settings, which can be done by using a custom passed fold methods on
the given valid settings for every level encountered, so that each directory has instances of immutable settings
which can be folded into subsequent ones. 

A stack may also help with an iterative, non-recursive approach to parsing the store.


## Subcommands

- `install`: extracts repos and tries to execute the matched script at each root directory specified by /installer.
- `backup`: creates backups in specified repos (or all, if no args are provided) if sources exist.
- `clean`: prunes and compacts the repo(s) (or all, if no args are provided).
- `init`: no options/args. parses the config and walks the expected directories, creating repos that do not exist
  and prompting the user to delete unexpected files (which might have been old repos removed from the config)
- `health`: simple wrapper for `borg check` that accepts no arguments and runs `borg check 
- `break-locks`: break any locks on repositories (or those given).

### Environment variables

the following are useful env vars to consider:
- RESTIC_REPOSITORY
- RESTIC_PASSWORD
- RESTIC_PASSWORD_FILE
- RESTIC_PASSWORD_COMMAND

### the install command

time-frames:
- `--before` and `--after` option for specifying time-frames.
- use the `time` key from `borg list --json` and `datetime` python module for filtering archives.

sample: `borger install --after 2021-01-31T01 --before 2022 some/repo other/repo`

this sample should install the latest possible archive between `2021-01-31T1:01:59:59` and `2022-01-01T00:00:00` 
from `some/repo` and `other/repo`

### the backup command

use `TZ=UTC` when creating backups to avoid overlaps. users can still see local timestamps
when using `borg list`, so that is not a concern.

### the clean command

provide an option that toggles compact.


## Misc notes or TBD where to put

