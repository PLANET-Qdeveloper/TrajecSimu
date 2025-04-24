import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

def loadWind(filename, interp_kind='linear'):
    df = pd.read_csv(filename)
    altitudes = np.array(df['altitude'])

    # 風のu, vの方向
    # U: 西→東に吹く風を正
    # V: 南→北を正
    wind_u = np.array(df['wind_u'])
    wind_v = np.array(df['wind_v'])
    wind_vec = np.c_[wind_u, wind_v]
    wind = interp1d(
            altitudes,
            wind_vec,
            kind=interp_kind,
            axis=0)
    return wind, altitudes