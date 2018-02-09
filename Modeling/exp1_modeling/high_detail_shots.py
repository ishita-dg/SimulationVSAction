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
N_CUTS = 1000

"""File paths"""
thispth = os.path.dirname(os.path.realpath(__file__))
trial_dir = os.path.join(thispth, "..", "exp1_trials")
oflnm_full = os.path.join(thispth, "high_detail_tables_full.csv")

if __name__ == "__main__":
    with open(oflnm_full, 'w') as ofl_full:
        ofl_full.write("TrialName,Angle,TruthIn\n")
        for trnm in glob.glob(os.path.join(trial_dir, "*.json")):
            if os.path.basename(trnm) != "TrList.json":
                sim = Simulator(trnm)
                nm = sim._trial.name
                angs = [np.pi * 2. * i for i in np.linspace(0., 1., N_CUTS)]
                gts = []
                for a in angs:
                    this_gt = sim.ground_truth_sim(a)[0] * 1
                    ofl_full.write(nm + ',' + str(a) + ',' + str(this_gt) + '\n')
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
