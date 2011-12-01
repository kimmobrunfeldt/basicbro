#!/usr/bin/python
# -*- coding: UTF-8 -*-
#

"""
Wrapper to add data to database with SQLite.
Provides a bit easier access to database than sqlite itself.
Table is created when not found. Database is saved after every delete_data()
and insert_data().

Look timer.py for an example how to use DbHandler.
First object is created, then just simply use the methods to access database.
"""

import time
import gevent
from gevent import Greenlet
from pysqlite2 import dbapi2 as sqlite

# Bot's own loggermodule
import logger
import useful

class DbHandler(object):
    """
    Wrapper for SQLite. Provides even easier access to database for other
    modules.
    """
    
    def __init__(self, bot, db_file, table, fields, ins_params):
        
        self.insert_params = ins_params # Params used in INSERT commands
        self.fields = fields # Fields to create new table
        self.table = table # Table's name
        self.db_file = db_file # Databases filename
        self.bot = bot # Handle to PerusBot
        self.log = logger.Logger('DB',bot.sets['db_logfile'])
    
        self.log.info('Opening %s database..'% self.db_file)
        self.connect()
    
    def connect(self):
        """Connect to database."""
        # Open database file.
        self.conn = sqlite.connect(self.db_file)
        self.cursor = self.conn.cursor()

        self.create_table() # Creates table if it does not exist!
        
    def create_table(self):
        """Create table if it does not exist"""        
        try: # Try to open table.
            self.cursor.execute('SELECT * FROM %s'% self.table)
            
        except sqlite.OperationalError, e:
            
            # Table does not exist. Create a new table.
            if 'no such table' in e[0]:
                
                # Get all necessary fields    
                
                logmsg = '%s: table "%s" does not exist.'%(self.db_file, self.table)
                logmsg += ' Creating table "%s", fields: %s ..'%(self.table, self.fields)
                self.log.info(logmsg)

                # Create table with given fields.
                sql_cmd = 'CREATE TABLE %s (%s)'% (self.table, self.fields)
                self.cursor.execute(sql_cmd)
                # Not commited, not necessary.
                    
            else: # It was unknown error, raise Exception.
                raise    
    
    def insert_data(self, values):
        """
        Insert data into table and save.
        values is tuple, that contains every mandatory value in table.
        """
        
        self.log.info('%s: Inserting %s to database.'% (self.db_file, values))
        
        sql_cmd = 'INSERT INTO %s VALUES %s'% (self.table, self.insert_params)
        
        # Insert given parameters to database.
        self.cursor.execute(sql_cmd, values)
        self.conn.commit() # Save changes to db.
    
    def delete_data(self, where):
        """Delete data matching where and save."""
    
        self.log.info('%s: Deleting items where %s'%(self.db_file, where))
        sql_cmd = 'DELETE FROM %s WHERE %s'%(self.table, where)
        
        self.cursor.execute(sql_cmd) # Delete matching
        self.conn.commit() # Save changes to db
        
    def select_data(self, where):
        """
        Select data from self.table, matching where statement, return as list.
        """
        
        sql_cmd = 'SELECT * FROM %s WHERE %s'%(self.table, where)
        
        # Return all jobs.
        return [job for job in self.cursor.execute(sql_cmd)]
                 
        
