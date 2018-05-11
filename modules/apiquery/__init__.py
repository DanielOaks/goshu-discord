#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import urllib.parse

import discord

from gcblib.formatting import unescape
from gcblib.modules import Module
from gcblib.utils import get_url, format_extract


class apiquery(Module):
    async def combined(self, message, cmd_info, command, arguments):
        if arguments == '':
            arguments = ' '

        values = {
            'escaped_query': urllib.parse.quote_plus(unescape(arguments))
        }

        url = cmd_info['url'].format(**values)
        async with message.channel.typing():
            r = get_url(url)

        if isinstance(r, str):
            display_name = cmd_info['display_name']
            await message.channel.send(unescape('*** {}: {}'.format(display_name, r)))
            return

        # parsing
        tex = r.text
        response = format_extract(cmd_info, tex, fail='No results')

        if isinstance(response, str):
            await message.channel.send(response)
        elif isinstance(response, discord.Embed):
            await message.channel.send(embed=response)
