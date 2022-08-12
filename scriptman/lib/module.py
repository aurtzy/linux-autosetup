import logging
import os
import stat
import subprocess
from pathlib import Path

from .configparser import ConfigParser
from .logger import log

# Runtypes are generic. Modify to your liking.
# Any name can be used without breakage as long as they don't overlap with other operation names (or any config names if
# you're expecting to run config file types like .yaml). An exception is raised if operations overlap.
runtypes = ('install', 'backup', 'run')


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

    class Settings:
        """Represents settings for a runtype of a Module."""

        def __init__(self, **kwargs):
            self.condition = ConfigParser.assert_tp(kwargs, 'condition', str, 'True')
            self.deps = tuple(map(ModuleID, ConfigParser.assert_tp(kwargs, 'deps', list)))
            self.optional: bool = ConfigParser.assert_tp(kwargs, 'optional', bool)
            self.addons = tuple(map(ModuleID, ConfigParser.assert_tp(kwargs, 'addons', list)))
            self.secrets = tuple(map(str, ConfigParser.assert_tp(kwargs, 'secrets', list)))

    def __init__(self, mod_id: ModuleID, **kwargs):
        self.settings: dict[str, Module.Settings] = {}
        settings = ConfigParser.assert_tp(kwargs, 'settings', dict)

        for runtype in runtypes:
            self.settings[runtype] = self.Settings(**ConfigParser.assert_tp(settings, runtype, dict))
        self.id = mod_id
        self.desc = ConfigParser.assert_tp(kwargs, 'desc', str, default='No description provided.')

    def info(self, verbose: bool):
        """Returns information about the module."""
        raise NotImplementedError('outdated info calls')  # todo: outdated
        info = [f'{self.id}', f'{self.desc}']
        if verbose:
            for runtype in runtypes:
                if deps_req := self.deps[runtype]['req']:
                    info.append(f'Required {runtype} dependencies ({len(deps_req)}): {deps_req}')
                if deps_opt := self.deps[runtype]['opt']:
                    info.append(f'Optional {runtype} dependencies ({len(deps_opt)}: {deps_opt}')
            if self.secrets:
                info.append(f'Secrets ({len(self.secrets)}): {self.secrets}')
        return '\n\t'.join(info)

    def __eq__(self, other):
        if isinstance(other, Module):
            return self.id == other.id
        else:
            raise NotImplementedError


