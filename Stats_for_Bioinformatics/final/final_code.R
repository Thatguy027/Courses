library(data.table)
library(stringr)
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
data <- test %>%
  filter(CONTROL_TYPE != "pos")

rm(expr,expr1,IDs,test,strains,strains1)
##### dev time course
#### at work
# expression data staged vs mixed sample
L2 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/L2_v_mixed-ref_edited.txt")
L3 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/L3_v_mixed-ref_edited.txt")
L4 <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/L4_v_mixed-ref_edited.txt")
ad <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/wtAdult_v_mixed-ref_edited.txt")
geneID <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/dev_tcourse_position-ID.txt")

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
############ combine data

L2L3 <- left_join(L2,L3,by="ID_REF")
L2L3L4 <- left_join(L2L3,L4,by="ID_REF")
devdat <- left_join(L2L3L4,ad,by="ID_REF")

devdat <- geneID%>%
  select(ID_REF = ID, ORF)%>%
  left_join(devdat, ., by = "ID_REF")%>%
  select(-ID_REF)

rm(L2,L3,L4,L2L3,L2L3L4,geneID,ad)

#### take the mean of probes that target same gene

mean2 <- function(x){
  mean(x,na.rm=TRUE)
}

data2 <- data%>%
  select(-CONTROL_TYPE,-SPOT_ID,-DESCRIPTION,-ROW,-COL,-SPOT,-CHROMOSOMAL_LOCATION,-ACCESSION_STRING, -ID)%>%
  unite(gene_seq, ORF,SEQUENCE,sep="_")%>%
  gather(strain, log2d, -gene_seq)

data2$log2d <- as.numeric(data2$log2d)

data3 <- data2%>%
  group_by(gene_seq,strain)%>%
  summarise(means = mean2(log2d))

#### only keep ORF that are the same in RIAILs and dev timecourse













