import logging
import os
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

    def __fspath__(self):
        return str(self.id)


class Module:
    """Stores information about a module."""

    def __init__(self, mod_id: ModuleID):

        def assert_tp(mapping: dict, key: str, tp, default=None):
            if default is None:
                default = tp()
            try:
                assert isinstance(val := mapping.get(key, default), tp), f'{key} should be a {tp}'
            except AssertionError as error:
                log(logging.ERROR, f'Unexpected type given for dependency settings: {error}')
                raise
            return val

        self.id = mod_id

        settings = ConfigParser.load(mod_id.joinpath(ConfigParser.MODULE_CFG))
        deps = assert_tp(settings, 'deps', dict)
        log(logging.DEBUG, f'{mod_id} settings: {settings}')
        try:
            self.desc = assert_tp(settings, 'desc', str, default='No description provided')
            self.deps_req = list(map(ModuleID, assert_tp(deps, 'req', list)))
            self.deps_opt = list(map(ModuleID, assert_tp(deps, 'opt', list)))
            self.secrets = list(map(str, assert_tp(settings, 'secrets', list)))
        except Exception:
            log(logging.ERROR, f'Error discovered in the {mod_id} config.')
            raise

    def info(self, verbose: bool):
        """Returns information about the module."""
        info = '\n\t'.join([f'{self.id}',
                            f'{self.desc}'])
        if verbose:
            info = '\n\t'.join([info,
                                f'Required dependencies ({len(self.deps_req)}): {self.deps_req}',
                                f'Optional dependencies ({len(self.deps_opt)}): {self.deps_opt}',
                                f'Secrets ({len(self.secrets)}): {self.secrets}'])
        return info

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


class ModulesRunner:
    """Stores modules to execute on a specific runtype."""

    def __init__(self, coll: ModuleCollection, runtype: str, *mod_ids: ModuleID, withdeps: bool = True,
                 confirm: bool = True, added: set[ModuleID] = None, dependents: set[ModuleID] = None):
        if added is None:
            added = set()
        if dependents is None:
            dependents = set()

        self.runtype = runtype
        self.modules: list[ModuleID] = []
        self.deps: list[ModulesRunner] = []

        for mod_id in mod_ids:
            if mod_id not in added:
                self.modules.append(mod_id)
                added.add(mod_id)
                if withdeps:
                    deps = []
                    if req := coll.get(mod_id).deps_req:
                        deps += req
                    # If confirm is disabled, don't run any optional dependencies. Forcing optionals to be run
                    # makes it more difficult to install only required packages. If they are ignored by
                    # default, users can just explicitly include them in arguments.
                    if opt := coll.get(mod_id).deps_opt and confirm:
                        # todo
                        pass
                    if deps:
                        if dep_loop := dependents.intersection(deps):
                            log(logging.CRITICAL, f'Discovered infinite dependency loop! {mod_id}'
                                                  f'depends on and is a dependency of: {dep_loop}')
                            raise RecursionError
                        self.deps.append(ModulesRunner(coll, runtype, *deps, withdeps=withdeps, confirm=confirm,
                                                       added=added, dependents=dependents.union({mod_id})))

    def pre_run(self):
        """This method serves as a preliminary setup method before running modules, particularly for prompts."""
        # todo
        pass

    def run(self):
        """Run the corresponding scripts for modules."""
        # todo
        pass
