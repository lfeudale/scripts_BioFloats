import commons.timerequestors as requestors
from commons.season import season
import basins.OGS as OGS
from instruments import bio_float
from instruments.var_conversions import FLOATVARS


seasonObj = season()
num_seas = 0 # Winter
req = requestors.Season_req(2015, num_seas ,seasonObj)

print req.timeinterval
modelvarname ='P_i'
Profilelist=bio_float.FloatSelector(FLOATVARS[modelvarname],req.timeinterval, OGS.tyr)

