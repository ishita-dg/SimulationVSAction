"""API for easy running physics simulations

This module mainly includes the `Simulator` class that allows for easy running
of physics simulations

You can load in a JSON-style physicsTable trial as a Simulator object and run
either ground-truth deterministic or noisy simulation

Example:

    from physics_simulation import Simulator
    import numpy as np
    trial_pathname = "sample_trial.json"
    sample_noise = {'kapv': 80., 'kapb': 20., 'kapm': 20000., 'perr': 10.}
    sim = Simulator(trial_pathname)
    print sim.ground_truth_sim(-np.pi / 4.)
    print sim.noisy_sim(-np.pi / 4., sample_noise)

"""

from phystables import load_trial, make_noisy, SimpleTable
from phystables.constants import REDGOAL, GREENGOAL, TIMEUP
import numpy as np
import json
import os

__all__ = ['Simulator']

def _set_ball_direction(table, angle, px_per_s=None):
    b = table.balls
    if px_per_s is None:
        v_vect = b.getvel()
        px_per_s = np.linalg.norm(v_vect)
    new_vel = [px_per_s * np.cos(angle), px_per_s * np.sin(angle)]
    b.setvel(new_vel)


class Simulator(object):
    """Wrapper object to simulate physicsTable trials by shot angle

    This class loads in a JSON-style physicsTable trial by file path and allows
    for simple simulation (either noisy or deterministic)
    """

    def __init__(self, trial_path, travel_time=5., px_per_s=600):
        """Initializer for a Simulator object

        Args:
            trial_path (str): File path to the JSON-style physicsTable trial
            travel_time (float): Maximum simulation time until TIMEUP failure
            px_per_s (float): The pixel / second velocity of ball shots
        """
        self._trial_json = trial_path
        self._trial = load_trial(self._trial_json)
        self._pps = px_per_s
        self._ttime = travel_time

    def _sim_filter(self, table):
        assert isinstance(table, SimpleTable)
        end_type, bounces = table.simulate(self._ttime, return_bounces=True)
        assert end_type in [GREENGOAL, REDGOAL, TIMEUP], "Table returned an illegal end type: " + str(end_type)
        success = end_type == GREENGOAL
        px_traveled = table.tm * self._pps
        return success, px_traveled, max(bounces)

    # Exposes a copy of the table to the world
    def _expose_table(self):
        """SimpleTable: A copy of the table created from the JSON file
        """
        tb = self._trial.make_table()
        tb.set_timestep(0.01)
        return tb

    table = property(_expose_table)

    def ground_truth_sim(self, angle):
        """Returns the outcome of the ball shot according to ground truth

        Args:
            angle (float): Angle in radians to shoot the ball

        Returns:
            A list of 3 items, including:
            1) Whether the shot hit the green goal
            2) The pixel distance traveled for the shot
            3) The number of bounces the ball took for that shot
        """
        tab = self.table
        _set_ball_direction(tab, angle, self._pps)
        return self._sim_filter(tab)

    def noisy_sim(self, angle, noise_dict):
        """Returns the outcome of the ball shot based on noisy dynamics

        Args:
            angle (float): Angle in radians to shoot the ball
            noise_dict (dict): A dict containing the keys of kapv, kapb, kapm, and perr

        Returns:
            A list of 3 items, including:
            1) Whether the shot hit the green goal
            2) The pixel distance traveled for the shot
            3) The number of bounces the ball took for that shot
        """
        tab = self.table
        _set_ball_direction(tab, angle, self._pps)
        ntab = make_noisy(tab, **noise_dict)
        return self._sim_filter(ntab)
