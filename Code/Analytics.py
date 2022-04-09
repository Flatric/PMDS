import os
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
# Set image resolution very high.
mpl.rcParams['figure.dpi'] = 500


if "data" in globals():
    pass
else:
    relative_path = os.getcwd()[:-4] + "\\Data"
    data = pd.read_excel(f"{relative_path}\\Todesursachen 98-20.xlsx", index_col=[0,1], header=[0,1])
    data = data[data.columns].replace(["-","."],0)
    causes_of_death = list(data.loc[1999].index)
    
    # Age standardization.
    standard_pop = pd.read_csv(f"{relative_path}\\European Standard Population.txt", index_col=0)
    age_brackets = pd.read_csv(f"{relative_path}\\Bevölkerung nach Alter.csv",index_col=[0,1])
    
    # Merge brackets
    for i in [1,15,20,25]:
        if i == 1:
            j = 15
        else: 
            j = i+5
            
        age_brackets[f"{i} - {j}"] = age_brackets[age_brackets.columns[i:j]].sum(axis=1)
        # Remove all age brackets that have been merged already.
    age_brackets = age_brackets.drop(columns=[f"{k} - {k+1}" for k in range(1,30)])
        
    age_brackets = age_brackets.drop("Insgesamt",axis=1)
    age_brackets = age_brackets = age_brackets[["0 - 1", "1 - 15", "15 - 20",
                                                "20 - 25", "25 - 30","30 - 65", "65 und älter"]]


def death_cause(names, years, data=data):
    
    if years == "all":
        years = [year for year in range(1998,2021)]
    
    if type(names) is str:
        names = [names]
    if type(years) is int:
        years = [years]
        
    data = data.loc[years].groupby(level=1).sum()
    data = pd.DataFrame(data.loc[names]).transpose()
    data = data.unstack(level=0)
    data.columns = data.columns.droplevel([0]) 
    data["total"] = data["männlich"] + data["weiblich"]
        
    return data 
    
def total_deaths(start: int, end: int, names: list, standardize=True, data=data, age_brackets=age_brackets, standard_pop=standard_pop):
    """
    
    Count the total deaths that occured in each year between start and end
    Parameters
    ----------
    start : int
        Year from which to start counting.
    end : int
        Year up to which to count.
    names: list
        Types of death causes to be considered.
    standardize: bool
        Whether to age standardize the data w.r.t the standard population given
        in standard_pop.
    -------
    pd.Series
        Series containing total deaths indexed by year.

    """
    if type(names) == str:
        names = [names]
        
    years = [year for year in range(start, end+1)]
    
    if standardize:
       total_deaths = []
       for year in years:
           deaths = data.loc[year].loc[names].sum()
           # .unstack dissolves multi index s.t frame has two more columns instead of one.
           deaths = deaths.unstack(level=0)
           deaths["total"] = deaths["männlich"] + deaths["weiblich"]
           # Drop deaths where age is unknown.
           deaths = deaths.drop("Alter unbekannt",axis=0)["total"]
           # Reindex deaths s.t index is sorted by ascending age bracket.
           deaths = deaths.reindex([deaths.index[-1]] + list(deaths.index[:-1]))
           # Sum deaths from age brackets between 30 and 65.
           deaths30_65 = pd.Series(data=[deaths.iloc[5:12].sum()], index=["30 bis unter 65 Jahre"])
           # add deats30_65 as a new row.
           deaths = pd.concat([deaths,deaths30_65])
           # Sum deaths from age brackets above 65.
           deaths65_plus = pd.Series(data=[deaths.iloc[12:17].sum()], index=["65 Jahre und mehr"])
           deaths = pd.concat([deaths,deaths65_plus])
           # Remove finer age brackets that were aggregrated in the lines above.
           deaths = deaths.drop(deaths.index[5:17])
           
           ## Deaths per age group in a given year
           # Get Age Brackets for the corresponding year.
           brackets = age_brackets.loc["Insgesamt",year]
           # Equalize indices to correctly perform arithmetic operations with both dataframes.
           brackets.index = deaths.index
           # people per thousand
           deaths_per_bracket = deaths/brackets
           
           ## Standardized death rate
           standard_pop.index = deaths.index
           standardized_deaths = deaths_per_bracket * standard_pop["ESP 2013"]
           standardized_deaths = standardized_deaths.sum()
           total_deaths.append(standardized_deaths)
           
       data = {"year": years, "deaths": total_deaths}
       return pd.DataFrame(data=data)
           
    else:
        total_deaths = []
        for year in years:
            deaths = data.loc[year].loc[names].sum()
            deaths = deaths.unstack(level=0)
            deaths["total"] = deaths["männlich"] + deaths["weiblich"]
            # Drop deaths where age is unknown.
            deaths = deaths.drop("Alter unbekannt",axis=0)["total"]
            total_deaths.append(deaths.sum())
            
        data = {"year": years, "deaths": total_deaths}
        return pd.DataFrame(data=data)

if __name__ == "__main__":
    
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
    print(f"Mean of last three years for males: {male_young_deaths.loc[[2018,2019,2020]].mean() * {n_deaths_2021_males}\n}")
    print(f"Mean of last three years for females: {female_young_deaths.loc[[2018,2019,2020]].mean() * {n_deaths_2021_females}}")

    