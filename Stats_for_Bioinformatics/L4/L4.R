
setwd("~/stat465F14/class/AffyData/prostateCancer/data")
pcnorm <- read.table("pstCancer.txt",sep="\t",skip=0,header=T)

#######use mlttest procedure

library(multtest)
pcnorm[1:10,1:10]  ##prostate cancer data

###assigning the treatment label to pcnorm.cl
pcnorm.cl <-c(rep(0,50),rep(1,52))

###calcuate the teststat
teststat <- mt.teststat(pcnorm[,1:102],pcnorm.cl)

###calculate raw p-value
rawp0<-2*(1-pt(abs(teststat),df=100))       
procs <- c("Bonferroni", "Holm", "Hochberg", "SidakSS", "SidakSD","BH", "BY")

###adjust p-value by different methods
res <- mt.rawp2adjp(rawp0, procs)

####sort the adjusted p-value to original order
adjp <- res$adjp[order(res$index), ]

###round the adjusted p-value to the second decimal places
round(adjp[1:10, ], 2)

###permutation based

resT <- mt.maxT(pcnorm[,1:102],pcnorm.cl,B=2000) #pvalue is in decreasing order
ord <- order(res$index)  ##recover to original gene order
rawp <- resT$rawp[ord]   ##raw pvalue from permutation test
maxT <- resT$adjp[ord]   ##adjusted p-value from permutation test

################
together <- cbind(adjp,rawp,maxT)


####significant analysis
library(samr)
setwd("~/stat465F14/class/AffyData/prostateCancer/data")
pcnorm <- read.table("pstCancer.txt",sep="\t",skip=0,header=T)

##in the pscancer data, I have 50 normal arrays and 52 cancer array, I create a label to
##represent the 102 arrays, condition 1 as "1" and condition 2 as "2"

y=c(rep(1,50),rep(2,52))

##SAMR requires a special input format as a list of data table and response
d=list(x=pcnorm,y=y,geneid=as.character(1:nrow(pcnorm)),genenames=paste("g",as.character(1:nrow(pcnorm)),sep=""), logged2=TRUE)
sam.pc=samr(d,resp.type="Two class unpaired")

##this function computes the false discovery rate under different delta
##[16,] 0.694788996     398.9769505        1676.1929347     8118 0.0491471976  0.2064785581 -8.506468e-01 1.4715555
pc.delta=samr.compute.delta.table(samr.obj=sam.pc, min.foldchange=0, dels=NULL, nvals=50)

##list of significant genes under the selected delta cutoff
pc.sig=samr.compute.siggenes.table(samr.obj=sam.pc,delta.table=pc.delta,del=0.69,data=d)
pc.sigGenes=pc.sig[[1]]
##output the table
write.table(pc.sigGenes,file="sigGenes.pcnorm.samr.txt")
##plot the sam curve
samr.plot(samr.obj=sam.pc,del=0.69)
