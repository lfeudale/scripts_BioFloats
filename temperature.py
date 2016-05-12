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
import matplotlib 

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

TI1 = TimeInterval('20130101','20160301','%Y%m%d')
#reg_sn = ['alb','sww','swe','nwm','tyr','adn','ads','aeg','ion','lev','med']
reg1 = [OGS.alb,OGS.sww,OGS.swe,OGS.nwm,OGS.tyr,OGS.adn,OGS.ads,OGS.aeg,OGS.ion,OGS.lev]
reg_sn = ['alb','sww','swe','nwm','tyr','adn','ads','aeg','ion','lev']
#reg_sn = ['tyr','adn','ads','aeg','ion','lev']
#reg1 = [OGS.tyr,OGS.adn,OGS.ads,OGS.aeg,OGS.ion,OGS.lev]
RR = 6371.
reg1 = [OGS.med]
reg_sn = ['med']
tt_reg = np.zeros((len(reg_sn),), np.float64)
dd_reg = np.zeros((len(reg_sn),), np.float64)
n_floats = np.zeros(((len(reg_sn)),), np.int)
n_profiles = np.zeros(((len(reg_sn)),), np.int)

modelvarname1 ='votemper'
varname1 ='TEMP'
modelvarname2 ='vosaline'
varname2 ='PSAL'
varname = ['TEMP','PSAL','DOXY','NITRATE']
varname = ['PSAL']

#for i,p in enumerate(OGS.P.basin_list):
for i,var in enumerate(varname):
  fl = reg_sn[i]
#for i,fl in enumerate(reg_sn):
#  Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname1],TI1,fl)
#  Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname1],TI1,reg1)
  Profilelist_1=bio_float.FloatSelector(var,TI1,OGS.med)
  nP_all = len(Profilelist_1)
#  Lon = np.zeros((nP,), np.float64)
#  Lat = np.zeros((nP,), np.float64)
#  LonR = np.zeros((nP,), np.float64)
#  LatR = np.zeros((nP,), np.float64)
#  DCM = np.zeros((nP,), np.float64)
#  Max_Depth = np.zeros((nP,), np.float64)
#  integral_chla = np.zeros((nP,), np.float64)
#  Tim = []
  Summer_list = []
  Winter_list = []
  season_list = []
#  P_month = np.zeros((nP,), np.int)
  Nam = np.zeros((nP_all,), np.int)
#  F1_cycle = np.zeros((nP,), np.int)
#  All_Profiles = np.zeros((nP,201), np.float64)
#  integral_CumulativeSum =  np.zeros((200,), np.float64)
#  fig=pl.figure(i)
 
#  MEAN1 = np.zeros((201,), np.float64)
#  STD1 = np.zeros((201,), np.float64)

  for w in Profilelist_1 :
    if (w.time.month <=3) | (w.time.month >=10) :
       Winter_list.append(w)
    else :
       Summer_list.append(w)

# CREATE A DOUBLE LOOP ON LISTS:
# LOOP 1: WINTER
# LOOP 2: SUMMER

#--------------------------------------------
# DO A LOOP ON THE FLOATS:
#--------------------------------------------

#  LOOP = 1
#  for LOOP in range(1,3) :
  for LOOP in range(2,3) :
    if LOOP == 1:
       season_list = Winter_list
       print 'WINTER'
       season_text = "w"
       season_text2 = "[OCT-MAR]"
    if LOOP == 2:
       season_list = Summer_list
       season_text = "s"
       print 'SUMMER'
       season_text2 = "[APR-SEP]"


    S1=set()
    for k in season_list: S1.add( k.name() )
    S1list=list(S1)
    nS1=len(S1list)
    snS1=str(nS1)
    S1l=np.asarray(S1list)

#########
    nP = len(season_list)
    Lon = np.zeros((nP,), np.float64)
    Lat = np.zeros((nP,), np.float64)
    LonR = np.zeros((nP,), np.float64)
    LatR = np.zeros((nP,), np.float64)

#    integral_chla = np.zeros((nP,), np.float64)
    P_month = np.zeros((nP,), np.int)
    Nam = np.zeros((nP,), np.int)
    F1_cycle = np.zeros((nP,), np.int)
#    All_Profiles = np.zeros((nP,201), np.float64)
    integral_CumulativeSum =  np.zeros((200,), np.float64)
########
    pos=range(len(season_list))
    ppos=np.asarray(pos)

    for ind in range(0, nS1 ):
#    for ind in range(15, nS1 ):
	    wmolist = S1l[ind]
            print ind, " - WMOLIST: ", wmolist
	  # CREATE THE LIST OF PROFILES FOR A SINGLE FLOAT
    	    Float = []
	    MEAN1 = np.zeros((201,), np.float64)
            STD1 = np.zeros((201,), np.float64)
 	    for ip, pp in enumerate(season_list):
        	Lon[ip] = pp.lon
        	Lat[ip] = pp.lat
        	LonR[ip] = np.pi/180.*pp.lon
        	LatR[ip] = np.pi/180.*pp.lat
