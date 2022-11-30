from enum import Enum
from typing import Literal

# Allowed soil parameters
SoilParameters = Literal[
    "SAND_CON",
    "CLAY_CON",
    "SILT_CON",
    "ORG_CON",
    "POROSITY",
    "STONE_FRAC",
    "SAT_WILT",
    "FIELD_CAPACITY",
    "BULK_DENSITY",
    "HYDRAUL_COND",
    "CLAPP_B",
    "CLAPP N,CLAPP M",
    "SAT_RES",
    "AIR_ENTRY_PRESSURE",
    "WILTING_PRESSURE",
    "HEAT_CAPACITY",
    "THERMAL_COND",
    "WETTING_FRONT_PSI",
    "EVAP_RES_FC",
    "SHUTTLEWORTH_B",
    "ALBEDO_WET",
    "ALBEDO_DRY",
    "VIZ_ZMIN",
    "VIC_ZMAX",
    "VIC ALPHA",
    "VIC_EVAP_GAMMA",
    "MAX_PERC_RATE",
    "PERC_N",
    "SAC_PERC_ALPHA",
    "SAC_PERC_EXPON",
    "HBV_BETA",
    "MAX_BASEFLOW_RATE",
    "BASEFLOW_N",
    "BASEFLOW_COEFF",
    "BASEFLOW_COEF2",
    "BASEFLOW_THRESH",
    "BF_LOSS_FRACTION",
    "STORAGE_THRESHOLD",
    "MAX_CAP_RISE_RATE",
    "MAX_INTERFLOW_RATE",
    "INTERFLOW_COEF",
    "UBC_EVAL_SOIL_DEF",
    "UBC_INFIL_SOIL_DEF",
    "GR4J_X2",
    "GR4J_X3",
]

StateVariables = Literal[
    "SURFACE_WATER",
    "ATMOSPHERE",
    "ATMOS_PRECIP",
    "PONDED_WATER",
    "SOIL",
    "GROUNDWATER",
    "CANOPY",
    "CANOPY_SNOW",
    "TRUNK",
    "ROOT",
    "DEPRESSION",
    "WETLAND",
    "LAKE_STORAGE",
    "SNOW",
    "SNOW_LIQ",
    "GLACIER",
    "GLACIER_ICE",
    "CONVOLUTION",
    "CONV_STOR",
    "SURFACE_WATER_TEMP",
    "SNOW_TEMP",
    "COLD_CONTENT",
    "GLACIER_CC",
    "SOIL_TEMP",
    "CANOPY_TEMP",
    "SNOW_DEPTH",
    "PERMAFROST_DEPTH",
    "SNOW_COVER",
    "SNOW_AGE",
    "SNOW_ALBEDO",
    "CROP_HEAT_UNITS",
    "CUM_INFIL",
    "CUM_SNOWMELT",
    "CONSTITUENT",
    "CONSTITUENT_SRC",
    "CONSTITUENT_SW",
    "CONSTITUENT_SINK",
]

LandUseParameters = Literal[
    "FOREST_COVERAGE",
    "IMPERMEABLE_FRAC",
    "ROUGHNESS",
    "FOREST_SPARSENESS",
    "DEP_MAX",
    "MAX_DEP_AREA_FRAC",
    "DD_MELT_TEMP",
    "MELT_FACTOR",
    "DD_REFREEZE_TEMP",
    "MIN_MELT_FACTOR",
    "REFREEZE_FACTOR",
    "REFREEZE_EXP",
    "DD_AGGRADATION",
    "SNOW_PATCH_LIMIT",
    "HBV_MELT_FOR_CORR",
    "HBV_MELT_ASP_CORR",
    "GLAC_STORAGE_COEFF",
    "HBV_MELT_GLACIER_CORR",
    "HBV_GLACIER_KMIN",
    "HBV_GLACIER_AG",
    "CC_DECAY_COEFF",
    "SCS_CN",
    "SCS_IA_FRACTION",
    "PARTITION_COEFF",
    "MAX_SAT_AREA_FRAC",
    "B_EXP",
    "ABST_PERCENT",
    "DEP_MAX_FLOW",
    "DEP_N",
    "DEP_SEEP_K",
    "DEP_K",
    "DEP_THRESHOLD",
    "PDMROF_B",
    "PONDED_EXP",
    "OW_PET_CORR",
    "LAKE_PET_CORR",
    "LAKE_REL_COEFF",
    "FOREST_PET_CORR",
    "GAMMA_SCALE",
    "GAMMA_SHAPE",
    "HMETS_RUNOFF_COEFF",
    "AET_COEFF",
    "GR4J_X4",
    "UBC_ICEPT_FACTOR",
]

