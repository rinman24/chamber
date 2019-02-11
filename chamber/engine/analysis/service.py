"""Analysis engine module."""

import math
import re

import dask.dataframe as dd
from dask.multiprocessing import get
import CoolProp.HumidAirProp as hap
import matplotlib.pyplot as plt
import nptdms
import numpy as np
import pandas as pd
from scipy import signal, stats
import uncertainties as un
from uncertainties import unumpy as unp

import chamber.utility.uncert as un_util
import chamber.engine.spalding.service as dbs


# ----------------------------------------------------------------------------
# Internal logic (adding experiment)


def _tdms_2_dict_of_df(filepath):
    """
    Convert tdms file to a dictionary of pandas DataFrames.

    Parameters
    ----------
    filepath : str
        filepath to the tdms file.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df('path')

    """
    tdms_file = nptdms.TdmsFile(filepath)

    settings_df = tdms_file.object('Settings').as_dataframe()
    settings_df = settings_df.rename(columns={'DutyCycle': 'Duty'})

    data_df = tdms_file.object('Data').as_dataframe()

    test_df = pd.DataFrame(
        data=dict(
            Author=tdms_file.object().properties['author'],
            DateTime=tdms_file.object().properties['DateTime'],
            Description=tdms_file.object().properties['description']
            ),
        index=[0]
        )

    dataframes = dict(setting=settings_df, data=data_df, test=test_df)

    return dataframes


def _build_setting_df(dataframes):
    """
    Add `Temperature` and `Pressure` keys to `setting` dataframe.

    Calculate averave experimental values of temperature and pressure using
    all observations. Average temperature and pressure are then rounded to the
    nearest 5 K and 5000 Pa, respectively.

    If `Duty` is zero in settings, `PowOut` and `PowRef` columns are
    dropped from `data` dataframe.

    If `IsMass` is truthy in settings, TC0-3 are dropped from `data`
    dataframe. Else, `Mass` is dropped from `data` dataframe.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df('path')
    >>> dataframes = _build_setting_df(dataframes)

    """
    if not dataframes['setting'].loc[0, 'Duty']:
        dataframes['data'].drop(columns=['PowOut', 'PowRef'], inplace=True)

    if dataframes['setting'].loc[0, 'IsMass']:  # TCs 0-3 not connected.
            initial_tc = 4
            dataframes['data'].drop(
                columns=['TC{}'.format(tc_bad) for tc_bad in range(0, 4)],
                inplace=True
                )
    else:
        initial_tc = 0
        dataframes['data'].drop(columns=['Mass'], inplace=True)

    tc_cols = ['TC{}'.format(num) for num in range(initial_tc, 14)]
    avg_temp = dataframes['data'].loc[:, tc_cols].mean().mean()
    avg_pressure = dataframes['data'].loc[:, 'Pressure'].mean()

    dataframes['setting'].loc[0, 'Pressure'] = _round(avg_pressure, 5000)
    dataframes['setting'].loc[0, 'Temperature'] = _round(avg_temp, 5)

    return dataframes


def _build_observation_df(dataframes):
    """
    Convert `data` dataframe into `observation` dataframe.

    Columns are 'popped' off of `data` an inserted into `observation` one at a
    time to avoid creating a full copy.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, and `test`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys same as input plus `observation`.

    Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)

    """
    columns_to_keep = ['CapManOk', 'DewPoint', 'Idx', 'OptidewOk', 'Pressure']

    if dataframes['setting'].loc[0, 'IsMass']:
        columns_to_keep.append('Mass')

    if dataframes['setting'].loc[0, 'Duty']:
        columns_to_keep += ['PowOut', 'PowRef']

    dataframes['observation'] = pd.DataFrame()
    for col in columns_to_keep:
        dataframes['observation'].loc[:, col] = dataframes['data'].pop(col)

    return dataframes


