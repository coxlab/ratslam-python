import ratslam

import os, os.path
import csv
import time

from itertools import imap
from pylab import  *
import numpy

import pipeffmpeg as pff
from PIL import Image
import cStringIO as StringIO


class VideoSource (object):
    
    def __init__(self, video_file, grayscale=False):
        
        self.video_stream = pff.InputVideoStream(video_file, cache_size=300)
        self.grayscale = grayscale
        
        self.first_frame = self[0]
        
    
    def __getitem__(self, index):
        fr = self.video_stream[index]
        
        im = numpy.asarray( Image.open( StringIO.StringIO(fr) ) )
        
        if self.grayscale:
            return mean(im,2)
        else:
            return im


        
    

# class ImageDirectorySource (object):
# 
#     def __init__(self, base_path, 
#                        n_images = 1000,
#                        filename_template=DEFAULT_NAME_TEMPLATE):
#         self.base_path = base_path
#         self.filename_template = filename_template
#     
#     
#     def __getitem__(self, index):
#         path = os.path.join(self.base_path, 
#                             (self.filename_template) % (index+1))
#         #return cv.LoadImage(path, cv.CV_LOAD_IMAGE_GRAYSCALE) 
#         return None # TODO
#         
#     def __iter__(self):
#         return imap(self.__getitem__, range(0, self.n_images))


class RatSLAM (object):
    
    def __init__(self, image_source):
        self.image_source = image_source
        
        self.templates = self.initialize_visual_templates()
        self.visual_odometer = self.initialize_odo()
        self.pose_cell_network = self.initialize_pose_cell_network()
        self.experience_map = self.initialize_experience_map()
        
        self.time_step = 0
        
    #creating visual templatecollection and initializing it with the first image.
    def initialize_visual_templates(self):
    
        self.templates = ratslam.VisualTemplateCollection()
        im = self.image_source[0]
        vt_id0 = self.templates.update(zeros(561))
        self.templates.curr_vc = self.templates.match(im)
        
        return self.templates

    #initializing Visual Odometer
    def initialize_odo(self):
    
        im0 = self.image_source[0]
        vod = ratslam.VisualOdometer()
        x = vod.update(im0)
        
        return vod
        
    #initializing position of the pose cell network activity bubble at center
    def initialize_pose_cell_network(self):

        pcnet = ratslam.PoseCellNetwork([61,61,36])
        xy_pc = 61/2+1 
        th_pc = 36/2+1 
        pcnet.posecells[xy_pc, xy_pc, th_pc] = 1

        v_temp = self.templates.get_template(0)
        pcnet.update(self.visual_odometer.delta, v_temp) 
        pcmax = pcnet.get_pc_max(pcnet.avg_xywrap, pcnet.avg_thwrap)

        return pcnet

    def initialize_experience_map(self):
          [x_pc, y_pc, th_pc] = self.pose_cell_network.max_pc
          vt_id = self.templates.curr_vc
          link = ratslam.ExperienceLink(exp_id = 0, facing_rad = pi/2,
                                                    heading_rad = pi/2, 
                                                    d = 0)
          links = []
          emap = ratslam.ExperienceMap(self.pose_cell_network, 
                                       self.templates)
                                       
          emap.update(self.visual_odometer.delta[0], 
                      self.visual_odometer.delta[1], 
                      self.pose_cell_network.max_pc[0], 
                      self.pose_cell_network.max_pc[1], 
                      self.pose_cell_network.max_pc[2], vt_id)
          return emap

    def evolve(self):
        c = self.time_step
        self.time_step += 1
        
        self.current_image = self.image_source[c]
        
        #get visual template
        vc = self.templates.match(self.current_image)
        v_temp = self.templates.get_template(vc)
    
        # get odometry
        self.current_odo = self.visual_odometer.update(self.current_image)

        #get pcmax
        self.pose_cell_network.update(self.visual_odometer.delta, v_temp) 
        pcmax = self.pose_cell_network.get_pc_max(self.pose_cell_network.avg_xywrap, 
                                                  self.pose_cell_network.avg_thwrap)
        
        self.current_pose_cell = pcmax
        
        
        
        #get curr_exp_id
        self.exp_id = self.experience_map.update(self.visual_odometer.delta[0], 
                                            self.visual_odometer.delta[1], 
                                            pcmax[0], pcmax[1], pcmax[2], vc)
