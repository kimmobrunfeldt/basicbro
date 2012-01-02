#!/usr/bin/python
# -*- coding: UTF-8 -*-
#


"""
Module to allow remote connections to bot.


CONS:

Poorly tested. 
        
DOCS:


Message terminator is "\r\n". Line terminator is "\n"
Client: Only oneliner messages. 
Server: Can send multiline messages, only last line ends with \r\n


If irc server gives error from used MR commands, MR still tells "OK."
YOU HAVE TO GIVE CORRECT COMMANDS TO MR!!

e.g newnick command is used to change nick to "Q", MR says "OK.", but it is
not ok, because "Q" is reserved! (in QuakeNet)

Keep in mind that most commands match arguments to a regex. If wrong syntax error
is given, it does not pass the regex.

Channels are always treated aand handled lowercase.

---------------- COMMANDS ------------------

NEWNICK [nick]

    Bot sends NICK [nick] to irc server. If nick is in use, the bot's events
    are built in a way, that it tries to use alternick. Beware!
    Replys: 003, 204, 208, 209

    regex: '^[a-zA-Z0-9]{1,15}$'
    [nick] must be alphanumeric. 1-15 long.

    e.g NEWNICK perusbro\r\n


NICKLIST [channel]
    
    Sends a sorted list of nicks in [channel] for MrClient.
    Reply is a multiline message, like: 004 [channel] [nick], last line ends
    with \r\n.
    Replys: 003, 004, 204, 208, 209, 210, 211

    regex: '^.{1,50}$'
    [channel] 1-50 chars.
    
    e.g NICKLIST #luola\r\n

RAW [args]*

    Sends everything to irvserver after "RAW ".
    USE WITH CARE!! If you mess up with raw commands, bot might confuse.
    Replys: 003, 204, 208, 209
    
    e.g RAW PRIVMSG #luola :secrets\r\n


WEBMSG [receiver] [sender] [message]

    Sends message to a channel with webirc stamp in it.
        
    regex: '^.{1,40} .{1,20} .{1,500}$'
    [receiver] is channel or nick in irc server which receives the message, max 40 chars
    [sender] sender's name, max 20 chars
    [message] message, max 500 chars per message.
    Replys: 003, 204, 208, 209, 205
    
    
    e.g WEBMSG #luola kimbledon Example message to be sent to #luola-channel\r\n


TOPIC [channel]

    Get channel's topic.
        
    regex: '^.{1,40}$'
    [channel] Channel's name.
    Replys: 210
    
    
    e.g TOPIC #luola\r\n
        
    
RECONNECT

    Reconnects bot.
    
    e.g RECONNECT\r\n
"""


import re
import gevent
from gevent.server import StreamServer
from gevent import Greenlet
from gevent import socket

# Bot's logger module
import logger
import useful

__all__ = ['MrServer']


msgs = {
    '001': '001 Auth.',
    '002': '002 Auth ok.',
    '003': '003 Done.',
    '004': '004 [channel] [nick]',
    '005': '005 [channel] [topic]',
    
    '201': '201 Already authed.',
    '202': '202 Wrong password.',
    '203': '203 Maximum authorize attempts exceeded.',
    '204': '204 Not authed.',
    '205': '205 Incorrect WEBMSG syntax.',
    '206': '206 Incorrect NEWNICK syntax.',
    '207': '207 Unknown command.',
    '208': '208 Bot is not connected to server.',
    '209': '209 No parameters given.',
    '210': '210 No such channel.',
    '211': '211 Incorrect NICKLIST syntax.',
    }
    
