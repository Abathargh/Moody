'''
Created on 29 set 2018

@author: mar

Logging utility stuff, this module is just some wrapping around the logging library in order to 
have some clarity and readability in the other libraries

'''

import datetime
import logging
import pathlib


class Logger() :
    
    '''
    
    Wrapper of the logging logger, this way the logging specific code is formatted in a compact way in here and
    it can be used by initializing a Logger object and using its methods, with the intent of cleaning the code as much
    as possible
    
    By default it outputs to a file in the logs directory and on the console.
    
    '''
    
    def __init__ ( self, name ) :
        
        super().__init__()
        
        #Generate date and time of execution for logging purposes
        now = datetime.datetime.now()
        formatted_date = "{}_{}_{}-{}_{}_{}".format( now.day, now.month, now.year, now.hour, now.minute, now.second )
        
        pathlib.Path ( "./moody/logs/" ).mkdir ( parents = True, exist_ok = True ) 
        
        
        self.logger = logging.getLogger( name )
        self.logger.setLevel ( logging.DEBUG )
        
        file_handler = logging.FileHandler ( "./moody/logs/{}-{}.log".format( name [ name.find ( "." ) + 1 : ],
                                                                                formatted_date ) )
        formatter = logging.Formatter ( "%(asctime)s - %(name)s - %(levelname)s : %(message)s" )
        file_handler.setFormatter( formatter )
        file_handler.setLevel( logging.DEBUG )
        self.logger.addHandler ( file_handler )
        
        
    def console( self, on ):
        
        if on :
            
            self.stream_handler = logging.StreamHandler()
            self.logger.addHandler ( self.stream_handler )
        
        else :
            
            self.logger.removeHandler( self.stream_handler )
            
    
    def setLevel( self, level) :
        
        self.logger.setLevel( level )
        
        