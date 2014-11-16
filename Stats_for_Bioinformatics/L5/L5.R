## HCL with R

yeast<-read.table("/Users/jon/stat465F14/class/cDNAdata/yeastCellCycle/yeastCellCycle_subset.csv",sep=",",header=TRUE,fill=TRUE)
indi<-apply(yeast[,2:19],1,sum)
yeast<-yeast[is.na(indi)==F,]

yeast1=yeast[,2:19]
row.names(yeast1)=yeast[,1]

dd <- as.dist((1 - cor(t(yeast1)))/2)
hc=hclust(dd)

plot(hc) # to see a dendrogram of clustered variables

## cut tree
memb <- cutree(hc, k = 10)
cluster1=yeast1[memb==2,]
heatmap(as.matrix(cluster1))



###read in data and delete rows with NA observations

yeast<-read.table("/Users/jon/stat465F14/class/cDNAdata/yeastCellCycle/yeastCellCycle.txt",sep="\t",header=TRUE,fill=TRUE)
#yeast <- yeast[-1,]
yeast<-as.matrix(yeast[,c(70:83)])

##time in unit of 30 minutes

T <- seq(0:13)

##indi is a indicator vector for whether any gene has missing values, if so, delete

indi<-apply(yeast,1,sum)
yeast<-yeast[is.na(indi)==F,]
yeastraw <- yeast

#standardize <- function(x){
#  x <- (x-mean(x))/sd(x)
#}
###standardize the data
#yeast=apply(yeast,2,standardize)



##############
##principle component analysis
eigenResult <- eigen(var(yeast))     ## Eigen analysis
eigenVector <- eigenResult$vectors   ##extract Eigen vectors
p1 <- eigenVector[,1]                ## first eigen vector
p2 <- eigenVector[,2]                ## second eigen vector
PCA1 <- yeast%*%p1                  ## convert to principal component 1
PCA2 <- yeast%*%p2                 ## convert to principal component 2
plot(PCA1,PCA2)
plot(eigenResult$values/sum(eigenResult$values))

##singular value decomposition
SVDResult <- svd(yeast)
plot(SVDResult$v[,2],type="b")
par(mfrow=c(4,4))

for (i in 1:ncol(SVDResult$v)){
  plot(SVDResult$v[,i],type="b",col=i)
}


#image(SVDResult$v)
##kmeans procedure
KmsYeast <- kmeans(yeast,6)
##
Yeast2 <- cbind(yeast,PCA1,PCA2,KmsYeast$cluster)
plot(PCA1,PCA2,type="n")

for (i in 1:6){
  points(PCA1[Yeast2[,17]==i],PCA2[Yeast2[,17]==i],col=i)
}





####k-means for iris data

iris.data <- read.table("~/mixture359/iris.data")

irisKmeans<-kmeans(iris.data[,1:4],centers=3)
iris.data <- cbind(iris.data,irisKmeans$cluster)


S <- var(iris.data[,1:4])        ## using sample variance for principal component analysis
eigenResult <- eigen(S)  ## Eigen analysis
eigenVector <- eigenResult$vectors   ##extract Eigen vectors
p1 <- eigenVector[,1]                ## first eigen vector
p2 <- eigenVector[,2]                ## second eigen vector
PCA1 <- as.matrix(iris.data[,1:4])%*%p1                 ## convert to principal component 1
PCA2 <- as.matrix(iris.data[,1:4])%*%p2                 ## convert to principal component 2


iris.data<-cbind(iris.data,PCA1,PCA2)
plot(PCA1,PCA2,type="n")

cluster1 <- iris.data[iris.data[,6]==1,]
cluster2 <- iris.data[iris.data[,6]==2,]
cluster3 <- iris.data[iris.data[,6]==3,]


cluster10<- iris.data[iris.data[,5]=="setosa",]
cluster20<- iris.data[iris.data[,5]=="versicolor",]
cluster30<- iris.data[iris.data[,5]=="virginica",]

points(cluster1[,7],cluster1[,8],col=1,pch="a")
points(cluster2[,7],cluster2[,8],col=2,pch="b")
points(cluster3[,7],cluster3[,8],col=3,pch="c")

points(cluster10[,7],cluster10[,8],pch="1",cex=1.5)
points(cluster20[,7],cluster20[,8],pch="2",cex=1.5)
points(cluster30[,7],cluster30[,8],pch="3",cex=1.5)


plot(PCA1,PCA2)                      ## plot the data with the first two PCAs

##plot in different color and differnt symbol

plot(PCA1[1:50], PCA2[1:50],col=1,xlim=c(min(PCA1),max(PCA1)),ylim=c(min(PCA2),max(PCA2)),pch=1 )
points(PCA1[51:100], PCA2[51:100],col=2,pch=2)
points(PCA1[101:150], PCA2[101:150],col=3,pch=3)


