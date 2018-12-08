import argparse
import configparser
import pyaudio
from pkg_resources import Requirement, resource_filename

import moody.audio as moody
import moody.utility.plotting as plotting


'''

Importing values  that are used in the application. Those can
be chosen at initialization too by passing different values to the constructor.

'''


if __name__ == "__main__" :
    
    
    config = configparser.ConfigParser()
    
    
    try :
        
        if len ( config.read ( "./moody/moody.conf" ) ) == 0 :
            
            config.read ( resource_filename ( Requirement.parse ( "Moody" ), "moody.conf" ) )
        
    except :
        
        raise ( "An error occurred while importing the default configuration!" )
    
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument ( "--format", "-f", help = "Sample format, can only be float32, int32, int16", type = str, default = config["Sampling"]["FORMAT"] )
    parser.add_argument ( "--chunksize", "-s", help = "The dimension of a single audio chunk, the number of samples in a frame", type = int, default = int ( config["Sampling"]["CHUNK_SIZE"] ) )
    parser.add_argument ( "--samplerate", "-r", help = "The sample rate, defaults to 44100 Hz", type = int, default = int ( config["Sampling"]["SAMPLE_RATE"] ) )
    parser.add_argument ( "--windowsize", "-w", help = "The size of the audio analysis window, where every element is a frame", type = int, default = int ( config["Analysis"]["WINDOW_SIZE"] ) )
    parser.add_argument ( "--silencerate", "-sr", help = "The minimum amount of zero energy frames in a window for it to be considered silence", type = float, default = float ( config["Analysis"]["SILENCE_RATE"] ) )
    parser.add_argument ( "--musicthresh", "-mt", help = "The value under which the difference between peaks is small enough to be considered music", type = float, default = float ( config["Analysis"]["MUSIC_THRESHOLD"] ) )
    parser.add_argument ( "--verbose", "-v", help = "If verbose is True, the programs print information on the energy level of every frame analyzed", action = "store_true" )
    args = parser.parse_args()
    
    
    FORMAT = None
    CHUNK_SIZE = args.chunksize
    SAMPLE_RATE = args.samplerate
    WINDOW_SIZE = args.windowsize
    SILENCE_RATE = args.silencerate
    MUSIC_THRESHOLD = args.musicthresh
    VERBOSE = args.verbose
    
    if args.format == "int32" :

        FORMAT = pyaudio.paInt32

    elif args.format == "int16" :
        
        FORMAT = pyaudio.paInt16

    elif args.format == "int8" :
        
        FORMAT = pyaudio.paInt8

    else :
        
        raise Exception ( "Formato non valido!" )
    
    full_data = []
    audio_types = []
    
    if VERBOSE :
                
        moody.logger.console( True )
    
    moody = moody.MoodyAudio ( audio_format = FORMAT, chunk_size = CHUNK_SIZE, sample_rate = SAMPLE_RATE, window_size = WINDOW_SIZE )
    running = True
    
    
    print ( "Recording audio to check the silence frames energy level, don't speak..." )
    moody.set_silence_threshold()
    
    while running :
        
        try :
            
            data_window = moody.listen()
            data_type = data_window.audio_type ( SILENCE_RATE, moody.silence_threshold, MUSIC_THRESHOLD )
            
            audio_types.append ( data_type )
            full_data.append( data_window )
            
                        
        except KeyboardInterrupt :
        
            moody.close()
            running = False
    
    plotting.plot( full_data, audio_types, FORMAT )
    
    print ( "\nBye!" )