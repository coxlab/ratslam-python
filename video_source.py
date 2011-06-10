import pyffmpeg
from pylab import imread

class VideoSource:
    """ Base VideoSource (yeah, I know: gratuitous in Python)"""
    
    # @property(get_frame)
    # frame
    
    def get_frame(self):
        pass
    
    def advance(self):
        pass

class DirVideoSource(VideoSource):
    def __init__(self, directory, template, starting_frame=1):
        self.frame_index = starting_frame
        self.template = template
        self.directory = directory
    
    def get_frame(self):
        return imread('/'.join((self.directory, self.template % self.frame_index)))
    
    def advance(self):
        self.frame_index += 1
        return self.get_frame()

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