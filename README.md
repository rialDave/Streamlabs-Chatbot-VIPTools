Streamlabs-Chatbot-Randombeer
=============================

A Python Script for Streamlabs Chatbot with some additional features for the (new) Twitch "VIP" role.

How to install 
----------------------------------

1. Go to this directory (starting from the root where Streamlabs Chatbot is installed):

```plain
Services\Scripts\
```

2. Create a new Folder called _"VIPTools"_
3. Drop all of the stuff from this Repository in there
4. Reload the scripts in SL Chatbot and you're good to go!

If you're having trouble with loading scripts in the SL Chatbot, see: https://www.youtube.com/watch?v=l3FBpY-0880

How to use
------------

You don't really need to (and can, because there's no config yet) configure much.
Usage information will be added here later.

Changelog
---------

**v0.0.1**

  * initial Build and commit

**Basic ideas and todo list while further developing this tool (in planned priority order)**

  * <s>Set up initial project on github</s>
  * Viewers can send a command to the chat once day / stream and after X ongoing "check ins" with this command they will be rewarded the VIP status
  * Viewers can list all current VIPs via command and the current max number of VIPs for the channel (this is limited by twitch in different stages, see: https://help.twitch.tv/s/article/Managing-Roles-for-your-Channel#faq) 
  * If a viewer reaches the necessary goal it will 1. set to "active vip status" in the data file of the script and 2. automatically set to VIP for the channel (only the streamer account can do this, so the script needs to send a command as streamer in the chat. Needs to be researched if this is possible)
  * Extend documentation in readme file
  * Automatic backup of data files located under "data"
  * Integrate codacy code checking and badge