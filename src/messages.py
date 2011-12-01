#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

import useful
import re

class MessageHandler(object):
    """
    Handles every PRIVMSG
    """
    def __init__(self, bot):
    
        self.bot = bot
        
    def analyze(self, prefix, cmd, args):
        """Handle every message from every channel in here."""
        
        nick = prefix.split('!')[0]
        recv = args[0]
        line = args[1]

        url_regex = re.compile(r"""https?://[^'"<>\s]+""")

        if self.bot.vars['bot_say_title'] == 'true':

            for match in re.findall(url_regex, line):
            	print(match)
                
                title = useful.get_title(match)

                # Dont print groovesharks ad text                
                if u'grooveshark.com' in match.lower():
                    title = title = title.split('|')[0]
                
                # get_title() gives empty string if title was not found.
                if len(title):
                    self.bot.send_msg(recv, 'title: %s'%title)
