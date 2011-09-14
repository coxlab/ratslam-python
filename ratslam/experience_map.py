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
    
    def __init__(self, parent, x_pc, y_pc, th_pc, vt, x_m, y_m, facing_rad):
        self.x_pc = x_pc
        self.y_pc = y_pc
        self.th_pc = th_pc
        
        self.facing_rad = facing_rad
                
        self.vt = vt
        
        self.links = []
        self.x_m = x_m #x_m is xcoord in experience map
        self.y_m = y_m #y_m is ycoord in experience map
    
        self.parent_map = parent

    def link_to(self, target):
        pm = self.parent_map
        d = sqrt(pm.accum_delta_x**2 + pm.accum_delta_y**2)
        heading_rad = signed_delta_rad(self.facing_rad, 
                                       arctan2(pm.accum_delta_y, 
                                               pm.accum_delta_x))
        facing_rad = signed_delta_rad(self.facing_rad, 
                                      pm.accum_delta_facing)

        new_link = ExperienceLink(target, facing_rad, d, heading_rad)
        self.links.append(new_link)

class ExperienceLink:
    "A directed link between two Experience objects"
    
    def __init__(self, target, facing_rad, d, heading_rad):
        self.target = target
        self.facing_rad = facing_rad
        self.d = d
        self.heading_rad = heading_rad
        

