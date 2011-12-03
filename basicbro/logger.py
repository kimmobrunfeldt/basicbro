#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

"""
Logger module. Logs errors and information.
"""


import time

__all__ = ['Logger']

def printbold(s): # prints text in bold
	if len(s) > 0: # do not do anything if the string is empty
		if s[-1] == '\n': s = s[:-1] # remove lineterminator if one
		print('\033[0;1m'+str(s)+'\033[m')

def printred(s): # prints text in red
	if len(s) > 0: # don't do anythin if string is empty
		if s[-1] == '\n': s = s[:-1] # remove lineterminator if one
		print('\033[0;31m'+str(s)+'\033[m')

class Logger(object):
    """
    Logs everything to files
    """
    
    def __init__(self, logname, logfile):
        
        # Logfile is name without ".log" ending
        self.logfile = logfile
        self.infolog = logfile + '.log'
        self.errorlog = logfile + '_error.log'
        self.encoding = 'utf-8'
        
        self.logname = logname
        
    def info(self, line):
        """
        Single lines are logged with this
        """
        
        try:
            line = line.encode(self.encoding)
            
        except UnicodeEncodeError:
            printred('Logger.info() was unable to encode(%s) a line:'% self.encoding)
            printred(line)
            return
                            
        timestamp = time.strftime('[%d.%m.%Y %H:%M:%S]')
        
        try:
            f = open(self.infolog, 'a')
        except:
            printred('Unable to open file: ' + self.infolog)
            return
        
        if line[-1] != '\n': # Add '\n'
            line = line + '\n'
        
        f.write(timestamp + ' ' + line)
        printbold('%s [%s] %s' %(timestamp, self.logname, line[:-1]))
    
        f.close()
        
    def error(self, lines):
        """
        Log errors with this function, it assumes that error is multiline
        error message from traceback.

        type(lines) = list
        """
        
        try:
            lines = map(lambda x: x.encode(self.encoding), lines)
            
        except UnicodeEncodeError:
            printred('Logger.error() was unable to encode(%s) a line:'% self.encoding)
            printred('\n'.join(lines))
            return
                        
        timestamp = time.strftime('[%d.%m.%Y %H:%M:%S]')
        
        try:
            f = open(self.errorlog, 'a')
        except:
            printred('Unable to open file: ' + self.errorlog)
            return
        
        # Write fancy "--------[timestamp]----------" kind of thing
        f.write(('-' * 20) + timestamp + ('-' * 20) + '\n')
        printbold(('-' * 20) + timestamp + ('-' * 20))
        
        # Go through lines to be logged
        for line in lines:
            
            
            if line[-1] != '\n': # Add '\n'
                line = line + '\n'
            
            f.write(line)
            printbold(line[:-1])
        
        f.write( ('-' * 61) + '\n')
        printbold('-' * 61)
        
        f.close()
        
if __name__ == '__main__':
    
    log = Logger('LG','LOGTESTER')
    
    log.info('Testing..')
    log.error(['Line1','Line2'])
