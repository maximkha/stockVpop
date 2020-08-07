from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import scipy
import argparse

countryInfo = dict()
countryInfo["USA"] = ("SPY", "United States")
countryInfo["RUS"] = ("RTSI", "Russian Federation")
countryInfo["CHN"] = ("Shanghai Composite", "China")

#DISP_PLOT = False
def boolstr(x):
    r = ["false", "true", "0", "1", "f", "t", "no", "yes"].index(x.lower())
    if r == -1:
        raise Exception("Invalid bool")
    return r % 2 == 1

#curCountry = countryInfo["CHN"]
parser = argparse.ArgumentParser()
parser.add_argument("country", type=str, help="The country to use for calculations")
parser.add_argument("display", type=boolstr, help="Show a pop v price scatter plot", )
args = parser.parse_args()
if args.country not in countryInfo:
    print("No info on " + str(args.country))
    exit()
#print(args)
DISP_PLOT = args.display
curCountry = countryInfo[args.country]

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def GetCorrTime(data):
    return GetCorr(range(len(data)), data)
    #slope_1, intercept_1, r_val_1, p_val_1, stderr_1 = stats.linregress(range(len(data)), data) #assume data is linear with time
    #return r_val_1 ** 2

def GetCorr(data, data2):
    return stats.spearmanr(data, data2).correlation
    #slope_1, intercept_1, r_val_1, p_val_1, stderr_1 = stats.linregress(data, data2)
    #return r_val_1 ** 2

popDF = pd.read_csv("API_SP.POP.TOTL_DS2_en_csv_v2_1308146.csv")
russiaRow = popDF.loc[popDF["Country Name"] == curCountry[1]]
russiaRow = russiaRow[russiaRow.columns.difference(["Country Name","Country Code","Indicator Name","Indicator Code"])]

years = russiaRow.columns.tolist()[:-1] #the format left a extra comma on the header so pandas interpreted it as an unamed column
population = russiaRow.values[0][:-1]

commonYears = []
commonPop = []
commonPrice = []
rstiDF = pd.read_csv(curCountry[0] + " Historical Data.csv")
rstiDF["Date"] = pd.to_datetime(rstiDF["Date"])
for i in range(len(years)):
    year = years[i]
    rows = rstiDF.loc[rstiDF["Date"].dt.year == int(year)]
    if len(rows) == 0:
        continue
    pop = population[i]
    commonPop.append(pop)
    commonYears.append(year)
    commonPrice.append(rows.iloc[[-1]]["Price"].astype(str).str.replace(",","").astype(float).values[0])

print("Name: " + curCountry[1])
print("Pop        SPR: " + str(GetCorrTime(commonPop)))
print("Prce       SPR: " + str(GetCorrTime(commonPrice)))
print("PopVPrce   SPR: " + str(GetCorr(commonPop, commonPrice)))

if DISP_PLOT:
    plt.scatter(NormalizeData(commonPop), NormalizeData(commonPrice))
    plt.ylabel("price")
    plt.xlabel("population")
    plt.title(curCountry[1])
    plt.show()