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

from shutil import copyfile

import clr

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# Load own modules
sys.path.append(os.path.dirname(__file__)) # point at current folder for classes / references
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) # point at lib folder for classes / references

from definitions import ROOT_DIR
import config
import fsLib


#---------------------------
#   [Required] Script Information (must be existing in this main file)
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------
ScriptName = config.ScriptName
Website = config.Website
Description = config.Description
Creator = config.Creator
Version = config.Version

#############################################
# START: Generic Chatbot functions
#############################################

#---------------------------
#   [Required] Initialize Data (Only called on load of script)
#---------------------------
def Init():
    #   Checks if vipdataFile exists, if it doesnt: creates it
    if os.path.isfile(config.VipdataFilepath) == 0:
        # TODO: generate data and archive directory

        # generate empty data file and save it
        data = {}
        with open(config.VipdataFilepath, 'w') as f:
            json.dump(data, f, indent=4)
    
    Log("Script successfully initialized")

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    currentStreamObjectStorage = GetTwitchApiResponse(config.ApiUrlCurrentStream)
    currentStreamObject = GetStreamObjectByObjectStorage(currentStreamObjectStorage)

    # call parse function if any of our defined commands is called
    # vipcheckin command called
    if (data.IsChatMessage() and data.GetParam(0).lower() == config.CommandVIPCheckIn):
        if (currentStreamObject == None):
            Parent.SendStreamMessage(config.ResponseOnlyWhenLive)
            return

        ParsedResponse = Parse(config.ResponseVIPCheckIn, config.CommandVIPCheckIn, data) # Parse response
        Parent.SendStreamMessage(ParsedResponse) # Send your message to chat

    # reset after reconnect command called
    if (data.IsChatMessage() and data.GetParam(0).lower() == config.CommandResetAfterReconnect):
        if (currentStreamObject == None):
            Parent.SendStreamMessage(config.ResponseOnlyWhenLive)
            return
        else:
            if (True == Parent.HasPermission(data.User, "Moderator", "")):
                ParsedResponse = Parse(config.ResponseResetAfterReconnect, config.CommandResetAfterReconnect, data) # Parse response
                Parent.SendStreamMessage(ParsedResponse) # Send your message to chat
            else:
                Parent.SendStreamMessage(config.ResponsePermissionDeniedMod)
                return

    # reset checkIns command called
    if (data.IsChatMessage() and data.GetParam(0).lower() == config.CommandResetCheckIns):
        if (currentStreamObject == None):
            Parent.SendStreamMessage(config.ResponseOnlyWhenLive)
            return

        if (1 == ResetCheckinsForUser(data.User)):
            Parent.SendStreamMessage(config.ResponseResetCheckIns) # Send your message to chat

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
def Parse(parseString, command, data):
    if (command == config.CommandVIPCheckIn):
        parseString = UpdateDataFile(data.User)

        if ("error" != parseString):
            parseString = parseString + GetStats(data.User)

    if (command == config.CommandResetAfterReconnect):
        parseString = FixDatafileAfterReconnect()

    # after every necessary variable was processed: return the whole parseString, if it wasn't already
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
    Log("Script unloaded")
    BackupDataFile()
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

#############################################
# END: Generic Chatbot functions
#############################################

#---------------------------
#   Log helper (For logging into Script Logs of the Chatbot)
#---------------------------
def Log(message):
    Parent.Log(ScriptName, str(message))
    return

#---------------------------
#   Gets stream id of last stream for channel
#---------------------------
def GetLastStreamId():
    lastVideosObjectStorage = GetTwitchApiResponse(config.ApiUrlLastStream)
    lastVideoObject = GetVideoOfVideoObjectStorageByListId(lastVideosObjectStorage, 1)
    Log(lastVideoObject.get("broadcast_id"))
    lastStreamId = lastVideoObject.get("broadcast_id")

    return lastStreamId

#---------------------------
#   Gets stream id of current stream for channel
#---------------------------
def GetCurrentStreamId():
    
    currentStreamObjectStorage = GetTwitchApiResponse(config.ApiUrlCurrentStream)
    currentStreamObject = GetStreamObjectByObjectStorage(currentStreamObjectStorage)
    currentStreamId = currentStreamObject.get("_id")

    return currentStreamId

