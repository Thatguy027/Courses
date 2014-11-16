
library(affy)
##pcpc <- ReadAffy(sampleNames=c("N1","N2","N3","N4","N5","N6","T1","T2","T3","T4","T5","T6")) ##Read in all affy data in the current directory

datadir <- "/Users/jon/stat465F14/class/AffyData/prostateCancer/classdata"
fnames <- dir(path=datadir, pattern=".CEL")
pcpc <- ReadAffy(filenames=fnames,celfile.path=datadir)

##pcpc<-ReadAffy()  this command will read all CEL files in the current directory.
##pcpc <- ReadAffy(widget=T) ##requires tkWidget package
##to install the tkWidgets packages:
##>source("http://www.bioconductor.org/biocLite.R")
##>biocLite("tkWidgets")


sampleNames(pcpc) <- c("N1","N2","N3","N4","N5","N6","T1","T2","T3","T4","T5","T6")
pc <- rma(pcpc)  ##robust microarray average, fast but less versertile
write.exprs(pc,"pstCancer.txt")

pc=read.table("pstCancer.txt")
boxplot(pc,col = c(rep(2, 6),rep(3, 6)))

### choose different methods in different steps.
#pcN <- expresso(pcpc,widget=T)

##pcN=expresso(pcpc, bgcorrect.method="rma",normalize.method="constant",pmcorrect.method="pmonly",summary.method="avgdiff")
        
###array sets information
phenoData(pcpc)
pData(pcpc)

##access PM and MM data
pm(pcpc)[1:10,]

##illustration of non-linear normalization in affy data
y <- log2(pm(pcpc)[,1])[1:5000]
x <- log2(pm(pcpc)[,2])[1:5000]
LO <- loess(y~x,span=0.3)
pdf("/Users/jon/stats465F12/L4/nonLinearNorm.pdf",horizontal=T)
plot(x,y,main="array 1 vs array 2, array1 is baseline",xlab="array 2",ylab="array 1")
points(x,predict(LO),col=4,lwd=5)
dev.off()

###image
hist(pcpc[,1:2])
par(mfrow=c(3,4))
image(pcpc)
boxplot(pcpc,col=c(rep(2,6),rep(3,6)))

###RNA degradation plot
deg <- AffyRNAdeg(pcpc[,1])
plotAffyRNAdeg(deg)        

###MVA plot
gn <- sample(geneNames(pcpc),100)       
pms <- pm(pcpc[,1:2],gn)
mva.pairs(pms)
        
###normalized plot

normalized.pcpc <- merge(normalize(pcpc[,1:6],method="loess"), normalize(pcpc[,7:12]),method="loess")
boxplot(normalized.pcpc, col = c(rep(2, 6),rep(3, 6)))

pms <- pm(pc[,1:2], gn)
mva.pairs(pms)


#####
boxplot(pcpc)
plot(pm(pcpc)[,1:2])
mva.pairs(pm(pcpc)[,1:2])
        
pc<-rma(pcpc)
pms<-exprs(pc)

## store the post-norm data into a matrix, each column corresponds to a array

mva.pairs(pms[,1:2])
x<-c(pms[,1],pms[,2])
y<-c(rep(1,length(x)/2),rep(2,length(x)/2))
boxplot(x~y,col=c(2,3))   ##bot plot of array 1 and 2 side by side., you can do more than 2 arrays.
