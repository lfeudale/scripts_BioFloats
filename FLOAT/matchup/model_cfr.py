import scipy.io.netcdf as NC
import numpy as np
import os
from commons.time_interval import TimeInterval
from commons.layer import Layer

from profiler import *
import basins.OGS as OGS
from instruments import bio_float
from instruments.var_conversions import FLOATVARS
from commons.layer import Layer

M = Matchup_Manager(T_INT,INPUTDIR,BASEDIR)

maskfile    = os.getenv("MASKFILE"); 
ncIN=NC.netcdf_file(maskfile,"r")
nav_lev = ncIN.variables['nav_lev'].data.copy()
ncIN.close()

layer=Layer(0,200)
modelvarname='P_i'
Profilelist=bio_float.FloatSelector(FLOATVARS[modelvarname],T_INT,OGS.tyr)
#Floatmatchups = M.getMatchups(Profilelist, nav_lev, modelvarname)
#Floatmatchups.subset(layer)
#Floatmatchups.densityplot2()

for p in Profilelist[:1]:
    singlefloatmatchup = M.getMatchups([p], nav_lev, modelvarname)
    s200 = singlefloatmatchup.subset(layer)
    print s200.bias()
    print 'DIFF:'
    print s200.diff()
