#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

import urllib2
import re, htmlentitydefs
import httplib
import hashlib
from gevent import monkey

monkey.patch_all()


def sup(text):
    """
    Replaces <sup>235</sup> -> ²³⁵
    text MUST be unicode!
    Problem: look the .replace method comment.
    """
    
    # digits bet
    matcher = re.compile('<sup>\d+</sup>')
    
    for match in matcher.findall(text):
        
        cut = match[5:-6] # Cut <sup> and </sup>
        
        number = ''
        # Loop through every character
        for char in cut:
            
            try:
                char = int(char)
            except ValueError: # Skip to next and try if it is number
                raise
        
            # 1-3 are traditional and present without unicode.
            if char == 1:
                char = u'\xb9'

            elif char == 2:
                char = u'\xb2'
            
            elif char == 3:
                char = u'\xb3'
            
            elif char == 0:
                char = unichr(8304) # unichar(8304) -> ⁰ 
            
            # ⁴ is unichr(8308) so we distract 4 from char to get how much
            # we have to add to 8308 to get corresponding unichr(x)
            else:
                four_sup = 8308
                add = char - 4 # 4 - 4 = +; 5 - 4 = 1 etc.
                char = unichr(four_sup + add)
            
            number += char
        
        # Replace found match with the number.
        # If we have X same <sup> taghed number, then the loop is done X - 1
        # many times for no reason. 
        text = text.replace(match, number)
    
    return text
        
        
def unescape(text):
    """
    Replaces HTML entities with correct characters
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def between(text, begin, end):
    """Returns text between first found begin and end"""
    
    idx1 = text.find(begin)
    idx2 = text.find(end,idx1)
    
    if idx1 == -1 or idx2 == -1:
        return ''
        
    return text[idx1 + len(begin):idx2].strip()

def uni(text):
    """
    Tries to convert text to unicode
    """
    try: # First guess: line is utf-8 encoded
        text = text.decode('utf-8')
       
    except UnicodeDecodeError: # It was not utf-8 encoded
        try:
            # Second guess: line is iso-8859-1 encoded
            text = text.decode('iso-8859-1')

        except UnicodeDecodeError: # It was not iso-8859-1 encoded
            text = u''
            
    return text


def get_http(url, timeout=3, data=35536):
    """Get data from http url."""
    try:
        # Request page as Mozilla browser
        req = urllib2.Request(url)
        agent = 'Mozilla/5.0 (X11; Linux i686; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'
        req.add_header('User-Agent', agent)

        # Read only first 35536 bytes, speeds up a lot. Set timeout to 3 secs
        page = ''.join(urllib2.urlopen(req, timeout=timeout).read(data))
        return page
        
    # Errors like 404 Not Found.
    except urllib2.HTTPError,e:
        print e
        return u''

    except urllib2.URLError,e: # e.g Host does not exist
        print e
        return u''

    # For example invalid port http://google.fi:lol
    except httplib.InvalidURL,e: 
        print e
        return u''

    # This should never be raised. It is raised when url is "sdag" not "http://x"
    except ValueError,e:
        print e
        return u''

    except: # Otherwise raise exception.
        raise
    

def get_title(url, timeout=4):
    """Returns title of x page"""
    
    page = get_http(url, timeout)
        
    title = between(page,'<title>','</title>')
    title = uni(title) # Convert title to unicode
    title = unescape(title) # Change HTML entities to correct characters
    title = u' '.join(title.split()) # Replace whitespaceblocks with ' '
    
    return title.strip() # Strip starting and ending whitespace.

def sha256_hex(data):
    """Returns sha256 hexdigest of given data."""
    if isinstance(data, unicode):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    else:
        return hashlib.sha256(data).hexdigest()
        

def is_number(data):
    """Test if data is number"""
    try:
        float(data)
        return True
    except ValueError:
        return False
    
    
    

