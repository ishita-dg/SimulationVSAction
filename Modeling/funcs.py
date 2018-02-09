from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

import GPy
get_ipython().magic(u'matplotlib inline')
import json
from scipy import signal
from scipy.stats import gaussian_kde

from utilities import *

#from PhysicsAPI.physics_simulation import Simulator

import bayesian_optimization
import acquisition_functions

import os
import pickle


n_disc = 100
n_approx = 50
thetas = np.linspace(0.0, 1.0, n_disc)

# np.random.seed(1)

bounds = [0, 1]
# Test-inputs
inputs = np.linspace(*bounds, num=100)[:, None]
inputs = np.hstack((inputs, np.ones_like(inputs)))
inputs_sim = inputs.copy()
inputs_sim[:, 1] = 0


def logit(p):
    return np.log(p) - np.log(1 - p)

def inv_logit(p):
    return np.exp(p) / (1 + np.exp(p))


def raster(rpath, wpath, setupfn, n_disc, n_approx):
    
    try: 
        #Temporarily storing values because long computation
        with open(wpath + 'rasters/noisy_' + setupfn + '.json', 'r') as f:
            noisy = json.load(f)
        with open(wpath + 'rasters/true_' + setupfn + '.json', 'r') as f:
            true = json.load(f)
            
    except IOError :
        
        trial_pathname = rpath + setupfn + ".json"
        sample_noise = {'kapv': 80., 'kapb': 20., 'kapm': 20000., 'perr': 10.}
        sim = Simulator(trial_pathname)
        
        
        # thetas = 2*np.pi*np.linspace(0.0, 1.0, n_disc)
        thetas = np.linspace(0.0, 1.0, n_disc)
        
        true = {'vals' : np.zeros((n_disc,1)).tolist(),
                'dists' : np.zeros((n_disc,1)).tolist(),
                'bounces' : np.zeros((n_disc,1)).tolist()
               }
        noisy = {'vals' : np.zeros((n_disc,n_approx)).tolist(),
                'dists' : np.zeros((n_disc,n_approx)).tolist(),
                'bounces' : np.zeros((n_disc,n_approx)).tolist()
               }
    
        for i, theta in enumerate(thetas):
            val, dist, bounce = sim.ground_truth_sim(2*np.pi*theta)
            true['vals'][i] = val
            true['dists'][i] = dist
            true['bounces'][i] = bounce
            print(i, theta)
            for j in xrange(n_approx):
                val, dist, bounce = sim.noisy_sim(2*np.pi*theta, sample_noise)
                noisy['vals'][i][j] = val
                noisy['dists'][i][j] = dist
                noisy['bounces'][i][j] = bounce
        
        with open(wpath + 'rasters/noisy_' + setupfn + '.json', 'w') as f:
            json.dump(noisy, f)
        with open(wpath + 'rasters/true_' + setupfn + '.json', 'w') as f:
            json.dump(true, f)
    
    
    noisy_fun = np.mean(np.array([np.array(row[:30]) for row in noisy['vals']]), axis = 1)
    true_fun = np.array([int(x) for x in true['vals']])
    
    return (noisy_fun, true_fun)


def dprocess(n_disc, sd_smooth, fun, ret_avg = True):
    
    if n_disc%2:
        Nw = n_disc
    else:
        Nw = n_disc - 1
    window = signal.gaussian(Nw, std=sd_smooth)
    window = np.array(window)/sum(window)
    
    Neach = int((Nw-1)/2)
    temp_fun = np.concatenate((fun, fun, fun))
    smooth_fun = np.zeros(n_disc)

    for i in range(n_disc):
        smooth_fun[i] = np.sum(window*temp_fun[n_disc + i - Neach: n_disc + i + Neach + 1])

    lim = 0.00000001
    fun_logit = logit(np.clip(smooth_fun, 0.0 + lim, 1.0 - lim))
    avg = np.mean(fun_logit)
    fun_logit -= avg
    
    if ret_avg:
        return fun_logit, avg
    else:
        return fun_logit


def find_nearest_arg(array, value):
    diffs = np.array([np.abs(array - v) for v in value])
    return diffs.argmin(axis = 1)
 

