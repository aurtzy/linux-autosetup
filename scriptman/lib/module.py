import logging
import os
import stat
import subprocess
from pathlib import Path

from .configparser import ConfigParser
from .logger import log


class ModuleID(os.PathLike):
    """Wrapper class for module ID strings."""

    def __init__(self, path: str | os.PathLike):
        try:
            self.id = Path(os.path.abspath(path)).relative_to(Path(os.path.abspath('.')))
        except ValueError:
            log(logging.CRITICAL, 'Could not interpret the following path - not present in modules root directory:'
                                  f'{path}')
            raise

    def joinpath(self, path):
        """Joins id path with the provided path argument."""
        return self.id.joinpath(path)

    def __eq__(self, other):
        if isinstance(other, ModuleID):
            return self.id == other.id
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)

    def __fspath__(self):
        return str(self.id)


class Module:
    """Stores information about a module."""

    # Generic runtypes. Any name can be used without breakage as long as they don't overlap with
    # other operation names (or module-specific filenames like mod.yaml).
    RUNTYPES = ('install', 'backup', 'run')

    def __init__(self, mod_id: ModuleID):
        self.id = mod_id

        try:
            settings = ConfigParser.load(mod_id.joinpath(ConfigParser.MODULE_CFG))
        except FileNotFoundError as error:
            log(logging.CRITICAL, f'Module {mod_id} is not valid! No config was found.')
            raise
        log(logging.DEBUG, f'{mod_id} settings: {settings}')
        try:
            self.desc = self.assert_tp(settings, 'desc', str, default='No description provided.')
            self.deps: dict[str, dict[str, list]] = {}
            deps = self.assert_tp(settings, 'deps', dict)
            for runtype in self.RUNTYPES:
                deps_runtype = self.assert_tp(deps, runtype, dict)
                self.deps.update({runtype: {dep_tp: list(map(ModuleID, self.assert_tp(deps_runtype, dep_tp, list)))
                                            for dep_tp in ('req', 'opt')}})
            self.secrets = list(map(str, self.assert_tp(settings, 'secrets', list)))
        except Exception:
            log(logging.ERROR, f'Error discovered in the {mod_id} config.')
            raise

    def info(self, verbose: bool):
        """Returns information about the module."""
        info = [f'{self.id}', f'{self.desc}']
        if verbose:
            for runtype in self.RUNTYPES:
                if deps_req := self.deps[runtype]['req']:
                    info.append(f'Required {runtype} dependencies ({len(deps_req)}): {deps_req}')
                if deps_opt := self.deps[runtype]['opt']:
                    info.append(f'Optional {runtype} dependencies ({len(deps_opt)}: {deps_opt}')
            if self.secrets:
                info.append(f'Secrets ({len(self.secrets)}): {self.secrets}')
        return '\n\t'.join(info)

    @staticmethod
    def assert_tp(mapping: dict, key: str, tp, default=None):
        """Asserts that a setting is of some type and return it, or a default value if it does not exist."""
        if default is None:
            default = tp()
        try:
            assert isinstance(val := mapping.get(key, default), tp), f'{key} value should be a {tp}'
        except AssertionError as error:
            log(logging.ERROR, f'Unexpected type given for settings: {error}')
            raise
        return val

    def __eq__(self, other):
        if isinstance(other, Module):
            return self.id == other.id
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.id)


class ModuleCollection:
    """Stores a collection of modules that can be accessed."""

    def __init__(self):
        self._modules: dict[ModuleID, Module] = {}

    def add(self, path: str | os.PathLike):
        """
        Initializes and adds module corresponding to the given path if it does not exist.

        Raises a FileNotFoundError if the path is not a valid module. A module is valid if the given path's parent
        directories as well as itself contains a module config, not including the root modules directory.
        """
        mod_id = (ModuleID(path) if not isinstance(path, ModuleID) else path)
        if isinstance(self._modules.get(mod_id), Module):
            log(logging.DEBUG, f'Module "{mod_id}" already exists - no need to add.')
            return
        log(logging.DEBUG, f'Adding Module "{mod_id}" to collection.')

        # Walk parent directories to modules root to check validity.
        for parent_id in map(ModuleID, mod_id.id.parents[:-1]):
            if parent_id in self._modules:
                break
            elif (cfg_path := parent_id.joinpath(ConfigParser.MODULE_CFG)).exists():
                self._modules[parent_id] = ...
                continue
            else:
                log(logging.ERROR, f'Tried to add module "{parent_id}", but could not find module config: {cfg_path}')
                for fix_id in map(ModuleID, mod_id.id.parents[:-1]):
                    # Preserves validity of modules in _modules, although I'm not sure when this will ever be useful.
                    self._modules.pop(fix_id)
                    if fix_id == parent_id:
                        break
                raise FileNotFoundError(cfg_path)

        self._modules[mod_id] = Module(mod_id)

    def get(self, path: str | os.PathLike):
        """
        Gets module corresponding to the given path.

        If it does not exist, module will be added before returning it.
        """
        mod_id = (ModuleID(path) if not isinstance(path, ModuleID) else path)
        if not isinstance(self._modules.get(mod_id), Module):
            self.add(mod_id)
        return self._modules[mod_id]


