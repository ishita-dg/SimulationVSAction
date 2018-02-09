#' ---
#' title: Sim/Act CogSci Analyses
#' author: Kevin A Smith
#' date: Jan 23, 2018
#' output:
#'    html_document:
#'      theme: default
#'      highlight: tango
#' ---

#+ General settings, echo = TRUE, results = 'hide', fig.width = 4, fig.height = 4 ------------------------------------------------------------------------------

knitr::opts_chunk$set(warning=F, message=F, cache = F, echo=F)
options(digits = 5)
kable = knitr::kable
export = F
FIGURE_DIR = "Figures"

#+ Initialization ----------------------------------------------------------

library(ppcor)
library(parallel)
library(lme4)
library(ggplot2)
library(ggrepel)
library(tidyr)
library(dplyr)
library(xtable) # Not directly used but helpful for latex translating

human_data_path = "../../Experiments/ParseSimExp1/trial_data.csv"
human_shot_data_path = "../../Experiments/ParseSimExp1/shot_data.csv"
model_data_path = "full_trial_data.csv"
dyna_data_path = "dyna_trial_data.csv"
guess_data_path = "random_shot_tables.csv"

MISSING_THRESHOLD = .5 # Threshold for removing participants who lost x% of trials

model_cost_factor_translation = c("1.1" = "Cheap", "2.2" = "Costly")

abl = geom_abline(intercept=0, slope=1, linetype='dashed')

cohensD = function(ttest) {
  return( 2*ttest$statistic / sqrt(ttest$parameter))
}

EXAMPLE_TRIALS = c('Trial6' = 'red', 'Trial7' = 'blue', 'Trial18' = 'darkgreen')
FONT = 'Helvetica'
PLOT_THEME = theme_bw() + theme(axis.text = element_text(family=FONT, size=12),
                                axis.title = element_text(family=FONT, size=16, face='bold'),
                                title = element_text(family=FONT, size=16, face='bold'))

#+ Loading data --------------------------------------

guess_data = read.csv(guess_data_path)
trial_mapping = read.csv('trial_name_translation.csv')

raw_human_data = read.csv(human_data_path) %>% filter(WasIntro == "False", ExpCostCondition != 6)
subj_tab = table(raw_human_data$WID)
bad_subjs = names(subj_tab)[subj_tab != 18]
raw_human_data = raw_human_data %>% filter(!(WID %in% bad_subjs)) %>%
  mutate(MissingTrial = TimedOutShot== 'True' | FocusLost == 'True' | ScoreOut == 'True')
missing_humans = raw_human_data %>% group_by(WID, ExpCostCondition) %>% summarize(Missing = mean(MissingTrial))
more_bad_subjs = as.character((missing_humans %>% filter(Missing > MISSING_THRESHOLD))$WID)
raw_human_data = raw_human_data %>% filter(!(WID %in% more_bad_subjs))

human_data = read.csv(human_data_path) %>%
  filter(!(WID %in% c(bad_subjs, more_bad_subjs)), WasIntro == "False", TimedOutShot == "False", FocusLost == "False", ExpCostCondition != 6) %>%
  #filter(ScoreOut=='False') %>%
  mutate(ExpCost = ExpCostCondition,
         ExpCostCondition = factor(c("10" = "Cheap", "20" = "Costly")[as.character(ExpCostCondition)]),
         ReconstructedTime = (100-ScoreRemaining - ExpCost*NumExperiments) / TimeCostCondition) %>%
  merge(guess_data %>% select(TrialName, GuessPct = TruthIn))

trial_data_wcond = human_data %>% group_by(TrialName, ExpCostCondition, GuessPct) %>% 
  summarize(AvgExp = mean(NumExperiments), AvgTime = mean(PlayTime), AvgReconTime = mean(ReconstructedTime),
            AvgScore = mean(ScoreEarned), Acc = mean(Accurate=='True'), MedExp = median(NumExperiments)) %>%
  ungroup

