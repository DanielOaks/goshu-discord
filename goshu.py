#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import asyncio
import discord
import yaml
from gcblib import utils
from gcblib.modules import Modules

# load modules
ModulesHandler = Modules('./modules')
ModulesHandler.load_init()

# load config
config = {}
with open('config.yaml') as config_file:
    config = yaml.safe_load(config_file.read())

mention = config.get('mention')
if mention:
    mention = mention + ' '  # for matching

class Ikamouto(discord.Client):
    commands = {}

    async def on_ready(self):
        print('Logged on as {}!'.format(self.user))

        if config.get('game'):
            game = discord.Game(config['game'])
            await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            name = '~dm with {}~'.format(message.channel.recipient)
        elif isinstance(message.channel, discord.GroupChannel):
            name = '~group with {}~'.format(','.join(message.channel.recipients))
        else:
            name = '#{}'.format(message.channel.name)
        try:
            print('#{0} <{1.author}> {1.content}'.format(name, message))
        except:
            print('~dm with {0.author}~ <{0.author}> {0.content}'.format(message))

        if message.author == client.user:
            return
        
        # check cmd prefix
        content = message.content
        if content.startswith("'"):
            content = content[1:]
        elif mention and content.startswith(mention):
            content = content[6:]
        else:
            return

        # dispatch command
        await ModulesHandler.handle_command(message, content)


client = Ikamouto()

client.run(config['token'])
