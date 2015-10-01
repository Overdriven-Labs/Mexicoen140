#!/usr/bin/env python
# -*- coding: latin-1 -*-

######################################################################

import re
import htmlentitydefs

######################################################################

emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# The components of the tokenizer:
regex_strings = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?            
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?    
      \d{3}          # exchange
      [\-\s.]*   
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    emoticon_string
    ,    
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[\w][\w'\-_]+[\w])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots. 
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
    )

######################################################################
# This is the core tokenizing regex:
    
word_re = re.compile(r"""(%s)""" % "|".join(regex_strings), re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can preserve case for them as needed:
emoticon_re = re.compile(regex_strings[1], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
html_entity_digit_re = re.compile(r"&#\d+;")
html_entity_alpha_re = re.compile(r"&\w+;")
amp = "&amp;"

######################################################################

class Tokenizer:
    def __init__(self, preserve_case=False, remove_urls=True):
        self.preserve_case = preserve_case
        self.remove_urls = remove_urls

    def tokenize(self, s):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list returns the original string if preserve_case=False
        """        
        # Try to ensure unicode:
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = str(s).encode('string_escape')
            s = unicode(s)
        # Fix HTML character entitites:
        s = self.__html2unicode(s)
        # remove URLS
        if (self.remove_urls):
            s = ' '.join([w for w in s.split() if not w.lower().startswith('http')])
        # Tokenize:
        words = word_re.findall(s)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:            
            words = map((lambda x : x if emoticon_re.search(x) else x.lower()), words)
        return words

    def __html2unicode(self, s):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        # First the digits:
        ents = set(html_entity_digit_re.findall(s))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    s = s.replace(ent, unichr(entnum))	
                except:
                    pass
        # Now the alpha versions:
        ents = set(html_entity_alpha_re.findall(s))
        ents = filter((lambda x : x != amp), ents)
        for ent in ents:
            entname = ent[1:-1]
            try:            
                s = s.replace(ent, unichr(htmlentitydefs.name2codepoint[entname]))
            except:
                pass                    
            s = s.replace(amp, " and ")
        return s

###############################################################################

if __name__ == '__main__':
    tok = Tokenizer(preserve_case=False, remove_urls=True)
    samples = (
        u'He publicado una foto nueva en Facebook http://t.co/Jk8b1dUZWN',
        u'He publicado una foto nueva en Facebook http://t.co/RkhCqOFJta',
        u'en la parada listo para salir, esperando algo q pasara http://t.co/DOHDptsPB7',
        u'#QuintanaRoo participa este 2015 en las ferias de turismo m\xe1s importantes, generando contacto con m\xe1s de 1000 agencias y tour operadoras.',
        u'Rumbo al @PCTYUC a dar inicio al programa de certificaci\xf3n de profesionales en programaci\xf3n con M\xe9xico First \u201cTalento TI Yucat\xe1n\u201d. @CANIETI',
        u'Durante el primer trimestre del a\xf1o la industria tur\xedstica de #Canc\xfan obtuvo una derrama econ\xf3mica de 1,408 MDD.',
        u'Cumplimos con nuestro deber de dar por iguales a los m\xe1s alejados de los alejados y vamos por m\xe1s http://t.co/NMptCkVHfz',
        u'Entrega de becas universal de Huajicori, hasta lo m\xe1s lejano de la SIERRA. http://t.co/dVliIy9bBV',
        u'RT @omardelasse: Hoy en Patios d la Estaci\xf3n 15hrs daremos muestra d la participaci\xf3n comunitaria. #Morelos #NosMuevelaPaz #Cuernavaca http\u2026'
        )

    for s in samples:
        print "======================================================================"
        print s
        tokenized = tok.tokenize(s)
        print "\n".join(tokenized)

