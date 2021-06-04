##############################################################################
################--- 0. IMPORT LIBRARIES AND DEFINE FUNCTIONS---###############
##############################################################################
import numpy as np
import pandas as pd
import os
from datetime import datetime, date
import warnings
from itertools import product
import matplotlib.pyplot as plt

# from concurrent.futures import ProcessPoolExecutor
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from fbprophet.plot import plot_plotly
import plotly.offline as py

warnings.filterwarnings("ignore", category=UserWarning)


def create_grid(param_grid: dict) -> object:
    """Generate a grid, containing all the combination of parameters passed.

    Args:
        param_grid: dictionary containing the possible parameters of each model
            desired to be run. In the format:
                {'model' : [m], 'initial' : ['x days','x days'],
                'period'  : ['x days'], 'horizon' : ['x days']}
    Returns:
        dict: grid of parameters
    """
    param_grid_list = [param_grid].copy()
    for p in param_grid_list:
        items = sorted(p.items())
        if not items:
            yield {}
        else:
            keys, values = zip(*items)
            for v in product(*values):
                params = dict(zip(keys, v))
                yield params


def create_ts(df: pd.DataFrame, date_var: str, y_var: str, x_vars: list = False, sort_ts: bool = False):
    """Transform the input df in order to be used by prophet.
        this means keeping just "ds", "y_var" and optional "x_vars" columns.

    Args:
        df: input df
        date_var: name of the variable containing the dates
        y_var: name of the variable for which the predictions will be estimated
        x_vars: name of the (optional) exogenous variables. False for no exogenous variables
        sort_ts: Boolean. True to sort the df in ascending way (+ computation time)

    Returns:
         pd.DataFrame: df containing the ts ready to be fit by prophet
    """
    # 1. Univariate time series (just "ds" and "y")
    if not x_vars:
        ts = df[[date_var, y_var]]
        ts.columns = ["ds", "y"]

    # 2. Multivariate time series ("ds", "y" and "x1", "x2", etc)
    else:
        ts = df[[date_var, y_var] + x_vars]
        ts = ts.rename(columns={date_var: "ds", y_var: "y"})

    ts = ts.assign(ds=pd.to_datetime(ts["ds"], format="%Y/%m/%d"))
    if sort_ts:
        ts = ts.sort_values(by="ds", ascending=True)
    return ts


def cross_validation_compare_models(cross_valid_params: list, metric: str = "mse") -> pd.DataFrame:
    """Execute Cross Validation to compare models with different parameters.

    Args:
        cross_valid_params: List of dict generated by the create_grid function
        metric: metric desired to be optimized

    Returns:
        pd.DataFrame: df with cross_validation result.
    """
    assert metric in ["mse", "rmse", "mae", "mape"], "metric must be either mse, rmse, mae or mape"
    df_ps = pd.DataFrame()

    for cross_valid_param in cross_valid_params:
        df_cv = cross_validation(**cross_valid_param)
        df_p = performance_metrics(df_cv, rolling_window=1)
        df_p["initial"] = cross_valid_param["initial"]
        df_p["period"] = cross_valid_param["period"]
        df_ps = df_ps.append(df_p)

    df_ps = df_ps.loc[:, df_ps.columns.isin(list(["initial",
                                                  "horizon",
                                                  "period",
                                                  "mse",
                                                  "rmse",
                                                  "mae",
                                                  "mape",
                                                  "coverage",
                                                  ]))]
    return df_ps


def detect_anomalies(forecast: pd.DataFrame) -> pd.DataFrame:
    """Identify anomalies.
        That is observations outside the interval of confidence defined using yhat_lower/yhat_upper,
        and create the "importance" variable as the relative
        deltas between observed values and lower/upper values of the interval of confidence.

    Args:
        forecast: input df containing the fbprophet predictions

    Returns:
        pd.DataFrame: df containing predictions + "anomaly" & "importance" variables
    """
    df = forecast.copy()
    df["anomaly"] = 0
    df.loc[df["fact"] > df["yhat_upper"], "anomaly"] = 1
    df.loc[df["fact"] < df["yhat_lower"], "anomaly"] = -1

    # anomaly importances
    df["importance"] = 0
    df.loc[df["anomaly"] == 1, "importance"] = (df["fact"] - df["yhat_upper"]) / df["fact"]
    df.loc[df["anomaly"] == -1, "importance"] = (df["yhat_lower"] - df["fact"]) / df["fact"]
    return df


