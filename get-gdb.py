#!/usr/bin/python
# -*- coding: utf-8 -*-

GDB_VERSION_LIST = ()

class Lang(object):
    '''Language class.'''
    def __init__(self, language="en"):
        self.data = {}
        self.language = language
        self.is_set = False
        self.add('Please install "%s" before go to next step.',
                 '在进行下一步以前请先安装软件包"%s"。')

    def set_language(self, language):
        if language != "":
	    if self.language[0] == "e" or self.language[0] == "E":
		self.language = "en"
	    else:
	        self.language = "cn"
            self.is_set = True

    def add(self, en, cn):
        self.data[en] = cn

    def string(self, s):
        if self.language == "en" or (not self.data.has_key(s)):
            return s
        return self.data[s]

def select_from_list(entry_list, default_entry, introduction):
    if type(entry_list) == dict:
	entry_dict = entry_list
	entry_list = list(entry_dict.keys())
	entry_is_dict = True
    else:
	entry_is_dict = False
    while True:
        default = -1
        default_str = ""
        for i in range(0, len(entry_list)):
	    if entry_is_dict:
                print("[%d] %s %s" %(i, entry_list[i], entry_dict[entry_list[i]]))
            else:
		print("[%d] %s" %(i, entry_list[i]))
            if default_entry != "" and entry_list[i] == default_entry:
                default = i
                default_str = "[%d]" %i
        try:
            select = input(introduction + default_str)
        except SyntaxError:
            select = default
        except Exception:
            select = -1
        if select >= 0 and select < len(entry_list):
            break
    return entry_list[select]

lang = Lang()
lang.set_language(select_from_list(("English", "Chinese"), "", "Which language do you want to use?"))