def _build_temp_observation_df(dataframes):
    """
    Pivot remaining tc columns in `data` to the format required by database.

    Columns are 'popped' off of `data` an inserted into `temp_observation` one
    at a time to avoid creating a full copy.

    Parameters
    ----------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `data`, `test`, and `observation`.

    Returns
    -------
    dict of {str: pandas.DataFrame}
        Keys same as input plus `temp_observation`.

     Examples
    --------
    >>> dataframes = _tdms_2_dict_of_df(filepath)
    >>> dataframes = _build_setting_df(dataframes)
    >>> dataframes = _build_observation_df(dataframes)
    >>> dataframes = _build_temp_observation_df(dataframes)

    """
    tc_num, temp, idx = [], [], []
    elements = len(dataframes['data'].index)
    if dataframes['setting'].loc[0, 'IsMass']:
        initial_tc = 4
    else:
        initial_tc = 0

    for tc in range(initial_tc, 14):
        tc_num += [tc]*elements
        col = 'TC{}'.format(tc)
        temp += list(dataframes['data'].pop(col))
        idx += list(dataframes['observation'].loc[:, 'Idx'])

    dataframes['temp_observation'] = pd.DataFrame(
        dict(
            ThermocoupleNum=tc_num,
            Temperature=temp,
            Idx=idx
            )
        )

    return dataframes


# ----------------------------------------------------------------------------
# Internal logic (processing data)


def _calc_avg_te(temp_data):
    """Calculate average temperature."""
    # Manager is responsible for pivoting the table before calling.
    mean = temp_data.mean(axis=1)
    std = temp_data.std(axis=1)

    avg_te = pd.DataFrame(
        unp.uarray(mean, std), columns=['AvgTe'], index=temp_data.index
        )

    return avg_te


def _filter_observations(obs_data):
    """
    Apply Savitzky-Golay filter to observation data.

    Notes
    -----
    No uncertainty yet as no calculations have been done. Conversion to
    `ufloat` at this stage would be a poor use of resources. Unlike
    `_calc_avg_temp` where we would like to propigate the error associated
    with the calculation that was performed.

    """
    filt_obs = obs_data.copy()

    filt_obs.DewPoint = signal.savgol_filter(filt_obs.DewPoint, 1801, 2)
    filt_obs.Mass = signal.savgol_filter(filt_obs.Mass, 301, 2)
    filt_obs.Pressure = signal.savgol_filter(filt_obs.Pressure, 3601, 1)

    return filt_obs


def _preprocess_observations(obs_data, temp_data):
    """Preprocess and ask user to proceed."""
    avg_te = _calc_avg_te(temp_data)
    nominal_temps = np.array(
        [avg_te.loc[i, 'AvgTe'].nominal_value for i in avg_te.index]
        )
    temp_std = np.array(
        [avg_te.loc[i, 'AvgTe'].std_dev for i in avg_te.index]
        )

    filt_obs = _filter_observations(obs_data)

    fig = plt.figure(figsize=(10, 8))

    # Temperature ------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 1)
    ax.plot(avg_te.index, nominal_temps, label='Nominal $T_e$')
    ax.fill_between(
        avg_te.index, nominal_temps-temp_std, nominal_temps+temp_std,
        color='gray', alpha=0.2)
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$T_e$/K')
    ax.grid()

    # DewPoint ---------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 2)
    obs_data.DewPoint.plot(ax=ax, label='Observed')
    filt_obs.DewPoint.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.DewPoint - un_util.del_tdp,
        filt_obs.DewPoint + un_util.del_tdp,
        color='gray', alpha=0.2)
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$T_{DP}}$/K')
    ax.grid()

    # Mass -------------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 3)
    obs_data.Mass.plot(ax=ax, label='Observed')
    filt_obs.Mass.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.Mass - un_util.del_m,
        filt_obs.Mass + un_util.del_m,
        color='gray', alpha=0.2)
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$m$/kg')
    ax.grid()

    # Pressure ---------------------------------------------------------------
    ax = fig.add_subplot(2, 2, 4)
    p_err = [p * un_util.pct_p for p in obs_data.Pressure]
    obs_data.Pressure.plot(ax=ax, label='Observed')
    filt_obs.Pressure.plot(ax=ax, label='Filtered')
    ax.fill_between(
        filt_obs.index,
        filt_obs.Pressure - p_err, filt_obs.Pressure + p_err,
        color='gray', alpha=0.2)
    ax.legend()
    ax.set_xlabel('$t$/s')
    ax.set_ylabel('$P$/Pa')
    ax.grid()

    plt.show()

    response = input('Proceed ([y]/n)? ').lower()

    if (not response) or ('y' in response):  # pragma: no cover
        return filt_obs.join(avg_te)
    elif 'n' in response:
        return 'Analysis canceled.'
    else:
        return 'Unrecognized response.'


# ----------------------------------------------------------------------------
# Internal logic (locating target indexes)

