class PoseCellNetwork:

    def __init__(self, shape):
        self.activities = array(shape)

        self.view_template_inject_energy = None # TODO
        
        # excitatory parameters
        self.e_xy_wrap = None # TODO
        self.e_th_wrap = None # TODO
        self.e_w_dim = None # TODO
        self.excitatory_weights = None # TODO
        
        # inhibitory parameters
        self.i_xy_wrap = None # TODO
        self.i_th_wrap = None # TODO
        self.i_w_dim = None # TODO
        self.inhibitory_weights = None # TODO
        
        self.c_size_th = None # TODO
    
    def deafult_pose_cell_weight_distribution(self, dim, var):
        """ Create a 3D normalized distribution of size dim^3,
            with a variance of var
            
            (Matlab version: equivalent to rs_create_posecell_weights)
        """
        
        dim_center = floor(dim/2.);
        weights = zeros((dim,dim,dim))
        for x in range(0, dim):
            for y in range(0, dim):
                for z in range(0, dim):
                    weights[x,y,z] = 
                        1./(var*sqrt(2*pi))*exp((-(x-dim_center)**2 -       \
                            (y-dim_center)**2-(z-dim_center)**2)/(2*var^2));
        total = sum( weights.ravel() ) 
        return weights / total
    
    def update(self, view_template, trans_est, rot_est):
        """ Evolve the network, given a visual template input and estimates of 
            translation and rotation (e.g. from visual odometry)
            
            (Matlab version: equivalent to rs_posecell_iteration) 
        """
        
        if not view_template.first:
            act_x = min( max(round(view_template.x_pc),0), 
                         self.activities.shape[0]-1 )
            act_y = min( max(round(view_template.y_pc),0), 
                         self.activities.shape[1]-1 )
            act_th = min( max(round(view_template.th_pc),0), 
                          self.activities.shape[2]-1)
            
            energy = self.view_template_inject_energy * (1/30.) * \
                     (30 - exp(1.2 * view_template.template_decay))
            
            if energy > 0:
                activities[act_x, act_y, act_th] += energy
        
        # local excitation
        new_activity = zeros_like(self.activities)
        for x in range(0, self.activities.shape[0]):
            for y in range(0, self.activities.shape[1]):
                for z in range(0, activities.shape[2]):
                    if activities[x,y,z] != 0:
                        xs = self.e_xy_wrap[x:x+self.w_e_dim-1]
                        ys = self.e_xy_wrap[y:y+self.w_e_dim-1]
                        ths = self.e_th_wrap[z:z+self.w_e_dim-1]
                        new_activity[xs,ys,th] += self.activities[x,y,s] * \
                                                  self.excitatory_weights
        
        self.activities = new_activity
        
        # local inhibition
        new_activity = zeros_like(self.activities)
        for x in range(0, self.activities.shape[0]):
            for y in range(0, self.activities.shape[1]):
                for z in range(0, self.activities.shape[2]):
                    if self.activities[x,y,z] != 0:
                        xs = self.i_xy_wrap[x:x+self.w_i_dim-1]
                        ys = self.i_xy_wrap[y:y+self.w_i_dim-1]
                        ths = self.i_th_wrap[z:z+self.w_i_dim-1]
                        new_activity[xs,ys,th] += self.activities[x,y,s] * \
                                                  self.inhibitory_weights
        
        self.activities -= new_activity
        
        # global inhibition
        self.activities -= self.global_inhibition
        self.activities[self.activities < 0.0] = 0.0
        
        # normalization
        self.activities /= sum(self.activities.ravel())
        
        # path integration
        # trans_est affects xy direction
        # rot_est affects th
        for dir_pc in range(0, self.activities.shape[2]):
            direction = dir_pc * self.c_size_th
            
            # TODO: left off at line 109
            if direction == 0:
                self.activities[:,:,dir_pc] *= (1 - trans_est)
                self.activities[:,:,dir_pc] += \
                    roll(self.activities[:,:,dir_pc],1,1)*trans_est
            elif direction == pi/2.:
                self.activities[:,:,dir_pc] *= (1 - trans_est)
                self.activities[:,:,dir_pc] += \
                    roll(self.activities[:,:,dir_pc],1,0)*trans_est
            elif direction == pi:
                self.activities[:,:,dir_pc] *= (1 - trans_est)
                self.activities[:,:,dir_pc] += \
                    roll(self.activities[:,:,dir_pc],-1,1)*trans_est
            elif direction == 3*pi/2.:
                self.activities[:,:,dir_pc] *= (1 - trans_est)
                self.activities[:,:,dir_pc] += \
                    roll(self.activities[:,:,dir_pc],-1,0)*trans_est
            else:
                # rotate activities instead of implementing for four quadrants
                activities90 = rot90(activities[:,:,dir_pc], 
                    floor(direction * 2. / pi))
                dir90 = direction - floor(direction*2/pi) * pi / 2.
                
                # extend pose cell one unit each direction
                # work out weigh contribution to the NE cell from the SW,
                # NW, SE cells
                # given vtrans and the direction
                # weight_sw = v * cos(th) * v * sin(th)
                # weight_se = (1 - v * cos(th)) * v * sin(th)
                # weight_nw = (1 - v * sin(th)) * v * sin(th)
                # weight_ne = 1 - weight_sw - weight_se - weight_nw
                # think in terms of NE divided into 4 rectangles with the sides
                # given by vtrans and the angle
                
                new_act = zeros(activities.shape[0]+2)
                new_act[1:-1,1:-1] = activities90
                weight_sw = trans_est**2 * cos(dir90) * sin(dir90)
                weight_se = trans_est*sin(dir90) - \
                                    trans_est**2 * cos(dir90) * sin(dir90)
                weight_nw = trans_est*cos(dir90) - \
                                    trans_est**2 * cos(dir90) * sin(dir90)
                weight_ne = 1.0 - weight_sw - weight_se - weight_nw
                
                # circular shift and multiple by the contributing weight
                # copy those shifted elements for the wrap around       
                new_act = new_act*weight_ne + \
                          roll(new_act, 1, 1) * weight_nw + \
                          roll(new_act, 1, 0) * weight_se + \
                          roll(roll(new_act,1,0),1,1) * weight_sw
                activities90 = new_act[1:-1,1:-1]
                activities90[1:,0] += new_act[2:-1,-1]
                activities90[0,1:] += new_act[-1,2:-1]
                activities90[0,0] += new_act[-1,-1]

                # unrotate the pose cell xy layer
                activities[:,:,dir_pc] = rot90(activities90,
                                               4 - floor(direction*2/pi))
        # Path integration: Theta
        # shift pose cells +/- theta, given rot_est
        if rot_est is not 0:
            # mod to work out the partial shift amount
            weight = mod(abs(rot_est) / self.activities.shape[2],1)
            if weight == 0:
                weight = 1.0
            roll_amount1 = sign(rot_est) * \
                                floor(abs(rot_est)/self.activities[2])
            roll_amount2 = sign(rot_est) * \
                                ceil(abs(rot_est)/self.activities[2])
                          
            self.activities = roll(self.activities,roll_amount1,2)     \
                                                      *  (1.-weight) + \
                              roll(self.activities,roll_amount2,2)     \
                                                      *  (weight)
    
    
    def activty_packet_center(self):
        """ Find the x,y,th center of the activity in the network
        
            (Matlab version: equivalent to rs_get_posecell_xyth)
        """
        # find the most active cell
        (x,y,z) = unravel_index( activies.argmax(), activities.shape )
        
        # take max +- avg cell in 3D space (whatever that means...)
        z_pose_cells = zeros(activities.shape)
        
        z_val = self.activities[self.avg_xy_wrap[x:x+self.n_cells_to_average*2],
                                self.avg_xy_wrap[y:y+self.n_cells_to_average*2],
                                self.avg_th_wrap[z:z+self.n_cells_to_average*2]]
        
        z[ self.avg_xy_wrap[x:x+self.n_cells_to_average*2],
           self.avg_xy_wrap[y:y+self.n_cells_to_average*2],
           self.avg_th_wrap[z:z+self.n_cells_to_average*2] ] = z_val
                
        # get the sums for each axis
        x_sums = sum( sum( z, 1), 2 ).T
        y_sums = sum( sum( z, 0), 2 )
        th_sums = sum( sum( z, 0), 1).T
        
        # find the x,y,th using population vector decoding
                                    
        x = mod( arctan2( sum(self.xy_sum_sin_lookup * x_sums),
                          sum(self.xy_sum_cos_lookup * x_sums) ) * \
                              self.activities.shape[0] / (2 * pi),
                          self.activities.shape[0] )
                 
        y = mod( arctan2( sum(self.xy_sum_sin_lookup * y_sums),
                          sum(self.xy_sum_cos_lookup * y_sums) ) * \
                              self.activities.shape[1] / (2 * pi),
                          self.activities.shape[1] )
        th = mod( arctan2( sum(self.th_sum_sin_lookup * th_sums),
                           sum(self.th_sum_cos_lookup * th_sums) ) * \
                                self.activities.shape[2] / (2 * pi),
                           self.activities.shape[2] )
        return (x,y,th)
