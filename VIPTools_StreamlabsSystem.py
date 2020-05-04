#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
import time
import collections
from pprint import pprint
from shutil import copyfile

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

# Load own modules
sys.path.append(os.path.dirname(__file__)) # point at current folder for classes / references
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) # point at lib folder for classes / references

from definitions import ROOT_DIR
import config
import miscLib
import twitchLib


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
    # generate data and archive directory if they don't exist (uses VipdataBackupPath because it includes the data path)
    if (False == os.path.isdir(config.VipdataBackupPath)):
        os.makedirs(config.VipdataBackupPath)

    # Creates an empty data file if it doesn't exist
    if (False == os.path.isfile(config.VipdataFilepath)):
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
    currentStreamObjectStorage = twitchLib.GetTwitchApiResponse(config.ApiUrlCurrentStream, Parent)
    currentStreamObject = twitchLib.GetStreamObjectByObjectStorage(currentStreamObjectStorage)

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


    # top10vipcheckins command called
    if (data.IsChatMessage() and data.GetParam(0).lower() == config.CommandTop10Vipcheckins):
        top10vipcheckinsMessage = GetTop10VipcheckinsWithData()
        Parent.SendStreamMessage(str(top10vipcheckinsMessage)) # Send your message to chat

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
    # if vipcheckin command is called
    if (command == config.CommandVIPCheckIn):
        parseString = UpdateDataFile(data.User)

        if ("error" != parseString):
            parseString = parseString + GetStats(data.User)

    # if CommandResetAfterReconnect is called
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
#   Note that you need to pass the "Parent" object and use the normal "Parent.Log" function if you want to log something inside of a module
#---------------------------
def Log(message):
    Parent.Log(ScriptName, str(message))
    return

#---------------------------
#   UpdateDataFile: Function for modfiying the file which contains the data, see data/vipdata.json
#   returns the parseString for parse(Function)
#---------------------------
def UpdateDataFile(username):
    currentday = miscLib.GetCurrentDayFormattedDate()
    response = "error"

    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        # check if the given username exists in data. -> user doesnt exist yet, create array of the user data with current default values, which will be stored in vipdata.json
        if (True == IsNewUser(username)):
            data[str(username.lower())] = {}
            data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
            data[str(username.lower())][config.JSONVariablesRemainingJoker] = 2
            data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] = 1
            data[str(username.lower())][config.JSONVariablesHighestCheckInStreakDate] = currentday

            # directly return it, because "isnewstream" would be technically true as well but not correct in this case
            response = "Congratulations for your first check in, " + username + "! When you reach a streak of 30 check ins in a row, you'll have the chance to get the VIP badge (you have two jokers if you miss some streams). Good luck! Hint: type '/vips' to list all current VIPs of this channel. "

        # if the user already exists, update the user with added checkIn count, but we need to check here if it's the first beer today or not to set the right values 
        else:
            if (data[str(username.lower())][config.JSONVariablesCheckInsInARow]):

                # for existing users: check and set highest streak to current streak
                if (data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] < data[str(username.lower())][config.JSONVariablesCheckInsInARow]):
                    data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] = data[str(username.lower())][config.JSONVariablesCheckInsInARow]
                    data[str(username.lower())][config.JSONVariablesHighestCheckInStreakDate] = data[str(username.lower())][config.JSONVariablesLastCheckIn]

                # new stream since last checkIn?
                if (True == IsNewStream(username)):
                    
                    # ongoing check in (no missed stream)?
                    if (True == EqualsLastCheckinGivenStreamByListId(username, 1)):
                        data[str(username.lower())][config.JSONVariablesCheckInsInARow] += 1
                        data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                        data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
                        # only count highest streak counter up if it's actually lower than the checkins
                        if (data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] < data[str(username.lower())][config.JSONVariablesCheckInsInARow]):
                            data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] = data[str(username.lower())][config.JSONVariablesCheckInsInARow]
                            data[str(username.lower())][config.JSONVariablesHighestCheckInStreakDate] = data[str(username.lower())][config.JSONVariablesLastCheckIn]

                        response = username + ' just checked in for this stream! '
                    else:
                        # joker available?
                        if (GetJoker(username) > 0):
                            data[str(username.lower())][config.JSONVariablesCheckInsInARow] += 1
                            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
                            data[str(username.lower())][config.JSONVariablesRemainingJoker] -= 1
                            # only count highest streak counter up if it's actually lower than the checkins
                            if (data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] < data[str(username.lower())][config.JSONVariablesCheckInsInARow]):
                                data[str(username.lower())][config.JSONVariablesHighestCheckInStreak] = data[str(username.lower())][config.JSONVariablesCheckInsInARow]
                                data[str(username.lower())][config.JSONVariablesHighestCheckInStreakDate] = data[str(username.lower())][config.JSONVariablesLastCheckIn]

                            response = username + ' just checked in for this stream, but needed to use a joker! '
                        else:
                            data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
                            data[str(username.lower())][config.JSONVariablesLastCheckIn] = currentday
                            data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
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
        currentStreamId = twitchLib.GetCurrentStreamId(Parent)

        if (currentStreamId != lastCheckInStreamId):
            return True

    return newStream

