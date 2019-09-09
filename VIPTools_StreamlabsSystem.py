#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import time
from pprint import pprint

from datetime import datetime

import clr
#   Import your Settings class
from Settings_Module import MySettings

sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------
#   [Required] Script Information
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------
ScriptName = "VIPTools"
Website = "https://twitch.tv/rialDave/"
Description = "Adds new features for Twitchs VIP functionality"
Creator = "rialDave"
Version = "0.0.1-dev"
CommandListVips = "!listvips"
# CommandVIPCheckIn = "!vipcheckin"
VariableChannelName = "$channelName"
VariableVipList = "$vips"
Response = "The current VIPs of " + VariableChannelName + " are: " + VariableVipList

#---------------------------
#   Define Global Variables
#---------------------------
vipdataFile = os.path.join('data', 'vipdata.json')
vipdataFilepath = os.path.join(os.path.dirname(__file__), vipdataFile)

# Configuration of keys in json file
# tbd

#---------------------------
#   [Required] Initialize Data (Only called on load of script)
#---------------------------
def Init():

    #   Checks if vipdataFile exists, if it doesnt: creates it
    if os.path.isfile(vipdataFilepath) == 0:
        data = {}
        with open(vipdataFilepath, 'w') as f:
            json.dump(data, f, indent=4)

    Log('in init')

    # for debugging purposes: log available methods from Parent object
    for method_name in dir(Parent):
        Log(method_name)

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    Log('in execute')
    if data.IsChatMessage() and data.GetParam(0).lower() == CommandListVips:
        ParsedResponse = Parse(Response) # Parse response first
        Parent.SendStreamMessage(ParsedResponse) # Send your message to chat

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#   Runs basically every millisecond since the script is activated^^
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters)
#   Here's where the magic happens, all the strings are sent and processed through this function
#   
#   Parent.FUNCTION allows to use functions of the Chatbot and other outside APIs (see: https://github.com/AnkhHeart/Streamlabs-Chatbot-Python-Boilerplate/wiki/Parent)
#
# ORIGINAL DEF: def Parse(parseString, userid, username, targetid, targetname, message):
#---------------------------
def Parse(parseString):
    Log('in parse')

    # after every necessary variable was processed: return the whole parseString
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

#---------------------------
#   Log helper
#---------------------------
def Log(message):
    Parent.Log(ScriptName, message)
    return