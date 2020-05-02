#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import fsLib

#---------------------------
#   [Required] Script Information
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------

ScriptName = "VIPTools"
Website = "https://twitch.tv/rialDave/"
Description = "Adds new features for Twitchs VIP functionality"
Creator = "rialDave"
Version = "0.4.3-dev"

#---------------------------
#   Global Variables
#   Some stuff from here should be moved to a GUI settings file later
#---------------------------
VipdataFilepath = fsLib.GetFilepathInFolder("data", "vipdata.json")
VipdataBackupFilePrefix = "vipdata_bak-"
VipdataBackupPath = "data/archive"

VariableChannelName = "$channelName"
VariableUser = "$user"
VariableCheckInCount = "$checkInCount"
VariableCheckInCountReadable = "$checkInCountReadable"
VariableNeededCheckins = "$neededCheckIns"
ChannelId = "159000697"
AppClientId = "znnnk0lduw7lsppls5v8kpo9zvfcvd"
VIPStatusLocalization = {
    0: "No VIP",
    1: "VIP - but you can go on collecting check ins, if you want. Thank you for always being here! <3"
}
ApiVideoLimit = "10"

# Configuration of keys in json file
JSONVariablesCheckInsInARow = "check_ins_in_a_row"
JSONVariablesLastCheckIn = "last_check_in"
JSONVariablesLastCheckInStreamId = "last_check_in_streamid"
JSONVariablesRemainingJoker = "remaining_joker"
JSONVariablesVIPStatus = "vipstatus"

# Configuration of twitch api urls
ApiUrlLastStream = str("https://api.twitch.tv/kraken/channels/" + ChannelId + "/videos?limit=" + ApiVideoLimit + "&client_id=" + AppClientId)
ApiUrlCurrentStream = str("https://api.twitch.tv/kraken/streams/" + ChannelId + "?client_id=" + AppClientId)

#---------------------------
#   Command settings and responses (caution: some of the response texts are overwritten later / not refactored yet)
#---------------------------

CommandVIPCheckIn = "!vipcheckin"
ResponseVIPCheckIn = "Great! " + VariableUser + " just checked in for the " + VariableCheckInCountReadable + " time in a row! Status: " + VariableCheckInCount + "/" + VariableNeededCheckins
CommandResetAfterReconnect = "!resetcheckins" # todo: set permissions for this to mod-only
ResponseResetAfterReconnect = "Okay, I've reset the checkins from last stream to the current stream."
CommandResetCheckIns = "!resetvipcheckins"
ResponseResetCheckIns = "Okay! Your check ins have been reset and you automatically checked in for this stream. Just send " + CommandVIPCheckIn + " again, the next time you're here again."

ResponsePermissionDeniedMod = "Permission denied: You have to be a Moderator to use this command!"
ResponseOnlyWhenLive = "ERROR: This command is only available, when the stream is live. Sorry!"