#---------------------------
#   returns bool if the last checkin was in the same stream as given by listid (offset of saved streams)
#---------------------------
def EqualsLastCheckinGivenStreamByListId(username, listId):
    # this loads the data of file vipdata.json into variable "data"
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        lastCheckInStreamId = data[str(username.lower())][config.JSONVariablesLastCheckInStreamId]
        secondLastStreamId = twitchLib.GetAttributeByVideoListId("broadcast_id", listId, Parent)

        if (secondLastStreamId == lastCheckInStreamId):
            return True

    return False

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
            # if user already checked in before reconnection
            if (EqualsLastCheckinGivenStreamByListId(user.lower(), 1) == True):
                Log('This user checked in, in the last stream object and will be reset:')
                Log(user)
                data[user][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
                data[user][config.JSONVariablesLastCheckIn] = miscLib.GetCurrentDayFormattedDate()
            # if user didn't check in before reconnection, but checked in in the last real stream (second last stream)
            if (EqualsLastCheckinGivenStreamByListId(user.lower(), 2) == True):
                Log('This User checked in in the second last stream object and will be reset:')
                Log(user)
                data[user][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetAttributeByVideoListId("broadcast_id", 1, Parent)
                data[user][config.JSONVariablesLastCheckIn] = twitchLib.GetAttributeByVideoListId("recorded_at", 1, Parent)[0:10] # only use the first 10 digits, because working with RFC3339 in python is......
                

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the vipdata.json file     
    os.remove(config.VipdataFilepath)
    with open(config.VipdataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return "Okay, I've reset the checkins from last stream to the current stream."

#---------------------------
# IsVip
#
# Returns 0 or 1 if a given user is a VIP or not (in our datafile)
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

        data[str(username.lower())][config.JSONVariablesCheckInsInARow] = 1
        data[str(username.lower())][config.JSONVariablesLastCheckIn] = miscLib.GetCurrentDayFormattedDate()
        data[str(username.lower())][config.JSONVariablesLastCheckInStreamId] = twitchLib.GetCurrentStreamId(Parent)
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
    if (True == os.path.isfile(config.VipdataFilepath)):

        if (False == os.path.isdir(config.VipdataBackupPath)):
            os.makedirs(config.VipdataBackupPath)

        dstFilename = config.VipdataBackupFilePrefix + str(miscLib.GetCurrentDayFormattedDate()) + "_" + str(int(time.time())) + ".json"
        dstFilepath = os.path.join(config.VipdataBackupPath, dstFilename)
        copyfile(config.VipdataFilepath, dstFilepath)
    
    return

#---------------------------
# GetTop10Vipcheckins
#
# Returns a list of all top 10 vipcheckin users sorted by checkins to be iterated
#---------------------------
def GetTop10Vipcheckins():
    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        # build sortableDict with user and checkin count like "user: checkins"
        sortableCheckinsDict = {}
        for user in data:
            sortableCheckinsDict[user] = data[user][config.JSONVariablesCheckInsInARow]

    # sort it by checkins and put it in a list of max 10 items
    sortedCheckinsList = sorted(sortableCheckinsDict.items(), key=lambda x: x[1], reverse=True)
    sortedCheckinsDict = collections.OrderedDict(sortedCheckinsList)
    
    # only the first 10 items
    return sortedCheckinsDict.keys()[:10]

#---------------------------
# GetTop10VipcheckinsWithData
#
# Returns a complete string of all top 10 vipcheckin users sorted by checkins and with data (checkins)
#---------------------------
def GetTop10VipcheckinsWithData():
    top10Vipcheckins = GetTop10Vipcheckins()
    top10VipcheckinsWithData = config.ResponseTop10Vipcheckins

    with open(config.VipdataFilepath, 'r') as f:
        data = json.load(f)

        position = 0
        for checkinUser in top10Vipcheckins:
            position += 1
            top10VipcheckinsWithData += "#" + str(position) + " "
            top10VipcheckinsWithData += str(checkinUser)
            top10VipcheckinsWithData += " (" + str(data[checkinUser][config.JSONVariablesCheckInsInARow]) + ")"
            top10VipcheckinsWithData += " [" + config.VIPStatusLocalizationSimple[int(IsVip(checkinUser))] + "]"
            
            # only display dash below last position
            if (position < 10):
                 top10VipcheckinsWithData += " - "

    return top10VipcheckinsWithData