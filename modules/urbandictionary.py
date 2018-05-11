#!/usr/bin/env python3
# Goshu Chatbot
# written by Daniel Oaks <daniel@danieloaks.net>
# licensed under the ISC license

import json
import urllib.request, urllib.parse, urllib.error

from gcblib.modules import Module


class urbandictionary(Module):
    async def cmd_ud(self, message, command, arguments):
        """See UrbanDictionary definition"""
        encoded_query = urllib.parse.urlencode({b'term': arguments})
        url = 'http://www.urbandictionary.com/iphone/search/define?%s' % (encoded_query)
        try:
            search_results = urllib.request.urlopen(url)
            json_result = json.loads(search_results.read().decode('utf-8'))
            try:
                url_result = str(json_result['list'][0]['word']).replace('\r', '').replace('\n', ' ').strip()
                url_result += ' --- '
                url_result += str(json_result['list'][0]['definition']).replace('\r', '').replace('\n', ' ').strip()
            except:
                url_result = 'No Results'
        except urllib.error.URLError:
            url_result = 'Connection Error'

        response = '*** UrbanDictionary: ' + url_result

        await message.channel.send(response)
