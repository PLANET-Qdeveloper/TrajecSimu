import numpy as np
import numpy.linalg as LA
import sympy
import json


def getConditionalBivariateNorm(mu_X, mu_Y, sigma_XX, sigma_XY, sigma_YY, X):
    # Y|X が多変量正規分布N(mu, Sigma)に従う場合のmu, Sigmaを求める
    sigma_XX_i = LA.inv(sigma_XX)
    mu = mu_Y + np.dot(np.dot(sigma_XY.T, sigma_XX_i), (X - mu_X))
    Sigma = sigma_YY - np.dot(np.dot(sigma_XY.T, sigma_XX_i), sigma_XY)
    return mu, Sigma


def getEllipseParameters(mu, sigma, alpha=0.95):
    # mu: 平均 ([alt][x|y])
    # sigma: 分散共分散行列
    # alpha: 楕円内に点が入る確率

    sigma_i = LA.inv(sigma)
    eigvals, M = LA.eig(sigma_i)
    lmda2 = -2*np.log(1.00000000 - alpha)
    scale = np.sqrt(lmda2/eigvals)
    return scale, M, mu


def getEllipsePlot(a, b, Mrot=None, angle_rad=0, x0=0, y0=0, n_plots=100):
    theta = np.linspace(0, 2 * np.pi, n_plots)

    v0 = np.array([x0, y0])
    v = np.array([a * np.cos(theta), b * np.sin(theta)])

    if Mrot is None:
        Mrot = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
            ])

    return np.dot(Mrot, v) + v0[:, None]


def getAzimuthWindByPlot(U, V, azimuth_rad):
    # 基準高度の楕円上の各風の方位計算[-pi, +pi]
    wind_dir = np.arctan2(-U, -V)
    idx = np.argmin(abs(wind_dir - azimuth_rad))
    return np.array([U[idx], V[idx]])


def getAzimuthWindByEllipse(
        center_pos, scale, rotateMatrix,
        wind_direction, std_wind=np.array([0., 0.])
        ):
    # 媒介変数表示による楕円 U(t), V(t)と V = alpha * U (alphaは飛行方位の傾き)の関係から
    # 方程式を立ててtについて解き、U,V を求める。
    t = sympy.Symbol('t')
    x = scale[0] * sympy.cos(t)
    y = scale[1] * sympy.sin(t)
    U = rotateMatrix[0, 0] * x + rotateMatrix[0, 1] * y + center_pos[0]
    V = rotateMatrix[1, 0] * x + rotateMatrix[1, 1] * y + center_pos[1]
    print('wind direction: ', wind_direction)
    if np.mod(wind_direction, np.pi) != 0.:
        alpha = sympy.cot(wind_direction)
        expr = (V - std_wind[1]) - alpha * (U - std_wind[0])
    else:
        expr = (U - std_wind[0])
    t_solutions_tmp = sympy.solve(expr)
    t_solutions = [float(t_sol) for t_sol in t_solutions_tmp]
    #print('solutions: ', t_solutions)

    n_solutions = len(t_solutions)
    wind_tmp = np.zeros((n_solutions, 2))
    for i, t_solution in enumerate(t_solutions):
        wind_tmp[i] = [
                        float(U.subs(t, t_solution)),
                        float(V.subs(t, t_solution))
                    ]

    az_wind_directions = np.arctan2(
                            -(wind_tmp.T[0] - std_wind[0]),
                            -(wind_tmp.T[1] - std_wind[1])
                            )
    direction_diff = np.round(az_wind_directions - wind_direction, 2)
    direction_diff = np.mod(direction_diff, 6.28)
    #print('direction diff', direction_diff)
    mask = direction_diff == 0.

    if mask.any():
        #print('mask wind', wind_tmp[mask])
        idx = np.argmax(LA.norm(wind_tmp[mask].T, axis=0))
        azimuth_wind = wind_tmp[mask][idx]
    else:
        #print('azimuth wind not found')
        idx = np.argmin(LA.norm(wind_tmp.T, axis=0))
        azimuth_wind = wind_tmp[idx]

    return azimuth_wind


