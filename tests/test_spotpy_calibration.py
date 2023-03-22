import datetime as dt
import time

import pytest
import spotpy

# from ravenpy.models import GR4JCN
from ravenpy.utilities.calibration import SpotpySetup, SpotSetup

from ravenpy.new_config.emulators.gr4jcn import GR4JCN
from ravenpy.new_config.emulators.hmets import HMETS
from ravenpy.new_config.emulators.mohyse import Mohyse



from ravenpy.new_config import commands as rc

salmon_river = "raven-gr4j-cemaneige/Salmon-River-Near-Prince-George_meteo_daily.nc"

bounds = {
    "GR4JCN": {
        "low": (0.01, -15.0, 10.0, 0.0, 1.0, 0.0),
        "high": (2.5, 10.0, 700.0, 7.0, 30.0, 1.0),
    }
}


def test_spotpy_calibration(symbolic_config, tmpdir):
    name = symbolic_config.__class__.__name__
    if name not in bounds:
        pytest.skip("No bounds defined.")

    spot_setup = SpotSetup(
        config=symbolic_config,
        low=bounds[name]["low"],
        high=bounds[name]["high"],
        path=tmpdir,
    )

    sampler = spotpy.algorithms.dds(
        spot_setup, dbname="RAVEN_model_run", dbformat="ram", save_sim=False
    )

    sampler.sample(10, trials=1)


class TestSpotpy:
    def test_simple_gr4j(self, get_file, tmpdir):
        ts = get_file(salmon_river)

        alt_names = {
            "RAINFALL": "rain",
            "TEMP_MIN": "tmin",
            "TEMP_MAX": "tmax",
            "PET": "pet",
            "HYDROGRAPH": "qobs",
            "SNOWFALL": "snow",
        }

        salmon_land_hru_1 = dict(
            area=4250.6, elevation=843.0, latitude=54.4848, longitude=-123.3659
        )

        model = GR4JCN(
            params=[0.529, -3.396, 407.29, 1.072, 16.9, 0.947],
            ObservationData=rc.ObservationData.from_nc(ts, alt_names="qobs"),
            Gauge=rc.Gauge.from_nc(
                ts,
                alt_names=alt_names,
                extra={1: {"elevation": salmon_land_hru_1["elevation"]}},
            ),
            HRUs=[salmon_land_hru_1],
            StartDate=dt.datetime(2000, 1, 1),
            EndDate=dt.datetime(2002, 1, 1),
            RunName="test",
            EvaluationMetrics=("NASH_SUTCLIFFE",),
        )

        spot_setup = SpotSetup(
            config=model,
            low=(0.01, -15.0, 10.0, 0.0, 1.0, 0.0),
            high=(2.5, 10.0, 700.0, 7.0, 30.0, 1.0),
            path=tmpdir,
        )

        sampler = spotpy.algorithms.dds(
            spot_setup, dbname="RAVEN_model_run", dbformat="ram", save_sim=False
        )
        rep = 100

        # FIXME: These tests should have assertions. Remove print functions.

        sampler.sample(rep, trials=1)

    def test_simple_hmets(self, get_file, tmpdir):
        ts = get_file(salmon_river)

        alt_names = {
            "RAINFALL": "rain",
            "TEMP_MIN": "tmin",
            "TEMP_MAX": "tmax",
            "PET": "pet",
            "HYDROGRAPH": "qobs",
            "SNOWFALL": "snow",
        }

        salmon_land_hru_1 = dict(
            area=4250.6, elevation=843.0, latitude=54.4848, longitude=-123.3659
        )

        model = HMETS(
            params=[
                9.5019, 0.2774, 6.3942, 0.6884, 1.2875, 5.4134, 2.3641,
                0.0973, 0.0464, 0.1998, 0.0222, -1.0919, 2.6851, 0.3740,
                1.0000, 0.4739, 0.0114, 0.0243, 0.0069, 310.7211, 916.1947
            ],
            ObservationData=rc.ObservationData.from_nc(ts, alt_names="qobs"),
            Gauge=rc.Gauge.from_nc(
                ts,
                alt_names=alt_names,
                extra={1: {"elevation": salmon_land_hru_1["elevation"]}},
            ),
            HRUs=[salmon_land_hru_1],
            StartDate=dt.datetime(2000, 1, 1),
            EndDate=dt.datetime(2002, 1, 1),
            RunName="test",
            EvaluationMetrics=("NASH_SUTCLIFFE",),
        )

        spot_setup = SpotSetup(
            config=model,
            low=(0.3, 0.01, 0.5, 0.15, 0.0, 0.0, -2.0, 0.01, 0.0, 0.01, 0.005,
                 -5.0, 0.0, 0.0, 0.0, 0.0, 0.00001, 0.0, 0.00001, 0.0, 0.0),
            high=(20.0, 5.0, 13.0, 1.5, 20.0, 20.0, 3.0, 0.2, 0.1, 0.3,
                  0.1, 2.0, 5.0, 1.0, 3.0, 1.0, 0.02, 0.1, 0.01, 0.5, 2.0),
            path=tmpdir,
        )

        sampler = spotpy.algorithms.dds(
            spot_setup, dbname="RAVEN_model_run", dbformat="ram", save_sim=False
        )
        rep = 100

        # FIXME: These tests should have assertions. Remove print functions.

        sampler.sample(rep, trials=1)

    def test_simple_mohyse(self, get_file, tmpdir):
        ts = get_file(salmon_river)

        alt_names = {
            "RAINFALL": "rain",
            "TEMP_MIN": "tmin",
            "TEMP_MAX": "tmax",
            "PET": "pet",
            "HYDROGRAPH": "qobs",
            "SNOWFALL": "snow",
        }

        salmon_land_hru_1 = dict(
            area=4250.6, elevation=843.0, latitude=54.4848, longitude=-123.3659
        )

        model = Mohyse(
            params=[1.0000, 0.0468, 4.2952, 2.6580, 0.4038, 0.0621, 0.0273, 0.0453, 0.9039, 5.6179775],
            ObservationData=rc.ObservationData.from_nc(ts, alt_names="qobs"),
            Gauge=rc.Gauge.from_nc(
                ts,
                alt_names=alt_names,
                extra={1: {"elevation": salmon_land_hru_1["elevation"]}},
            ),
            HRUs=[salmon_land_hru_1],
            StartDate=dt.datetime(2000, 1, 1),
            EndDate=dt.datetime(2002, 1, 1),
            RunName="test",
            EvaluationMetrics=("NASH_SUTCLIFFE",),
        )

        spot_setup = SpotSetup(
            config=model,
            low=(0.01, 0.01, 0.01, -5.0, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01),
            high=(20.0, 1.0, 20.0, 5.0, 0.5, 1.0, 1.0, 1.0, 15.0, 15.0),
            path=tmpdir,
        )

        sampler = spotpy.algorithms.dds(
            spot_setup, dbname="RAVEN_model_run", dbformat="ram", save_sim=False
        )
        rep = 100

        # FIXME: These tests should have assertions. Remove print functions.

        sampler.sample(rep, trials=1)
