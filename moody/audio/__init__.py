'''

Created on 25 set 2018

@author: mar

Main audio package

'''

import configparser
import pyaudio
import logging
import datetime
import pathlib
import numpy as np
from threading import Semaphore

from .structures import AudioChunk, ChunkWindow
from ..utility.log import Logger


SILENCE_CHECK_DURATION = 5 #seconds
WAIT_TIME = 2 #seconds    


logger = Logger( __name__ )



class MoodyAudio () :
    
    '''
    
    MoodyAudio setups the pyaudio audio stream and comes with a set of methods to be used
    to setup the application you want to run to analyze audio; it acts similarly to a façade 
    
    
    '''
    
    def __init__ ( self, audio_format, chunk_size, sample_rate, window_size ) :
        
        self.logger = logging.getLogger( __name__ )
        
        self.format = audio_format
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.window_size = window_size
                        
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open( rate = self.sample_rate,
                             format = self.format,
                             frames_per_buffer = self.chunk_size,
                             input = True,
                             channels = 1 )
        
        self.logger.info ( "MoodyAudio on" )
        
        self.silence_threshold = None
    
    
    
    def set_silence_threshold ( self ) :
    
        '''
        
        Listens for SILENCE_CHECK_DURATION seconds and sets the silence threshold energy level to
        the highest energy level read in the reading interval.
        
        '''
    
        self.logger.info ( "Listening to set the silence threshold..." )
        
        self.stream.start_stream()            

        max_energy_value = -float("inf")
        #min_energy_value = float("inf")
        #We count the frames recorded, and ignore the the ones read in the first 1.5 seconds
        #as they contain transient-like behaviour that we don't want to record
        
        frame_counter = 0
        
        for _ in range ( 0, int ( self.sample_rate / self.chunk_size * SILENCE_CHECK_DURATION + WAIT_TIME ) ) :
            
            try :
                
                self.stream.read ( self.chunk_size )
                frame_counter += 1
                
                if frame_counter >= ( self.sample_rate / self.chunk_size * WAIT_TIME ) :
                
                    frame_energy = AudioChunk ( self.stream.read ( self.chunk_size ), self.format ).rms( db = True )
                    
                    self.logger.debug( round ( frame_energy, 3 ) )
                    
                    if frame_energy > max_energy_value :
                        
                        max_energy_value = frame_energy
                    
                    #if frame_energy < min_energy_value :
                        
                    #    min_energy_value = frame_energy
                
            
            except :
                                
                self.stream.stop_stream()
                self.audio.terminate()
                
                self.logger.exception (" An error occurred while reading the silence energy levels! ")
                
                
        self.stream.stop_stream()
        self.silence_threshold = max_energy_value
        self.logger.info( "Silence threshold = {} dB".format( self.silence_threshold )  )

       
    def listen ( self ) :
        
        '''
        
        listens attempts to read a number of chunks from the pyaudio input stream, returning them in the form of
        an ChunkList object, which is an extension of the default python type list, containing AudioChunk objects.
        
        '''
       
        self.logger.info ( "Recording audio data..." )
        
        if self.silence_threshold == None :
            
            self.set_silence_threshold()
        
        
        
        data =  ChunkWindow()
        running = True
        counter = 0
        
        while running :
            
                
            self.stream.start_stream()            
            
            try:
                chunk = self.stream.read ( self.chunk_size, exception_on_overflow = False )
                data.append ( AudioChunk ( chunk , self.format ) ) 
            
            except Exception as e:
                self.logger.error( "Error while reading audio data: {}".format( e ) )
                data = '\x00' * self.chunk_size
            
            counter += 1
            
            if counter == self.window_size :
            
                running = False
            
        self.stream.stop_stream()

    
        return data
    
    def close ( self ) :
        
        self.audio.terminate()
        self.logger.info ( "MoodyAudio off" )
            