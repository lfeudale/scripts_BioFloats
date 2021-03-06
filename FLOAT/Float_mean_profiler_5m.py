import os,sys
from commons.time_interval import TimeInterval
from commons.Timelist import TimeList
from basins.region import Region, Rectangle
from layer_integral import coastline
import instruments
from instruments import bio_float
from instruments.var_conversions import FLOATVARS
import scipy.io.netcdf as NC
import numpy as np
from commons.utils import addsep
import pylab as pl
from basins import OGS
from validation.online.profileplotter import figure_generator, ncwriter, add_metadata
import matplotlib
from mhelpers.pgmean import PLGaussianMean
#import matchup.matchup

TI1 = TimeInterval('20130101','20160301','%Y%m%d')
reg1 = [OGS.med]
reg_sn = ['med']

varname = ['CHLA','DOXY','NITRATE','TEMP','PSAL']
plotvarname = [r'Chl $[mg/m^3]$',r'Oxy $[mmol/m^3]$',r'Nitr $[mmol/m^3]$',r'Temp $[^\circ C]$','Sal']
read_adjusted = [True,False,False,False,False]
mapgraph = [3,4,5,1,2]

meanObj11 = PLGaussianMean(11,1.0)
Profilelist_1=bio_float.FloatSelector(None,TI1,OGS.med)

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


for LOOP in range(2,5) :
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
    nP = len(season_list)

    for ind, fl in enumerate(S1list) :
      if ind > 11 :
	wmolist = S1l[ind]
	print ind, " - WMOLIST: ", wmolist

# CREATE THE LIST OF PROFILES FOR A SINGLE FLOAT
        Float = []
        for ip, pp in enumerate(season_list):
	  if wmolist == pp._my_float.wmo :
	   fig = pl.figure(ind)
	   
	   print pp._my_float.wmo , pp._my_float.cycle
	   Float.append(pp._my_float)

	   All_Profiles = np.zeros((len(Float),201,len(varname)), np.float64)
	   integral_CumulativeSum =  np.zeros((200,), np.float64)
	   MEAN1 = np.zeros((201,len(varname), np.float64)
           STD1 = np.zeros((201,len(varname)), np.float64)
	   DCM1 = np.zeros((201,len(varname)), np.float64)
           MAX1 = np.zeros((201,len(varname)), np.float64)
	   fig, axs = pl.subplots(2,3, facecolor='w', edgecolor='k')
 	   for ipp, fix_float in enumerate(Float) :
#	      All_Profiles = np.zeros((len(Float),41), np.float64)
#	      integral_CumulativeSum =  np.zeros((40,), np.float64)
#	   for fix_float in Float[4:] :

#########################      #     
#	      fig, axs = pl.subplots(2,3, facecolor='w', edgecolor='k')
    	      hsize=10
    	      vsize=12
    	      fig.set_size_inches(hsize,vsize)
    #figtitle = " date="+p.time.strftime('%Y/%m/%d')+" float="+p.name()
    #fig.set_title(figtitle)
    	      fig.subplots_adjust(hspace = 0.15, wspace=0.3)
    	      axs = axs.ravel()

    	      ax = axs[0]
    	      c_lon, c_lat=coastline.get()
    	      ax.plot(c_lon,c_lat, color='#000000',linewidth=0.5)
    	      ax.plot(fix_float.lon,fix_float.lat,'ro')
    	      ax.set_xticks(np.arange(-6,36,2))
    	      ax.set_yticks(np.arange(0,100,2))
     	      ax.set_xlabel("lon")
    	      ax.set_ylabel("lat")

	      extent=10 #degrees
	      ax.set_xlim([fix_float.lon -extent/2, fix_float.lon+extent/2])
	      ax.set_ylim([fix_float.lat -extent/2, fix_float.lat+extent/2])
	      bbox=ax.get_position()

	      deltax, _ =bbox.size
	      new_deltay = deltax* hsize/vsize
	      bottom = bbox.ymax - new_deltay
	      ax.set_position([bbox.xmin, bottom, deltax, new_deltay])
	      floatlabel = 'Float '+ str(fix_float.wmo) + ' \n' + season_text2
	      ax.set_title(floatlabel)

##############
	      for ax in axs[1:]:
              	 ax.set_ylim(0,200)
              	 ax.locator_params(axis='x',nbins=4)
              	 ax.yaxis.grid()

              for ax in [axs[2], axs[4], axs[5]]:
                 ax.set_yticklabels([])

#########################
	      fig_name = ''.join(['FLOAT_',wmolist,'_',str(season_text),'.png'])
	      for i_var, var in enumerate(varname) :
#		fig_name = ''.join([var,'_float_',wmolist,'_',str(season_text),'.png'])
		ax=axs[mapgraph[i_var]] #get subplot
		#MEAN1 = np.zeros((41,), np.float64)
            	#STD1 = np.zeros((41,), np.float64)
		#DCM1 = np.zeros((41,), np.float64)
            	#MAX1 = np.zeros((41,), np.float64)
		if var in fix_float.available_params.split(" ") :
#			fig_name = ''.join([var,'_float_',wmolist,'_',str(season_text),'.png'])			
			Pres,Prof,Qc = fix_float.read(var,read_adjusted=read_adjusted[i_var])
			Pres,Prof_smooth,Qc = fix_float.read(var,meanObj11,read_adjusted[i_var])
			NewPres_5m=np.linspace(0,200,41)
			#MEAN1 = np.zeros((41,), np.float64)
            		#STD1 = np.zeros((41,), np.float64)
			#DCM1 = np.zeros((41,), np.float64)
            		#MAX1 = np.zeros((41,), np.float64)
# SELECT JUST DEPTHS BETWEEN 0-200M
            		ii200 = Pres<200 ;
            		if len(Prof_smooth[ii200])>0 :
# INTERPOLATE THE CHLA DATA TO 5M VERTICAL RESOLUTION:
              			NewProf_5m = np.interp(NewPres_5m,Pres[ii200],Prof_smooth[ii200])
			#ax.scatter(Prof,Pres)
				#ax.plot(Prof_smooth,Pres)
			#pl.gca().invert_yaxis()
				#ax.invert_yaxis()
			#ax.title(plotvarname[i_var])
				 All_Profiles[ipp, ,i_var] = NewProf_5m
			#title_str = ''.join([plotvarname[i_var]])
			#ax.set_title(title_str)
		
		MEAN1(:,i_var)= np.mean(All_Profiles,1)
		STD1 = np.std(All_Profiles,1)
		DCM1 = np.max(All_Profiles,1)
		MAX1 = NewPres_5m(np.argmax(All_Profiles,1))

#	   pl.show(block=False)
	   #pl.savefig(fig_name)
	   #pl.close(fig)
sys.exit()
'DOXY' in p.available_params.split(" ")

for i, var in enumerate(varname) :


	for ip, p in enumerate(Profilelist_1) :
		if var in p.available_params.split(" "):
			print var, " in ", p.name()

Pres, Profile, Qc = p.read(ref_varname,read_adjusted[i])
if len(Pres) == 0:
    Pres, Profile, Qc = p.read(ref_varname,not read_adjusted    [i])
print model_varname, len(Profile)


VARLIST = p._my_float.available_params.strip().rsplit(" ")
VARLIST.remove('PRES')

Profilelist_1=bio_float.FloatSelector(None,TI1,OGS.med)

for i,var in enumerate(varname):
	Profilelist_2=bio_float.FloatSelector(var,TI1,OGS.med)

