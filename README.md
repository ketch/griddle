# Griddle project scope

Griddle deals with data fields on collections of mapped, structured grids.  It enables reading, writing, and plotting of such data, including time series.  It interfaces to:

- data structures: numpy and petsc4py (and in the future, pyboxlib)
- file formats: ASCII text, hdf5
- plotting tools: matplotlib, IPython notebook, yt

The main data structure is a Solution.

## Griddle.geometry

## Griddle.data/solution

## Griddle.plot project scope

`Griddle.plot` facilitates plotting of data fields, and especially time series
of data fields, on collections of mapped, structured grids.  The main output
functionalities are:

- figures on screen or in the notebook
- image files to disk
- animations in the IPython notebook
- an interactive plotting command loop
- web galleries of plots

The user must provide a `plot_spec`, which is a list of Python dictionaries.
Each dict must specify a dataset (a list of `Solution` objects, or a path to a
directory containing Solution files), as well as what and how to plot from that
dataset.
