Streamlabs-Chatbot-VIPTools
=============================

A Python Script for Streamlabs Chatbot with some additional features for the (new) Twitch "VIP" role (Users can check-in every time you stream to earn the badge).

How to install 
----------------------------------

1. Go to this directory (starting from the root where Streamlabs Chatbot is installed):

```plain
Services\Scripts\
```

2. Create a new Folder called _"VIPTools"_
3. Drop/clone all of the stuff from this Repository in there
4. Load the scripts in SL Chatbot and you're good to go!

If you're having trouble with loading scripts in the SL Chatbot, see: https://www.youtube.com/watch?v=l3FBpY-0880

How to use
------------

You don't really need to (and can, because there's no config yet) configure much.
Usage information will be added here later.

Changelog
---------

**v0.0.1**

  * initial Build and commit

**v0.1.0**

  * Released first working version with correct stream comparison
  * Added some QoL stuff, especially code cleanup and some additional chat responses (still hardcoded)
  * (Jokers to be added in one of the next releases)

**v0.2.0**

  * Added joker functionality
  * Fixed some bugs related to stream ID comparison
  * Still needs to be tested in one of the next streams, expect some bugs

**v0.2.1**

  * Fixes some bugs again, stream comparison and updating data file should be working fine now (but still needs to be tested a lot more #expectmorebugs)

**v0.3.0**

  * Adds new Feature: "!resetcheckins" command for mods, to reset all checkins from the last stream to the current stream id (useful if you had a stream reconnect for example)

**v0.4.0**

  * Adds new Feature: VIPStatusHandler. This one always adds your current VIP Status to the response message

**v0.4.1**

  * Fixes a bug with the new VIPStatusHandler feature, which prevented new users to be added to the data file

**v0.4.2**

  * Fixes a bug that the tool didn't check if the channels last video is a stream video or highlight (users lost jokers even if they checked in at the last stream, when a highlight as created in the meantime)
  
**v0.4.3**

  * Fixes a bug where the VIP status wasn't correctly handled, when a user reaches VIP or is VIP already

**v0.5.0**

  * Added new feature: automatic backups in archive folder on every unload of the script
  * Added new feature: automatic creation of data and archive folder on startup
  * Fixed a bug with !resetcheckins mod-command, that didn't handle checkins in the second last stream (the last "real" stream)
  * Renamed "!resetcheckins" mod-command to "!rcar" (for "reset checkins after reconnect" :P)
  * Some additional refactoring tasks and code quality improvements (like splitting up in some first modules)

**v0.6.0**

  * Added new feature: Top10Vipcheckins command to view the current top checkins (maybe there will be another command to see the top 10 all-time check in streaks in the future, see below)

**Basic ideas and todo list while further developing this tool (in planned priority order)**

  * <s>Set up initial project on github</s>
  * <s>Viewers can send a command to the chat once day / stream and after X ongoing "check ins" with this command they will be rewarded the VIP status (manually)</s>
  * <s>Maybe there could be something like joker: Let's say a user has 2 joker which will be used when he doesn't check in within the next stream in a row. After the joker count hits 0 he loses his collected streak.</s>
  * <s>Prevent command from being called when the stream isn't live (can't get stream object stuff)</s>
  * <s>Viewers can list all current VIPs via command and the current max number of VIPs for the channel</s> (this is limited by twitch in different stages, see: https://help.twitch.tv/s/article/Managing-Roles-for-your-Channel#faq) Official Twitch function: "/vips"
  * <s>If a viewer reaches the necessary goal it will set to "active vip status" in the data file of the script</s>
  * <s>Reconnect-Improvement: Overhaul of the "resetcheckins"-command for streamers: Two commands: Everyone who already checked in in the last stream, will just be set to the current stream id and date. Everyone who didn't yet checkin, but did in the second last stream, will be set to the last stream id and date (could be a stable v1.0.0 after that).</s>
  * <s>Automatically backup data files in archive folder with timestamp when stream starts (on script load)</s>
  * <s>Feature: Top10VipCheckins or something similar</s>
  * Feature: Log highest checkinstreak in vipdata file (with date of last checkin of that streak)
  * Replace "in a row" with dynamic response (only if it's more then 1 checkIn in a row)
  * Clean up config file / make adjustable in chatbot settings
  * Extend documentation in readme file
  * Automatically set as VIP for the channel when goal reached (only the streamer account can do this, so the script needs to send a command as streamer in the chat. Needs to be researched if this is possible via Twitch API)
  * Integrate codacy code checking and badge