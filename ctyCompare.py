# Load libraries
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import numpy as np

# Load in the combined file
with open("countyCombPops.pickle", "rb") as f:
    df = pickle.load(f)

# Fill missing values with 0, calculate difference between estimates
df[["fpPopulation", "Population"]] = df[["fpPopulation", "Population"]].fillna(0)
df["dif"] = df["fpPopulation"] - df["Population"]
df["dif"].sum() # 282,958 delta (28.3k per year, on average)

# Categorize age for some crosstabs
df["AgeCat"] = np.select(
    [
        df["AgeGroup"].between("000", "017"),
        df["AgeGroup"].between("018", "044"),
        df["AgeGroup"].between("045", "064"),
        df["AgeGroup"] > "064"
    ],
    ["0-17", "18-44", "45-64", "65+"],
    default = "Unknown"
)

############################################################
# County by year
############################################################
# Compare sums by county
ctySums = df.groupby(["Year", "County"])[["fpPopulation", "Population", "dif"]].\
    sum().sort_values(["County", "Year"]).reset_index()
ctySums["pctDiff"] = ctySums["dif"] / ctySums["Population"]
ctySums = ctySums.round(3)
ctySums.to_csv("ctySumsFpVsOfm.csv", index = False)

# Plot overall county by year
fix, ax = plt.subplots(figsize=(12,8.5))
bp = ctySums.groupby("county").plot(x = "Year", y = "")


############################################################
# Age group by year
############################################################
# Compare sums by county
ageSums = df.groupby(["Year", "AgeCat"])[["fpPopulation", "Population", "dif"]].\
    sum().sort_values(["Year", "AgeCat"]).reset_index()
ageSums["pctDiff"] = ageSums["dif"] / ageSums["Population"]
ageSums = ageSums.round(3)
ageSums.to_csv("ageSumsFpVsOfm.csv", index = False)

############################################################
# Age group + County by year
############################################################
# Compare sums by county
ageCtySums = df.groupby(["Year", "County", "AgeCat"])[["fpPopulation", "Population", "dif"]].\
    sum().sort_values(["AgeCat", "County", "Year"]).reset_index()
ageCtySums["pctDiff"] = ageCtySums["dif"] / ageCtySums["Population"]
ageCtySums = ageCtySums.round(3)
ageCtySums.to_csv("ageCountySumsFpVsOfm.csv", index = False)
