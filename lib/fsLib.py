#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
# fsLib Module
#
# Contains some helpful functions for filesystem stuff
#---------------------------

import os
from definitions import ROOT_DIR

#---------------------------
# GetFilepathInFolder
#
# Returns the (os) path for given folderpath (str) and filename (str)
#---------------------------
def GetFilepathInFolder(folderpath, filename):
    file = os.path.join(ROOT_DIR, folderpath, filename)
    return os.path.join(os.path.dirname(__file__), file)