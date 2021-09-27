
## use "source( 'scatterBoxPlot.r' )"  from R prompt or "R -f scatterBoxPlot.r" from command line.
tab1 <- read.csv(file="IPCC-AR5-WGII-Chap21SM_scatter.csv",head=TRUE,sep=",",na.strings=c("NA"))
#n,T,pr,Model,Activity,Scenario,Region,Label,Mask,Season,Year

## or X11(type="Xlib")
jpeg('scatterBox.jpg', width=9., height=7., units="cm", res=1200)
par("mar")
par(
  mar      = c(2, 3, 4, 2),
  xaxs     = "i",
  yaxs     = "i",
  cex.axis = 0.35,
  cex.main = 0.5,
  cex.lab  = 0.75
)
par(mgp = c(4.2, .8, 0))
boxplot(pr~Scenario, data=tab1, notch=FALSE, ylim=c(0,6),
   subset = Label == "EAF" & Season == "DJF",
   col=(c("gold","blue","darkgreen")),
   main="Precipitation spread over models\n(change: 2071-2100 relative to 1961-1990)\nRegion: East Africa; Season: DJF")

dev.off()
