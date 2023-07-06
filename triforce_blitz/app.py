from shiny import ui, render, App
import pickle
from matplotlib import pyplot as plt
from collections import Counter
import numpy as np
import pandas as pd

with open('Triforce_data.pkl', 'rb') as file: 
    dict_data = pickle.load(file)
class Seed: 
    def __init__(self, **entries): 
        self.__dict__.update(entries)
seed_data = [Seed(**seed) for seed in dict_data]


app_ui = ui.page_fluid(
    ui.h2("Summary statistics on Triforce Blitz"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_radio_buttons("Dungeon", "Triforce Location", seed_data[0].dungeons)
        ),
        ui.panel_main(
            ui.output_plot("plot")
        )
    ),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("steps", "Steps", 0, 30, value=(0, 30), step=1)
        ),
        ui.panel_main(
            ui.output_plot("plot2")
        )
    ),
    ui.output_plot("plot3")
    
)

def server(input, output, session):
    @output
    @render.plot
    def plot(): 
        list_seeds = [triforce[0] for file in seed_data for triforce in file.zipped if triforce[1].__contains__(input.Dungeon())]
        n_paths = len(list_seeds)
        
        path_items = [items for path in list_seeds for items in path]
        counted_items = Counter(path_items)
        counted_items = dict(sorted(counted_items.items(), key=lambda item: item[1])[-12:])
        
        fig, ax = plt.subplots()
        plt.barh(list(counted_items.keys()), np.fromiter(counted_items.values(),dtype=float)/n_paths)
        plt.title('How often does a Triforce in LOCATION require path ITEM?')
        plt.xlim([0, 1])
        ax.set_axisbelow(True)
        ax.grid(color='gray', linestyle='dashed')
        return fig
    
    @output
    @render.plot
    def plot2():
        list_seeds = [triforce for file in seed_data for triforce in file.zipped if len(triforce[0]) in list(range(input.steps()[0], input.steps()[1]+1))]
        n_paths = len(list_seeds)
        
        location = [triforce[1] for triforce in list_seeds]
        counted_locations = Counter(location)
        counted_locations = dict(sorted(counted_locations.items(), key=lambda item: item[1]))
        
        fig = plt.figure()
        ax = plt.GridSpec(1,2)
        
        ax1 = plt.subplot(ax[0,0])
        plt.barh(list(counted_locations.keys()), np.fromiter(counted_locations.values(),dtype=float)/n_paths)
        plt.title('How often does N-step Triforce appear in LOCATION')
        ax1.set_axisbelow(True)
        ax1.grid(color='gray', linestyle='dashed')
        

            
        
        
        path_items = [items for triforce in list_seeds for items in triforce[0]]
        counted_items = Counter(path_items)
        counted_items = dict(sorted(counted_items.items(), key=lambda item: item[1])[-12:])
        
        ax2 = plt.subplot(ax[0,1])
        plt.barh(list(counted_items.keys()), np.fromiter(counted_items.values(),dtype=float)/n_paths)
        plt.title('How often does N-step Triforce require path ITEM')
        plt.xlim([0, 1])
        ax2.set_axisbelow(True)
        ax2.grid(color='gray', linestyle='dashed')
    
    @output
    @render.plot
    def plot3():       
        list_seeds = [[len(triforce[0]), triforce[1]] for file in seed_data for triforce in file.zipped]
        step_seeds = [[seed for seed in list_seeds if seed[0] == i] for i in range(30)]
        counted_seeds = [dict(Counter([seed[1] for seed in count])) for count in step_seeds]
        df = pd.DataFrame(counted_seeds).fillna(0)
        df = df.div(df.sum(axis=1), axis=0)
        df = df.reindex(sorted(df.columns, key=lambda location: seed_data[0].dungeons.index(location)), axis=1)
        colors = ['#9debb1', '#fa899a', '#a6ecff', '#3e422c', '#25e81e', '#ed111f', '#0722f0', 
                  '#8f13e8', '#e39b27', '#18ede6', '#d3adff', '#fffb00']
        
        ax = df.plot.bar(stacked = True, color=colors)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc='center left',bbox_to_anchor=(1.0, 0.5));
        plt.title('Location of Triforce by path count')
        return ax
    
app = App(app_ui, server)