#---------------------------
#   UpdateDataFile: Function for modfiying the file which contains the data, see data/vipdata.json
#   returns the parseString for parse(Function)
#---------------------------
def UpdateDataFile(username):
    currentday = GetCurrentDayFormattedDate()
    response = "error"

    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        # check if the given username exists in data. -> user doesnt exist yet, create array of the user data with current default values, which will be stored in vipdata.json
        if (True == IsNewUser(username)):
            data[str(username.lower())] = {}
            data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
            data[str(username.lower())][config.JSONVariablesRemainingJoker] = 2

            # directly return it, because "isnewstream" would be technically true as well but not correct in this case
            response = "Congratulations for your first check in, " + username + "! When you reach a streak of 30 check ins in a row, you'll have the chance to get the VIP badge (you have two jokers if you miss some streams). Good luck! Hint: type '/vips' to list all current VIPs of this channel. "

        # if the user already exists, update the user with added checkIn count, but we need to check here if it's the first beer today or not to set the right values 
        else:
            if (data[str(username.lower())][config.JSONVariablesCheckInsInARow]):

                # new stream since last checkIn?
                if (True == IsNewStream(username)):
                    
                    # ongoing check in (no missed stream)?
                    if (True == IsLastCheckinLastStream(username)):
                        data[str(username.lower())][config.JSONVariablesCheckInsInARow] += 1
                        data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                        data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()

                        response = username + ' just checked in for this stream! '
                    else:
                        # joker available?
                        if (GetJoker(username) > 0):
                            data[str(username.lower())][config.JSONVariablesCheckInsInARow] += 1
                            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
                            data[str(username.lower())][config.JSONVariablesRemainingJoker] -= 1

                            response = username + ' just checked in for this stream, but needed to use a joker! '
                        else:
                            data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
                            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
                            data[str(username.lower())][config.JSONVariablesRemainingJoker] = 2

                            response = "Daaamn " + username + ", you wasted all your jokers. Now you're starting from scratch! Come join again the next time and don't miss a stream again! "
                else:
                    response = username + ' already checked in for this stream. Come join again the next time! '

    # VIP Status Handler
    if (IsVip(username) == 0):
        if (config.JSONVariablesVIPStatus in data[str(username.lower())]):
            if (data[str(username.lower())][config.JSONVariablesCheckInsInARow] == 30):
                data[str(username.lower())][config.JSONVariablesVIPStatus] = 1
                response = "WHOOP! You've just made it and got 30 VIP check ins in a row. Get in contact with Dave and collect your VIP badge - congrats!"

            else:
                if (data[str(username.lower())][config.JSONVariablesVIPStatus] != 1 and data[str(username.lower())][config.JSONVariablesCheckInsInARow] >= 30):
                    data[str(username.lower())][config.JSONVariablesVIPStatus] = 1
                else:
                    data[str(username.lower())][config.JSONVariablesVIPStatus] = 0
        else:
            data[str(username.lower())][config.JSONVariablesVIPStatus] = 0

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the vipdata.json file 
    os.remove(config.VipdataFilepath)
    with open(config.VipdataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return response + " | VIP-Status: " + config.VIPStatusLocalization[int(IsVip(username))]

#---------------------------
#   returns bool if it is a new stream or not
#---------------------------
def IsNewStream(username):
    newStream = False

    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        lastCheckInStreamId = data[str(username.lower())][config.JSONVariablesLastCheckInStreamId]
        currentStreamId = GetCurrentStreamId()

        if (currentStreamId != lastCheckInStreamId):
            return True

    return newStream

#---------------------------
#   returns bool if the last checkin was in the last stream
#---------------------------
def IsLastCheckinLastStream(username):
    newStream = False

    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        lastCheckInStreamId = data[str(username.lower())][config.JSONVariablesLastCheckInStreamId]
        lastStreamId = GetLastStreamId()

        if (lastStreamId == lastCheckInStreamId):
            return True

    return newStream

#---------------------------
#   returns the formatted date of current day 
#---------------------------
def GetCurrentDayFormattedDate():
    currenttimestamp = int(time.time())
    return datetime.fromtimestamp(currenttimestamp).strftime('%Y-%m-%d')

#---------------------------
#   returns the string formatted streak (still hardcoded)
#---------------------------
def GetStreak(username):

    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            streak = "1/30"
        else:
            streak = str(data[str(username.lower())][config.JSONVariablesCheckInsInARow]) + "/30"

    return streak

#---------------------------
#   returns the remaining joker int
#---------------------------
def GetJoker(username):

    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            joker = 2
        else:
            joker = int(data[str(username.lower())][config.JSONVariablesRemainingJoker])

    return joker

#---------------------------
#   returns the response from api request
#---------------------------
def GetTwitchApiResponse(url):
    headers = {'Accept': 'application/vnd.twitchtv.v5+json'}
    return Parent.GetRequest(url, headers)

#---------------------------
#   helper class to log all variables of last stream object (debugging)
#---------------------------
def LogAllVariablesOfVideoObject(videoObject):
    for attributes in videoObject:
        Log(attributes)

    return

#---------------------------
#   GetVideoOfVideoObjectStorageByListId
#---------------------------
def GetVideoOfVideoObjectStorageByListId(videoObjectStorage, listId):
    listId = int(listId) # let's be safe here

    parsedLastVideo = json.loads(videoObjectStorage)
    dataResponse = parsedLastVideo["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict, contents: _total, videos
    videosList = parsedDataResponse.get("videos") # list

    while (int(videosList[listId].get("broadcast_id")) == 1 or videosList[listId].get("status") == "recording"):
        
        if (listId >= int(config.ApiVideoLimit)):
            Log("Failed to find valid stream object in list of defined last videos of channel")
            break

        listId += 1

    return videosList[listId] # dict

#---------------------------
#   GetStreamObjectByObjectStorage
#---------------------------
def GetStreamObjectByObjectStorage(streamObjectStorage):
    parsedStreamObjectStorage = json.loads(streamObjectStorage)
    dataResponse = parsedStreamObjectStorage["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict
    return parsedDataResponse.get("stream")

#---------------------------
#   IsNewUser
#---------------------------
def IsNewUser(username):
    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            return True
        else:
            return False

#---------------------------
# GetStats
#---------------------------
def GetStats(username):
    return ' | Current streak: ' + str(GetStreak(username)) + ' | Remaining joker: ' + str(GetJoker(username))

#---------------------------
# FixDatafileAfterReconnect
#---------------------------
def FixDatafileAfterReconnect():
    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f) # dict

        for user in data:
            if (IsLastCheckinLastStream(user.lower()) == True):
                data[user][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the vipdata.json file     
    os.remove(config.VipdataFilepath)
    with open(config.VipdataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return "Okay, I've reset the checkins from last stream to the current stream."

#---------------------------
# IsVip
#
# Returns 0 or 1 if a given user is a VIP or not
#---------------------------
def IsVip(username):
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f) # dict

        if str(username.lower()) not in data:
            return 0

        if (config.JSONVariablesVIPStatus in data[str(username.lower())]):
            if (data[str(username.lower())][config.JSONVariablesVIPStatus] == 1):
                return 1

    return 0

#---------------------------
# ResetCheckinsForUser (but not the vip status)
#
# Returns 1 if the function was successful or not
#---------------------------
def ResetCheckinsForUser(username):
    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f) # dict

        currentday = GetCurrentDayFormattedDate()

        data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
        data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
        data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
        data[str(username.lower())][config.JSONVariablesRemainingJoker] = 2

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the vipdata.json file     
    os.remove(config.VipdataFilepath)
    with open(config.VipdataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return 1

#---------------------------
# BackupDataFile
#
# Backups the data file in the "archive" folder with current date and timestamp for ease of use
#---------------------------
def BackupDataFile():
    dstFilename = "vipdata_bak-" + str(GetCurrentDayFormattedDate()) + "_" + str(int(time.time())) + ".json"
    dstFilepath = fsLib.GetFilepathInFolder("data/archive", dstFilename)
    copyfile(config.VipdataFilepath, dstFilepath)