class ModuleCollection:
    """Stores a collection of modules that can be accessed."""

    def __init__(self):
        self._modules: dict[ModuleID, Module] = {}

    def add(self, path: str | os.PathLike):
        """
        Initializes and adds module corresponding to the given path if it does not exist.

        Raises a FileNotFoundError if the path is not a valid module. A module is valid if the given path's parent
        directories as well as itself contains a module config, not including the root modules directory.

        Raises an AssertionError if incorrect types are discovered in the config.
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

        try:
            settings = ConfigParser.load(mod_id.joinpath(ConfigParser.MODULE_CFG))
            log(logging.DEBUG, f'{mod_id} raw settings: {settings}')
        except AssertionError:
            log(logging.CRITICAL, f'Error discovered in the {mod_id} config.')
            raise
        self._modules[mod_id] = Module(mod_id, **settings)

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
        settings = runner.coll.get(mod_id).settings.get(runner.runtype)

        if mod_id in runner.rejected_mods:
            raise RejectedModuleError(mod_id)
        elif not (self._eval_condition(settings.condition)):
            if mod_id in runner.explicit_mods:
                # todo: prompt user whether user should continue - mod was explicit, but did not satisfy condition.
                ...
            else:
                runner.reject_mod(mod_id)
                raise RejectedModuleError(mod_id)

        if runner.withdeps:
            # todo: this is where handling of the module exception will be, since this will be dealing with dependencies.
            #  the general idea is this => for each dep, try to process, keeping only the ones that can be processed.
            #  for each of these, create a ModuleRunnerNode as done before. however, IF there is an exception while
            #  creating that node, check if it was optional. if True, then move on - that module will be processed,
            #  but not added. if False, then re-raise and reject_mod.
            # todo: another issue related to module rejection
            #  this still doesn't solve the case where other dependencies were successfully processed, but have to
            #  then be discarded due to a parent being rejected as a result of another rejected depenedency.
            if deps_loop := dependents.intersection(settings.deps):
                log(logging.CRITICAL, f'Discovered infinite dependency loop! {mod_id} '
                                      f'depends on and is a dependency of: {deps_loop}')
                raise RecursionError
            log(logging.DEBUG, f'Initializing deps: {settings.deps}')
            self.deps = [ModuleRunnerNode(runner, dep_id, dependents.union({mod_id}))
                         for dep_id in settings.deps]

        # todo: addons
        self.addons: list[ModuleRunnerNode] = ...

        # todo: secrets

        self.runner = runner
        self.id = mod_id
        self.secrets = None

    def run(self):
        """Run corresponding runtype scripts for the module and dependencies/addons, if there are any."""
        for dep in self.deps:
            log(logging.DEBUG, f'Running dependency {self.id}...')
            dep.run()

        file = self.id.joinpath(self.runner.runtype)
        if file.is_file():
            log(logging.INFO, f'Executing {self.id} {self.runner.runtype} script...')
            # todo: rework to work with new extension system
            # set (and reset after running) file permissions to temporarily allow file execution in case it is not enabled
            orig_perms = os.stat(file).st_mode
            os.chmod(file, os.stat(file).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            subprocess.run(file, input=None)  # todo: input
            os.chmod(file, orig_perms)
        else:
            log(logging.INFO, f'No {self.runner.runtype} script found for {self.id} - skipping...')

        for addon in self.addons:
            log(logging.DEBUG, f'Running addon {self.id}...')
            addon.run()

    def _clear(self):
        for addon in self.addons:
            addon._clear()
        log(logging.DEBUG, f'Clearing module {self.id}...')
        self.runner.clear_mod(self.id)
        for dep in self.deps:
            dep._clear()

    def _cond_success(self, expr: str):
        ...

    def _cond_prompt(self):
        ...

    def _eval_condition(self, condition):
        """
        Evaluates a user-defined condition written in Python that should be True for the module to run.

        The eval() namespace is limited to only methods from this class that start with "_cond_". This prefix is
        automatically filtered, so "prompt()" would be used instead of "_cond_prompt()" for the user.
        """
        method_names = filter(lambda name: name.startswith('_cond_'), dir(self))
        methods = {name.removeprefix('_cond_'): getattr(self, name)
                   for name in method_names}
        return eval(condition, methods)


class ModuleRunner:
    """Wrapper for creating ModuleRunnerNode instances."""

    def __init__(self, coll: ModuleCollection, runtype: str, extensions: dict[str, list[str]], *mod_ids: ModuleID,
                 confirm: bool = True, withdeps: bool = True):
        log(logging.DEBUG, f'Initializing ModuleRunner: {{{coll}, {runtype}, {mod_ids}, {confirm}, {withdeps}}}')
        self.coll = coll
        self.runtype = runtype
        self.extensions = extensions
        self.confirm = confirm
        self.withdeps = withdeps

        self.runners: list[ModuleRunnerNode] = []
        self.explicit_mods: set[ModuleID] = set(mod_ids)
        self.processed_mods: set[ModuleID] = set()
        self.rejected_mods: set[ModuleID] = set()
        for i, mod_id in enumerate(mod_ids):
            if self.try_process_mod(mod_id):
                self.runners.append(ModuleRunnerNode(self, mod_id, set()))

    def run(self):
        log(logging.DEBUG, 'Running ModuleRunner...')
        for module in self.runners:
            module.run()

    def try_process_mod(self, mod_id: ModuleID):
        """Tries to add to processed_mods. Returns True if it was added, and False if already present."""
        if mod_id not in self.processed_mods:
            self.processed_mods.add(mod_id)
            return True
        return False

    def clear_mod(self, mod_id: ModuleID):
        """Clears a mod from processed_mods if it is present, or does nothing otherwise."""
        self.processed_mods.discard(mod_id)

    def reject_mod(self, mod_id: ModuleID):
        """Adds a module to rejected_mods if it isn't already added."""
        self.rejected_mods.add(mod_id)


class RejectedModuleError(Exception):
    pass
