#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
# twitchLib Module
#
# Contains some helpful functions for Twitch API stuff
#---------------------------

import os
import json
import config

#---------------------------
#   returns the response from api request
#---------------------------
def GetTwitchApiResponse(url, Parent, UserSettings):
    headers = {
        "Authorization": "Bearer " + GetCurrentAccessToken(),
        "Client-Id": UserSettings.AppClientId
    }
    return Parent.GetRequest(url, headers)

#---------------------------
#   returns the combined URL for last streams including the user defined ChannelId
#---------------------------
def GetApiUrlLastStreams(UserSettings):
    return config.ApiUrlLastStreamsBase + "&user_id=" + UserSettings.ChannelId

#---------------------------
#   returns the combined URL for current stream of channel
#---------------------------
def GetApiUrlCurrentStream(UserSettings):
    return config.ApiUrlCurrentStream + "?user_id=" + UserSettings.ChannelId

#---------------------------
#   helper function to log all variables of last stream object (debugging)
#---------------------------
def LogAllVariablesOfVideoObject(videoObject, Parent):
    for attributes in videoObject:
        Parent.Log(Parent.ScriptName, attributes)

    return

#---------------------------
#   Gets specified attribute value of given stream by list id (offset index to the current stream)
#---------------------------
def GetAttributeByVideoListId(attribute, listId, Parent, UserSettings):
    lastVideosObjectStorage = GetTwitchApiResponse(GetApiUrlLastStreams(UserSettings), Parent, UserSettings)
    videoObject = GetVideoOfVideoObjectStorageByListId(lastVideosObjectStorage, listId, Parent)

    return videoObject.get(str(attribute))

#---------------------------
#   Gets stream id of current stream for channel
#---------------------------
def GetCurrentStreamId(Parent, UserSettings):
    currentStreamObjectStorage = GetTwitchApiResponse(GetApiUrlCurrentStream(UserSettings), Parent, UserSettings)
    currentStreamObject = GetStreamObjectByObjectStorage(currentStreamObjectStorage, Parent)
    return int(currentStreamObject[0].get("id"))

#---------------------------
#   GetVideoOfVideoObjectStorageByListId
#   hint: listId 0 = current stream
#---------------------------
def GetVideoOfVideoObjectStorageByListId(videoObjectStorage, listId, Parent):
    listId = int(listId) # let's be safe here

    parsedLastVideo = json.loads(videoObjectStorage)
    dataResponse = parsedLastVideo["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict, contents: _total, videos
    videosList = parsedDataResponse.get("data") # list

    while (int(videosList[listId].get("id")) == 1 or videosList[listId].get("status") == "recording"):
        
        if (listId >= int(Parent.ApiVideoLimit)):
            Parent.Log(Parent.ScriptName, "Failed to find valid stream object in list of defined last videos of channel")
            break

        listId += 1

    return videosList[listId] # dict

#---------------------------
#   GetStreamObjectByObjectStorage
#---------------------------
def GetStreamObjectByObjectStorage(streamObjectStorage, Parent):
    parsedStreamObjectStorage = json.loads(streamObjectStorage)
    dataResponse = parsedStreamObjectStorage["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict
    return parsedDataResponse.get("data")

def GetCurrentStreamObject(Parent, UserSettings):
    currentStreamObjectStorage = GetTwitchApiResponse(GetApiUrlCurrentStream(UserSettings), Parent, UserSettings)
    return GetStreamObjectByObjectStorage(currentStreamObjectStorage, Parent) 

#
# Access Token Shizzle
#

def GetCurrentAccessToken():
    f = open(config.TokenFile)
    return str(f.readlines()[0])

def IsTokenValid(Parent, Token):
    headers = {"Authorization": "Bearer " + Token}
    result = Parent.GetRequest("https://id.twitch.tv/oauth2/validate", headers)
    parsedResult = json.loads(result)

    if (200 == parsedResult["status"]):
        Parent.Log(config.ScriptName, "Token still valid")
        return True
    else:
        Parent.Log(config.ScriptName, "Token invalid, getting new one..")
        return False

def GetNewAccessToken(Parent, UserSettings):
    result = Parent.PostRequest("https://id.twitch.tv/oauth2/token?client_id=" + UserSettings.AppClientId + "&client_secret=" + UserSettings.AppSecret + "&grant_type=client_credentials&scope=channel:manage:videos channel:manage:broadcast", {}, {}, True)
    parsedResult = json.loads(result)
    if (200 == parsedResult["status"]):
        dataResponse = parsedResult["response"] #str
        parsedDataResponse = json.loads(dataResponse) # dict

        return parsedDataResponse["access_token"]
    else:
        Parent.Log(config.ScriptName, "Got error when trying to get a new access token:" + str(parsedResult))

def WriteNewAccessToken(Parent, UserSettings): 
    data = {"token": GetNewAccessToken(Parent, UserSettings)}
    with open(config.TokenFile, 'w') as f:
        f.write(GetNewAccessToken(Parent, UserSettings))
        f.close
        Parent.Log(config.ScriptName, "Wrote new access token")
        return True

def CheckAndRefreshAccessToken(Parent, UserSettings):
    if (True == os.path.isfile(config.TokenFile) and 0 != os.stat(config.TokenFile).st_size):
        if (False == IsTokenValid(Parent, GetCurrentAccessToken())): 
            WriteNewAccessToken(Parent, UserSettings)
    else: 
        Parent.Log(config.ScriptName, "Access token didn't exist yet, generating new one..")
        WriteNewAccessToken(Parent, UserSettings)