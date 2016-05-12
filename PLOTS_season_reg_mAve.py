import scipy.io.netcdf as NC
import numpy as np
import os
from commons.time_interval import TimeInterval
from basins.region import Region, Rectangle

from instruments import bio_float
from instruments.var_conversions import FLOATVARS

from basins import OGS
import pylab as pl

import time
import scipy.integrate as integrate

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

TI1 = TimeInterval('20130101','20160301','%Y%m%d')
#reg1 = OGS.P
#reg_sn = OGS.P.basin_list
#reg1 = OGS.lev
#reg1 = OGS.P
#reg_sn = 'nwm'
#reg1 = [OGS.lev]
#reg_sn = ['lev']
#reg_sn = ['alb','sww','swe','nwm','tyr','adn','ads','aeg','ion','lev','med']
reg1 = [OGS.alb,OGS.sww,OGS.swe,OGS.nwm,OGS.tyr,OGS.adn,OGS.ads,OGS.aeg,OGS.ion,OGS.lev]
reg_sn = ['alb','sww','swe','nwm','tyr','adn','ads','aeg','ion','lev']
#reg_sn = ['tyr','adn','ads','aeg','ion','lev']
#reg1 = [OGS.tyr,OGS.adn,OGS.ads,OGS.aeg,OGS.ion,OGS.lev]
RR = 6371.
reg1 = [OGS.ion,OGS.lev]
reg_sn = ['ion','lev']
#reg1 = [OGS.nwm,OGS.tyr,OGS.adn,OGS.ads,OGS.aeg,OGS.ion,OGS.lev]
#reg_sn = ['nwm','tyr','adn','ads','aeg','ion','lev']
#reg1 = [OGS.nwm]
#reg_sn = ['nwm']
#reg1 = [OGS.ads]
#reg_sn = ['ads']
tt_reg = np.zeros((len(reg_sn),), np.float64)
dd_reg = np.zeros((len(reg_sn),), np.float64)
n_floats = np.zeros(((len(reg_sn)),), np.int)
n_profiles = np.zeros(((len(reg_sn)),), np.int)

modelvarname1='P_i'

#for i,p in enumerate(OGS.P.basin_list):
for i,p in enumerate(reg1):
  fl = reg_sn[i]
#for i,fl in enumerate(reg_sn):
#  Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname1],TI1,fl)
#  Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname1],TI1,reg1)
  Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname1],TI1,p)
#  nP = len(Profilelist_1)
#  Lon = np.zeros((nP,), np.float64)
#  Lat = np.zeros((nP,), np.float64)
#  LonR = np.zeros((nP,), np.float64)
#  LatR = np.zeros((nP,), np.float64)
#  DCM = np.zeros((nP,), np.float64)
#  Max_Depth = np.zeros((nP,), np.float64)
#  integral_chla = np.zeros((nP,), np.float64)
  Tim = []
  Summer_list = []
  Winter_list = []
#  P_month = np.zeros((nP,), np.int)
#  Nam = np.zeros((nP,), np.int)
#  F1_cycle = np.zeros((nP,), np.int)
#  All_Profiles = np.zeros((nP,201), np.float64)
#  integral_CumulativeSum =  np.zeros((200,), np.float64)
#  fig=pl.figure(i)
 
#  MEAN1 = np.zeros((201,), np.float64)
#  STD1 = np.zeros((201,), np.float64)

  S1=set()
  for k in Profilelist_1: S1.add( k.name() )
  S1list=list(S1)
  nS1=len(S1list)
  snS1=str(nS1)

  for w in Profilelist_1 :
    if (w.time.month <=3) | (w.time.month >=10) :
       Winter_list.append(w)
    else :
       Summer_list.append(w)

# CREATE A DOUBLE LOOP ON LISTS:
# LOOP 1: WINTER
# LOOP 2: SUMMER

#  LOOP = 1
  for LOOP in range(1,3) :
   if LOOP == 1:
       season_list = Winter_list
       print 'WINTER'
   if LOOP == 2:
       season_list = Summer_list
       print 'SUMMER'

#  for ip, p in enumerate(Profilelist_1):
#########################################
   nP = len(season_list)
   Lon = np.zeros((nP,), np.float64)
   Lat = np.zeros((nP,), np.float64)
   LonR = np.zeros((nP,), np.float64)
   LatR = np.zeros((nP,), np.float64)
   DCM = np.zeros((nP,), np.float64)
   Max_Depth = np.zeros((nP,), np.float64)
   integral_chla = np.zeros((nP,), np.float64)
   P_month = np.zeros((nP,), np.int)
   Nam = np.zeros((nP,), np.int)
   F1_cycle = np.zeros((nP,), np.int)
   All_Profiles = np.zeros((nP,201), np.float64)
   integral_CumulativeSum =  np.zeros((200,), np.float64)
   fig=pl.figure(i)

   MEAN1 = np.zeros((201,), np.float64)
   STD1 = np.zeros((201,), np.float64)
