#!/usr/bin/env python

import pose_cell_network
import experience_map
import visual_odometer
import visual_templates
import video_source

class RatSLAM:
    """ A complete rat slam instance
        
        (Matlab version: equivalent to rs_main)
    """
    
    def __init__(self, **kwargs):
        pose_cell_shape = kwargs.pop("pose_cell_dimensions", (100,100,60))
        
                
        self.odometer = SimpleVisualOdometer(fov_deg = kwargs.pop("fov_deg",50),
                                             im_trans_y_range = kwargs.pop("im_trans_y_range"),
                                             im_rot_y_range = kwargs.pop("im_rot_y_range"),
                                             im_odo_x_range = kwargs.pop("im_odo_x_range"),
                                             shift_match = kwargs.pop("odo_shift_match",20),
                                             trans_scale = kwargs.pop("odo_trans_scale",100.))
        
        self.view_templates = ViewTemplateCollection( 
                    template_decay = kwargs.pop('template_decay', 1.0),
                    y_range = kwargs.pop('im_vt_y_range', None),
                    x_range = kwargs.pop('im_vt_x_range', None),
                    shift_match = kwargs.pop('odo_shift_match', None),
                    match_threshold = kwargs.pop('vt_match_threshold', None))
                
        self.pose_cell_network = PoseCellNetwork(pose_cell_shape,
                                                 self.view_templates)
        
        
        self.experience_map = ExperienceMap(self.pose_cell_network,
                                            self.view_templates,
                                            delta_pc_threshold = kwargs.pop("exp_delta_pc_threshold",1.0),
                                            correction_factor = kwargs.pop("exp_correction_factor",0.5),
                                            exp_loops = kwargs.pop("exp_loops",100))
        


    def update(self, video_frame):
        
        pass
        

if __name__ == "__main__":
    
    # instantiate a "RatSLAM" model
    rs = RatSlam( fov_deg = 50.,
                  odo_shift_match = 20,
                  odo_trans_scale = 100.,
                  im_trans_y_range = 270:430,
                  im_x_offset = 15,
                  vt_match_threshold = 0.09,
                  im_vt_y_range = (480/2 - 80 - 40):(480/2 + 80 - 40),
                  im_vt_x_range = (640/2 - 280 + 15):(640/2 + 280 + 15),
                  im_trans_y_range = 270:430,
                  im_rot_y_range = 75:240,
                  im_odo_x_range = (180 + 15):(460 + 15),
                  exp_delta_pc_threshold = 1.0,
                  exp_correction_factor = 0.5,
                  exp_loops = 100,
                  pc_trans_scaling = 1./10.)
    
    # get the video source
    block_read = 100
    render_rate = 10
    
    video_source = FFMpegVideoSource("stlucia_1to21000.mov")
    
    # feed each video frame into the model
    frame = video_source.frame

    while frame is not None:
        
        # convert frame into form the model wants
        frame = mean(frame, 2)
        
        # update the model with the new frame
        rs.update(frame)  
        
        # Report some diagnostic info
        pass
        
        # fetch the next frame
        frame = video_source.advance()
