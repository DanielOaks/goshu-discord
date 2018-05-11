#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license


def command_dict(module, info):
    command_name = info['name'][0]
    aliases = info['name'][1:]

    description = info.get('description', '--- generated command')

    cmd = Command(command_name, module.combined, aliases=aliases, description=description, json=info)

    commands = {
        command_name: cmd,
    }

    for name in aliases:
        commands[name] = cmd
    
    return commands


def create_command_from_docstring(name, handler, docstring):
    aliases = [name.lower(),]
    extracted_aliases = []
    description = ''
    long_description = ''

    print('creating command from docstring:', name)

    cmd = Command(name, handler, aliases=extracted_aliases,
        description=description, long_description=long_description)

    return aliases, cmd


class Command:
    """Represents a command a user can run."""

    def __init__(self, name, handler, aliases=[], json={}, description='', long_description=''):
        self.name = name
        self.handler = handler
        self.aliases = aliases
        self.json = json  # used for json-generated commands

        self.description = description
        self.long_description = long_description
        if not long_description.strip():
            self.long_description = description
