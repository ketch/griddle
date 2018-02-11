r"""
griddle.plot: plotting time-series data on multi-patch structured mapped grids.
"""
import matplotlib.pyplot as plt
import os
import numpy as np
import griddle

def plot_frame(plot_spec,frame_num=0):
    r"""
    Plot a list of items, specified in plot_spec, using `frame[frame_num]`.

    Returns: `all_plot_objects`, a list of lists of plot objects.
    `all_plot_objects[i][j]` is a handle to the plot object for plot_item
    `plot_spec[i]` on patch j.
    """

    # Sanitize items and prepare for plotting
    # Most of this should happen somewhere else
    # probably in PlotItem.__init__().
    for plot_item in plot_spec:
        _set_up_time_series(plot_item)
        _set_plot_item_defaults(plot_item)
        assert _valid_plot_item(plot_item)
        if 'yt' not in plot_item['plot_type']:
            _clear_item_axes(plot_item)

    all_plot_objects = []

    # Now do the actual plots
    for plot_item in plot_spec:

        plot_objects = plot_item_frame(plot_item,frame_num)

        plot_item['plot_objects'] = plot_objects

        if 'yt' in plot_item['plot_type']:
            plot_item['axes'] = plot_objects[0].plots[plot_item['field']].axes
        else:
            plot_item['axes'] = plot_objects[0].axes

        plot_item['axes'].set(**plot_item['axis_settings'])
        _set_axis_title(plot_item,frame_num)
        plot_item['axes'].figure.set_tight_layout(True)

        if (plot_item['plot_type'] in ['pcolor']) and not ('colorbar' in plot_item):
            plot_item['colorbar'] = plot_item['axes'].figure.colorbar(plot_objects[0])

        all_plot_objects.append(plot_objects)

    return all_plot_objects


def plot_item_frame(plot_item,frame_num):
    r"""
    Plot a single plot_item (typically one field of one gridded_data) on a specified
    axes.

    Inputs:
        - plot_item : a plot_spec plot_item
        - frame num : an integer

    Returns a list of handles to the plot objects (e.g., line) on each patch.
    """
    gridded_data = plot_item['frames'][str(frame_num)]
    field = plot_item['field']
    plot_type = plot_item['plot_type']
    axes = plot_item.get('axes')
    plot_objects = plot_item.get('plot_objects')
    plot_args = plot_item.get('plot_args',{})

    if 'yt' in plot_type:
        # For yt plots, convert to yt.dataset
        ds = _solution_to_yt_ds(gridded_data)
        if plot_objects is None:  # yt plots are always a single object
            plot_objects = [None]
    else:
        # For matplotlib plots, replace plot objects instead of updating in-place
        plot_objects = [None]*len(gridded_data.states)

    # =======================================
    # yt plotting - AMR patches handled by yt
    # =======================================
    if plot_type == 'yt_slice':
        import yt
        if plot_objects[0] is None:
            slice_plot = yt.SlicePlot(ds, fields=field, **plot_args)
            slice_plot.set_log(field,False)
            # return [slice_plot.plots.values()[0]]
            return [slice_plot]
        else:
            # If the plot object already exists, just change the data source
            plot_objects[0]._switch_ds(ds)
            return plot_objects

    # ==========================================
    # non-yt plotting - AMR patches handled here
    # ==========================================
    patch_values = []
    for state in gridded_data.states:
        q = _get_field_values_on_all_patches(state,field)
        patch_values.append(q)

    if plot_type == 'pcolor':
        # Get color range
        zmin = min([v.min() for v in patch_values])
        zmax = max([v.max() for v in patch_values])

    if axes is None:
        figure = plt.figure()
        axes = figure.add_subplot(111)

    for i,state in enumerate(gridded_data.states):
        centers = state.grid.p_centers
        q = patch_values[i]

        if plot_type == 'line':
            xc = centers[0]
            plot_objects[i] = axes.plot(xc,q,**plot_args)[0]
        elif plot_type == 'fill_between':
            xc = centers[0]
            plot_objects[i] = axes.fill_between(xc,q[0],q[1],**plot_args)
        elif plot_type == 'pcolor':
            xe, ye = state.grid.p_nodes
            plot_objects[i] = axes.pcolormesh(xe, ye, q, vmin=zmin,
                                              vmax=zmax, shading='flat',
                                              zorder=state.patch.level,
                                              **plot_args)
            if plot_item.get('show_patch_boundaries'):
                axes.plot(xe[0, :],ye[0, :],'-k',lw=2,zorder=100)
                axes.plot(xe[-1,:],ye[-1,:],'-k',lw=2,zorder=100)
                axes.plot(xe[:, 0],ye[:, 0],'-k',lw=2,zorder=100)
                axes.plot(xe[:,-1],ye[:,-1],'-k',lw=2,zorder=100)

            axes.axis('image')

    return plot_objects

