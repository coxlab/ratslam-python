'''
Created on Jun 22, 2011

@author: Christine
'''
from pylab import *
import vod2

class template: #same thing as local view cell
    
    def __init__ (self, curr_xsums, **kwargs):

        self.template = curr_xsums #scanline profile of an image
        self.activity = kwargs.pop('activity', float64(1.0)) 
        
        self.x_pc = kwargs.pop('x_pc', 31)
        self.y_pc = kwargs.pop('y_pc', 31)
        self.th_pc = kwargs.pop('th_pc', 19)
                
        self.vc = kwargs.pop('vt_id', 0) #vc is visual template count/id: vc=vt_id 
        self.first = kwargs.pop('First', True) # Boolean that tells whether this is the first time this vt is being activated       
        
        self.exps = [] #list of exp_id associated with visual template

class templateCollection:
    
    def __init__ (self, **kwargs):
        
        self.templates = [] #list of all templates in template collection
        
        self.x_range = kwargs.pop('x_range', slice(54,615))
        self.y_range = kwargs.pop('y_range', slice(119,280)) # standard is 0:480 but changed because of parameters specified in st_lucia program
        
        self.globalDecay = kwargs.pop('globalDecay', 0.1) #global decay for all local view cells within the same template collection
        self.decay = kwargs.pop('decay', 1.0) #local decay for a specific template
        
        self.offsetP = kwargs.pop('offsetP', 20) #set to 20 in VT_SHIFT_MATCH
        self.match_threshold = kwargs.pop('match_threshold', 0.09) #set to 0.09
        
        self.curr_vc = kwargs.pop('curr_vt_id', None)
    
    def match(self, im): 
    
        sub_im = (im[self.y_range, self.x_range]) 
        sub_im = asarray(sub_im, dtype = 'float64')
        
        im_xsums = sum(sub_im, 0)
        im_xsums = im_xsums/(sum(im_xsums))
        

        diff = inf #the quality of the match
        diff_id = None #index in the array of xsums of the minfuncval
        
        for k in xrange (len(self.templates)): 
            self.templates[k].activity -= self.globalDecay
            
            if self.templates[k].activity<0: 
                self.templates[k].activity = 0
            (minS, minFuncVal) = vod2.rs_compare_segments(im_xsums, self.templates[k].template, self.offsetP, len(im_xsums))
        
            if (minFuncVal<diff): #if-statement finds the minimum value of the difference between two templates
                diff = minFuncVal
                diff_id = k

        if (diff*len(im_xsums)>self.match_threshold): #if the minimum difference multiplied by the width of the image is greater than the match threshold
            vc = self.update(im_xsums) #create a new local view cell that contains the current imxsums
        else: 
            vc = diff_id #otherwise, the current view cell is activated again
            if (self.curr_vc != vc):
                self.templates[vc].first = False
            self.templates[vc].activity += self.decay 

        self.templates[vc].diff = diff
        self.templates[vc].diff_id = diff_id

        return vc # return the identification number of the local view cell that "matches" the current xsums or return the identification number of the new local view cell that was just created 

    def update(self, curr_xsums):
        new_template = template(curr_xsums) #create a new template
        new_template.vc = len(self.templates) #update the new template's number         
        self.templates.append(new_template) #add the new template to the template collection
        return new_template.vc
    
    def get_template(self, vc):
        for each in self.templates:
            if each.vc==vc:
                return each

        

        
                