def getData_ESruns(Epath = None, fn = None, opt = None):
    
    
    
    if opt is not None:
        mask = np.array([x[0] < 1.0 and x[0] > 0.0 for x in opt.X_]).astype(bool)
        Nss = sum([x[1] == 0 for x in opt.X_[mask]])
        Nes = sum([x[1] == 1 for x in opt.X_[mask]])
        mean, var = opt.model.predict_noiseless(inputs)
        final_x = inputs[np.argmax(mean), 0]
        conf_in_final = opt.best_value()
        
        return (Nss, Nes, final_x, conf_in_final)

        
    else: 
        
        Nss = []
        Nes = []
        final_x = []
        conf_in_final = []
        
        lfn = len(fn)
        opt_files = sorted([f for f in os.listdir(Epath) if f[:lfn] == fn and f[lfn:lfn+3] == 'opt'])
        
        for of in opt_files:
            
            with open(Epath + of) as infile:
                opt = pickle.load(infile)
            
            mask = np.array([x[0] < 1.0 and x[0] > 0.0 for x in opt.X_]).astype(bool)
            Nss.append(sum([x[1] == 0 for x in opt.X_[mask]]))
            Nes.append(sum([x[1] == 1 for x in opt.X_[mask]]))
            mean, var = opt.model.predict_noiseless(inputs)
            final_x.append(inputs[np.argmax(mean), 0])

            conf_in_final.append(opt.best_value())
            
        
        return (np.array(Nss), np.array(Nes),
                np.array(final_x), np.array(conf_in_final))


def startXY(tm):
    least_info = thetas[np.argmin(np.abs(tm.sim_logit - 0.0))] 
    X = np.array([[least_info, 1], [least_info + 1.0, 0], [least_info - 1.0, 0]])
    Y = tm.fun(tm.limX(X), noise=False)
    
    return X, Y
    
class tradeoff_model():
    
    def __init__(self, sim_logit, true_logit, sd_smooth, noise_exp, noise_err):
        self.sim_logit = sim_logit
        self.true_logit = true_logit
        self.error_logit = sim_logit - true_logit
        self.sd_smooth = sd_smooth
        self.kernel1 = GPy.kern.RBF(input_dim=1, active_dims=[0], lengthscale=sd_smooth*(1.0/n_disc), variance=np.std(sim_logit)**2, name='sim')
        self.kernel2 = GPy.kern.RBF(input_dim=1, active_dims=[0], lengthscale=sd_smooth*(1.0/n_disc), variance=np.std(self.error_logit)**2, name='error')
        self.delta = GPy.kern.DomainKernel(input_dim=1, start=0.5, stop=1.5, active_dims=[1], name='delta')
        self.kernel = self.kernel1.copy() + self.delta.copy() * self.kernel2.copy()
        self.noise_exp = noise_exp 
        self.noise_err = noise_err 
        
    # Define a joint function over the extended parameter space (a, delta)
    def fun(self, X, noise=True, bins=thetas):
        """Return either an experiment on the simulator or the real system.
        
        Parameters
        ----------
        X: 2d array
            The data, last column is an indicator for each experiment
            (1 = real system, 0 = simulation)
        noise: bool
            Optional parameter that indicates whether to return noisy evaluations
        """
        Y = np.zeros((X.shape[0], 1), dtype=np.float)
        exp_id = X[:, 1].astype(np.bool)
        if np.any(exp_id):
            # if is experiment
            inds = find_nearest_arg(bins, X[exp_id, 0])
            Y[exp_id] = self.sim_logit[inds, None] - self.error_logit[inds, None]         + noise * (np.random.normal(0,np.sqrt(self.noise_exp)))
    
        if not np.all(exp_id):
            # if is simulation
            inds = find_nearest_arg(bins, X[~exp_id, 0])
            Y[~exp_id] = self.sim_logit[inds, None] +         + noise * (np.random.normal(0,np.sqrt(self.noise_exp)) + np.random.normal(0,np.sqrt(self.noise_err)))
            
        return Y

    def get_het_noise(self,X):
        return self.noise_exp * X[:, [1]] + self.noise_err * np.logical_not(X[:, [1]])
    
    def demirror (self,x):
        x += 1.0
        return ((x*10)%10)/10.0
    
    def limX(self,mat):
        return np.array([[self.demirror(x), y] for x,y in mat])



