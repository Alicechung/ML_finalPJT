library(foreign)
library(readtext)
library(stringr)
library(stm)
library(stats)
library(dplyr)
library(wordcloud)
library(ggplot2)

setwd("~/Desktop/2018WINTER/PLSC43502/ML_finalPJT/Data/")
alldf<-read.csv('alldf_covariates_adddtm.csv')

alldf_addsw <-alldf%>%mutate(swing = ifelse((Year==2008&swing_last_08 <= 0.05)|
                                              (Year==2012&swing_last_12 <= 0.05)|
                                              (Year==2016&swing_last_16 <= 0.05), 1, 0))

alldf_sw<-subset(alldf_addsw, (!is.na(alldf_addsw$swing)))

alldf_rust<-subset(alldf_sw, alldf_sw$Rustbelt == 1)
alldf_norust<-subset(alldf_sw, alldf_sw$Rustbelt == 0)

alldf_norust_nosw<-subset(alldf_norust, alldf_norust$swing == 0)
alldf_norust_sw<-subset(alldf_norust, alldf_norust$swing == 1)

alldf_rust_nosw<-subset(alldf_rust, alldf_rust$swing == 0)
alldf_rust_sw<-subset(alldf_rust, alldf_rust$swing == 1)

# Rustbelt
run_stm<-function(df, topicnum, wordnum){
  processed <- textProcessor(df$Clean,
                            removestopwords = T, removenumbers = T, 
                             lowercase = T, removepunctuation = T)
  
  out<- prepDocuments(processed$documents, processed$vocab, 
                               processed$meta)
  fit <- stm(out$documents, out$vocab 
                          , K=topicnum
                          , emtol = 0.00001
                          , seed = 12345
                          , verbose = F)
  stm_labels <- labelTopics(fit, n = wordnum, topics = 1:topicnum)
  
  result_frex <- stm_labels$frex
  r_dt <- as.data.frame(result_frex)
  r_theta <- data.frame(fit$theta)
  
  return(list(result_frex, stm_labels, r_dt, r_theta, fit))
}

rust_sw <- run_stm(alldf_rust_sw, 45, 15)
rust_nosw <- run_stm(alldf_rust_nosw, 45, 15)
norust_sw <- run_stm(alldf_norust_sw, 45, 15)
norust_nosw <- run_stm(alldf_norust_nosw, 45, 15)
rust<-run_stm(alldf_rust,45,15)
norust<-run_stm(alldf_norust,45,15)

#write.csv(norust_nosw[3], file = "../Result/STM/alldf_norust_nosw_t45_w15_180302.csv")
#write.csv(norust_nosw[4], file = "../Result/STM/alldf_norust_nosw_t45_w15_180302_theta.csv")

#plot(fit_10_sw, type = "summary", xlim = c(0, .3))
#labeltype = c("prob", "frex", "lift", "score")

plot(rust_sw[[5]], type = "perspective", topics = c(1, 34),
     labeltype = "frex", n = 30)

#jpeg("../Result/Plots/word_cloud_rust_nosw.png")
png("../Result/Plots/word_cloud_norust_nosw.png", width = 8, height = 8, 
    units = 'in', res = 300)
pal2 <- brewer.pal(7,"GnBu")
par(bg="black") 
cloud(norust_nosw[[5]], topic = 5, scale = c(6,.8), colors=pal2,random.order=FALSE)
#ggsave("../ML_finalPJT/Result/Plots/test.png", width = 14, height = 14, dpi = 300)
dev.off() 
#dev.off()

#nonrust_sw<-read.csv('../Result/alldf_norust_sw_t45_theta.csv')
#nonrust_nosw<-read.csv('../Result/alldf_norust_nonsw_t45_theta.csv')

stmdf_nonrust_sw<- cbind(alldf_norust_sw1$PartyID, alldf_norust_sw1$Year, nonrust_sw)

stmdf_nonrust_nonsw<- cbind(alldf_norust_sw0$PartyID, alldf_norust_sw0$Year, nonrust_nosw)

norust_sw_dem_res <- subset(stmdf_nonrust_sw, stmdf_nonrust_sw$`alldf_norust_sw1$PartyID` == "Dem")
norust_sw_dem_pro <- colMeans(norust_sw_dem_res[4:48])

norust_sw_rep_res <- subset(stmdf_nonrust_sw, stmdf_nonrust_sw$`alldf_norust_sw1$PartyID` == "Rep")
norust_sw_rep_pro <- colMeans(norust_sw_rep_res[4:48])

norust_nosw_dem_res <- subset(stmdf_nonrust_nonsw, stmdf_nonrust_nonsw$`alldf_norust_sw0$PartyID` == "Dem")
norust_nosw_dem_pro <- colMeans(norust_nosw_dem_res[4:48])

norust_nosw_rep_res <- subset(stmdf_nonrust_nonsw, stmdf_nonrust_nonsw$`alldf_norust_sw0$PartyID` == "Rep")
norust_nosw_rep_pro <- colMeans(norust_nosw_rep_res[4:48])

#jpeg("../Result/plots.png")
par(mfrow=c(2,2))

barplot(norust_sw_dem_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 36, for Dem in Non-Rustbelt & Swing",
        col = 'orange', cex.main =.9, ylim = c(-0,0.2))

barplot(norust_sw_rep_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 36, for Rep Non-Rustbelt & Swing",
        col = 'orange', cex.main =.9, ylim = c(-0,0.2))

barplot(norust_nosw_dem_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 5, for Dem in Non-Rustbelt & Non-Swing",
        col = 'blue', cex.main =.9, ylim = c(-0,0.2))

barplot(norust_nosw_rep_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 5,  for Rep Non-Rustbelt & Non-Swing",
        col = 'blue', cex.main =.9, ylim = c(-0,0.2))


dev.off()
