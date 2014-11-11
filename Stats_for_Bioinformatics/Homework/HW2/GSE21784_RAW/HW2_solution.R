source("http://bioconductor.org/biocLite.R")
biocLite("affy")
library(affy)


setwd("~/Northwestern/Courses/Stats_for_Bioinformatics/Homework/HW2/GSE21784_RAW/")

pcpc <- ReadAffy()
sampleNames(pcpc) <- c("L41","L42","L43", "d61", "d62","d63","d151","d152","d153")
pData(pcpc)
# pc <- rma(pcpc)

pm(pcpc)[1:10,]

y <- log2(pm(pcpc)[,1])[1:5000]
x <- log2(pm(pcpc)[,2])[1:5000]
LO <- loess(y~x,span=0.3)

plot(x,y,main="array 1 vs array 2, array1 is baseline",xlab="array 2",ylab="array 1")
points(x,predict(LO),col=4,lwd=1)

df <- pm(pcp)

hist(pcpc[,1:3])

boxplot(pcpc,col=c(rep(2,3),rep(3,3),rep(4,3)))


###RNA degradation plot
deg <- AffyRNAdeg(pcpc[,1])
plotAffyRNAdeg(deg)    

###MVA plot
gn <- sample(geneNames(pcpc),100)       
pms <- pm(pcpc[,1:2],gn)
mva.pairs(pms)

###normalized plot

normalized.pcpc <- merge(normalize(pcpc[,1:3],method="loess"), 
                         normalize(pcpc[,4:6],method="loess"))

normalized.pcpc <- merge(normalized.pcpc, 
                         normalize(pcpc[,7:9],method="loess"))

boxplot(normalized.pcpc,col=c(rep(2,3),rep(3,3),rep(4,3)))



pc<-rma(pcpc)
pms<-exprs(pc)

## store the post-norm data into a matrix, each column corresponds to a array

mva.pairs(pms[,1:2])
x<-c(pms[,1],pms[,2])
y<-c(rep(1,length(x)/2),rep(2,length(x)/2))
boxplot(x~y,col=c(2,3))   ##bot plot of array 1 and 2 side by side., you can do more than 2 arrays.

biocLite("made4")
library(made4)

overview(pc)




