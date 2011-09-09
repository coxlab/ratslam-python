class RatSLAM:
    """ A complete rat slam instance
        
        (Matlab version: equivalent to rs_main)
    """
    
    def __init__(self, **kwargs):
        pose_cell_shape = kwargs.pop("pose_cell_dimensions", (100,100,60))
        self.PoseCellNetwork(pose_cell_shape)
        pass


class PoseCellNetwork:

    def __init__(self, shape):
        self.activities = array(shape)
        self.inhibitory_weights = None
        self.excitatory_weights = None
    
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
    
    def update(self, template_id, trans_est, rot_est):
        """ Evolve the network, given a visual template input and estimates of 
            translation and rotation (e.g. from visual odometry)
            
            (Matlab version: equivalent to rs_posecell_iteration) 
        """
    
        pass
        
    
    def activty_packet_center(self):
        """ Find the x,y,th center of the activity in the network
        
            (Matlab version: equivalent to rs_get_posecell_xyth)
        """
        x = 0
        y = 0
        th = 0
        return (x,y,th)
        

class ExperienceMap:
    
    def __init__(self):
        self.experience_map = None
        
    def update(self, template_id, trans_est, rot_est, pose_cell_packet_center):
        """ Update the experience map
        
            (Matlab version: equivalent to rs_experience_map_iteration)
        """


class VisualOdometer:
    
    def __init__(self):
        self.last_image = None
        self.fov_deg = 50.
        
        
    def estimate_odometry(self, im):
        """ Estimate the translation and rotation of the viewer, given a new 
            image sample of the environment
            
            (Matlab version: equivalent to rs_visual_odometry)
        """        
        dpp = self.fov_deg / im.shape[1]
        
        trans = 0
        rot = 0
        return trans, rot
        
    def compare_segments(self, seg1, seg2, slen, cwl):
        """ Do a simple template match of two segments to find the best match
        
            (Matlab version: equivalent to rs_compare_segments)
        """
        
        # assume a large difference
        mindiff = 1e6
        diffs = zeros(slen)
        
        return (offset, sdif)
