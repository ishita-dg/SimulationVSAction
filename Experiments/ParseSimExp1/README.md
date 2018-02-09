# Information on the parsed files:

trial_data.csv: Summary information for each trial

* WID: The worker identifier
* TrialName: Unique identifier for each trial
* ExpCostCondition: The cost of each experiment for participant (10 or 20)
* TimeCostCondition: Dummy for now -- always basic time (6/s)
* Accurate: Boolean indicating whether final shot was successful
* ShotAngle: Angle (rad) of final shot
* ScoreEarned: The score earned for that trial based on shot outcome
* NumExperiments: The number of play experiment shots run
* PlayTime: How long (in s) until the take a shot was hit
* ShotTime: The time between the "take a shot" button and doing it
* ScoreRemaining: The potential score that could be earned by a shot
* WasIntro: Boolean indicating whether this was an introductory trial
* TrialOrder: The order participant saw this trial in
* TimedOutShot: Boolean indicating the shot wasn't taken
* ScoreOut: Boolean indicating the score ran down to 0
* FocusLost: Boolean indicating the participant browsed away from the screen

shot_data.csv: Individual lines for each experiment & shot

* WID: The worker identifier
* TrialName: Unique identifier for each trial
* ShotType: {Experiment / Final} indicating which type
* WasIn: Boolean indicating it hit the green goal
* ShotAngle: Angle (rad) for the shot
* TimeFromBeginning: Time since the beginning of the exp that this happened
* WasIntro: Boolean indicating whether this was an intro trial
* FocusLost: Boolean indicating the participant browsed away from the screen
