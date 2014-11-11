
#######
###permutaiton test
#####
x<-c(7.7,7.67,7.58,7.56,7.39,7.55,7.20,7.32,7.40,7.10,7.32,7.42)
T0 <-  (mean(x[1:6])-mean(x[7:12]))/sqrt(var(x[1:6])*.5+var(x[7:12])*.5)/sqrt(1/3)
Tstat <- numeric()
for ( i in 1:20000){
  sam <- sample(x,12,replace=F)
  T1 <- (mean(sam[1:6])-mean(sam[7:12]))/sqrt(var(sam[1:6])*.5+var(sam[7:12])*.5)/sqrt(1/3)
  Tstat <- c(Tstat,T1)
}
p <- 2*sum(Tstat>T0)/20000

hist(Tstat, col=2)

#############################################################################
#This R codes demonstrate how to use multtest to test differential expression
##############################################################################

setwd("/Users/jon/stat465S11/class/AffyData/prostateCancer/classdata")

library(affy)
pcpc <- ReadAffy()
pc <- rma(pcpc)  ##robust microarray average, fast but less versertile
write.exprs(pc,"pstCancer.txt")

pcnorm <- read.table("pstCancer.txt",sep="\t",skip=1)

colnames(pcnorm)<-c("gene","N01", "N02", "N03", "N04", "N05", "N06", "T01",  "T02", "T03",  "T04",  "T05",  "T06")


#######use mlttest procedure
library(multtest)
pcnorm[1:10,1:10]  ##prostate cancer data

###assigning the treatment label to pcnorm.cl
pcnorm.cl <-c(rep(0,6),rep(1,6))

###calcuate the teststat
teststat <- mt.teststat(pcnorm[,2:13],test="t.equalvar",pcnorm.cl)   ###default is t test.

###calculate raw p-value
rawp0<-2*(1-pt(abs(teststat),df=10))       
procs <- c("Bonferroni", "Holm", "Hochberg", "SidakSS", "SidakSD","BH", "BY")

###adjust p-value by different methods
res <- mt.rawp2adjp(rawp0, procs)

####sort the adjusted p-value to original order
adjp <- res$adjp[order(res$index), ]

###round the adjusted p-value to the second decimal places
adjp <- round(adjp[1:10, ], 2)


###permutation based

resT <- mt.maxT(pcnorm[,2:13],pcnorm.cl,B=2000) #pvalue is in decreasing order
ord <- order(res$index)  ##recover to original gene order
rawp <- resT$rawp[ord]   ##raw pvalue from permutation test
maxT <- resT$adjp[ord]   ##adjusted p-value from permutation test







####significant analysis
library(siggenes)
samR <- sam(pcnorm[2:103],pcnorm.cl)