def _calc_single_phi(row):
    t, del_t = row.AvgTe.nominal_value, row.AvgTe.std_dev

    phi = hap.HAPropsSI('RH', 'P', row.Pressure, 'T', t, 'Tdp', row.DewPoint)

    del_p = hap.HAPropsSI(
        'RH',
        'P', un_util.pct_p * row.Pressure,
        'T', t,
        'Tdp', row.DewPoint) - phi
    del_t = hap.HAPropsSI(
        'RH',
        'P', row.Pressure,
        'T', t + del_t,
        'Tdp', row.DewPoint) - phi
    del_tdp = hap.HAPropsSI(
        'RH',
        'P', row.Pressure,
        'T', t,
        'Tdp', row.DewPoint + un_util.del_tdp) - phi

    phi_std = math.sqrt(del_p**2 + del_t**2 + del_tdp**2)

    return (phi, phi_std)


def _calc_multi_phi(data):  # pragma: no cover
    ddata = dd.from_pandas(data, npartitions=8)

    res = ddata.map_partitions(
        lambda df: df.apply((lambda row: _calc_single_phi(row)), axis=1),
        meta=('float', 'float')
        ).compute(get=get)

    data['phi'] = res.apply(lambda x: un.ufloat(x[0], x[1]))

    return data


def _get_valid_phi_targets(data):
    phi_step_pct = 1
    # Multipy by 100 to get into percent
    phi_min = data.phi.min() * 100
    phi_max = data.phi.max() * 100

    phi_min_valid = int(
        math.ceil(phi_min.nominal_value/phi_step_pct)
        ) * phi_step_pct
    phi_max_valid = int(
        math.floor(phi_max.nominal_value/phi_step_pct)
        ) * phi_step_pct

    # Devide by 100 to get back to dimensionless phi
    my_map = map(
        lambda x: x/100,
        range(phi_min_valid, phi_max_valid + 5, phi_step_pct))

    return list(my_map)


def _get_valid_phi_indexes(data):
    valid_phi_targets = _get_valid_phi_targets(data)
    result = []

    for target in valid_phi_targets:
        phi = data.phi.copy()
        phi = phi - target
        if len(phi[phi > 0].index):
            target_idx = min(phi[phi > 0].index)
            result.append(dict(target=target, idx=target_idx))
    return result


def _get_max_window_lengths(data):
    indexes = _get_valid_phi_indexes(data)
    for _dict in indexes:
        to_the_left = _dict['idx'] - data.index[0]
        to_the_right = data.index[-1] - _dict['idx']
        _dict.update({'max_hl': min(to_the_left, to_the_right)})

    return indexes


def _perform_single_chi2_fit(sample):
    # constants
    n = len(sample)
    sig_coef = 1/un_util.del_m**2

    # chi2 variables
    s = n*sig_coef
    s_x = sig_coef*sample.index.values.sum()
    s_y = sig_coef*sample.Mass.sum()
    s_xx = sig_coef*sample.index.values.dot(sample.index.values)
    s_xy = sig_coef*sample.index.values.dot(sample.Mass)
    delta = s*s_xx - s_x**2

    # fit params
    a = (s_xx*s_y - s_x*s_xy)/delta
    b = (s*s_xy - s_x*s_y)/delta
    sig_a = math.sqrt(s_xx/delta)
    sig_b = math.sqrt(s/delta)

    # p-value
    model = a + b*sample.index.values
    chi2 = ((sample.Mass-model)/un_util.del_m).pow(2).sum()
    p_val = stats.chi2.cdf(chi2, len(sample)-2)

    # r-squared
    ss_res = (sample.Mass-model).pow(2).sum()
    ss_tot = (sample.Mass-sample.Mass.mean()).pow(2).sum()
    r2 = 1 - ss_res/ss_tot

    result = dict(a=a, sig_a=sig_a, b=b, sig_b=sig_b, r2=r2, p_val=p_val)
    return result


def _select_best_fit(data, target_idx, max_hl):
    for hl in range(1, max_hl):
        # Grab a sample
        start, end = target_idx-hl, target_idx+hl
        sample = data.loc[start: end, :]
        result_dict = _perform_single_chi2_fit(sample)

        # check if stop condition is satisfied
        percent_error = abs(result_dict['sig_b']/result_dict['b']*100)
        error_satisfied = (percent_error <= 1)
        r2_satisfied = (result_dict['r2'] >= 0.999)
        p_val_satisfied = (result_dict['p_val'] <= 0.01)

        if error_satisfied and r2_satisfied and p_val_satisfied:
            return result_dict

    # No stop criteria was not found
    return None


# ----------------------------------------------------------------------------
# Public functions


