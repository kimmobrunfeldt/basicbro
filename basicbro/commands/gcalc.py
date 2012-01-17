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
import json
from gevent import monkey

monkey.patch_all()

class Command(object):
    
    def __init__(self, bot):
        
        self.use_limit = 5  # In seconds.
        self.last_used = 0  # Unixtime when command was last time used.
        self.bot = bot
        self.syntax = re.compile(r'^!c')
        self.command = u'c' # in lower without !
        self.help_syntax = "Syntax: \"!c [operation]\", example: \"!c ln(1) * 3\""
        self.help_desc = "Uses Google's calculator to calculate operations. http://www.googleguide.com/calculator.html"
    
    def main(self, senderhost, recv, out, words, wordsline):

        regex = re.compile(r'^!c .+$')
        
        if regex.match(wordsline) is None:
            self.bot.send_msg(out, self.help_syntax)
            return
        
        expr = wordsline[3:] # Get only the operation
        
        legal = self.bot.vars['gcalc_legal'] # Check if illeagal characters
        reg = r'^[a-zA-Z0-9' + re.escape(legal) + r']+$'
        regex = re.compile(reg)
        
        if regex.match(expr) is None:
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
            answer = answer.replace('\\x22', '&quot;') # This way quotes won't mix json.
            answer = answer.decode('string_escape')
            
            print repr(answer)
            # Keynames must be between quotes in valid JSON
            answer = answer.replace('lhs:','"lhs":').replace('rhs:','"rhs":')
            answer = answer.replace('error:','"error":').replace('icc:','"icc":')
            
            print repr(answer)
            # Read the JSON format.
            answer = json.loads(answer)
            
            oper = answer['lhs'] # Operation as understood
            result = answer['rhs'] # Result of calculation
            error = answer['error'].replace('&quot;', '"')
            
            # &#215; etc to corretcans
            oper = useful.unescape(oper)
            result = useful.unescape(result)

            # <sup>35</sup> -> ³⁵
            oper = useful.sup(oper)
            result = useful.sup(result)

            # lhs = understood input
            # rhs = answer
            # error = error
        except ValueError:
            raise
            self.bot.send_msg(out, "Google has changed their calculator.")
            self.bot.log.error([u'Google has changed calculator', answer, expr])
            return

        except SyntaxError:
            raise
            if len(answer) == 0: # Empty string->decode was not success
                self.bot.send_msg(out, "Problem with decoding.")
                self.bot.log.error(['Problem with decoding!', answer, expr])
            else:
                raise
            
        if len(error) > 0:
            self.bot.send_msg(out, "Operation was not understood. Error: \"%s\""%error)
            return
        
        # Send out the answer    
        self.bot.send_msg(out, u"%s = %s"%(oper, result))
        
        
        
