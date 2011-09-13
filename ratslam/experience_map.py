from pylab import *

def min_delta(d1, d2, max):
    delta = min([abs(d1-d2), max-abs(d1-d2)])
    return delta

def clip_rad_180(angle):
    while angle > pi:
        angle -= 2*pi
    while angle <= -pi:
        angle += 2*pi
    return angle

def clip_rad_360(angle):
    while angle < 0:
        angle += 2*pi
    while angle >= 2*pi:
        angle -= 2*pi
    return angle

def signed_delta_rad(angle1, angle2):
    dir = clip_rad_180(angle2-angle1)
    
    delta_angle = abs(clip_rad_360(angle1)-clip_rad_360(angle2))
    
    if (delta_angle < (2*pi-delta_angle)):
        if (dir>0):
            angle = delta_angle
        else:
            angle = -delta_angle
    else: 
        if (dir>0):
            angle = 2*pi - delta_angle
        else:
            angle = -(2*pi-delta_angle)
    return angle

class Experience:
    "A point in the experience map"
    
    def __init__(self, **kwargs):
        self.x_pc = kwargs.pop('x_pc', 0)
        self.y_pc = kwargs.pop('y_pc', 0)
        self.th_pc = kwargs.pop('th_pc', 0)
                
        self.vt_id = kwargs.pop('vt_id', 0)
        self.exp_id = kwargs.pop('exp_id', 0) #index correlate on experience map/experience list
        
        self.links = kwargs.pop('links', []) #a link is another exp that this exp is connected to.
        self.x_m = kwargs.pop('x_m', 0) #x_m is xcoord in experience map
        self.y_m = kwargs.pop('y_m', 0) #y_m is ycoord in experience map
        
        self.facing_rad = kwargs.pop('facing_rad', 0)

class ExperienceLink:
    "A link between two Experience objects"
    
    def __init__(self, exp_id=0, facing_rad=0, d=0, heading_rad=0):
        self.exp_id = exp_id
        self.facing_rad = facing_rad
        self.d = d
        self.heading_rad = heading_rad

