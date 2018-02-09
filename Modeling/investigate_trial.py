"""

Used to report the proportion of random shots that will
 (a) go in the goal
 (b) be simulated into the goal

"""

from __future__ import division, print_function
from PhysicsAPI import Simulator
import sys
import os
import numpy as np

"""The number of cuts of a circle to shoot the ball at"""
N_CUTS = 100

"""The number of simulations to run for each shot angle"""
N_SIMS = 100

"""Noise parameters (approx from Smith & Vul 2013)"""
sample_noise = {'kapv': 80., 'kapb': 20.,
                'kapm': 20000., 'perr': 10.}


if __name__ == "__main__":
    assert len(sys.argv) > 1, "Need a trial to load"
    trnm = sys.argv[1]
    trpth = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         trnm)
    sim = Simulator(trpth)
    #angs = [np.pi * 2. * i / N_CUTS for i in range(N_CUTS)]
    angs = [np.pi * 2. * i for i in np.linspace(0., 1., N_CUTS)]
    gr_trs = [sim.ground_truth_sim(a)[0] for a in angs]
    print("Proportion of ground truth in:", np.mean(gr_trs))

    #sim_trs = []
    #for a in angs:
    #    sim_trs.append(np.mean([sim.noisy_sim(a, sample_noise)[0]
    #                            for _ in range(N_SIMS)]))

    #print("Proportion of simulations in:", np.mean(sim_trs))
