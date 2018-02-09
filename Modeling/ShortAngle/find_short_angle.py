"""
Translates these game tables into things that can be used by RRT path planning
and finds the angle the shortest path leaves at
"""

from phystables import *
from phystables.constants import *
import rrt
import pygame as pg
import os
import numpy as np
import glob

def get_path(trial, steps=2000):
    space = rrt.interface.load_phystable_trial(trial, [GREENGOAL])
    planner = rrt.RRTstar(space, tr.ball[0], 50, 50)
    for _ in xrange(steps):
        planner.step()
    dist, path = planner.get_shortest_path()
    return path

def show_path(trial, path):
    pg.init()
    d = pg.display.set_mode(trial.dims)
    tb = tr.make_table()
    tb.draw()
    drpth = [rrt.viz.intify(p) for p in path]
    pg.draw.lines(d, pg.Color('blue'), False, path, 2)
    pg.display.flip()
    rrt.viz.pause_pg()

def get_angle(path, distbreaks):
    distbreaks.sort()
    distbreaks = np.array(distbreaks)
    ospot = path[0]
    norms = []
    checks = 0
    for p in path[1:]:
        diff = p - ospot
        dist = np.linalg.norm(diff)
        placement = sum(distbreaks < dist)
        if placement > checks:
            checks = placement
            norms.append(diff / dist)
    avg_x = np.mean([d[0] for d in norms])
    avg_y = np.mean([d[1] for d in norms])
    print norms
    return np.arctan2(avg_y, avg_x)



if __name__ == '__main__':
    flpth = os.path.join(os.path.dirname(__file__),
                       '..', 'exp1_trials', '*.json')
    newpth = os.path.join(os.path.dirname(__file__), 'initial_angles.csv')
    with open(newpth, 'w') as ofl:
        ofl.write('TrialName,Angle\n')
        for f in glob.glob(flpth):
            if os.path.basename(f)[0] in ['e', 'm', 'h']:
                tr = load_trial(f)
                nm = tr.name
                dbreaks = [tr.ball[2] * b for b in [1,2,3]]
                path = get_path(tr, 5000)
                ang = get_angle(path, dbreaks)
                ofl.write(nm + ',' + str(ang) + '\n')
                print('Done with ' + nm)