#########################################
   for ip, pp in enumerate(season_list):
    Lon[ip] = pp.lon
    Lat[ip] = pp.lat
    LonR[ip] = np.pi/180.*pp.lon
    LatR[ip] = np.pi/180.*pp.lat
    Tim.append( pp.time.date() )
#    P_month[ip]=p.time.month
# SPRING-SUMMER
#    P_ss = (P_month>3) & (P_month<10)
# AUTUMN-WINTER
#    P_aw = (P_month<=3) | (P_month>=10)

    pos=range(len(season_list))
    Nam[ip] = pp.name()
    F1=pp._my_float
    F1_cycle[ip] = F1.cycle

    #print ip, F1.filename
    #Pres,Prof,Qc = F1.read_raw('CHLA')
    Pres,Prof,Qc = F1.read('CHLA')
# REGRID THE DEPTH TO 1M
    NewPres_1m=np.linspace(0,200,201)
#    Prof_mAve = movingaverage(Prof,7)
# SELECT JUST DEPTHS BETWEEN 0-200M
    ii200 = Pres<200 ;
    #print Prof
    if len(Prof[ii200])>0 :
# IF THE ARRAY IS NOT EMPTY, PLOT THE VALUES OF CHLA
       #pl.plot(Prof[ii200],Pres[ii200])
       pl.scatter(Prof[ii200],Pres[ii200])
#       pl.plot(Prof_mAve[ii200],Pres[ii200])
# INTERPOLATE THE CHLA DATA TO 1M DEPTH
       NewProf_1m = np.interp(NewPres_1m,Pres[ii200],Prof[ii200])
#       pl.plot(np.interp(NewPres,Pres[ii200],Prof[ii200]),NewPres,'-x')
# DP A RUNNING AVERAGE TO A [-10m]-[+10m] SPACE WINDOW
       NewProf_1m_RAve = movingaverage(NewProf_1m,21)
# DO THE SMOOTHING LATER!
###       NewProf_1m_RAve = NewProf_1m
       #
# SAVE ALL THE SMOOTHED PROFILES OF THE SAME FLOAT IN ONE ARRAY
       All_Profiles[ip,] = NewProf_1m_RAve
       #
#       pl.plot(NewProf_1m_RAve,NewPres_1m,'-x')
       pl.plot(NewProf_1m_RAve,NewPres_1m)
       pl.axis([0, 2.1, 0, 200])
       if LOOP == 1:
          fig_title= ''.join(['CHLA ',str(nP), ' profiles area: ',fl ,' [OCT-MAR]'])
       #fig_name= ''.join(['FLOAT_RAW_',fl,'.png' ])
       #fig_name= ''.join(['FLOAT_',fl,'.png' ])
          fig_name= ''.join(['FLOAT_timeseries_40mRA_',fl,'_aw.png' ])
       if LOOP == 2:
	  fig_title= ''.join(['CHLA ',str(nP), ' profiles area: ',fl ,' [APR-SEP]'])
          fig_name= ''.join(['FLOAT_timeseries_40mRA_',fl,'_ss.png' ])
       pl.title(fig_title)
       pl.savefig(fig_name)
#       DCM1 = max(Prof[ii200])
#       MAX1 = Pres[np.argmax(Prof[ii200])]
       QC1 = Qc[np.argmax(Prof[ii200])]
       #######
       DCM1 = max(NewProf_1m_RAve)
       MAX1 = NewPres_1m[np.argmax(NewProf_1m_RAve)]
#       QC1 = Qc[np.argmax(NewProf_1m_RAve)] 
       #######
       print "DCM! = ", DCM1, " QC! = ", QC1 
       q75,q25 = np.percentile(Prof[ii200],[75,25])
       iqr = q75-q25
###       print "IQR = ", iqr
    else :
       MAX1 = np.nan
       DCM1 = np.nan
   DCM[ip] = DCM1
   Max_Depth[ip] = MAX1
#    STD1[ = np.std(All_Profiles[, 

   pl.show(block=False)
   pl.close(fig)

# CALCULATE THE MEAN AND STD EVERY METEROF DEPTH:
   for kk in range(0,201):
      MEAN1[kk] = np.mean(All_Profiles[:,kk])
      STD1[kk] = np.std(All_Profiles[:,kk])
  
#  lim_3sigma = NewProf_1m_RAve < (MEAN1+3*STD1)
   fig=pl.figure(i)
   for npp in range(0,nP):
      tmp_All_Profiles=All_Profiles[npp,]
# ELIMINATE POINTS ABOVE 3STD
      lim_3sigma = tmp_All_Profiles < (MEAN1+3*STD1)