class ExperienceMap:
    def __init__(self, **kwargs):
        
        self.exps = []
        self.current_exp = None

        self.accum_delta_x = 0
        self.accum_delta_y = 0
        self.accum_delta_facing = pi/2
        
        # a link to a collection of view templates
        #self.view_templates = template_collection.templates
       
        self.current_vt = None
        
        # TODO: this doesn't appear to be referenced anywhere
        #self.pose_cell_network = posecellnetwork
        
        self.PC_DIM_XY = kwargs.pop('PC_DIM_XY', 61)
        self.PC_DIM_TH = kwargs.pop('PC_DIM_TH', 36)
        self.EXP_DELTA_PC_THRESHOLD = kwargs.pop('EXP_DELTA_PC_THRESHOLD', 1.0)
        
        self.exploops = kwargs.pop('exp_loop_iter', 100)
        self.exp_correction = kwargs.pop('exp_correction', 0.5)
        
        self.history = []
     
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
    
        
    # def link_exps(self, curr_exp_id, new_exp_id):
    # 
    #     d = sqrt(self.accum_delta_x**2 + self.accum_delta_y**2)
    #     heading_rad = signed_delta_rad(self.exps[curr_exp_id].facing_rad, 
    #                                        arctan2(self.accum_delta_y, 
    #                                                self.accum_delta_x))
    #     facing_rad = signed_delta_rad(self.exps[curr_exp_id].facing_rad, 
    #                                       self.accum_delta_facing)
    #     
    #     nlink = ExperienceLink(exp_id = new_exp_id, 
    #                            d = d, 
    #                            heading_rad = heading_rad, 
    #                            facing_rad = facing_rad)
    #                            
    #     curr_exp = self.exps[curr_exp_id]
    #     if curr_exp.links!=None:
    #         curr_exp.links.append(nlink)
    #     else:
    #         curr_exp.links = [nlink]


    def create_and_link_new_exp(self, nx_pc, ny_pc, nth_pc, vt):
        "Create a new experience and link current experience to it"

        new_x_m = self.accum_delta_x
        new_y_m = self.accum_delta_y
        new_facing_rad = clip_rad_180(self.accum_delta_facing)
        
        # add contributions from the current exp, if one is available
        if self.current_exp is not None:
            new_x_m += self.current_exp.x_m
            new_y_m += self.current_exp.y_m
            
            # TODO: no contribution from current_exp?
            new_facing_rad = clip_rad_180(self.accum_delta_facing)
    
        # create a new expereince
        new_exp = Experience(self, x_pc = nx_pc, y_pc = ny_pc, th_pc = nth_pc, 
                             vt = vt, x_m = new_x_m, y_m = new_y_m, 
                             facing_rad = new_facing_rad)
        
        
        if self.current_exp is not None:
            # link the current_exp for this one
            self.current_exp.link_to(new_exp)
        
        # add the new experience to the map
        self.exps.append(new_exp)
        
        # add this experience to the view template for efficient lookup
        vt.exps.append(new_exp)

        return new_exp
        
    def update(self, vtrans, vrot, x_pc, y_pc, th_pc, vt):
        """ Update the experience map
        
            (Matlab version: equivalent to rs_experience_map_iteration)
        """
        
        # update accumulators
        self.accum_delta_facing = clip_rad_180(self.accum_delta_facing+vrot)
        self.accum_delta_x += vtrans*cos(self.accum_delta_facing)
        self.accum_delta_y += vtrans*sin(self.accum_delta_facing)

        # check if this the first update
        if self.current_exp is None:
            # first experience
            delta_pc = 0
        else:
            # subsequent experience
            delta_pc = sqrt(min_delta(self.current_exp.x_pc, 
                                      x_pc, self.PC_DIM_XY)**2 + \
                            min_delta(self.current_exp.y_pc, 
                                      y_pc, self.PC_DIM_XY)**2 + \
                            min_delta(self.current_exp.th_pc, 
                                      th_pc, self.PC_DIM_TH)**2) 

        
        # if this view template is not associated with any experiences yet,
        # or if the pc x,y,th has changed enough, create and link a new exp
        if len(vt.exps) == 0 or delta_pc > self.EXP_DELTA_PC_THRESHOLD:
                                    
            new_exp = self.create_and_link_new_exp(x_pc, y_pc, th_pc, vt)
            self.current_exp = new_exp
            
            # reset accumulators
            self.accum_delta_x = 0
            self.accum_delta_y = 0
            self.accum_delta_facing = self.current_exp.facing_rad
        
        # if the view template has changed (but isn't new) search for the 
        # mathcing experience
        elif vt != self.current_exp.vt:
            
            # find the exp associated with the current vt and that is under the
            # threshold distance to the centre of pose cell activity
            # if multiple exps are under the threshold then don't match (to 
            # reduce hash collisions)
            
            matched_exp = None
            
            delta_pcs = []
            n_candidate_matches = 0
            for (i, e) in enumerate(vt.exps):
                delta_pc = sqrt(min_delta(self.exps[e_id].x_pc, 
                                          x_pc, self.PC_DIM_XY)**2 + \
                                min_delta(self.exps[e_id].y_pc, 
                                          y_pc, self.PC_DIM_XY)**2 + \
                                min_delta(self.exps[e_id].th_pc, 
                                          th_pc, self.PC_DIM_TH)**2)
                delta_pcs.append(delta_pc)
                
                if delta_pc < self.EXP_DELTA_PC_THRESHOLD:
                    n_candidate_matches += 1 
                

            if n_candidate_matches > 1:
                # this means we aren't sure about which experience is a match 
                # due to hash table collision instead of a false posivitive 
                # which may create blunder links in the experience map keep 
                # the previous experience matched_exp_count
                
                # TODO: raise?
                # TODO: what is being accomplished here
                #       check rs_experience_map_iteration.m, line 75-ish
                print("Too many candidate matches")
                pass
            else: 
                min_delta_val = min(delta_pcs)
                min_delta_id = argmin(delta_pcs)
                
                if min_delta_val < self.EXP_DELTA_PC_THRESHOLD:
                    matched_exp = vt.exps[min_delta_id]

                    # check if a link already exists
                    link_exists = False
                    
                    for linked_exp in [l.target for l in self.current_exp.links]:
                        if linked_exp == matched_exp:
                            link_exists = True
                            break
                    
                    if not link_exists:
                        self.current_exp.link_to(matched_exp)

                
                #self.exp_id = len(self.exps)-1

                if matched_exp is None:
                    matched_exp = self.create_and_link_exp(x_pc, y_pc, 
                                                           th_pc, vt_id)
                
                
                self.accum_delta_x = 0
                self.accum_delta_y = 0
                self.accum_delta_facing = self.current_exp.facing_rad
                self.current_exp = matched_exp
    
        
        # iteratively update the experience map with the new information     
        for i in range(0, self.exploops):
            for e0 in self.exps:
                for l in e0.links:
                    # e0 is the experience under consideration
                    # e1 is an experience linked from e0
                    # l is the link object which contains additoinal heading
                    # info

                    e1 = l.target
                    
                    # correction factor
                    cf = self.exp_correction
                    
                    # work out where exp0 thinks exp1 (x,y) should be based on 
                    # the stored link information
                    lx = e0.x_m + l.d * cos(e0.facing_rad + l.heading_rad)
                    ly = e0.y_m + l.d * sin(e0.facing_rad + l.heading_rad);

                    # correct e0 and e1 (x,y) by equal but opposite amounts
                    # a 0.5 correction parameter means that e0 and e1 will be 
                    # fully corrected based on e0's link information
                    e0.x_m = e0.x_m + (e1.x_m - lx) * cf
                    e0.y_m = e0.y_m + (e1.y_m - ly) * cf
                    e1.x_m = e1.x_m - (e1.x_m - lx) * cf
                    e1.y_m = e1.y_m - (e1.y_m - ly) * cf

                    # determine the angle between where e0 thinks e1's facing
                    # should be based on the link information
                    df = signed_delta_rad(e0.facing_rad + l.facing_rad, 
                                          e1.facing_rad)

                    # correct e0 and e1 facing by equal but opposite amounts
                    # a 0.5 correction parameter means that e0 and e1 will be 
                    # fully corrected based on e0's link information           
                    e0.facing_rad = clip_rad_180(e0.facing_rad + df * cf)
                    e1.facing_rad = clip_rad_180(e1.facing_rad - df * cf)
    
        self.history.append(self.current_exp)

        return

        