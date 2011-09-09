import numpy as np
import simple_vision

from visual_odometer import compare_segments


class VisualTemplate:
    def __init__(self, template, vt_id, x_pc, y_pc, z_pc, decay, **kwargs):
        self.id = vt_id
        self.x_pc = x_pc
        self.y_pc = y_pc
        self.z_pc = z_pc
        self.exps = []
        self.template_decay = decay
        self.first = True
        self.template = template
        
    
    

class VisualTemplateCollection:
    """ A collection of simple visual templates against which an incoming
        frame can be compared
        
        (Matlab equivalent: rs_visual_template)"""
        
        
    def __init__(self, **kwargs):
        self.template_decay = kwargs.pop('template_decay', None)
        self.match_y_range = kwargs.pop('y_range', None)
        self.match_x_range = kwargs.pop('x_range', None)
        self.global_decay = kwargs.pop('global_decay', 0.1)
        self.shift_match = kwargs.pop('shift_match', 20)
        self.match_threshold = kwargs.pop('match_threshold', None)
        self.templates = []
        self.curr_vt_id = None
        
        
    def match(self, input_frame, x, y, th):
        
        vt_id = 0   # this is the return value
        
        sub_im = input_frame[self.match_y_range, self.match_x_range]
        
        # normalised intensity sums 
        image_x_sums = sum(sub_im, 0)
        image_x_sums = image_x_sums / sum(image_x_sums)

        min_offset = np.ones((len(self.templates), 1))
        min_diff = np.ones((len(self.templates), 1));

        for k in range(0, len(self.templates)):
            vt = self.templates[k]
            vt.template_decay -= self.global_decay;
            if vt.template_decay < 0.0:
                vt.template_decay = 0.0

            (min_offset[k], min_diff[k]) = compare_segments(image_x_sums, 
                                                        vt.template, 
                                                        self.shift_match,
                                                        image_x_sums.shape[0])
        
        if len(self.templates) == 0:
            diff = np.inf
            diff_id = None
        else:
            diff = min(min_diff)
            diff_id = argmin(min_diff)
        

        # if this intensity template doesn't match any of the existing templates
        # then create a new template
        if (diff * image_x_sums.shape[1]) > self.match_threshold or (len(self.templates) == 0):
            vt_id = len(self.templates)
            template = image_x_sums
            
            new_template = VisualTemplate( template, 
                                         vt_id, x, y, th, 
                                         self.template_decay)
            self.templates.append(new_template)
            
        else:
            vt_id = diff_id
            self.templates[vt_id].template_decay += self.template_decay;
            if self.prev_vt_id != self.vt_id:
                self.templates[vt_id].first = False

        # self.vt_history.append(vt_id)
        self.curr_vt_id = vt_id
        return vt_id

