import griddle
from clawpack import pyclaw

def test_time_series():
    ts = griddle.data.TimeSeries('./test_data/_amrclaw_2d_acoustics/')
    assert type(ts['1']) == pyclaw.Solution
