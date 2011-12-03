#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

"""
Handle all connection and TCP stuff in this module
"""

import gevent
from gevent import queue
from gevent import socket

__all__ = ['Tcp']

class Tcp(object):
    """Handles TCP connections, `timeout` is in secs."""
    
    def __init__(self, bot, host, port, timeout=200):
        
        self.bot = bot
        # Empty buffers
        self._ibuffer = '' 
        self._obuffer = ''

        # Set input/output queues
        self.iqueue = queue.Queue()
        self.oqueue = queue.Queue()
        
        # Set host and port
        self.host = host
        self.port = port
        # Timeout in seconds
        self.timeout = timeout
        
        self.loops = [] # recv_loop, and send_loop
        self.end_loops = False
    
    def _create_socket(self):
        return socket.socket()
    
    def connect(self):
        """
        Connect to server, if unable to connect, try again at an interval.
        """
        
        # In this dictionary, bot keeps track of people in channels
        # { channel: {nick.lower(): correct_nick} }
        self.bot.nicklist = {} 
        for chan in self.bot.sets['bot_channels']:
            self.bot.nicklist[chan] = {}
        
        # Loop until we are connected.
        connected = False
        
        while not connected:
            try:
                self._socket = self._create_socket() # Create socket (again)
                self._socket.settimeout(self.timeout) # Set socket timeout
                
                self.bot.log.info('Connecting to %s..'% self.bot.sets['bot_server'])    
                self._socket.connect((self.host, self.port))
                connected = True

                self.bot.register() # Send USER, NICK etc..
                
            except Exception, e: # Error while connecting
                self.bot.log.info('Unable to connect, reason: %s'% e)
                
                interval = self.bot.sets['bot_reconnect_interval']
                self.bot.log.info('Reconnecting in %s seconds..'% interval)
                gevent.sleep(interval)
                
                self._socket.close()
                
        try:
            self.loops = [gevent.spawn(self._recv_loop), gevent.spawn(self._send_loop)]
            gevent.joinall(self.loops)
                                    
        finally:
            gevent.killall(self.loops)
        
    def disconnect(self):
        """Disconnect from server."""
        self._socket.close()
        self.bot.sets['bot_connected'] = False
        self.end_loops = True
    
    def reconnect(self):
        self.bot.log.info('Reconnecting..')
        self.disconnect()
        self.connect()
    
    def _recv_loop(self):
        """
        Receive lines from server
        """
        
        self.end_loops = False
        while not self.end_loops:
        
            try:
                data = self._socket.recv(4096)
            except socket.timeout:
                self.bot.log.info('Connection lost..')
                self.reconnect()
                
            if not data:
                break
            
            self._ibuffer += data
            while '\r\n' in self._ibuffer: # Split long data to chunks
                line, self._ibuffer = self._ibuffer.split('\r\n', 1)
                self.iqueue.put(line)
    
    def _send_loop(self):
        """
        Send lines to server
        """
        self.end_loops = False
        while not self.end_loops: # Split long messages to smaller
        
            line = self.oqueue.get().splitlines()[0][:500]
            
            self._obuffer += line + '\r\n'
            while self._obuffer:
                sent = self._socket.send(self._obuffer)
                self._obuffer = self._obuffer[sent:]
            
            
