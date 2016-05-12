import scipy.io.netcdf as NC
import numpy as np
import os
from commons.time_interval import TimeInterval
from commons.layer import Layer
import pylab as pl

from profiler import *
import basins.OGS as OGS
from instruments import bio_float
from instruments.var_conversions import FLOATVARS
from commons.layer import Layer

TI1 = TimeInterval('20150101','20160101','%Y%m%d')

M = Matchup_Manager(TI1,INPUTDIR,BASEDIR)

maskfile    = os.getenv("MASKFILE"); 
ncIN=NC.netcdf_file(maskfile,"r")
nav_lev = ncIN.variables['nav_lev'].data.copy()
ncIN.close()

layer=Layer(0,200)
modelvarname='P_i'

# PRESSURE WITH 1M OF RESOLUTION:
NewPres=np.linspace(0,200,201)
Profilelist_1=bio_float.FloatSelector(FLOATVARS[modelvarname],TI1,OGS.med)

# DIVIDE BY SEASONS:
Winter_list = []
Spring_list = []
Summer_list = []
Autumn_list = []

for w in Profilelist_1 :
	if (w.time.month >=1) & (w.time.month <=3) :
		Winter_list.append(w)
	if (w.time.month >=4) & (w.time.month <=6) :
                Spring_list.append(w)
        if (w.time.month >=7) & (w.time.month <=9) :
                Summer_list.append(w)
        if (w.time.month >=10) & (w.time.month <=12) :
                Autumn_list.append(w)

for LOOP in range(1,5) :
#for LOOP in range(1,2) :
    if LOOP == 1:
       season_list = Winter_list
       print 'WINTER'
       season_text = "wn"
       season_text2 = "[JAN-MAR]"
    if LOOP == 2:
       season_list = Spring_list
       print 'SPRING' 
       season_text = "sp"
       season_text2 = "[APR-JUN]"
    if LOOP == 3:
       season_list = Summer_list
       season_text = "sm"
       print 'SUMMER'
       season_text2 = "[JUL-SEP]"
    if LOOP == 4:
       season_list = Autumn_list
       season_text = "at"
       print 'AUTUMN'
       season_text2 = "[OCT-DEC]"

    S1=set()
    for k in season_list: S1.add( k.name() )
    S1list=list(S1)
    nS1=len(S1list)
    snS1=str(nS1)
    S1l=np.asarray(S1list)
#    S1l=np.asarray(S1)
    nP = len(season_list)

    for ind, fl in enumerate(S1list) :
#    for ind, fl in enumerate(S1) :
#      if ind == 0 :
	wmolist = S1l[ind]
	print ind, " - WMOLIST: ", wmolist
	fig = pl.figure(ind)

# CREATE THE LIST OF PROFILES FOR A SINGLE FLOAT
        Float = []
        for i, p in enumerate(season_list):
	  if wmolist == p._my_float.wmo :
	   
	   	print p._my_float.wmo , p._my_float.cycle
#	   	Float.append(p._my_float)
	   	Float.append(p)
	
	AllProfiles = np.zeros((len(Float),201),np.float64)
# 	  for ip, pp in enumerate(Float[:1]) :
 	for ip, pp in enumerate(Float) :

#Profilelist=bio_float.FloatSelector(FLOATVARS[modelvarname],TI1,OGS.tyr)
#Floatmatchups = M.getMatchups(Profilelist, nav_lev, modelvarname)
#Floatmatchups.subset(layer)
#Floatmatchups.densityplot2()

#for p in Profilelist[:1]:
	    singlefloatmatchup = M.getMatchups([pp], nav_lev, modelvarname)
	    s200 = singlefloatmatchup.subset(layer)
	    print s200.bias()
	    if np.invert(np.isnan(s200.bias())) :
	    #print 'DIFF:'
	    #print s200.diff()
	    	s200int=np.interp(NewPres,s200.Depth,s200.diff())
	    	AllProfiles[ip,:] = s200int

	pmean=(np.mean(AllProfiles,0))
	pstd=(np.std(AllProfiles,0))
	pl.plot(pmean,NewPres,'b')
	pl.plot(pmean+pstd,NewPres,'b:')
	pl.plot(pmean-pstd,NewPres,'b:')
	pl.gca().invert_yaxis()
	floatlabel = 'Float '+ str(wmolist) + ' ' + season_text2 + ' \n' + 'n.profiles: ' + str(len(Float))
	fig_name = ''.join(['DIFF_Obs_Mod_',wmolist,'_',season_text,'.png'])
	fig.suptitle(floatlabel)
	pl.xlabel(r'Chl $[mg/m^3]$')
	pl.ylabel(r'Depth $[m]$')
	pl.savefig(fig_name)
	pl.show(block=False)
	pl.close(fig)

