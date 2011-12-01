INSTALLING:

1. Clone repository to your computer:

$ git clone git://github.com/kimbledon/basicbro.git

or download zip file provided by github and extract it.

2. Modify settings.py to your needs.

3. Run script

$ python bot.py

The basic functionality of IRC bot. Hilights:

    - Uses gevent, co-routine based Python networking library,
      http://www.gevent.org/
      When written, 0.13.0 - 0.13.6 versions worked.
    
    - Reconnecting. Bot sends PING message to serverevery x seconds and the
      receiving socket loop has a timeout which is x + y seconds. If
      receiving socket timeouts, bot reconnects.
      
    - Timer. Bot can be set up to send message or call a function after
      certain amount of seconds. (start_timer() in this file)
    
    - Backdoor server(MrServer). With MrServer it is possible to control
      bot with sockets(= with telnet also). The server has authentication
      and the auth password is sha256 hexdigest in bots settings.
      Read more from mr_server.py
      
    - Keeps track of nicks in channels.
    
    - Commands are in "commands" directory. When adding command, put new
      file in the directory, and add it to commands/__init__.py like others.
      Look other commands for example how to build a command. Syntax is matched
      with regex.
    
    - Handles text in unicode format. Encodes out going text to UTF-8.
      NOTE: It does not make a good guess of incoming text's encoding. It is 
      based on "foolish" assumption, that Finnish users use almost always
      ISO-8859-1 or UTF-8.
    
    - Splits overlong lines in multiple lines, default is 150 characters / line.
    
    - Gets title of every http:// starting link in channel. Yes, it could have
      a kilometer long regex and it would work for every friggin link, but
      based on experience, this works better, and it does not confuse from any
      character like those regex solutions. Bot's variable bot_say_title
      controls this option.


NOTES:

    - Bot keeps track of people in channels, but channelnames are ALWAYS
      lowercase, the are never casesensitive, remember when coding. Also it is
      tested, but poorly. In events: JOIN, INVITE, PART, KICK, QUIT, RPL_WHOREPLY

    - If useful.uni fails to decode text, it returns empty string. 
      It is difficult to find if you don't know it.


MODULES:

    - logger, has 2 kinds of log messages: errors and info.
      for every separate greenlet(thread) there is own logfile(bot, timer, MR).

    - timer, makes function call scheduling possible, also repeated
      tasks are possible to set(check Timer.add_repeat())
    
    - mr_server, backdoorserver that allows bot control without irc protocol
      possible. read mr_server.py to more details of MR protocol
    
    - events, EVERYTHING that server sends to bot, is handled here. Events can
      be categorized in two parts: numeric replys(001 Welcome msg), and
      commands(JOIN, QUIT, etc..). If one wants to handle what happens when 
      "KICK" command comes from server, it should be done in events.
    
    - messages, every PRIVMSG that the bot sees, is handled in messages. 
      Note that every PRIVMSG could also be handled in events. These two are
      separated for clerance. For example getting links' titles is done there.
    
    - tcp, most of socket-level stuff happens in this module. The connection
      stuff is separated from the actual bot to make the main bot code shorter.
      
HOWTO:

    - Adding new command:
        - Create new file to commands directory, look other commands for an 
          example. Command module's name doesn't need to be the same as irc 
          commands name. Your file can be. lol.py, and command !search.
        - Command class, __init__ and main methods are mandatory. __init__ must
          contain bot handle, syntax, help_syntax and help_desc.
        - syntax must be compiled regex object that matches for command use.
        - main method has always the same arguments
        
    - Adding new event(=to hook server reply or command): (events.py)
        - Create new item IrcEvents.events dictionary in events.py. Look others
          for an example. Just hook a command to a IrcEvents method. Every event
          has to have same parameters(prefix, cmd, args).
        -  :servercentral.il.us.quakenet.org 352 perusbro #perusprot ~kimble kimblee-.users.quakenet.org *.quakenet.org kimbledon H@x :3 Kimmo Brunfeldt
          
           an example from whoreply(352).
           
           prefix = 'servercentral.il.us.quakenet.org'
           cmd = '352'
           args[0] = 'perusbro'
           args[1] = '#perusprot'
           args[2] = '~kimble'
           args[3] = 'kimblee-.users.quakenet.org'
           args[4] = '*.quakenet.org'
           args[5] = 'kimbledon'
           args[6] = 'H@x'
           args[7] = '3 Kimmo Brunfeldt'
    
    - Adding new PRIVMSG handler: (messages.py)
        - In messages module MessageHandler has method analyze(). Simply add
        - wanted code there.
    
    - Adding new timer:
        - timer.py handles different kind of timers. Check timers.py to add
          a new task type.
        - Check function start_timer() in bot.py to see how new timers are added.
    
    - Using logger: (logger.py)
        - Check BroBot class in bot.py, method __init__ and look how it sets up its
          logger, the same way, you could add a new log.
    
