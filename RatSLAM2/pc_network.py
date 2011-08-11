'''
Created on Jun 27, 2011

@author: Christine
'''
import localView as lv
from pylab import *

class pc_Network:
    
    def __init__(self, shape, **kwargs):
        
        self.shape = kwargs.pop('pc_shape', shape) # [61, 61, 36]
        PC_DIM_XY = self.shape[0]
        PC_DIM_TH = self.shape[2]
        
        self.posecells = zeros(shape)
        
        self.vt_inject = kwargs.pop('vt_inject', 0.1)
        self.pc_vtrans_scaling = kwargs.pop('vtrans_scaling', float64(0.1)) 
        
        #excitation constants
        self.e_wdim = kwargs.pop('e_wdim', 7)
        e_dim_half = self.e_wdim/2
        self.e_xywrap = append(append(arange(PC_DIM_XY-e_dim_half, PC_DIM_XY), arange(0, PC_DIM_XY)), arange(0, PC_DIM_XY-e_dim_half)) 
        self.e_thwrap = append(append(arange(PC_DIM_TH-e_dim_half, PC_DIM_TH), arange(0, PC_DIM_TH)), arange(0, PC_DIM_TH-e_dim_half))
        self.e_pcw = self.create_pcWeights(self.e_wdim, 1)
        
        #inhibition constants
        self.i_wdim = kwargs.pop('i_wdim', 5)
        i_dim_half = self.i_wdim/2
        self.i_xywrap = append(append(arange(PC_DIM_XY-i_dim_half, PC_DIM_XY), arange(0, PC_DIM_XY)), arange(0, PC_DIM_XY-i_dim_half))
        self.i_thwrap = append(append(arange(PC_DIM_TH-i_dim_half, PC_DIM_TH), arange(0, PC_DIM_TH)), arange(0, PC_DIM_TH-i_dim_half))
        self.i_pcw = self.create_pcWeights(self.i_wdim, 2)
        
        self.global_inhibition = kwargs.pop('global_pc_inhibition', 0.00002)
        self.c_size_th = kwargs.pop('c_size_th', 2*float64(pi)/36)
        
        #finding pose cell centre constants
        self.xy_sum_sin = sin(arange(PC_DIM_XY)* 2*float64(pi)/PC_DIM_XY)
        self.xy_sum_cos = cos(arange(PC_DIM_XY)* 2*float64(pi)/PC_DIM_XY)
        self.th_sum_sin = sin(arange(PC_DIM_TH)* 2*float64(pi)/PC_DIM_TH)
        self.th_sum_cos = cos(arange(PC_DIM_TH)* 2*float64(pi)/PC_DIM_TH)
        
        self.cells_avg = kwargs.pop('cell_avg', 3)
        self.avg_wdim = kwargs.pop('avg_wdim', 7)
        avg_dim_half = self.avg_wdim/2
        self.avg_xywrap = append(append(arange(PC_DIM_XY-avg_dim_half, PC_DIM_XY), arange(0, PC_DIM_XY)), arange(0, PC_DIM_XY-avg_dim_half))
        self.avg_thwrap = append(append(arange(PC_DIM_TH-avg_dim_half, PC_DIM_TH), arange(0, PC_DIM_TH)), arange(0, PC_DIM_TH-avg_dim_half))
        
        self.max_pc = [0, 0, 0]
    
    def create_pcWeights(self, dim, var): #dim is dimension and var is variance
        weight = zeros([dim, dim, dim])
        dim_centre = math.floor(dim/2)
        
        for x in xrange(dim):
            for y in xrange(dim):
                for z in xrange(dim): 
                    weight[x,y,z] = 1.0/(var*math.sqrt(2*pi))*math.exp(-((x-dim_centre)**2+(y-dim_centre)**2+(z-dim_centre)**2)/(2*var**2)) 

        total = abs(sum(sum(sum(weight)))) 
        weight = weight/total
    
        return weight

    def activityMatrix(self, xywrap, thwrap, wdim, pcw): 
        
        #returns gaussian distribution of excitation/inhibition pc activity
        pca_new = zeros(self.shape)  
        indices = nonzero(self.posecells) 
        for index in xrange(len(indices[0])):
            (i, j, k) = (indices[0][index], indices[1][index], indices[2][index])
            pca_new[ix_(xywrap[i:i+wdim], xywrap[j:j+wdim],thwrap[k:k+wdim])] += self.posecells[i,j,k]*pcw
        
        return pca_new
    
    def get_pc_max(self, xywrap, thwrap):
        
        (x,y,z) = unravel_index(self.posecells.argmax(), self.posecells.shape)
        
        z_posecells=zeros(self.shape) 
        
        zval = self.posecells[ix_(xywrap[x:x+7], xywrap[y:y+7], thwrap[z:z+7])]
        z_posecells[ix_(self.avg_xywrap[x:x+self.cells_avg*2+1], self.avg_xywrap[y:y+self.cells_avg*2+1], self.avg_thwrap[z:z+self.cells_avg*2+1])] = zval
        
        # get the sums for each axis
        x_sums = sum(sum(z_posecells, 2), 1) 
        y_sums = sum(sum(z_posecells, 2), 0)
        th_sums = sum(sum(z_posecells, 1), 0)
        th_sums = th_sums[:]
        
        # now find the (x, y, th) using population vector decoding to handle the wrap around 
        x = (arctan2(sum(self.xy_sum_sin*x_sums), sum(self.xy_sum_cos*x_sums)) *self.shape[0]/(2*pi)) % (self.shape[0])
        y = (arctan2(sum(self.xy_sum_sin*y_sums), sum(self.xy_sum_cos*y_sums)) *self.shape[0]/(2*pi)) % (self.shape[0])
        th = (arctan2(sum(self.th_sum_sin*th_sums), sum(self.th_sum_cos*th_sums)) *self.shape[2]/(2*pi)) % (self.shape[2])

        return (x, y, th)
    
    def update(self, ododelta, v_temp): 
        
        vtrans = ododelta[0]*self.pc_vtrans_scaling 
        vrot = ododelta[1] 

        #if this visual template has been activated before, inject more energy into the pc associated with it.
        if (v_temp.first != True): 
            act_x = min([max([round(v_temp.x_pc), 1]), self.shape[0]]) 
            act_y = min([max([round(v_temp.y_pc), 1]), self.shape[0]])
            act_th = min([max([round(v_temp.th_pc), 1]), self.shape[2]])
    
            energy = self.vt_inject * 1.0/30.0 * (30.0 - math.exp(1.2 * v_temp.activity))
            if energy > 0:
                self.posecells[act_x, act_y, act_th] += energy;
        
        #excitation weighted matrix                                                            
        self.posecells = self.activityMatrix(self.e_xywrap, self.e_thwrap, self.e_wdim, self.e_pcw) 
        
        #inhibition weighted matrix
        self.posecells = self.posecells - self.activityMatrix(self.i_xywrap, self.i_thwrap, self.i_wdim, self.i_pcw) 
        
        #global inhibition
        self.posecells[self.posecells<self.global_inhibition] = 0
        self.posecells[self.posecells >= self.global_inhibition] -=self.global_inhibition

        #normalization
        total = (sum(sum(sum(self.posecells))))
        self.posecells = self.posecells/total
        
        #path integration for trans
        for dir_pc in xrange(1, self.shape[2]): #TODO: only goes through 35 iterations when it should go through 36
            direction = float64(dir_pc-1) * self.c_size_th 
            # N,E,S,W are straightforward
            if (direction == 0):
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + roll(self.posecells[:,:,dir_pc], 1,1)*vtrans
            elif direction == pi/2:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + roll(self.posecells[:,:,dir_pc], 1,0)*vtrans
            elif direction == pi:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + roll(self.posecells[:,:,dir_pc], -1,1)*vtrans
            elif direction == 3*pi/2:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + roll(self.posecells[:,:,dir_pc], -1,0)*vtrans
            else:
                pca90 = rot90(self.posecells[:,:,dir_pc], floor(direction *2/pi))
                dir90 = direction - floor(direction *2/pi) * pi/2
                pca_new=zeros([self.shape[0]+2, self.shape[0]+2])   
                pca_new[1:-1, 1:-1] = pca90 
                weight_sw = (vtrans**2) *cos(dir90) * sin(dir90)
                weight_se = vtrans*sin(dir90) - (vtrans**2) *cos(dir90) * sin(dir90)
                weight_nw = vtrans*cos(dir90) - (vtrans**2) *cos(dir90) * sin(dir90)
                weight_ne = 1.0 - weight_sw - weight_se - weight_nw
          
                pca_new = pca_new*weight_ne + roll(pca_new, 1, 1)*weight_nw + roll(pca_new, 1, 0)*weight_se + \
                            roll(roll(pca_new, 1, 1), 1, 0)*weight_sw

                pca90 = pca_new[1:-1, 1:-1]
                pca90[1:, 0] = pca90[1:, 0] + pca_new[2:-1, -1]
                pca90[1, 1:] = pca90[1, 1:] + pca_new[-1, 2:-1]
                pca90[0,0] = pca90[0,0] + pca_new[-1,-1]

                #unrotate the pose cell xy layer
                self.posecells[:,:,dir_pc] = rot90(pca90, 4 - floor(direction * 2/pi))

        #path integration for rot
        if vrot != 0: 
            weight = (abs(vrot)/self.c_size_th)%1
            if weight == 0:
                weight = 1.0
            shift_1 = int(sign(vrot) * floor(abs(vrot)/self.c_size_th))
            shift_2 = int(sign(vrot) * ceil(abs(vrot)/self.c_size_th))
            self.posecells = roll(self.posecells, shift_1, 2) * (1.0 - weight) + roll(self.posecells, shift_2, 2) * (weight)
        
        self.max_pc = self.get_pc_max(self.avg_xywrap, self.avg_thwrap)
    
        return self.max_pc

        
        
                             

