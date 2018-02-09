from simacttrial import SimActTrial
from phystables.constants import REDGOAL, GREENGOAL, RED, GREEN
import os
import json

fldr = "exp1"

if __name__ == '__main__':

    """ Make the easiest trials (p(guess) > 30%) """

    # Straight shot -- 50% green, 50% red
    easy_1 = SimActTrial('easy_1', dims=(1000, 600))
    easy_1.add_ball((300, 300), (0, 1))
    easy_1.add_goal((990, 0), (1000, 300), GREENGOAL, GREEN)
    easy_1.add_goal((990, 300), (1000, 600), REDGOAL, RED)

    # Trivially easy -- you have to try to get it wrong
    easy_2 = SimActTrial('easy_2', dims=(1000, 600))
    easy_2.add_goal((0, 0), (900, 10), GREENGOAL, GREEN)
    easy_2.add_goal((900, 0), (1000, 10), REDGOAL, RED)
    easy_2.add_wall((900, 200), (1000, 600))
    easy_2.add_ball((500, 300), (0, 1))

    # Requires some bounces but hard to lose
    easy_3 = SimActTrial('easy_3', dims=(1000, 600))
    easy_3.add_goal((0, 590), (400, 600), REDGOAL, RED)
    easy_3.add_goal((400, 590), (1000, 600), GREENGOAL, GREEN)
    easy_3.add_wall((0, 300), (500, 350))
    easy_3.add_wall((450, 150), (500, 300))
    easy_3.add_ball((200, 200), (0, 1))

    # You know where to go
    easy_4 = SimActTrial('easy_4', dims=(1000, 600))
    easy_4.add_goal((0, 0), (1000, 10), GREENGOAL, GREEN)
    easy_4.add_goal((0, 10), (10, 600), REDGOAL, RED)
    easy_4.add_goal((990, 10), (1000, 600), REDGOAL, RED)
    easy_4.add_ball((200, 550), (0, 1))

    # Ice cream sandwich
    easy_5 = SimActTrial('easy_5', dims=(1000, 600))
    easy_5.add_goal((0, 0), (10, 600), REDGOAL, RED)
    easy_5.add_goal((990, 0), (1000, 600), GREENGOAL, GREEN)
    easy_5.add_wall((350, 100), (400, 500))
    easy_5.add_wall((600, 100), (650, 500))
    easy_5.add_ball((500, 300), (0, 1))

    # Don't screw it up
    easy_6 = SimActTrial('easy_6', dims=(1000, 600))
    easy_6.add_goal((0, 0), (1000, 10), REDGOAL, RED)
    easy_6.add_goal((0, 10), (10, 300), REDGOAL, RED)
    easy_6.add_goal((990, 10), (1000, 300), REDGOAL, RED)
    easy_6.add_goal((0, 300), (10, 590), GREENGOAL, GREEN)
    easy_6.add_goal((990, 300), (1000, 590), GREENGOAL, GREEN)
    easy_6.add_goal((0, 590), (1000, 600), GREENGOAL, GREEN)
    easy_6.add_ball((100, 500), (0, 1))

    """ Make the moderate trials (p(guess) between 10% and 30%) """

    moderate_1 = SimActTrial('moderate_1', dims=(1000, 600))
    moderate_1.add_goal((0,590), (500,600), GREENGOAL, GREEN)
    moderate_1.add_goal((500,590), (1000,600), REDGOAL, RED)
    moderate_1.add_wall((0,450), (400, 500))
    moderate_1.add_wall((600, 450), (1000, 500))
    moderate_1.add_ball((700, 100), (0, 1))

    moderate_2 = SimActTrial('moderate_2', dims=(1000, 600))
    moderate_2.add_ball((200,500), (0, 1))
    moderate_2.add_wall((0,300), (600,400))
    moderate_2.add_goal((0,0),(300,10), REDGOAL, RED)
    moderate_2.add_goal((300,0),(700,10), GREENGOAL, GREEN)
    moderate_2.add_goal((700,0), (1000,10), REDGOAL, RED)

    # Tunnel to the green goal
    moderate_3 = SimActTrial('moderate_3', dims=(1000, 600))
    moderate_3.add_goal((0, 0), (10, 250), REDGOAL, RED)
    moderate_3.add_goal((0, 250), (10, 350), GREENGOAL, GREEN)
    moderate_3.add_goal((0, 350), (10, 600), REDGOAL, RED)
    moderate_3.add_wall((10, 220), (500, 250))
    moderate_3.add_wall((10, 350), (500, 380))
    moderate_3.add_ball((750, 300), (0, 1))

    # Avoid the L
    moderate_4 = SimActTrial('moderate_4', dims=(1000, 600))
    moderate_4.add_goal((0, 0), (400, 10), GREENGOAL, GREEN)
    moderate_4.add_goal((400, 0), (1000, 10), REDGOAL, RED)
    moderate_4.add_goal((990, 10), (1000, 600), REDGOAL, RED)
    moderate_4.add_wall((0, 280), (400, 320))
    moderate_4.add_wall((600, 150), (640, 450))
    moderate_4.add_ball((150, 500), (0, 1))

    # Going around
    moderate_5 = SimActTrial('moderate_5', dims=(1000, 600))
    moderate_5.add_goal((0, 0), (1000, 10), GREENGOAL, GREEN)
    moderate_5.add_goal((0, 590), (1000, 600), REDGOAL, RED)
    moderate_5.add_wall((220, 80), (780, 100))
    moderate_5.add_ball((500, 400), (0, 1))

    # Grand escape
    moderate_6 = SimActTrial('moderate_6', dims=(1000, 600))
    moderate_6.add_goal((990, 0), (1000, 300), REDGOAL, RED)
    moderate_6.add_goal((750, 0), (990, 10), REDGOAL, RED)
    moderate_6.add_goal((990, 300), (1000, 600), GREENGOAL, GREEN)
    moderate_6.add_goal((750, 590), (990, 600), GREENGOAL, GREEN)
    moderate_6.add_wall((0, 0), (500, 50))
    moderate_6.add_wall((0, 50), (50, 550))
    moderate_6.add_wall((0, 550), (500, 600))
    moderate_6.add_wall((450, 250), (500, 550))
    moderate_6.add_wall((200, 250), (450, 300))
    moderate_6.add_wall((200, 300), (250, 400))
    moderate_6.add_ball((350, 350), (0, 1))


    """ Make the hardest trials (p(guess) < 10%) """

    hard_1 = SimActTrial('hard_1', dims=(1000, 600))
    hard_1.add_ball((700,300), (0,1))
    hard_1.add_goal((0, 0), (10, 300), GREENGOAL, GREEN)
    hard_1.add_goal((0, 300), (10, 600), REDGOAL, RED)
    hard_1.add_wall((300,0), (350, 450))

    hard_2 = SimActTrial('hard_2', dims=(1000, 600))
    hard_2.add_goal((990, 0), (1000, 150), REDGOAL, RED)
    hard_2.add_goal((990, 150), (1000, 450), GREENGOAL, GREEN)
    hard_2.add_goal((990, 450), (1000, 600), REDGOAL, RED)
    hard_2.add_wall((200, 200), (800, 250))
    hard_2.add_wall((750, 250), (800, 600))
    hard_2.add_ball((600, 400), (0, 1))

    hard_3 = SimActTrial('hard_3', dims=(1000, 600))
    hard_3.add_goal((0, 0), (10, 200), REDGOAL, RED)
    hard_3.add_goal((0, 200), (10, 500), GREENGOAL, GREEN)
    hard_3.add_goal((0, 500), (10, 600), REDGOAL, RED)
    hard_3.add_wall((150, 200), (200, 600))
    hard_3.add_wall((450, 0), (500, 400))
    hard_3.add_ball((600, 300), (0, 1))

    # Requires extremely precise bounce
    hard_4 = SimActTrial('hard_4', dims=(1000, 600))
    hard_4.add_goal((0, 0), (300, 10), GREENGOAL, GREEN)
    hard_4.add_goal((300, 0), (1000, 10), REDGOAL, RED)
    hard_4.add_wall((0, 100), (300, 200))
    hard_4.add_wall((500, 100), (1000, 200))
    hard_4.add_ball((100, 400), (0, 1))

    # THREAD THE NEEDLE!!!
    hard_5 = SimActTrial('hard_5', dims=(1000, 600))
    hard_5.add_goal((0, 0), (990, 10), REDGOAL, RED)
    hard_5.add_goal((990, 0), (1000, 250), REDGOAL, RED)
    hard_5.add_goal((990, 250), (1000, 350), GREENGOAL, GREEN)
    hard_5.add_goal((990, 350), (1000, 600), REDGOAL, RED)
    hard_5.add_goal((0, 590), (990, 600), REDGOAL, RED)
    hard_5.add_wall((700, 450), (900, 480))
    hard_5.add_wall((350, 120), (550, 150))
    hard_5.add_wall((0, 450), (200, 480))
    hard_5.add_wall((750, 250), (770, 350))
    hard_5.add_ball((100, 375), (0, 1))

    # The floor is lava!!!
    hard_6 = SimActTrial('hard_6', dims=(1000, 600))
    hard_6.add_goal((0, 0), (1000, 10), REDGOAL, RED)
    hard_6.add_goal((0, 10), (10, 590), REDGOAL, RED)
    hard_6.add_goal((990, 10), (1000, 590), REDGOAL, RED)
    hard_6.add_goal((0, 590), (100, 600), REDGOAL, RED)
    hard_6.add_goal((100, 590), (200, 600), GREENGOAL, GREEN)
    hard_6.add_goal((200, 590), (1000, 600), REDGOAL, RED)
    hard_6.add_ball((880, 50), (0, 1))


    """ Intro trials """

    intro_1 = SimActTrial('intro_1', dims=(1000, 600))
    intro_1.add_goal((0, 0), (1000, 10), GREENGOAL, GREEN)
    intro_1.add_goal((0, 10), (10, 250), GREENGOAL, GREEN)
    intro_1.add_goal((0, 250), (10, 350), REDGOAL, RED)
    intro_1.add_goal((0, 350), (10, 600), GREENGOAL, GREEN)
    intro_1.add_wall((700, 200), (800, 500))
    intro_1.add_ball((300, 300), (0, 1))

    intro_2 = SimActTrial('intro_2', dims=(1000, 600))
    intro_2.add_goal((990, 0), (1000, 600), GREENGOAL, GREEN)
    intro_2.add_goal((0, 0), (10, 600), REDGOAL, RED)
    intro_2.add_wall((500, 100), (700, 250))
    intro_2.add_wall((700, 400), (900, 550))
    intro_2.add_ball((100, 450), (0, 1))

    intro_3 = SimActTrial('intro_3', dims=(1000, 600))
    intro_3.add_goal((0, 0), (1000, 10), REDGOAL, RED)
    intro_3.add_goal((0, 590), (1000, 600), GREENGOAL, GREEN)
    intro_3.add_wall((300, 100), (1000, 250))
    intro_3.add_wall((0, 350), (700, 500))
    intro_3.add_ball((200, 300), (0, 1))

    intro_4 = SimActTrial('intro_4', dims=(1000, 600))
    intro_4.add_goal((0, 0), (10, 600), GREENGOAL, GREEN)
    intro_4.add_goal((990, 0), (1000, 600), REDGOAL, RED)
    intro_4.add_goal((300, 590), (990, 600), REDGOAL, RED)
    intro_4.add_wall((250, 0), (300, 100))
    intro_4.add_wall((250, 200), (300, 600))
    intro_4.add_ball((800, 500), (0, 1))

    intro_5 = SimActTrial('intro_5', dims=(1000, 600))
    intro_5.add_goal((990, 0), (1000, 200), REDGOAL, RED)
    intro_5.add_goal((990, 200), (1000, 400), GREENGOAL, GREEN)
    intro_5.add_goal((990, 400), (1000, 600), REDGOAL, RED)
    intro_5.add_wall((700, 200), (750, 400))
    intro_5.add_ball((200, 300), (0, 1))

    intro_6 = SimActTrial('intro_6', dims=(1000, 600))
    intro_6.add_goal((0, 0), (1000, 10), GREENGOAL, GREEN)
    intro_6.add_goal((0, 590), (1000, 600), REDGOAL, RED)
    intro_6.add_wall((300, 100), (1000, 250))
    intro_6.add_wall((0, 350), (700, 500))
    intro_6.add_ball((200, 300), (0, 1))

    intro_7 = SimActTrial('intro_7', dims=(1000, 600))
    intro_7.add_goal((0, 0), (10, 600), GREENGOAL, GREEN)
    intro_7.add_goal((990, 0), (1000, 600), REDGOAL, RED)
    intro_7.add_wall((100, 0), (200, 100))
    intro_7.add_wall((100, 170), (200, 600))
    intro_7.add_wall((800, 0), (900, 100))
    intro_7.add_wall((800, 170), (900, 600))
    intro_7.add_ball((500, 500), (0, 1))


    tr_list = [diff + '_' + str(i+1) for i in range(6) for
               diff in ['easy', 'moderate', 'hard']]

    easy_1.save("easy_1.json", fldr, askoverwrite=False)
    easy_2.save("easy_2.json", fldr, askoverwrite=False)
    easy_3.save("easy_3.json", fldr, askoverwrite=False)
    easy_4.save("easy_4.json", fldr, askoverwrite=False)
    easy_5.save("easy_5.json", fldr, askoverwrite=False)
    easy_6.save("easy_6.json", fldr, askoverwrite=False)

    moderate_1.save("moderate_1.json", fldr, askoverwrite=False)
    moderate_2.save("moderate_2.json", fldr, askoverwrite=False)
    moderate_3.save("moderate_3.json", fldr, askoverwrite=False)
    moderate_4.save("moderate_4.json", fldr, askoverwrite=False)
    moderate_5.save("moderate_5.json", fldr, askoverwrite=False)
    moderate_6.save("moderate_6.json", fldr, askoverwrite=False)

    hard_1.save("hard_1.json", fldr, askoverwrite=False)
    hard_2.save('hard_2.json', fldr, askoverwrite=False)
    hard_3.save("hard_3.json", fldr, askoverwrite=False)
    hard_4.save("hard_4.json", fldr, askoverwrite=False)
    hard_5.save("hard_5.json", fldr, askoverwrite=False)
    hard_6.save("hard_6.json", fldr, askoverwrite=False)

    intro_1.save("intro_1.json", fldr, askoverwrite=False)
    intro_2.save("intro_2.json", fldr, askoverwrite=False)
    intro_3.save("intro_3.json", fldr, askoverwrite=False)
    intro_4.save("intro_4.json", fldr, askoverwrite=False)
    intro_5.save("intro_5.json", fldr, askoverwrite=False)
    intro_6.save("intro_6.json", fldr, askoverwrite=False)
    intro_7.save("intro_7.json", fldr, askoverwrite=False)

    with open(os.path.join(fldr, "TrList.json"), 'w') as trfl:
        json.dump(tr_list, trfl)
