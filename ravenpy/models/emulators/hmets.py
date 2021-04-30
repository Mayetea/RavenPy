from pathlib import Path

from pydantic.dataclasses import dataclass

from ravenpy.config.commands import HRU, LU, BasinIndexCommand, HRUState, Sub
from ravenpy.config.rvs import RVI
from ravenpy.models.base import Ostrich, Raven


class HMETS(Raven):
    @dataclass
    class Params:
        GAMMA_SHAPE: float = None
        GAMMA_SCALE: float = None
        GAMMA_SHAPE2: float = None
        GAMMA_SCALE2: float = None
        MIN_MELT_FACTOR: float = None
        MAX_MELT_FACTOR: float = None
        DD_MELT_TEMP: float = None
        DD_AGGRADATION: float = None
        SNOW_SWI_MIN: float = None
        SNOW_SWI_MAX: float = None
        SWI_REDUCT_COEFF: float = None
        DD_REFREEZE_TEMP: float = None
        REFREEZE_FACTOR: float = None
        REFREEZE_EXP: float = None
        PET_CORRECTION: float = None
        HMETS_RUNOFF_COEFF: float = None
        PERC_COEFF: float = None
        BASEFLOW_COEFF_1: float = None
        BASEFLOW_COEFF_2: float = None
        TOPSOIL: float = None
        PHREATIC: float = None

    @dataclass
    class DerivedParams:
        TOPSOIL_m: float = None
        PHREATIC_m: float = None
        SUM_MELT_FACTOR: float = None
        SUM_SNOW_SWI: float = None
        TOPSOIL_hlf: float = None
        PHREATIC_hlf: float = None

    @dataclass
    class ForestHRU(HRU):
        land_use_class: str = "FOREST"
        veg_class: str = "FOREST"
        soil_profile: str = "DEFAULT_P"
        aquifer_profile: str = "[NONE]"
        terrain_class: str = "[NONE]"

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.config.update(
            identifier="hmets",
            hrus=(HMETS.ForestHRU(),),
            subbasins=(
                Sub(
                    subbasin_id=1,
                    name="sub_001",
                    downstream_id=-1,
                    profile="None",
                    gauged=True,
                ),
            ),
            params=HMETS.Params(),
            derived_params=HMETS.DerivedParams(),
        )

        #########
        # R V P #
        #########

        rvp_tmpl = """
        #-----------------------------------------------------------------
        # Soil Classes
        #-----------------------------------------------------------------
        :SoilClasses
          :Attributes,
          :Units,
          TOPSOIL,
          PHREATIC,
        :EndSoilClasses

        #-----------------------------------------------------------------
        # Land Use Classes
        #-----------------------------------------------------------------
        :LandUseClasses,
          :Attributes,        IMPERM,    FOREST_COV,
               :Units,          frac,          frac,
               FOREST,           0.0,           1.0,
        :EndLandUseClasses

        #-----------------------------------------------------------------
        # Vegetation Classes
        #-----------------------------------------------------------------
        :VegetationClasses,
          :Attributes,        MAX_HT,       MAX_LAI, MAX_LEAF_COND,
               :Units,             m,          none,      mm_per_s,
               FOREST,             4,             5,             5,
        :EndVegetationClasses

        #-----------------------------------------------------------------
        # Soil Profiles
        #-----------------------------------------------------------------
        :SoilProfiles
                 LAKE, 0
                 ROCK, 0
          DEFAULT_P, 2, TOPSOIL,  {derived_params.TOPSOIL_m}, PHREATIC, {derived_params.PHREATIC_m},
        # DEFAULT_P, 2, TOPSOIL,   x(20)/1000, PHREATIC,   x(21)/1000,
        :EndSoilProfiles

        #-----------------------------------------------------------------
        # Global Parameters
        #-----------------------------------------------------------------
        :GlobalParameter         SNOW_SWI_MIN {params.SNOW_SWI_MIN}     # x(9)
        :GlobalParameter         SNOW_SWI_MAX {derived_params.SUM_SNOW_SWI}     # x(9)+x(10)
        :GlobalParameter     SWI_REDUCT_COEFF {params.SWI_REDUCT_COEFF} # x(11)
        :GlobalParameter             SNOW_SWI 0.05         # not sure why/if needed...

        #-----------------------------------------------------------------
        # Soil Parameters
        #-----------------------------------------------------------------
        :SoilParameterList
          :Parameters,        POROSITY,      PERC_COEFF,  PET_CORRECTION,  BASEFLOW_COEFF
               :Units,               -,             1/d,               -,             1/d
              TOPSOIL,             1.0,     {params.PERC_COEFF},{params.PET_CORRECTION},{params.BASEFLOW_COEFF_1}
             PHREATIC,             1.0,             0.0,             0.0, {params.BASEFLOW_COEFF_2}
         #    TOPSOIL,             1.0,           x(17),           x(15),           x(18)
         #   PHREATIC,             1.0,             0.0,             0.0,           x(19)
        :EndSoilParameterList

        #-----------------------------------------------------------------
        # Land Use Parameters
        #-----------------------------------------------------------------
        :LandUseParameterList
          :Parameters, MIN_MELT_FACTOR,  MAX_MELT_FACTOR,    DD_MELT_TEMP,  DD_AGGRADATION,  REFREEZE_FACTOR,    REFREEZE_EXP,  DD_REFREEZE_TEMP,  HMETS_RUNOFF_COEFF,
               :Units,          mm/d/C,          mm/d/C,               C,            1/mm,          mm/d/C,               -,                C,                  -,
            [DEFAULT],{params.MIN_MELT_FACTOR},{derived_params.SUM_MELT_FACTOR},  {params.DD_MELT_TEMP},{params.DD_AGGRADATION},{params.REFREEZE_FACTOR},  {params.REFREEZE_EXP},{params.DD_REFREEZE_TEMP},{params.HMETS_RUNOFF_COEFF},
        #                         x(5),       x(5)+x(6),            x(7),            x(8),           x(13),           x(14),            x(12),              x(16),
        :EndLandUseParameterList
        :LandUseParameterList
          :Parameters,   GAMMA_SHAPE,     GAMMA_SCALE,    GAMMA_SHAPE2,    GAMMA_SCALE2,
               :Units,             -,             1/d,               -,             1/d,
            [DEFAULT],  {params.GAMMA_SHAPE},   {params.GAMMA_SCALE},  {params.GAMMA_SHAPE2},  {params.GAMMA_SCALE2},
            #                   x(1),            x(2),            x(3),            x(4),
        :EndLandUseParameterList
        #-----------------------------------------------------------------
        # Vegetation Parameters
        #-----------------------------------------------------------------
        :VegetationParameterList
          :Parameters,  RAIN_ICEPT_PCT,  SNOW_ICEPT_PCT,
               :Units,               -,               -,
            [DEFAULT],             0.0,             0.0,
        :EndVegetationParameterList
        """
        self.config.rvp.set_tmpl(rvp_tmpl)

        #########
        # R V I #
        #########

        rvi_tmpl = """
        :PotentialMeltMethod     POTMELT_HMETS
        :RainSnowFraction        {rain_snow_fraction}
        :Evaporation             {evaporation}  # PET_OUDIN
        :CatchmentRoute          ROUTE_DUMP
        :Routing                 ROUTE_NONE

        :SoilModel               SOIL_TWO_LAYER

        :Alias DELAYED_RUNOFF CONVOLUTION[1]

        :HydrologicProcesses
          :SnowBalance     SNOBAL_HMETS    MULTIPLE     MULTIPLE
          :Precipitation   RAVEN_DEFAULT   ATMOS_PRECIP MULTIPLE
          :Infiltration    INF_HMETS       PONDED_WATER MULTIPLE
            :Overflow      OVERFLOW_RAVEN  SOIL[0]      DELAYED_RUNOFF
          :Baseflow        BASE_LINEAR     SOIL[0]      SURFACE_WATER   # interflow, really
          :Percolation     PERC_LINEAR     SOIL[0]      SOIL[1]         # recharge
            :Overflow      OVERFLOW_RAVEN  SOIL[1]      DELAYED_RUNOFF
          :SoilEvaporation SOILEVAP_ALL    SOIL[0]      ATMOSPHERE      # AET
          :Convolve        CONVOL_GAMMA    CONVOLUTION[0] SURFACE_WATER #'surface runoff'
          :Convolve        CONVOL_GAMMA_2  DELAYED_RUNOFF SURFACE_WATER #'delayed runoff'
          :Baseflow        BASE_LINEAR     SOIL[1]      SURFACE_WATER
        :EndHydrologicProcesses
        """
        self.config.rvi.set_tmpl(rvi_tmpl)

        self.config.rvi.evaporation = "PET_OUDIN"
        self.config.rvi.rain_snow_fraction = RVI.RainSnowFractionOptions.DATA

        #########
        # R V C #
        #########

        self.config.rvc.soil0 = None
        self.config.rvc.soil1 = None

    def derived_parameters(self):
        self.config.rvp.derived_params.TOPSOIL_hlf = (
            self.config.rvp.params.TOPSOIL * 0.5
        )
        self.config.rvp.derived_params.PHREATIC_hlf = (
            self.config.rvp.params.PHREATIC * 0.5
        )
        self.config.rvp.derived_params.TOPSOIL_m = (
            self.config.rvp.params.TOPSOIL / 1000.0
        )
        self.config.rvp.derived_params.PHREATIC_m = (
            self.config.rvp.params.PHREATIC / 1000.0
        )

        self.config.rvp.derived_params.SUM_MELT_FACTOR = (
            self.config.rvp.params.MAX_MELT_FACTOR
        )
        self.config.rvp.derived_params.SUM_SNOW_SWI = (
            self.config.rvp.params.SNOW_SWI_MAX
        )

        # Default initial conditions if none are given
        if not self.config.rvc.hru_states:
            soil0 = (
                self.config.rvp.derived_params.TOPSOIL_hlf
                if self.config.rvc.soil0 is None
                else self.config.rvc.soil0
            )
            soil1 = (
                self.config.rvp.derived_params.PHREATIC_hlf
                if self.config.rvc.soil1 is None
                else self.config.rvc.soil1
            )
            self.config.rvc.hru_states[1] = HRUState(soil0=soil0, soil1=soil1)


