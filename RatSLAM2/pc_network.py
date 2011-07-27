'''
Created on Jun 27, 2011

@author: Christine
'''
import localView as lv
import numpy as np
import math, scipy, time

class pc_Network:
    def __init__(self, shape, **kwargs):
        self.shape = shape # self.shape[0] (and self.shape[1]) is equivalent to PC_DIM_XY, and self.shape[0] is PC_DIM_TH
        self.posecells = np.zeros(shape)
        self.vt_inject = 0.1
        self.pc_vtrans_scaling = np.float64(0.1) 
        
        #excitation constants
        self.e_xywrap = np.append(np.append(np.arange(58, 61), np.arange(0, 61)), np.arange(0, 3)) 
        self.e_thwrap = np.append(np.append(np.arange(33, 36), np.arange(0, 36)), np.arange(0, 3))
        self.e_wdim = 7
        self.e_pcw = self.create_pcWeights(self.e_wdim, 1)
        
        #inhibition constants
        self.i_xywrap = np.append(np.append(np.arange(59, 61), np.arange(0, 61)), np.arange(0, 2))
        self.i_thwrap = np.append(np.append(np.arange(34, 36), np.arange(0, 36)), np.arange(0, 2))
        self.i_wdim = 5
        self.i_pcw = self.create_pcWeights(self.i_wdim, 2)
        
        self.global_inhibition = 0.00002
        self.c_size_th = 2*np.float64(np.pi)/36
        
        #finding pose cell centre constants
        self.xy_sum_sin = np.sin(np.arange(61)*2*np.float64(np.pi)/61.0)
        self.xy_sum_cos = np.cos(np.arange(61)*2*np.float64(np.pi)/61.0)
        self.th_sum_sin = np.sin(np.arange(36)*2*np.float64(np.pi)/36.0)
        self.th_sum_cos = np.cos(np.arange(36)*2*np.float64(np.pi)/36.0)
        
        self.cells_avg = 3
        self.avg_xywrap = np.append(np.append(np.arange(58, 61), np.arange(0, 61)), np.arange(0, 3)) #same as e_xywrap
        self.avg_thwrap = np.append(np.append(np.arange(33, 36), np.arange(0, 36)), np.arange(0, 3))
        
        self.max_pc = 0
        
    def create_pcWeights(self, dim, var): #dim is dimension and var is variance
        weight = np.zeros([dim, dim, dim])
        dim_centre = math.floor(dim/2)
        
        for x in xrange(dim):
            for y in xrange(dim):
                for z in xrange(dim): 
                    weight[x,y,z] = 1.0/(var*math.sqrt(2*np.pi))*math.exp(-((x-dim_centre)**2+(y-dim_centre)**2+(z-dim_centre)**2)/(2*var**2)) 

        total = abs(sum(sum(sum(weight)))) 
        weight = weight/total
        return weight

    def activityMatrix(self, xywrap, thwrap, wdim, pcw): 
        
        #returns gaussian distribution of excitation/inhibition
        pca_new = np.zeros(self.shape)  
        indices = np.nonzero(self.posecells) 
        for index in xrange(len(indices[0])):
            (i, j, k) = (indices[0][index], indices[1][index], indices[2][index])
            pca_new[np.ix_(xywrap[i:i+wdim], xywrap[j:j+wdim],thwrap[k:k+wdim])] += self.posecells[i,j,k]*pcw
        return pca_new
    
    def get_pc_max(self, xywrap, thwrap):
        
