# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:29:00 2022

@author: Admin
"""
from Analytics import data
import pandas as pd


# Get yearly total deaths between 1998 and 2020.
yearly_deaths = data.loc[[[year,"Insgesamt"] for year in range(1998,2021)]]

# Share of under one year olds of total deaths of males and females between age 0 and 15. 
male_juvenile_deaths = yearly_deaths["männlich"][["unter 1 Jahr","1 bis unter 15 Jahre"]]
female_juvenile_deaths = yearly_deaths["weiblich"][["unter 1 Jahr","1 bis unter 15 Jahre"]]

male_juvenile_deaths["ratio"] = male_juvenile_deaths["unter 1 Jahr"] / (male_juvenile_deaths["unter 1 Jahr"] +  male_juvenile_deaths["1 bis unter 15 Jahre"])
female_juvenile_deaths["ratio"] = female_juvenile_deaths["unter 1 Jahr"] / (female_juvenile_deaths["unter 1 Jahr"] +  female_juvenile_deaths["1 bis unter 15 Jahre"])

# Same procedures for people between 15 and 30.
male_young_deaths = yearly_deaths["männlich"][["15 bis unter 20 Jahre", "20 bis unter 25 Jahre", "25 bis unter 30 Jahre"]]
female_young_deaths = yearly_deaths["weiblich"][["15 bis unter 20 Jahre", "20 bis unter 25 Jahre", "25 bis unter 30 Jahre"]]

male_young_deaths["15 bis unter 20 Jahre"] = male_young_deaths["15 bis unter 20 Jahre"]/male_young_deaths.sum(axis=1)
female_young_deaths["15 bis unter 20 Jahre"] = female_young_deaths["15 bis unter 20 Jahre"]/female_young_deaths.sum(axis=1)

male_young_deaths["20 bis unter 25 Jahre"] = male_young_deaths["20 bis unter 25 Jahre"]/male_young_deaths.sum(axis=1)
female_young_deaths["20 bis unter 25 Jahre"] = female_young_deaths["20 bis unter 25 Jahre"]/female_young_deaths.sum(axis=1)

male_young_deaths["25 bis unter 30 Jahre"] = 1 - (male_young_deaths["20 bis unter 25 Jahre"] + male_young_deaths["15 bis unter 20 Jahre"])
female_young_deaths["25 bis unter 30 Jahre"] = 1 - (male_young_deaths["20 bis unter 25 Jahre"] + male_young_deaths["15 bis unter 20 Jahre"])

# Add index for plotting.
male_young_deaths.index = female_young_deaths.index = [year for year in range(1998,2021)]
# Plot development of shares.
male_young_deaths.plot(marker="o",markersize=4, title="Anteil an den männlichen Toten zwischen 15-30 Jahren", xlabel="Jahr", ylabel="Anteil")
female_young_deaths.plot(marker="o",markersize=4, title="Anteil an den weiblichen Toten zwischen 15-30 Jahren", xlabel="Jahr", ylabel="Anteil")
# Take mean of the last three years in order to calculate deaths for 2021.
n_deaths_2021_males = 1790
n_deaths_2021_females = 1127
print(f"Mean of last three years for males: {male_young_deaths.loc[[2018,2019,2020]].mean()} * {n_deaths_2021_males}\n")
print(f"Mean of last three years for females: {female_young_deaths.loc[[2018,2019,2020]].mean()} * {n_deaths_2021_females}")