def runES(tm, factor, entropy_thresh, p_diff_thresh, p_thresh, avg, m, af, opt, dyna = False, verbose = False, pverbose = True):
    
    expt = True
    count = 0
    up_c = 0.0
    n_e = 0
    n_s = 0
    latest_e = 0
    latest_s = 0
    # initialise 
    t_entropy_thresh = 1000
    # disable t_entropy_thresh stopping criteria
    # to make analogous to dyna
    #entropy_thresh = 0
     
    # Probability difference threshold
    p_diff_thresh = 0.0000001
    # Initialise best
    best_so_far = 0.0
    
    
    boundaries = np.zeros((1,2))
    boundaries[0,:] = np.array([0.0, 1.0])    
    
    while (True):
        count += 1
        new_x0_e, entropy_e = opt.select_query_point(boundaries, thetas, expt = expt)
        new_x0_s, entropy_s = opt.select_query_point(boundaries, thetas, expt = not expt)
        e_fact = entropy_e/entropy_s
        # Decision if not dyna
        if not dyna:
            
            #if entropy_e == -1 :
            if False:
                new_x = np.insert(new_x0_e, 1, 0)
                if verbose: print("Random")
                
            elif e_fact > factor:
                new_x = np.insert(new_x0_e, 1, 1)
                if verbose: print("Experiment")
                up_c += 1.0
                n_e += 1
                t_entropy_thresh = np.abs((entropy_e - latest_e))/entropy_e
                latest_e = entropy_e
                
            elif e_fact < factor:
                new_x = np.insert(new_x0_e, 1, 0)
                if verbose: print("Simulation")
                up_c -= 1.0
                n_s += 1
                t_entropy_thresh = np.abs((entropy_s - latest_s))/entropy_s
                latest_s = entropy_s
                
            
        # Decision if dyna
        if dyna:
            if np.floor((n_s / (factor/1.3)**2)) > n_e:
                new_x = np.insert(new_x0_e, 1, 1)
                if verbose: print("Experiment")
                up_c += 1.0
                n_e += 1
                t_entropy_thresh = np.abs((entropy_e - latest_e))/entropy_e
                latest_e = entropy_e
                
            else:
                new_x = np.insert(new_x0_e, 1, 0)
                if verbose: print("Simulation")
                up_c -= 1.0
                n_s += 1
                t_entropy_thresh = np.abs((entropy_s - latest_s))/entropy_s
                latest_s = entropy_s
                
                

        # Add sampled point
        
        new_x = np.array([new_x, [new_x[0] + 1.0, new_x[1]], [new_x[0] - 1.0, new_x[1]]])
        y = tm.fun(tm.limX(new_x))
        opt.update(new_x, y)
        opt.model['.*het_Gauss.variance'] = tm.get_het_noise(opt.model.X)
        af.model = opt.model
        
        
        # Check if to stop
        
        mean, var = opt.model.predict_noiseless(inputs)
        n_best_so_far = max(inv_logit(tm.fun(inputs, noise=False)[np.argmax(mean)] + avg), best_so_far)
        
        if n_best_so_far > p_thresh: 
            if verbose: print("Prob of success thresh reached ", n_best_so_far, 360*inputs[np.argmax(mean), 0])
            break
        if count > 5 and n_best_so_far - best_so_far < p_diff_thresh: 
            if verbose: print("Diff in prob of succes thresh reached ")
            break
        if t_entropy_thresh > 0 and t_entropy_thresh < entropy_thresh :
            if verbose: print("Diff in entropy thresh reached ", t_entropy_thresh)
            break
        if count == 20:
            if verbose: print("Limit of total runs reached")
            break
        
        best_so_far = n_best_so_far
                
        
        
    
    if verbose: print("/n ********** /n")
    if pverbose:
        print("Net number of runs = ", count)
        print("Net number of simulations = ", count - n_e)
        print("Net number of experiments = ", n_e)
    
    #mean, var = opt.model.predict_noiseless(inputs)
    #ans = inputs[np.argmax(mean), 0]
    #tans = inputs[np.argmax(tm.fun(inputs, noise=False)), 0]
    #yans = tm.fun(inputs, noise=False)[np.argmax(mean)]
    #ytans = np.max(tm.fun(inputs, noise=False))
    
    return opt #, count, n_e, ans, yans, tans, ytans

## In[162]:

## Plotting functions not fully functional/not sure if correct

