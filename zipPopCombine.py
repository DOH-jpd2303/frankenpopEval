# Load libraries
import os
from zipfile import ZipFile
import pandas as pd
import glob
import itertools
import matplotlib.pyplot as plt

# Read in MARS 97 categories
mars97Cats = pd.read_excel(
    os.path.join(os.getenv("ofmPopDir"), "SADE Data Dictionary.xlsx"),
    sheet_name="MARS97",
    dtype="str")
mars97Cats = mars97Cats[["Mars97Code", "LabelS"]]
mars97Cats.columns = ["RaceMars97", "RaceCat"]

# Columns to group and sum race pops by
grpCols = ["Year", "ZipCode", "Hispanic", "AgeGroup", "Gender", "RaceCat"]

############################################################
# Frankenpop
############################################################
# Directory of FP zip code files
fpDir = os.path.join(os.getenv("piePopDir"), "zipcode 2010-2020.zip")

# Locate zip folder, read in all files
zf = ZipFile(fpDir)
def readFun(zf, f):
    return (pd.read_csv(zf.open(f), compression="gzip"))
fplist = [readFun(zf, f) for f in zf.namelist()]
fp = pd.concat(fplist)

# Filter to 2021, rename/reorganize columns
fp = fp[fp["Year"] >= 2011]
fp.columns = fp.columns.str.replace(r"[0-9]{4}", "", regex=True)
fp.columns = fp.columns.str.replace("Population", "fpPopulation")

# Add proper string padding
fp["ZipCode"] = fp["ZipCode"].astype(str).str.pad(5, side = "left", fillchar="0")
fp["AgeGroup"] = fp["AgeGroup"].astype(str).str.pad(3, side = "left", fillchar="0")
fp["RaceMars97"] = fp["RaceMars97"].astype(str).str.pad(5, side = "right", fillchar="0")
fp = fp.merge(mars97Cats, how = "left")

# Get sum of counts by age category
fp2 = fp.groupby(grpCols)["fpPopulation"].sum().reset_index()

# Not all combinations have values because of 0 population
# Create placeholder rows for all combos
frameCols = ["Hispanic", "AgeGroup", "Gender", "RaceCat", "Year", "ZipCode"]
frameVals = [fp2[x].unique() for x in frameCols]
frameVals2 = pd.DataFrame(itertools.product(*frameVals))
frameVals2.columns = frameCols
fp3 = frameVals2.merge(fp2, how="left")

############################################################
# OFM
############################################################
# Identify all OFM zip files
ofmDir = os.path.join(os.getenv("ofmPopDir"), "ZIPcodes\CSV\New race categories")
ofmFiles = glob.glob(ofmDir + "\*.csv")

# Read in zip files, add string padding to categoricals, merge with race data
def ofmReadFun(x):
    df = pd.read_csv(x)
    df.columns = df.columns.str.replace(r"[0-9]{4}", "", regex=True)
    return (df)
ofm = pd.concat([ofmReadFun(x) for x in ofmFiles])
ofm["ZipCode"] = ofm["ZipCode"].astype(str).str.pad(5, side = "left", fillchar="0")
ofm["AgeGroup"] = ofm["AgeGroup"].astype(str).str.pad(3, side = "left", fillchar="0")
ofm["RaceMars97"] = ofm["RaceMars97"].astype(str).str.pad(5, side = "right", fillchar="0")
ofm = ofm.merge(mars97Cats, how = "left")

# Get sum of counts by age category
ofm2 = ofm.groupby(grpCols)["Population"].sum().reset_index()

# Add missing rows, fill with 0
frameVals = [ofm2[x].unique() for x in frameCols]
frameVals2 = pd.DataFrame(itertools.product(*frameVals))
frameVals2.columns = frameCols
ofm3 = frameVals2.merge(ofm2, indicator=True, how="left").drop("_merge", axis=1)

############################################################
# Combine
############################################################
# Merge and organize
keepCols = ["Year", "ZipCode", "Hispanic", "AgeGroup", "Gender", 
            "RaceCat", "fpPopulation", "Population", "_merge"]
comb = pd.merge(fp3, ofm3, how="outer", indicator=True)[keepCols]

import pickle
with open("combPops.pickle", "wb") as f:
    pickle.dump(comb, f, protocol=pickle.HIGHEST_PROTOCOL)
