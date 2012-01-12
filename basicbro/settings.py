"""
SETTINGS
"""

"""
BOT SETTINGS
"""
# Bot's settings, these are meant to be in a separate config file.    
settings = {}
settings['bot_server'] = 'irc.freenode.org'
settings['bot_port'] = 6667
settings['bot_channels'] = ['#yourchannel']
settings['bot_nick'] = 'basicbro'
settings['bot_realname'] = 'Basic Bro'
# Use logs directory, if you change, check bot.py bottom
settings['bot_logfile'] = 'logs/bot'
settings['bot_timeout'] = 220 # Receiving socket's timeout.
settings['bot_reconnect_interval'] = 10
settings['bot_ping_interval'] = 200 # Interval to send own PING
settings['bot_encoding_out'] = 'utf-8'
settings['bot_quit_message'] = '->'
settings['bot_tm_zone'] = 3600 * 3 # Europe/Helsinki, added to time()
settings['bot_max_line_length'] = 1500
# If default nick is already in use, add this to the default nick.
settings['bot_alter_ending'] = 'u'
settings['bot_reconnect_delay_on_error'] = 20

"""
TIMER SETTINGS
"""
# Use db directory, if you change, check bot.py bottom
settings['timer_db_file'] = 'db/jobs.db'
settings['timer_logfile'] = 'logs/timer'

"""
DB SETTINGS
"""
# Use logs directory, if you change, check bot.py bottom
settings['db_logfile'] = 'logs/db'

"""
MRSERVER SETTINGS
"""
# THIS IS AN EXAMPLE PASS!!! ->  It is: "password"
# Auth password in sha256 hexdigest, see useful.py module for function.
settings['mr_password'] = '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
settings['mr_port'] = 48827 # Port to listen
settings['mr_host'] = 'localhost' # Accept connections only from localhost!

# Use logs directory, if you change, check bot.py bottom
settings['mr_logfile'] = 'logs/mr'



"""
VARIABLES
"""
# Bot's variables, these are always string types
variables = {}
variables['bot_debug'] = 'true' # Debuggind mode
variables['bot_say_title'] = 'true' # Say title: x on every link
# %n = nick , %m = message
variables['mr_webirc_stamp'] = u'<webirc, %n>: %m'
variables['gcalc_legal'] = " +-*/()!^'"