class ExperienceMap:
    def __init__(self, posecellnetwork, tempcol, **kwargs):
        self.exps = []
        self.exp_id = kwargs.pop('exp_id', None)

        self.accum_delta_x = 0
        self.accum_delta_y = 0
        self.accum_delta_facing = pi/2
        
        self.vt = tempcol.templates
        self.vt_id = kwargs.pop('vt_id', 0)
        self.pcnet = posecellnetwork
        
        self.PC_DIM_XY = kwargs.pop('PC_DIM_XY', 61)
        self.PC_DIM_TH = kwargs.pop('PC_DIM_TH', 36)
        self.EXP_DELTA_PC_THRESHOLD = kwargs.pop('EXP_DELTA_PC_THRESHOLD', 1.0)
        
        self.exploops = kwargs.pop('exp_loop_iter', 100)
        self.exp_correction = kwargs.pop('exp_correction', 0.5)
     
    # TODO: DDC: Huh? This returns nothing and has no side-effects...
    #            if a tree falls in the woods, does it make a sound?
    #
    # def get_exp(self, exp_id):
    #     [xpc, ypc, thpc] = [self.exps[exp_id].x_pc, 
    #                         self.exps[exp_id].y_pc, 
    #                         self.exps[exp_id].th_pc]
    #     vistemp =  self.exps[exp_id].vt_id
    #     ident = self.exps[exp_id].exp_id
    #     l = self.exps[exp_id].links
    #     [xm, ym] = [self.exps[exp_id].x_m, self.exps[exp_id].y_m]
    #     fr = self.exps[exp_id].facing_rad
    
        
    def link_exps(self, curr_exp_id, new_exp_id):

        d = sqrt(self.accum_delta_x**2 + self.accum_delta_y**2)
        heading_rad = signed_delta_rad(self.exps[curr_exp_id].facing_rad, 
                                           arctan2(self.accum_delta_y, 
                                                   self.accum_delta_x))
        facing_rad = signed_delta_rad(self.exps[curr_exp_id].facing_rad, 
                                          self.accum_delta_facing)
        
        nlink = ExperienceLink(exp_id = new_exp_id, 
                               d = d, 
                               heading_rad = heading_rad, 
                               facing_rad = facing_rad)
                               
        curr_exp = self.exps[curr_exp_id]
        if curr_exp.links!=None:
            curr_exp.links.append(nlink)
        else:
            curr_exp.links = [nlink]

    def create_exp(self, curr_exp_id, new_exp_id, 
                  nx_pc, ny_pc, nth_pc, nvt_id):
        "Create a new experience and link current experience to it"
                  
        #first you have to make a link between the current experience and the 
        # new one that is being created
        if (curr_exp_id==None):
            new_x_m = self.accum_delta_x
            new_y_m = self.accum_delta_y
            new_facing_rad = clip_rad_180(self.accum_delta_facing)
        
        else:
            self.link_exps(curr_exp_id, new_exp_id)
        
            #initialize exp map variable coordinates
            new_x_m = self.exps[curr_exp_id].x_m + self.accum_delta_x
            new_y_m = self.exps[curr_exp_id].y_m + self.accum_delta_y
            new_facing_rad = clip_rad_180(self.accum_delta_facing)
    
        #add new experience to experience map
        new_exp = Experience(x_pc = nx_pc, y_pc = ny_pc, th_pc = nth_pc, 
                             vt_id = nvt_id, exp_id = new_exp_id, 
                             x_m = new_x_m, y_m = new_y_m, 
                             facing_rad = new_facing_rad)
        self.exps.append(new_exp)
        
        # TODO: DDC what is this?
        #update vistemp/wtf. this seems to be aroundabout way of doing things.
        self.vt[nvt_id].exps.append(new_exp_id)
        if len(self.vt[nvt_id].exps)>len(self.vt[nvt_id].exps):
            temp = self.vt[nvt_id].exps[len(self.vt[nvt_id].exps)]
            self.vt[nvt_id].exps[len(self.vt[nvt_id].exps)] =new_exp_id
            self.vt[nvt_id].exps[-1] =temp
        
        return self.exps[new_exp_id] #returns the newly created experience
        
    def update(self, vtrans, vrot, x_pc, y_pc, th_pc, vt_id):
        """ Update the experience map
        
            (Matlab version: equivalent to rs_experience_map_iteration)
        """
        
        self.accum_delta_facing = clip_rad_180(self.accum_delta_facing+vrot)
        self.accum_delta_x += vtrans*cos(self.accum_delta_facing)
        self.accum_delta_y += vtrans*sin(self.accum_delta_facing)

        if (self.exp_id==None):
            delta_pc = 0
        else:
            delta_pc = sqrt(min_delta(self.exps[self.exp_id].x_pc, 
                                      x_pc, self.PC_DIM_XY)**2 + \
                            min_delta(self.exps[self.exp_id].y_pc, 
                                      y_pc, self.PC_DIM_XY)**2 + \
                            min_delta(self.exps[self.exp_id].th_pc, 
                                      th_pc, self.PC_DIM_TH)**2) 

        if (len(self.vt[vt_id].exps) == 0) or \
           (delta_pc > self.EXP_DELTA_PC_THRESHOLD):
            self.create_exp(self.exp_id, 
                            len(self.exps), 
                            x_pc, y_pc, th_pc, vt_id)
            self.exp_id = len(self.exps)-1
            self.accum_delta_x = 0
            self.accum_delta_y = 0
            self.accum_delta_facing = self.exps[self.exp_id].facing_rad
        
        elif vt_id != self.vt_id:
            
            # find the exp associated with the current vt and that is under the
            # threshold distance to the centre of pose cell activity
            # if multiple exps are under the threshold then don't match (to 
            # reduce hash collisions)
            
            matched_exp_id = 0
            matched_exp_count = 0
            delta_pc = []
            for search_id in xrange(len(self.vt[vt_id].exps)):
                e_id = self.vt[vt_id].exps[search_id]
                delta_pc.insert(search_id, 
                                sqrt(min_delta(self.exps[e_id].x_pc, 
                                                  x_pc, self.PC_DIM_XY)**2 + \
                                     min_delta(self.exps[e_id].y_pc, 
                                                  y_pc, self.PC_DIM_XY)**2 + \
                                     min_delta(self.exps[e_id].th_pc, 
                                                  th_pc, self.PC_DIM_TH)**2))
                if delta_pc[search_id] <self.EXP_DELTA_PC_THRESHOLD:
                    matched_exp_count += 1

            if matched_exp_count > 1:
                # this means we aren't sure about which experience is a match 
                # due to hash table collision instead of a false posivitive 
                # which may create blunder links in the experience map keep 
                # the previous experience matched_exp_count
                pass
            else:
                [min_delta_val, min_delta_id] = [min(delta_pc), 
                                             delta_pc.index(min(delta_pc))]
                
                if min_delta_val < self.EXP_DELTA_PC_THRESHOLD:
                    e_id = self.vt[vt_id].exps[min_delta_id]
                    matched_exp_id = self.exps[e_id].exp_id
                    
                    link_exists = False
                    for link_id in xrange(len(self.exps[self.exp_id].links)):
                        if self.exps[self.exp_id].links[link_id].exp_id == matched_exp_id:
                            link_exists = True
                            break
                    
                    if (link_exists!=True):
                        self.link_exps(self.exp_id, len(self.exps[self.exp_id].links))
                
                self.exp_id = len(self.exps)-1

                if matched_exp_id==0:
                    self.create_exp(self.exp_id, len(self.exps), x_pc, y_pc, th_pc, vt_id)
                    matched_exp_id = len(self.exps)
                    
                
                self.accum_delta_x = 0
                self.accum_delta_y = 0
                self.accum_delta_facing = self.exps[self.exp_id].facing_rad
        
        for i in xrange(self.exploops):
            for exp_id in xrange(len(self.exps)):
                for link_id in xrange(len(self.exps[self.exp_id].links)):
                    e0 = self.exp_id
                    e1 = self.exps[self.exp_id].links[link_id].exp_id
                    
                    lx = self.exps[e0].x_m + \
                         self.exps[e0].links[link_id].d * \
                            cos(self.exps[e0].facing_rad + \
                                self.exps[e0].links[link_id].heading_rad)
                                
                    ly = self.exps[e0].y_m +\
                         self.exps[e0].links[link_id].d * \
                            sin(self.exps[e0].facing_rad + \
                                self.exps[e0].links[link_id].heading_rad)
                                     
                    self.exps[e0].x_m += \
                                (self.exps[e1].x_m - lx)* self.exp_correction
                    self.exps[e0].y_m += \
                                (self.exps[e1].y_m - ly)* self.exp_correction
                    self.exps[e1].x_m -= \
                                (self.exps[e1].x_m - lx)* self.exp_correction
                    self.exps[e1].y_m -= \
                                (self.exps[e1].y_m - ly)* self.exp_correction
                    
                    df = signed_delta_rad(\
                        self.exps[e0].facing_rad + \
                            self.exps[e0].links[link_id].facing_rad,
                        self.exps[e1].facing_rad)
                    
                    self.exps[e0].facing_rad = \
                                clip_rad_180(self.exps[e0].facing_rad + \
                                             df*self.exp_correction)
                                             
                    self.exps[e1].facing_rad = \
                                clip_rad_180(self.exps[e1].facing_rad - \
                                             df*self.exp_correction)
        
        #self.get_exp(self.exp_id)
        self.vt_id = vt_id
    
        return self.exp_id

        