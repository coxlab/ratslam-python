import numpy as np
import pylab as plt
import simple_vision

def compare_segments(x_sums, prev_x_sums, shift, shape):
    if (x_sums is None) or (prev_x_sums is None):
        return 0, 0
    minval = np.inf
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

class SimpleVisualOdometer:
    """ Very simple visual odometry machinery """

    def __init__(self, **kwargs):
        self.last_image = None
        self.fov_deg = kwargs.pop("fov_deg", 50.)
        self.im_trans_y_range = kwargs.pop("im_trans_y_range", slice(100,120))
        self.im_rot_y_range = kwargs.pop("im_rot_y_range", slice(75,240))
        self.im_odo_x_range = kwargs.pop("im_odo_x_range", slice(200,460))
        
        self.shift_match = kwargs.pop("shift_match", 20) #VISUAL_ODO_SHIFT_MATCH
        self.trans_scale = kwargs.pop("trans_scale", 100.)   #VTRANS_SCALE
        self.prev_trans_x_sums = None   # prev_vtrans_image_x_sums
        self.prev_rot_x_sums = None  # prev_vrot_image_x_sums
        
        # initial heading
        self.odo = np.array([0, 0, np.pi / 2.])
    
    def estimate_odometry(self, im):
        """ Estimate the translation and rotation of the viewer, given a new 
            image sample of the environment
            
            (Matlab version: equivalent to rs_visual_odometry)
        """
        degrees_per_pixel = self.fov_deg / im.shape[1]
        
        # Translation
        # take slice of the image to average over
        sub_im = im[self.im_trans_y_range, self.im_odo_x_range]
        
        # sum down to a single strip
        im_x_sums = sum(sub_im, 0)
        # plt.imshow(sub_im)
        # plt.plot(im_x_sums)
        # plt.show()
        avint = sum(im_x_sums) / im_x_sums.shape[0]
        im_x_sums /= avint
        # im_x_sums /= sum(im_x_sums) / im_x_sums.shape[0]
        
        (min_offset, min_diff) = compare_segments(im_x_sums,
                                                  self.prev_trans_x_sums,
                                                  self.shift_match,
                                                  im_x_sums.shape[0])
        trans = min_diff * self.trans_scale
        
        if trans > 10.0:
            trans = 0.0
        
        # cache for the next round
        self.prev_trans_x_sums = im_x_sums
        
        # Rotation
        sub_im = im[ self.im_rot_y_range,  self.im_odo_x_range ]
        im_x_sums = sum(sub_im, 0)
        avint = sum(im_x_sums) / im_x_sums.shape[0]
        im_x_sums /= avint
        # im_x_sums /= sum(im_x_sums) / im_x_sums.shape[0]
        
        (min_offset, min_diff) = compare_segments(im_x_sums,
                                                  self.prev_rot_x_sums,
                                                  self.shift_match,
                                                  im_x_sums.shape[0])
        
        rot = min_offset * degrees_per_pixel * np.pi / 180.
        self.prev_rot_x_sums = im_x_sums
        
        # update odometry
        self.odo[2] += rot
        self.odo[0] += trans * np.cos(self.odo[2])
        self.odo[1] += trans * np.sin(self.odo[2])
        
        return (trans, rot, self.odo)
        
        