def diagnostic_metrics(forecast: pd.DataFrame, actual: pd.DataFrame):
    """Compute diagnostics metrics (ME, MAE, MAPE, MPE, MSE, RMSE).

    Args:
        forecast: df containing the predictions
        actual: df containing the actual values

    Returns:
        dict: calculated diagnostic metrics
    """
    mape = np.mean(np.abs(forecast - actual) / np.abs(actual))  # MAPE
    me = np.mean(forecast - actual)  # ME
    mae = mean_absolute_error(actual, forecast)  # MAE
    mpe = np.mean((forecast - actual) / actual)  # MPE
    mse = mean_squared_error(actual, forecast)  # MSE
    rmse = sqrt(mse)  # RMSE
    return {
        "ME   - Mean Error                 ": round(me.iloc[0], 3),
        "MAE  - Mean Absolute Error        ": round(mae, 3),
        "MAPE - Mean Absolute Percent Error": round(mape.iloc[0], 5),
        "MPE  - Mean Percentage Error      ": round(mpe.iloc[0], 5),
        "MSE  - Mean Squared Error         ": round(mse, 3),
        "RMSE - Root Mean Squared Error    ": round(rmse, 3),
    }


def fit_predict(
    df: pd.DataFrame,
    df_holidays: pd.DataFrame = None,
    x_vars: str = False,
    x_standardize: str = "auto",
    plot_predictions: bool = False,
    plot_pred_interactive: bool = False,
    plot_components: bool = False,
    freq_data: str = "D",
    future_pred_period: int = False,
    growth: str = "linear",
    cap: float = False,
    floor: float = False,
    yearly_seasonality: str = "auto",
    weekly_seasonality: str = "auto",
    daily_seasonality: str = "auto",
    custom_seasonality: list = False,
    seasonality_mode: str = "additive",
    seasonality_prior_scale: float = 10.0,
    holidays_prior_scale: float = 10.0,
    holidays_country: str = None,
    interval_width: float = 0.95,
    changepoints: list = None,
    n_changepoints: int = 25,
    changepoint_range: object = 0.8,
    changepoint_prior_scale: float = 0.05,
    mcmc_samples: int = 0,
    uncertainty_samples: int = 1000,
) -> tuple:
    """Fit prophet model, returning the forecast df containing predictions & their interval of confidence.

    Args:
        df: input df. Must contain "ds" and "y" columns, and optionally all the exogenous variables.
        df_holidays: df with columns holiday (string) and ds (date type)
        x_vars: Exogenous regressors used to fit y. Note: To predict the future, a df of future x_vars is required.
        x_standardize: Whether to standardize the regressors prior to fitting.
            Can be 'auto'(standardize if not binary), True, False (default="auto")
        plot_predictions: Whether to plot the Predictions & Observed values or not.
        plot_pred_interactive: Whether to plot Predictions & Observed values using an Interactive plots of plotly.
        plot_components: Whether to plot forecasts components: Trend & seasonalities.
        freq_data: Frequency of the data, used to make future predictions.
            (pd.date_range format: 'H':hourly, 'D':Daily, 'MS':Month Start, 'M':Month End)
        future_pred_period: N° of periods (hours/days/months) to predict in the future. False for no future predictions.
        growth: linear or logistic trend. If logistic you need to provide cap and floor of your predictions.
            Recommendation: Generally use linear, unless you know of a particular logistic trend with saturation
        cap: Cap value for logistic growth (saturating maximum).
            Cap does not have to be constant. If the market size is growing, then cap can be an increasing sequence.
        floor: Floor value for logistic growth (saturating minimum).
            To use a logistic growth trend with a saturating minimum, a maximum capacity must also be specified.
        yearly_seasonality: Whether to include yearly_seasonality. Can be 'auto', True, False.
        weekly_seasonality: Whether to include weekly_seasonality. Can be 'auto', True, False.
        daily_seasonality: Whether to include daily_seasonality. Can be 'auto', True, False.
        custom_seasonality: List containing custom seasonality in the format:
            [name, freq_period in a year, fourier_order] (e.g ["Quarterly", (365.25/4), 10]
        seasonality_mode: 'additive' (default) or 'multiplicative'.
            Recommendation: `additive` if the seasonality trend is "constant" over the entire period.
            `multiplicative` if seasonality effect is really different during the period (e.g. fast-growing variable)
        seasonality_prior_scale: strength of the seasonality model. larger values => larger seasonal fluctuations.
            Recommendation: Use the default, or increase it up to 25 if you know seasonalities have big effect.
        holidays_prior_scale: strength of the holiday components model.
            Recommendation: Use the default, or increase it up to 40 if you know holidays have big effect.
        holidays_country: name of the country of which load standard holidays (e.g. "US").
        interval_width: Float, width of the uncertainty intervals provided for the forecast.
            If mcmc_samples=0, this will be only the uncertainty in the trend using the MAP estimate of
            the extrapolated generative model. If mcmc.samples>0, this will be integrated over all model
            parameters, which will include uncertainty in seasonality.
        changepoints: List of dates at which to include potential changepoints.
            If not specified, changepoints are selected automatically.
            Recommendation: Use the default
        n_changepoints: Number of potential changepoints to include. Not used if input `changepoints` is supplied.
            If `changepoints` is not supplied, then n_changepoints potential changepoints are selected uniformly from
            the first `changepoint_range` proportion of the history.
            Recommendation: Use the default
        changepoint_range: Proportion of history in which trend changepoints will be estimated.
            Defaults to 0.8 for the first 80%. Not used if `changepoints` is specified.
            Recommendation: Use the default
        changepoint_prior_scale: Flexibility of automatic changepoint selection & consequently of the trend.
            Increase it to make the trend more flexible allowing many changepoints, but risking overfitting.
            Recommendation: Use the default (0.05), or try up to 0.2
        mcmc_samples: Integer, if 0, will do MAP (Maximum a Posteriori) estimation to train and predict.
            If >0, will do full Bayesian inference with the specified number of MCMC (Markov Chain Monte Carlo) samples.
            Recommendation: Use the default
        uncertainty_samples: Number of simulated draws used to estimate uncertainty intervals.
            Settings this value to 0 or False will disable uncertainty estimation and speed up the calculation.
            Recommendation: Use default, unless you want to speed-up the environment sacrificing model precision.

    Returns:
        forecast: a dataframe containing past observations + forecasts
        m: the prophet model estimated
        seasonalities: list containing the seasonalities fitted by the model.

    """

    # Set-up the prophet model "m"
    m = Prophet(
        growth=growth,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        seasonality_mode=seasonality_mode,
        seasonality_prior_scale=seasonality_prior_scale,
        holidays=df_holidays,
        holidays_prior_scale=holidays_prior_scale,
        interval_width=interval_width,
        changepoints=changepoints,
        n_changepoints=n_changepoints,
        changepoint_range=changepoint_range,
        changepoint_prior_scale=changepoint_prior_scale,
        mcmc_samples=mcmc_samples,
        uncertainty_samples=uncertainty_samples,
    )
    # Add holidays of the country if specified
    if holidays_country:
        m.add_country_holidays(country_name=holidays_country)

    # Add exogenous regressors if specified
    if x_vars:
        if isinstance(x_vars, str):
            for x_i in list([x_vars]):
                m.add_regressor(
                    x_i,
                    prior_scale=None,  # scale for the normal prior (holidays_prior_scale if not provided)
                    standardize=x_standardize,  # whether to standardize the regressors prior to fitting
                    mode=None,
                )  # 'additive' or 'multiplicative' (default=seasonality_mode)
        elif isinstance(x_vars, list):
            for x_i in x_vars:
                m.add_regressor(x_i, prior_scale=None, standardize=x_standardize, mode=None)
        df_X = df[x_vars].copy().reset_index(drop=True)
        df_X.columns = [str(col) + "_fact" for col in df_X.columns]

    # Add custom seasonalities
    if custom_seasonality:
        m.add_seasonality(
            name=custom_seasonality[0],
            period=custom_seasonality[1],
            fourier_order=custom_seasonality[2],
        )

    # Fit the model for the past observation of the df
    df_fact = df["y"].copy().reset_index(drop=True)
    if isinstance(cap, (int, float)):
        df["cap"] = cap
    if isinstance(floor, (int, float)):
        df["floor"] = floor
    with suppress_stdout_stderr():  # to suppress some verbose outputs
        m = m.fit(df)

    # Make the forecast. If future_pred_period is set-up, make predictions also for the future
    if future_pred_period:
        df = m.make_future_dataframe(periods=future_pred_period, freq=freq_data)
        if isinstance(cap, (int, float)):
            df["cap"] = cap
        if isinstance(floor, (int, float)):
            df["floor"] = floor
    forecast = m.predict(df)
    forecast["fact"] = df_fact.reset_index(drop=True)

    # Plot predictions & Observed values
    if plot_predictions:
        print(
            "1.A Plot of Observed & Predicted values + Changepoints "
            "(date points where the time series have abrupt changes in the trajectory)"
        )
        fig1 = m.plot(forecast)
        fig1_ = add_changepoints_to_plot(fig1.gca(), m, forecast)
    # Plot predictions & Observed values, using an Interactive plots of plotly
    if plot_pred_interactive:
        print("1.B Plot of Observed & Predicted values - in interactive window")
        fig2 = plot_plotly(m, forecast)  # This returns a plotly Figure
        py.iplot(fig2)

    # Plot forecast components
    if plot_components:
        print(
            "2. Plot of forecasts components: Trend & seasonality (weekly/yearly & holidays if added)"
        )
        fig3 = m.plot_components(forecast)

    # define seasonalities containing all the seasonalities/holidays/regressors included in the model
    seasonalities = list_seasonalities(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        custom_seasonality=custom_seasonality,
        holidays_country=holidays_country,
        x_vars=x_vars,
    )

    # Keep just the useful columns
    forecast = forecast.loc[:, forecast.columns.isin(
        list(["ds", "trend", "yhat", "yhat_lower", "yhat_upper", "fact"]) + seasonalities)]
    return forecast, m, seasonalities


