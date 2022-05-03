# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 08:42:27 2022

@author: Admin
"""

from Analytics import eurostats_loader
import pandas as pd
import numpy as np
from statsmodels.tsa.deterministic import CalendarFourier, DeterministicProcess
from statsmodels.graphics.tsaplots import plot_pacf
from scipy.signal import periodogram
from sklearn.linear_model  import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["#0645ad", "#800020"]) 

#%% Create Data
Weekly_Deaths = eurostats_loader()
Weekly_Deaths = Weekly_Deaths[Weekly_Deaths.index.year >= 2008]

Weekly_Deaths_train = Weekly_Deaths[Weekly_Deaths.index.year < 2019]
Weekly_Deaths_val = Weekly_Deaths[Weekly_Deaths.index.year == 2019]
Weekly_Deaths_test = Weekly_Deaths[Weekly_Deaths.index.year > 2019]


#%% Periodogram of Series
fs = pd.Timedelta("1Y") / pd.Timedelta("1W")
f, Pxx = periodogram(Weekly_Deaths_train.Value, fs=fs, detrend="linear", scaling="spectrum")
# The Power Spectrum Pxx indicates the share of each frequency of the variance of the Time Series.
print(np.sum(Pxx) == np.var(Weekly_Deaths_train.Value))
plt.plot(f, Pxx)
plt.xlabel('Frequency [Year]')
plt.ylabel('Power Spectrum [V**2]')
plt.show()

#%% Modeling of Time Series

fourierA = CalendarFourier(freq="A", order=3)


y_train = Weekly_Deaths_train.Value

dp = DeterministicProcess(index=y_train.index.to_period("W"),
                          constant=True,               # dummy feature for bias (y-intercept)
                          order=1,                     # trend (order 1 means linear)
                          additional_terms=[fourierA],) # annual seasonality (fourier)
X_train = dp.in_sample()

val_index = Weekly_Deaths_val.index
X_val = dp.out_of_sample(len(val_index), val_index)

#%% Fit Models and Plot Results.

Models = [LinearRegression(fit_intercept=False),
          GradientBoostingRegressor(max_depth=1)]

num_models = len(Models)
fig, axes = plt.subplots(num_models,2,layout="constrained",sharex="col",figsize = (15,8))

for i,model in enumerate(Models):
    
    model.fit(X_train,y_train)
    y_pred = pd.Series(model.predict(X_train).reshape(-1), index=y_train.index)
    y_val = pd.Series(model.predict(X_val).reshape(-1), index=val_index)
    
    mse = np.mean(np.sqrt((y_val-Weekly_Deaths_val.Value)**2))
    
    ax_train = axes[i,0]
    #ax_train.set_title(type(model).__name__)
    y_pred.plot(ax=ax_train)
    Weekly_Deaths_train.Value.plot(ax=ax_train)
    
    ax_val = axes[i,1]
    ax_val.axes.annotate(f"MSE: {mse:.2f}", xy=(0.8,0.9), xycoords='axes fraction', fontsize=10)
    y_val.plot(ax=ax_val)
    Weekly_Deaths_val.Value.plot(ax=ax_val)

#%% Analyze Residuals
residuals = Weekly_Deaths_train.Value - y_pred
fig, ax = plt.subplots(2,1, layout="constrained")
residuals.plot(ax=ax[0], kind="hist").set_title("Distribution of Residuals")
plot_pacf(residuals, ax=ax[1], method='ols', zero=False)
ax[1].set_ylabel("Correlation")
    
#%% Calculate Excess Deaths with best model.

y_comb_train = Weekly_Deaths[Weekly_Deaths.index.year < 2020]

dp = DeterministicProcess(index=y_comb_train.index.to_period("W"),
                          constant=True,               # dummy feature for bias (y-intercept)
                          order=1,                     # trend (order 1 means linear)
                          additional_terms=[fourierA],  # annual seasonality (fourier)
                          drop=True,)                  # drop terms to avoid collinearity


X_comb_train = dp.in_sample()

model = GradientBoostingRegressor(max_depth=1)
model.fit(X_comb_train, y_comb_train)
y_comb_pred = pd.Series(model.predict(X_comb_train).reshape(-1), index=y_comb_train.index)


test_index = Weekly_Deaths_test.index
X_test = dp.out_of_sample(len(test_index), test_index)
y_test = pd.Series(model.predict(X_test).reshape(-1), index=test_index)
excess_deaths = np.sum(Weekly_Deaths_test.Value-y_test)

fig_test, ax_test = plt.subplots()
ax_test.axes.annotate(f"Estimated Excess Deaths: {excess_deaths:.0f}", xy=(0.55,0.9), xycoords='axes fraction', fontsize=8)
y_test.plot(ax=ax_test)
Weekly_Deaths_test.Value.plot(ax=ax_test)





