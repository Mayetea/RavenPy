from collections import defaultdict
from pathlib import Path
from typing import cast

from pydantic.dataclasses import dataclass

from ravenpy.config import options
from ravenpy.config.commands import HRU, LU, BasinIndexCommand, HRUState, Sub
from ravenpy.models.base import Ostrich, Raven

from .gr4jcn import GR4JCN


class MOHYSE(Raven):
    """Modèle Hydrologique Simplifié à l'Extrême (MOHYSE)

    References
    ----------
    Fortin, V.; Turcotte, R. Le modèle hydrologique MOHYSE. In Note de Cours Pour SCA7420,
    Université du Québec à Montréal: Montréal, QC, Canada, 2007; p. 14.

    Troin, M., Arsenault, R. and Brissette, F., 2015. Performance and uncertainty evaluation
    of snow models on snowmelt flow simulations over a Nordic catchment (Mistassibi, Canada).
    Hydrology, 2(4), pp.289-317.
    """

    @dataclass
    class Params:
        par_x01: float
        par_x02: float
        par_x03: float
        par_x04: float
        par_x05: float
        par_x06: float
        par_x07: float
        par_x08: float
        par_x09: float
        par_x10: float

    def __init__(self, *args, **kwds):
        kwds["identifier"] = kwds.get("identifier", "mohyse")
        super().__init__(*args, **kwds)

        self.config.update(
            hrus=(GR4JCN.LandHRU(),),
            subbasins=(
                Sub(
                    subbasin_id=1,
                    name="sub_001",
                    downstream_id=-1,
                    profile="None",
                    gauged=True,
                ),
            ),
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
          TOPSOIL
          GWSOIL
        :EndSoilClasses

        #-----------------------------------------------------------------
        # Land Use Classes
        #-----------------------------------------------------------------
        :LandUseClasses,
          :Attributes,        IMPERM,    FOREST_COV,
          :Units,             frac,      frac,
          LU_ALL,             0.0,       1.0
        :EndLandUseClasses

        #-----------------------------------------------------------------
        # Vegetation Classes
        #-----------------------------------------------------------------
        :VegetationClasses,
          :Attributes,        MAX_HT,       MAX_LAI,    MAX_LEAF_COND,
          :Units,             m,            none,       mm_per_s,
         VEG_ALL,             0.0,          0.0,        0.0
        :EndVegetationClasses

        #-----------------------------------------------------------------
        # Soil Profiles
        #-----------------------------------------------------------------
        :SoilProfiles
                 LAKE, 0
                 ROCK, 0
               # DEFAULT_P,      2, TOPSOIL, MOHYSE_PARA_5, GWSOIL, 10.0
                 DEFAULT_P,      2, TOPSOIL,     {params.par_x05}, GWSOIL, 10.0
        :EndSoilProfiles

        #-----------------------------------------------------------------
        # Global Parameters
        #-----------------------------------------------------------------
        #:GlobalParameter      RAINSNOW_TEMP              -2.0
        :GlobalParameter       TOC_MULTIPLIER              1.0
        # :GlobalParameter     MOHYSE_PET_COEFF  MOHYSE_PARA_1
        :GlobalParameter       MOHYSE_PET_COEFF      {params.par_x01}

        #-----------------------------------------------------------------
        # Soil Parameters
        #-----------------------------------------------------------------
        :SoilParameterList
          :Parameters,        POROSITY,  PET_CORRECTION,        HBV_BETA,  BASEFLOW_COEFF,      PERC_COEFF,
               :Units,               -,               -,               -,             1/d,             1/d, # (units not generated by .rvp template)
            # TOPSOIL,            1.0 ,             1.0,             1.0,   MOHYSE_PARA_7,   MOHYSE_PARA_6,
            #  GWSOIL,            1.0 ,             1.0,             1.0,   MOHYSE_PARA_8,             0.0,
              TOPSOIL,            1.0 ,             1.0,             1.0,       {params.par_x07},       {params.par_x06},
               GWSOIL,            1.0 ,             1.0,             1.0,       {params.par_x08},             0.0,
        :EndSoilParameterList

        #-----------------------------------------------------------------
        # Land Use Parameters
        #-----------------------------------------------------------------
        :LandUseParameterList
          :Parameters,     MELT_FACTOR,       AET_COEFF, FOREST_SPARSENESS, DD_MELT_TEMP,
               :Units,          mm/d/K,            mm/d,                 -,         degC,
          # [DEFAULT],   MOHYSE_PARA_3,   MOHYSE_PARA_2,               0.0,MOHYSE_PARA_4,
            [DEFAULT],       {params.par_x03},       {params.par_x02},               0.0,    {params.par_x04},
        :EndLandUseParameterList

        #-----------------------------------------------------------------
        # Vegetation Parameters
        #-----------------------------------------------------------------
        :VegetationParameterList
          :Parameters,    SAI_HT_RATIO,  RAIN_ICEPT_PCT,  SNOW_ICEPT_PCT,
               :Units,               -,               -,               -,
            [DEFAULT],             0.0,             0.0,             0.0,
        :EndVegetationParameterList
        """
        self.config.rvp.set_tmpl(rvp_tmpl)

        #########
        # R V I #
        #########

        rvi_tmpl = """
        :SoilModel             SOIL_TWO_LAYER
        :PotentialMeltMethod   POTMELT_DEGREE_DAY
        :Routing               ROUTE_NONE
        :CatchmentRoute        ROUTE_GAMMA_CONVOLUTION
        :Evaporation           {evaporation}  # PET_MOHYSE
        :DirectEvaporation
        :RainSnowFraction      {rain_snow_fraction}

        :HydrologicProcesses
             :SoilEvaporation  SOILEVAP_LINEAR    SOIL[0]            ATMOSPHERE
             :SnowBalance      SNOBAL_SIMPLE_MELT SNOW PONDED_WATER
             :Precipitation    RAVEN_DEFAULT      ATMOS_PRECIP       MULTIPLE
             :Infiltration     INF_HBV            PONDED_WATER       SOIL[0]
             :Baseflow         BASE_LINEAR        SOIL[0]            SURFACE_WATER
             :Percolation      PERC_LINEAR        SOIL[0]            SOIL[1]
             :Baseflow         BASE_LINEAR        SOIL[1]            SURFACE_WATER
        :EndHydrologicProcesses

        #:CreateRVPTemplate

        # :Alias MOHYSE_PARA_1      1.5589    # :GlobalParameter         MOHYSE_PET_COEFF
        # :Alias MOHYSE_PARA_2	    0.9991    # LandUseParameterList --> AET_COEFF
        # :Alias MOHYSE_PARA_3	    2.1511    # LandUseParameterList --> MELT_FACTOR
        # :Alias MOHYSE_PARA_4	   -1.6101    # LandUseParameterList --> DD_MELT_TEMP
        # :Alias MOHYSE_PARA_5	    0.5000    # SoilProfiles         --> thickness of TOPSOIL (in mm????? must be m!!!)
        # :Alias MOHYSE_PARA_6	    0.1050    # SoilParameterList    --> PERC_COEFF (TOPSOIL)
        # :Alias MOHYSE_PARA_7	    0.0533    # SoilParameterList    --> BASEFLOW_COEFF (TOPSOIL)
        # :Alias MOHYSE_PARA_8	    0.0132    # SoilParameterList    --> BASEFLOW_COEFF (GWSOIL)
        # :Alias MOHYSE_PARA_9	    1.0474    # :SubBasinProperties  --> GAMMA_SHAPE
        # :Alias MOHYSE_PARA_10	    7.9628    # :SubBasinProperties  --> TIME_CONC = MOHYSE_PARA_10 / 0.3 = 26.542666666
        """
        self.config.rvi.set_tmpl(rvi_tmpl)

        #########
        # R V H #
        #########

        rvh_tmpl = """
        {subbasins}

        {hrus}

        :SubBasinProperties
        #                  1.0 / MOHYSE_PARA_10,   MOHYSE_PARA_9
           :Parameters,             GAMMA_SCALE,     GAMMA_SHAPE,
           :Units,                          1/d,               -
                      1,         {par_rezi_x10},       {par_x09}
        :EndSubBasinProperties
        """
        self.config.rvh.set_tmpl(rvh_tmpl)

        #########
        # R V I #
        #########

        self.config.rvi.rain_snow_fraction = options.RainSnowFraction.DATA
        self.config.rvi.evaporation = "PET_MOHYSE"

    def derived_parameters(self):
        params = cast(MOHYSE.Params, self.config.rvp.params)

        par_rezi_x10 = 1.0 / params.par_x10

        self.config.rvp.set_extra_attributes(par_rezi_x10=par_rezi_x10)

        self.config.rvh.set_extra_attributes(
            par_rezi_x10=par_rezi_x10,
            par_x09=params.par_x09,
        )


class MOHYSE_OST(Ostrich, MOHYSE):
    def __init__(self, *args, **kwds):
        kwds["identifier"] = kwds.get("identifier", "mohyse-ost")
        super().__init__(*args, **kwds)

        self.config.update(
            algorithm="DDS",
            max_iterations=50,
            run_name="run",
            run_index=0,
            suppress_output=True,
        )

        ####################
        # R V P (OST TMPL) #
        ####################

        rvp_tmpl = """
        #-----------------------------------------------------------------
        # Soil Classes
        #-----------------------------------------------------------------
        :SoilClasses
          :Attributes,
          :Units,
          TOPSOIL
          GWSOIL
        :EndSoilClasses

        #-----------------------------------------------------------------
        # Land Use Classes
        #-----------------------------------------------------------------
        :LandUseClasses,
          :Attributes,        IMPERM,    FOREST_COV,
          :Units,             frac,      frac,
          LU_ALL,             0.0,       1.0
        :EndLandUseClasses

        #-----------------------------------------------------------------
        # Vegetation Classes
        #-----------------------------------------------------------------
        :VegetationClasses,
          :Attributes,        MAX_HT,       MAX_LAI,    MAX_LEAF_COND,
          :Units,             m,            none,       mm_per_s,
         VEG_ALL,             0.0,          0.0,        0.0
        :EndVegetationClasses

        #-----------------------------------------------------------------
        # Soil Profiles
        #-----------------------------------------------------------------
        :SoilProfiles
                 LAKE, 0
                 ROCK, 0
               # DEFAULT_P,      2, TOPSOIL, MOHYSE_PARA_5, GWSOIL, 10.0
                 DEFAULT_P,      2, TOPSOIL,       par_x05, GWSOIL, 10.0
        :EndSoilProfiles

        #-----------------------------------------------------------------
        # Global Parameters
        #-----------------------------------------------------------------
        #:GlobalParameter      RAINSNOW_TEMP              -2.0
        :GlobalParameter       TOC_MULTIPLIER              1.0
        # :GlobalParameter     MOHYSE_PET_COEFF  MOHYSE_PARA_1
        :GlobalParameter       MOHYSE_PET_COEFF        par_x01

        #-----------------------------------------------------------------
        # Soil Parameters
        #-----------------------------------------------------------------
        :SoilParameterList
          :Parameters,        POROSITY,  PET_CORRECTION,        HBV_BETA,  BASEFLOW_COEFF,      PERC_COEFF,
               :Units,               -,               -,               -,             1/d,             1/d, # (units not generated by .rvp template)
            # TOPSOIL,            1.0 ,             1.0,             1.0,   MOHYSE_PARA_7,   MOHYSE_PARA_6,
            #  GWSOIL,            1.0 ,             1.0,             1.0,   MOHYSE_PARA_8,             0.0,
              TOPSOIL,            1.0 ,             1.0,             1.0,         par_x07,         par_x06,
               GWSOIL,            1.0 ,             1.0,             1.0,         par_x08,             0.0,
        :EndSoilParameterList

        #-----------------------------------------------------------------
        # Land Use Parameters
        #-----------------------------------------------------------------
        :LandUseParameterList
          :Parameters,     MELT_FACTOR,       AET_COEFF, FOREST_SPARSENESS, DD_MELT_TEMP,
               :Units,          mm/d/K,            mm/d,                 -,         degC,
          # [DEFAULT],   MOHYSE_PARA_3,   MOHYSE_PARA_2,               0.0,MOHYSE_PARA_4,
            [DEFAULT],         par_x03,         par_x02,               0.0,      par_x04,
        :EndLandUseParameterList

        #-----------------------------------------------------------------
        # Vegetation Parameters
        #-----------------------------------------------------------------
        :VegetationParameterList
          :Parameters,    SAI_HT_RATIO,  RAIN_ICEPT_PCT,  SNOW_ICEPT_PCT,
               :Units,               -,               -,               -,
            [DEFAULT],             0.0,             0.0,             0.0,
        :EndVegetationParameterList
        """
        self.config.rvp.set_tmpl(rvp_tmpl, is_ostrich=True)

        ####################
        # R V H (OST TMPL) #
        ####################

        rvh_tmpl = """
        # tied parameters:
        # (it is important for OSTRICH to find every parameter place holder somewhere in this file)
        # (without this "par_x11" wouldn't be detectable)
        #    para_rezi_x10 = 1.0 / par_x10
        #    para_x11      = par_x11

        :SubBasins
                :Attributes     NAME    DOWNSTREAM_ID   PROFILE   REACH_LENGTH    GAUGED
                :Units          none    none            none      km              none
                1,            mohyse,   -1,             NONE,     _AUTO,          1
        :EndSubBasins

        :HRUs
                :Attributes     AREA    ELEVATION  LATITUDE    LONGITUDE   BASIN_ID  LAND_USE_CLASS  VEG_CLASS   SOIL_PROFILE  AQUIFER_PROFILE   TERRAIN_CLASS   SLOPE   ASPECT
                :Units           km2            m       deg          deg       none            none       none           none             none            none   ratio      deg
                     1,       4250.6,       843.0,  54.4848,   -123.3659,         1,         LU_ALL,   VEG_ALL,     DEFAULT_P,          [NONE],         [NONE], [NONE],  [NONE]
        :EndHRUs

        :SubBasinProperties
        #          1.0 / MOHYSE_PARA_10,   MOHYSE_PARA_9
           :Parameters,     GAMMA_SCALE,     GAMMA_SHAPE,
           :Units,                  1/d,               -
                      1,   par_rezi_x10,         par_x09
        :EndSubBasinProperties
        """
        self.config.rvh.set_tmpl(rvh_tmpl, is_ostrich=True)

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
          {identifier}.rvh.tpl;  {identifier}.rvh
          #can be multiple (.rvh, .rvi)
        EndFilePairs

        #Parameter/DV Specification
        BeginParams
          #parameter      init.    low      high    tx_in  tx_ost  tx_out
          par_x01         random   {lowerBounds.par_x01}  {upperBounds.par_x01}  none   none     none
          par_x02         random   {lowerBounds.par_x02}  {upperBounds.par_x02}  none   none     none
          par_x03         random   {lowerBounds.par_x03}  {upperBounds.par_x03}  none   none     none
          par_x04         random   {lowerBounds.par_x04}  {upperBounds.par_x04}  none   none     none
          par_x05         random   {lowerBounds.par_x05}  {upperBounds.par_x05}  none   none     none
          par_x06         random   {lowerBounds.par_x06}  {upperBounds.par_x06}  none   none     none
          par_x07         random   {lowerBounds.par_x07}  {upperBounds.par_x07}  none   none     none
          par_x08         random   {lowerBounds.par_x08}  {upperBounds.par_x08}  none   none     none
          par_x09         random   {lowerBounds.par_x09}  {upperBounds.par_x09}  none   none     none
          par_x10         random   {lowerBounds.par_x10}  {upperBounds.par_x10}  none   none     none
        EndParams

        BeginTiedParams
          # 2-parameter ratio (par_rezi_x10 = 1.0 / par_x10 )
          # Xtied =(c3 * par_x10 + c2)/(c1 * par_x10 + c0)
          #   --> c3 = 0.0
          #   --> c2 = 1.0
          #   --> c1 = 1.0
          #   --> c0 = 0.0
          par_rezi_x10 2 par_x10 par_x10 ratio 0.00 1.00 1.00 0.00 free
        EndTiedParams

        BeginResponseVars
          #name   filename                              keyword         line    col     token
          RawMetric  ./model/output/{identifier}-{run_index}_Diagnostics.csv;       OST_NULL        1       3       ','
        EndResponseVars

        BeginTiedRespVars
        # <name1> <np1> <pname 1,1 > <pname 1,2 > ... <pname 1,np1 > <type1> <type_data1>
          Metric 1 RawMetric wsum {evaluation_metric_multiplier}
        EndTiedRespVars

        BeginGCOP
          CostFunction Metric
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
