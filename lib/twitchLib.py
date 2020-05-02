#!/usr/bin/python
# -*- coding: utf-8 -*-

#---------------------------
# twitchLib Module
#
# Contains some helpful functions for Twitch API stuff
#---------------------------

import os
import config
import json

#---------------------------
#   returns the response from api request
#---------------------------
def GetTwitchApiResponse(url, Parent):
    headers = {'Accept': 'application/vnd.twitchtv.v5+json'}
    return Parent.GetRequest(url, headers)

#---------------------------
#   helper class to log all variables of last stream object (debugging)
#---------------------------
def LogAllVariablesOfVideoObject(videoObject, Parent):
    for attributes in videoObject:
        Parent.Log(config.ScriptName, attributes)

    return

#---------------------------
#   Gets stream id of last stream for channel
#---------------------------
def GetLastStreamId(Parent):
    lastVideosObjectStorage = GetTwitchApiResponse(config.ApiUrlLastStream, Parent)
    lastVideoObject = GetVideoOfVideoObjectStorageByListId(lastVideosObjectStorage, 1, Parent)
    lastStreamId = lastVideoObject.get("broadcast_id")

    return lastStreamId

#---------------------------
#   Gets stream id of current stream for channel
#---------------------------
def GetCurrentStreamId(Parent):
    
    currentStreamObjectStorage = GetTwitchApiResponse(config.ApiUrlCurrentStream, Parent)
    currentStreamObject = GetStreamObjectByObjectStorage(currentStreamObjectStorage)
    currentStreamId = currentStreamObject.get("_id")

    return currentStreamId

#---------------------------
#   GetVideoOfVideoObjectStorageByListId
#---------------------------
def GetVideoOfVideoObjectStorageByListId(videoObjectStorage, listId, Parent):
    listId = int(listId) # let's be safe here

    parsedLastVideo = json.loads(videoObjectStorage)
    dataResponse = parsedLastVideo["response"] # str
    parsedDataResponse = json.loads(dataResponse) # dict, contents: _total, videos
    videosList = parsedDataResponse.get("videos") # list

    while (int(videosList[listId].get("broadcast_id")) == 1 or videosList[listId].get("status") == "recording"):
        
        if (listId >= int(config.ApiVideoLimit)):
            Parent.Log(config.ScriptName, "Failed to find valid stream object in list of defined last videos of channel")
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