from textwrap import dedent

from ravenpy.config.commands import (
    AdiabaticLapseRate,
    HRUState,
    HRUStateVariableTableCommand,
    PotentialMeltMethod,
    SuppressOutput,
)
from ravenpy.config.options import PotentialMelt


def test_adiabatic_lapse_rate_coefficient():
    alr = AdiabaticLapseRate(0.2)
    assert alr.to_rv() == ":AdiabaticLapseRate   0.2\n"


def test_potential_melt_method_option():
    expected = ":PotentialMeltMethod  POTMELT_EB\n"
    assert PotentialMeltMethod("POTMELT_EB").to_rv() == expected
    assert PotentialMeltMethod(PotentialMelt.EB).to_rv() == expected


def test_suppress_output():
    assert SuppressOutput(True).to_rv() == ":SuppressOutput\n"
    assert SuppressOutput(False).to_rv() == ""


def test_hru_state():
    s = HRUState(index=1, data={"SOIL[0]": 1, "SOIL[1]": 2.0})
    assert s.to_rv() == "1,1.0,2.0"


class TestHRUStateVariableTableCommand:
    def test_to_rv(self):
        s1 = HRUState(index=1, data={"SOIL[0]": 0.1, "SOIL[1]": 1.0})
        s2 = HRUState(index=2, data={"SOIL[3]": 3, "SOIL[2]": 2.0})
        t = HRUStateVariableTableCommand(hru_states={1: s1, 2: s2})
        assert dedent(t.to_rv()) == dedent(
            """
            :HRUStateVariableTable
                :Attributes,SOIL[0],SOIL[1],SOIL[2],SOIL[3]
                1,0.1,1.0,0.0,0.0
                2,0.0,0.0,2.0,3.0
            :EndHRUStateVariableTable
            """
        )

    def test_parse(self):
        solution = """
:HRUStateVariableTable
  :Attributes,SURFACE_WATER,ATMOSPHERE,ATMOS_PRECIP,PONDED_WATER,SOIL[0],SOIL[1],SNOW,SNOW_LIQ,CUM_SNOWMELT,CONVOLUTION[0],CONVOLUTION[1],AET,CONV_STOR[0],CONV_STOR[1],CONV_STOR[2],CONV_STOR[3],CONV_STOR[4],CONV_STOR[5],CONV_STOR[6],CONV_STOR[7],CONV_STOR[8],CONV_STOR[9],CONV_STOR[10],CONV_STOR[11],CONV_STOR[12],CONV_STOR[13],CONV_STOR[14],CONV_STOR[15],CONV_STOR[16],CONV_STOR[17],CONV_STOR[18],CONV_STOR[19],CONV_STOR[20],CONV_STOR[21],CONV_STOR[22],CONV_STOR[23],CONV_STOR[24],CONV_STOR[25],CONV_STOR[26],CONV_STOR[27],CONV_STOR[28],CONV_STOR[29],CONV_STOR[30],CONV_STOR[31],CONV_STOR[32],CONV_STOR[33],CONV_STOR[34],CONV_STOR[35],CONV_STOR[36],CONV_STOR[37],CONV_STOR[38],CONV_STOR[39],CONV_STOR[40],CONV_STOR[41],CONV_STOR[42],CONV_STOR[43],CONV_STOR[44],CONV_STOR[45],CONV_STOR[46],CONV_STOR[47],CONV_STOR[48],CONV_STOR[49],CONV_STOR[50],CONV_STOR[51],CONV_STOR[52],CONV_STOR[53],CONV_STOR[54],CONV_STOR[55],CONV_STOR[56],CONV_STOR[57],CONV_STOR[58],CONV_STOR[59],CONV_STOR[60],CONV_STOR[61],CONV_STOR[62],CONV_STOR[63],CONV_STOR[64],CONV_STOR[65],CONV_STOR[66],CONV_STOR[67],CONV_STOR[68],CONV_STOR[69],CONV_STOR[70],CONV_STOR[71],CONV_STOR[72],CONV_STOR[73],CONV_STOR[74],CONV_STOR[75],CONV_STOR[76],CONV_STOR[77],CONV_STOR[78],CONV_STOR[79],CONV_STOR[80],CONV_STOR[81],CONV_STOR[82],CONV_STOR[83],CONV_STOR[84],CONV_STOR[85],CONV_STOR[86],CONV_STOR[87],CONV_STOR[88],CONV_STOR[89],CONV_STOR[90],CONV_STOR[91],CONV_STOR[92],CONV_STOR[93],CONV_STOR[94],CONV_STOR[95],CONV_STOR[96],CONV_STOR[97],CONV_STOR[98],CONV_STOR[99]
  :Units,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm,mm
  1,0.00000,0.00000,-0.16005,0.00000,144.54883,455.15708,0.16005,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
:EndHRUStateVariableTable
        """
        sv = HRUStateVariableTableCommand.parse(solution)
        assert len(sv.hru_states) == 1
        assert sv.hru_states[1].index == 1
        assert sv.hru_states[1].data["ATMOS_PRECIP"] == -0.16005
