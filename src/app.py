from shiny import ui, render, App
import pickle
from matplotlib import pyplot as plt
from collections import Counter
from matplotlib.ticker import PercentFormatter
import numpy as np
import pandas as pd

############################

df = pd.read_csv('2022MunicipalElectionAnonymousBallotMarking.csv', skiprows=[0, 2], dtype=str)
headers = pd.read_csv('2022MunicipalElectionAnonymousBallotMarking.csv', nrows=2)


df = df.dropna()
for col in df.columns[3:]:
    df[col] = df[col].astype(int)

    
candidates = {}
for candidate in df.columns[3:-6]: 
    n, name = candidate.split(' ', 1)
    candidates[n] = name
    candidates[name] = n

df.columns = ['Vote Type', 'Poll', 'Ballot Type'] + list(candidates)[::2] + ['1Y', '1N', '2Y', '2N', '3Y', '3N']



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
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_radio_buttons("Mayor", "Mayoral Vote", MayoralCandidates)
        ),
        ui.panel_main(
            ui.output_plot("plot"),
            ui.output_plot("plot2")
        )
    ),

)


def server(input, output, session):
    @output
    @render.plot
    def plot(): 
        df_mayor = df[df[candidates[input.Mayor()]]==1]
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.subplot(121)
        df_mayor['Council'].hist(ax=ax1, bins=11, density=True, align='mid')
        plt.title('Number of Council Votes')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.subplot(122)
        df_mayor['Park'].hist(ax=ax2, bins=7, density=True, align='mid')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.title('Number of Park Board Votes')
        #ax.set_axisbelow(True)
        #ax.grid(color='gray', linestyle='dashed')
        return fig
    
    @output
    @render.plot
    def plot2(): 
        df_mayor = df[df[candidates[input.Mayor()]]==1]
        fig, ax = plt.subplots()
        data = df_mayor.loc[:,'100':'158'].sum().sort_values(ascending=False)[0:15]/df_mayor.shape[0]
        data = data.sort_values(ascending=True)
        data.index = data.index.map(lambda x: candidates[x])
        data.plot.barh(ax=ax)
        plt.title('Council Votes')
        #ax.set_axisbelow(True)
        #ax.grid(color='gray', linestyle='dashed')
        return fig

app = App(app_ui, server)
