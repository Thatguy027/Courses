## next generation sequencing analysis using R
## using Bowtie

setwd("~/stat465F14/NGS/spombe")
fileIndex="."

refFiles=dir(".", pattern="*.fasta", full.names=TRUE)
refFiles

#[1] "./chromosome1.fasta" "./chromosome2.fasta"
#[3] "./chromosome3.fasta"

####################################################################
##      basic onscreen alignment, output only one alignment, default
## 	example 1: bowtie -v 2 -B 1 spombe -c AAGGAATCTTTTTCATCTCCGGTCATTTG

results=bowtie(sequences="AAGGAATCTTTTTCATCTCCGGTCATTTG",index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE)

## 	c stands for command line, B=1 index starting from position 1 and v=2 allows more more than two mismatches
## 	results
##  	[1] "0\t+\tchr3\t380089\tAAGGAATCTTTTTCATCTCCGGTCATTTG\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t0\t10:G>T"
####################################################################


####################################################################
##      basic onscreen alignment, output all alignment -a
##      example 2: bowtie -a -v 2 -B 1 spombe -c CAAAACATAAATAAATATTACAAAA

results=bowtie(sequences="CAAAACATAAATAAATATTACAAAA", index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE,a=TRUE)

##   a=TRUE means list all alignments.
##   > results
##   [1] "0\t+\tchr3\t15743\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"  
##   [2] "0\t+\tchr3\t4873\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"   
##   [3] "0\t-\tchr3\t2448379\tTTTTGTAATATTTATTTATGTTTTG\tIIIIIIIIIIIIIIIIIIIIIIIII\t0\t"
####################################################################

##########################################################################
##      basic onscreen alignment, output specified number of alignments -k
##      Example 3:  bowtie -k 2 -v 2 -B 1 spombe -c CAAAACATAAATAAATATTACAAAA

results=bowtie(sequences="CAAAACATAAATAAATATTACAAAA",k=2, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE)

##   k=2 means list only two alignments.
##   > results
##   [1] "0\t+\tchr3\t15743\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"
##   [2] "0\t+\tchr3\t4873\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t" 
####################################################################

####################################################################
##      basic onscreen alignment, suppress alignments that have more than m hits
##      Example 4:  bowtie -k 2 -v 2 -B 1 spombe -c CAAAACATAAATAAATATTACAAAA  -m 1

results1=bowtie(sequences="CAAAACATAAATAAATATTACAAAA",a=TRUE, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE,m=1)
results2=bowtie(sequences="CAAAACATAAATAAATATTACAAAA",a=TRUE, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE,m=2)
results3=bowtie(sequences="CAAAACATAAATAAATATTACAAAA",a=TRUE, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE,m=3)

##   m=1 means only report reads with 1 hit and etc, or only report unique mapping
##   > results3
##  [1] "0\t+\tchr3\t15743\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"  
##  [2] "0\t+\tchr3\t4873\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"   
##  [3] "0\t-\tchr3\t2448379\tTTTTGTAATATTTATTTATGTTTTG\tIIIIIIIIIIIIIIIIIIIIIIIII\t0\t"
####################################################################

####################################################################
##      basic onscreen alignment, multiple sequences from command line
##      Example 5:  bowtie -k 2 -v 2 -B 1 spombe -c CAAAACATAAATAAATATTACAAAA,AAGGAATCTTTTTCATCTCCGGTCATTTG  -a

results=bowtie(sequences=c("CAAAACATAAATAAATATTACAAAA","AAGGAATCTTTTTCATCTCCGGTCATTTG"),a=TRUE, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE)

##  put sequences in a vector
##  > results
##  [1] "0\t+\tchr3\t15743\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"               
##  [2] "0\t+\tchr3\t4873\tCAAAACATAAATAAATATTACAAAA\tIIIIIIIIIIIIIIIIIIIIIIIII\t1\t"                
##  [3] "0\t-\tchr3\t2448379\tTTTTGTAATATTTATTTATGTTTTG\tIIIIIIIIIIIIIIIIIIIIIIIII\t0\t"             
##  [4] "1\t+\tchr3\t380089\tAAGGAATCTTTTTCATCTCCGGTCATTTG\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t0\t10:G>T"
####################################################################


####################################################################
##     basic onscreen alignment, sort alignment based on quality
##     Example 6:  bowtie -a --best -v 2 -B 1 spombe -c TGATCTATTATATTACATTACACAGGTTA

