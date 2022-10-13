# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # tsgettoolbox and tstoolbox - Python Programming Interface
# ## 'tsgettoolbox nwis ...': Download data from the National Water Information System (NWIS)
# This notebook is to illustrate the Python API usage for 'tsgettoolbox' to download and work with data from the National Water Information System (NWIS).  There is a different notebook to do the same things from the command line called tsgettoolbox-nwis-cli.  The CLI version of tsgettoolbox can be used from other languages that have the ability to make a system call.

# %%
# %matplotlib inline
from tsgettoolbox import tsgettoolbox

# %% [markdown]
# Let's say that I want flow (parameterCd=00060) for site '02325000'.  All of the tsgettoolbox functions create a _pandas_ DataFrame.

# %%
df = tsgettoolbox.nwis_dv(sites="02325000", startDT="2000-01-01", parameterCd="00060")

# %%
df.head()  # The .head() function gives the first 5 values of the time-series

# %% [markdown]
# ## 'tstoolbox ...': Process data using 'tstoolbox'
# Now lets use "tstoolbox" to plot the time-series.  The 'input_ts' option is used to read in the time-series from the DataFrame.

# %%
from tstoolbox import tstoolbox

# %%
tstoolbox.plot(input_ts=df, ofilename="plot_api.png")

# %% [markdown]
# ![](plot_api.png)

# %% [markdown]
# 'tstoolbox plot' has many options that can be used to modify the plot.

# %%
tstoolbox.plot(
    input_ts=df,
    ofilename="flow_api.png",
    ytitle="Flow (cfs)",
    title="02325000: FENHOLLOWAY RIVER NEAR PERRY, FLA",
    legend=False,
)

# %% [markdown]
# ![](flow_api.png)

# %%
mdf = tstoolbox.aggregate(input_ts=df, agg_interval="M", statistic="mean")

# %%
tstoolbox.plot(input_ts=mdf, drawstyle="steps-pre", ofilename="flow_api_monthly.png")

# %% [markdown]
# ![](flow_api_monthly.png)

# %%
