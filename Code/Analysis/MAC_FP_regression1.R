rm(list=ls())

library(readr)
library(tidyr)
library(stringr)
library(lubridate)
library(ggmap)
library(magrittr)
library(MASS)
library(dplyr)
library(stargazer)
library(plm)
library(zeligverse)
library(ggplot2)
library(pscl)
library(arm)
library(fBasics, warn.conflicts = FALSE)
library(foreign)
library(readtext)
library(stringr)
library(stm)
library(stats)
library(gpclib)
library(ggrepel)

select <- dplyr::select 
sim <- Zelig::sim
logit <- VGAM::logit
expand <- tidyr::expand

setwd("C:/Users/minju/Dropbox/UChicago/MachineLearning/FinalProject")
mac_final <- read.csv("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data/alldf_covariates_adddtm_allwords.csv", header=TRUE, as.is = T)
unemploy <- read.csv("C:/Users/minju/Dropbox/UChicago/MA Thesis/TAA/TAAcases/unemployment_statelevel.csv")
unemploy_lag <- unemploy%>%mutate(year_lag = year + 1)%>%select(-year)
colnames(unemploy_lag)[which(colnames(unemploy_lag) == 'unemployment')] <- 'lagged_unemploy'

mac_final <-left_join(mac_final, unemploy_lag, by = c("Year" = "year_lag", "Abb" = "state"))

mac_final <-mac_final%>%mutate(swing = ifelse((Year==2008&swing_last_08 <= 0.05)|
                                                  (Year==2012&swing_last_12 <= 0.05)|
                                                  (Year==2016&swing_last_16 <= 0.05), 1, 0),
                                 votemargin = case_when((Year==2008 ~ swing_last_08),
                                                        (Year==2012 ~ swing_last_12),
                                                        (Year==2016 ~ swing_last_16)))


mac_final$PartyID <- as.character(mac_final$PartyID)

mac_final <- mac_final%>%mutate(party = ifelse(PartyID == "Dem", 1, 0))  

mac_final <- mac_final%>%mutate(grlabel = paste (Author, Year, Abb, sep = ",", collapse = NULL))

#rust_swing <- subset(mac_final, Rustbelt==1 & swing ==1)
rust <- subset(mac_final, Rustbelt==1)
nonrust <- subset(mac_final, Rustbelt==0)

##sum rust words
rust <- rust%>%mutate(sumtrade_rust = trade + labor + worker + 
                               agreement + union + nafta + 
                               china + manufactur + play + 
                               plant + outsourc + wage + 
                               steel + organ + green)


nonrust <- nonrust%>%mutate(sumtrade_nonrust = african.american + hillari + clinton + 
                        inner + unleash + email + 
                        nafta + disastr + donor + 
                        lie + trade + massiv + 
                        oppress + rig + fail)


########Regression
model1 <- lm(sumtrade_rust ~ as.factor(PartyID) + swing + lagged_unemploy + challenger +
               governorp + primary + factor(Year), rust)

summary(model1)


stargazer(model1, type="html",
          column.labels = "Rustbelt Trade Rhetoric",
          dep.var.caption="Frequency of Trade-related Words",
          dep.var.labels.include=FALSE, no.space=TRUE,
          out="rust_model.htm")

########Graph
rustdot <- ggplot(rust, aes(x = votemargin, y= pro_rust, shape = factor(PartyID))) +
  geom_point(aes(colour = factor(PartyID)))+
  theme_bw() + 
  labs(x = "Vote Margin in Last Election", y = "Proportion of Trade-related Words", 
       title = "Relationship between Swing State and Trade Topic Salience, Rustbelt") +
  theme(plot.title = element_text(size =15, face = "bold"))

rustdot

rustdot2 <- rustdot + geom_label_repel(data = subset(rust, pro_rust> 0.04|votemargin>0.225),
  aes(votemargin, pro_rust, label = grlabel, fill = factor(PartyID)), color = 'white',
  box.padding = 0.1, point.padding = 0.1,
  segment.color = 'grey50')

rustdot2





##################Regression2
nonrust$governorp <- as.factor(nonrust$governorp)
nonrust2 <- subset(nonrust, governorp != "")

model2 <- lm(sumtrade_nonrust ~ as.factor(PartyID) + swing + lagged_unemploy + challenger +
               governorp + primary + factor(Year), nonrust2)

summary(model2)


stargazer(model2, type="html",
          column.labels = "Non-rustbelt Trade Rhetoric",
          dep.var.caption="Frequency of Trade-related Words",
          dep.var.labels.include=FALSE, no.space=TRUE,
          out="nonrust_model.htm")

########Graph
nonrustdot <- ggplot(nonrust2, aes(x = votemargin, y= pro_norust, shape = factor(PartyID))) +
  geom_point(aes(colour = factor(PartyID)))+
  theme_bw() + 
  labs(x = "Vote Margin in Last Election", y = "Proportion of Trade-related Words", 
       title = "Relationship between Swing State and Trade Topic Salience, Non-rustbelt") +
  theme(plot.title = element_text(size =15, face = "bold"))

nonrustdot

nonrustdot2 <- nonrustdot + geom_label_repel(data = subset(nonrust2, pro_norust> 0.05| votemargin> 0.35),
                                       aes(votemargin, pro_norust, label = grlabel, fill = factor(PartyID)), color = 'white',
                                       box.padding = 0.1, point.padding = 0.1,
                                       segment.color = 'grey50')
nonrustdot2

