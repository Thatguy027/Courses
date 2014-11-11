LM<-read.table("~/stat465F12/L7/lm.txt",header=TRUE,sep="\t")
LM=LM[,-c(1,2)]

t=numeric()
LM <- as.matrix(LM)
for (i in 1:nrow(LM)){
  t[i]<- (mean(LM[i,1:27])-mean(LM[i,28:38]))/sqrt(26*var(LM[i,1:27])/36+10*var(LM[i,28:38])/36)
}

LM <- cbind(LM,t)
LM <-LM[is.na(t)==F,]

library(MASS)

candidate<-LM[abs(LM[,39])>1,]

candidate1 <- matrix(0,0,38)
t <- sort(candidate[,39])

for (i in 1:nrow(candidate)){
  candidate1 <- rbind(candidate1,candidate[candidate[,39]==t[i],1:38])
}

co <- cor(candidate1)  ###correlation between samples
image(seq(1:38),1:38,co)

######discriminant analysis

class <- c(rep("L",27),rep("M",11))

candidate2 <-cbind(t(candidate1),class)
candidate2 <- data.frame(candidate2)


write.table(candidate2,"~/stat465F14/L7/candidate2.txt",quote=F,sep="\t",col.names=T,row.names=F)

candidate2<-read.table("~/stat465F14/L7/candidate2.txt",header=T)


###linear/quadratic discriminant analysis using lda
tr<- sample(38,34)
tr <- sort(tr)
z <- lda(class~ .,candidate2,subset=tr)

##z <- qda(class~ .,candidate2,subset=tr)

predictClass <- predict(z,candidate2[-tr,])$class
predictClass
class[-tr]


#### cross-validation, choose the number of genes which gives lowest error rat
error <- numeric()
for ( i in 1:200){
  cat("i=",i,"\n")
  tr<- sample(38,34)
  tr <- sort(tr)
  z <- lda(class~ .,candidate2,subset=tr)
  predictClass <- predict(z,candidate2[-tr,])$class
  error <- c(error,sum(predictClass!=class[-tr])) 
}

###test error
errorRate <- sum(error)/(38-length(tr))/length(error)

############## PAM
##Install

#install.packages("pamr")

##use PAM

library(pamr)

LM<-pamr.from.excel("~/stat465F12/L9/lmSAMformat.txt",40)
#LM$x<-log2(LM$x)
#pamr.menu(LM)
LM.train <- pamr.train(LM)
LM.results <- pamr.cv(LM.train,LM,nfold=10)

##plot cross-validation result

postscript("LMcv.ps", paper="letter",horizontal=T)
pamr.plotcv(LM.results)
dev.off()

##plot cross-validated probabilites
postscript("LMprob.ps", paper="letter",horizontal=T)
pamr.plotcvprob(LM.results,LM, threshold=2.2)
dev.off()

##plot class centroids
postscript("LMcen.ps", paper="letter",horizontal=T)
pamr.plotcen(LM.train,LM,threshold=2)
dev.off()
