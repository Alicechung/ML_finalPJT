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

select <- dplyr::select 
sim <- Zelig::sim
logit <- VGAM::logit
expand <- tidyr::expand

setwd("C:/Users/minju/Dropbox/UChicago/MachineLearning/FinalProject")
mac_final <- read.csv("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data/alldf_180223.csv", header=TRUE)

###Add state-level unemployment
unemploy <- read.csv("C:/Users/minju/Dropbox/UChicago/MA Thesis/TAA/TAAcases/unemployment_statelevel.csv", header=TRUE)
mac_final <- left_join(mac_final, unemploy, by = c("Year" = "year", "Abb" = "state"))

###position as incumbent party vs. challenging party
mac_final <- mac_final%>%
  mutate(challenger = ifelse( Year == 2008 & PartyID == "Dem"|
                                Year == 2012 & PartyID == "Rep"|
                                Year == 2016 & PartyID == "Rep", 1, 0))

###local governor party similarity
localg <- read.csv("C:/Users/minju/Dropbox/UChicago/MA Thesis/TAA/TAAcases/states_partystrength.csv", na.strings = "", header=TRUE)
lgparty <- localg%>%select(state, year, governor)%>%dplyr::filter(year > 2007)
##filling in north carolina blanks
lgparty <- lgparty%>%mutate(nc = case_when((state=="north carolina"& year > 2007) &(state=="north carolina"& year < 2013) ~ "D", 
                                           (state=="north carolina"& year > 2012) ~ "R"))
lgparty$governor <- as.character(lgparty$governor)
lgparty$nc <- as.character(lgparty$nc)
lgparty <- lgparty%>%mutate(governor2 = ifelse(is.na(governor), nc, governor))%>%
  select(-governor, -nc)

lgparty <- lgparty%>%mutate(governorp = case_when(governor2 == "D" ~ "Dem", 
                                                governor2 == "R" ~ "Rep",
                                                governor2 == "I" ~ "Independent",
                                                governor2 == "Mark Dayton (DFL)" ~ "Ohters"))
lgparty <- lgparty%>%select(-governor2)

##left_join
mac_final$State = tolower(mac_final$State)
mac_final <- left_join(mac_final, lgparty, by = c("Year" = "year", "State" = "state"))%>%unique()

sum(length(which(!is.na(mac_final$swing_last_08) & is.na(mac_final$governorp))))

###before and after primary
mac_final$Date <- as.Date(mac_final$Date)
mac_final <- mac_final%>%mutate(primary = ifelse((Year == 2016 & PartyID == "Rep" & Date < "2016-05-27")|
                                                   (Year == 2016 & PartyID == "Dem" & Date < "2016-07-27")|
                                                   (Year == 2012 & PartyID == "Rep" & Date < "2012-05-30")|
                                                   (Year == 2012 & PartyID == "Dem" & Date < "2012-04-04")|
                                                   (Year == 2008 & PartyID == "Rep" & Date < "2008-03-05")|
                                                   (Year == 2008 & PartyID == "Dem" & Date < "2008-06-04"), 1, 0))

write.csv(mac_final, "Add_covariates2.csv")
