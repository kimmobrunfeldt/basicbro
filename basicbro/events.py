#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

"""
Every command that server sends is handled here.
"""

# Constants taken from twisted irc library.

# Constants (from RFC 2812)
RPL_WELCOME = '001'
RPL_YOURHOST = '002'
RPL_CREATED = '003'
RPL_MYINFO = '004'
RPL_ISUPPORT = '005'
RPL_BOUNCE = '010'
RPL_USERHOST = '302'
RPL_ISON = '303'
RPL_AWAY = '301'
RPL_UNAWAY = '305'
RPL_NOWAWAY = '306'
RPL_WHOISUSER = '311'
RPL_WHOISSERVER = '312'
RPL_WHOISOPERATOR = '313'
RPL_WHOISIDLE = '317'
RPL_ENDOFWHOIS = '318'
RPL_WHOISCHANNELS = '319'
RPL_WHOWASUSER = '314'
RPL_ENDOFWHOWAS = '369'
RPL_LISTSTART = '321'
RPL_LIST = '322'
RPL_LISTEND = '323'
RPL_UNIQOPIS = '325'
RPL_CHANNELMODEIS = '324'
RPL_NOTOPIC = '331'
RPL_TOPIC = '332'
RPL_INVITING = '341'
RPL_SUMMONING = '342'
RPL_INVITELIST = '346'
RPL_ENDOFINVITELIST = '347'
RPL_EXCEPTLIST = '348'
RPL_ENDOFEXCEPTLIST = '349'
RPL_VERSION = '351'
RPL_WHOREPLY = '352'
RPL_ENDOFWHO = '315'
RPL_NAMREPLY = '353'
RPL_ENDOFNAMES = '366'
RPL_LINKS = '364'
RPL_ENDOFLINKS = '365'
RPL_BANLIST = '367'
RPL_ENDOFBANLIST = '368'
RPL_INFO = '371'
RPL_ENDOFINFO = '374'
RPL_MOTDSTART = '375'
RPL_MOTD = '372'
RPL_ENDOFMOTD = '376'
RPL_YOUREOPER = '381'
RPL_REHASHING = '382'
RPL_YOURESERVICE = '383'
RPL_TIME = '391'
RPL_USERSSTART = '392'
RPL_USERS = '393'
RPL_ENDOFUSERS = '394'
RPL_NOUSERS = '395'
RPL_TRACELINK = '200'
RPL_TRACECONNECTING = '201'
RPL_TRACEHANDSHAKE = '202'
RPL_TRACEUNKNOWN = '203'
RPL_TRACEOPERATOR = '204'
RPL_TRACEUSER = '205'
RPL_TRACESERVER = '206'
RPL_TRACESERVICE = '207'
RPL_TRACENEWTYPE = '208'
RPL_TRACECLASS = '209'
RPL_TRACERECONNECT = '210'
RPL_TRACELOG = '261'
RPL_TRACEEND = '262'
RPL_STATSLINKINFO = '211'
RPL_STATSCOMMANDS = '212'
RPL_ENDOFSTATS = '219'
RPL_STATSUPTIME = '242'
RPL_STATSOLINE = '243'
RPL_UMODEIS = '221'
RPL_SERVLIST = '234'
RPL_SERVLISTEND = '235'
RPL_LUSERCLIENT = '251'
RPL_LUSEROP = '252'
RPL_LUSERUNKNOWN = '253'
RPL_LUSERCHANNELS = '254'
RPL_LUSERME = '255'
RPL_ADMINME = '256'
RPL_ADMINLOC = '257'
RPL_ADMINLOC = '258'
RPL_ADMINEMAIL = '259'
RPL_TRYAGAIN = '263'
ERR_NOSUCHNICK = '401'
ERR_NOSUCHSERVER = '402'
ERR_NOSUCHCHANNEL = '403'
ERR_CANNOTSENDTOCHAN = '404'
ERR_TOOMANYCHANNELS = '405'
ERR_WASNOSUCHNICK = '406'
ERR_TOOMANYTARGETS = '407'
ERR_NOSUCHSERVICE = '408'
ERR_NOORIGIN = '409'
ERR_NORECIPIENT = '411'
ERR_NOTEXTTOSEND = '412'
ERR_NOTOPLEVEL = '413'
ERR_WILDTOPLEVEL = '414'
ERR_BADMASK = '415'
ERR_UNKNOWNCOMMAND = '421'
ERR_NOMOTD = '422'
ERR_NOADMININFO = '423'
ERR_FILEERROR = '424'
ERR_NONICKNAMEGIVEN = '431'
ERR_ERRONEUSNICKNAME = '432'
ERR_NICKNAMEINUSE = '433'
ERR_NICKCOLLISION = '436'
ERR_UNAVAILRESOURCE = '437'
ERR_USERNOTINCHANNEL = '441'
ERR_NOTONCHANNEL = '442'
ERR_USERONCHANNEL = '443'
ERR_NOLOGIN = '444'
ERR_SUMMONDISABLED = '445'
ERR_USERSDISABLED = '446'
ERR_NOTREGISTERED = '451'
ERR_NEEDMOREPARAMS = '461'
ERR_ALREADYREGISTRED = '462'
ERR_NOPERMFORHOST = '463'
ERR_PASSWDMISMATCH = '464'
ERR_YOUREBANNEDCREEP = '465'
ERR_YOUWILLBEBANNED = '466'
ERR_KEYSET = '467'
ERR_CHANNELISFULL = '471'
ERR_UNKNOWNMODE = '472'
ERR_INVITEONLYCHAN = '473'
ERR_BANNEDFROMCHAN = '474'
ERR_BADCHANNELKEY = '475'
ERR_BADCHANMASK = '476'
ERR_NOCHANMODES = '477'
ERR_BANLISTFULL = '478'
ERR_NOPRIVILEGES = '481'
ERR_CHANOPRIVSNEEDED = '482'
ERR_CANTKILLSERVER = '483'
ERR_RESTRICTED = '484'
ERR_UNIQOPPRIVSNEEDED = '485'
ERR_NOOPERHOST = '491'
ERR_NOSERVICEHOST = '492'
ERR_UMODEUNKNOWNFLAG = '501'
ERR_USERSDONTMATCH = '502'

