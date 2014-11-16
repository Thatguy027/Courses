library(data.table)
library(MASS)
library(pamr)
library(dplyr)


LM <- data.frame(fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/Homework/HW5/lm.txt"))
LM <- LM[,-c(1,2)]
LM <- LM[,c(1:27)]


t <- numeric()
LM <- as.matrix(LM)
for (i in 1:nrow(LM)){
  t[i]<- (mean(LM[i,1:19])-mean(LM[i,20:27]))/sqrt(18*var(LM[i,1:19])/25+7*var(LM[i,20:27])/25)
}

LM <- cbind(LM,t)
LM <- LM[is.na(t)==F,]

library(MASS)

candidate<-LM[abs(LM[,28])>1,]

candidate1 <- matrix(0,0,27)
t <- sort(candidate[,28])

for (i in 1:nrow(candidate)){
  candidate1 <- rbind(candidate1,candidate[candidate[,28]==t[i],1:27])
}

co <- cor(candidate1)  ###correlation between samples
image(seq(1:27),1:27,co)


######discriminant analysis

class <- c(rep("B",19),rep("T",8))

candidate2 <-cbind(t(candidate1),class)
candidate2 <- data.frame(candidate2)


write.table(candidate2,"~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/Homework/HW5/candidate2.txt",quote=F,sep="\t",col.names=T,row.names=F)

candidate2<-read.table("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/Homework/HW5/candidate2.txt",header=T)


###linear/quadratic discriminant analysis using lda
tr<- sample(27,22)
tr <- sort(tr)
z <- lda(class~ .,candidate2,subset=tr)

zz <- lda(class~ .,candidate2,subset=tr,CV=T)
plot()
##z <- qda(class~ .,candidate2,subset=tr)

predictClass <- predict(z,candidate2[-tr,])$class
predictClass
class[-tr]


#### cross-validation, choose the number of genes which gives lowest error rat
error <- numeric()
for ( i in 1:200){
  cat("i=",i,"\n")
  tr<- sample(27,22)
  tr <- sort(tr)
  z <- lda(class~ .,candidate2,subset=tr)
  predictClass <- predict(z,candidate2[-tr,])$class
  error <- c(error,sum(predictClass!=class[-tr])) 
}

###test error
errorRate <- sum(error)/(27-length(tr))/length(error)



############## PAM
##Install

#install.packages("pamr")

##use PAM

library(pamr)

LM<-pamr.from.excel("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/Homework/HW5/lmSAMformat.txt",40)
#LM$x<-log2(LM$x)
#pamr.menu(LM)
LM.train <- pamr.train(LM)
LM.results <- pamr.cv(LM.train,LM,nfold=10)

##plot cross-validation result
pamr.plotcv(LM.results)
dev.off()

##plot cross-validated probabilites
pamr.plotcvprob(LM.results,LM, threshold=2.2)
dev.off()

##plot class centroids
pamr.plotcen(LM.train,LM,threshold=2)
dev.off()





