results=bowtie(sequences="TGATCTATTATATTACATTACACAGGTTA",a=TRUE, best=TRUE, index=file.path(fileIndex,"index"), B=1,v=2, c=TRUE)

##  best=TRUE specifies ordering of quality in alignment
##  >results
##  [1] "0\t+\tchr1\t5325211\tTGATCTATTATATTACATTACACAGGTTA\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t1\t17:A>T"        
##  [2] "0\t+\tchr2\t2080991\tTGATCTATTATATTACATTACACAGGTTA\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t1\t17:A>T"        
##  [3] "0\t-\tchr3\t1401128\tTAACCTGTGTAATGTAATATAATAGATCA\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t0\t8:G>A"         
##  [4] "0\t+\tchr3\t1582044\tTGATCTATTATATTACATTACACAGGTTA\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t0\t3:C>T"         
##  [5] "0\t-\tchr1\t2854315\tTAACCTGTGTAATGTAATATAATAGATCA\tIIIIIIIIIIIIIIIIIIIIIIIIIIIII\t15\t17:T>A,28:C>T"
####################################################################

####################################################################
##     alignment using input file, paired end

##    Example 7: bowtie -m 1 -v 3 -B 1 --fr -f -1 ./examples/example7/read1.fa -2 ./examples/example7/read2.fa –p 4 spombe

Seq1Files=file.path(".", "examples","example7","read1.fa")
Seq2Files=file.path(".", "examples","example7","read2.fa")
outFileName=file.path(".", "examples","example7","paired_map_m1_v0_1.txt")

bowtie(sequences=list(Seq1Files,Seq2Files),type="paired",fr=TRUE, a=TRUE, best=TRUE,f=TRUE, index=file.path(fileIndex,"index"),B=1,v=2, outfile=outFileName,force=TRUE)

## sequences=list(Seq1Files,Seq2Files): list of two mate files
##   type="paired": paired reads
##   f=TRUE: fasta format
##   outfile: output file
##   force=TRUE: overide existing file if exists
####################################################################

####################################################################
##     alignment using input file in color space, single-end

##    example 8: bowtie -p 4 -m 1 -v 3 -B 1 -C spombeC --col-keepend -f ./examples/example8/reads.csfasta -Q ./examples/example8/reads.qual > ./examples/example8/col_map_m1_v3.txt


SeqFile=file.path(".", "examples","example8","reads.csfasta")
QualityFile=file.path(".", "examples","example8","reads.qual")
outFileName=file.path(".", "examples","example8","paired_map_m1_v3_1.txt")


bowtie(sequences=SeqFile,Q=QualityFile, m=1, C=TRUE, a=TRUE, best=TRUE, index=file.path(fileIndex,"spombeC"), f=TRUE, B=1,v=3, outfile=outFileName,force=TRUE)

## sequences=list(Seq1Files,Seq2Files): list of two mate files
##   type="paired": paired reads
##   f=TRUE: fasta format
##   outfile: output file
##   force=TRUE: overide existing file if exists
####################################################################

####################################################################
##     alignment using input file in color space, paired-end

##    example 9: bowtie -p 4 -m 1 -v 3  -B 1 -C spombeC  --col-keepend --fr -f -1 ./examples/example9/read1.csfasta  -2 ./examples/example9/read2.csfasta --Q1 ./examples/example9/read1.qual --Q2 ./examples/example9/read2.qual > ./examples/example9/paired_col_m1_v3.txt 

Seq1File=file.path(".", "examples","example9","read1.csfasta")
Seq2File=file.path(".", "examples","example9","read2.csfasta")

Quality1File=file.path(".", "examples","example9","read1.qual")
Quality2File=file.path(".", "examples","example9","read2.qual")

outFileName=file.path(".", "examples","example9","paired_map_m1_v3_1.txt")


bowtie(sequences=list(Seq1File,Seq2File), Q1=Quality1File,Q2=Quality2File,fr=TRUE, type="paired", m=1, C=TRUE, a=TRUE, best=TRUE, index=file.path(fileIndex,"spombeC"), f=TRUE, B=1,v=3, outfile=outFileName,force=TRUE)

## sequences=list(Seq1Files,Seq2Files): list of two mate files
##   type="paired": paired reads
##   f=TRUE: fasta format
##   outfile: output file
##   force=TRUE: overide existing file if exists
####################################################################
