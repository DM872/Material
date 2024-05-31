# -*- coding: utf-8 -*-
from enum import Enum
import re
import sys
from typing import List 

class DayNotAllowed(BaseException):
    # Constructor or Initializer
    def __init__(self, value: str) -> None:
        self.value = value
 
    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.value))    



class Session(Enum):
    ORDINARY=0
    REEXAM=1

def is_NAT_code(_in):
    return _in[0].isalpha() and _in[-1].isdigit() and (_in[0]!="N" or _in[0:3] == "NAT") and (_in.find("-")<0) and len(_in)<=6

def is_EKA_code(_in):
    return _in[-1]=='2' and (_in[0].isdigit() or (_in[0] in ["N","S","T"] and _in[0:3] != "NAT" and len(_in)==10) or _in[0:3]=="MC-")

def parse_type(_type: str) -> str:
    oral = ["oral", "mundtlig", "fremlæggelse"]
    written = ["written", "skriftlig", "multiple choice","elektronisk"]
    deliverables = ["bachelorprojekt","kandidatspeciale"]

    oral += [x.capitalize() for x in oral]
    written += [x.capitalize() for x in written]
    deliverables += [x.capitalize() for x in deliverables]
    stype = 'u'
    if any([_type.find(w) >= 0 for w in deliverables]):
        stype='u'
    elif any([_type.find(w) >= 0 for w in oral]):
        stype = 'm'
    elif any([_type.find(w) >= 0 for w in written]):
        stype = 's'
    return stype


def parse_title(_title):
    parts = _title.split(":",maxsplit=1)
    if len(parts)<2:
        return _title.strip()
    code = parts[0].strip()
    if is_NAT_code(code):
        return parts[1].strip()
    return(_title)

def parse_NAT_code(_title):
    parts = _title.split(":",maxsplit=1)
    if len(parts)<2:
        return ""
    code = parts[0].strip()
    if is_NAT_code(code):
        return code
    return ""


def is_among(word, keywords):
    '''
    return true if the word starts with exactly one of the words i keywords
    '''
    for w in keywords:
        if re.search('^'+w,word) is not None:
            return True
    return False


def continue_question(text=""):
    if input(f"\n {text} Continue? [yY] ") in ["y", "Y", ""]:
        sys.stdout.write("OK")
    else:
        sys.exit(0)


def fixed_dates_not_given(entry: dict) -> bool:
        return 'Faste datoer' not in entry or len(entry['Faste datoer'])==0
