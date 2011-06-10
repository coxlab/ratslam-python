import numpy as np
import simple_vision

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
        im_x_sums /= sum(im_x_sums) / im_x_sums.shape[1]
        
        (min_offset, min_diff) = compare_segments(im_x_sums,
                                                  self.prev_trans_x_sums,
                                                  self.shift_match,
                                                  im_x_sums.shape[1])
        trans = mindiff * self.trans_scale
        
        if vtrans > 10.0:
            vtrans = 0.0
        
        # cache for the next round
        self.prev_trans_x_sums = im_x_sums
        
        # Rotation
        sub_im = im[ self.im_rot_y_range,  self.im_odo_x_range ]
        im_x_sums = sum(sub_im, 0)
        im_x_sums /= sum(im_x_sums) / im_x_sums.shape[1]
        
        (min_offset, min_diff) = compare_segments(im_x_sums,
                                                  self.prev_rot_x_sums,
                                                  self.shift_match,
                                                  im_x_sums.shape[1])
        
        rot = min_offset * degrees_per_pixel * np.pi / 180.
        self.prev_rot_x_sums = im_x_sums
        
        return (trans, rot)
        
        