def getProbEllipse(mu, sigma, alpha=0.95, n_plots=100):
    # mu: 平均 ([alt][x|y])
    # sigma: 分散共分散行列
    # alpha: 楕円内に点が入る確率
    # n_plots: プロット数

    scale, M, _ = getEllipseParameters(mu, sigma, alpha)
    plots = getEllipsePlot(
        scale[0],
        scale[1],
        M,
        x0=mu[0],
        y0=mu[1],
        n_plots=n_plots)
    return plots[0], plots[1]


def getStatWindVector(
        statistics_parameters,
        wind_direction_deg,
        wind_std,
        alpha=0.95
        ):
    alt_axis = statistics_parameters['alt_axis']
    # alt_std = alt_axis[alt_index_std]
    n_alt = len(alt_axis)

    mu4 = np.array(statistics_parameters['mu4'])
    sigma4 = np.array(statistics_parameters['sigma4'])

    # ----------------------------
    # Probabillity Ellipse
    # ----------------------------
    stat_wind_u = []
    stat_wind_v = []
    # print('X: ', wind_std)
    for h in range(n_alt):

        # u,vが決まった時のdu,dvの条件付き正規分布の平均と共分散行列
        mu, sigma = getConditionalBivariateNorm(
            mu_X=mu4[h][2:],
            mu_Y=mu4[h][:2],
            sigma_XX=sigma4[h][2:, 2:],
            sigma_XY=sigma4[h][2:, :2],
            sigma_YY=sigma4[h][:2, :2],
            X=wind_std[h])

        scale, M, _ = getEllipseParameters(mu, sigma, alpha=alpha)
        # print('wind direction deg', wind_direction_deg)
        w = getAzimuthWindByEllipse(
                            mu + wind_std[h],
                            scale,
                            M,
                            np.deg2rad(wind_direction_deg),
                            mu + wind_std[h]
                            )

        stat_wind_u.append(w[0])
        stat_wind_v.append(w[1])
        print(
            'Altitude: ', alt_axis[h], ' ',
            stat_wind_u[h], ', ', stat_wind_v[h])

    stat_wind = np.array([stat_wind_u, stat_wind_v])
    return stat_wind, alt_axis


class TypeEncoder(json.JSONEncoder):
    # Numpyの型をそのままjsonにdumpすることができないので
    # それを対応させるクラス
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(TypeEncoder, self).default(obj)


if __name__ == '__main__':
    import argparse
    from tools.load_wind import loadWind

    parser = argparse.ArgumentParser(description='誤差統計パラメータファイルと予報風から、各高度における風向風速分布楕円を出すスクリプト')
    parser.add_argument('error_stat_filename')
    parser.add_argument('forecast_filename')
    parser.add_argument('output_path')
    parser.add_argument('--alpha', default='0.95', help='求める楕円内に風ベクトルが入る確率。大きくするほど楕円が大きくなる。デフォルト0.95')

    args = parser.parse_args()

    error_stat_filename = args.error_stat_filename
    forecast_filename = args.forecast_filename
    out_path = args.output_path
    alpha = float(args.alpha)

    forecastWindFunc, _ = loadWind(forecast_filename)

    with open(error_stat_filename, 'r') as f:
        es_params = json.load(f)
    
    alt_axis = es_params['alt_axis']
    n_alt = len(alt_axis)
    fore_wind = forecastWindFunc(alt_axis)
    wind_directions = np.arange(0.0, 360.0, 22.5)
    print('fore_wind', fore_wind)

    wind_profile = {}
    #ellipse_edge_winds = np.zeros((len(wind_directions), 2, n_alt))
    for direction in wind_directions:
        print('direction', direction)
        ellipse_edge_wind, _ = getStatWindVector(es_params, direction, fore_wind, alpha=alpha)
        wind_profile[str(direction)] = {
            'wind_u': ellipse_edge_wind[0],
            'wind_v': ellipse_edge_wind[1]
        }
    
    saved_data = {
        'alt_axis': alt_axis,
        'years': es_params['years'],
        'months': es_params['months'],
        'days': es_params['days'],
        'location': es_params['location'],
        'targer_hour': es_params['target_hour'],
        'MSM_init_hour': es_params['MSM_init_hour'],
        'MSM_forecast_hour': es_params['MSM_forecast_hour'],
        'wind': wind_profile
    }

    with open(out_path, 'w') as f:
        json.dump(saved_data, f, indent=4, cls=TypeEncoder)