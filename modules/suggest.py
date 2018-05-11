#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import os

from gcblib.modules import Module
from gcblib.utils import filename_escape


class suggest(Module):
    async def cmd_suggest(self, message, command, arguments):
        """Suggest something, anything at all!

        @usage <suggestion>
        """
        if arguments == '':
            await message.channel.send("You should give me a suggestion!")
            return

        output = 'From {}\n\n{}\n\n-----\n\n'.format(message.author.display_name, arguments)

        with open('suggestions.txt', 'a', encoding='utf-8') as outfile:
            outfile.write(output)

        await message.channel.send("Thanks for your suggestion, {}!".format(message.author.mention))
