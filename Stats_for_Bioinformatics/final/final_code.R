library(data.table)
library(stringr)
library(dplyr)
expr <- fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/2010rockman_riail_expression.txt")

strains <- colnames(data.frame(expr))

strains1 <- str_split_fixed(strains, pattern = "\\.", n=3)
strains1 <- strains1[,2]
strains1[1] <- "ID"

colnames(expr) <- strains1
expr1 <- data.frame(expr)

expr1 <- expr1%>%
  filter(ID != "ID_REF")

IDs <- data.frame(fread("~/Dropbox/AndersenLab/LabFolders/Stefan/Courses/Stats_for_Bioinformatics/final/gene_ID_array.txt"))

IDs <- IDs%>%
  filter(ID %in% expr$ID)

IDs$ID <- as.character(IDs$ID)

test <- left_join(expr1, IDs, by ="ID")

data <- test %>%
  filter(CONTROL_TYPE != "pos")