trial_data = human_data %>%
  group_by(TrialName, GuessPct) %>% 
  summarize(AvgExp = mean(NumExperiments), AvgTime = mean(PlayTime), AvgReconTime = mean(ReconstructedTime),
            AvgScore = mean(ScoreEarned), Acc = mean(Accurate=='True'), MedExp = median(NumExperiments)) %>%
  ungroup

shot_data = read.csv(human_shot_data_path) %>% 
  filter(!(WID %in% c(bad_subjs, more_bad_subjs)), WasIntro != "True", FocusLost == "False")

shot_data$TimeSinceLast = 0
shot_data$TimeSinceLast[1] = shot_data$TimeFromBeginning[1]
shot_data$ShotOrder = 1
last_wid = shot_data$WID[1]
last_trial = shot_data$TrialName[1]
cur_shot = 1
for (i in 2:nrow(shot_data)) {
  if (shot_data$WID[i] == last_wid && shot_data$TrialName[i] == last_trial) {
    shot_data$TimeSinceLast[i] = shot_data$TimeFromBeginning[i] - shot_data$TimeFromBeginning[i-1]
    cur_shot = cur_shot + 1
    shot_data$ShotOrder[i] = cur_shot
  } else {
    shot_data$TimeSinceLast[i] = shot_data$TimeFromBeginning[i]
    last_wid = shot_data$WID[i]
    last_trial = shot_data$TrialName[i]
    cur_shot = 1
    shot_data$ShotOrder[i] = cur_shot
  }
}

exp_shots = shot_data %>% filter(ShotType == "Experiment")
exp_shots = exp_shots %>% 
  merge(exp_shots %>% group_by(WID, TrialName) %>% summarize(MaxShots = max(ShotOrder))) %>%
  merge(human_data %>% select(WID, TrialName, ScoreOut))

human_data2 = human_data %>% merge(exp_shots %>% group_by(WID, TrialName) %>% summarize(MaxShots = max(ShotOrder)))

model_data_full = read.csv("fullangle.csv") %>%
  rename(TrialName = V2, CostFactor = V3, NumModelExp = V4, NumModelSim = V5) %>%
  filter(CostFactor == 2.2) %>% 
  mutate(TrialName = trimws(as.character(TrialName))) %>%
  merge(trial_mapping) %>%
  select(TrialName, AnodyneName, CostFactor, NumModelExp, NumModelSim)
  
model_data = model_data_full %>%
  group_by(TrialName, AnodyneName, CostFactor) %>%
  summarize(AvgModExpts = mean(NumModelExp), SDModExpts = sd(NumModelExp),
            AvgModSims = mean(NumModelSim), SDModSim = sd(NumModelSim)) %>%
  mutate(ExpCostCondition = factor(model_cost_factor_translation[as.character(CostFactor)])) %>%
  select(-CostFactor) %>% ungroup

model_data_nocond = model_data_full %>%
  group_by(TrialName, AnodyneName) %>%
  summarize(AvgModExpts = mean(NumModelExp), SDModExpts = sd(NumModelExp),
            AvgModSims = mean(NumModelSim), SDModSim = sd(NumModelSim)) %>% ungroup

exponly_data_full = read.csv("exponlyangles.csv") %>%
  rename(TrialName = V2, CostFactor = V3, NumModelExp = V4, NumModelSim = V5) %>%
  mutate(TrialName = trimws(as.character(TrialName))) %>%
  merge(trial_mapping) %>%
  select(TrialName, AnodyneName, CostFactor, NumModelExp, NumModelSim)

exponly_data = exponly_data_full %>%
  group_by(TrialName, AnodyneName) %>%
  summarize(AvgEOnlyExpts = mean(NumModelExp), SDEOnlyExpts = sd(NumModelExp),
            AvgEOnlySims = mean(NumModelSim), SDEOnlySim = sd(NumModelSim)) %>% ungroup

