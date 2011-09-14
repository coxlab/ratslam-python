from numpy import *
from visual_odometer import compare_segments

import numpy as np
#import simple_vision

from visual_odometer import compare_segments


class ViewTemplate (object):
       
    def __init__(self, x_pc, y_pc, z_pc):
        self.x_pc = x_pc
        self.y_pc = y_pc
        self.z_pc = z_pc
        self.exps = []
         
    def match(self, input_frame):
        raise NotImplemented


class IntensityProfileTemplate(ViewTemplate):
    """A very simple view template as described in Milford and Wyeth's 
       original algorithm.  Basically, just compute an intensity profile 
       over some region of the image. Simple, but suprisingly effective
       under certain conditions
       
    """
    
    def __init__(self, input_frame, x_pc, y_pc, z_pc,
                       y_range, x_range, shift_match):
        
        ViewTemplate.__init__(self, x_pc, y_pc, z_pc)
        
        self.x_range = x_range
        self.y_range = y_range
        self.shift_match = shift_match
        
        self.first = True
        
        # compute template from input_frame
        self.template = self.convert_frame(input_frame)

    def convert_frame(self, input_frame):
        "Convert an input frame into an intensity line-profile"
        
        sub_im = input_frame[self.y_range, self.x_range]
        
        # normalised intensity sums 
        image_x_sums = sum(sub_im, 0)
        image_x_sums = image_x_sums / sum(image_x_sums)
        
        return image_x_sums
    
    def match(self, input_frame):
        "Return a score for how well the template matches an input frame"
        image_x_sums = self.convert_frame(input_frame)
        
        toffset, tdiff = compare_segments(image_x_sums, 
                                        self.template, 
                                        self.shift_match,
                                        image_x_sums.shape[0])
                                        
        return tdiff * len(image_x_sums)

    
class ViewTemplateCollection (object):
    """ A collection of simple visual templates against which an incoming
        frame can be compared.  The entire collection of templates is matched
        against an incoming frame, and either the best match is returned, or
        a new template is created from the input image in the event that none
        of the templates match well enough
        
        (Matlab equivalent: rs_visual_template)
    
    """
        
        
    def __init__(self, template_generator, match_threshold, global_decay):
        """
        Arguments:
        template_generator -- a callable object that generates a ViewTemplate
                              subclass
        match_threshold -- the threshold below which a subtemplate's match
                           is considered "good enough".  Failure to match at
                           this threshold will result in the generation of a 
                           new template object
        global_decay -- not currently used
        
        """
        self.template_generator = template_generator
        self.global_decay = global_decay
        self.match_threshold = match_threshold

        self.templates = []
        self.current_template = None
    
    
    def __getitem__(self, index):
        return self.templates[index]
    
    def match(self, input_frame, x, y, th):
        
        match_scores = [ t.match(input_frame) for t in self.templates]
        
        if len(match_scores) == 0 or min(match_scores) > self.match_threshold:
            # no matches, so build a new one
            new_template = self.template_generator(input_frame, x, y, th)
            self.templates.append(new_template)
            return new_template
            
        best_template = self.templates[argmin(match_scores)]
        
        return best_template
        

                