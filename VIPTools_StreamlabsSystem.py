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
Version = "0.2.1"

#---------------------------
#   Global Variables
#---------------------------
vipdataFile = os.path.join('data', 'vipdata.json')
vipdataFilepath = os.path.join(os.path.dirname(__file__), vipdataFile)

VariableChannelName = "$channelName"
VariableVipList = "$vips"
VariableUser = "$user"
VariableCheckInCount = "$checkInCount"
VariableCheckInCountReadable = "$checkInCountReadable"
VariableNeededCheckins = "$neededCheckIns"
ChannelId = "159000697"
AppClientId = "znnnk0lduw7lsppls5v8kpo9zvfcvd"

# Configuration of keys in json file
JSONVariablesCheckInsInARow = "check_ins_in_a_row"
JSONVariablesLastCheckIn = "last_check_in"
JSONVariablesLastCheckInStreamId = "last_check_in_streamid"
JSONVariablesRemainingJoker = "remaining_joker"

# Configuration of twitch api urls
ApiUrlLastStream = str("https://api.twitch.tv/kraken/channels/" + ChannelId + "/videos?limit=2&client_id=" + AppClientId)
ApiUrlCurrentStream = str("https://api.twitch.tv/kraken/streams/" + ChannelId + "?client_id=" + AppClientId)

#---------------------------
#   Settings
#---------------------------

CommandListVips = "!listvips"
ResponseListVips = "The current VIPs of " + VariableChannelName + " are: " + VariableVipList
CommandVIPCheckIn = "!vipcheckin"
ResponseVIPCheckIn = "Great! " + VariableUser + " just checked in for the " + VariableCheckInCountReadable + " time in a row! Status: " + VariableCheckInCount + "/" + VariableNeededCheckins

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
    
    Log("initialized")

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):

    # call parse function if any of our defined commands is called
    if (data.IsChatMessage() and data.GetParam(0).lower() == CommandVIPCheckIn):
        currentStreamObjectStorage = GetTwitchApiResponse(ApiUrlCurrentStream)
        currentStreamObject = GetStreamObjectByObjectStorage(currentStreamObjectStorage)
        if (currentStreamObject == None):
            Parent.SendStreamMessage("ERROR: This command is only available, when the stream is live. Sorry!")
            return

        ParsedResponse = Parse(ResponseVIPCheckIn, CommandVIPCheckIn, data) # Parse response
        Parent.SendStreamMessage(ParsedResponse) # Send your message to chat

    if (data.IsChatMessage() and data.GetParam(0).lower() == CommandListVips):
        ParsedResponse = Parse(ResponseListVips, CommandListVips, data) # Parse response
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
def Parse(parseString, command, data):
    Log('in parse')

    if (command == CommandVIPCheckIn):
        parseString = UpdateDataFile(data.User)

        if ("error" != parseString):
            parseString = parseString + GetStats(data.User)

    if (command == CommandListVips):
        Log('in parse for CommandListVips')

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
    Parent.Log(ScriptName, str(message))
    return

#---------------------------
#   Gets stream id of last stream for channel
#---------------------------
def GetLastStreamId():
    lastVideosObjectStorage = GetTwitchApiResponse(ApiUrlLastStream)
    lastVideoObject = GetVideoOfVideoObjectStorageByListId(lastVideosObjectStorage, 1)
    lastStreamId = lastVideoObject.get("broadcast_id")

    return lastStreamId

#---------------------------
#   Gets stream id of current stream for channel
#---------------------------
def GetCurrentStreamId():
    
    currentStreamObjectStorage = GetTwitchApiResponse(ApiUrlCurrentStream)
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
    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        # check if the given username exists in data. -> user doesnt exist yet, create array of the user data, which will be stored in vipdata.json
        if (True == IsNewUser(username)):
            data[str(username.lower())] = {}
            data[str(username.lower())][JSONVariablesCheckInsInARow] = 1
            data[str(username.lower())][JSONVariablesLastCheckIn] = currentday
            data[str(username.lower())][JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
            data[str(username.lower())][JSONVariablesRemainingJoker] = 2

            # directly return it, because "isnewstream" would be technically true as well but not correct in this case
            response = "Congratulations for you first check in, " + username + "! When you reach a streak of 30 check ins in a row, you'll have the chance to get the VIP badge (you have two jokers if you miss some streams). Good luck! "

        # if the user already exists, update the user with added checkIn count, but we need to check here if it's the first beer today or not to set the right values 
        else:
            # new stream since last checkIn?
            if (True == IsNewStream(username)):
                
                # ongoing check in (no missed stream)?
                if (True == IsLastCheckinLastStream(username)):
                    data[str(username.lower())][JSONVariablesCheckInsInARow] += 1
                    data[str(username.lower())][JSONVariablesLastCheckIn] = currentday
                    data[str(username.lower())][JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()

                    response = username + ' just checked in for this stream! '
                else:
                    # joker available?
                    if (GetJoker(username) > 0):
                        data[str(username.lower())][JSONVariablesCheckInsInARow] += 1
                        data[str(username.lower())][JSONVariablesLastCheckIn] = currentday
                        data[str(username.lower())][JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
                        data[str(username.lower())][JSONVariablesRemainingJoker] -= 1

                        response = username + ' just checked in for this stream, but needed to use a joker! '
                    else:
                        data[str(username.lower())][JSONVariablesCheckInsInARow] = 1
                        data[str(username.lower())][JSONVariablesLastCheckIn] = currentday
                        data[str(username.lower())][JSONVariablesLastCheckInStreamId] = GetCurrentStreamId()
                        data[str(username.lower())][JSONVariablesRemainingJoker] = 2

                        response = "Daaamn " + username + ", you wasted all your jokers. Now you're starting from scratch! Come join again the next time and don't miss a stream again! "
            else:
                response = username + ' already checked in for this stream. Come join again the next time! '

    # after everything was modified and updated, we need to write the stuff from our "data" variable to the beerdata.json file 
    os.remove(vipdataFilepath)
    with open(vipdataFilepath, 'w') as f:
        json.dump(data, f, indent=4)

    return response

#---------------------------
#   returns bool if it is a new stream or not
#---------------------------
def IsNewStream(username):
    newStream = False

    # this loads the data of file vipdata.json into variable "data"
    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        lastCheckInStreamId = data[str(username.lower())][JSONVariablesLastCheckInStreamId]
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
    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        lastCheckInStreamId = data[str(username.lower())][JSONVariablesLastCheckInStreamId]
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

    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            streak = "1/30"
        else:
            streak = str(data[str(username.lower())][JSONVariablesCheckInsInARow]) + "/30"

    return streak

#---------------------------
#   returns the remaining joker int
#---------------------------
def GetJoker(username):

    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            joker = 2
        else:
            joker = str(data[str(username.lower())][JSONVariablesRemainingJoker])

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
    parsedLastVideo = json.loads(videoObjectStorage)
    dataResponse = parsedLastVideo["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict, contents: _total, videos
    videosList = parsedDataResponse.get("videos") # list
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
    with open(vipdataFilepath, 'r') as f:
        data = json.load(f)

        if str(username.lower()) not in data:
            return True
        else:
            return False

#---------------------------
# GetStats
#---------------------------
def GetStats(username):
    return 'Current streak: ' + str(GetStreak(username)) + ' | Remaining joker: ' + str(GetJoker(username))