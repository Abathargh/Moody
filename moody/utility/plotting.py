'''

Created on 29 set 2018

@author: mar

A module containing class and functions used to plot graphs from
data contained in lists or data structures used in the other packages of the project

'''
import numpy as np
from threading import Thread
import time
import pathlib
import datetime
from .log import Logger
import logging
from moody.audio.structures import pyaudio_to_numpy_format

TIME_BETWEEN_GRAPHS = 900

logger = Logger( __name__ )

class ThreadedPlotter( Thread ):
    
    
    
    def __init__( self, audio_format ):
        super().__init__()
        
        self.logger = logging.getLogger( __name__ )
        self.data = list()
        self.types = list()
        self.audio_format = audio_format
         
    def append( self, data, types ):
        self.data.append( data )
        self.types.append( types )
        
    def run( self ):
        time.sleep( TIME_BETWEEN_GRAPHS )
        self.plot( self.data, self.types, self.audio_format )
        
    def plot ( self, data_list, audio_types, audio_format ) :
        
        '''
        
        plot ( data_list, audio_format )
        
        data_list is a list and audio format is of the pyaudio formats. The function works for normal lists
        but it's thought for ChunkWindow, in order to generate graphs with lots of details thanks to 
        the various methods of the ChunkWindow and AudioChunk classes. 
        
        '''
        
        numpy_format = pyaudio_to_numpy_format( audio_format )
            
        
        data = b"".join ( [ e.to_binary_string() for e in data_list ] )
        
        types = [ { 0: "s", 1: "a", 2: "m" }[ t ] for t in audio_types ]
                
        try:
            import matplotlib.pyplot as plt
            
            amplitude = np.frombuffer( data, numpy_format )  
            chunks_beg = np.array( [ n * len ( data_list[0] ) * len ( data_list[0][0].chunk ) for n in range( len ( data_list ) ) ] )
            types = np.array ( types )
            plt.xticks( chunks_beg, types )       
            amplitude = amplitude /  np.iinfo( numpy_format ).max
            plt.plot ( amplitude )
            pathlib.Path ( "/home/pi/Tesi/Moody/moody/graphs/" ).mkdir ( parents = True, exist_ok = True ) 
            now = datetime.datetime.now()
            formatted_date = "{}_{}_{}-{}_{}_{}".format( now.day, now.month, now.year, now.hour, now.minute, now.second )        
            
    
            plt.savefig ( "/home/pi/Tesi/Moody/moody/graphs/{}".format ( formatted_date ) )
        
        except Exception as e :
            
            self.logger.error( "Couldn't plot a graph, {}".format( e ) )
            
        
        
        