import numpy as np
import pandas as pd

coins = ['REP','ICN','GNT','GNO','LUN','BAT','ADX','BNT','CFI','OMG','STORJ', 
         'DGD','EDG','1ST','HMQ','RLC','MLN','MYST','PTOY','SNGLS','PAY','TKN','ETH']
csv = '_USDT.csv'

included_dates = []
for month in [str(x) for x in range(7,12)]:
    if int(month) < 10:
        month = '0'+month
    for day in [str(x) for x in range(1,32)]:
        if int(day) < 10:
            day = '0'+day
        included_dates.append('2017-'+month+'-'+day)

coin_data = {}
for coin in coins:
    x = pd.read_csv(coin+csv)
    coin_data[coin] = x.loc[x['timeDate'].isin(included_dates)]
    (length, _) = coin_data[coin].shape
    coin_data[coin].index = range(length)

def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
        
    return pd.DataFrame(series_dict)

combined_coin_data = merge_dfs_on_column(list(coin_data.values()), list(coin_data.keys()), 'close')

import plotly.offline as py
import plotly.graph_objs as go
#import plotly.figure_factory as ff
py.init_notebook_mode(connected=True)

def df_scatter(df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
    '''Generate a scatter plot of the entire dataframe'''
    label_arr = list(df)
    series_arr = list(map(lambda col: df[col], label_arr))
    
    layout = go.Layout(
        title=title,
        legend=dict(orientation="h"),
        xaxis=dict(type='date'),
        yaxis=dict(
            title=y_axis_label,
            showticklabels= not seperate_y_axis,
            type=scale
        )
    )
    
    y_axis_config = dict(
        overlaying='y',
        showticklabels=False,
        type=scale )
    
    visibility = 'visible'
    if initial_hide:
        visibility = 'legendonly'
        
    # Form Trace For Each Series
    trace_arr = []
    for index, series in enumerate(series_arr):
        trace = go.Scatter(
            x=series.index, 
            y=series, 
            name=label_arr[index],
            visible=visibility
        )
        
        # Add seperate axis for the series
        if seperate_y_axis:
            trace['yaxis'] = 'y{}'.format(index + 1)
            layout['yaxis{}'.format(index + 1)] = y_axis_config    
        trace_arr.append(trace)

    fig = go.Figure(data=trace_arr, layout=layout)
    py.iplot(fig)
    
coin_correlation = combined_coin_data.pct_change().corr(method='pearson')
ETH_correlation = {}
for coin in coins:
    ETH_correlation[coin] = coin_correlation[coin]['ETH'] 
ETH_correlation
combined_coin_data = combined_coin_data[sorted(ETH_correlation, key=ETH_correlation.get)]

coin_correlation = combined_coin_data.pct_change().corr(method='pearson')
coin_correlation.to_csv('ETH_coin_correlations.csv')

def correlation_heatmap(df, title, absolute_bounds=True):
    '''Plot a correlation heatmap for the entire dataframe'''
    heatmap = go.Heatmap(
        z=df.corr(method='pearson').as_matrix(),
        x=df.columns,
        y=df.columns,
        colorbar=dict(title='Pearson Coefficient'),
    )
    
    layout = go.Layout(title=title)
    
    if absolute_bounds:
        heatmap['zmax'] = 1.0
        heatmap['zmin'] = -1.0
        
    fig = go.Figure(data=[heatmap], layout=layout)
    py.iplot(fig)

correlation_heatmap(combined_coin_data.pct_change(), "Correlations of Ethereum Based Coins (Jul-Nov 2016) ")