VegetationParameters = Literal[
    "MAX_HEIGHT",
    "MAX_LEAF_COND",
    "MAX_LAI",
    "SVF_EXTINCTION",
    "RAIN_ICEPT_PCT",
    "SNOW_ICEPT_PCT",
    "RAIN_ICEPT_FACT",
    "SNOW_ICEPT_FACT",
    "SAI_HT_RATIO",
    "TRUNK_FRACTION",
    "STEMFLOW_FRAC",
    "ALBEDO",
    "ALBEDO_WET",
    "MAX_CAPACITY",
    "MAX_SNOW_CAPACITY",
    "ROOT_EXTINCT",
    "MAX_ROOT_LENGTH",
    "MIN_RESISTIVITY",
    "XYLEM_FRAC",
    "ROOTRADIUS",
    "PSI_CRITICAL",
    "DRIP_PROPORTION",
    "MAX_INTERCEPT_RATE",
    "CHU_MATURITY",
    "PET_VEG_CORR",
]


class AirPressureMethod(Enum):
    BASIC = "AIRPRESS_BASIC"  # Default
    CONST = "AIRPRESS_CONST"
    DATA = "AIRPRESS_DATA"
    UBC = "AIRPRESS_UBC"


class Calendar(Enum):
    PROLEPTIC_GREGORIAN = "PROLEPTIC_GREGORIAN"
    JULIAN = "JULIAN"
    GREGORIAN = "GREGORIAN"
    STANDARD = "STANDARD"
    NOLEAP = "NOLEAP"
    _365_DAY = "365_DAY"
    ALL_LEAP = "ALL_LEAP"
    _366_DAY = "366_DAY"


class CatchmentRoute(Enum):
    """:CatchmentRoute"""

    DUMP = "ROUTE_DUMP"
    GAMMA = "ROUTE_GAMMA_CONVOLUTION"
    TRI = "ROUTE_TRI_CONVOLUTION"
    RESERVOIR = "ROUTE_RESERVOIR_SERIES"
    EXP = "ROUTE_EXPONENTIAL"


class CloudCoverMethod(Enum):
    NONE = "CLOUDCOV_NONE"  # default
    DATA = "CLOUDCOV_DATA"  # gauge or gridded time series used
    UBC = "CLOUDCOV_UBC"


class EvaluationMetrics(Enum):
    NASH_SUTCLIFFE = "NASH_SUTCLIFFE"
    LOG_NASH = "LOG_NASH"
    RMSE = "RMSE"
    PCT_BIAS = "PCT_BIAS"
    ABSERR = "ABSERR"
    ABSMAX = "ABSMAX"
    PDIFF = "PDIFF"
    TMVOL = "TMVOL"
    RCOEFF = "RCOEFF"
    NSC = "NSC"
    KLING_GUPTA = "KLING_GUPTA"


class Evaporation(Enum):
    PET_CONSTANT = "PET_CONSTANT"
    PET_PENMAN_MONTEITH = "PET_PENMAN_MONTEITH"
    PET_PENMAN_COMBINATION = "PET_PENMAN_COMBINATION"
    PET_PRIESTLEY_TAYLOR = "PET_PRIESTLEY_TAYLOR"
    PET_HARGREAVES = "PET_HARGREAVES"
    PET_HARGREAVES_1985 = "PET_HARGREAVES_1985"
    PET_FROMMONTHLY = "PET_FROMMONTHLY"
    PET_DATA = "PET_DATA"
    PET_HAMON_1961 = "PET_HAMON_1961"
    PET_TURC_1961 = "PET_TURC_1961"
    PET_MAKKINK_1957 = "PET_MAKKINK_1957"
    PET_MONTHLY_FACTOR = "PET_MONTHLY_FACTOR"
    PET_MOHYSE = "PET_MOHYSE"
    PET_OUDIN = "PET_OUDIN"


