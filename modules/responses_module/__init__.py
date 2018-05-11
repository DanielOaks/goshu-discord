#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel$danieloaks.net>
# licensed under the ISC license

import json
import os
import random
import time

import discord

from gcblib.formatting import unescape
from gcblib.modules import Module


class responses_module(Module):
    """Supports creating special custom commands with simple json dictionaries."""
    def __init__(self):
        Module.__init__(self)

        random.seed()

        # $s means source, the nick of whoever did the command
        # $t means target, either whoever they write afterwards, or the current self nick
        # note: $S and $T represent allcaps versions of $s and $t
        # $f at the start means: ignore the standard pre / post lines
        # $m at the start means: send this line as a /me rather than a /msg

    async def combined(self, message, cmd_info, command, arguments):
        async with message.channel.typing():
            time.sleep(0.6)

        source = message.author.mention
        sourceupper = source

        target = message.author.mention
        targetupper = target
        tnum = '1'
        if arguments.strip() != '':
            target = arguments.strip()
            targetupper = target.upper()
            tnum = '2'

            # search for a target user we can mention
            if target.lower() == 'me':
                tnum = '1'
            elif 2 < len(target):
                mentioned = []
                tnick = target.lower()
                # huehuheue
                if tnick == 'dan':
                    tnick = 'dan-'
                if isinstance(message.channel, discord.DMChannel):
                    ...
                elif isinstance(message.channel, discord.GroupChannel):
                    for member in message.channel.recipients:
                        mnick = member.display_name.lower()
                        if tnick in mnick:
                            mentioned.append(member)
                else:
                    for member in message.channel.members:
                        mnick = member.display_name.lower()
                        if tnick in mnick:
                            mentioned.append(member)

                if len(mentioned) == 1:
                    target = mentioned[0].mention
                    targetupper = target

        # message format = initial, 1/2pre, line(s), 1/2post, outro
        output = []

        if 'initial' in cmd_info:
            if type(cmd_info['initial']) == list:
                for line in cmd_info['initial']:
                    output.append(line)
            else:
                output.append(cmd_info['initial'])

        pre = ''
        if tnum + 'pre' in cmd_info:
            pre = cmd_info[tnum + 'pre']

        post = ''
        if tnum + 'post' in cmd_info:
            post = cmd_info[tnum + 'post']

        if tnum == '2':
            if tnum not in cmd_info:
                tnum = '1'

        response_list = cmd_info[tnum]
        response_num = random.randint(1, len(response_list)) - 1
        random.shuffle(response_list)
        response = response_list[response_num]

        if response[0:2] == '@f':
            pre = ''
            post = ''
            response = response[2:]

        if type(response) == str:
            response = [response]
        for line in response:
            output.append(pre + line + post)

        for line in output:
            use_action = False
            if line[:2] == '@m':
                line = line[2:]
                use_action = True

            line = unescape(line, {
                's': source,
                'S': sourceupper,
                't': target,
                'T': targetupper,
                'prefix': "'",
                'randomchannelnick': [random_channel_nick, [source, message]]
            })

            if use_action:
                await message.channel.send('_{}_'.format(line.strip()))
            else:
                await message.channel.send(line.strip())


def random_channel_nick(source, message):
    try:
        if isinstance(message.channel, discord.DMChannel):
            user_list = [message.channel.me, message.channel.recipient]
        elif isinstance(message.channel, discord.GroupChannel):
            user_list = message.channel.recipients + message.channel.me
        else:
            user_list = message.channel.members
        user_num = random.randint(1, len(user_list)) - 1
        if 1 < len(user_list):
            while user_list[user_num].display_name == source:
                user_num = random.randint(1, len(user_list)) - 1
        return user_list[user_num].display_name

    except:
        return source