trial_data_wcond = trial_data_wcond %>% merge(model_data)

trial_data = trial_data %>% merge(model_data_nocond) %>% merge(exponly_data)

participant_data = human_data %>% group_by(WID, ExpCostCondition) %>%
  summarize(AvgAcc = mean(Accurate=='True'), AvgScore = mean(ScoreEarned), AvgExp=mean(NumExperiments),
            AvgTime=mean(ReconstructedTime))


# Write out the cleaned human data
write.csv(human_data, "clean_human_data.csv", row.names = F)

# Write out trial renaming conventions
guess_data = guess_data %>% filter(substr(as.character(guess_data$TrialName), 1, 1) != 'i') %>% arrange(TruthIn)
guess_data$AnodyneName = paste("Trial", 1:nrow(guess_data), sep="")
guess_data$AnodyneNumber = as.character(1:nrow(guess_data))

write.csv(guess_data %>% select(TrialName, AnodyneName, TruthIn), "trial_name_translation.csv", row.names=F)

trial_data_wcond = trial_data_wcond %>% merge(guess_data %>% select(TrialName, AnodyneName, AnodyneNumber))
trial_data = trial_data %>% merge(guess_data %>% select(TrialName, AnodyneName, AnodyneNumber))
# Color the trials
trial_data_wcond = trial_data_wcond %>% mutate(PlotColor = EXAMPLE_TRIALS[as.character(AnodyneName)], PlotColor = ifelse(is.na(PlotColor), "black", PlotColor),
                                   PlotSurroundWidth = ifelse(PlotColor == 'black', .25, 1.5))
trial_data = trial_data %>% mutate(PlotColor = EXAMPLE_TRIALS[as.character(AnodyneName)], PlotColor = ifelse(is.na(PlotColor), "black", PlotColor),
                                   PlotSurroundWidth = ifelse(PlotColor == 'black', .25, 1.5))


#+ Behavioral results ------------------------------------

#' # Data cleaning numbers
#' 
#' ### Total number of participants in each cost condition
#' 
print(table(raw_human_data$ExpCostCondition) / 18)

#' ### Removals due to shot time-out

shot_time_out_tab = table(raw_human_data$TimedOutShot)
print(shot_time_out_tab)
print(paste("Pct:", shot_time_out_tab[2]/ sum(shot_time_out_tab)))

#' ### Removals due to lost focus
#' 
focus_lost_tab = table(raw_human_data$FocusLost)
print(focus_lost_tab)
print(paste("Pct:", focus_lost_tab[2]/sum(focus_lost_tab)))

#' ### Bad subjects who lost > 50% of data due to time-outs
print(with(missing_humans, table(ExpCostCondition, Missing > MISSING_THRESHOLD)))

#' # Behavioral results
#' 
#' ## Effects of chance guessing
#'
#' ### Accuracy better than chance
#' 
#' Test if the average accuracy for each trial is higher than average guessing accuracy

acc_above_chance_test = t.test(trial_data$Acc, mu = mean(trial_data$GuessPct))
print(acc_above_chance_test)

print(paste("d=", cohensD(acc_above_chance_test)))


#' ### Is accuracy correlated with guess percentage?
#' 

print(paste("r between trial accuracy & trial guess pct:", with(trial_data,cor(Acc, GuessPct))))
print(with(trial_data, cor.test(Acc, GuessPct)))
print(ggplot(trial_data, aes(x=GuessPct, y=Acc)) + 
  geom_point() + abl +
  xlim(c(0,1)) + ylim(c(0,1)) +
  theme_bw())

#' ### Is number of experiments correlated with guess percentage?

