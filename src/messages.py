#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

import useful

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
        words = args[1:]

        for word in words:
            
            # A link was said.
            if word.startswith('http://') and self.bot.vars['bot_say_title'] == 'true':
                
                title = useful.get_title(word)

                # Dont print groovesharks ad text                
                if u'grooveshark.com' in word.lower():
                    title = title = title.split('|')[0]
                
                # get_title() gives empty string if title was not found.
                if len(title):
                    self.bot.send_msg(recv, 'title: %s'%title)
