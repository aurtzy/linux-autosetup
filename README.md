# stowup
Apply a dotfiles backup strategy to your entire setup!

stowup is a backup program with functionalities inspired by GNU Stow. It uses restic as a backend
which makes it feasible for backing up more than just dotfiles, and it allows for containerization
of backups, centralizing repositories that can be individually installed or backed up on any machine.

It is built mainly to complement the use of GNU Stow, but it is not required for this program to function on its own.

I started this project with the following goals in mind:
- Offline backups
- Portability
- Allowing options with what to back up or install

# Development

This software uses `restic (insert hyperlink here)` as a backend, but the stowing code does not rely on it at all,
which makes it (hopefully) relatively easy to switch out for other programs if that is desired.

## Dependencies

...