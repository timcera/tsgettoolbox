# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .sh
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Bash
#     language: bash
#     name: bash
# ---

# %% [markdown]
# # tsgettoolbox and tstoolbox - Command Line Interface
# ## 'tsgettoolbox nwis ...': Download data from the National Water Information System (NWIS)
# This notebook is to illustrate the command line usage for 'tsgettoolbox' and 'tstoolbox' to download and work with data from the National Water Information System (NWIS).  There is a different notebook to do the same thing from within a Python program called tsgettoolbox-nwis-api.
#
# First off, always nice to remind myself about the options.  Each sub-command has their own options kept consistent with the options available from the source service.  The way that NWIS works is you have one major filter and one or more minor filters to define what sites you want.

# %%
tsgettoolbox nwis_dv --help

# %% [markdown]
# Let's say that I want flow (parameterCd=00060) for site '02325000'.  I first make sure that I am getting what I want by allowing the output to be printed to the screen.  Note the pipe ('|') that directs output to the 'head' command to display the top 10 lines of the time-series.

# %%
tsgettoolbox nwis_dv --sites 02325000 --startDT '2000-01-01' --parameterCd 00060 | head

# %% [markdown]
# Then I redirect to a file with "> filename.csv" so that I don't have to wait for the USGS NWIS services for the remaining work or analysis.

# %%
tsgettoolbox nwis_dv --sites 02325000 --startDT '2000-01-01' --parameterCd 00060 > 02325000_flow.csv

# %% [markdown]
# ## 'tstoolbox ...': Process data using 'tstoolbox'
# Now lets use "tstoolbox" to plot the time-series.  Note the redirection again, this time for input as "< filename.csv".  Default plot filename is "plot.png".

# %%
tstoolbox plot <02325000_flow.csv

# %% [markdown]
# ![title](plot.png)

# %% [markdown]
# 'tstoolbox plot' has many options that can be used to modify the plot.

# %%
tstoolbox plot --help

# %%
tstoolbox plot --ofilename flow.png --ytitle 'Flow (cfs)' --title '02325000: FENHOLLOWAY RIVER NEAR PERRY, FLA' --legend False <02325000_flow.csv

# %% [markdown]
# ![title](flow.png)

# %% [markdown]
# ## Monthly Average Flow
# You can also use tstoolbox to make calculations on the time-series, for example to aggregate to monthly average flow:

# %%
tstoolbox aggregate --groupby M --statistic mean <02325000_flow.csv | head

# %%
tstoolbox aggregate --groupby M --statistic mean <02325000_flow.csv | tstoolbox plot --ofilename plot_monthly.png --drawstyle steps-pre

# %% [markdown]
# ![title](plot_monthly.png)