def write_plots(plot_spec,path='./_plots/',file_format='png'):
    r"""
    Write image files to disk.  Multiple figures are written to different
    subdirectories.
    """
    if path[-1] != '/': path = path + '/'
    if not os.path.exists(path):
        os.mkdir(path)
    # This assumes all items have the same number of frames:
    for plot_item in plot_spec:
        _set_up_time_series(plot_item)
    for frame_num in plot_spec[0]['frames'].list_frames:
        plot_objects = plot_frame(plot_spec,frame_num)

        figures = _get_figures(plot_objects)
        for figure in figures:
            items = _get_figure_items(plot_spec,figure)
            try:
                subdir = '_'.join(plot_item['name'] for plot_item in items)+'/'
            except KeyError:
                subdir = 'fig%s/' % str(figure.number)
            if not os.path.exists(path+subdir):
                os.mkdir(path+subdir)
            filename = 'frame%s.%s' % (str(frame_num).zfill(4), file_format)
            figure.savefig(path+subdir+filename)


def _set_up_time_series(plot_item,refresh=True):
    r"""Take a plot_item and set the 'frames' key based on either
        'data' or 'data_path'.
    """
    if refresh or not plot_item.get('frames'):
        if plot_item.get('data'):
            plot_item['frames'] = griddle.data.TimeSeries(plot_item['data'])
        else:
            plot_item['frames'] = \
                griddle.data.TimeSeries(plot_item['data_path'],
                                        file_format=plot_item.get('data_format'))


def _get_figure_items(plot_spec,figure):
    r"""
    Take a list of items and a figure, and return the items that belong
    to that figure.
    """
    items = []
    for plot_item in plot_spec:
        if plot_item['axes'].figure == figure:
            items.append(plot_item)
    return items


def animate(plot_spec):
    """
    Create an animation widget in an IPython notebook.
    Note that only the figure corresponding to the first plot_item
    in plot_spec will be animated; the rest will be ignored.

    plot_spec[i]['data'] may be:

        - a list of Solution objects
        - a controller possessing a list of Solution objects
    """
    from matplotlib import animation
    from clawpack.visclaw.JSAnimation import IPython_display

    # Sanitize items and prepare for plotting
    # This should happen somewhere else
    # probably in PlotItem.__init__().
    for plot_item in plot_spec:
        _set_up_time_series(plot_item)
        _set_plot_item_defaults(plot_item)
        assert _valid_plot_item(plot_item)

    plot_objects = plot_frame(plot_spec)
    if plot_spec[0]['plot_type'] == 'yt_slice':
        fig = plot_objects[0][0].plots['Density'].figure
    else:
        fig = plot_objects[0][0].figure

    def fplot(frame_number):
        plot_objects = plot_frame(plot_spec,frame_number)
        return plot_objects[0]

    return animation.FuncAnimation(fig, fplot, frames=len(plot_spec[0]['frames'].list_frames))


def make_plot_gallery(plot_path='./_plots'):
    """
    Make a pretty static HTML gallery of plots.  A sub-gallery is created for
    each subdirectory of `plot_path`.
    """
    from sigal.gallery import Gallery
    from sigal.settings import _DEFAULT_CONFIG

    if not os.path.exists(plot_path):
        raise Exception('plot_path does not exist: %s' % plot_path)

    settings = _DEFAULT_CONFIG
    settings['source'] = plot_path
    settings['theme'] = 'colorbox'
    settings['index_in_url'] = True
    settings['use_orig'] = True
    settings['title'] = 'Plots'
    settings['links'] = [('griddle on Github', 'http://github.com/ketch/griddle'),
                         ('Clawpack', 'http://clawpack.github.io')]
    gal = Gallery(settings)
    gal.build()
    print('Open your browser to ./_build/index.html')