print(paste("r between avg num guesses & trial guess pct:", with(trial_data,cor(AvgExp, GuessPct))))
print(with(trial_data, cor.test(AvgExp, GuessPct)))
#print(ggplot(trial_data, aes(x=GuessPct, y=AvgExp)) + 
#        geom_point() +
#        xlim(c(0,1)) +
#        theme_bw())
plot_exp_guess = ggplot(trial_data, aes(x=GuessPct, y=AvgExp, label=AnodyneNumber)) +
  geom_label(fill = trial_data$PlotColor, color='white', label.size = trial_data$PlotSurroundWidth,
             family=FONT, fontface='bold') +
  xlim(c(0,1)) + 
  xlab("Chance of guessing") + ylab("Avg. number of experiments") +
  PLOT_THEME

print(plot_exp_guess)

#' ### Is number of experiments not just explained by guess pct?

test_just_guess_pct = glm(NumExperiments ~ GuessPct, data=human_data, family=poisson)
test_with_trial_name = glm(NumExperiments ~ TrialName + GuessPct, data=human_data, family=poisson)
anova(test_just_guess_pct, test_with_trial_name, test='Chisq')

#' ### Is time correlated with guess percentage?

print(paste("r between avg num guesses & trial guess pct:", with(trial_data,cor(AvgReconTime, GuessPct))))
print(with(trial_data, cor.test(AvgReconTime, GuessPct)))
#print(ggplot(trial_data, aes(x=GuessPct, y=AvgReconTime)) + 
#        geom_point() +
#        xlim(c(0,1)) +
#        theme_bw())
plot_time_guess = ggplot(trial_data, aes(x=GuessPct, y=AvgReconTime, label=AnodyneNumber)) +
  geom_label(fill = trial_data$PlotColor, color='white', label.size = trial_data$PlotSurroundWidth,
             family=FONT, fontface='bold') +
  xlim(c(0,1)) + 
  xlab("Chance of guessing") + ylab("Avg. thinking time (s)") +
  PLOT_THEME

print(plot_time_guess)

#' ## Effects of condition
#' 
#' ### Does accuracy change by condition?
#' 
acc_by_condition_test = t.test(AvgAcc ~ ExpCostCondition, data=participant_data)
print(acc_by_condition_test)
print(paste('d=',cohensD(acc_by_condition_test)))

#' ### Does number of experiments change by condition?
avg_exp_by_condition_test = t.test(AvgExp ~ ExpCostCondition, data=participant_data)
print(avg_exp_by_condition_test)
print(paste('d=',cohensD(avg_exp_by_condition_test)))

#' ### Does time change by condition?
avg_time_by_condition_test = t.test(AvgTime ~ ExpCostCondition, data=participant_data)
print(avg_time_by_condition_test)
print(paste('d=',cohensD(avg_time_by_condition_test)))


#lots_o_shots = exp_shots %>% filter(MaxShots >= 3) %>% filter(ScoreOut == "False")
#lots_o_shots %>% group_by(ShotOrder) %>% summarize(Time = mean(TimeSinceLast), SDTime = sd(TimeSinceLast))

#' ## Do people who use more experiments do better?

#' ### Are they more accurate?

acc_vs_exp_test = with(participant_data, cor.test(AvgAcc, AvgExp))
print(acc_vs_exp_test)

#' ### Do they take less time?
acc_vs_time_test = with(participant_data, cor.test(AvgAcc, AvgTime))
print(acc_vs_time_test)

#' ### Correlation between exp and time
exp_vs_time_test = with(participant_data, cor.test(AvgExp, AvgTime))
print(exp_vs_time_test)


#+ Model Comparison ------------------

#' # Model comparison
#' 
#' ## Correlations with full model
#' 
#' ### Between model and people: # experiments

cor_mod_exps = with(trial_data, cor.test(AvgModExpts, AvgExp))
cor_mod_exps_r = cor_mod_exps$estimate
cor_mod_exps_p = cor_mod_exps$p.value
cor_mod_exps_lab = paste("r=", signif(cor_mod_exps_r, 2), sep="")


