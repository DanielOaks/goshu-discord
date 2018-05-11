#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import random
from gcblib.modules import Module


class random_module(Module):
    def __init__(self):
        Module.__init__(self)

        random.seed()

    async def cmd_random(self, message, command, arguments):
        """Random selection from phrases separated by a |

        @usage <first>|<second>|<third>...
        """
        if '|' not in arguments:
            await message.channel.send("You should try something like:  'random apples|bananas|oranges")
            return

        response = message.author.mention + ' '

        random_list = arguments.split('|')
        random_num = random.randint(1, len(random_list)) - 1

        response += random_list[random_num].strip()

        if random_list[random_num].strip() != '':
            await message.channel.send(response)
