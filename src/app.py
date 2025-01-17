from shiny import ui, render, App
from pathlib import Path
import pickle
from matplotlib import pyplot as plt
from collections import Counter
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

############################

infile = Path(__file__).parent / 'Votes_compressed.csv.gz'
df = pd.read_csv(infile, compression='gzip')


for col in df.columns[2:]:
    df[col] = df[col].astype(int)


candidates = {}
for candidate in df.columns[2:-6]: 
    n, name = candidate.split(' ', 1)
    candidates[n] = name
    candidates[name] = n

df.columns = ['Vote Type', 'Poll'] + list(candidates)[::2] + ['1Y', '1N', '2Y', '2N', '3Y', '3N']



MayoralCandidates = [candidates[str(i)] for i in range(50,65)]
mayor_votes = {str(i): df[str(i)].sum() for i in range(50,65)}
MayoralCandidates = sorted(MayoralCandidates, key = lambda x: mayor_votes[candidates[x]], reverse=True)
CouncilCandidates = [candidates[str(i)] for i in range(100,159)]


df['Mayor'] = df.loc[:, '50':'64'].sum(axis=1)
df['Park'] = df.loc[:, '200':'231'].sum(axis=1)
df['Council'] = df.loc[:, '100':'158'].sum(axis=1)
df['Borrow'] = df.loc[:, '1Y':'3N'].sum(axis=1)



############################



app_ui = ui.page_fluid(
    ui.h2("Vancouver 2022 Election Data"),
    
    ui.input_select("Candidate", 
                    "Choose a candidate:", 
                    {
                        "Mayoral Candidates": {i:i for i in MayoralCandidates}, 
                        "Council Candidates": {i:i for i in CouncilCandidates}
                    },
                   ),
    ui.output_plot("plot"),
    ui.output_plot("plot2")


)


def server(input, output, session):
    @output
    @render.plot
    def plot(): 
        df_mayor = df[df[candidates[input.Candidate()]]==1]
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.subplot(121)
        df_mayor['Council'].hist(ax=ax1, bins=[0.5+i for i in range(-1, 11)], density=True, align='mid')
        plt.title('Number of Council Votes')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.subplot(122)
        df_mayor['Park'].hist(ax=ax2, bins=[0.5+i for i in range(-1, 8)], density=True, align='mid')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.title('Number of Park Board Votes')
        #ax.set_axisbelow(True)
        #ax.grid(color='gray', linestyle='dashed')
        return fig
    
    @output
    @render.plot
    def plot2(): 
        df_mayor = df[df[candidates[input.Candidate()]]==1]
        fig, ax = plt.subplots()
        data = df_mayor.loc[:,'100':'158'].sum().sort_values(ascending=False)[0:15]
        data = data.sort_values(ascending=True)
        data.index = data.index.map(lambda x: candidates[x])
        data.plot.barh(ax=ax, xlim = [0, df_mayor.shape[0]])
        
        plt.title('Council Votes')
        #ax.set_axisbelow(True)
        #ax.grid(color='gray', linestyle='dashed')
        return fig

app = App(app_ui, server)
