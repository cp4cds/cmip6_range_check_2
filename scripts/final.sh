tables=(fx Ofx Lmon LImon SImon Omon Amon)

## day
#vars=(huss pr psl sfcWind tasmax tasmin tas)
## done: tas, tasmax
## tasmin, huss
## pr psl sfcWind

## Amon
atmos_vars=(tas ts tasmax tasmin psl ps uas vas sfcWind hurs huss pr prsn evspsbl tauu tauv hfls hfss rlds rlus rsds rsus rsdt rsut rlut clt ta ua va hur hus zg)
atmos_vars2="tas ts tasmax tasmin psl ps uas vas sfcWind hurs huss pr prsn evspsbl tauu tauv hfls hfss rlds rlus rsds rsus rsdt rsut rlut clt"
atmos_vars3="ta ua va hur hus zg"

# done
# tas, ta
# tasmax, ts
# tasmin, psl, ps
# uas, vas, sfcWing

##SImon.siconc  SImon.simass  SImon.sitemptop  SImon.sithick
##mon.clt      Amon.hur   Amon.pr    Amon.rlds  Amon.rsdt     Amon.ta      Amon.tauu  Amon.uas  day.pr       day.tasmax 
## fx.sftgif  Lmon.mrro      Ofx.sftof  SImon.siconc
## day.pr       day.tasmax  day.psl day.tasmin  day.sfcWind  day.tas day.huss
##Amon.evspsbl  Amon.hurs  Amon.prsn  Amon.rlus  Amon.rsus     Amon.tas     Amon.tauv  Amon.va   day.psl      day.tasmin  fx.sftlf   Lmon.mrsos     Omon.sos   SImon.simass
##Amon.hfls     Amon.hus   Amon.ps    Amon.rlut  Amon.rsut     Amon.tasmax  Amon.ts    Amon.vas  day.sfcWind  fx.mrsofc   LImon.snd  Ofx.areacello  Omon.tos   SImon.sitemptop
##Amon.hfss     Amon.huss  Amon.psl   Amon.rsds  Amon.sfcWind  Amon.tasmin  Amon.ua    day.huss  day.tas      fx.orog     LImon.snw  Ofx.deptho     Omon.zos   SImon.sithick

##day.huss  day.pr  day.psl  day.sfcWind  day.tas  day.tasmax  day.tasmin
vars=(tas ts tasmax tasmin psl ps uas vas sfcWind hurs huss pr prsn evspsbl tauu tauv hfls hfss rlds rlus rsds rsus rsdt rsut rlut clt ta ua va hur hus zg)

vars=(areacella mrsofc sftlf sftgif orog areacello deptho sftof)
tables=(fx fx fx fx fx Ofx Ofx Ofx)

## ocean: Omon.sos  Omon.tos  Omon.zos
## Lmon.mrro  Lmon.mrsos LImon.snd  LImon.snw

for v in $atmos_vars2
  do
    python jprep_ranges.py -v Amon.$v
  done
##python consol_to_json.py -d sh_05/Amon.vas
##python consol_to_json.py -d sh_05/Amon.sfcWind
