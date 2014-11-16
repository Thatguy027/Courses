





yeast <- read.table("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/Homework/HW4/yst_cell_cycle.txt",
                    fill=T,header=T, sep="\t")
colnames(yeast) <- c("gene",colnames(yeast[,2:83]))


cdc28 <- yeast%>%
  select( contains("cdc28"))%>%
  select(-cdc28)
row.names(cdc28) <- yeast[,1]
cdc28 <- na.omit(cdc28)


dd <- as.dist((1 - cor(t(cdc28),use = "pairwise.complete.obs"))/2)
hc=hclust(dd)
plot(hc)

## cut tree
memb <- cutree(hc, k = 5)
cluster1<-cdc28[memb==2,]
heatmap(as.matrix(cluster1))

#### k-means

##############
##principle component analysis
eigenResult <- eigen(var(cdc28))     ## Eigen analysis
eigenVector <- eigenResult$vectors   ##extract Eigen vectors
p1 <- eigenVector[,1]                ## first eigen vector
p2 <- eigenVector[,2]                ## second eigen vector

cdc28m <- as.matrix(cdc28)
PCA1 <- cdc28m%*%p1                  ## convert to principal component 1
PCA2 <- cdc28m%*%p2                 ## convert to principal component 2
plot(PCA1,PCA2)
plot(eigenResult$values/sum(eigenResult$values))

View(eigenResult$values/sum(eigenResult$values))

varcomp <- data.frame(varexp = eigenResult$values/sum(eigenResult$values))
varcomp <- arrange(varcomp,varexp)
varcomp$expl <- cumsum(varcomp$varexp)


#image(SVDResult$v)
##kmeans procedure
KmsYeast <- kmeans(cdc28,17)
##
Yeast2 <- cbind(cdc28,PCA1,PCA2,KmsYeast$cluster)
plot(PCA1,PCA2,type="n")

for (i in 1:13){
  points(PCA1[Yeast2[,20]==i],PCA2[Yeast2[,20]==i],col=i)
}


```{r}
Yeast2$gene <- row.names(Yeast2)

mcdc28 <- melt(Yeast2, id.vars=c("gene","KmsYeast$cluster"))
colnames(mcdc28) <- c("gene","cluster","time","value")
ggplot(mcdc28)+
  aes(y=gene, x=time, fill=scale(value))+
  scale_fill_gradientn(colours = topo.colors(3))+
  geom_tile()+
  facet_grid(cluster~.)+
  theme(axis.ticks = element_blank(), axis.text.y = element_blank())
```





