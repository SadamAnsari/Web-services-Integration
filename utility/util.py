#!/usr/bin/python
import re

def is_https(url):
    return False if None == re.match("https",url,re.IGNORECASE) else True

def add_http(url, is_secure=False):
    http_str = ""
    if None == re.match("^https?://",url,re.IGNORECASE):
        http_str = "https://" if is_secure else "http://"
    
    return ( "%s%s" % (http_str, url) )
