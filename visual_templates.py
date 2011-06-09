import simple_vision


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
        
        
    def __init__(**kwargs):
        self.template_decay = kwargs.pop('template_decay', None)
        self.match_y_range = kwargs.pop('y_range', None)
        self.match_x_range = kwargs.pop('x_range', None)
        self.global_decay = kwargs.pop('global_decay', 0.1)
        self.shift_match = kwargs.pop('shift_match', 20)
        self.match_threshold = kwargs.pop('match_threshold', None)
        self.templates = []
        
        
    def match(self, input_frame, x, y, th):
        
        vt_id = 0   # this is the return value
        
        sub_im = input_frame[self.match_y_range, self.match_x_range]
        
        # normalised intensity sums 
        image_x_sums = sum(sub_image, 0)
        image_x_sums = image_x_sums / sum(image_x_sums)

        min_offset = ones(len(self.templates), 1)
        min_diff = ones(len(self.templates), 1);

        for k in range(0, len(self.templates)):
            vt = self.templates[k]
            vt.template_decay -= self.global_decay;
            if vt.template_decay < 0.0:
                vt.template_decay = 0.0

            (min_offset[k], min_diff[k]) = rs_compare_segments(image_x_sums, 
                                                        vt.template, 
                                                        self.shift_match,
                                                        image_x_sums.shape[1])
        
        diff = min(mindiff)
        diff_id = argmin(mindiff)
        

        # if this intensity template doesn't match any of the existing templates
        # then create a new template
        if (diff * image_x_sums.shape[1]) > self.match_threshold):
            vt_id = len(self.view_templates)
            template = image_x_sums
            
            new_template = ViewTemplate( template, 
                                         vt_id, x, y, th, 
                                         self.template_decay)
            self.templates.append(new_template)
            
        else:
            vt_id = diff_id
            self.templates[vt_id].template_decay += self.template_decay;
            if self.prev_vt_id != self.vt_id:
                self.templates[vt_id].first = False

        self.vt_history.append(vt_id)

        return vt_id

