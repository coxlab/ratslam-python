'''
Created on Jul 8, 2011

@author: Christine
'''
from pylab import *
import cv, time

def get_im_xSums(im, y_range_type, x_range):
    #essentially this function gets the scanline intensity which is returned as im_xsums of the sub_image specified by the parameters initialized in the constructor
    sub_im = im[y_range_type, x_range] #where do i get im_odo_xrange?
    im_xsums = sum(sub_im, 0) #im_sums is a 1-d matrix of sums of the y-values at each x in the sub_im
    im_xsums = im_xsums/(sum(im_xsums)/ len(im_xsums)) #.shape is a command that tells you the size/length of a matrix im_sums and the[0] is there because usually .shape returns a tuple
    return im_xsums

def compare (curr_xsums, prev_xsums, offsetP, widthW):
    if (curr_xsums is None) or (prev_xsums is None):
        return (0,0)
    minFuncVal = inf #y-value of function  
    minS = 0
    for s in xrange(offsetP-widthW, widthW-offsetP):
        func = 0.0
        for n in xrange(widthW-abs(s)):
            func += abs(curr_xsums[n+max(s,0)] - prev_xsums[n-min(s,0)]) 
        func= func/(widthW - abs(s))
        if (minFuncVal>func):
            minFuncVal= func
            minS = s
    return (minS, minFuncVal) #returns a tuple of (profile shift at which the function was at its minimum, minimum function value)

def compare_segments(x_sums, prev_x_sums, shift, shape):
    if (x_sums is None) or (prev_x_sums is None):
        return 0, 0
    minval = inf
    offset = 0
    for s in range(shift-shape, shape-shift):
        val = 0
        for n in xrange(shape-abs(s)):
            val += abs(x_sums[n+max(s,0)] - prev_x_sums[n-min(s,0)])
        val /= (shape - abs(s))
        if val < minval:
            minval = val
            offset = s
    return offset, minval

def rs_compare_segments(seg1, seg2, slen, cwl):

    # assume a large difference
    #in matlab code, did not understand the point of diffs array of zeros..
    mindiff = inf
        
    # for each offset sum the abs difference between the two segments
    for offset in xrange(0, slen):
        cdiff = abs(seg1[offset:cwl] - seg2[0:cwl - offset])
        cdiff = float(sum(cdiff, 0)) / float(cwl - offset)
        if (cdiff < mindiff):
            mindiff = cdiff
            minoffset = offset

    for offset in xrange(0, slen):
        cdiff = abs(seg1[0:cwl - offset] - seg2[offset:cwl])
        cdiff = sum(cdiff, 0) / float(cwl - offset)
        if (cdiff < mindiff):
            mindiff = cdiff
            minoffset = -offset
    offset = minoffset
    sdif = mindiff
    
    return (offset, sdif)

class VisOdom:

    def __init__(self, **kwargs):
        
        self.prev_vrot_image_x_sums = kwargs.pop('prev_vrot_image_x_sums', None)
        self.prev_vtrans_image_x_sums = kwargs.pop('prev_vtrans_image_x_sums', None)
        self.IMAGE_ODO_X_RANGE = kwargs.pop('IMAGE_ODO_X_RANGE', slice(195, 475))
        self.IMAGE_VTRANS_Y_RANGE = kwargs.pop('IMAGE_VTRANS_RANGE', slice(270, 430))
        self.IMAGE_VROT_Y_RANGE = kwargs.pop('IMAGE_VROT_Y_RANGE', slice(75, 240) )
        self.VTRANS_SCALE = 100
        self.VISUAL_ODO_SHIFT_MATCH = 140 
        
        self.odo = [0.0,0.0, pi/2]
        self.delta = [0,0] #vtrans, vrot
        
    def update(self, raw_image): #raw image will actually be a cvmatrix of pixels
        image = cv.LoadImage(raw_image, cv.CV_LOAD_IMAGE_GRAYSCALE)
        FOV_DEG = 50.0
        dpp = float64(FOV_DEG) / image.width

        # vtrans 
        sub_image = image[self.IMAGE_VTRANS_Y_RANGE, self.IMAGE_ODO_X_RANGE]

        image_x_sums = sum(sub_image, 0)
        avint = float(sum(image_x_sums)) / len(image_x_sums)
        image_x_sums = image_x_sums/avint;
        
        if (self.prev_vtrans_image_x_sums==None):
            #self.prev_vtrans_image_x_sums = image_x_sums
            self.prev_vtrans_image_x_sums = zeros(image_x_sums.shape)

        [minoffset, mindiff] = rs_compare_segments(image_x_sums, self.prev_vtrans_image_x_sums, self.VISUAL_ODO_SHIFT_MATCH, len(image_x_sums))
        
        vtrans = mindiff * self.VTRANS_SCALE
        
        #a hack to detect excessively large vtrans
        if vtrans > 10:
            vtrans = 0

        self.prev_vtrans_image_x_sums = image_x_sums
        
        # now do rotation
        sub_image = image[self.IMAGE_VROT_Y_RANGE, self.IMAGE_ODO_X_RANGE]
        
        image_x_sums = sum(sub_image, 0)
        avint = float(sum(image_x_sums)) / len(image_x_sums)
        image_x_sums = image_x_sums/avint

        if (self.prev_vrot_image_x_sums==None):
            #self.prev_vrot_image_x_sums = image_x_sums #this is a better way to do it, but the matlab initializes all sums to zero...
            self.prev_vrot_image_x_sums = zeros(image_x_sums.shape)
        
        [minoffset, mindiff] = rs_compare_segments(image_x_sums, self.prev_vrot_image_x_sums, self.VISUAL_ODO_SHIFT_MATCH, len(image_x_sums))
        
        vrot = minoffset * dpp * pi / 180.0;
        self.prev_vrot_image_x_sums = image_x_sums
        
        self.odo[2] += vrot 
        self.odo[0] += vtrans* cos(self.odo[2]) #xcoord 
        self.odo[1] += vtrans* sin(self.odo[2]) #ycoord    
        
        self.delta = [vtrans, vrot]
        return self.odo

def testVOD():
    ot = time.time()
    vod = VisOdom()
    vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml2.png')
    print vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml3.png')
    print vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml4.png')
    print vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml5.png')
    print vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml6.png')
    print vod.update('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop/ml7.png')
    print 'time: ' + str(time.time()-ot)