def plot(tm, opt, avg_s, avg_t, ax, rad = False, prior=False):
    """Plot the functions
    
    Parameters
    ----------
    prior: bool
        If true, plot the function prior (this needs to be seperate, since the GPy library
        does not allow gp models without data :/)
    """
    if prior:
        mean = np.zeros_like(inputs[:, 0])
        var = opt.model.kern.Kdiag(inputs)
        
        var_cond = tm.kernel1.Kdiag(inputs)
    else:
        mean, var = opt.model.predict_noiseless(inputs)
        mean_sim, var_sim = opt.model.predict_noiseless(inputs_sim)
        mean_sim = mean_sim.squeeze()
        var_sim = var_sim.squeeze()
        std_sim = np.sqrt(var_sim)
        x_tmp = opt.X_.copy()
        y_tmp = opt.y_.copy()
        
    mean = mean.squeeze()
    var = var.squeeze()
    std = np.sqrt(var)
    

    if not rad:
        # Plotting...
        ax.plot(inputs[:, [0]], tm.fun(inputs, noise=False), 'tab:orange', label = "expt")
        ax.plot(inputs_sim[:, [0]], tm.fun(inputs_sim, noise=False), 'tab:blue', label = "sim")
        
        ax.plot(inputs[:, 0], mean, color='k', linewidth = 2, label = "pred")
        ax.fill_between(inputs[:, 0],
                         mean - std,
                         mean + std,
                         color='k', alpha=0.1, zorder=-10)
        
        
        exp_id = opt.X_[:, 1].astype(np.bool)
    
        
        if not prior:
            expt_true = np.array([x[1] == 1 for x in opt.X_]) 
            sims = np.array([x for x in opt.X_ if x[1] == 0])
            expts = np.array([x for x in opt.X_ if x[1] == 1])
            if sims.shape[0]: ax.scatter(sims[:,0], opt.y_[np.logical_not(expt_true)],
                                         facecolors = 'tab:blue', edgecolors = 'k')
            if expts.shape[0]: ax.scatter(expts[:,0], opt.y_[expt_true], 
                                          facecolors = 'tab:orange', edgecolors = 'k')
    
    
        
        # Some labelling
    #     plt.xlim(-1, 2)
        ax.set_xlim(0,1)
        ax.set_ylim(-8.5,4.5)
        ax.set_xlabel(r'Inputs $\mathbf{x}$')
        ax.set_ylabel(r'Performance $J(\mathbf{x}$)')
        #ax.legend()
        
    if rad:
        # Plotting...
        ax.set_theta_direction(-1)
        
        ax.plot(2*np.pi*inputs[:, [0]], inv_logit(avg_t + tm.fun(inputs, noise=False)), 
                'tab:orange', label = "expt", zorder = 3)
        ax.plot(2*np.pi*inputs_sim[:, [0]], inv_logit(avg_s + tm.fun(inputs_sim, noise=False)), 
                'tab:blue', label = "sim", zorder = 2)
        ax.plot(2*np.pi*inputs[:, 0], inv_logit(min(avg_s, avg_t) + mean), color='k', linewidth = 1.5, label = "pred", zorder = 1)
        #ax.fill_between(2*np.pi*inputs[:, 0],
                         #inv_logit(mean - std),
                         #inv_logit(mean - std),
                         #color='tab:purple', alpha=0.2, zorder=-10)
        
        
        exp_id = opt.X_[:, 1].astype(np.bool)
        
        ylim = np.clip(1.1*max(inv_logit(avg_t + tm.fun(inputs, noise=False))), 0.0, 1.0)
    
        print 
        if not prior:
            mask = np.array([x[0] < 1.0 and x[0] > 0.0 for x in opt.X_]).astype(bool)
            expt_true = np.array([x[1] == 1 for x in opt.X_]).astype(bool)
            sims = np.array([x for x in opt.X_[mask] if x[1] == 0])
            expts = np.array([x for x in opt.X_[mask] if x[1] == 1])
            
            if sims.shape[0]: 
                ax.scatter(2*np.pi*sims[:,0], 
                           ylim*np.ones_like(sims[:,0]), s = 40,
                           facecolors = 'tab:blue', zorder = 4)#, edgecolors = 'k')
                x = np.repeat(2*np.pi*sims[:,0], 2)
                y = np.vstack((ylim*np.ones_like(sims[:,0]), np.zeros_like(sims[:,0]))).reshape((-1,),order='F')
                ax.plot(x, y, 'tab:blue', alpha = 0.2, zorder = 1)
            
            
            if expts.shape[0]: 
                ax.scatter(2*np.pi*expts[:,0], 
                           ylim*np.ones_like(expts[:,0]), s = 40,
                           facecolors = 'tab:orange', zorder = 5)#, edgecolors = 'k')
                x = np.repeat(2*np.pi*expts[:,0], 2)
                y = np.vstack((ylim*np.ones_like(expts[:,0]), np.zeros_like(expts[:,0]))).reshape((-1,),order='F')
                ax.plot(x, y, 'tab:orange', alpha = 0.2, zorder = 1)
                
            
              #if sims.shape[0]: ax.scatter(2*np.pi*sims[:,0], 
                                          #inv_logit(avg_s + opt.y_[np.logical_and(mask,np.logical_not(expt_true))]), s = 40,
                                          #facecolors = 'tab:blue', zorder = 4)#, edgecolors = 'k')
            #if expts.shape[0]: ax.scatter(2*np.pi*expts[:,0], 
                                           #inv_logit(avg_t + opt.y_[np.logical_and(expt_true, mask)]), s = 40,
                                           #facecolors = 'tab:orange', zorder = 5)#, edgecolors = 'k')
    
    
        
        # Some labelling
    #     plt.xlim(-1, 2)
    
        ax.tick_params(axis='x', which='major', labelsize=15)
            
        ticks = np.round(100*np.array([0.25, 0.50, 0.75, 1.0])*ylim)/100.0
        ax.set_rticks(ticks)
        
        ax.set_ylim([0, 1.2 *ylim])
        ax.set_yticklabels([]) 
        #ax.set_xlabel(r'Inputs $\mathbf{x}$')
        #ax.set_ylabel(r'Performance $J(\mathbf{x}$)')
        #ax.legend()
        
        return ylim




