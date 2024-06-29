# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # topoWX
# This downloads topoWX data using tsgettoolbox

# %%
from tsgettoolbox import tsgettoolbox as tsget

# %%
help(tsget.topowx_daily)

# %% [markdown]
# ## Monthly data
# This is a sample code to download daily data

# %%
topowx = tsget.topowx(lat=30, lon=-100, start_date="2014-01-01", end_date="2015-02-01")

# %%
topowx

# %% [markdown]
# ## Daily data
# This is a sample code to download daily data

# %%
topowx_daily = tsget.topowx_daily(
    lat=30, lon=-100, start_date="2014-01-01", end_date="2015-02-01"
)

# %%
topowx_daily
