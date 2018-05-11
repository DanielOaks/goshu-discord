#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import imp
import importlib
import inspect
import json
import os
import threading

from .commands import command_dict, create_command_from_docstring
from .data import DataStore
from .utils import JsonHandler, add_path
from . import utils


class Module:
    """A Module contains commands and/or event handlers."""

    def __init__(self):
        # get name for assumed path, store name, etc
        if getattr(self, 'name', None) is None:
            self.name = self.__class__.__name__

        # load datastore
        self.store_filename = os.sep.join(['data', 'modules', '{}.json'.format(self.name)])
        self.store = DataStore(self.store_filename)
        
        # get part of the assumed filename used to indicate dynamic json commands
        # e.g. a module named "responses" would have an ext on its json commands of '.res.json'
        if getattr(self, 'ext', None) is None:
            if len(self.name) >= 3:
                self.ext = self.name[:3]
            else:
                self.ext = self.name

        # load static commands
        self.commands = {}
        self.static_commands = {}
        for name, handler in inspect.getmembers(self):
            if handler.__doc__ is None:
                continue

            elif name.startswith('cmd_'):
                name = name.split('_', 1)[-1]
                all_aliases, cmd = create_command_from_docstring(name, handler, handler.__doc__)

                for name in all_aliases:
                    self.static_commands[name] = cmd
        self.commands.update(self.static_commands)

        # init json handler and dynamic commands
        self.dynamic_path = os.path.join('.', 'modules', self.name)
        self.dynamic_commands = {} # in case the below doesn't happen
        self.json_handlers = []

        if os.path.exists(self.dynamic_path):
            # setup our new module's dynamic json command handler
            new_handler = JsonHandler(self, self.dynamic_path, **{
                'attr': 'dynamic_commands',
                'callback_name': '_json_command_callback',
                'ext': self.ext,
                'yaml': True,
            })
            self.json_handlers.append(new_handler)
            self.reload_json() # load all commands together

    def reload_json(self):
        """Reload any json handlers we have."""
        for json_h in self.json_handlers:
            json_h.reload()

    def _json_command_callback(self, new_json):
        """Update our command dictionary.
        Mixes new json dynamic commands with our static ones.
        """
        # assemble new json dict into actual commands dict
        new_commands = {}
        for key, info in new_json.items():
            single_command_dict = command_dict(self, info)
            new_commands.update(single_command_dict)

        # merge new dynamic commands with static ones
        commands = getattr(self, 'static_commands', {}).copy()
        commands.update(new_commands)

        self.commands = commands

    def unload(self):
        ...

    def combined(self, message, cmd_info, command, arguments):
        ...


def isModule(member):
    if member in Module.__subclasses__():
        return True
    return False


class Modules:
    """Manages goshubot's modules."""
    def __init__(self, path):
        self.whole_modules = {}
        self.modules = {}
        self.path = path
        add_path(path)

        # info lists
        self.module_names = []
        self.dcm_module_commands = {}  # dynamic command module command lists

    def _modules_from_path(self, path=None):
        if path is None:
            path = self.path

        modules = []
        for entry in os.listdir(path):
            if os.path.isfile(os.path.join(path, entry)):
                (name, ext) = os.path.splitext(entry)
                if ext == os.extsep + 'py' and name != '__init__':
                    modules.append(name)
            elif os.path.isfile((os.path.join(path, entry, os.extsep.join(['__init__', 'py'])))):
                modules.append(entry)
        return modules

    def load_init(self):
        modulelist = []
        modules = self._modules_from_path()
        for module in modules:
            loaded_module = self.load(module)
            if loaded_module:
                modulelist.append(module)

        if modulelist:
            print('modules {} loaded'.format(', '.join(modulelist)))
        else:
            print('no modules loaded')

    def load(self, name):
        whole_module = importlib.import_module(name)
        imp.reload(whole_module)  # so reloading works

        # find the actual goshu Module(s) we wanna load from the whole module
        modules = []
        for item in inspect.getmembers(whole_module, isModule):
            modules.append(item[1]())
            break
        if not modules:
            return False

        # if /any/ are dupes, exit
        for module in modules:
            if module.name in self.modules:
                return False

        self.whole_modules[name] = []

        for module in modules:
            self.whole_modules[name].append(module.name)
            self.modules[module.name] = module

            module.folder_path = os.path.join('modules', name)

        return True

    def unload(self, name):
        if name not in self.whole_modules:
            print('module', name, 'not in', self.whole_modules)
            return False

        for modname in self.whole_modules[name]:
            self.modules[modname].unload()
            del self.modules[modname]

        del self.whole_modules[name]
        return True

    async def handle_command(self, message, content):
        # get cmd and args
        command, arguments = utils.split_num(content)
        command = command.lower()

        # run handler
        for _, module in self.modules.items():
            # call static cmd
            handler_info = module.static_commands.get(command)
            if handler_info is not None:
                await handler_info.handler(message, command, arguments)
                continue

            # call dynamic cmd
            handler_info = module.commands.get(command)
            if handler_info is not None:
                await handler_info.handler(message, handler_info.json, command, arguments)
