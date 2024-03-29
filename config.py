#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from definitions import ROOT_DIR

#---------------------------
#   [Required] Script Information
#   TODO: Some stuff from here should be moved to a GUI settings file later
#---------------------------

ScriptName = "♦ VIPTools"
Website = "https://twitch.tv/rialDave/"
Description = "Adds new features for Twitchs VIP functionality (Users can check-in every time you stream to earn the badge)"
Creator = "rialDave"
Version = "0.7.0-dev"

#---------------------------
#   Global Variables
#   Some stuff from here should be moved to a GUI settings file later
#---------------------------

VipdataFolder = "data"
VipdataFilename = "vipdata.json"
VipdataFilepath = os.path.join(ROOT_DIR, VipdataFolder, VipdataFilename)
VipdataBackupFolder = "archive" # inside data path
VipdataBackupFilePrefix = "vipdata_bak-"
VipdataBackupPath = os.path.join(ROOT_DIR, VipdataFolder, VipdataBackupFolder)

SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

TokenFile = os.path.join(os.path.dirname(__file__), "token.txt")

VariableChannelName = "$channelName"
VariableUser = "$user"
VariableCheckInCount = "$checkInCount"
VariableCheckInCountReadable = "$checkInCountReadable"
VariableNeededCheckins = "$neededCheckIns"
VIPStatusLocalization = {
    0: "No VIP",
    1: "VIP - but you can go on collecting check ins, if you want. Thank you for always being here! <3"
}
VIPStatusLocalizationSimple = {
    0: "No VIP",
    1: "VIP"
}
ApiVideoLimit = "10"

# Configuration of keys in json file
JSONVariablesCheckInsInARow = "check_ins_in_a_row"
JSONVariablesLastCheckIn = "last_check_in"
JSONVariablesLastCheckInStreamId = "last_check_in_streamid"
JSONVariablesRemainingJoker = "remaining_joker"
JSONVariablesVIPStatus = "vipstatus"
JSONVariablesHighestCheckInStreak = "highest_check_in_streak"
JSONVariablesHighestCheckInStreakDate = "highest_check_in_streak_date"

#---------------------------
#   Command settings and responses (caution: some of the response texts are overwritten later / not refactored yet)
#---------------------------

CommandVIPCheckIn = "!vipcheckin"
ResponseVIPCheckIn = "Great! " + VariableUser + " just checked in for the " + VariableCheckInCountReadable + " time in a row! Status: " + VariableCheckInCount + "/" + VariableNeededCheckins
CommandResetAfterReconnect = "!rcar"
ResponseResetAfterReconnect = "Okay, I've reset the checkins from last stream to the current stream."
CommandResetCheckIns = "!resetvipcheckins"
ResponseResetCheckIns = "Okay! Your check ins have been reset and you automatically checked in for this stream. Just send " + CommandVIPCheckIn + " again, the next time you're here again."
CommandTop10Vipcheckins = "!top10vipcheckins"
ResponseTop10Vipcheckins = "Alright, here are the top 10 craziest VIPCheckin guys (THANKS <3):"
CommandTop10VipcheckinsAlltime = "!top10vipcheckinsalltime"
ResponseTop10VipcheckinsAlltime = "Oh, All-time? Alright, here are the top 10 craziest VIPCheckin guys of ALL-TIME (THANKS <3):"

ResponsePermissionDeniedMod = "Permission denied: You have to be a Moderator to use this command!"
ResponseOnlyWhenLive = "ERROR: This command is only available, when the stream is live. Sorry!"

# Twitch API-URLs
ApiUrlCurrentStream = "https://api.twitch.tv/helix/streams"
ApiUrlLastStreamsBase = "https://api.twitch.tv/helix/videos?limit=" + ApiVideoLimit