r"""
griddle.plot: plotting time-series data on multi-patch structured mapped grids.
"""
import matplotlib.pyplot as plt
from clawpack import pyclaw
import os
import numpy as np


def plot_frame(plot_spec,frame_num=0):
    r"""
    Plot a list of items, specified in plot_spec, using `frame[frame_num]`.

    Returns: `all_plot_objects`, a list of lists of plot objects.
    `all_plot_objects[i][j]` is a handle to the plot object for item
    `plot_spec[i]` on patch j.
    """
    assert _valid_plot_spec(plot_spec)

    # Sanitize items and prepare for plotting
    for item in plot_spec:
        # Add data field if necessary; this only happens once for a time series
        if not item.has_key('data'):
            item['data_format'] = item.get('data_format')
            if item['data_format'] is None:
                item['data_format'] = _get_data_format(item['data_path'])
            item['data'] = [None]*_get_num_data_files(item['data_path'],item['data_format'])

        # Load data from file if necessary
        if item['data'][frame_num] is None:
            item['data'][frame_num] = pyclaw.Solution(frame_num, \
                                          path=item['data_path'],
                                          file_format=item['data_format'])

        _set_plot_item_defaults(item,frame_num)
        if 'yt' not in item['plot_type']:
            _clear_axes(item)

    all_plot_objects = []


    # Now do the actual plots
    for item in plot_spec:

        plot_objects = plot_item(item,frame_num)

        item['plot_objects'] = plot_objects
        if 'yt' in item['plot_type']:
            item['axes'] = plot_objects[0].plots[item['field']].axes
        else:
            item['axes'] = plot_objects[0].axes
        item['axes'].set(**item['axis_settings'])
        _set_axis_title(item,frame_num)
        item['axes'].figure.set_tight_layout(True)

        if item['plot_type'] in ['pcolor'] and not item.has_key('colorbar'):
            item['colorbar'] = item['axes'].figure.colorbar(plot_objects[0])

        all_plot_objects.append(plot_objects)

    return all_plot_objects


def plot_item(item,frame_num):
    r"""
    Plot a single item (typically one field of one gridded_data) on a specified
    axes.

    Inputs:
        - gridded_data : a PyClaw Solution object or a yt dataset
        - field : an integer or a function.  If an integer, plot
            state.q[i,...] for each state in gridded_data.states.  If a
            function, it should accept a state as an argument and return a
            computed field.

    Returns a list of handles to the plot objects (e.g., line) on each patch.
    """
    gridded_data = item['data'][frame_num]
    field = item['field']
    plot_type = item['plot_type']
    axes = item.get('axes')
    plot_objects = item.get('plot_objects')
    plot_args = item.get('plot_args',{})

    if 'yt' in plot_type:
        # For yt plots, convert to yt.dataset
        ds = _solution_to_yt_ds(gridded_data)
        if plot_objects is None: # yt plots are always a single object
            plot_objects = [None]
    else:
        # For matplotlib plots, replace instead of updating in-place
        plot_objects = [None]*len(gridded_data.states)

    # ===============
    # yt plotting
    # ===============
    if plot_type == 'yt_slice':
        import yt
        if plot_objects[0] is None:
            slc = yt.SlicePlot(ds, fields=field, **plot_args)
            slc.set_log(field,False);
            #return [slc.plots.values()[0]]
            return [slc]
        else:
            plot_objects[0]._switch_ds(ds)
            return plot_objects

    # ===============
    # non-yt plotting
    # ===============
    patch_values = []
    for state in gridded_data.states:
        q = _get_patch_values(state,field)
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
            xe, ye = state.grid.p_edges
            plot_objects[i] = axes.pcolormesh(xe, ye, q, vmin=zmin, vmax=zmax, \
                                              shading='flat', **plot_args)
            if item.get('show_patch_boundaries'):
                axes.plot(xe[0,:],ye[0,:],'-k',lw=2,zorder=100)
                axes.plot(xe[-1,:],ye[-1,:],'-k',lw=2,zorder=100)
                axes.plot(xe[:,0],ye[:,0],'-k',lw=2,zorder=100)
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
    for i in range(len(plot_spec[0]['data'])):
        plot_objects = plot_frame(plot_spec,i)

        figures = _get_figures(plot_objects)
        for figure in figures:
            items = _get_figure_items(plot_spec,figure)
            try:
                subdir = '_'.join(item['name'] for item in items)+'/'
            except KeyError:
                subdir = 'fig%s/' % str(figure.number)
            if not os.path.exists(path+subdir):
                os.mkdir(path+subdir)
            filename = 'frame%s.%s' % (str(i).zfill(4), file_format)
            figure.savefig(path+subdir+filename)

def _get_figure_items(plot_spec,figure):
    items = []
    for item in plot_spec:
        if item['axes'].figure == figure:
            items.append(item)
    return items


