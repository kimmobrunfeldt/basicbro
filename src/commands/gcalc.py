#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

import urllib
import urllib2
import httplib
import time
import re
import ast
import useful
from gevent import monkey

monkey.patch_all()

class Command(object):
    """
    Gives age when birth year is given.
    """
    
    def __init__(self, bot):
        
        self.use_limit = 5
        self.last_used = 0
        self.bot = bot
        self.syntax = re.compile(r'^!c')
        self.command = u'c' # in lower without !
        self.help_syntax = "Syntax: \"!c [operation]\", example: \"!c ln(1) * 3\""
        self.help_desc = "Uses Google's calculator to calculate operations. http://www.googleguide.com/calculator.html"
    
    def main(self, senderhost, recv, out, words, wordsline):

        regex = re.compile(r'^!c .+$')
        
        if regex.match(wordsline) == None: # Hit!
            self.bot.send_msg(out, self.help_syntax)
            return
        
        expr = wordsline[3:] # Get only the operation
        
        legal = self.bot.vars['gcalc_legal'] # Check if illeagal characters
        reg = r'^[a-zA-Z0-9' + re.escape(legal) + r']+$'
        regex = re.compile(reg)
        
        if regex.match(expr) == None: # Hit!
            self.bot.send_msg(out, "Operation can contain only a-z, A-Z, 0-9 and following characters: \"%s\""%legal)
            return
        
        # Avoid command flood!
        if self.last_used + self.use_limit > time.time():
            self.bot.send_msg(out, "This command was used less than %s seconds ago."%self.use_limit)
            return
        
        self.last_used = time.time()
         
        expr = urllib.quote_plus(expr) # Replace " " -> + etc.
             
        url = "http://www.google.com/ig/calculator?hl=en&q=" + expr
        
        answer = useful.get_http(url) # Get url with this error handling GET
        
        if len(answer) == 0:
            self.bot.send_msg(out, "Error in connecting to Google.")
            return
        
        
        try:
            print repr(answer)
            # Change "\x26" -> "&"
            answer = answer.decode('string_escape')
            
            print repr(answer)
            # Replace these, then literal_eval() is possible to use
            answer = answer.replace('lhs','"lhs"').replace('rhs','"rhs"')
            answer = answer.replace('error','"error"').replace('icc','"icc"')
            answer = answer.replace('true','True').replace('false','False')
            
            # Change it to dictionary
            # This is here, because only after this, we can decode the string
            # to unicode.
            answer = ast.literal_eval(answer)
            
            oper = answer['lhs'] # Operation as understood
            result = answer['rhs'] # Result of calculation
            
            print repr(oper)
            print repr(result)
            
            # Change it to unicode.
            oper = useful.uni(oper)
            result = useful.uni(result)
            
            print repr(oper)
            print repr(result)
            
            # &#215; etc to corretcans
            oper = useful.unescape(oper)
            result = useful.unescape(result)

            print repr(oper)
            print repr(result)

            # <sup>35</sup> -> ³⁵
            oper = useful.sup(oper)
            result = useful.sup(result)

            print repr(oper)
            print repr(result)

            # lhs = understood input
            # rhs = answer
            # error = error
        except ValueError:
            self.bot.send_msg(out, "Google has changed their calculator.")
            self.log.error([u'Google has changed calculator', answer, expr])
            return

        except SyntaxError:

            if len(answer) == 0: # Empty string->decode was not success
                self.bot.send_msg(out, "Problem with decoding.")
                self.log.error(['Problem with decoding!', answer, expr])
            else:
                raise
            
            
        if len(answer['error']) > 0:
            self.bot.send_msg(out, "Operation was not understood.")
            return
        
        # Send out the answer    
        self.bot.send_msg(out, u"%s = %s"%(oper, result))
        
        
        
