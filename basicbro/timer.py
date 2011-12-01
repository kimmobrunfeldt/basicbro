#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

"""
Bot schedules tasks with this timer.
"""

import time
import gevent
from gevent import Greenlet

# Bots own loggermodule
import logger
import database

class Timer(Greenlet):
    """
    Schedules tasks for ircbot.
    Msg_jobs are saved in sqlite database with database-module
    Database has table named 'jobs', table structure is in __init__()
    
    Calls are used to schedule function executing. !!!DO NOT!!! schedule functions 
    that take too much time to run( > 500ms)
    Calls dictionary's structure is:
    
    calls = {
            unixtime: [(function, [args])],
           }
    

    Repeats is used to repeatedly call a function at an interval.
    repeats structure is:    
    
    repeats = {
            seconds: [(function, [args]),]
            }
    """
    
    def __init__(self, bot):
    
        # Make the thread stoppable
        Greenlet.__init__(self)
        self._stop = gevent.event.Event()
              
        self.bot = bot # Handle to PerusBot
        self.repeats = {} # Explained in docstring
        self.calls = {} # Explained in docstring
        self.lastrepeat = 0 # Time when last repeating tasks were done
         
        # Add own logger to Timer.    
        self.log = logger.Logger('Timer',bot.sets['timer_logfile'])

        # USE DATABASE.
        # Values to create to table.
        table_values = 'id INTEGER PRIMARY KEY,time INTEGER,'
        table_values += 'receiver TEXT,msg TEXT'
        
        # Basically, id is null and ? is replced given value when insert_data()
        # is called.
        ins_params = '(null, ?, ?, ?)'
        
        db_file = self.bot.sets['timer_db_file'] # Database filename
        table = 'jobs'
        
        self.db = database.DbHandler(self.bot, db_file, table, table_values, ins_params)
        
        
        
    def stop(self):
        """This must be called from main program to stop this thread."""
        self.log.info('Stopping Timer..')
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
    
    def add_repeat(self, interval, function, *args):
        """
        Create new repeating timer.
        Repeating timers die when bot is closed. They have to be set again on
        every startup!
        """
        if interval not in self.repeats:
            self.repeats[interval] = [(function, args),]

        else:
            self.repeats[interval].append( (function, args), )
    
    def add_msgjob(self, unixtime, receiver, msg):
        """
        Send message at given time. TMZONE is added here!
        """
        unixtime = int(unixtime + self.bot.sets['bot_tm_zone'])
        
        # Tuple (time, receiver, msg)
        values = (unixtime, receiver, msg)
        self.db.insert_data(values)
        
    def add_call(self):
        pass
        
    def _run(self):
        """
        Check for jobs.
        """

        # Do until stop is called
        while not self.stopped():
            
            gevent.sleep(0.5)
            time_now = int(time.time() + self.bot.sets['bot_tm_zone']) # Current time
            
            if not self.bot.sets['bot_connected']: # Don't do any jobs if bot is not connected
                continue

            
            where = 'time<=%s'% time_now
            # Get current message jobs.
            msg_jobs = self.db.select_data(where)
            
            if len(msg_jobs) > 0:
            
                for job in msg_jobs:
                    
                    recv = job[2]
                    message = job[3]
                    
                    # Send messages.
                    self.bot.send_msg(recv, message)
            
                # Delete sent messages and save.
                self.db.delete_data(where)
                

            # Check if time has come to execute functions
            for job_time, joblist in self.calls.items():
                
                if job_time <= time_now: # This job has to be done
                    
                    for job_item in joblist:
                        
                            # Call function with proper args
                            job_item[0](job_item[1])
                            self.log.info('Delayed function done: %s "%s"'%(job_item[0], job_item[1]))
                    
                    del self.calls[job_time] # Remove done tasks.
                            
                            
            # Prevent multiple calls per one second because sleep(0.x)
            if self.lastrepeat < time_now:
            
                # Check for repeating tasks
                for interval, funcs in self.repeats.items():
                    
                    if time_now % interval == 0:
                        
                        for f in funcs:
                            
                            # Call function
                            f[0](f[1][0])
            self.lastrepeat = time_now


if __name__ == '__main__':    
    pass

                            