# DO ANOTHE MOVING AVERAGE OF +3 -3 AFTER REMOVING POSSIBLE POINTS ABOVE 3STD:
      if len(tmp_All_Profiles[lim_3sigma]) > 50 :
         tmp_MA_All_Profiles = movingaverage(tmp_All_Profiles[lim_3sigma],7)
####      integral_chla = np.cumsum(tmp_MA_All_Profiles)
#      pl.plot(tmp_All_Profiles[lim_3sigma],NewPres_1m[lim_3sigma])
         pl.plot(tmp_MA_All_Profiles,NewPres_1m[lim_3sigma])
         tmp_P = tmp_All_Profiles[lim_3sigma]
#      integral_CumulativeSum = np.cumsum(np.diff(NewPres_1m[lim_3sigma])*(tmp_All_Profiles[lim_3sigma][0:(len(lim_3sigma)-1)]))
         integral_CumulativeSum = np.cumsum(np.diff(NewPres_1m[lim_3sigma])*(tmp_P[0:(len(tmp_P)-1)]))

         integral_chla[npp] = integral_CumulativeSum[len(integral_CumulativeSum)-1]
         print npp, "INTEGRAL: ", integral_chla[npp]
      else :
         print "LESS THAN 50 POINTS IN THE PROFILE"
   pl.axis([0, max(MEAN1+4*STD1), 0, 200])
#   fig_title_smooth= ''.join(['CHLA profiles with smoothing - area: ',fl ])
   if LOOP == 1 :
     fig_title_smooth= ''.join(['CHLA ',str(nP), ' profiles with smoothing - area: ',fl ,' [OCT-MAR]' ])
     fig_name_smooth = ''.join(['FLOAT_timeseries_smooth_40mRA_',fl,'_aw.png' ])
     fig_title_MEAN_STD= ''.join(['CHLA mean profile for area ',fl ,' [OCT-MAR]'])
     fig_name_MEAN = ''.join(['MEAN_PROFILE_',fl,'_aw.png' ])
     fig_title_INTEGRAL = ''.join(['INTEGRAL 0-200m for area ',fl ,' [OCT-MAR]' ])
     fig_name_INTEGRAL = ''.join(['INTEGRAL_',fl,'_aw.png' ])
   if LOOP == 2 :
     fig_title_smooth= ''.join(['CHLA ',str(nP), ' profiles with smoothing - area: ',fl ,' [APR-SEP]' ])
     fig_name_smooth = ''.join(['FLOAT_timeseries_smooth_40mRA_',fl,'_ss.png' ])
     fig_title_MEAN_STD= ''.join(['CHLA mean profile for area ',fl ,' [APR-SEP]'])
     fig_name_MEAN = ''.join(['MEAN_PROFILE_',fl,'_ss.png' ])
     fig_title_INTEGRAL = ''.join(['INTEGRAL 0-200m for area ',fl ,' [APR-SEP]' ])
     fig_name_INTEGRAL = ''.join(['INTEGRAL_',fl,'_ss.png' ])

   pl.plot(MEAN1,NewPres_1m,'r--',linewidth=3.0)
   pl.plot(MEAN1+STD1,NewPres_1m,'r-.',linewidth=3.0)
   pl.plot(MEAN1-STD1,NewPres_1m,'r-.',linewidth=3.0)
   pl.title(fig_title_smooth)
   pl.savefig(fig_name_smooth)

   pl.show(block=False)
   pl.close(fig)
 
# PLOT THE INTEGRAL FOR AREA:
# PLOT THE MEAN AND STD FOR AREA:
   pl.figure(50)
   pl.plot(MEAN1)
   pl.plot(MEAN1+STD1,'r')
   pl.plot(MEAN1-STD1,'r')

#  fig_title_MEAN_STD= ''.join(['CHLA mean profile for area ',fl ])
#  fig_name_MEAN = ''.join(['MEAN_PROFILE_',fl,'.png' ])
   pl.title(fig_title_MEAN_STD)
   pl.show(block=False)
   pl.savefig(fig_name_MEAN)
################  integral_chla =  np.cumsum(np.diff(NewPres_1m[lim_tmp])*(tmp_All_Profiles[lim_tmp][0:187])
#  pl.show(block=False)
   pl.close(50)

   pl.figure(70)
   pl.plot(integral_chla)
#  fig_title_INTEGRAL = ''.join(['INTEGRAL 0-200m for area ',fl ])
#  fig_name_INTEGRAL = ''.join(['INTEGRAL_',fl,'.png' ])
   pl.title(fig_title_INTEGRAL)
   pl.show(block=False)
   pl.savefig(fig_name_INTEGRAL)
   pl.close(70)
   TimARR=np.asarray(Tim)
   
   print 'END LOOP ', LOOP

