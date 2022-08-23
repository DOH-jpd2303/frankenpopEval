#########################################################
#   SETUP AND LOAD DATA
#########################################################
# Load imports
import os
import pandas as pd
import numpy as np

# Identify all CSVs in the dir (exclude summary file)
fns = os.listdir()
fns = [x for x in fns if "csv" in x]
fns = [x for x in fns if "summary" not in x]

# Read in each CSV, add race col, combine
# Need to drop duplicates
df = pd.DataFrame()
for fn in fns:        
    nm = os.path.splitext(fn)[0]
    tmp = pd.read_csv(fn).drop_duplicates()
    tmp["RACE"] = nm
    df = df.append(tmp)

# Get the percent difference and whether the PCT dif is >10%
df["OfmToFranken"] = df["Ofm"]/df["Franken"]
df["PctDif"] = df["Difference"]/df["Franken"]
df["GtTenPctDif"] = -np.logical_and(df["OfmToFranken"] >= 0.9, df["OfmToFranken"] <= 1.1)
sort = ['all', 'aian', 'asian', 'black', 'hisp', 'multi', 'nhpi', 'white']
df["RACE"] = pd.Categorical(df["RACE"], ordered = True, categories = sort)


#########################################################
#   STATEWIDE OUTPUT
#########################################################
# Race summary values
sSum = pd.DataFrame(df.groupby("RACE")[["Franken", "Ofm"]].sum())
sSum["n"] = df.groupby("RACE")["Tract"].count()
sSum["totalDiff"] = sSum["Ofm"] - sSum["Franken"]
sSum["totalDifPct"] = sSum["totalDiff"]/sSum["Franken"]
sSum["meanCtDif"] = df.groupby("RACE")["Difference"].mean()
sSum["meanCtPctDif"] = df.groupby("RACE")["PctDif"].mean()
sSum["tractsHighlyVariable"] = df.groupby("RACE")["GtTenPctDif"].sum()
sSum["tractsHighlyVariablePct"] = sSum["tractsHighlyVariable"]/sSum["n"]
sSum["personsHighlyVariable"] = df[df["GtTenPctDif"]].groupby("RACE")["Franken"].sum()
sSum["personsHighlyVariablePct"] = sSum["personsHighlyVariable"]/sSum["Franken"]

# Sort data, output to CSV
sSum.to_csv("statesummary.csv")

#########################################################
#   COUNTY OUTPUT
#########################################################
# Get Washington FIPS codes from OFM
fips = pd.read_excel("geographic_codes.xlsx", index_col = None, \
    sheet_name = "County", usecols = ["COUNTY_NAME", "COUNTYFP"], dtype = str)
    
# Let's extract the FIPS codes from each census tract and join to our dictionary
df["COUNTYFP"] = df["Tract"].astype(str).str[2:5]
df2 = df.merge(fips, how = "left", on = "COUNTYFP")

# County summary values
cSum = pd.DataFrame(df2.groupby(["COUNTY_NAME", "RACE"])[["Franken", "Ofm"]].sum())
cSum["n"] = df2.groupby(["RACE", "COUNTY_NAME"])["Tract"].count().tolist()
cSum["totalDiff"] = cSum["Ofm"] - cSum["Franken"]
cSum["totalDifPct"] = cSum["totalDiff"]/cSum["Franken"]
cSum["tractsHighlyVariable"] = df2.groupby(["COUNTY_NAME", "RACE"])["GtTenPctDif"].sum()
cSum["tractsHighlyVariablePct"] = cSum["tractsHighlyVariable"]/cSum["n"]
cSum["personsHighlyVariable"] = df2[df2["GtTenPctDif"]].groupby(["COUNTY_NAME", "RACE"])["Franken"].sum()
cSum["personsHighlyVariablePct"] = cSum["personsHighlyVariable"]/cSum["Franken"]
cSum.sort_values(["RACE", "COUNTY_NAME"])
cSum.to_csv("countysummary.csv")