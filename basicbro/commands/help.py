#!/usr/bin/python
# -*- coding: UTF-8 -*-
#


import time
import re

class Command(object):
    """
    Shows 
    """
    
    def __init__(self, bot):
        
        self.bot = bot
        self.syntax = re.compile(r'^!help')
        self.command = u'help' # in lower without !
        self.help_syntax = "Syntax: \"!help [command]\", example: \"!help c\""
        self.help_desc = "Shows all available commands and how to use them."
    
    def main(self, senderhost, recv, out, words, wordsline):

        all_cmds = self.bot.bot_cmds
        cmds = u'!' + ', !'.join(all_cmds.keys())
        
        # Not only !help
        if len(words) > 1:

            command = words[1].lower()
            if command[0] == '!': # Remove possible ! mark
                command = command[1:]
                            
            if command not in all_cmds.keys():
                self.bot.send_msg(out, 'No such command.')
                self.bot.send_msg(out, 'Available commands: %s'%cmds)
                return
            
            self.bot.send_msg(out, all_cmds[command]['desc'])
            self.bot.send_msg(out, all_cmds[command]['syntax'])
            
            
        else:

            self.bot.send_msg(out, 'Available commands: %s'%cmds)
            self.bot.send_msg(out, 'Write !help [command] to get more information. For example: !help c')
        
