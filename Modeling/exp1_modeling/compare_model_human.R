library(dplyr)
library(ggplot2)
library(tidyr)

# Load in the data
cost_factor_translation = c("1.5" = "Cost10", "2" = "Cost20")

human_data_path = "../../Experiments/ParseSimExp1/trial_summary.csv"
full_human_data_path = "../../Experiments/ParseSimExp1/trial_data.csv"
model_data_path = "full_trial_data.csv"
dyna_data_path = "dyna_trial_data.csv"

fullhdat = read.csv(full_human_data_path) %>% filter(WasIntro == 'False', FocusLost == 'False')
hdat = read.csv(human_data_path)

# Transform model data to summarize by trial
model_data = read.csv(model_data_path, header=F,
                      col.names = c('RandomID', 'TrialName', 'CostFactor', 'NumExpts', 'NumSim'))

mdat = model_data %>% mutate(TrialName = trimws(TrialName)) %>%
  group_by(TrialName, CostFactor) %>%
  summarize(AvgModExpts = mean(NumExpts), SDModExpts = sd(NumExpts),
            AvgModSims = mean(NumSim), SDModSim = sd(NumSim))
mdat$ExpCostCondition = factor(cost_factor_translation[as.character(mdat$CostFactor)])
mdat = mdat %>% select(-CostFactor) %>% ungroup()

# Transform DYNA data to summarize by trial
dyna_data = read.csv(dyna_data_path, header=F,
                      col.names = c('RandomID', 'TrialName', 'CostFactor', 'NumExpts', 'NumSim'))
ddat = dyna_data %>% mutate(TrialName = trimws(TrialName)) %>%
  group_by(TrialName, CostFactor) %>%
  summarize(AvgDYNAExpts = mean(NumExpts), SDDYNAExpts = sd(NumExpts),
            AvgDYNASims = mean(NumSim), SDDYNASim = sd(NumSim))
ddat$ExpCostCondition = factor(cost_factor_translation[as.character(ddat$CostFactor)])
ddat = ddat %>% select(-CostFactor) %>% ungroup()

compdat = merge(hdat, mdat) %>% merge(ddat)

#######################################
# Show the comparisons -- with the model
ggplot(compdat, aes(x = AvgModExpts, y=AvgExp, color=ExpCostCondition, label=TrialName)) +
  geom_label() +
  geom_point() + theme_bw()

ggplot(compdat, aes(x = AvgModSims, y=AvgTime, color=ExpCostCondition, label=TrialName)) +
  geom_label() +
  geom_point() + theme_bw()

# Overall model/data comparisons
with(compdat, cor(AvgModExpts, AvgExp))
with(compdat, cor(AvgModSims, AvgTime))

# Comparison of experiments by cost condition
with(compdat %>% filter(ExpCostCondition == 'Cost10'), cor(AvgModExpts, AvgExp))
with(compdat %>% filter(ExpCostCondition == 'Cost20'), cor(AvgModExpts, AvgExp))

# Does the cost condition make a difference in the model fits?
summary(lm(data=compdat, AvgExp ~ AvgModExpts*ExpCostCondition))
summary(lm(data=compdat, AvgExp ~ AvgModExpts))
anova(lm(data=compdat, AvgExp ~ AvgModExpts),
      lm(data=compdat, AvgExp ~ AvgModExpts*ExpCostCondition))

# Comparison of time by cost condition
with(compdat %>% filter(ExpCostCondition == 'Cost10'), cor(AvgModSims, AvgTime))
with(compdat %>% filter(ExpCostCondition == 'Cost20'), cor(AvgModSims, AvgTime))

#######################################
# Show the comparisons -- with DYNA
ggplot(compdat, aes(x = AvgDYNAExpts, y=AvgExp, color=ExpCostCondition, label=TrialName)) +
  geom_label() +
  geom_point() + theme_bw()

ggplot(compdat, aes(x = AvgDYNASims, y=AvgTime, color=ExpCostCondition, label=TrialName)) +
  geom_label() +
  geom_point() + theme_bw()

with(compdat, cor(AvgDYNAExpts, AvgExp))
with(compdat, cor(AvgDYNASims, AvgTime))

with(compdat %>% filter(ExpCostCondition == 'Cost10'), cor(AvgDYNAExpts, AvgExp))
with(compdat %>% filter(ExpCostCondition == 'Cost20'), cor(AvgDYNAExpts, AvgExp))

with(compdat %>% filter(ExpCostCondition == 'Cost10'), cor(AvgDYNASims, AvgTime))
with(compdat %>% filter(ExpCostCondition == 'Cost20'), cor(AvgDYNASims, AvgTime))

#######################################
# Compare model & dyna

ggplot(compdat, aes(x=AvgDYNAExpts, y=AvgModExpts, color=ExpCostCondition)) +
  geom_point() + theme_bw()

ggplot(compdat, aes(x=AvgDYNASims, y=AvgModSims, color=ExpCostCondition)) +
  geom_point() + theme_bw()

#######################################
# Compare empirical

ggplot(compdat, aes(x=AvgExp, y=AvgTime, color=ExpCostCondition, label=TrialName)) +
  geom_label() + geom_point() + theme_bw()
with(compdat, cor(AvgExp, AvgTime))

empcor = fullhdat %>% group_by(WID) %>% summarize(r = cor(NumExperiments, PlayTime))
with(empcor %>% filter(!is.na(r)), mean(r))
