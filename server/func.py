import json
import logging
import pytz
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Tuple
from influxdb import DataFrameClient

with open('config.json', 'r') as f:
    config = json.load(f)

logger = logging.getLogger(config['log_name'])
client = DataFrameClient(**config['influxdb']['client'])


def fft(payload: list, td: int) -> pd.Series:
    # does not work
    # s_data = pd.Series(payload)
    data_len = len(payload)
    time_step = td / data_len / 1e6
    ps = np.abs(np.fft.fft(payload)) ** 2
    freqs = np.fft.fftfreq(data_len, time_step)
    idx = np.argsort(freqs)
    s_ps = pd.Series(index=freqs[idx], data=ps[idx])
    s_ps_f = s_ps[(s_ps.index > 20) & (s_ps.index < 80)]
    print(s_ps_f)
    idx_diff_min = s_ps_f.index[abs((s_ps_f.index - 50)).argmin()]
    s_ps_50hz = s_ps_f[idx_diff_min]
    print(idx_diff_min, s_ps_50hz)

    return s_ps


def rms(payload: List[int], ticks: List[int], dt_0: datetime = None) -> Tuple[pd.Series, float]:
    if dt_0 is None:
        dt_0 = pytz.utc.localize(datetime.utcnow().replace(microsecond=0))

    td = ticks[-1] - ticks[0]
    if td < 0:
        return pd.Series(), -1

    x0 = ticks[0]
    idx = [dt_0 + pd.Timedelta(x - x0, 'us') for x in ticks]
    td_f = td - td % 20000  # 20 ms ~ 50 Hz

    s_data = pd.Series(index=idx, data=payload)
    s_data_1us = s_data.resample('1us').interpolate()
    s_data_1us_f = s_data_1us[s_data_1us.index[:td_f]]
    s_data_1us_f0 = s_data_1us_f - s_data_1us_f.mean()

    rms_value = np.sqrt(s_data_1us_f0.dot(s_data_1us_f0) / s_data_1us_f0.size)
    rms_power = rms_value * config['meas_to_rms_coeff'] * config['voltage']

    if rms_power < 100:
        rms_power = 0

    return s_data, rms_power


def rms_to_influx(rms_value: float, dt: datetime):
    df_data = pd.DataFrame(data={'value': {dt: round(rms_value)}})
    client.write_points(df_data, config['influxdb']['measurement_rms'])
    return None


def meas_to_influx(s_data: pd.Series):
    df_data = pd.DataFrame(data={'value': s_data})
    client.write_points(df_data, config['influxdb']['measurement_data'])
    return None
