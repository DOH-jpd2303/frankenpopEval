# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import pickle

# Load in the combined file
with open("combPops.pickle", "rb") as f:
    df = pickle.load(f)

# Fill missing values with 0, calculate difference between estimates
df[["fpPopulation", "Population"]] = df[["fpPopulation", "Population"]].fillna(0)
df["dif"] = df["fpPopulation"] - df["Population"]
df["dif"].sum() # 75,164 over 10 years...NBD

# Compare sums by zip code
zipSums = df.groupby(["Year", "ZipCode"])[["fpPopulation", "Population", "dif"]].\
    sum().sort_values(["ZipCode", "Year"]).reset_index()
zipSums["pctDiff"] = zipSums["dif"] / zipSums["Population"]
zipSums = zipSums.round(3)
zipSums.to_csv("zipSumsFpVsOfm.csv", index = False)

# Get differences of at least 5 + pct differences of 10
checkZips = zipSums[(abs(zipSums["dif"] >= 5)) & (abs(zipSums["pctDiff"] >= 10))]["ZipCode"].unique()
zipSumsCheck = zipSums[zipSums["ZipCode"].isin(checkZips)]
zipSumsCheck.to_csv("zipSumsCheck.csv", index=False)
