library(ggplot2)
library(dplyr)
library(tidyr)
library(lme4)
abl = geom_abline(intercept=0, slope=1, linetype='dashed')

dat = read.csv('trial_data.csv') %>% filter(WasIntro == "False", TimedOutShot == "False",
                                            FocusLost == "False", ExpCostCondition != 6)
dat$ExpCost = dat$ExpCostCondition
dat$ExpCostCondition = factor(dat$ExpCostCondition)
levels(dat$ExpCostCondition) = c("Cost10", "Cost20")
dat$ReconstructedTime = with(dat, (100-ScoreRemaining - ExpCost*NumExperiments) / TimeCostCondition)

# Aggregate by trial / condition
aggdat = dat %>% group_by(TrialName, ExpCostCondition) %>% 
  summarize(AvgExp = mean(NumExperiments), AvgTime = mean(PlayTime), AvgReconTime = mean(ReconstructedTime),
            AvgScore = mean(ScoreEarned), Acc = mean(Accurate=='True'), MedExp = median(NumExperiments))

write.csv(aggdat, 'trial_summary.csv', row.names=F)

# Are there more experiments in the costly condition?
exp_by_cost = aggdat %>% select(TrialName, ExpCostCondition, AvgExp) %>%
  spread(ExpCostCondition, AvgExp)
maxc = max(aggdat$AvgExp)

ggplot(exp_by_cost, aes(x=Cost10, y=Cost20)) + geom_label(aes(label=TrialName)) + geom_point() +
  abl + theme_bw() + xlim(c(0,maxc)) + ylim(c(0,maxc))
with(exp_by_cost, cor(Cost10, Cost20))

qplot(Cost10, Cost20,
      data=aggdat %>% select(TrialName, ExpCostCondition, MedExp) %>% spread(ExpCostCondition, MedExp)) +
  abl + theme_bw() + xlim(c(0,maxc)) + ylim(c(0,maxc))

with(aggdat, cor(AvgExp, AvgTime)) # Num exp correlates with time?

# Aggregate by individual
aggind = dat %>% group_by(WID, ExpCostCondition) %>%
  summarize(AvgExp = mean(NumExperiments), AvgScore = mean(ScoreEarned), Acc = mean(Accurate=='True'))

ggplot(aggind, aes(x=ExpCostCondition, y=AvgExp)) + geom_jitter(width=.2, height=0)  + theme_bw()

t.test(data = aggind, AvgExp ~ ExpCostCondition)
aggind %>% group_by(ExpCostCondition) %>% summarize(med = median(AvgExp))

diff_split = aggdat
diff_split$Diff = sapply(strsplit(as.character(diff_split$TrialName), '_'), function(x) {x[1]})
diff_split_agg = diff_split %>% group_by(Diff, ExpCostCondition) %>%
  summarize(AvgExpAgg = mean(AvgExp), SDExp = sd(AvgExp))
ggplot(diff_split_agg, aes(x=Diff, y=AvgExpAgg, group=ExpCostCondition, fill=ExpCostCondition)) + 
  geom_bar(stat='identity', position='dodge')

