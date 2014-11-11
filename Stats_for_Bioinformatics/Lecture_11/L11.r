##generate the data
T <- matrix(c(0.95,0.1,0.05,0.95),2,2)
p0 <- rep(1/6,6)
p1 <- c(rep(1/10,5),0.5)

##stationary probability P(pi=0)=2/3, P(pi=1)=1/3

##generate the state path,starting with fair die
## 0 fair; 1:loaded

s <- numeric()
s[1] <- rbinom(1,1,1/3)

for (i in 1:1000){
  s <- c(s, (1-s[i-1])*rbinom(1,1,0.05)+s[i-1]*rbinom(1,1,0.9))
}

x <- numeric()
for (i in 1:1000){
  x <- c(x,(1-s[i])*sample(c(1:6),1,p=p0)+s[i]*sample(c(1:6),1,p=p1))
}

##################################################################
# Initial state transition probability is set as ab0=2/3, ab1=1/3
#
# The same for the ending probability.
##################################################################

### Viterbi algorithm finding the most proble path
v0 <- numeric()    ## v vector for state 0
v1 <- numeric()   ## v vector for state 1
pt0 <- c(0)
pt1 <- c(0)

##beginning
v0 <- c(v0,log2(2/3*p0[x[1]]))
v1 <- c(v1,log2(1/3*p1[x[1]]))

pt0[1] <- 0
pt1[1] <- 1

for (i in 2:length(x)){
  v0a00e0 <- v0[i-1]+log2(p0[x[i]])+log2(T[1,1])
  v1a10e0 <- v1[i-1]+log2(p0[x[i]])+log2(T[2,1])
  v1a11e1 <- v1[i-1]+log2(p1[x[i]])+log2(T[2,2]) 
  v0a01e1 <- v0[i-1]+log2(p1[x[i]])+log2(T[1,2])

  v0 <- c(v0,max(v0a00e0,v1a10e0))
  v1 <- c(v1,max(v0a01e1,v1a11e1))
  pt0[i] <- 0*(v0a00e0>v1a10e0)+1*(v0a00e0<v1a10e0)
  pt1[i] <- 0*(v0a01e1>v1a11e1)+1*(v0a01e1<v1a11e1)
}

##ending state
v0 <- c(v0,v0[i]+log2(2/3))
v1 <- c(v1,v1[i]+log2(1/3))

pt <- numeric()
pt[1] <- 0*(v0[i]+log2(2/3)>v1[i]+log2(1/3))+1*(v0[i]+log2(2/3)<v1[i]+log2(1/3))

##track back the states history

L <- length(pt1)-1
for (j in 1:L){
  pt <- c(pt,pt0[L-j+2]*(pt[j]==0)+pt1[L-j+2]*(pt[j]==1))
  }

pt <- rev(pt)

sum(s==pt)

plot(s-pt)


####################################
## background and forward algorithm
####################################

####forward
L <- length(x)
f0 <- numeric()
f1 <- numeric()
sc <- numeric()

sc[1] <- p0[x[1]]*2/3+p1[x[1]]*1/3
f0[1] <- p0[x[1]]*2/3/sc[1]
f1[1] <- p1[x[1]]*1/3/sc[1]

for (i in 2:L){
  sc <- c(sc,p0[x[i]]*(f0[i-1]*T[1,1]+f1[i-1]*T[2,1])+p1[x[i]]*(f0[i-1]*T[1,2]+f1[i-1]*T[2,2]))
  f0 <- c(f0,p0[x[i]]*(f0[i-1]*T[1,1]+f1[i-1]*T[2,1])/sc[i])
  f1<- c(f1,p1[x[i]]*(f0[i-1]*T[1,2]+f1[i-1]*T[2,2])/sc[i])
}
             
px <- f0[L]*2/3+f1[L]*1/3




####backward
             
b0 <- numeric(L)
b1 <- numeric(L)
b0[L] <- 2/3/sc[L]
b1[L] <- 1/3/sc[L]

for (i in (L-1):1){
  b0[i] <-T[1,1]*b0[i+1]*p0[x[i+1]]+T[1,2]*b1[i+1]*p1[x[i+1]]
  b1[i] <-T[2,1]*b0[i+1]*p0[x[i+1]]+T[2,2]*b1[i+1]*p1[x[i+1]]
  b0[i] <- b0[i]/sc[i]
  b1[i] <- b1[i]/sc[i]
}

###poscterior decoding
pc0 <- numeric()
pc1 <- numeric()
pt2 <- numeric()
for (i in 1:L){
  pc0 <- c(pc0,f0[i]*b0[i]*sc[i]/px)
  pc1 <- c(pc1,f1[i]*b1[i]*sc[i]/px)
  pt2 <- c(pt2,0*(pc0[i]>pc1[i])+1*(pc0[i]<pc1[i]))
}
           
             
sum(s==pt)
sum(s==pt2)

postscript("viterbiBF.ps",paper="letter",horizontal=T)
par(mfrow=c(4,1))
plot(s,type="l")
plot(pt,type="l")
plot(pc1,type="l")
plot(pt2,type="l")
dev.off()
