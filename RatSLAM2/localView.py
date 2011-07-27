'''
Created on Jun 22, 2011

@author: Christine
'''
import numpy
import vod2 as ratslam

class template:
    def __init__ (self, curr_xsums, **kwargs):
        self.template = curr_xsums #xsums or scanline profile of an image
        self.activity = numpy.float64(1.0)
        
        self.x_pc = kwargs.pop('x_pc', 31)
        self.y_pc = kwargs.pop('y_pc', 31)
        self.th_pc = kwargs.pop('th_pc', 19)
                
        self.vc = 0 #vc is the view cell count number (identifier)
        self.first = True
        
        self.exps = []
        
        self.diff = 0
        self.diff_id = 0

class templateCollection:
    def __init__ (self, **kwargs):
        self.templates = [] #list of all templates in template collection
        
        self.x_range = slice(54,615)
        self.y_range = slice(119,280) # standard is 0:480 but changed because of parameters specified in st_lucia program
        
        self.globalDecay = 0.1 #global decay for a bunch of local view cells within the same template collection
        self.decay = 1.0 #temporary decay for a specific template
        
        self.offsetP = 20 #set to 20 in VT_SHIFT_MATCH
        self.match_threshold = 0.09 #set to 0.09
        
        self.curr_vc = None
    
    def match(self, im): #takes in not the image but the xsums
    
        sub_im = (im[self.y_range, self.x_range]) #where do i get im_odo_xrange?
        sub_im = numpy.asarray(sub_im, dtype = 'float64')
        
        im_xsums = numpy.sum(sub_im, 0)
        im_xsums = im_xsums/(sum(im_xsums))
        

        diff = numpy.inf #diff is analogous to minfuncval in ratslam, also the quality of the match
        diff_id = None #index in the array of xsums of the minfuncval
        
        for k in xrange (len(self.templates)): #k is a template
            self.templates[k].activity -= self.globalDecay
            if self.templates[k].activity<0: 
                self.templates[k].activity = 0
            (minS, minFuncVal) = ratslam.rs_compare_segments(im_xsums, self.templates[k].template, self.offsetP, len(im_xsums))
            if (minFuncVal<diff): #if statement finds the minimum value of the different in two templates
                diff = minFuncVal
                diff_id = k

        if (diff*len(im_xsums)>self.match_threshold): #if the minimum difference multiplied by the width of the image is greater than the match threshold
            vc = self.update(im_xsums) #create a new local view cell that defines the current imxsums
        else: 
            vc = diff_id #otherwise, the current view cell is activated again
            if (self.curr_vc != vc):
                self.templates[vc].first = False
            self.templates[vc].activity += self.decay #i don't know where/what this decay paramter is coming from
        self.templates[vc].diff = diff
        self.templates[vc].diff_id = diff_id
        return vc # return the identification number of the local view cell that "matches" the current xsums or return the identification number of the new local view cell that you created 

    def update(self, curr_xsums):
        new_template = template(curr_xsums) #create a new template
        new_template.vc = len(self.templates) #update the new template's number         
        self.templates.append(new_template) #add teh new template to the template collection
        return new_template.vc
    
    def get_template(self, vc):
        for each in self.templates:
            if each.vc==vc:
                return each

        

        
                