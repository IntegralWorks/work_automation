import csv
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

df = pd.read_csv(sys.argv[1], engine='c')

#manually add this line to the first row of the csv if the automated method doesn't work
#A,B,C,D,E,F,G,H,I,J,K,

#declaring a dataframe row and inserting it: https://kite.com/python/answers/how-to-insert-a-row-into-a-pandas-dataframe
# letters = pd.DataFrame(['A','B','C','D','E','F','G','H','I','J','K']) //note: automated row insertion currently broken.
# newdf = pd.concat([letters,df], ignore_index=True)

#concatenating dataframe columns: https://stackoverflow.com/questions/21231834/creating-a-pandas-dataframe-from-columns-of-other-dataframes-with-similar-indexe
newdf = pd.concat([df['D'],df['E'],df['J'],df['K']],axis=1, keys=['timeCH1','CH1','timeCH2','CH2'])
newdf.to_csv('cleanData.csv')

#Sanity check of data
dataValidationNote = open("dataValidationNote.txt","a")

#validating time values
dataValidationNote.write("Were time values the same?: " + str(pd.Series.all(pd.Series.eq(pd.Series(df.loc[:, "D"]),pd.Series(df.loc[:, "J"])))) + "\n")

#ensuring that the waveform values are not the same
dataValidationNote.write("Were voltage values the same?: " + str(pd.Series.all(pd.Series.eq(pd.Series(df.loc[:, "E"]),pd.Series(df.loc[:, "K"])))) + "\n")
