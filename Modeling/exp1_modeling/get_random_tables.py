"""

Used to report the proportion of random shots that will
 (a) go in the goal
 (b) be simulated into the goal

"""

from __future__ import division, print_function
import sys
sys.path.append('..') # For the simulator
from PhysicsAPI import Simulator
import os
import numpy as np
import glob

"""The number of cuts of a circle to shoot the ball at"""
N_CUTS = 100

"""The number of simulations to run for each shot angle"""
N_SIMS = 100

"""Noise parameters (approx from Smith & Vul 2013)"""
sample_noise = {'kapv': 80., 'kapb': 20.,
                'kapm': 20000., 'perr': 10.}

"""File paths"""
thispth = os.path.dirname(os.path.realpath(__file__))
trial_dir = os.path.join(thispth, "..", "exp1_trials")
oflnm_full = os.path.join(thispth, "random_shot_tables_full.csv")
oflnm_comb = os.path.join(thispth, "random_shot_tables.csv")

if __name__ == "__main__":
    with open(oflnm_full, 'w') as ofl_full, open(oflnm_comb, 'w') as ofl_comb:
        ofl_full.write("TrialName,Angle,TruthIn,SimIn\n")
        ofl_comb.write("TrialName,TruthIn,SimIn\n")
        for trnm in glob.glob(os.path.join(trial_dir, "*.json")):
            if os.path.basename(trnm) != "TrList.json":
                sim = Simulator(trnm)
                nm = sim._trial.name
                angs = [np.pi * 2. * i for i in np.linspace(0., 1., N_CUTS)]
                gts = []
                simin = []
                for a in angs:
                    this_gt = sim.ground_truth_sim(a)[0] * 1
                    this_sim = [sim.noisy_sim(a, sample_noise)[0] for _ in range(N_SIMS)]
                    avg_sim = np.mean(this_sim)
                    ofl_full.write(nm + ',' + str(a) + ',' + str(this_gt) +
                                   ',' + str(avg_sim) + '\n')
                    gts.append(this_gt)
                    simin.append(avg_sim)
                ofl_comb.write(nm + ',' + str(np.mean(gts)) + ',' +
                               str(np.mean(simin)) + '\n')
                print("Done with " + nm)



    """
    assert len(sys.argv) > 1, "Need a trial to load"
    trnm = sys.argv[1]
    trpth = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         trnm)
    sim = Simulator(trpth)
    #angs = [np.pi * 2. * i / N_CUTS for i in range(N_CUTS)]
    angs = [np.pi * 2. * i for i in np.linspace(0., 1., N_CUTS)]
    gr_trs = [sim.ground_truth_sim(a)[0] for a in angs]
    print("Proportion of ground truth in:", np.mean(gr_trs))
"""
