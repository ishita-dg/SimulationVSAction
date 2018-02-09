"""Trial class to hold Simulation/Action trials

This module specifies a trial type that can be used to check the trial used
in Simulation/Action experiments for consistency and to extract information
about possible action outcomes

Example:

    tr = SimActTrial('test', dims=(1000, 600))
    tr.add_ball((300, 300), (0, 1))
    tr.add_goal((990, 0), (1000, 300), GREENGOAL)
    tr.add_goal((990, 300), (1000, 600), REDGOAL)
    tr.check_consistency()
    tr.save('test.json','.')
    tr2 = load_trial('test.json', SimActTrial)
    tr2.make_table()

"""

from __future__ import division, print_function
from phystables import *
from phystables.constants import *
import warnings
import numpy as np
import json

__all__ = ['SimActTrial', 'DEF_NOISE_DICT']

DEF_NOISE_DICT = {
    'kapv': 80,
    'kapb': 30,
    'kapm': 20000,
    'perr': 10
}

class SimActTrial(SimpleTrial):
    """Class to instantiate Simulation/Action trials"""

    def __init__(self, name, dims=(1000, 600), ball_radius=20, **kwdargs):
        """Initialize the SimActTrial

        Args:
            name (str): The name of the trial
            dims ([int,int]): The dimensions of the trial (default (1000,600))
            ball_radius: Radius of the ball in px (default is 20)
        """
        super(SimActTrial, self).__init__(name, dims=dims,
                                          def_ball_rad=ball_radius, **kwdargs)

    def check_consistency(self, check_greenhit=True, max_time=5.,
                          num_angles=100):
        """Ensures this is a legal table

        Checks for no overlaps and a reachable green goal

        Args:
            check_greenhit (bool): whether to test whether green is reachable
            max_time (float): number of seconds to simulate for reach check
            num_angles (int): precision of shots to test for green goal

        Returns:
            bool indicating whether this is a legal trial
        """
        good = super(SimActTrial, self).check_consistency(50000, True)
        if len(self.goals) == 0:
            warnings.warn("Must have at least one green goal")
            good = False
        elif not any(g[2] == GREENGOAL for g in self.goals):
            warnings.warn("Must have at least one green goal")
            good = False
        if check_greenhit:
            outcomes = self.get_successes(max_time, num_angles)
            hits = any([o[1] for o in outcomes])
            if not hits:
                warnings.warn("No way for the ball to hit the green goal")
                good = False
        return good

    def _replace_ball_vel(self, new_v):
        """Private function to switch in new ball velocity easily"""
        b = self.ball
        newb = (b[0], new_v, b[2], b[3], b[4])
        self.ball = newb

    def get_successes(self, max_time=5., num_angles=100):
        """Returns the proportion of uniform shots that reach green

        Args:
            max_time (float): number of seconds to simulate for reach check
            num_angles (int): precision of shots to test for green goal

        Returns:
            A list of angles and bools for each angle indicating whether that
            shot hit the green goal
        """
        orig_vel = self.ball[1]
        angs = [2*np.pi * (i/num_angles) for i in range(num_angles)]
        outcomes = []
        for a in angs:
            self._replace_ball_vel((np.cos(a), np.sin(a)))
            self.normalize_vel()
            tb = self.make_table()
            r = tb.simulate(max_time)
            outcomes.append((a, r == GREENGOAL))
        self._replace_ball_vel(orig_vel)
        return outcomes

    def get_simulation_outcomes(self, max_time=5., num_angles=100,
                                num_sims=100, noise_dict=DEF_NOISE_DICT):
        """Provides the simulated probability of green from uniform shots

        Runs noisy simulations across a variety of shot angles and provides the
        proportion that return GREENGOAL

        Args:
            max_time (float): number of seconds to simulate for reach check
            num_angles (int): precision of shots to test for green goal
            num_sims (int): number of simulations per shot
            noise_dict (dict): dictionary containing noise parameters

        Returns:
            A list of angles and proportions of simulations hitting GREENGOAL
            for each shot
        """
        def _get_noisy_outcome(tb):
            ntb = make_noisy(tb, **noise_dict)
            ntb.basicts = 0.01 # Set to speed simulation
            return (ntb.simulate(max_time, timeres=0.01) == GREENGOAL)

        orig_vel = self.ball[1]
        angs = [2*np.pi * (i/num_angles) for i in range(num_angles)]
        outcomes = []
        for a in angs:
            self._replace_ball_vel((np.cos(a), np.sin(a)))
            self.normalize_vel()
            tb = self.make_table()
            sims = [_get_noisy_outcome(tb) for i in range(num_sims)]
            outcomes.append((a,np.mean(sims)))
        self._replace_ball_vel(orig_vel)
        return outcomes

    def record_outcomes(self, flnm=None, max_time=5., num_angles=100,
                        num_sims=100, noise_dict=DEF_NOISE_DICT):
        """Saves the shot and simulation outcomes for a series of angles

        Records get_successes and get_simulation_outcomes to a JSON file. NOTE:
        may take a while to run for any reasonable number of num_angles and
        num_sims

        Args:
            flnm (str): filename to write to
            max_time (float): number of seconds to simulate for reach check
            num_angles (int): precision of shots to test for green goal
            num_sims (int): number of simulations per shot
            noise_dict (dict): dictionary containing noise parameters

        Returns:
            A dict with (success, sim_outcomes) for each angle key (also
            written to JSON file)
        """
        shot_out = self.get_successes(max_time, num_angles)
        shot_dict = dict(shot_out)
        sim_out = self.get_simulation_outcomes(max_time, num_angles,
                                               num_sims, noise_dict)
        sim_dict = dict(sim_out)
        comb_dict = {}
        for a, shot in shot_dict.items():
            sim = sim_dict[a]
            comb_dict[a] = (shot, sim)
        if flnm is not None:
            with open(flnm, 'w') as ofl:
                json.dump(comb_dict, ofl)
        return comb_dict


if __name__ == '__main__':
    tr = SimActTrial('test', dims=(1000, 600))
    tr.add_ball((300, 300), (0, 1))
    tr.add_goal((990, 0), (1000, 300), GREENGOAL)
    tr.add_goal((990, 300), (1000, 600), REDGOAL)
    print (tr.check_consistency())
    #tr.save('test.json','.')
    #tr2 = load_trial('test.json', SimActTrial)
    #print(tr2.record_outcomes())