class ModuleRunnerNode:
    """Tree node that enables executing a module script runtype and its dependencies."""

    def __init__(self, runner: "ModuleRunner", mod_id: ModuleID, dependents: set[ModuleID]):
        self.deps = []
        if runner.withdeps:
            dep_ids = list(filter(self._try_add_processed, runner.coll.get(mod_id).deps[runner.runtype]['req']))
            # If confirm is disabled, don't run any optional dependencies. Forcing optionals to be run
            # just makes it more difficult to run only required module scripts. If they are ignored by
            # default, users can just explicitly include them in arguments. May consider a "--(no)forcedeps" option
            # of some kind in the future to force run/ignore opt deps if it looks like it might actually be useful.
            if runner.confirm:
                for dep_opt in filter(self._try_add_processed, runner.coll.get(mod_id).deps[runner.runtype]['opt']):
                    # todo
                    #  if dep_opt is in explicit_mods, skip prompt and auto-add. if not in explicit_mods, prompt.
                    ...

            if dep_ids:
                if deps_loop := dependents.intersection(dep_ids):
                    log(logging.CRITICAL, f'Discovered infinite dependency loop! {mod_id}'
                                          f'depends on and is a dependency of: {deps_loop}')
                    raise RecursionError
                log(logging.DEBUG, f'Initializing deps: {dep_ids}')
                self.deps = [ModuleRunnerNode(runner, dep_id, dependents.union({mod_id})) for dep_id in dep_ids]

        # todo: secrets

        self.runner = runner
        self.id = mod_id
        self.secrets = None

    def _try_add_processed(self, dep):
        """Tries to add to processed_mods in runner. Returns True if it was added, and False if already present."""
        if dep not in self.runner.processed_mods:
            self.runner.processed_mods.add(dep)
            return True
        return False

    def run(self):
        """Run corresponding runtype scripts for the module and dependencies."""
        for dep in self.deps:
            log(logging.DEBUG, f'Running {self.id} dependency...')
            dep.run()

        file = self.id.joinpath(self.runner.runtype)
        if file.is_file():
            log(logging.INFO, f'Executing {self.id} {self.runner.runtype} script...')
            # set (and reset after running) file permissions to temporarily allow file execution in case it is not enabled
            orig_perms = os.stat(file).st_mode
            os.chmod(file, os.stat(file).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            subprocess.run(file, input=None)  # todo: input
            os.chmod(file, orig_perms)
        else:
            log(logging.INFO, f'No {self.runner.runtype} script found for {self.id} - skipping...')


class ModuleRunner:
    """Wrapper for creating ModuleRunnerNode instances."""

    def __init__(self, coll: ModuleCollection, runtype: str, *mod_ids: ModuleID,
                 confirm: bool = True, withdeps: bool = True):
        log(logging.DEBUG, f'Initializing ModuleRunner: {{{coll}, {runtype}, {mod_ids}, {confirm}, {withdeps}}}')
        self.coll = coll
        self.runtype = runtype
        self.confirm = confirm
        self.withdeps = withdeps

        self.runner_nodes = []
        self.explicit_mods = set(mod_ids)
        self.processed_mods = set()
        for i, mod_id in enumerate(mod_ids):
            if mod_id not in self.processed_mods:
                self.processed_mods.add(mod_id)
                self.runner_nodes.append(ModuleRunnerNode(self, mod_id, set()))

    def run(self):
        log(logging.DEBUG, 'Running ModuleRunner...')
        for module in self.runner_nodes:
            module.run()
