"""
Parses output from psiTurk's download_datafiles into two files:

trial_data.csv: Summary information for each trial
    WID: The worker identifier
    TrialName: Unique identifier for each trial
    ExpCostCondition: The cost of each experiment for participant (10 or 20)
    TimeCostCondition: Dummy for now -- always basic time (6/s)
    Accurate: Boolean indicating whether final shot was successful
    ShotAngle: Angle (rad) of final shot
    ScoreEarned: The score earned for that trial based on shot outcome
    NumExperiments: The number of play experiment shots run
    PlayTime: How long (in s) until the take a shot was hit
    ShotTime: The time between the "take a shot" button and doing it
    ScoreRemaining: The potential score that could be earned by a shot
    WasIntro: Boolean indicating whether this was an introductory trial
    TrialOrder: The order participant saw this trial in
    TimedOutShot: Boolean indicating the shot wasn't taken
    ScoreOut: Boolean indicating the score ran down to 0
    FocusLost: Boolean indicating the participant browsed away from the screen

shot_data.csv: Individual lines for each experiment & shot
    WID: The worker identifier
    TrialName: Unique identifier for each trial
    ShotType: {Experiment / Final} indicating which type
    WasIn: Boolean indicating it hit the green goal
    ShotAngle: Angle (rad) for the shot
    TimeFromBeginning: Time since the beginning of the exp that this happened
    WasIntro: Boolean indicating whether this was an intro trial
    FocusLost: Boolean indicating the participant browsed away from the screen
"""

from __future__ import division, print_function
import pandas as pd
import json
import os

TIME_COST = "6" #CHANGE IF THIS CHANGES IN EXPT

if __name__ == '__main__':

    tdat = os.path.join('..', 'psiturk-simexp-1', 'trialdata.csv')
    qdat = os.path.join('..', 'psiturk-simexp-1', 'questiondata.csv')

    wid_mapping_idx = 0 # For anonymity of MTurk workers
    wid_mappings = {}

    trial_raw = pd.read_csv(tdat, names=["WID", "Index", "TimeStamp", "Data"])
    question_raw = pd.read_csv(qdat, names=["WID", "Key", "Value"])
    question_raw = question_raw.set_index("WID")

    with open('trial_data.csv', 'w') as trial_dat, \
    open('shot_data.csv', 'w') as shot_dat:
        # Headers
        trial_dat.write("WID,TrialName,ExpCostCondition,TimeCostCondition," +
                        "Accurate,ShotAngle,ScoreEarned,NumExperiments," +
                        "PlayTime,ShotTime,ScoreRemaining,WasIntro," +
                        "TrialOrder,TimedOutShot,ScoreOut,FocusLost\n")
        shot_dat.write("WID,TrialName,ShotType,WasIn,ShotAngle," +
                       "TimeFromBeginning,WasIntro,FocusLost\n")

        for raw_wid, dat in zip(trial_raw.WID, trial_raw.Data):
            if raw_wid not in wid_mappings.keys():
                this_map = "worker_" + str(wid_mapping_idx)
                wid_mapping_idx += 1
                wid_mappings[raw_wid] = this_map
            wid = wid_mappings[raw_wid]
            pdat = json.loads(dat)
            trname = pdat['trial_name']
            play_time = float(pdat['play_time'])
            shot_time = float(pdat['shot_time'])
            exp_cost = question_raw.lookup([raw_wid],['Value'])[0]
            # Write the trial data
            trial_dat.write(wid + ',' + trname + ',' + str(exp_cost) + ',' +
                TIME_COST + ',' + str(pdat['accurate']) + ',' +
                str(pdat['shot_angle']) + ',' + str(pdat['score']) + ',' +
                str(pdat['num_experiments']) + ',' + str(play_time) + ',' +
                str(shot_time) + ',' + str(pdat['points_left']) + ',' +
                str(pdat['isintro']) + ',' + str(pdat['trial_order']) + ',' +
                str(pdat['shot_timeout']) + ',' + str(pdat['time_up']) + ',' +
                str(pdat['badtrial']) + '\n')

            # Write the individual shot data
            for exp in pdat['experiments']:
                shot_dat.write(wid + ',' + trname + ',Experiment,' +
                    str(exp['Outcome']) + ',' + str(exp['Angle']) + ',' +
                    str(exp['ExpTime']) + ',' + str(pdat['isintro']) + ',' +
                    str(pdat['badtrial']) + '\n')
            if not pdat['shot_timeout']:
                shot_dat.write(wid + ',' + trname + ',Final,' +
                    str(pdat['accurate']) + ',' + str(pdat['shot_angle']) + ',' +
                    str(play_time + shot_time) + ',' + str(pdat['isintro']) + ',' +
                    str(pdat['badtrial']) + '\n')