class MrServer(object):
    """
    Backdoor server that makes controlling bot without irc protocol possible.

    The way that parser passes socket handle to every called command function
    is because, multiple parsers are spawned. They cant have a shared handle, 
    it would cause synchronation errors.
    """
    
    def __init__(self, bot):
        self.bot = bot # Handle to the bot.
        
        self.cmds = {
                    'webmsg': self.webmsg,
                    'raw': self.raw,
                    'newnick': self.newnick,
                    'nicklist': self.nicklist,
                    'reconnect': self.reconnect,
                    }
        
        self.log = logger.Logger('MrServer',bot.sets['mr_logfile'])
                
    def parser(self, socket, address):
        """
        Parses everything that is sent to MRserver
        """
        
        self.log.info('Client connected from %s'% address[0])
        
        
        # makefile() allows to use readline()
        fileobj = socket.makefile()
        
        # Ready to get commands
        self.send(fileobj, msgs['001']) # Welcome message
        
        # This is local, because making it self.quit would lead to synchronation
        # errors between "threads"
        # quit = False
        
        authorized = False # Not authorized yet.
        auth_tries = 3 
        
        # Serve forever
        while True:
        
            # Read received line, make it unicode, expecting utf-8 or iso-8859-1
            try:
                line = fileobj.readline()
            
            except Exception, e:
                self.log.info(e)
                self.log.info("Disconnecting session.")
                break
            
            if not line:
                self.log.info("Client disconnected.")
                break

            line = useful.uni(line).strip()
            args = line.split(u' ')
            wordline = u' '.join(args[1:])
            command = args[0].lower()
            
            
            if command == 'quit':
                self.log.info("Client quit.")
                break
            
            # Auth command is here to make loop process simpler.
            if command == 'auth':
                
                if authorized: # Already authed.
                    self.send(fileobj, msgs['201'])
                    continue

                    
                auth_tries -= 1
                
                hashed = useful.sha256_hex(wordline)
                if hashed == self.bot.sets['mr_password']: # Pass was correct
                    self.send(fileobj, msgs['002']) # Auth ok
                    authorized = True
                
                else: # Wrong password
                    self.send(fileobj, msgs['202']) # Wrong password.
                    self.log.error(['Wrong password from %s'%address[0]])
                    
                    if auth_tries < 1: # Too many auth attempts
                        self.send(fileobj, msgs['203'])
                        self.log.error(['Max auth tries from %s'%address[0]])
                        break
                    
                    gevent.sleep(1) # Give time to think.
                    
                continue # Start loop again
            
            if command not in self.cmds:
                self.send(fileobj, msgs['207']) # Unknown command.  
                continue
            
            if authorized:            
                    
                # Received a known command.
                if command in self.cmds:
                        
                        # Pass arguments to function
                        self.cmds[command](fileobj, wordline)
                        
            else: # Not authorized
                
                self.send(fileobj, msgs['204']) # Not authed.
                
                
    def send(self, obj, data):
        """Send data to client."""
        
        if isinstance(data, list): # Multiple lines
            
            for index, line in enumerate(data): # Loop lines. enum to get position
                
                if index == len(data) - 1: # Final line, send data terminator
                    obj.write(line + '\r\n')
                else:
                    obj.write(line + '\n') # Send only line term.
        
        elif isinstance(data, str): # One line.
                
            obj.write(data + '\r\n')
        
        elif isinstance(data, unicode):
            
            obj.write(data.encode('UTF-8') + '\r\n')
            
        else:
            raise Exception, "MrServer's send() got wrong type of data."
        
        try:
            obj.flush()
        except socket.error, e:
            print e
            

    def nicklist(self, obj, words):
        """Lists nicks in a channel"""
        
        # channel
        # [1-50]
        regex = re.compile('^.{1,50}$')

        if regex.match(words) is None:
            self.send(obj, msgs['211'])
            return

        if not self.bot.sets['bot_connected']:
            self.send(obj, msgs['208']) # Bot is not connected.
            return        
        
        
        channel = words.lower().strip()
        
        if channel not in self.bot.nicklist.keys():
            self.send(obj, msgs['210']) # Bot is not connected.
            return 
        
        # This speeds up(minimal), but simplifies code.
        nicklist = self.bot.nicklist
        
        nicks = []
        # Sort list.
        for sorted_nick in sorted(nicklist[channel].keys()):
            nick = nicklist[channel][sorted_nick]
            nicks.append('004 %s %s'% (channel, nick))
        
        for x in nicks:
            # Send multiline message. 004 [nick] on each line.
            print x
            print type(x)
            self.send(obj, x)
            
        self.log.info("Nicklist from %s was asked."%channel)
        return
        
    def webmsg(self, obj, words):
        """Sends webirc message to a receiver."""
        
        # receiver sender  message
        # [1-20]   [1-20]  *
        regex = re.compile('^.{1,50} .{1,20} .{1,500}$')

        if regex.match(words) is None:
            self.send(obj, msgs['205'])
            return

        if not self.bot.sets['bot_connected']:
            self.send(obj, msgs['208']) # # Bot is not connected.
            return
                
        args = words.split(u' ')
        recv = args[0]
        sender = args[1]
        message = u' '.join(args[2:])
        
        
        msg = self.bot.vars['mr_webirc_stamp']
        msg = msg.replace(u'%n', sender) # Put sender in place
        
        # From <stamp, %n> %m  remove letters %m, you get length
        stamp_len = len(msg) - 2 
        
        msg = msg.replace(u'%m', message) # Put message in place
        
        
        max_len = self.bot.sets['bot_max_line_length']
        
        # Intend lines nicely when max line len is exeeded.
        if len(msg) > max_len:
        
            buf = msg
            
            msg = buf[0:max_len] # line with the stamp
            
            self.bot.send_msg(recv, msg) # send msg
            
            buf = buf[max_len:] # Chop the first sent message off
            
            while len(buf) > 0:
                
                if stamp_len + len(buf) > max_len:
                    msg = ' ' * stamp_len + buf[0:(max_len - stamp_len)]
                    buf = buf[max_len - stamp_len:]
                else:
                    msg = ' ' * stamp_len + buf
                    buf = u''
                
                self.bot.send_msg(recv, msg)
        
        else:
            self.bot.send_msg(recv, msg)
            
        self.send(obj, msgs['003']) # OK.
        self.log.info("Webirc was used, sender: %s."%sender)
        return
    
    def raw(self, obj, words):
        """Sends data to server without modifying."""
        
        if not self.bot.sets['bot_connected']:
            self.send(obj, msgs['208']) # # Bot is not connected.
            return
        
        if len(words.strip()) == 0:
            self.send(obj, msgs['209']) # Empty parameters.
            return
        
        self.bot.send(words)
        self.send(obj, msgs['003']) # OK.
        self.log.info("RAW: %s"%words)    
        return
        
    def newnick(self, obj, words):
        """Changes bot's nick"""

        # newnick
        # [1-15]^[a-zA-Z0-9_]*
        regex = re.compile('^[a-zA-Z0-9]{1,15}$')
        
        if regex.match(words) is None:
            self.send(obj, msgs['206'])
            return
            
        if not self.bot.sets['bot_connected']:
            self.send(obj, msgs['208']) # OK.
            return
        
        nick = words.strip()
        self.bot.send(u'NICK %s'% nick)
        self.send(obj, msgs['003']) # OK.
        self.log.info("NEWNICK: %s"%nick)
        return

    def reconnect(self, obj, words):
        """Bot reconnects"""

        if not self.bot.sets['bot_connected']:
            self.send(obj, msgs['208']) # OK.
            return
        
        self.bot.reconnect()
        return