class LWRadiationMethod(Enum):
    DATA = "LW_RAD_DATA"
    DEFAULT = "LW_RAD_DEFAULT"
    UBCWM = "LW_RAD_UBC"


class MonthlyInterpolationMethod(Enum):
    UNIFORM = "MONTHINT_UNIFORM"
    LINEAR_MID = "MONTHINT_LINEAR_MID"
    LINEAR_FOM = "MONTHINT_LINEAR_FOM"
    LINEAR_21 = "MONTHINT_LINEAR_21"


class OroPETCorrect(Enum):
    NONE = "OROCORR_NONE"
    SIMPLELAPSE = "OROCORR_SIMPLELAPSE"
    HBV = "OROCORR_HBV"


class OroPrecipCorrect(Enum):
    NONE = "OROCORR_NONE"
    UBC = "OROCORR_UBC"
    HBV = "OROCORR_HBV"
    SIMPLELAPSE = "OROCORR_SIMPLELAPSE"


class PotentialMeltMethod(Enum):
    """:PotentialMelt algorithms"""

    DEGREE_DAY = "POTMELT_DEGREE_DAY"
    RESTRICTED = "POTMELT_RESTRICTED"
    DATA = "POTMELT_DATA"
    EB = "POTMELT_EB"
    USACE = "POTMELT_USACE"
    HMETS = "POTMELT_HMETS"
    HBV = "POTMELT_HBV"
    UBC = "POTMELT_UBC"


class PrecipIceptFract(Enum):
    """"""

    USER = "PRECIP_ICEPT_USER"  # default
    LAI = "PRECIP_ICEPT_LAI"
    EXPLAI = "PRECIP_ICEPT_EXPLAI"
    NONE = "PRECIP_ICEPT_NONE"
    HEDSTROM = "PRECIP_ICEPT_HEDSTROM"


class RainSnowFraction(Enum):
    DATA = "RAINSNOW_DATA"
    DINGMAN = "RAINSNOW_DINGMAN"
    UBC = "RAINSNOW_UBC"
    HBV = "RAINSNOW_HBV"
    HARDER = "RAINSNOW_HARDER"
    HSPF = "RAINSNOW_HSPF"


class RelativeHumidityMethod(Enum):
    CONSTANT = "RELHUM_CONSTANT"
    DATA = "RELHUM_DATA"
    MINDEWPT = "RELHUM_MINDEWPT"


class Routing(Enum):
    DIFFUSIVE_WAVE = "ROUTE_DIFFUSIVE_WAVE"
    HYDROLOGIC = "ROUTE_HYDROLOGIC"
    NONE = "ROUTE_NONE"
    STORAGE_COEFF = "ROUTE_STORAGE_COEFF"
    PLUG_FLOW = "ROUTE_PLUG_FLOW"
    MUSKINGUM = "MUSKINGUM"


class SoilModel(Enum):
    ONE_LAYER = "SOIL_ONE_LAYER"
    TWO_LAYER = "SOIL_TWO_LAYER"
    MULTILAYER = "SOIL_MULTILAYER"


class SubdailyMethod(Enum):
    NONE = "SUBDAILY_NONE"
    SIMPLE = "SUBDAILY_SIMPLE"
    UBC = "SUBDAILY_UBC"


class SWCanopyCorrect(Enum):
    NONE = "SW_CANOPY_CORR_NONE"  # Default
    STATIC = "SW_CANOPY_CORR_STATIC"
    DYNAMIC = "SW_CANOPY_CORR_DYNAMIC"
    UBC = "SW_CANOPY_CORR_UBC"


class SWCloudCorrect(Enum):
    NONE = "SW_CLOUDCOV_CORR_NONE"  # Default
    DINGMAN = "SW_CLOUDCOV_CORR_DINGMAN"
    UBC = "SW_CLOUDCOV_CORR_UBC"


class SWRadiationMethod(Enum):
    DATA = "SW_RAD_DATA"
    DEFAULT = "SW_RAD_DEFAULT"
    UBCWM = "SW_RAD_UBCWM"


class WindspeedMethod(Enum):
    CONSTANT = "WINDVEL_CONSTANT"
    DATA = "WINDVEL_DATA"
    UBC = "WINDVEL_UBC"