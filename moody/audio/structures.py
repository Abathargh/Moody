'''
Created on 25 set 2018

@author: mar

'''

import pyaudio
import numpy as np
from enum import Enum
import moody.audio.util as util

HUMAN_HEARING_LOWER_BOUND = 110 #Hz

class Type ( Enum ):
    
    SILENCE = 0
    SPEECH = 1
    MUSIC = 2
    

class AudioChunk ():
    
    '''
    
    Abstract representation of an audio chunk, it essentially wraps every chunk in an interface that makes it easier
    to evaluate certain mathematical properties.

    '''


    def __init__( self, chunk, audio_format, frequency_strategy = None ):

        self.chunk = chunk 
        self.format = audio_format
        
        self.frequency = frequency_strategy
        
        
        
    def rms ( self, db = False ) :
        
        '''
        
        Evaluates the rms of the audio chunk, the second operation in here normalizes the list, with
        the element with highest energy possible being the max value that a np.int16 number can assume  
        
        It can either be returned as a decimal number x : 0 <= x <= 1 or in a decibel notation.
        
        '''
        
        list_from_chunk = np.frombuffer ( self.chunk, pyaudio_to_numpy_format( self.format ) )
        
        list_from_chunk = list_from_chunk /  np.iinfo( pyaudio_to_numpy_format( self.format ) ).max 
     
        rms = np.sqrt ( np.mean ( np.square ( list_from_chunk ) ) )
    
    
        if db :
            
            return 20 * np.log10 ( rms )
        
        return rms
    
    def frequency ( self, framerate ) :
    
        '''
        
        Default frequency evaluation strategy, taken from:
        https://stackoverflow.com/questions/2648151/python-frequency-detection
        by Justin Peel
        
        '''
        
        window = np.blackman ( len( self.chunk ) / self.sample_width )
        indata = np.array( np.frombuffer( self.chunk, self.format ) ) * window

        
        fftData = abs ( np.fft.rfft ( indata ) ) ** 2
        which = fftData[ 1: ].argmax() + 1
        
        
        y0, y1, y2 = np.log ( fftData[ which-1 : which+2 : ] )
        x1 = ( y2 - y0 ) * .5 / ( 2 * y1 - y2 - y0 )
        
        freq = ( which + x1 ) * framerate / ( len( self.chunk ) / self.sample_width )
        

        
        return None if freq < HUMAN_HEARING_LOWER_BOUND else freq
    
    
    
class ChunkWindow ( list ) :
   
   
    '''
    
    An extension of list that contains AudioChunk and represents a single window of content recorded
    by MoodyAudio.listen(). It follows that every instance of this class should have size equal to 
    MoodyAudio.window_size.
    
    
    The following methods act accordingly with the hypothesis that an instance of this class contains AudioChunk objects:
    if this data structure is used outside of this library, it is wise to make this assumption a reality.
    
    Moreover, a Strategy approach is used in order to make it possible to use different algorithms to evaluate
    the type of the audio represented by the various chunk in the list: one simple algorithm is given as a default
    in the audio_type implementation below.
    
    Other strategies should return an audio.structures.Type object when evaluating the audio type of the chunks.
    
    '''
    
    def __init__( self, audio_type_strategy = None ) :
        
        super().__init__()
        self.audio_type_strategy = audio_type_strategy
        
    
    def audio_type ( self, silence_rate, silence_threshold, music_threshold ) :
        
        if self.audio_type_strategy == None :
            
            db_data = [ chunk.rms ( db = True ) for chunk in self ]
            print ( str([ 0 if rms_value < silence_threshold else rms_value for rms_value in db_data ].count ( 0 )) +" " + str( util.average ( util.differences( db_data ) ) ) )
            
            if [ 0 if rms_value < silence_threshold else rms_value for rms_value in db_data ].count ( 0 ) >= len( db_data ) * silence_rate : return Type.SILENCE
            
            if  util.average ( util.differences( db_data ) ) <= music_threshold :
                
                return Type.MUSIC
            
            return Type.SPEECH  
        
        else :
            
            self.audio_type_strategy ( silence_rate, silence_threshold, music_threshold )    
        
    def to_binary_string( self ):
        
        string = []
        
        for chunk in self :
            
            string.append( chunk.frame )
            
        return b"".join( string )


def pyaudio_to_numpy_format ( pyaudio_format ) :
   
    '''
    
    Quick function to convert the pyaudio formats to the numpy ones
   
    '''
   
    if pyaudio_format == pyaudio.paInt32 :
   
        return np.int32
       
    elif pyaudio_format == pyaudio.paInt16 :
       
        return np.int16
       
    elif pyaudio_format == pyaudio.paInt8 :
       
        return np.int8
               
    raise Exception ( "Formato non valido!" )        