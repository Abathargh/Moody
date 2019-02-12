'''
Created on 05 feb 2019

@author: mar

Communication package

'''

import time
import logging
from ..utility.log import Logger
from paho.mqtt.client import Client


'''

Connection settings

'''
MAX_ATTEMPTS = 5
WAIT_TO_RECONNECT = 1 #sec


logger = Logger( __name__ )


class Publisher ( Client ):
    
    def __init__( self, sensor_id ):
        super().__init__( client_id = sensor_id )
        self.logger = logging.getLogger( __name__ )
        
    
    '''
    
    Overriding some event based callback Client methods
    
    '''
         
    @property
    def on_connect ( self ):
        self.logger.info("{} successfully connected to the broker!".format( str( self._client_id, "UTF-8" ) ) )
    
    @property
    def on_disconnect ( self ):
        self.logger.info("{} disconnected from the broker!".format( str ( self._client_id, "UTF-8" ) ) )
    
    @property
    def on_publish ( self ):
        self.logger.info("Message published with success!")
  
    
    '''
    
    Adding the retry feature to the connect method
    
    '''
        
    def connect ( self, host, port = 1883, keepalive = 60, bind_address = "" ):
        
        '''
        
        The sensor tries to connect to the broker
        if it's not successful it will retry for a maximum of MAX_ATTEMPTS times
        
        '''
        
        attempts = 0
        
        while attempts < MAX_ATTEMPTS :                                       
            
            try:
                self.logger.info ( "Connecting to the broker... attempt number {}".format ( attempts ) )
                super().connect( host = host, port = port )
            
            except ConnectionError: 
                   
                time.sleep( WAIT_TO_RECONNECT )
                attempts += 1
                continue
            
            break
        
        if attempts == MAX_ATTEMPTS: 
            self.logger.error ( "Couldn't connect to the broker!" )
            raise ConnectionError
        
        