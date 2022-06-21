import logging
import os
from pathlib import Path

from .configparser import ConfigParser
from .logger import log


class ModuleID:
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


class Module:
    """Stores information about a module."""

    def __init__(self, modid: ModuleID):

        def assert_tp(mapping: dict, key: str, tp, default=None):
            if default is None:
                default = tp()
            try:

                assert isinstance(val := mapping.get(key, default), tp), f'{key} should be a {tp}'
            except AssertionError as error:
                log(logging.ERROR, f'Unexpected type given for dependency settings: {error}')
                raise
            return val

        self.modid = modid

        settings = ConfigParser.load(modid.joinpath(ConfigParser.MODULE_CFG))
        deps = assert_tp(settings, 'deps', dict)
        log(logging.DEBUG, f'{modid} settings: {settings}')
        try:
            self.desc = assert_tp(settings, 'desc', str, default='No description provided')
            self.deps_req = list(map(ModuleID, assert_tp(deps, 'req', list)))
            self.deps_opt = list(map(ModuleID, assert_tp(deps, 'opt', list)))
            self.secrets = list(map(str, assert_tp(settings, 'secrets', list)))
        except Exception:
            log(logging.ERROR, f'Error discovered in the {modid} config.')
            raise

    def info(self, verbose: bool):
        """Returns information about the module."""
        info = '\n\t'.join([f'{self.modid}',
                            f'{self.desc}'])
        if verbose:
            info = '\n\t'.join([info,
                                f'Required dependencies ({len(self.deps_req)}): {self.deps_req}',
                                f'Optional dependencies ({len(self.deps_opt)}): {self.deps_opt}',
                                f'Secrets ({len(self.secrets)}): {self.secrets}'])
        return info

    def __eq__(self, other):
        if isinstance(other, Module):
            return self.modid == other.modid
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.modid)


class ModuleCollection:
    """Stores a collection of modules that can be accessed."""

    _UNINITIALIZED = object()

    def __init__(self):
        self._modules: dict[ModuleID, Module] = {}

    def add(self, path):
        """
        Initializes and adds module corresponding to the given path if it does not exist.

        Raises an error if the path is not a valid module.
        """
        modid = (ModuleID(path) if not isinstance(path, ModuleID) else path)


        # todo: placeholder thing
        def is_valid_module(modid: ModuleID):
            for parent in modid.id.parents[:-1]:
                # if there is existing entry (which would indicate it's been explored already and is valid); return true
                # else if module config is not present; return false
                # else; continue
                pass

    def get(self, path):
        """
        Gets module corresponding to the given path.

        If it does not exist, module will be added before returning it.
        """
        modid = ModuleID(path)
        if isinstance(module := self._modules.get(modid), Module):
            return module
        elif module == self._UNINITIALIZED:
            self._modules[modid] = Module(modid)
        else:
            self.add(modid)


class ModulesRunner:
    """Stores modules to execute on a specific runtype."""

    def __init__(self, coll: ModuleCollection, runtype: str, *modids: ModuleID, withdeps: bool = True,
                 confirm: bool = True, added: set[ModuleID] = None, dependents: set[ModuleID] = None):
        if added is None:
            added = set()
        if dependents is None:
            dependents = set()

        self.runtype = runtype
        self.modules: list[ModuleID] = []
        self.deps: list[ModulesRunner] = []

        for modid in modids:
            if modid not in added:
                self.modules.append(modid)
                added.add(modid)
                if withdeps:
                    deps = []
                    if req := coll.get(modid).deps_req:
                        deps += req
                    # If confirm is disabled, don't run any optional dependencies. Forcing optionals to be run
                    # makes it more difficult to install only required packages. If they are ignored by
                    # default, users can just explicitly include them in arguments.
                    if opt := coll.get(modid).deps_opt and confirm:
                        # todo
                        pass
                    if deps:
                        if dep_loop := dependents.intersection(deps):
                            log(logging.CRITICAL, f'Discovered infinite dependency loop! {modid}'
                                                  f'depends on and is a dependency of: {dep_loop}')
                            raise RecursionError
                        self.deps.append(ModulesRunner(coll, runtype, *deps, withdeps=withdeps, confirm=confirm,
                                                       added=added, dependents=dependents.union({modid})))

    def pre_run(self):
        """This method serves as a preliminary setup method before running modules, particularly for prompts."""
        # todo
        pass

    def run(self):
        """Run the corresponding scripts for modules."""
        # todo
        pass
