library(foreign)
#library(readtext)
library(stringr)
library(stm)
library(stats)
library(dplyr)
library(wordcloud)
library(ggplot2)

#setwd("~/Desktop/2018WINTER/PLSC43502/ML_finalPJT/Data/")
setwd("C:/Users/user/Desktop/ML_finalPJT/Data/")
alldf<-read.csv('alldf_w15_180306.csv')

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

col.lse <- function(mat) {
  matrixStats::colLogSumExps(mat)
}

calcfrex <- function(logbeta, w=.5, wordcounts=NULL) {
  excl <- t(t(logbeta) - col.lse(logbeta))
  if(!is.null(wordcounts)) {
    #if word counts provided calculate the shrinkage estimator
    excl <- safelog(sapply(1:ncol(excl), function(x) js.estimate(exp(excl[,x]), wordcounts[x])))
  } 
  freqscore <- apply(logbeta,1,data.table::frank)/ncol(logbeta)
  exclscore <- apply(excl,1,data.table::frank)/ncol(logbeta)
  frex <- 1/(w/freqscore + (1-w)/exclscore)
  apply(frex,2,order,decreasing=TRUE)
}


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
  
  return(list(result_frex, stm_labels, r_dt, r_theta, fit, out))
}

rust_sw <- run_stm(alldf_rust_sw, 45, 15)
rust_nosw <- run_stm(alldf_rust_nosw, 45, 15)
norust_sw <- run_stm(alldf_norust_sw, 45, 15)
norust_nosw <- run_stm(alldf_norust_nosw, 45, 15)
rust<-run_stm(alldf_rust,45,15)
norust<-run_stm(alldf_norust,45,15)
all<-run_stm(alldf_sw, 100, 15)
all_again<-run_stm(alldf_addsw, 100, 15)

write.csv(all_again[3], file = "../Result/STM/alldf_t100_w15_180307_1247.csv")
write.csv(all_again[4], file = "../Result/STM/alldf_t100_w15_180307_theta_1247.csv")

#        col = 'orange', cex.main =.9, ylim = c(-0,0.2))

barplot(norust_nosw_dem_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 5, for Dem in Non-Rustbelt & Non-Swing",
        col = 'blue', cex.main =.9, ylim = c(-0,0.2))

barplot(norust_nosw_rep_pro, #names.arg = c('T1','T2','T3','T4','T5','T6','T7','T8'),
        main="Topic 5,  for Rep Non-Rustbelt & Non-Swing",
        col = 'blue', cex.main =.9, ylim = c(-0,0.2))


dev.off()