class IrcEvents(object):
    """
    Handles every command we get from
    """
    def __init__(self, bot):
    
        self.bot = bot
        
        # Must contain every server command that bot reacts from.
        # Numeric server messages are constants, see above.
        self.event_dict = {
            'PART': self.part,
            'QUIT': self.quit,
            'JOIN': self.join,
            'NICK': self.nick,
            'KICK': self.kick,
            'INVITE': self.invite,
            'TOPIC': self.topic,
            RPL_WHOREPLY: self.rpl_whoreply,
            RPL_WELCOME: self.rpl_welcome,
            ERR_NICKNAMEINUSE: self.err_nicknameinuse,
            RPL_ENDOFMOTD: self.rpl_endofmotd,
            RPL_TOPIC: self.rpl_topic,
            }

    def quit(self, prefix, cmd, args):
        """Person quits."""
        nick = prefix.split('!')[0]
        
        # Remove him from channel list
        for channel, nick_dict in self.bot.nicklist.items():
        
            if nick.lower() in nick_dict.keys():
                del self.bot.nicklist[channel][nick.lower()]
        
        # If the ghost bot drops, steal it's nickname
        if nick.lower() == self.bot.sets['bot_orig_nick'].lower():
            self.bot.send('NICK %s'% self.bot.sets['bot_orig_nick'])
                    
        # print self.bot.nicklist
        
    def part(self, prefix, cmd, args):
        """Person parts channel."""

        nick = prefix.split('!')[0]
        channel = args[0].lower()

        del self.bot.nicklist[channel][nick.lower()] # Remove from channel-list     

        # Its the bot who parted. 
        if nick == self.bot.sets['bot_nick']:
            del self.bot.nicklist[channel]
            
            self.bot.sets['bot_channels'].remove(channel)
            
        # print self.bot.nicklist
        
    def join(self, prefix, cmd, args):
        """Person joins."""    

        nick = prefix.split('!')[0]
        channel = args[0].lower()
        
        # nicklist structure: { channel: {lowernick: correctnick} }
        
        # Bot is joining to a new channel.
        if channel not in self.bot.nicklist.keys():
            self.bot.nicklist[channel] = {}
            
            self.bot.sets['bot_channels'].append(channel)
            
            self.bot.send('WHO %s'% channel) # Get userlist.
            
        # Someone joined a channel the bot is already in    
        else:
            self.bot.nicklist[channel][nick.lower()] = nick
        
        # print self.bot.nicklist
        
    def nick(self, prefix, cmd, args):
        """Person changes nick."""

        nick = prefix.split('!')[0]
        new_nick = args[0]
        
        if nick == self.bot.sets['bot_nick']: # I changed nick.
            self.bot.sets['bot_nick'] = args[0]
        
        # Change nick in channel list
        for channel, nick_dict in self.bot.nicklist.items():
        
            if nick.lower() in nick_dict.keys():
                del self.bot.nicklist[channel][nick.lower()]
                self.bot.nicklist[channel][new_nick.lower()] = new_nick 
                
                
        # print self.bot.nicklist
                
    def invite(self, prefix, cmd, args):
        """Someone was invited to a channel."""
        
        invited_nick = args[0]
        channel = args[1].lower()
        
        if invited_nick.lower() == self.bot.sets['bot_nick'].lower():
        
            self.bot.send('JOIN %s'% channel)
            self.bot.sets['bot_channels'].append(channel)

            self.bot.nicklist[channel] = {} # Create channel to memory.
            self.bot.send('WHO %s'% channel) # Get the users from channel.
            
            # print self.bot.nicklist
            
    def kick(self, prefix, cmd, args):
        """Remove channel from settings when kicked"""
        
        kicked_nick = args[1]
        channel = args[0].lower()
        
        # Remove channel from settings.
        if kicked_nick.lower() == self.bot.sets['bot_nick'].lower():
            self.bot.sets['bot_channels'].remove(channel)
            
            del self.bot.nicklist[channel] # Remove channel from memory
        
        # Kicked was not the bot.
        else:
            del self.bot.nicklist[channel][kicked_nick.lower()]
        
        # print self.bot.nicklist

    def topic(self, prefix, cmd, args):
        """Topic change"""
        
        topic = args[1]
        channel = args[0].lower()
        
        self.bot.topics[channel] = topic
        
    def rpl_whoreply(self, prefix, cmd, args):
        """Server sent reply to WHO command"""

        #                                         0          1         2               3                       4          5      6           7
        #:servercentral.il.us.quakenet.org 352 perusbro #perusprot ~kimble kimblee-.users.quakenet.org *.quakenet.org kimbledon H@x :3 Kimmo Brunfeldt
        
        # print args
        channel = args[1].lower()
        nick = args[5]
        
        # Add persons to nicklist.
        # Create channel in nicklist
        if channel not in self.bot.nicklist.keys():
            self.bot.nicklist[channel] = {nick.lower(): nick}
        else:
            self.bot.nicklist[channel][nick.lower()] = nick 
        
        # print self.bot.nicklist
        
        
    def rpl_welcome(self, prefix, cmd, args):
        """001, as in welcome message from server"""
        self.bot.sets['bot_connected'] = True
        
        # Join channels
        for chan in self.bot.sets['bot_channels']:
            self.bot.send('JOIN %s'%chan)
            self.bot.send('WHO %s'% chan) # Get the users from channel.
    
    def rpl_endofmotd(self, prefix, cmd, args):
        """End of motd"""
        
        # If our nick is not original nick, try to change it.
        orig = self.bot.sets['bot_orig_nick']
        if self.bot.sets['bot_nick'].lower() != orig.lower():
            self.bot.send('NICK %s'% self.bot.sets['bot_orig_nick'])
        
    def err_nicknameinuse(self, prefix, cmd, args):
        """Nick that bot tried to set was already in use"""
        
        tried_nick = args[1]
        self.bot.log.info('%s nick was already in use.'% tried_nick)
        
        orig = self.bot.sets['bot_orig_nick'] # Bots original nick
        alter = self.bot.sets['bot_alter_nick'] # Bots alternick
        
        if tried_nick.lower() == orig.lower():
        
            # Use an alternative nick. bot_alter_ending is added to default nick.
            self.bot.sets['bot_nick'] = self.bot.sets['bot_nick'] + self.bot.sets['bot_alter_ending']
            
            self.bot.send('NICK %s'% self.bot.sets['bot_nick'])
            self.bot.log.info('Using nick %s.'% alter)

    def rpl_topic(self, prefix, cmd, args):
        """Topic"""
        
        topic = args[2]
        channel = args[1].lower()
        
        self.bot.topics[channel] = topic            