#def plot_shots(Epath, fn, ax, ylim, rad = True):


def kde_scipy(x, x_grid, bandwidth=0.2, **kwargs):
    """Kernel Density Estimation with Scipy"""
    # Note that scipy weights its bandwidth by the covariance of the
    # input data.  To make the results comparable to the other methods,
    # we divide the bandwidth by the sample standard deviation here.
    kde = gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1), **kwargs)
    return kde.evaluate(x_grid)


def plot_shots(ax, pos_p, pos_h, legend = False):
    
    ax.set_theta_direction(-1)
    pos_h = np.array(pos_h)
    
    ylim = 1
    #pos = np.array(pos)
    noise = np.clip(np.random.normal(0, 0.05, len(pos_p)), -0.05, 0.05)
    #ax.scatter(2*np.pi*pos_p, 0.5*np.ones_like(pos_p) + noise, s = 40, 
    #           marker = 'o',facecolors = 'k', zorder = 5,
    #           label = "Model Shots")
    pdf = kde_scipy(pos_p, inputs[:,0], bandwidth=0.05)
    pdf /= np.max(pdf)
    #ax.hist(2*np.pi*pos, bins = 40)
    ax.fill(2*np.pi*inputs[:,0], pdf, ec='gray', fc='gray', alpha=0.4)
    
    for i, val in enumerate(pos_h):
        if val < 0:
            pos_h[i] += 2*np.pi
            
    pos_h /= 2*np.pi
    noise = np.clip(np.random.normal(0, 0.05, len(pos_h)), -0.05, 0.05)
    ax.scatter(2*np.pi*pos_h, 0.6*np.ones_like(pos_h) + noise, s = 40, 
               marker = 'o',facecolors = 'tab:purple', zorder = 5, 
               label = "Human data")
    pdf = kde_scipy(pos_h, inputs[:,0], bandwidth=0.05)
    pdf /= np.max(pdf)
    
    #ax.hist(2*np.pi*pos, bins = 40)
    ax.fill(2*np.pi*inputs[:,0], pdf, ec='tab:purple', fc='tab:purple', alpha=0.4)
    
    ax.tick_params(axis='x', which='major', labelsize=15)
    ax.set_ylim([0, 1.1*ylim])
    ax.set_yticklabels([])
    
    if legend: ax.legend(fontsize = 15)
    #x = np.repeat(2*np.pi*pos, 2)
    #y = np.vstack((ylim*1.1*np.ones_like(pos), np.zeros_like(pos))).reshape((-1,),order='F')

