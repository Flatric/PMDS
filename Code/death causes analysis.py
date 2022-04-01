import pandas as pd
import seaborn as sns

data = pd.read_excel("Todesursachen 98-20.xlsx", index_col=[0,1], header=[0,1])
data = data[data.columns].replace(["-","."],0)

#print(data.head,"\n")
#print(f"Columns: {data.columns}\n")
## Check for NaN values:
#print(f"NaN values: {data.isnull().sum()}\n")


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
    
def total_deaths(start: int, end: int, data=data):
    """
    
    Count the total deaths that occured in each year between start and end
    Parameters
    ----------
    start : int
        Year from which to start counting.
    end : int
        Year up to which to count.
    data : pd.DataFrame
        Pandas DataFrame containing data about death cases from the destatis website.
    Returns
    -------
    pd.Series
        Series containing total deaths indexed by year.

    """
    index = [year for year in range(start, end+1)]
    total_deaths = [data.loc[year,"Insgesamt"].sum() for year in index]
    return pd.Series(data=total_deaths , index=index)


# Example: 
#  Plotting total deaths from 1998 until 2020.
#total_deaths = total_deaths(1998,2020)   
#sns.lineplot(x=total_deaths.index, y=total_deaths)

test2 = death_cause("Grippe", 1998)
