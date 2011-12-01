#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

# License: CC BY-SA 3.0, http://creativecommons.org/licenses/by-sa/3.0/
# Author: Kimmo Brunfeldt

# Python default modules
import ConfigParser
import traceback
import sys
import time
import os

# Gevent modules
import gevent
from gevent import socket
from gevent import queue
from gevent.server import StreamServer
from gevent.pool import Pool

if gevent.__version__ < '0.13':
    print('Too old gevent version! Must be >=0.13')
    sys.exit()
    

# BroBot's modules
import mr_server
import logger
import events
import messages
import commands
from timer import Timer
from tcp import Tcp

import commands

class IrcNullMessage(Exception):
    pass


class BroBot(object):
    """
    Modular irc bot which has integrated scheduling system, and backdoor server.
    """
    def __init__(self, settings, variables):
        
        # Every command from server is handled in events.py
        self.events = events.IrcEvents(self)
        
        # Every PRIVMSG from server is handled in messages.py
        self.msg_handle = messages.MessageHandler(self)
        
        # Add commands to a dictionary, structure is:
        # cmd_dict = { <re patterobject>: <function command> }
        self.cmd_dict = {}
        self.bot_cmds = {} # This is for !help.

        for item in commands.__all__:
            
            obj = eval('commands.' + item + '.Command(self)')
            self.cmd_dict[obj.syntax] = obj.main
            self.bot_cmds[obj.command] = {}
            self.bot_cmds[obj.command]['desc'] = obj.help_desc
            self.bot_cmds[obj.command]['syntax'] = obj.help_syntax
            
        
        self.lines = queue.Queue()
        
        # Settings are "immutable". They are meant to be variables that can be
        # listed for example in admin panel. They can be changed from code
        # but not with setting command
        self.sets = settings
        self.sets['bot_connected'] = False
        self.sets['bot_orig_nick'] = self.sets['bot_nick']
        self.sets['bot_alter_nick'] = self.sets['bot_nick'] + self.sets['bot_alter_ending']

        # Variables are "mutable". They can be listed but also changed via 
        # setting command.
        # Their type is always string, because they might be set via irc.
        self.vars = variables

        self.log = logger.Logger('Bot', self.sets['bot_logfile'])
        self.log.info('Using commands: %s' % ', '.join(commands.__all__))

        self.timer = None
        
    def send_ping(self, *args):
        """
        Sends PING :1 to server.
        To determine a connection lost, this is repeatedly called.
        """
        self.send('PING :1') 

    def send_msg(self, receiver, line):
        """Send PRIVMSG"""
        
        max_len = self.sets['bot_max_line_length']
        
        # Split over-long lines to parts!
        if len(line) > self.sets['bot_max_line_length']:
            
            buf = line
            
            while len(buf) > 0:
                
                line = buf[0:max_len] # Take first max_len chars to line
                buf = buf[max_len:] # Remove fist max_len chars fro buffer
                
                self.log.info('Sent message: %s "%s"'% (receiver, line) )
                self.send('PRIVMSG %s :%s'% (receiver, line) )
                gevent.sleep(0.5) # Prevent excess flood.
       
        else:
            self.log.info('Sent message: %s "%s"'% (receiver, line) )
            self.send('PRIVMSG %s :%s'% (receiver, line) )
        
    def send(self, line):
        """Sends raw line(s) to server"""
        
        encoding = self.sets['bot_encoding_out']
        try:
            line = line.encode(encoding)
            
        except UnicodeEncodeError:
            self.log.error(['send() was unable to encode(%s) a line:'% encoding,
                            line])
            return
        
        self.conn.oqueue.put(line)

    def create_connection(self):
        return Tcp(self, self.sets['bot_server'], self.sets['bot_port'], self.sets['bot_timeout'])
        
    def connect(self):
        """
        Connect irc bot to server, the raw socket controls are called in
        tcp.py.
        """
        self.conn = self.create_connection()
        gevent.spawn(self.conn.connect)

        self.parse_loop()
    
    def register(self):
        """Register to server"""
        
        nick = self.sets['bot_nick']
        
        self.send('USER %s 2 * :%s'% (nick, self.sets['bot_realname']))
        self.send('NICK %s'% nick)
    
    def disconnect(self):
        """Disconnect from server."""
        self.conn.disconnect()
        
    def reconnect(self):
        """Reconnect to server."""
        self.conn.reconnect()
        
    def quit(self, msg=None):
        """Quit properly from server."""
        self.log.info('Quitting..')
        self.send('QUIT :%s'% self.sets['bot_quit_message'])
        self.conn.disconnect()

    def parsemsg(self, s):
        """
        Breaks a message from an IRC server into its prefix, command, 
        and arguments. Taken from Twisted library!!
        """
        
        prefix = ''
        trailing = []
        if not s:
            raise IrcNullMessage('Received an empty line from the server.')
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args

    def parse_loop(self):
        """
        Parse commands and text coming from server
        """
        
        # Do forever.
        while True:
        
            line = self.conn.iqueue.get() # Get line from incoming queue
            
            # The approach to decode lines is ok if iso-8859-1 and utf-8 are
            # mainly used.
            try: # First guess: line is utf-8 encoded
                line = line.decode('utf-8')
               
            except UnicodeDecodeError: # It was not utf-8 encoded
                try:
                    # Second guess: line is iso-8859-1 encoded
                    line = line.decode('iso-8859-1')

                except UnicodeDecodeError: # It was not iso-8859-1 encoded
                    self.log.error(['Unable to decode a line! Line was:',
                                    line])
            
            prefix, command, args = self.parsemsg(line)

            print(line)
            
            # Handle events in events.py
            if command in self.events.event_dict.keys():
                self.events.event_dict[command](prefix, command, args)
           
            if command == 'PRIVMSG':
                
                # Hangle PRIVMSGs in messages.py
                self.msg_handle.analyze(prefix, command, args)
                
                # Check if line matched to commands syntax.                
                for pattern, func in self.cmd_dict.items():
                    
                    if pattern.match(args[1]) is not None: # Hit!
                    
                        # Pass a nick or channel to command function.
                        if args[0].lower() == self.sets['bot_nick'].lower():
                            out = prefix.split('!')[0] # it was privmsg to bot
                        else:
                            out = args[0] # It was msg to channel
                        
                        # Call command function. main looks like:
                        # def main(self, sender, recv, words)    
                        func(prefix, args[0], out, args[1].split(), args[1])
                
            # Answer to PING messages with PONG.
            if command == 'PING': 
                self.send('PONG :%s'% args[0])
            