#        	Tim.append( pp.time.date() )
#		F1_cycle[ip] = F1.cycle
#########################################
		if wmolist == pp._my_float.wmo :
   	   	   Float.append(pp._my_float)
		   
	    name_fig = ''.join([var,'_float_',wmolist,'_',str(season_text),'.png'])
	    name_fig_DCM = ''.join(['DCM_FLOAT_',wmolist,'_',str(season_text),'.png'])
	    fig_name_INTEGRAL = ''.join([var,'_INTEGRAL_',wmolist,'_',str(season_text),'.png' ])
	    fig_title_INTEGRAL = ''.join([var,' - INTEGRAL 0-200m for FLOAT ',wmolist ,':',str(season_text2) ])    
            fig_title= ''.join([var,' ',str(len(Float)), ' FLOAT: ',wmolist ,' ',str(season_text2)])
          # DO THE ANALYSIS ON ALL THE PROFILES OF EACH SINGLE FLOAT
	    TT = np.zeros((len(Float),), np.float64)
            SS = np.zeros((len(Float),), np.float64)
    	    DCM = np.zeros((len(Float),), np.float64)
    	    Max_Depth = np.zeros((len(Float),), np.float64)
	    All_Profiles = np.zeros((len(Float),201), np.float64)
	    integral_chla = np.zeros((len(Float),), np.float64)
	    integral_CumulativeSum =  np.zeros((200,), np.float64)
	    Float_cycle = np.zeros((len(Float),), np.int)
	    Tim = []
	    fig=pl.figure(ind)
	    for iii in range(len(Float)):
                Float_cycle[iii] = Float[iii].cycle
		Tim.append( Float[iii].time.date() )
  	        Pres,Prof,Qc = Float[iii].read(var,read_adjusted=False)
		NewPres_1m=np.linspace(0,200,201)
		ii200 = Pres<200 ;
		if len(Prof[ii200])>10 :
		   check_na = 0
		   matplotlib.rc('xtick', labelsize=12)
		   matplotlib.rc('ytick', labelsize=12)
		   pl.scatter(Prof[ii200],Pres[ii200])
#                pl.plot(Prof[ii200],Pres[ii200])
		 # INTERPOLATE THE CHLA DATA TO 1M DEPTH
                   NewProf_1m = np.interp(NewPres_1m,Pres[ii200],Prof[ii200])
#       pl.plot(np.interp(NewPres,Pres[ii200],Prof[ii200]),NewPres,'-x')
		 # DO A RUNNING AVERAGE TO A [-10m]-[+10m] SPACE WINDOW
                   NewProf_1m_RAve = movingaverage(NewProf_1m,21)
		 # SAVE ALL THE SMOOTHED PROFILES OF THE SAME FLOAT IN ONE ARRAY
                   All_Profiles[iii,] = NewProf_1m_RAve
       #
#       pl.plot(NewProf_1m_RAve,NewPres_1m,'-x')
                   pl.plot(NewProf_1m_RAve,NewPres_1m)
# TEMP                   pl.axis([5, 30, 0, 200])
		   pl.axis([20, 40, 0, 200])
		   pl.title(fig_title)
                   QC1 = Qc[np.argmax(Prof[ii200])]      
                   DCM1 = max(NewProf_1m_RAve)
                   MAX1 = NewPres_1m[np.argmax(NewProf_1m_RAve)]
                   print "CYCLE: ", Float_cycle[iii], " MAX1 = ", MAX1, "DCM1 = ", DCM1, " QC1 = ", QC1
#            	   DCM[iii] = DCM1
#            	   Max_Depth[iii] = MAX1
                else :
		   print "NO DATA"
                   check_na = 1
       		   MAX1 = np.nan
       		   DCM1 = np.nan


  	        TimARR=np.asarray(Tim)
		if check_na == 0 :
                	pl.savefig(name_fig)
	        	pl.show(block=False)
  	    	DCM[iii] = DCM1
   	    	Max_Depth[iii] = MAX1
                pl.close(fig)
             
 


   	    for kk in range(0,201):
      		MEAN1[kk] = np.mean(All_Profiles[:,kk])
      		STD1[kk] = np.std(All_Profiles[:,kk])

#	    TimARR=np.asarray(Tim)
#            pl.savefig(name_fig)
#	    pl.show(block=False)
#            pl.close(fig)

	    figg=pl.figure(ind+1)
            figg, ax1 = pl.subplots()
#	    ax1.plot(Float_cycle,DCM,'G')
	    matplotlib.rc('xtick', labelsize=7)
	    matplotlib.rc('ytick', labelsize=10)
	    if np.invert(np.isnan(DCM)).any() :
	    	ax1.plot(TimARR,DCM,'G')
	    	ax1.set_ylabel(r"TEMP C",fontsize=16,color="green")
	    	ax2=ax1.twinx()
#	    ax2.plot(Float_cycle,Max_Depth,'b')
	    	ax2.plot(TimARR,Max_Depth,'b')
	    	ax2.set_ylabel(r"Depth of maxT m",fontsize=16,color="blue")
	    	pl.savefig(name_fig_DCM)
	    pl.close(figg)

	    for mm in range(len(Float)):
		tmp_All_Profiles=All_Profiles[mm,]
      		sigma3 = tmp_All_Profiles < (MEAN1+3*STD1)
#		fig_m = pl.figure(mm)
#		pl.plot(tmp_All_Profiles,NewPres_1m[sigma3])
#		pl.show(block=False)
		if len(tmp_All_Profiles[sigma3]) > 50 :
			tmp_P = tmp_All_Profiles[sigma3]
			integral_CumulativeSum = np.cumsum(np.diff(NewPres_1m[sigma3])*(tmp_P[0:(len(tmp_P)-1)]))
			integral_chla[mm] = integral_CumulativeSum[len(integral_CumulativeSum)-1]
			print mm, "INTEGRAL: ", integral_chla[mm]
		else :
			print "LESS THAN 50 POINTS IN THE PROFILE"

	    fig_int = pl.figure(50)
	    pl.plot(TimARR,integral_chla)
	    pl.title(fig_title_INTEGRAL)
  	    pl.show(block=False)
	    pl.savefig(fig_name_INTEGRAL)
	    pl.close(fig_int)
 #          pl.plot(DCM,'g')
 #	    pl.plot(Max_Depth,'b')
#    pl.plot(integral,'r')
#########################################

print 'END LOOP ', LOOP

