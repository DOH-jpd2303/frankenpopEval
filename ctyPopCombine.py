# Load libraries
import os
from zipfile import ZipFile
import pandas as pd
import glob
import itertools
import matplotlib.pyplot as plt
import pickle

# Read in MARS 97 categories
mars97Cats = pd.read_excel(
    os.path.join(os.getenv("ofmPopDir"), "SADE Data Dictionary.xlsx"),    
    sheet_name="MARS97",
    dtype="str")
mars97Cats = mars97Cats[["Mars97Code", "LabelS"]]
mars97Cats.columns = ["RaceMars97", "RaceCat"]

# Columns to group and sum race pops by
grpCols = ["Year", "County", "Hispanic", "AgeGroup", "Gender", "RaceCat"]

############################################################
# Frankenpop
############################################################
# Directory of FP zip code files
fpDir = os.path.join(
    os.getenv("piePopDir"), "blkgrp 2010-2020.zip"
)

# Locate zip folder, read in all files
zf = ZipFile(fpDir)
def readFun(zf, f, mars97Cats, grpCols):
    # Read in data, standardize columns
    df = pd.read_csv(zf.open(f), compression="gzip")
    df.columns = df.columns.str.replace(r"[0-9]{4}", "", regex=True)
    df.columns = df.columns.str.replace("Population", "fpPopulation")

    # Transform columns into final form, collapse by race/eth
    df["County"] = df["CensusBlockGroupCode"].astype(str).str[:5]
    df["AgeGroup"] = df["AgeGroup"].astype(str).str.pad(3, side = "left", fillchar="0")
    df["RaceMars97"] = df["RaceMars97"].astype(str).str.pad(5, side = "right", fillchar="0")    
    df = df.merge(mars97Cats, how = "left")
    df2 = df.groupby(grpCols)["fpPopulation"].sum().reset_index()
    return (df2)

# Run the functions on all files (skip 2010), then flatten into single DF
fplist = [readFun(zf, f, mars97Cats, grpCols) for f in zf.namelist()[1:]]
fp = pd.concat(fplist)

# Not all combinations have values because of 0 population
# Create placeholder rows for all combos
frameCols = ["Hispanic", "AgeGroup", "Gender", "RaceCat", "Year", "County"]
frameVals = [fp[x].unique() for x in frameCols]
frameVals2 = pd.DataFrame(itertools.product(*frameVals))
frameVals2.columns = frameCols
fp = frameVals2.merge(fp, how="left")

############################################################
# OFM
############################################################
# Identify all OFM zip files
ofmDir = os.path.join(os.getenv("ofmPopDir"), "County\CSV\New race categories")
ofmFiles = glob.glob(ofmDir + "\*.csv")

# Read in zip files, add string padding to categoricals, merge with race data
def ofmReadFun(x):
    df = pd.read_csv(x)
    df.columns = df.columns.str.replace(r"[0-9]{4}", "", regex=True)
    return (df)
ofm = pd.concat([ofmReadFun(x) for x in ofmFiles])
ofm["AgeGroup"] = ofm["AgeGroup"].astype(str).str.pad(3, side = "left", fillchar="0")
ofm["RaceMars97"] = ofm["RaceMars97"].astype(str).str.pad(5, side = "right", fillchar="0")
ofm = ofm.merge(mars97Cats, how = "left")
ofm = ofm.rename(columns={"CensusCountyCode": "County"})

# Get sum of counts by age category
ofm2 = ofm.groupby(grpCols)["Population"].sum().reset_index()

# Add missing rows, fill with 0
frameVals = [ofm2[x].unique() for x in frameCols]
frameVals2 = pd.DataFrame(itertools.product(*frameVals))
frameVals2.columns = frameCols
ofm3 = frameVals2.merge(ofm2, indicator=True, how="left").drop("_merge", axis=1)
ofm3["County"] = ofm3["County"].astype("str")

############################################################
# Combine and compare
############################################################
# Merge and organize
keepCols = ["Year", "County", "Hispanic", "AgeGroup", "Gender", 
            "RaceCat", "fpPopulation", "Population", "_merge"]
comb = pd.merge(fp, ofm3, how="outer", indicator=True)[keepCols]

# Save to file
with open("countyCombPops.pickle", "wb") as f:
    pickle.dump(comb, f, protocol=pickle.HIGHEST_PROTOCOL)