#        self.posecells[1,2,3] = 500 @ was used to test whether the max pose cell was being found and it was; this function works
        (x,y,z) = np.unravel_index(self.posecells.argmax(), self.posecells.shape)
        
        # take the max activated cell +- AVG_CELL in 3d space
        z_posecells=np.zeros(self.shape) 
        
        zval = self.posecells[np.ix_(xywrap[x:x+7], xywrap[y:y+7], thwrap[z:z+7])]
        z_posecells[np.ix_(self.avg_xywrap[x:x+self.cells_avg*2+1], self.avg_xywrap[y:y+self.cells_avg*2+1], self.avg_thwrap[z:z+self.cells_avg*2+1])] = zval
        
        # get the sums for each axis
        x_sums = np.sum(np.sum(z_posecells, 2), 1) #gives 1d array
        y_sums = np.sum(np.sum(z_posecells, 2), 0)
        th_sums = np.sum(np.sum(z_posecells, 1), 0)
        th_sums = th_sums[:]
        
        # now find the (x, y, th) using population vector decoding to handle the wrap around 
        x = (np.arctan2(sum(self.xy_sum_sin*x_sums), sum(self.xy_sum_cos*x_sums)) *self.shape[0]/(2*np.pi)) % (self.shape[0])
        y = (np.arctan2(sum(self.xy_sum_sin*y_sums), sum(self.xy_sum_cos*y_sums)) *self.shape[0]/(2*np.pi)) % (self.shape[0])
        th = (np.arctan2(sum(self.th_sum_sin*th_sums), sum(self.th_sum_cos*th_sums)) *self.shape[2]/(2*np.pi)) % (self.shape[2])


        return (x, y, th)
    
    def update(self, ododelta, v_temp): 
        updatestart = time.time()
        
        vtrans = ododelta[0]*self.pc_vtrans_scaling 
        vrot = ododelta[1] 

        #if this visual template has been activated before, inject more energy into the pc associated with it.
        if (v_temp.first != True): 
            act_x = min([max([round(v_temp.x_pc), 1]), self.shape[0]]) #then record the activity of x as the minimum of the maximum of the rounded xpc
            act_y = min([max([round(v_temp.y_pc), 1]), self.shape[0]])
            act_th = min([max([round(v_temp.th_pc), 1]), self.shape[2]])
    
            energy = self.vt_inject * 1.0/30.0 * (30.0 - math.exp(1.2 * v_temp.activity))
            if energy > 0:
                self.posecells[act_x, act_y, act_th] += energy;

        #the milford paper was lying, and in the matlab code, the parameters for local excitation and for local inhibition are different!! (figure out what those parameters are)
        
        #excitation weighted matrix                                                            
        self.posecells = self.activityMatrix(self.e_xywrap, self.e_thwrap, self.e_wdim, self.e_pcw) 
        
        #inhibition weighted matrix
        self.posecells = self.posecells - self.activityMatrix(self.i_xywrap, self.i_thwrap, self.i_wdim, self.i_pcw) 
        
        #global inhibition
        self.posecells[self.posecells<self.global_inhibition] = 0
        self.posecells[self.posecells >= self.global_inhibition] -=self.global_inhibition

        #self.posecells[self.posecells<0] = 0
        #normalization
        total = (sum(sum(sum(self.posecells))))
        self.posecells = self.posecells/total
        
        #path integration for trans
        for dir_pc in xrange(1, self.shape[2]): #TODO: only goes through 35 iterations when it should go through 36
            direction = np.float64(dir_pc-1) * self.c_size_th 
            # N,E,S,W are straightforward
            if (direction == 0):
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + np.roll(self.posecells[:,:,dir_pc], 1,1)*vtrans
            elif direction == np.pi/2:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + np.roll(self.posecells[:,:,dir_pc], 1,0)*vtrans
            elif direction == np.pi:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + np.roll(self.posecells[:,:,dir_pc], -1,1)*vtrans
            elif direction == 3*np.pi/2:
                self.posecells[:,:,dir_pc] = self.posecells[:,:,dir_pc]*(1.0 - vtrans) + np.roll(self.posecells[:,:,dir_pc], -1,0)*vtrans
            else:
                pca90 = np.rot90(self.posecells[:,:,dir_pc], np.floor(direction *2/np.pi))
                dir90 = direction - np.floor(direction *2/np.pi) * np.pi/2
                pca_new=np.zeros([self.shape[0]+2, self.shape[0]+2])   
                pca_new[1:-1, 1:-1] = pca90 #correct.
                weight_sw = (vtrans**2) *np.cos(dir90) * np.sin(dir90)
                weight_se = vtrans*np.sin(dir90) - (vtrans**2) *np.cos(dir90) * np.sin(dir90)
                weight_nw = vtrans*np.cos(dir90) - (vtrans**2) *np.cos(dir90) * np.sin(dir90)
                weight_ne = 1.0 - weight_sw - weight_se - weight_nw
          
                pca_new = pca_new*weight_ne + np.roll(pca_new, 1, 1)*weight_nw + np.roll(pca_new, 1, 0)*weight_se + \
                            np.roll(np.roll(pca_new, 1, 1), 1, 0)*weight_sw

                pca90 = pca_new[1:-1, 1:-1]
                pca90[1:, 0] = pca90[1:, 0] + pca_new[2:-1, -1]
                pca90[1, 1:] = pca90[1, 1:] + pca_new[-1, 2:-1]
                pca90[0,0] = pca90[0,0] + pca_new[-1,-1]

                #unrotate the pose cell xy layer
                self.posecells[:,:,dir_pc] = np.rot90(pca90, 4 - np.floor(direction * 2/np.pi))

        #path integration for rot
        if vrot != 0: #vrot is the incremental change between images.
            #mod to work out the partial shift amount
            weight = (abs(vrot)/self.c_size_th)%1
            if weight == 0:
                weight = 1.0
            shift_1 = int(np.sign(vrot) * np.floor(abs(vrot)/self.c_size_th))
            shift_2 = int(np.sign(vrot) * np.ceil(abs(vrot)/self.c_size_th))
            self.posecells = np.roll(self.posecells, shift_1, 2) * (1.0 - weight) + np.roll(self.posecells, shift_2, 2) * (weight)
        self.max_pc = self.get_pc_max(self.avg_xywrap, self.avg_thwrap)

        
        
                             

