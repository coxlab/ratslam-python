import pyffmpeg


class VideoSource:
    """ Base VideoSource (yeah, I know: gratuitous in Python)"""
    
    @property(get_frame)
    frame
    
    def get_frame(self):
        pass
    
    def advance(self):
        pass
        
class FFMpegVideoSource (VideoSource):
    
    def __init__(self, filename):
        self.stream = pyffmpeg.VideoStream()
        self.stream.open(filename)
    
    def get_frame(self):
        try:
            frame = stream.GetCurrentFrame()
        except Exception, e:
            return None
            
        return frame.asarray()
    
    def advance(self):
        try:
            frame = stream.GetNextFrame()
        except Exception, e:
            return None
        return frame.asarray()