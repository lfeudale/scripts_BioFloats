


    def getSingleWmoPlot(Profilelist,outdir="./"):
        '''
        Dumps an image png file and a NetCDF file for each profile
        The filenames refers to time and float wmo.
        Both files contain matchups about chl,O2o,N3n,temperature, salinity


        Matchups are provided at fixed depths: every 5 meters from 0 to 400m,
        because in biofloats physical and biological variables do not have the same sampling.

        Arguments:
        * Profilelist * is provided by FloatSelector
        * outdir * optional is the output location


        The matchups are couples of values (Model,Ref)
        obtained to a given selection in space and time,
        to be used in statistics.


        At the moment it can happen that a short model profile is extrapolated over a long float profile.
        Then, a replication of matchups could occur.

        Returns nothing
        '''
        from validation.online.profileplotter import figure_generator
        
        MODELVARLIST=['P_i','O2o','N3n','votemper','vosaline']
        plotvarname = [r'Chl $[mg/m^3]$',r'Oxy $[mmol/m^3]$',r'Nitr $[mmol/m^3]$',r'Temp $[^\circ C]$','Sal']
        read_adjusted = [True,False,False,False,False]
        mapgraph = [3,4,5,1,2]
        p = Profilelist[0]

        fig, axs = figure_generator(p)
# CERCO LA TRAIETTORIA
        LON =[]
        LAT= []
        for p in Profilelist:
            LON.append(p.lon)
            LAT.append(p.lat)

        ax=axs[0]
        ax.plot(LON,LAT,'ro')
  
        for p in Profilelist:
 
            VARLIST = p._my_float.available_params.strip().rsplit(" ")
            VARLIST.remove('PRES')

            for i,model_varname in enumerate(MODELVARLIST):
                ref_varname = self.reference_var(p, model_varname)
                if ref_varname not in VARLIST: continue
                Pres, Profile, Qc = p.read(ref_varname,read_adjusted[i])
                if len(Pres) == 0:
                    Pres, Profile, Qc = p.read(ref_varname,not read_adjusted[i])

                print model_varname, len(Profile)

                ax=axs[mapgraph[i]] #get subplot
                fig, ax = p._my_float.plot(Pres,Profile,fig,ax)



       pngfile = filename + ".png"
       fig.savefig(pngfile)
       pl.close(fig)
        return
