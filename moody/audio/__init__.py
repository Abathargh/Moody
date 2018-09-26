'''

Created on 25 set 2018

@author: mar

Main audio package

'''

import configparser
import pyaudio
import numpy as np
from threading import Semaphore

from .structures import AudioChunk, ChunkWindow

SILENCE_CHECK_DURATION = 5 #seconds

class MoodyAudio () :
    
    '''
    
    MoodyAudio setups the pyaudio audio stream and comes with a set of methods to be used
    to setup the application you want to run to analyze audio; it acts similarly to a façade 
    
    
    '''
    def __init__ ( self, audio_format, chunk_size, sample_rate, window_size ) :
        
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
        
        self.silence_threshold = None
    
    
    
    def set_silence_threshold ( self ) :
    
        '''
        
        Listens for SILENCE_CHECK_DURATION seconds and sets the silence threshold energy level to
        the highest energy level read in the reading interval.
        
        '''
    
        print ( "Recording audio to check the silence frames energy level, don't speak for " + str ( SILENCE_CHECK_DURATION ) + " seconds..." )
        
        self.stream.start_stream()            

        min_energy_value = float("inf")
        
        for _ in range ( 0, int ( self.sample_rate / self.chunk_size * SILENCE_CHECK_DURATION ) ) :
            
            try :
                
                frame_energy = AudioChunk ( self.stream.read ( self.chunk_size ), self.format ).rms( db = True )
                
                if frame_energy < min_energy_value :
                    
                    min_energy_value = frame_energy
            
            except Exception as e :
                
                print ( e )
                
                self.stream.stop_stream()
                self.audio.terminate()
                
                raise Exception (" An error occurred while reading the silence energy levels! ")
        
        self.stream.stop_stream()
        self.silence_threshold = min_energy_value + 10
        
        print ( self.silence_threshold )
       
    def listen ( self ) :
        
        '''
        
        listens attempts to read a number of chunks from the pyaudio input stream, returning them in the form of
        an ChunkList object, which is an extension of the default python type list, containing AudioChunk objects.
        
        '''
        
        if self.silence_threshold == None :
            
            self.set_silence_threshold()
        
        
        self.stream.start_stream()            
        
        data =  ChunkWindow()
        running = True
        counter = 0
        
        while running :
            
            chunk = self.stream.read ( self.chunk_size )

            data.append ( AudioChunk ( chunk , self.format ) ) 
            
            
            counter += 1
            
            if counter == self.window_size :
            
                running = False
    
        self.stream.stop_stream()
    
    
        return data
    
    def close ( self ) :
        
        self.audio.terminate()
            