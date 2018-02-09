"""

Used to visualize a trial (as a quick check)

"""

from __future__ import division, print_function
from phystables import *
import sys
import os
import pygame as pg
from pygame.constants import *

if __name__ == "__main__":
    assert len(sys.argv) > 1, "Need a trial to load"
    trnm = sys.argv[1]
    trpth = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         trnm)
    tr = load_trial(trpth)
    pg.init()
    s = pg.display.set_mode((1000, 600))
    tb = tr.make_table()
    tb.draw()
    pg.display.flip()
    running = True
    
    try:
        wpath = sys.argv[2]
        k = sys.argv[1].rfind('/')
        pg.image.save(s, wpath + 'screenshots/' + sys.argv[1][k+1:-4]+"jpeg")
    except IndexError:
        while running:
            for e in pg.event.get():
                if e.type == QUIT:
                    running = False
                elif e.type == KEYDOWN:
                    running = False