def start_timer(bot):
    """Set up schedule service for bot"""
    
    tm = Timer(bot) # Set up timer, with empty joblist

    # Repeatedly send PONG to keep
    tm.add_repeat(bot.sets['bot_ping_interval'], bot.send_ping, [])
    
    tm.log.info('Starting Timer..')
    tm.start() # Start timer
    return tm


def start_mr(bot):
    """Set up MrServer."""
    mr = mr_server.MrServer(bot) # Start mr server
    
    listener = (settings['mr_host'], settings['mr_port'])
    server = StreamServer(listener, mr.parser)
    
    mr.log.info('Starting MrServer..')
    server.start()
    return mr, server


if __name__ == '__main__':
        
    # Check settings.py for bot's settings    
    from settings import *
    
    try:

        # Create logs and db directories.
        if not os.path.isdir('logs'):
            print('Creating logs directory..')
            os.makedirs('logs')
    
        if not os.path.isdir('db'):
            print('Creating db directory..')
            os.makedirs('db')
        
        bot = BroBot(settings, variables) # Start bot

        tm = start_timer(bot) # Start timer.
        bot.timer = tm # Now bot can add jobs
        
        mr, server = start_mr(bot) # Start MrServer    
        
        bot.connect() # Start the bot
        
        
    except KeyboardInterrupt:
        bot.log.info('KeyboardInterrupt.')
        tm.stop()
        
        mr.log.info('Stopping MrServer..')
        server.stop()
        bot.quit()
        
        sys.exit()
    