plot_cor_mod_exps = ggplot(trial_data, 
       aes(x = AvgModExpts, y = AvgExp, label = AnodyneNumber)) + 
  ggtitle("Number of experiments") +
  abl + 
  geom_label_repel(fill = trial_data$PlotColor, color='white', label.size = trial_data$PlotSurroundWidth,
             family=FONT, fontface='bold',
             segment.color = "black") +
  xlab("Predicted") + ylab("Observed") +
  geom_text(x = 0.15, y=1.75, label=cor_mod_exps_lab, family=FONT, size=4) + 
  coord_fixed(xlim = c(0, 1.8), ylim = c(0, 1.8)) + 
  PLOT_THEME

print(cor_mod_exps)
print(plot_cor_mod_exps)


trial_data$PredictedModelTime = predict(lm(AvgReconTime ~ AvgModSims, data=trial_data))
cor_mod_time = with(trial_data, cor.test(PredictedModelTime, AvgReconTime))
cor_mod_time_r = cor_mod_time$estimate
cor_mod_time_p = cor_mod_time$p.value
cor_mod_time_lab = paste("r=", signif(cor_mod_time_r, 2), sep="")


plot_cor_mod_time = ggplot(trial_data, 
                           aes(x = PredictedModelTime, y = AvgReconTime, label = AnodyneNumber)) + 
  ggtitle("Time spent thinking") +
  abl + 
  geom_label(fill = trial_data$PlotColor, color='white', label.size = trial_data$PlotSurroundWidth,
                   family=FONT, fontface='bold',
                   segment.color = 'black') +
  xlab("Predicted") + ylab("Observed") +
  geom_text(x = 1.7, y=3.9, label=cor_mod_time_lab, family=FONT, size=4) + 
  coord_fixed(xlim = c(1.5, 4), ylim=c(1.5, 4)) + 
  PLOT_THEME

print(cor_mod_time)
print(plot_cor_mod_time)

#' ## Model correlation between expts and time

cor_mod_exp_vs_time = with(trial_data, cor.test(AvgModSims, AvgModExpts))
print(cor_mod_exp_vs_time)

1#' ## Do model simulations explain anything beyond experiments
test_time_by_expt_only = lm(data=trial_data, AvgReconTime ~ AvgExp)
test_time_with_mod_sims = lm(data=trial_data, AvgReconTime ~ AvgExp + AvgModSims)
print(anova(test_time_by_expt_only, test_time_with_mod_sims))

test_pcor_time_by_sims = trial_data %>% select(AvgReconTime, AvgExp, AvgModSims) %>% pcor

# FOR NOW: experiment only

with(trial_data, cor.test(AvgEOnlyExpts, AvgExp))

ggplot(trial_data, 
       aes(x = AvgEOnlyExpts, y = AvgExp, label = AnodyneNumber)) + 
  ggtitle("Number of experiments") +
  abl + 
  geom_label_repel(fill = trial_data$PlotColor, color='white', label.size = trial_data$PlotSurroundWidth,
                   family=FONT, fontface='bold',
                   segment.color = "black") +
  xlab("Predicted") + ylab("Observed") +
  #geom_text(x = 0.15, y=1.75, label=cor_mod_exps_lab, family=FONT, size=4) + 
  coord_fixed(xlim = c(0, 1.8), ylim = c(0, 1.8)) + 
  PLOT_THEME



####################
# Saving files
####################

ggsave(paste(FIGURE_DIR, 'exp_vs_guess.png', sep='/'), plot_exp_guess, width=4, height=4, units='in', dpi=300)
ggsave(paste(FIGURE_DIR, 'time_vs_guess.png', sep='/'), plot_time_guess, width=4, height=4, units='in', dpi=300)

ggsave(paste(FIGURE_DIR, 'modcomp_exp.png', sep='/'), plot_cor_mod_exps, width=4, height=4, units='in', dpi=300)
ggsave(paste(FIGURE_DIR, 'modcomp_time.png', sep='/'), plot_cor_mod_time, width=4, height=4, units='in', dpi=300)


