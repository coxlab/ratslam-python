#!/usr/bin/env python

import numpy as np
import pylab as plt

from pose_cell_network import PoseCellNetwork
from experience_map import ExperienceMap
from visual_odometer import SimpleVisualOdometer
from visual_templates import VisualTemplateCollection
from video_source import FFMpegVideoSource, DirVideoSource

class RatSLAM:
    """ A complete rat slam instance
        
        (Matlab version: equivalent to rs_main)
    """
    
    def __init__(self, **kwargs):
        pose_cell_shape = kwargs.pop("pose_cell_dimensions", (100,100,60))
        
        
        shift_match = kwargs.pop("odo_shift_match", 20)
        
        # self.odometer = SimpleVisualOdometer()
        self.odometer = SimpleVisualOdometer(fov_deg = kwargs.pop("fov_deg",50),
                                             im_trans_y_range = kwargs.pop("im_trans_y_range"),
                                             im_rot_y_range = kwargs.pop("im_rot_y_range"),
                                             im_odo_x_range = kwargs.pop("im_odo_x_range"),
                                             shift_match = shift_match,
                                             trans_scale = kwargs.pop("odo_trans_scale",100.))
        
        # vt_match_threshold = kwargs.pop('vt_match_threshold', None)
        # self.view_templates = VisualTemplateCollection()
        self.view_templates = VisualTemplateCollection( template_decay = kwargs.pop('template_decay', 1.0),
                    match_y_range = kwargs.pop('im_vt_y_range', None),
                    match_x_range = kwargs.pop('im_vt_x_range', None),
                    shift_match = shift_match,
                    match_threshold = kwargs.pop('vt_match_threshold', None))
                
        self.pose_cell_network = PoseCellNetwork(pose_cell_shape)#,
                                                 # self.view_templates)
        
        
        self.experience_map = ExperienceMap(self.pose_cell_network,
                                            self.view_templates,
                                            delta_pc_threshold = kwargs.pop("exp_delta_pc_threshold",1.0),
                                            correction_factor = kwargs.pop("exp_correction_factor",0.5),
                                            exp_loops = kwargs.pop("exp_loops",100))
        


    def update(self, video_frame):
        # TODO save experience map
        
        # convert video_frame to grayscale
        # plt.imshow(video_frame)
        # plt.show()
        
        # get most active visual template (bassed on current video_frame)
        
        # get odometry from video
        
        # update post cells
        
        # get 'best' center of pose cell activity
        
        # run an iteration fo the experience map
        
        # store current odometry for next update
        pass
        

if __name__ == "__main__":
    
    # instantiate a "RatSLAM" model
    rs = RatSLAM( fov_deg = 50.,
                  odo_shift_match = 20,
                  odo_trans_scale = 100.,
                  im_x_offset = 15,
                  vt_match_threshold = 0.09,
                  im_vt_y_range = slice((480/2 - 80 - 40),(480/2 + 80 - 40)),
                  im_vt_x_range = slice((640/2 - 280 + 15),(640/2 + 280 + 15)),
                  im_trans_y_range = slice(270,430),
                  im_rot_y_range = slice(75,240),
                  im_odo_x_range = slice((180 + 15),(460 + 15)),
                  exp_delta_pc_threshold = 1.0,
                  exp_correction_factor = 0.5,
                  exp_loops = 100,
                  pc_trans_scaling = 1./10.)
    
    # get the video source
    block_read = 100
    render_rate = 10
    
    test_video = DirVideoSource('/Users/graham/Desktop/ratslam/videos/stlucia_0to21000',"%06i.png",1)
    n_frames = 2102
    # test_video = FFMpegVideoSource("stlucia_1to21000.mov")
    
    # feed each video frame into the model
    # frame = test_video.frame
    
    # while frame is not None:
    for i in xrange(n_frames):
        frame = test_video.get_frame()
        
        # convert frame into form the model wants
        frame = np.mean(frame, 2)
        
        # update the model with the new frame
        rs.update(frame)  
        
        # Report some diagnostic info
        pass
        
        # fetch the next frame
        frame = test_video.advance()
