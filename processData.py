# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 16:22:17 2018

@author: JulioCaye
"""
import pandas as pd
from sqlalchemy import create_engine

##connect to database
engine = create_engine("sqlite:///desafio.db")
selic = pd.read_sql('selic', engine)
petr4 = pd.read_sql('petr4', engine)

##set dates column to datetime objects and remove irrelevant columns
selic["inicio"] = pd.to_datetime(selic.periodo.apply(lambda x: x[:10]), infer_datetime_format = True)
selic = selic.drop(["index", "n_reuniao", "data_reuniao", "vies_reuniao", "TBAN", "periodo", "meta_selic"], axis = 1)
selic = selic[1:]

petr4.Data = pd.to_datetime(petr4.Data, infer_datetime_format = True)

##drop months without selic values or without PETR4 data and drop year and month columns
data_monthly = ((data_monthly[data_monthly.selic != 0])[data_monthly.volume != 0]).drop(["year", "month"], axis = 1)

##normalize all fields
for key in data_monthly.keys():
    data_monthly[key] = (data_monthly[key] - data_monthly[key].min())/(data_monthly[key].max() - data_monthly[key].min())

##collect data by month average for the closing value and month total for volume and negotiations
year = 2018
while (year > 2007):
    month = 12
    while month > 0:
        row = {}
        row["fech"] = (petr4[petr4.Data.apply(lambda x: x.month == month and x.year == year)])["Fech."].mean()
        row["volume"] = (petr4[petr4.Data.apply(lambda x: x.month == month and x.year == year)])["Volume"].sum()
        row["neg"] = (petr4[petr4.Data.apply(lambda x: x.month == month and x.year == year)])["Negócios"].sum()
        row["year"] = year
        row["month"] = month
        month -= 1
        data_monthly = data_monthly.append(row, ignore_index = True)
    year -= 1

##find selic values for each month
year = 2018
selic_values = []
for i, row in data_monthly.iterrows():
    values = selic[selic.inicio.apply(lambda x: x.year >= row["year"] and x.month >= row["month"])]
    values = values["taxa_selic_media"].tolist()
    if len(values) == 0:
        selic_values.append(0)
    else:
        selic_values.append(values[-1])
data_monthly["selic"] = selic_values

##drop months without selic values or without PETR4 data
data_monthly = ((data_monthly[data_monthly.selic != 0])[data_monthly.volume != 0]).drop(["year", "month"], axis = 1)
for key in data_monthly.keys():
    data_monthly[key] = (data_monthly[key] - data_monthly[key].min())/(data_monthly[key].max() - data_monthly[key].min())

##plot raw selic and closing values
data_monthly.plot(y = ["selic", "fech"])

##fit linear model fech = A * selic + B and print modeled curve
from sklearn.linear_model import LinearRegression as LR
model = LR().fit(data_monthly.selic.values.reshape(-1, 1), data_monthly.fech)
data_monthly["model_values"] = model.predict(data_monthly.selic.values.reshape(-1, 1))

##calculate R^2
from sklearn.metrics import r2_score
score = r2_score(data_monthly.fech, data_monthly.model_values)

##plot
data_monthly.plot(y = ["fech", "model_values"], title = "Model and true values with R2 = " + str(score))

##find residuals
data_monthly["residual"] = data_monthly.fech - data_monthly.model_values
data_monthly.plot(y = ["residual"])

##autocorrelate them with different lag times
auto = []
for i in range(48):
    auto.append(data_monthly.residual.autocorr(i))

import matplotlib.pyplot as plt
plt.figure()
plt.plot(auto)
plt.show()