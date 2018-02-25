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
##If you cannot download gpclib, download Rtools first 

gpclibPermitStatus()


setwd("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data")
speech <- read.csv("C:/Users/minju/Documents/GitHub/ML_finalPJT/Data/primaryresult_words_count.csv", header=TRUE)


##conversion from city to lon, lat
speech$City <- as.character(speech$City)
speech <- cbind(speech, geocode(speech$City))
sum(is.na(speech$lon))
#conversion failed in the case of Hampton, Fayetteville, West Palm Beach

##add party variable to the candidate
speech <- speech%>%
  mutate(democrat = ifelse(Author == "Barack Obama"|
                             Author == "Hillary Clinton"|
                             Author == "John Edwards"|
                             Author == "Bill Richardson"|
                             Author == "Christopher Dodd"|
                             Author == "Joseph Biden"|
                             Author == "Bernie Sanders"|
                             Author == "Martin O'Malley"|
                             Author == "Lincoln Chafee"|
                             Author == "Jim Webb", 1, 0))

##classify protectionism/free trade words
speech <- speech%>%mutate(protectionism = sum(cheap + china + compete + competition + export + 
                                                import +protect + protection + rust.belt +
                                                subsidy + unemploy + unemployment))

##rustbelt dummy

write_csv(speech, "wordcount_geocode.csv")


##subsetting by year and party--for graph
rep_2008 <- subset(speech, democrat == 0 & Year == "2008")                          
dem_2008 <- subset(speech, democrat == 1 & Year == "2008")
rep_2012 <- subset(speech, democrat == 0 & Year == "2012")                          
dem_2012 <- subset(speech, democrat == 1 & Year == "2012")
rep_2016 <- subset(speech, democrat == 0 & Year == "2016")                          
dem_2016 <- subset(speech, democrat == 1 & Year == "2016")

##subsetting only year--for word frequency comparison
both_2016 <- subset(speech, Year == "2016")

##How many NAs in lon lat?
sum(is.na(rep_2008$lon))
sum(is.na(dem_2008$lon))
sum(is.na(rep_2012$lon))
sum(is.na(dem_2012$lon))
sum(is.na(rep_2016$lon))
sum(is.na(dem_2016$lon))

########Drawing map 

##us state map from US Census Bureau 
usa <- readOGR(
  "C:/Users/minju/Documents/GitHub/ML_finalPJT/Data/cb_2016_us_state_20m/cb_2016_us_state_20m.shp")
#Download the shape file from https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html
#Download state-cb_2016_us_state_20m.zip 

fortify(usa) %>%
  head()
as_tibble(usa@data)

usa %>%
  fortify(region = "STATEFP") %>%
  head() 

(usa2 <- usa %>%
    fortify(region = "NAME") %>%
    as_tibble() %>%
    left_join(usa@data, by = c("id" = "NAME")))

usa2 <- usa2 %>%
  filter(id != "Alaska", id != "Hawaii", id != "Puerto Rico")


##rep_2008 map
rep_2008_map <- ggplot() + 
  coord_map(xlim = c(-130, -60),
            ylim = c(20, 50)) + 
  geom_polygon(data = usa2, mapping = aes(x = long, y = lat, group = group),
               color = "black", fill = "white") +
  geom_point(data = rep_2008, aes(x = lon, y = lat),
             fill = "grey", color = "black", alpha = .2) +
  # strip out background junk and remove legend
  theme_void() +
  theme(legend.position = "none")

##dem_2008 map
dem_2008_map <- ggplot() + 
  coord_map(xlim = c(-130, -60),
            ylim = c(20, 50)) + 
  geom_polygon(data = usa2, mapping = aes(x = long, y = lat, group = group),
               color = "black", fill = "white") +
  geom_point(data = dem_2008, aes(x = lon, y = lat),
             fill = "grey", color = "black", alpha = .2) +
  # strip out background junk and remove legend
  theme_void() +
  theme(legend.position = "none")

##rep_2012 map
##dem_2012 map
##rep_2016 map
rep_2016_map <- ggplot() + 
  coord_map(xlim = c(-130, -60),
            ylim = c(20, 50)) + 
  geom_polygon(data = usa2, mapping = aes(x = long, y = lat, group = group),
               color = "black", fill = "white") +
  geom_point(data = rep_2016, aes(x = lon, y = lat),
             fill = "grey", color = "black", alpha = .2) +
  ggtitle("2016 Republican Party") + 
  # strip out background junk and remove legend
  theme_void() +
  theme(legend.position = "none")


##dem_2016 map
dem_2016_map <- ggplot() + 
  coord_map(xlim = c(-130, -60),
            ylim = c(20, 50)) + 
  geom_polygon(data = usa2, mapping = aes(x = long, y = lat, group = group),
               color = "black", fill = "white") +
  geom_point(data = dem_2016, aes(x = lon, y = lat),
             fill = "grey", color = "black", alpha = .2) +
  ggtitle("2016 Democratic Party") + 
  # strip out background junk and remove legend
  theme_void() +
  theme(legend.position = "none") 
  
##mering the two into one 
grid.arrange(rep_2016_map, dem_2016_map, nrow=1) 
pe2016 <- arrangeGrob(rep_2016_map, dem_2016_map, nrow=1) 
ggsave(file="pe2016.png", pe2016) 

###Word Frequency 

##########2016 election 
groupbyparty <- group_by(both_2016, democrat)
summarise(groupbyparty, protectionism=sum(protectionism))
##more protectionist words by Republican candidates

########Overall
groupbypartyyear <- speech%>%group_by(Year, democrat)%>%
  summarise(nprotectionism = sum(protectionism))

##graph
groupbypartyyear$democrat <- as.factor(groupbypartyyear$democrat)

disliketrade <- ggplot(data= groupbypartyyear, aes(x= democrat, y = nprotectionism, fill =democrat)) + 
  geom_bar(stat = "identity", width= 1) + 
  geom_text(mapping = aes(label = paste0(nprotectionism)), vjust = -0.5) +
  facet_wrap( ~ Year, strip.position = "bottom", scales = "free_x") +
  ggtitle("Partisan Commitment to Protectionismm") +
  xlab("Year") + ylab("Party") + theme_void() + theme(plot.title = element_text(hjust = 0.5)) +
    theme(panel.spacing = unit(0, "lines"),
          strip.background = element_blank(),
          strip.placement = "outside")

ggsave(file="disliketrade.png", disliketrade, width = 5, height =4) 
