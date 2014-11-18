library(data.table)
library(stringr)
library(CCA)
library(dplyr)

#### RIAILS
expr <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/2010rockman_riail_expression.txt")
expr <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/2010rockman_riail_expression.txt")


strains <- colnames(data.frame(expr))
strains1 <- str_split_fixed(strains, pattern = "\\.", n=3)
strains1 <- strains1[,2]
strains1[1] <- "ID"
colnames(expr) <- strains1
expr1 <- data.frame(expr)

expr1 <- expr1%>%
  filter(ID != "ID_REF")

# microarray setup
IDs <- data.frame(fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/gene_ID_array.txt"))
IDs <- data.frame(fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/gene_ID_array.txt"))

IDs <- IDs%>%
  filter(ID %in% expr$ID)
IDs$ID <- as.character(IDs$ID)

# combine array data with ID information
test <- left_join(expr1, IDs, by ="ID")
RILexp <- test %>%
  filter(CONTROL_TYPE != "pos")

rm(expr,expr1,IDs,test,strains,strains1)
##### dev time course
#### at work
# expression data staged vs mixed sample
T1 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP1_dev.txt")
T2 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP2_dev.txt")
T3 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP3_dev.txt")
T4 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP4_dev.txt")
T5 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP5_dev.txt")
T6 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP6_dev.txt")
T7 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP7_dev.txt")
T8 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP8_dev.txt")
T9 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP9_dev.txt")
T10 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP10_dev.txt")
T11 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP11_dev.txt")
T12 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/TP12_dev.txt")
devID <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/dev_geneID.txt")
### at home
# expression data staged vs mixed sample
T1 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP1_dev.txt")
T2 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP2_dev.txt")
T3 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP3_dev.txt")
T4 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP4_dev.txt")
T5 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP5_dev.txt")
T6 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP6_dev.txt")
T7 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP7_dev.txt")
T8 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP8_dev.txt")
T9 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP9_dev.txt")
T10 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP10_dev.txt")
T11 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP11_dev.txt")
T12 <- fread("~/Northwestern/Courses/Stats_for_Bioinformatics/final/TP12_dev.txt")
############ take means of 3 replicates of time course
mean2 <- function(x){
  mean(x,na.rm=TRUE)
}
############ 

meanCols <- function(df, tp, cols, gIDs){ 
  IDs <- select(gIDs, ID_REF = ID, ORF)
  temp <- as.data.frame(df)
  temp <- left_join(temp,IDs, by = "ID_REF")
  temp <- filter(temp, grepl(".",ORF))
  temp <- select(temp, -ID_REF)
  colnames(temp) <- c("rep1",  "rep2",  "rep3",	"ORF")
  temp <- temp %>%
    mutate(sums = rep1+rep2+rep3) %>%
    mutate(means = sums/cols)%>%
    select(means, ORF)
  colnames(temp) <- c(tp,"ORF")
  temp <- arrange(temp, ORF)
  return(temp)
}
### Calculate mean of three replicates for each timepoint measured
T1 <- meanCols(T1, tp = "T1", 3, devID)
T2 <- meanCols(T2, tp = "T2", 3, devID)
T3 <- meanCols(T3, tp = "T3", 3, devID)
T4 <- meanCols(T4, tp = "T4", 3, devID)
T5 <- meanCols(T5, tp = "T5", 3, devID)
T6 <- meanCols(T6, tp = "T6", 3, devID)
T7 <- meanCols(T7, tp = "T7", 3, devID)
T8 <- meanCols(T8, tp = "T8", 3, devID)
T9 <- meanCols(T9, tp = "T9", 3, devID)
T10 <- meanCols(T10, tp = "T10", 3, devID)
T11 <- meanCols(T11, tp = "T11", 3, devID)
T12 <- meanCols(T12, tp = "T12", 3, devID)
### join data sets together

devexp <- data.frame("ORF" = T1$ORF,
                   T1 = T1$T1,
                   T2 = T2$T2,
                   T3 = T3$T3,
                   T4 = T4$T4,
                   T5 = T5$T5,
                   T6 = T6$T6,
                   T7 = T7$T7,
                   T8 = T8$T8,
                   T9 = T9$T9,
                   T10 = T10$T10,
                   T11 = T11$T11,
                   T12 =T12$T12)

################################################### now we have mean data for all 12 timepoints of dev tcourse

rm(T1,T2,T3,T4,T5,T6,T7,T8,T9,T10,T11,T12,devID)

#### take the mean of probes that target same gene

data2 <- RILexp%>%
  select(-CONTROL_TYPE,-SPOT_ID,-DESCRIPTION,-ROW,-COL,-SPOT,-CHROMOSOMAL_LOCATION,-ACCESSION_STRING, -ID)%>%
  unite(gene_seq, ORF,SEQUENCE,sep="_")%>%
  gather(strain, log2d, -gene_seq)

data2$log2d <- as.numeric(data2$log2d)

data3 <- data2%>%
  group_by(gene_seq,strain)%>%
  summarise(means = mean2(log2d))

data3 <- data.frame(data3)
data4 <- spread(data3, key = strain, value = means)
# remove probes that don't have associated gene ID
data5 <- data4[566:nrow(data4),]
# remove 3 probes that have two "_" in the gene name
data6 <- data5%>%
  filter(!grepl("CE7X_3.1|CE7X_3.2|E_BE45912.2", gene_seq))
# split gene_seq column in order to filter both data sets to contain ORF
data7 <- data6 %>%
  separate(gene_seq, into = c("gene","seq"), sep = "_")
#### only keep ORF that are the same in RIAILs and dev timecourse
data8 <- data7 %>%
  filter(gene %in% devexp$ORF)%>%
  distinct(gene)
  
devexp1 <- devexp %>%
  filter(ORF %in% data8$gene) %>%
  distinct(ORF)

#################################
rm(data2,data3,data4,data5,data6,data7,devexp, df,RILexp,seq,stocks,stocksm)


X <- as.matrix((data8[,3:ncol(data8)]))
Y <- as.matrix((devexp1[,2:ncol(devexp1)]))

cc1 <- cc(X,Y)
cc2 <- comput(X, Y, cc1)
cc2[3]

conv1_2 <- data.frame(cv1 = cc2[[3]][,1], cv2 = cc2[[3]][,2])

plot(conv1_2[,1],conv1_2[,2])








