tables=(fx Ofx Lmon LImon SImon Omon Amon)

## day
#vars=(huss pr psl sfcWind tasmax tasmin tas)
## done: tas, tasmax
## tasmin, huss
## pr psl sfcWind

## Amon
atmos_vars="tas ts tasmax tasmin psl ps uas vas sfcWind hurs huss pr prsn evspsbl tauu tauv hfls hfss rlds rlus rsds rsus rsdt rsut rlut clt ta ua va hur hus zg"
atmos_vars2="tas ts tasmax tasmin psl ps uas vas sfcWind hurs huss pr prsn evspsbl tauu tauv hfls hfss rlds rlus rsds rsus rsdt rsut rlut clt"
atmos_vars3="ua"
atmos_vars3="ta ua va hur hus zg"

day_vars="day.huss  day.pr  day.psl  day.sfcWind  day.tas  day.tasmax  day.tasmin"
misc_vars="Omon.sos  Omon.tos  Omon.zos SImon.siconc  SImon.simass  SImon.sitemptop  SImon.sithick Lmon.mrro  Lmon.mrsos LImon.snd  LImon.snw"


## ocean: Omon.sos  Omon.tos  Omon.zos
## Lmon.mrro  Lmon.mrsos LImon.snd  LImon.snw

fx_vars="fx.areacella fx.mrsofc fx.sftlf fx.sftgif fx.orog Ofx.areacello Ofx.deptho Ofx.sftof"

for v in $atmos_vars2
  do
    python jprep_ranges.py -v Amon.$v
  done
##python consol_to_json.py -d sh_05/Amon.vas
##python consol_to_json.py -d sh_05/Amon.sfcWind
