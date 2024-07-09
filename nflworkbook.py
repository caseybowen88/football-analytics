#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 22:20:00 2024

@author: caseybowen
"""

#%%
import pandas as pd
import plotly.graph_objects as go
import nfl_data_py as nfl
## Import the data from the 2021 season
pbp_py = nfl.import_pbp_data([2021])
## filter to non-null pass plays
filter_crit = 'play_type == "pass" & air_yards.notnull()'
## group by passer id and passer and aggregate to find mean air yards and number of passes thrown
pbp_py_p = (pbp_py.query(filter_crit).groupby(['passer_id', 'passer']).agg({'air_yards': ['count', 'mean']}))
## Collapse columns to make data easier to read
pbp_py_p.columns = list(map("_".join, pbp_py_p.columns.values))
## Create sort crit for qbs that have thrown > 100 passes
sort_crit = "air_yards_count > 100"
## Print out new data frame
print(
      pbp_py_p.query(sort_crit)\
          .sort_values(by = 'air_yards_mean', ascending = False)\
              .to_string())
#%%
import numpy as np
seasons = range(2016, 2022 +1)
pbp_py = nfl.import_pbp_data(seasons)
##Filtering out null values of air yards on passing plays
pbp_py_p = \
    pbp_py\
        .query('play_type == "pass" & air_yards.notnull()')\
            .reset_index()
##Assigning 'long' to passing plays w/ air_yards >= 20 and short to all others    
pbp_py_p["pass_length_air_yards"] = np.where(
    pbp_py_p["air_yards"] >= 20, "long", "short")
##Assigning null values of passing_yards to 0
pbp_py_p["passing_yards"] = \
    np.where(
        pbp_py_p["passing_yards"].isnull(), 0, pbp_py_p["passing_yards"])
##Symmart of all passing plays
pbp_py_p["passing_yards"]\
    .describe()
##Summary of 'short' passing plays
pbp_py_p\
    .query('pass_length_air_yards == "short"')['passing_yards']\
        .describe()
##Summary of 'long' passing plays     
pbp_py_p\
    .query('pass_length_air_yards == "long"')['passing_yards']\
        .describe()
##Summary of EPA on short passing plays
pbp_py_p\
    .query('pass_length_air_yards == "short"')['epa']\
        .describe()
##Summary of epa on long passing plays
pbp_py_p\
    .query('pass_length_air_yards == "long"')['epa']\
        .describe()
#%%
import seaborn as sns
import matplotlib.pyplot as plt
## Bar Chart of passing yards gained on all passing plays in 2021
sns.displot(data = pbp_py, x = 'passing_yards')
plt.show()
## Setting style to whitegrid and palette to colorblind for easier reading
sns.set_theme(style = "whitegrid", palette = "colorblind")
## Creating subset of all short passing plays
pbp_py_p_short = \
    pbp_py_p\
        .query('pass_length_air_yards == "short"')
## Bar chart of all short passing plays in 2021
pbp_py_hist_short = \
    sns.displot(data = pbp_py_p_short,
                binwidth = 1,
                x = 'passing_yards');
pbp_py_hist_short\
        .set_axis_labels(
            "Yards gained (or lost) during a passing play", "Count"
            );
plt.show();

#%%
## Boxplot of short and long passing plays based on air yards
pass_boxplot =\
    sns.boxplot(data = pbp_py_p,
                x = 'pass_length_air_yards',
                y = 'passing_yards');
pass_boxplot.set(
    xlabel = 'Pass length (long >= 20 yards, short < 20 yards)',
    ylabel = 'Yards gained (or lost) during a passing play',
    );
plt.show();
#%%
epa_boxplot =\
    sns.boxplot(data = pbp_py_p,
                x = 'pass_length_air_yards',
                y = 'epa');
epa_boxplot.set(
    xlabel = 'Pass length (long >= 20 yards, short < 20 yards)',
    ylabel = 'EPA gained (or lost) during a passing play',
    );
plt.show();
#%%
## Group by passer_id, passer, and season then find mean passing yards per play.
pbp_py_p_s =\
    pbp_py_p\
        .groupby(["passer_id", "passer", "season"])\
            .agg({"passing_yards": ["mean", "count"]})
## Collapse columns to make data easier to read      
pbp_py_p_s.columns = list(map("_".join, pbp_py_p_s.columns.values))
## Rename mean and count columns to ypa and n
pbp_py_p_s \
    .rename(columns = {'passing_yards_mean' : 'ypa',
                       'passing_yards_count' : 'n'},
            inplace = True)
## Sort in descending order
pbp_py_p_s \
    .sort_values(by = ['ypa'], ascending = False)\
        .head()
## Filter out qb's with less than 100 attempts to account for explosive trick plays and small sample sizes.   
pbp_py_p_s_100 = \
    pbp_py_p_s\
        .query("n >= 100")\
            .sort_values(by = ['ypa'], ascending = False)

pbp_py_p_s_100.head()
#%%
pbp_py_p_s_pl = \
    pbp_py_p\
        .groupby(["passer_id", "passer", "season", "pass_length_air_yards"])\
            .agg({"passing_yards":["mean", "count"]})

pbp_py_p_s_pl.columns = \
    list(map("_".join, pbp_py_p_s_pl.columns.values))
pbp_py_p_s_pl\
    .rename(columns={'passing_yards_mean' : 'ypa',
                     'passing_yards_count' : 'n'},
            inplace = True)
    
pbp_py_p_s_pl.reset_index(inplace = True)

q_value = (
    '(n >= 100 &' +
    'pass_length_air_yards == "short") | ' +
    '(n >= 30 &' + 
    'pass_length_air_yards == "long")'
    )
pbp_py_p_s_pl = pbp_py_p_s_pl.query(q_value).reset_index()

cols_save =\
    ["passer_id", "passer", "season",
     "pass_length_air_yards", "ypa"]
air_yards_py = \
    pbp_py_p_s_pl[cols_save].copy()
    
air_yards_lag_py =\
    air_yards_py\
        .copy()
air_yards_lag_py["season"] += 1
air_yards_lag_py\
    .rename(columns={'ypa':'ypa_last'},
            inplace=True)
    
pbp_py_p_s_pl =\
    air_yards_py\
        .merge(air_yards_lag_py,
               how = 'inner',
               on = ['passer_id', 'passer',
                     'season', 'pass_length_air_yards'])
        
print(
      pbp_py_p_s_pl[["pass_length_air_yards", "passer",
                     "season", "ypa", "ypa_last"]]\
          .query('passer == "T.Brady"| passer == "A.Rodgers"')\
              .sort_values(["passer", "pass_length_air_yards", "season"])\
                  .to_string()
                  )

pbp_py_p_s_pl\
    .info()
    
len(pbp_py_p_s_pl.passer_id.unique())
#%%
sns.lmplot(data = pbp_py_p_s_pl,
           x = "ypa",
           y = "ypa_last",
           col = "pass_length_air_yards");
plt.show();

pbp_py_p_s_pl\
    .query("ypa.notnull() & ypa_last.notnull()")\
        .groupby("pass_length_air_yards")[["ypa", "ypa_last"]]\
            .corr()
#%%
pbp_py_p_s_pl\
    .query(
        'pass_length_air_yards =="long" & season == 2017'
        )[["passer_id", "passer", "ypa"]]\
        .sort_values(["ypa"], ascending = False)\
            .head(10)
            
pbp_py_p_s_pl\
    .query(
        'pass_length_air_yards =="long" & season == 2018'
        )[["passer_id", "passer", "ypa"]]\
        .sort_values(["ypa"], ascending = False)\
            .head(10)
#%%
##Histogram of EPA on passing plays
sns.displot(data = pbp_py,
            x = 'epa')
plt.show()

pbp_py_epa_hist_short =\
    sns.displot(data = pbp_py_p_short,
                binwidth = 1,
                x = 'epa')
pbp_py_epa_hist_short\
    .set_axis_labels(
        "EPA on a short passing play", "Count")
plt.show();
#%%
##Boxplot of epa on short vs long passing plays
epa_boxplot =\
    sns.boxplot(data = pbp_py_p,
                x = 'pass_length_air_yards',
                y = 'epa');
epa_boxplot.set(
    xlabel = 'Pass length (long >= 20 yards, short < 20 yards)',
    ylabel = 'EPA gained (or lost) during a passing play',
    );
plt.show();
#%%
## Stability analysis for epa rather than ypa from above.
pbp_py_p_s =\
    pbp_py_p\
        .groupby(["passer_id", "passer", "season"])\
            .agg({"epa": ["mean", "count"]})
## Collapse columns to make data easier to read      
pbp_py_p_s.columns = list(map("_".join, pbp_py_p_s.columns.values))
## Rename mean and count columns to ypa and n
pbp_py_p_s \
    .rename(columns = {'epa_mean' : 'mean_epa',
                       'epa_count' : 'n'},
            inplace = True)
## Sort in descending order
pbp_py_p_s \
    .sort_values(by = ['mean_epa'], ascending = False)\
        .head()
## Filter out qb's with less than 100 attempts to account for explosive trick plays and small sample sizes.   
pbp_py_p_s_100 = \
    pbp_py_p_s\
        .query("n >= 100")\
            .sort_values(by = ['mean_epa'], ascending = False)

pbp_py_p_s_100.head()
#%%
##EPA stability analysis continued, including lags from season before
pbp_py_p_s_pl = \
    pbp_py_p\
        .groupby(["passer_id", "passer", "season", "pass_length_air_yards"])\
            .agg({"epa":["mean", "count"]})

pbp_py_p_s_pl.columns = \
    list(map("_".join, pbp_py_p_s_pl.columns.values))
pbp_py_p_s_pl\
    .rename(columns={'epa_mean' : 'mean_epa',
                     'epa_count' : 'n'},
            inplace = True)
    
pbp_py_p_s_pl.reset_index(inplace = True)

q_value = (
    '(n >= 100 &' +
    'pass_length_air_yards == "short") | ' +
    '(n >= 30 &' + 
    'pass_length_air_yards == "long")'
    )
pbp_py_p_s_pl = pbp_py_p_s_pl.query(q_value).reset_index()

cols_save =\
    ["passer_id", "passer", "season",
     "pass_length_air_yards", "mean_epa"]
air_yards_py = \
    pbp_py_p_s_pl[cols_save].copy()
    
air_yards_lag_py =\
    air_yards_py\
        .copy()
air_yards_lag_py["season"] += 1
air_yards_lag_py\
    .rename(columns={'mean_epa':'mean_epa_last'},
            inplace=True)
    
pbp_py_p_s_pl =\
    air_yards_py\
        .merge(air_yards_lag_py,
               how = 'inner',
               on = ['passer_id', 'passer',
                     'season', 'pass_length_air_yards'])
        
print(
      pbp_py_p_s_pl[["pass_length_air_yards", "passer",
                     "season", "mean_epa", "mean_epa_last"]]\
          .query('passer == "T.Brady"| passer == "A.Rodgers"')\
              .sort_values(["passer", "pass_length_air_yards", "season"])\
                  .to_string()
                  )

pbp_py_p_s_pl\
    .info()
    
len(pbp_py_p_s_pl.passer_id.unique())
#%%
sns.lmplot(data = pbp_py_p_s_pl,
           x = "mean_epa",
           y = "mean_epa_last",
           col = "pass_length_air_yards");
plt.show();

pbp_py_p_s_pl\
    .query("mean_epa.notnull() & mean_epa_last.notnull()")\
        .groupby("pass_length_air_yards")[["mean_epa", "mean_epa_last"]]\
            .corr()
#%%
pbp_py_p_s_pl\
    .query(
        'pass_length_air_yards =="long" & season == 2017'
        )[["passer_id", "passer", "mean_epa"]]\
        .sort_values(["mean_epa"], ascending = False)\
            .head(10)
            
pbp_py_p_s_pl\
    .query(
        'pass_length_air_yards =="long" & season == 2018'
        )[["passer_id", "passer", "mean_epa"]]\
        .sort_values(["mean_epa"], ascending = False)\
            .head(10)
#%%
import pandas as pd
import numpy as np
import nfl_data_py as nfl
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
##Importing data
seasons = range(2016, 2022 + 1)
pbp_py = nfl.import_pbp_data(seasons)
## Filtering to non-null rushier_id rushing plays
pbp_py_run =\
    pbp_py.query('play_type == "run" & rusher_id.notnull()')\
        .reset_index()
## Setting null rushing_yards values to zero
pbp_py_run\
    .loc[pbp_py_run.rushing_yards.isnull(), "rushing_yards"] = 0
## Scaterplot of rushing_yards by yards to go
sns.set_theme(style = "whitegrid", palette = "colorblind")
sns.scatterplot(data = pbp_py_run,
                x = "ydstogo",
                y = "rushing_yards");
plt.show();
## Same scatterplot with a trend line to get a better feel for data (still jumbled together tho)
sns.regplot(data = pbp_py_run, x = "ydstogo", y = "rushing_yards");
plt.show();
#%%
## Mean rushing yards grouped by yards to go
pbp_py_run_ave = \
    pbp_py_run.groupby(["ydstogo"])\
        .agg({"rushing_yards":["mean"]})

pbp_py_run_ave.columns = \
    list(map("_".join, pbp_py_run_ave.columns))

pbp_py_run_ave\
    .reset_index(inplace = True)
## Scatterplot of average rushing_yards by yds to go with trend line and confidence interval
sns.regplot(data = pbp_py_run_ave, x="ydstogo", y="rushing_yards_mean");
plt.show();
#%%
## Simple linear regression of rushing_yards ~ ydstogo
yards_to_go_py = \
    smf.ols(formula = 'rushing_yards ~ 1 + ydstogo', data = pbp_py_run)

print(yards_to_go_py.fit().summary())
## Creating a ryoe (rushing yards over expected) column in our dataframe based on our really terrible model
pbp_py_run["ryoe"]=\
    yards_to_go_py \
        .fit()\
            .resid
#%%
## Aggregating mean and total ryoe by rusher to see who has performed the best in this metric since 2016
ryoe_py =\
    pbp_py_run\
        .groupby(["season", "rusher_id", "rusher"])\
            .agg({
                "ryoe":["count", "sum", "mean"],
                "rushing_yards":["mean"]})

ryoe_py.columns =\
    list(map("_".join, ryoe_py.columns))

ryoe_py.reset_index(inplace = True)
## Renaming columns and filtering out rushers with less than 50 carries in a season
ryoe_py =\
    ryoe_py\
        .rename(columns={
            "ryoe_count": "n",
            "ryoe_sum": "ryoe_total",
            "ryoe_mean": "ryoe_per",
            "rushing_yards_mean": "yards_per_carry",
            }
            ).query("n > 50")
print(ryoe_py.sort_values("ryoe_total", ascending = False))