def perform_chi2_analysis(obs_data, temp_data, ref='Marrero', rule='1/3'):  # noqa: D103
    a = list()
    sig_a = list()
    b = list()
    sig_b = list()
    mddp = list()
    sig_mddp = list()
    r2 = list()
    p_val = list()
    phi = list()
    target_phi = list()
    g_m1 = list()
    sig_g_m1 = list()
    sh_l = list()
    sig_sh_l = list()
    g_h = list()
    sig_g_h = list()
    nu_l = list()
    sig_nu_l = list()
    film_cond = list()
    gr_r = list()
    sig_gr_r = list()

    area = math.pi * pow(0.015, 2)
    data = _preprocess_observations(obs_data, temp_data)
    data = _calc_multi_phi(data)
    target_info = _get_max_window_lengths(data)

    for dict_ in target_info:
        print('target phi:', dict_['target'])
        result = _select_best_fit(
            data, dict_['idx'], dict_['max_hl']
            )
        if result:
            a.append(result['a'])
            sig_a.append(result['sig_a'])
            b.append(result['b'])
            sig_b.append(result['sig_b'])
            mddp.append(-result['b']/area)
            sig_mddp.append(result['sig_b']/area)
            r2.append(result['r2'])
            p_val.append(result['p_val'])
            phi.append(data.loc[dict_['idx'], 'phi'])
            target_phi.append(dict_['target'])

            # --------------------------------------------------------------------
            # Set up the film conductance model and solve
            spald_input = dict(
                m=data.Mass[dict_['idx']],
                p=data.Pressure[dict_['idx']],
                t_e=data.AvgTe[dict_['idx']].nominal_value,
                t_dp=data.DewPoint[dict_['idx']],
                ref=ref, rule=rule)
            spald = dbs.Spalding(**spald_input)
            spald.solve()
            film_cond.append(spald.solution)

            # --------------------------------------------------------------------
            # Now use the film potential to estimate parameters
            g_m1_temp = mddp[-1]/spald.solution['B_m1']
            g_m1.append(g_m1_temp.nominal_value)
            sig_g_m1.append(g_m1_temp.std_dev)

            sh_l_temp = (
                (g_m1_temp*spald.exp_state['L'])
                / (spald.solution['rho']*spald.solution['D_12'])
                )
            sh_l.append(sh_l_temp.nominal_value)
            sig_sh_l.append(sh_l_temp.std_dev)

            g_h_temp = mddp[-1]/spald.solution['B_h']
            g_h.append(g_h_temp.nominal_value)
            sig_g_h.append(g_h_temp.std_dev)

            nu_l_temp = (
                (g_h_temp*spald.exp_state['L'])
                / (spald.solution['rho']*spald.solution['alpha'])
                )
            nu_l.append(nu_l_temp.nominal_value)
            sig_nu_l.append(nu_l_temp.std_dev)

            gr_r.append(spald.solution['Gr_R'].nominal_value)
            sig_gr_r.append(spald.solution['Gr_R'].std_dev)

    result = pd.DataFrame(
        data=dict(
            a=a, sig_a=sig_a,
            b=b, sig_b=sig_b,
            mddp=mddp, sig_mddp=sig_mddp,
            r2=r2, p_val=p_val, phi=phi,
            g_m1=g_m1, sig_g_m1=sig_g_m1,
            Sh_L=sh_l, sig_Sh_L=sig_sh_l,
            g_h=g_h, sig_g_h=sig_g_h,
            Nu_L=nu_l, sig_Nu_L=sig_nu_l,
            Gr_R=gr_r, sig_Gr_R=sig_gr_r,
            )
        )

    return result, film_cond


def read_tdms(filepath):
    """
    Convert tdms file to several pandas dataframes.

    Dataframes mirror the database schema and are ready to be sent to sql.

    Parameters
    ----------
    filepath : str
        filepath to the tdms file.

    Returns
    -------
    dataframes : dict of {str: pandas.DataFrame}
        Keys include `setting`, `test`, `observation` and `temp_observation`.

    Examples
    --------
    >>> dataframes = read_tdms('path')

    """
    dataframes = _tdms_2_dict_of_df(filepath)
    dataframes = _build_setting_df(dataframes)
    dataframes = _build_observation_df(dataframes)
    dataframes = _build_temp_observation_df(dataframes)
    del dataframes['data']
    return dataframes


# ----------------------------------------------------------------------------
# helpers


def _round(number, nearest):
    return nearest*round(number/nearest)
