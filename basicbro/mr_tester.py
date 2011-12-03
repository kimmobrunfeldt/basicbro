#!/usr/bin/python
# -*- coding: UTF-8 -*-
#


import socket


a = socket.socket()

a.connect(('127.0.0.1', 48827))

# THIS IS EXAMPLE PASSWORD!
a.send('auth password\r\n')

# Test utf-8 and line splitting
a.send('webmsg #channel sender UTF-8 TEST: Č Ě Ď Ň Ř Ů Ĺ, Also split line test: '+ 'a'*120 + '012345678901234567890' + '\r\n')

# Test nicklisting for #channel
a.send('nicklist #channel\r\n')

# Quit
a.send('quit\r\n')

a.close() # Close socket
