import csv
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import xlwings as xw #https://docs.xlwings.org/en/stable/matplotlib.html

with open(sys.argv[1]) as fin, open(sys.argv[1]+'.csv', 'w') as fout:
    o = csv.writer(fout)
    for line in fin:
        o.writerow(line.split())

filename = sys.argv[1]+'.csv'

df = pd.read_csv(filename, engine='c')

b16 = lambda x: int(x, 16)

state = pd.Series(df.loc[:, "B0"])

time = pd.Series(df.loc[:, "TIME"])

Ph1_U = pd.Series(df.loc[: , "B2"])
Ph1_V = pd.Series(df.loc[: , "B3"]).apply(lambda x: int(x,16)) #https://stackoverflow.com/questions/37955856/convert-pandas-dataframe-column-from-hex-string-to-int

Ph2_U = pd.Series(df.loc[: , "B4"])
Ph2_V = pd.Series(df.loc[: , "B5"]).apply(lambda x: int(x,16))


time_np = time.to_numpy()
Ph1_U_np = Ph1_U.to_numpy()
Ph1_V_np = Ph1_V.to_numpy()
Ph2_U_np = Ph2_U.to_numpy()
Ph2_V_np = Ph2_V.to_numpy()

def plotSeperate():
    fig, axs = plt.subplots(2) #https://matplotlib.org/devdocs/gallery/subplots_axes_and_figures/subplots_demo.html
    fig.suptitle('Title goes here...')
    fig2 = plt.figure()
    axs[0].plot(time, Ph1_V_np)
    axs[1].plot(time, Ph2_V_np)
    plt.show()
    sht = xw.Book().sheets[0]
    sht.pictures.add(fig2, name='MyPlot', update=True)

def plotOverlaid():
    fig2 = plt.figure()
    plt.plot(time, Ph1_V_np, 'r') # plotting t, a separately 
    plt.plot(time, Ph2_V_np, 'b') # plotting t, b separately
    plt.show()
    sht = xw.Book().sheets[0]
    sht.pictures.add(fig2, name='MyPlot', update=True)
