
np.mean(np.diff( - ))
np.mean(np.abs(np.diff( -  )))
dtime = Float[3].time-Float[2].time
totsec=60*60*24
value = np.round(dtime.total_seconds()/totsec)
derivt=pl.plot(value/len(Float)
