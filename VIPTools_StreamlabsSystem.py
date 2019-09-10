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

#---------------------------
#   Define Global Variables
#---------------------------
vipdataFile = os.path.join('data', 'vipdata.json')
vipdataFilepath = os.path.join(os.path.dirname(__file__), vipdataFile)

VariableChannelName = "$channelName"
VariableVipList = "$vips"
VariableUser = "$user"
VariableCheckInCount = "$checkInCount"
VariableCheckInCountReadable = "$checkInCountReadable"
VariableNeededCheckins = "$neededCheckIns"
CommandListVips = "!listvips"
ResponseListVips = "The current VIPs of " + VariableChannelName + " are: " + VariableVipList
CommandVIPCheckIn = "!vipcheckin"
ResponseVIPCheckIn = "Great! " + VariableUser + " just checked in for the " + VariableCheckInCountReadable + " time in a row! Status: " + VariableCheckInCount + "/" + VariableNeededCheckins
ChannelId = "159000697"
AppClientId = "znnnk0lduw7lsppls5v8kpo9zvfcvd"

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
    
    lastStreamDate = GetLastStreamDate()

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):

    # call parse function if any of our defined commands is called
    if data.IsChatMessage() and data.GetParam(0).lower() == CommandListVips:
        ParsedResponse = Parse(ResponseListVips, CommandListVips) # Parse response first
        Parent.SendStreamMessage(ParsedResponse) # Send your message to chat

    if data.IsChatMessage() and data.GetParam(0).lower() == CommandVIPCheckIn:
        ParsedResponse = Parse(ResponseVIPCheckIn, CommandVIPCheckIn) # Parse response first
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
def Parse(parseString, command):
    Log('in parse')

    if (command == CommandVIPCheckIn):
        Log('last stream date: ' + GetLastStreamDate())

    if (command == CommandListVips):
        Log('in parse for CommandListVips')

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

#---------------------------
#   Gets date of last stream for channel
#---------------------------
def GetLastStreamDate():
    requestUrl = "https://api.twitch.tv/kraken/channels/" + ChannelId + "/videos?limit=1&client_id=" + AppClientId
    lastStream = Parent.GetRequest(requestUrl, {})
    parsedLastStream = json.loads(lastStream)
    dataResponse = parsedLastStream["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict, contents: _total, videos
    dataVideos = parsedDataResponse.get("videos") # list

    for item in dataVideos: # item = dict in dataVideos = list
        dataCreatedAt = item.get("created_at")

    return dataCreatedAt