class HMETS_OST(Ostrich, HMETS):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.config.update(
            identifier="hmets-ost",
            algorithm="DDS",
            max_iterations=50,
            lowerBounds=HMETS.Params(),
            upperBounds=HMETS.Params(),
            run_name="run",
            run_index=0,
            suppress_output=True,
        )

        ####################
        # R V C (OST TMPL) #
        ####################

        rvc_tmpl = """
        # Tied parameters:
        # (it is important for OSTRICH to find every parameter place holder somewhere in this file)
        # (without this "par_x20" and "par_x21" wouldn't be detectable)
        #    para_half_x20 = para_x20 / 2. = par_x20 / 2. [m] = par_half_x20 [mm]
        #    para_half_x21 = para_x21 / 2. = par_x21 / 2. [m] = par_half_x21 [mm]


        # initialize to 1/2 full
        :UniformInitialConditions SOIL[0] par_half_x20
        :UniformInitialConditions SOIL[1] par_half_x21

        :HRUStateVariableTable (formerly :IntialConditionsTable)
           :Attributes SOIL[0] SOIL[1]
           :Units mm mm
           1 par_half_x20 par_half_x21
        :EndHRUStateVariableTable
        """
        self.config.rvc.set_tmpl(rvc_tmpl, is_ostrich=True)

        ####################
        # R V P (OST TMPL) #
        ####################

        rvp_tmpl = """
        # tied parameters:
        # (it is important for OSTRICH to find every parameter place holder somewhere in this file)
        # (without this "par_x06" and "par_x10" wouldn't be detectable)
        #    para_sum_x05_x06 = par_x05 + par_x06
        #    para_sum_x09_x10 = par_x09 + par_x10

        #-----------------------------------------------------------------
        # Soil Classes
        #-----------------------------------------------------------------
        :SoilClasses
          :Attributes,
          :Units,
          TOPSOIL,
          PHREATIC,
        :EndSoilClasses

        #-----------------------------------------------------------------
        # Land Use Classes
        #-----------------------------------------------------------------
        :LandUseClasses,
          :Attributes,        IMPERM,    FOREST_COV,
               :Units,          frac,          frac,
               FOREST,           0.0,           1.0,
        :EndLandUseClasses

        #-----------------------------------------------------------------
        # Vegetation Classes
        #-----------------------------------------------------------------
        :VegetationClasses,
          :Attributes,        MAX_HT,       MAX_LAI, MAX_LEAF_COND,
               :Units,             m,          none,      mm_per_s,
               FOREST,             4,             5,             5,
        :EndVegetationClasses

        #-----------------------------------------------------------------
        # Soil Profiles
        #-----------------------------------------------------------------
        :SoilProfiles
                 LAKE, 0
                 ROCK, 0
          DEFAULT_P, 2, TOPSOIL,    par_x20, PHREATIC,    par_x21,
        # DEFAULT_P, 2, TOPSOIL, x(20)/1000, PHREATIC, x(21)/1000,
        :EndSoilProfiles

        #-----------------------------------------------------------------
        # Global Parameters
        #-----------------------------------------------------------------
        :GlobalParameter         SNOW_SWI_MIN par_x09           # x(9)
        :GlobalParameter         SNOW_SWI_MAX par_sum_x09_x10   # x(9)+x(10)
        :GlobalParameter     SWI_REDUCT_COEFF par_x11           # x(11)
        :GlobalParameter             SNOW_SWI 0.05   #not sure why/if needed...

        #-----------------------------------------------------------------
        # Soil Parameters
        #-----------------------------------------------------------------
        :SoilParameterList
          :Parameters,        POROSITY,      PERC_COEFF,  PET_CORRECTION, BASEFLOW_COEFF
               :Units,               -,             1/d,               -,            1/d
              TOPSOIL,             1.0,         par_x17,         par_x15,        par_x18
             PHREATIC,             1.0,             0.0,             0.0,        par_x19
         #    TOPSOIL,             1.0,           x(17),           x(15),          x(18)
         #   PHREATIC,             1.0,             0.0,             0.0,          x(19)
        :EndSoilParameterList

        #-----------------------------------------------------------------
        # Land Use Parameters
        #-----------------------------------------------------------------
        :LandUseParameterList
          :Parameters, MIN_MELT_FACTOR, MAX_MELT_FACTOR,    DD_MELT_TEMP,  DD_AGGRADATION, REFREEZE_FACTOR,    REFREEZE_EXP, DD_REFREEZE_TEMP, HMETS_RUNOFF_COEFF,
               :Units,          mm/d/C,          mm/d/C,               C,            1/mm,          mm/d/C,               -,                C,                  -,
            [DEFAULT],         par_x05, par_sum_x05_x06,         par_x07,         par_x08,         par_x13,         par_x14,          par_x12,            par_x16,
        #                         x(5),       x(5)+x(6),            x(7),            x(8),           x(13),           x(14),            x(12),              x(16),
        :EndLandUseParameterList
        :LandUseParameterList
          :Parameters,   GAMMA_SHAPE,     GAMMA_SCALE,    GAMMA_SHAPE2,    GAMMA_SCALE2,
               :Units,             -,               -,               -,               -,
            [DEFAULT],       par_x01,         par_x02,         par_x03,         par_x04,
            #                   x(1),            x(2),            x(3),            x(4),
        :EndLandUseParameterList
        #-----------------------------------------------------------------
        # Vegetation Parameters
        #-----------------------------------------------------------------
        :VegetationParameterList
          :Parameters,  RAIN_ICEPT_PCT,  SNOW_ICEPT_PCT,
               :Units,               -,               -,
            [DEFAULT],             0.0,             0.0,
        :EndVegetationParameterList
        """
        self.config.rvp.set_tmpl(rvp_tmpl, is_ostrich=True)

        #########
        # O S T #
        #########

        ost_tmpl = """
        ProgramType         {algorithm}
        ObjectiveFunction   GCOP
        ModelExecutable     ./ostrich-runs-raven.sh
        PreserveBestModel   ./save_best.sh
        #OstrichWarmStart   yes

        ModelSubdir processor_

        BeginExtraDirs
        model
        #best
        EndExtraDirs

        BeginFilePairs
          {identifier}.rvp.tpl;  {identifier}.rvp
          {identifier}.rvc.tpl;  {identifier}.rvc
          #can be multiple (.rvh, .rvi)
        EndFilePairs

        #Parameter/DV Specification
        BeginParams
          #parameter      init.    low      high    tx_in  tx_ost  tx_out
          par_x01         random   {lowerBounds.GAMMA_SHAPE}         {upperBounds.GAMMA_SHAPE}	       none   none     none
          par_x02         random   {lowerBounds.GAMMA_SCALE}	     {upperBounds.GAMMA_SCALE}	       none   none     none
          par_x03         random   {lowerBounds.GAMMA_SHAPE2}	     {upperBounds.GAMMA_SHAPE2}       none   none     none
          par_x04         random   {lowerBounds.GAMMA_SCALE2}	     {upperBounds.GAMMA_SCALE2}       none   none     none
          par_x05         random   {lowerBounds.MIN_MELT_FACTOR}     {upperBounds.MIN_MELT_FACTOR}    none   none     none
          par_x06         random   {lowerBounds.MAX_MELT_FACTOR}     {upperBounds.MAX_MELT_FACTOR}    none   none     none
          par_x07         random   {lowerBounds.DD_MELT_TEMP}	     {upperBounds.DD_MELT_TEMP}       none   none     none
          par_x08         random   {lowerBounds.DD_AGGRADATION}	     {upperBounds.DD_AGGRADATION}     none   none     none
          par_x09         random   {lowerBounds.SNOW_SWI_MIN}	     {upperBounds.SNOW_SWI_MIN}       none   none     none
          par_x10         random   {lowerBounds.SNOW_SWI_MAX}	     {upperBounds.SNOW_SWI_MAX}       none   none     none
          par_x11         random   {lowerBounds.SWI_REDUCT_COEFF}    {upperBounds.SWI_REDUCT_COEFF}   none   none     none
          par_x12         random   {lowerBounds.DD_REFREEZE_TEMP}    {upperBounds.DD_REFREEZE_TEMP}   none   none     none
          par_x13         random   {lowerBounds.REFREEZE_FACTOR}     {upperBounds.REFREEZE_FACTOR}    none   none     none
          par_x14         random   {lowerBounds.REFREEZE_EXP}	     {upperBounds.REFREEZE_EXP}       none   none     none
          par_x15         random   {lowerBounds.PET_CORRECTION}	     {upperBounds.PET_CORRECTION}     none   none     none
          par_x16         random   {lowerBounds.HMETS_RUNOFF_COEFF}  {upperBounds.HMETS_RUNOFF_COEFF} none   none     none
          par_x17         random   {lowerBounds.PERC_COEFF}	     {upperBounds.PERC_COEFF}	       none   none     none
          par_x18         random   {lowerBounds.BASEFLOW_COEFF_1}    {upperBounds.BASEFLOW_COEFF_1}   none   none     none
          par_x19         random   {lowerBounds.BASEFLOW_COEFF_2}    {upperBounds.BASEFLOW_COEFF_2}   none   none     none
          par_x20         random   {lowerBounds.TOPSOIL}	     {upperBounds.TOPSOIL}	       none   none     none
          par_x21         random   {lowerBounds.PHREATIC}            {upperBounds.PHREATIC}           none   none     none
        EndParams

        BeginTiedParams
          # par_sum_x05_x06 = par_x05 + par_x06
          # Xtied =(c3 * X1 * X2) + (c2 * X2) + (c1 * X1) + c0
          # --> c0 = 0.0
          # --> c1 = 1.0
          # --> c2 = 1.0
          # --> c3 = 0.0
          #
          par_sum_x05_x06 2 par_x05 par_x06 linear 0.00 1.00 1.00 0.00 free
          #
          # par_sum_x09_x10 = par_x09 + par_x10
          # Xtied =(c3 * X1 * X2) + (c2 * X2) + (c1 * X1) + c0
          # --> c0 = 0.0
          # --> c1 = 1.0
          # --> c2 = 1.0
          # --> c3 = 0.0
          #
          par_sum_x09_x10 2 par_x09 par_x10 linear 0.00 1.00 1.00 0.00 free
          #
          # par_half_x20 = par_x20 * 0.5 * 1000  --> half of it but in [mm] not [m]
          # Xtied = (c1 * X) + c0
          # --> c0 = 0.0
          # --> c1 = 500.
          #
          par_half_x20 1 par_x20 linear 500.0 0.0 free
          #
          # par_half_x21 = par_x21 * 0.5 * 1000  --> half of it but in [mm] not [m]
          # Xtied = (c1 * X) + c0
          # --> c0 = 0.0
          # --> c1 = 500.
          #
          par_half_x21 1 par_x21 linear 500.0 0.0 free
        EndTiedParams

        BeginResponseVars
          #name   filename                              keyword         line    col     token
          NS      ./model/output/{run_name}-{run_index}_Diagnostics.csv;       OST_NULL        1       3       ','
        EndResponseVars

        BeginTiedRespVars
          NegNS 1 NS wsum -1.00
        EndTiedRespVars

        BeginGCOP
          CostFunction NegNS
          PenaltyFunction APM
        EndGCOP

        BeginConstraints
                # not needed when no constraints, but PenaltyFunction statement above is required
                # name     type     penalty    lwr   upr   resp.var
        EndConstraints

        # Randomsed control added
        {random_seed}

        #Algorithm should be last in this file:

        BeginDDSAlg
                PerturbationValue 0.20
                MaxIterations {max_iterations}
                UseRandomParamValues
                # UseInitialParamValues
                # above intializes DDS to parameter values IN the initial model input files
        EndDDSAlg
        """
        self.config.ost.set_tmpl(ost_tmpl)

    def derived_parameters(self):
        """Derived parameters are computed by Ostrich."""
        pass

    def ost2raven(self, ops: dict) -> HMETS.Params:
        """Return a list of parameter names calibrated by Ostrich that match Raven's parameters.

        Parameters
        ----------
        ops: dict
          Optimal parameter set returned by Ostrich.

        Returns
        -------
        HMETSParams named tuple
          Parameters expected by Raven.
        """
        names = ["par_x{:02}".format(i) for i in range(1, 22)]
        names[5] = "par_sum_x05_x06"
        names[9] = "par_sum_x09_x10"

        out = [ops[n] for n in names]
        out[19] *= 1000
        out[20] *= 1000
        return HMETS.Params(*out)