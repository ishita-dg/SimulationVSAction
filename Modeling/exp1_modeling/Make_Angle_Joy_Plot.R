library(ggplot2)
library(ggridges)
library(dplyr)
library(scales)
library(gtools)

FONT = 'Helvetica'
PLOT_THEME = theme_bw() + theme(axis.text = element_text(family=FONT, size=12),
                                axis.title = element_text(family=FONT, size=16, face='bold'),
                                strip.text = element_text(family=FONT, size=12))

trial_mapping = read.csv('trial_name_translation.csv')

# Load in the data
dh = read.csv("clean_human_data.csv") %>% merge(trial_mapping) %>%
  mutate(angle = ifelse(ShotAngle < 0, ShotAngle + 2*pi, ShotAngle), type="Empirical") %>%
  select(trial=AnodyneName,type,angle)

db = read.csv("fullangle.csv") %>%
  rename(TrialName = V2, CostFactor = V3, ShotAngle = V6) %>%
  filter(CostFactor == 2.2) %>%
  mutate(TrialName = trimws(as.character(TrialName))) %>%
  merge(trial_mapping) %>%
  mutate(angle = ShotAngle * 2 * pi, type="Full Model") %>%
  select(trial=AnodyneName, type, angle)

deo = read.csv("exponlyangles.csv") %>% 
  rename(TrialName = V2, CostFactor = V3, ShotAngle = V6) %>%
  mutate(TrialName = trimws(as.character(TrialName))) %>%
  merge(trial_mapping) %>%
  mutate(angle = ShotAngle * 2 * pi, type="Experiment Only") %>%
  select(trial=AnodyneName, type, angle)

data = rbind(dh, db, deo)
data$trial = factor(data$trial, levels = mixedsort(levels(data$trial), decreasing=T))
data$type = factor(data$type, levels = c("Empirical", "Full Model", "Experiment Only"))


# Load in the correct angles
corrects = read.csv("high_detail_tables_full.csv") %>% merge(trial_mapping %>% select(-TruthIn)) %>%
  select(trial=AnodyneName, angle = Angle, goesin = TruthIn) %>%
  mutate(trial = factor(trial, levels = mixedsort(levels(trial), decreasing=T))) %>%
  arrange(trial, angle)

pi_scales <- math_format(.x * pi, format = function(x) x / pi)

p1 = ggplot(data, aes(x = angle, y = trial)) + 
  ylab("Trials")+xlab("Angle")+
  geom_density_ridges(scale = 1) +
  geom_ridgeline(data=corrects, aes(x=angle, y=trial, height=goesin), 
                 color='darkgreen', fill='darkgreen', alpha=.8, scale=-.05, min_height=.1, size=2) + 
  xlim(c(0, 2*pi))+
  facet_wrap(~type)+
  theme_ridges()+
  theme(axis.title.y=element_blank(),
        axis.title.x=element_blank())+
  scale_x_continuous(labels = pi_scales, breaks = seq(0*pi,  2*pi, pi / 2)) +
  PLOT_THEME

print(p1)

ggsave("Figures/shot_plot.pdf", p1, width=7, height=9, units='in')

#pdf("angles.pdf", width=6, height=8)
#p1
#dev.off()
#getwd()
