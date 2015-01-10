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
of data fields, on collections of mapped, structured grids.  
It is largely an adaptation of `clawpack.visclaw`.

### Griddle.plot usage
For examples, see [this IPython notebook](http://nbviewer.ipython.org/09bb72bf82043942e648).

The main output functionalities are:

- Plot figures on screen or in the notebook.  To plot a particular frame:

    `griddle.plot_frame(plot_spec, frame_num)`
    
- Plot an animation in the IPython notebook:

    `griddle.animate(plot_spec)`

- Write image files to disk

    `griddle.write_plots(plot_spec,path='./_plots/',file_format='png')`

- Launch an interactive plotting command loop:

```
    ip = griddle.Iplotsol(plot_spec)
    ip.plotloop()
```

- Web galleries of plots (using sigal):

    `griddle.make_plot_gallery(plot_spec)`

### `plot_spec`

The user must provide a `plot_spec`, which is a list of Python dictionaries.
For examples, see `griddle/test.py`.

#### Required keys

Each dict must specify the **data to be plotted** in one of the following ways:

- `plot_spec[i]['data']` : a list of `Solution` objects
- `plot_spec[i]['data_path']` : a directory containing Solution files

Each item must specify **which values to plot** in one of the following ways:

- `plot_spec[i]['field'] = j` where `j` is the index of the field (an integer)
- `plot_spec[i]['field'] = fun` where `fun` is a function that takes a State as
    argument and returns the computed field.

Each item must specify the **type of plot** to be made, via the key
`plot_type`.  The following plot types are currently supported:

- 1D data:
    - 'line' : line or scatter plot for 1D data
    - 'fill_between'
- 2D data:
    - 'pcolor'
- 3D data:
    - 'yt_slice' : a yt.SlicePlot

#### Optional keys
Other properties may be specified for each item in `plot_spec`:

- 'name' : a name for the item, to be used in the axis title and file directory
  name.
- 'axes' : a matplotlib axes object on which to place the item
- 'plot_args' : a dictionary of additional arguments to be passed to
  the plotting function.  For instance, for line plots one may pass
  'linestyle', 'linewidth', 'marker', etc.
- 'axis_settings' : these will be applied to the axes object on which the
  item is plotted.
- 'show_patch_boundaries' : to outline patch boundaries on pcolor plots of AMR
  data.


### Differences between griddle.plot and visclaw
Some of the key differences are:

- visclaw uses a hierarchical plot specification: figures->axes->items, whereas
  griddle uses a flat list of items, each of which can be associated with a
  particular set of axes by the user
- griddle currently allows plotting with yt as well as matplotlib
