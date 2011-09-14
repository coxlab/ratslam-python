import pipeffmpeg as pff
from PIL import Image
import cStringIO as StringIO
from numpy import *

class VideoSource (object):
    
    def __init__(self, video_file, grayscale=False):
        
        self.video_stream = pff.InputVideoStream(video_file, cache_size=300)
        self.grayscale = grayscale
        
        self.first_frame = self[0]
        
    
    def __getitem__(self, index):
        fr = self.video_stream[index]
        
        im = asarray( Image.open( StringIO.StringIO(fr) ) )
        
        if self.grayscale:
            return mean(im,2)
        else:
            return im