def list_seasonalities(
    yearly_seasonality: str = False,
    weekly_seasonality: str = False,
    daily_seasonality: str = False,
    custom_seasonality: list = False,
    holidays_country: str = None,
    x_vars: list = False,
) -> list:
    """Transforms a list of boolean values that specify if each seasonal components need to be fit,
        into a list of variables to be kept by the dataframe.

    Args:
        yearly_seasonality: Whether to include yearly_seasonality. Can be 'auto', True, False.
        weekly_seasonality: Whether to include weekly_seasonality. Can be 'auto', True, False.
        daily_seasonality: Whether to include daily_seasonality. Can be 'auto', True, False.
        custom_seasonality: List containing custom seasonality in the format:
            [name, freq_period in a year, fourier_order] (e.g ["Quarterly", (365.25/4), 10]
        holidays_country: name of the country of which load standard holidays (e.g. "US").
        x_vars: Exogenous regressors used to fit y. Note: To predict the future, a df of future x_vars is required.

    Returns:
        (list): seasonal components to be kept in the dataframe

    """
    seasonalities = []
    if yearly_seasonality:
        seasonalities.append("yearly")
    if weekly_seasonality:
        seasonalities.append("weekly")
    if daily_seasonality:
        seasonalities.append("daily")
    if custom_seasonality:
        seasonalities.append(custom_seasonality[0])
    if holidays_country:
        seasonalities.append("holidays")
    if x_vars:
        if isinstance(x_vars, str):
            seasonalities.append(x_vars)
            seasonalities.append(x_vars + "_fact")
        elif isinstance(x_vars, list):
            seasonalities = seasonalities + x_vars + [sub + "_fact" for sub in x_vars]
    return seasonalities


class suppress_stdout_stderr(object):
    """A context manager for doing a "deep suppression" of stdout and stderr in Python,
    i.e. will suppress all print, even if the print originates in a compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed to stderr just before a
    script exits, and after the context manager has exited.
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)