def _get_field_values_on_all_patches(state,field):
    r"""This is just a wrapper around _get_field_values.  It iterates
        over multiple fields if field is a list.
    """
    if hasattr(field, '__getitem__'):
        return [_get_field_values(state,f) for f in field]
    else:
        return _get_field_values(state,field)

def _get_field_values(state,field):
    r"""
    Inputs:
        state : a pyclaw.State object
        field : either an integer or a function.
                If an integer, then return state.q[field,...].
                If a function, then return field(state).
    """
    if type(field) is int:
        q = state.q[field,...]
    elif hasattr(field, '__call__'):
        q = field(state)
    else:
        raise Exception('Unrecognized field argument in plot_item: ', field)
    return q

def _get_figures(plot_object_list_list):
    """
    Given a list of lists of `plot_objects`, return a list of figures containing them
    (without duplicates).
    """
    figures_with_dupes = []
    for plot_object_list in plot_object_list_list:
        figures_with_dupes.extend([plot_object.figure for plot_object in plot_object_list])
    figures = list(set(figures_with_dupes))  # Discard duplicates
    return figures


def _valid_plot_item(plot_item):
    r"""Check that a plot_item is valid.

    A plot_item should be a dictionary.
    """
    if not type(plot_item) is dict:
        raise Exception('Each plot_spec entry should be a dictionary.')
    if 'data_path' not in plot_item:
        if 'data' not in plot_item:
            raise Exception('For each plot_item, you must specify either \
                             "data" or "data path".')
        if not hasattr(plot_item['data'],'__getitem__'):
            raise Exception('Data source should be a list or relative path string.')
    if 'field' not in plot_item:
        raise Exception('A field must be specified for each plot_item.')
    if 'plot_type' not in plot_item:
        raise Exception('A plot_type must be specified for each plot_item.')
    return True

def _set_plot_item_defaults(plot_item):
    r"""Choose reasonable defaults for required options that are not specified.
    """
    if 'plot_type' not in plot_item:
        num_dim = plot_item['frames'][0].state.num_dim
        if num_dim == 1:
            plot_item['plot_type'] = 'line'
        elif num_dim == 2:
            plot_item['plot_type'] = 'pcolor'
        elif num_dim == 3:
            plot_item['plot_type'] = 'yt_slice'

    # Fill in default values of None to avoid KeyErrors later
    for attr in ['plot_objects','axes']:
        plot_item[attr] = plot_item.get(attr)
    if 'plot_args' not in plot_item:
        plot_item['plot_args'] = {}
    if 'axis_settings' not in plot_item:
        plot_item['axis_settings'] = {}


def _clear_item_axes(plot_item):
        # Clear old items from plot axes
        if plot_item['axes'] is not None:
            plot_item['axes'].cla()
        # The code below doesn't work correctly:
        # if plot_item['plot_objects'] is not None:
        #    for plot_object in plot_item['plot_objects']:
        #        plot_object.remove()
        #        del plot_object


def _set_axis_title(plot_item,frame_num):
    if 'name' in plot_item:
        title = '%s at t = %s' % (str(plot_item['name']),plot_item['frames'][frame_num].t)
    else:
        title = 'Field %s at t = %s' % (str(plot_item['field']),plot_item['frames'][frame_num].t)
    plot_item['axes'].set_title(title)

def _solution_to_yt_ds(sol):
    r"""Convert pyclaw.Solution to yt.dataset."""
    import yt
    grid_data = []

    for state in sorted(sol.states, key=lambda a: a.patch.level):
        patch = state.patch

        d = {
            'left_edge': patch.lower_global,
            'right_edge': patch.upper_global,
            'level': patch.level,
            'dimensions': patch.num_cells_global,
            'Density': state.q[0,...],
            'x-momentum': state.q[1,:,:,:],
            'y-momentum': state.q[2,:,:,:],
            'z-momentum': state.q[3,:,:,:],
            'Energy': state.q[4,:,:,:]
        }
        grid_data.append(d)
        bbox = np.vstack((sol.patch.lower_global,sol.patch.upper_global)).T
    return yt.load_amr_grids(grid_data, sol.patch.num_cells_global, bbox=bbox)