def animate(plot_spec):
    """
    Create an animation widget in an IPython notebook.
    Note that only the figure corresponding to the first item
    in plot_spec will be animated; the rest will be ignored.

    plot_spec[i]['data'] may be:

        - a list of Solution objects
        - a controller possessing a list of Solution objects
    """
    from matplotlib import animation
    from clawpack.visclaw.JSAnimation import IPython_display

    plot_objects = plot_frame(plot_spec)
    if plot_spec[0]['plot_type'] == 'yt_slice':
        fig = plot_objects[0][0].plots['Density'].figure
    else:
        fig = plot_objects[0][0].figure

    def fplot(frame_number):
        plot_objects = plot_frame(plot_spec,frame_number)
        return plot_objects[0]

    return animation.FuncAnimation(fig, fplot, frames=len(plot_spec[0]['data']))


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
    print 'Open your browser to ./_build/index.html'


def _get_patch_values(state,field):
    if hasattr(field, '__getitem__'):
        return [_get_field_values(state,f) for f in field]
    else:
        return _get_field_values(state,field)

def _get_field_values(state,field):
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
    figures = list(set(figures_with_dupes)) # Discard duplicates
    return figures


def _valid_plot_spec(plot_spec):
    r"""Check that a plot_spec argument is valid.

    A plot_spec should be a list of dictionaries.
    """
    for item in plot_spec:
        if not type(item) is dict:
            raise Exception('Each plot_spec entry should be a dictionary.')
        if not item.has_key('data_path'):
            if not item.has_key('data'):
                raise Exception('Data source not specified.')
            if not hasattr(item['data'],'__getitem__'):
                raise Exception('Data source should be a list or relative path string.')
    return True

def _get_num_data_files(path,file_format):
    r"""Count the number of output files of type file_format in directory
        specified by path.
    """
    files = os.listdir(path)
    file_string = file_substrings[file_format]
    data_files = [file_string in filename for filename in files]
    return data_files.count(True)

def _get_data_format(path):
    r"""Figure out which file format to read.

        Check which of the known file types are present in directory specified
        by `path`.  If multiple types are present, ask user which to use.
    """
    files = os.listdir(path)
    file_types_present = []
    for file_type, string in file_substrings.iteritems():
        if any([string in filename for filename in files]):
            file_types_present.append(file_type)

    if len(file_types_present)==1:
        return file_types_present[0]
    else:
        return raw_input("""Multiple file types are present in the specified
                        data directory.  Which do you wish to use?
                        """+file_types_present)

def _set_plot_item_defaults(item,frame_num):
    r"""Choose reasonable defaults for required options that are not specified.
    """
    if not item.has_key('plot_type'):
        num_dim = item['data'][frame_num].state.num_dim
        if num_dim == 1:
            item['plot_type'] = 'line'
        elif num_dim == 2:
            item['plot_type'] = 'pcolor'
        elif num_dim == 3:
            item['plot_type'] = 'yt_slice'

    # Fill in default values of None to avoid KeyErrors later
    for attr in ['plot_objects','axes']:
        item[attr] = item.get(attr)
    if not item.has_key('plot_args'):
        item['plot_args'] = {}
    if not item.has_key('axis_settings'):
        item['axis_settings'] = {}


def _clear_axes(item):
        # Clear old items from plot axes
        # This doesn't work correctly:
        #if item['plot_objects'] is not None:
        #    for plot_object in item['plot_objects']:
        #        plot_object.remove()
        #        del plot_object
        if item['axes'] is not None:
            item['axes'].cla()

def _set_axis_title(item,frame_num):
    if item.has_key('name'):
        title = '%s at t = %s' % (str(item['name']),item['data'][frame_num].t)
    else:
        title = 'Field %s at t = %s' % (str(item['field']),item['data'][frame_num].t)
    item['axes'].set_title(title)

def _solution_to_yt_ds(sol):
    r"""Convert pyclaw.Solution to yt.dataset."""
    import yt
    grid_data = []

    for state in sorted(sol.states, key = lambda a: a.patch.level):
        patch = state.patch

        d = {
            'left_edge': patch.lower_global,
            'right_edge': patch.upper_global,
            'level': patch.level,
            'dimensions': patch.num_cells_global,
            'Density': state.q[0,...],
            'x-momentum' : state.q[1,:,:,:],
            'y-momentum' : state.q[2,:,:,:],
            'z-momentum' : state.q[3,:,:,:],
            'Energy'     : state.q[4,:,:,:]
            }
        grid_data.append(d)
        bbox = np.vstack((sol.patch.lower_global,sol.patch.upper_global)).T;
    return yt.load_amr_grids(grid_data, sol.patch.num_cells_global, bbox = bbox)


file_substrings = { #should be 'extensions'
        'ascii' : 'fort.q',
        'hdf5'  : 'hdf',
        'petsc' : 'ptc'
        }
