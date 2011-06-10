
class Experience:
    "A point in the experience map"
        
    def __init__(self, id, x_pc, y_pc, th_pc, x_m,  y_m, facing_rad, vt_id):
        self.id = id
        self.x_pc = x_pc
        self.y_pc = y_pc
        self.th_pc = th_pc
        self.x_m = x_m
        self.y_m = y_m
        self.facing_rad = facing_rad
        self.vt_id = vt_id
        
        self.links = []
        
    def add_link(self, target, d, heading_rad, facing_rad):
        link = ExperienceLink(target, d, heading_rad, facing_rad)
        self.links.append(links)

class ExperienceLink:
    "A link between two Experience objects"
    
    def __init__(self, target, d, heading_rad, facing_rad):
        self.target = target
        self.d = d
        self.heading_rad = heading_rad
        self.facing_rad = facing_rad

class ExperienceMap:
    
    def __init__(self, pose_cell_network, view_templates, **kwargs):
        self.exps = []
        self.current_exp_id = 0
        self.pc_network_shape = pose_cell_network.shape
        self.view_templates = view_templates
        
        self.delta_pc_threshold = kwargs.pop("delta_pc_threshold", 1.0)
        self.correction_factor = kwargs.pop("correction_factor", 0.5)
        self.exp_loops = kwargs.pop("exp_loops", 100)
        
    def update(self, vt_id, trans_est, rot_est, pose_cell_packet_center):
        """ Update the experience map
        
            (Matlab version: equivalent to rs_experience_map_iteration)
        """
        (x_pc, y_pc, th_pc) = pose_cell_packet_center
        vt = self.view_templates[vt_id]

        # integrate the delta x, y, facing
        accum_delta_facing = self.clip_rad_180(accum_delta_facing + rot_est);
        accum_delta_x = accum_delta_x + trans_est * cos(accum_delta_facing);
        accum_delta_y = accum_delta_y + trans_est * sin(accum_delta_facing);

        delta_pc = sqrt( self.min_delta( self.exps[curr_exp_id].x_pc, 
                                    x_pc, self.pc_network_shape[0])**2 + \
                         self.min_delta( self.exps[curr_exp_id].y_pc, 
                                    y_pc, self.pc_network_shape[1])**2 + \
                         self.min_delta( self.exps[curr_exp_id].th_pc, 
                                    th_pc, self.pc_network_shape[2])**2 )

        # if the vt is new or the pc x,y,th has changed enough create a new
        # experience
        if (vt.numexps == 0) or (delta_pc > self.delta_pc_threshold):

            self.add_new_exp(self.curr_exp_id, x_pc, y_pc, th_pc, vt_id)

            self.prev_exp_id = self.curr_exp_id
            self.curr_exp_id = self.numexps
            
            accum_delta_x = 0
            accum_delta_y = 0
            accum_delta_facing = self.exps[self.curr_exp_id].facing_rad
            
            curr_exp = self.exps[self.curr_exp_id]
        
        elif vt_id != prev_vt_id:
            
            # find the exp associated with the current vt and that is under the
            # threshold distance to the centre of pose cell activity
            # if multiple exps are under the threshold then don't match (to 
            # reduce hash collisions)
            matched_exp_id = 0
            matched_exp_count = 0
            
            for search_id in range(0, vt.numexps):
                search_exp = self.exps[vt.exps[search_id].id]
                search_x_pc = search_exp.x_pc
                search_y_pc = search_exp.y_pc
                search_th_pc = search_exp.th_pc
                delta_pc[search_id] = \
                    sqrt(self.min_delta( search_x_pc, 
                                         x_pc, self.pc_network_shape[0])**2+\
                         self.min_delta( search_y_pc, 
                                         y_pc, self.pc_network_shape[1])**2+\
                         self.min_delta( search_th_pc, 
                                         th_pc, self.pc_network_shape[2])**2)
                                         
                if delta_pc[search_id] < self.delta_pc_threshold:
                   matched_exp_count += 1; 

            if matched_exp_count > 1:
                # this means we aren't sure about which experience is a match due
                # to hash table collision
                # instead of a false posivitive which may create blunder links in
                # the experience map keep the previous experience
                # matched_exp_count
                pass
            else:
                min_delta = min(delta_pc)
                min_delta_id = argmin(delta_pc)
                
                if min_delta < self.delta_pc_threshold:

                    matched_exp_id = vt.exps[min_delta_id].id

                    # see if the prev exp already has a link to the current exp
                    link_exists = False
                    for link_id in range(0, len(self.exps[curr_exp_id].links)):
                        if curr_exp.links[link_id].exp_id == matched_exp_id:
                            link_exists = True
                            break
                    
                    # if we didn't find a link then create the link between 
                    # current experience and the expereince for the current vt
                    if not link_exists:
                        
                        d = sqrt(accum_delta_x**2 + accum_delta_y**2)
                        heading_rad = self.signed_delta_rad(curr_exp.facing_rad, 
                                                         arctan2(accum_delta_y, 
                                                                 accum_delta_x))
                        facing_rad = self.signed_delta_rad(curr_exp.facing_rad, 
                                                          accum_delta_facing)
                        curr_exp.add_link(self.exps[matched_expid],
                                          d, heading_rad, facing_rad)
                
                if matched_exp_id == 0:
                    newexp = self.add_new_exp(curr_exp_id,x_pc,y_pc,th_pc,vt_id)
                    matched_exp_id = newexp.id
                
                self.prev_exp_id = self.curr_exp_id
                self.curr_exp_id = matched_exp_id
                
                accum_delta_x = 0
                accum_delta_y = 0
                accum_delta_facing = self.exps[current_exp_id].facing_rad
                
        for i in range(0, self.exp_loops):
            # loop through experiences
            for exp_id in range(0, self.numexps):
                this_exp = self.exps[exp_id]
                for link_id in range(0, this_exp.numlinks):
                    # experience 0 has a link to experience 1
                    e0 = exp_id
                    e1 = this_exp.links[link_id].exp_id
                    linked_exp = self.exps[e1]
                    
                    # work out where e0 thinks e1 (x,y) should be based on 
                    # the stored link information
                    lx = this_exp.x_m + \
                         this_exp.links[link_id].d * \
                            cos(this_exp.facing_rad + \
                                this_exp.links[link_id].heading_rad)
                                
                    ly = this_exp.y_m + \
                         this_exp.links[link_id].d * \
                            sin(this_exp.facing_rad + \
                                this_exp.links[link_id].heading_rad)

                    # correct e0 and e1 (x,y) by equal but opposite amounts
                    # a 0.5 correction parameter means that e0 and e1 will 
                    # be fully corrected based on e0's link information
                    this_exp.x_m = this_exp.x_m + \
                                   (linked_exp.x_m-lx) * self.correction_factor
                                        
                    this_exp.y_m = this_exp.y_m + \
                                   (linked_exp.y_m-ly) * self.correction_factor
                                   
                    linked_exp.x_m = linked_exp.x_m - \
                                     (linked_exp.x_m-lx)*self.correction_factor

                    linked_exp.y_m = linked_exp.y_m - \
                                     (linked_exp.y_m-ly)*self.correction_factor

                    # determine the angle between where e0 thinks e1's 
                    # facing should be based on the link information
                    df = self.signed_delta_rad(
                                        (this_exp.facing_rad + \
                                        this_exp.links[link_id].facing_rad), 
                                        linked_exp.facing_rad)

                    # correct e0 and e1 facing by equal but opposite amounts
                    # a 0.5 correction parameter means that e0 and e1 will be fully
                    # corrected based on e0's link information           
                    this_exp.facing_rad = self.clip_rad_180(
                                    this_exp.facing_rad + df * \
                                            self.correction_factor)
                    linked_exp.facing_rad = self.clip_rad_180(
                                    linked_exp.facing_rad - df * \
                                            self.correction_factor)
        
        self.exp_history.append(self.curr_exp_id)


    def add_new_experience(self, curr_exp_id, 
                           new_exp_id, x_pc, y_pc, th_pc, vt_id):
        "Create a new experience and link current experience to it"
        
        # add link information to the current experience for the new experience
        # including the experience_id, odo distance to the experience, odo 
        # heading (relative to the current experience's facing) to the 
        # experience, odo delta  facing (relative to the current expereience's 
        # facing).
        
        curr_exp = self.exps[self.curr_exp_id]
        
        exp_id = len(self.exps)
        
        # create the new experience which will have no links to being with
        new_exp = Experience(exp_id, x_pc, y_pc, th_pc, vt_id,
                             curr_exp.x_m + accum_delta_x,   # x_m
                             curr_exp.y_m + accum_delta_y,   # y_m
                             self.clip_rad_180(accum_delta_facing), #facing_rad
                            )
        
        # compute properties of the link to the new experience
        d = sqrt(accum_delta_x**2 + accum_delta_y**2);
        heading_rad = self.signed_delta_rad(curr_exp.facing_rad, 
                                            arctan2(accum_delta_y, 
                                                    accum_delta_x))
        facing_rad = self.signed_delta_rad(curr_exp.facing_rad, 
                                           accum_delta_facing)

        # add the link to the new experience
        curr_exp.add_link(new_exp, d, heading_rad, facing_rad)
                             
        # add this experience id to the vt for efficient lookup
        self.view_templates[vt_id].exps.append(new_exp_id)

        # add the new Experience to the list
        self.exps.append(new_exp)
        
        return new_exp
        
    def clip_rad_360(self, angle):
        "Clip the input angle to between 0 and 2pi radians"
        while angle < 0:
            angle += 2*pi
        while angle >= 2*pi:
            angle -= 2*pi
        return angle
        
    def clip_rad_180(self, angle):
        "Clip the input angle to between -pi and pi radians"
        while angle > pi:
            angle -= 2*pi
        while angle <= -pi:
            angle += 2*pi
        return angle

    def min_delta(self, d1, d2, maxd):
        """ Get the minimum delta distance between two values assuming a wrap 
            to zero at max"""
        return min((abs(d1 - d2), maxd - abs(d1 - d2)))
    
    def signed_delta_rad(self, angle1, angle2):
        """ Get the signed delta angle from angle1 to angle2 handling the 
            wrap from 2pi to 0."""

        direction = self.clip_rad_180(angle2 - angle1)

        delta_angle = abs(self.clip_rad_360(angle1) - \
                          self.clip_rad_360(angle2))

        if (delta_angle) < (2*pi - delta_angle):
            if (direction > 0):
                angle = delta_angle
            else:
                angle = -delta_angle
        
        else:
            if (dir > 0):
                angle = 2*pi - delta_angle
            else:
                angle = -(2*pi - delta_angle)

        return angle