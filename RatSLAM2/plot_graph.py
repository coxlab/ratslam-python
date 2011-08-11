'''
Created on Jul 26, 2011

@author: Christine
'''

import csv, time, cv, vod2
import em
import localView as lv
import pc_network as pc
from pylab import  *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

imageDir = '/Users/Christine/Documents/REU Summer 2011/RatSLAM/Video/stlucia_matlab_testloop'
imageTemplate = 'mlpic%d.png'

def draw_position(x, y):
    scatter(x,y)

def draw_x_y_z(pcmax, subplot):
    ax3 = Axes3D(gcf(), rect=subplot.get_position())
    ax3.scatter(xcoord, ycoord, thcoord, 'z')
    ax3.set_xlim3d([0, 61])
    ax3.set_ylim3d([0, 61])
    ax3.set_zlim3d([0, 36])

def get_image(index):
    return '/'.join((imageDir, imageTemplate % (index+1)))

def initialize_em(tempCol, vod, pcnet):
    [x_pc, y_pc, th_pc] = pcnet.max_pc
    vt_id = tempCol.curr_vc
    link = em.link(exp_id = 0, facing_rad = pi/2, heading_rad = pi/2, d = 0)
    links = []
    emap = em.exp_map(pcnet, tempCol)
    emap.update(vod.delta[0], vod.delta[1], pcnet.max_pc[0], pcnet.max_pc[1], pcnet.max_pc[2], vt_id)
    return emap
    
#initializing position of the pose cell network activity bubble at center
def initialize_pc(tempCol, vod):
    
    pcnet = pc.pc_Network([61,61,36])
    xy_pc = 61/2+1 
    th_pc = 36/2+1 
    pcnet.posecells[xy_pc, xy_pc, th_pc] = 1
    
    v_temp = tempCol.get_template(0)
    pcnet.update(vod.delta, v_temp) 
    pcmax = pcnet.get_pc_max(pcnet.avg_xywrap, pcnet.avg_thwrap)
    
    return pcnet

#creating visual templatecollection and initializing it with the first image.
def initialize_lv():
    
    tempCol = lv.templateCollection()
    im = cv.LoadImage(get_image(0), cv.CV_LOAD_IMAGE_GRAYSCALE)
    vt_id0 = tempCol.update(zeros(561))
    vtid = tempCol.match(im)
    
    return tempCol

#initializing Visual Odometer
def initialize_odo():
    
    im0 = get_image(0)
    vod = vod2.VisOdom()
    x = vod.update(im0)
    
    return vod

tempCol = initialize_lv()
vod = initialize_odo()
pcnet = initialize_pc(tempCol, vod)
emap = initialize_em(tempCol, vod, pcnet)

xcoord = []
ycoord = []
thcoord = []

######################################################################################################################################################################
for i in xrange(1000):
    input = raw_input()
    if input == 'q':
        break
    
    im = get_image(i) #this is the raw image
    curr_im = cv.LoadImage(im, cv.CV_LOAD_IMAGE_GRAYSCALE) 
    
    #get visual template
    vc = tempCol.match(curr_im)
    v_temp = tempCol.get_template(vc)
    
    # get odometry
    odo = vod.update(im)

    #get pcmax
    pcnet.update(vod.delta, v_temp) 
    pcmax = pcnet.get_pc_max(pcnet.avg_xywrap, pcnet.avg_thwrap)
    xcoord.append(pcmax[0])
    ycoord.append(pcmax[1])
    thcoord.append(pcmax[2])
    
    #get curr_exp_id
    id = emap.update(vod.delta[0], vod.delta[1], pcmax[0], pcmax[1], pcmax[2], vc)

    im = imread(im)

    subplot(221)
    imshow(im)
    a=gca()
    a.axis('off')
    title('Raw Image')
    
    subplot(222)
    draw_position(odo[0], odo[1])
    b = gca()
    title('Raw Odometry')
    b.set_xlim([-50, 100])
    b.set_ylim([0, 125])
    
    pcdata = subplot(223)
    draw_x_y_z(pcmax, pcdata)
    title('Pose Cell Activity')
    pcdata.axis('off')
    
    subplot(224)
    draw_position(emap.exps[id].x_m, emap.exps[id].y_m)
    title('Experience Map')
    d = gca()
    d.set_xlim([-50, 100])
    d.set_ylim([0, 120])


    print "Using frames %i and %i" % (i, i+1)
    
    savefig('/Users/Christine/Documents/REU Summer 2011/RatSLAM/Pyplot_Data/072711v2output%06i.png' % i)
    print "Press key to continue to next image or 'q' to quit"
    
######################################################################################################################################################################

