library(ggplot2)
library(maps)
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
library(purrr)
setwd("~/Desktop/2018WINTER/PLSC43502/ML_finalPJT")

dtm <- read.csv('Data/alldf_covariates_adddtm.csv')
dtm$sum<-rowSums(dtm[, c(25:34)])/nrow(dtm)
sumbystate<-aggregate(dtm$sum, by=list(id=dtm$State), FUN=sum)

pro_state <- read.csv('Data/pro_state.csv')
propo <- data.frame(state = tolower(rownames(pro_state)), pro_state)
names(propo) <- c("state", "id", "proportion")
#state_wc $statelower <- tolower(state_wc$id)
map_pro <- merge(fifty_states, propo, by="id",all.x=TRUE)

data("fifty_states")

#fifty_states$border <- ifelse(fifty_states$id %in% c('illinois'), 'red', NA)
rust_ex <- c('illinois','pennsylvania', 'west virginia',
             'ohio', 'indiana', 'michigan','illinois',
             'iowa', 'wisconsin', 'missouri', 'new york')
filter<- fifty_states[fifty_states$id %in% rust_ex,]
#data("fifty_states") # this line is optional due to lazy data loading

#state_wc <- data.frame(state = tolower(rownames(sumbystate)), sumbystate)
#state_wc $statelower <- tolower(state_wc$id)
#map_wc <- merge(fifty_states, sumbystate, by="id",all.x=TRUE)
#map_wc$x[is.na(map_wc$x)] <- 0

# map_id creates the aesthetic mapping to the state name column in your data
p <- ggplot(map_pro, aes(map_id =id)) + 
  # map points to the fifty_states shape data
  geom_map(aes(fill = proportion), map = fifty_states) +
  #geom_map(map =filter, aes(col="red", fill=FALSE), fill=NA)  +
  #geom_map(map = subset(fifty_states, id %in% rust_ex),
  #         fill = NA, colour = "red", size = 0.7, alpha = 0.2) +
  expand_limits(x = fifty_states$long, y = fifty_states$lat) +
  coord_map() +
  scale_fill_gradient(low="white", high="dark green", name="Proportion")+
  scale_x_continuous(breaks = NULL) + 
  scale_y_continuous(breaks = NULL) +
  #scale_linetype_manual(values = c('darkgreen', 'red', 'yellow'),
  #                  labels = c('Above Mean', 'At Mean', 'Below Mean'))+
  #scale_colour_manual(name="Line Color",
  #                    values=c(myline1="red", myline2="blue", myline3="purple"))+
  #scale_size_manual(breaks = 'labelsize', values = 5)+
  labs(x = "", y = "") +
  theme(legend.position = "bottom")+
  theme(panel.background = element_rect(fill = 'skyblue')) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
  theme(axis.title.x=element_blank(),
        axis.text.x=element_blank(),
        axis.ticks.x=element_blank(),
        axis.title.y=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks.y=element_blank())

p
# add border boxes to AK/HI
p + fifty_states_inset_boxes() 

ggsave("../ML_finalPJT/Result/Plots/wcsum-length_addboundaries.png", width = 14, height = 8, dpi = 300)
dev.off() 
#x$region <- tolower(x$State)


#states <- map_data("state")
#map.df <- merge(states,x, by="region", all.x=T)
#map.df <- map.df[order(map.df$order),]
#ggplot(map.df, aes(x=long,y=lat,group=group))+
#  geom_polygon(aes(fill=Count))+
#  geom_path()+ 
#  scale_fill_gradientn(colours=rev(heat.colors(10)),na.value="grey90")+
#  coord_map()

#ggplot(sim_data_geo, aes(long, lat)) 
#+ geom_polygon(aes(group=group, fill=x))
#+scale_fill_gradient(low="white", high="red", name="Frequency")

#plot2 <- qplot(long, lat, data=sim_data_geo, geom="polygon",
#               fill=x, group=group) + scale_fill_gradient(low="white", 
#                                                                  high="red", name="Frequency") + 
#  theme(panel.background = element_rect(fill = 'skyblue')) +
#  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
#  theme(axis.title.x=element_blank(),
#        axis.text.x=element_blank(),
#        axis.ticks.x=element_blank(),
#        axis.title.y=element_blank(),
#        axis.text.y=element_blank(),
#        axis.ticks.y=element_blank())
#plot2
