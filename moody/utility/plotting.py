'''Cioè

Created on 29 set 2018

@author: mar

A module containing class and functions used to plot graphs from
data contained in lists or data structures used in the other packages of the project

'''
import numpy as np
import pathlib
import datetime
from moody.audio.structures import pyaudio_to_numpy_format, Type

#For the time being it's just this function

def plot ( data_list, audio_types, audio_format ) :
    
    '''
    
    plot ( data_list, audio_format )
    
    data_list is a list and audio format is of the pyaudio formats. The function works for normal lists
    but it's thought for ChunkWindow, in order to generate graphs with lots of details thanks to 
    the various methods of the ChunkWindow and AudioChunk classes. 
    
    '''
    
    numpy_format = pyaudio_to_numpy_format( audio_format )
        
    
    data = b"".join ( [ e.to_binary_string() for e in data_list ] )
    
    types = [ { Type.SILENCE: "s", Type.MUSIC: "m", Type.SPEECH: "a"}[ t ] for t in audio_types ]
            
    try:
            
        import matplotlib as mpl

        mpl.use("Agg")

        import matplotlib.pyplot as plt
        
        amplitude = np.frombuffer( data, numpy_format )  
        chunks_beg = np.array( [ n * len ( data_list[0] ) * len ( data_list[0][0].chunk ) for n in range( len ( data_list ) ) ] )
        types = np.array ( types )
        plt.xticks( chunks_beg, types )       
        amplitude = amplitude /  np.iinfo( numpy_format ).max
        plt.plot ( amplitude )
        pathlib.Path ( "./moody/graphs/" ).mkdir ( parents = True, exist_ok = True ) 
        now = datetime.datetime.now()
        formatted_date = "{}_{}_{}-{}_{}_{}".format( now.day, now.month, now.year, now.hour, now.minute, now.second )        
        

        plt.savefig ( "./moody/graphs/{}".format ( formatted_date ) )
    
    except Exception as e :
        
        print ( "Impossibile generare un grafico!" )
        print ( e )
        
    
    
    