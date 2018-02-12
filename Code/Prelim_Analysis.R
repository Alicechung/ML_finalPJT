rm(list=ls())
library(ggplot2)
library(ggmap)
library(gapminder)
library(fiftystater)
library(rgdal)
library(dplyr)
library(tidyr)
library(tidyverse)
library(stringr)
library(modelr)
library(forcats)
library(rgeos)
library(maptools)
library(gpclib)
library(gridExtra)

select <- dplyr::select 


setwd("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data")
speechgeo <- read.csv("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data/wordcount_geocode_2.csv", header=TRUE)

length(which(is.na(speechgeo$lon)))
length(which(is.na(speechgeo$lat)))


