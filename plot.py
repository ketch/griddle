r"""
griddle.plot: plotting time-series data on structured grids.
"""
import matplotlib.pyplot as plt
from clawpack import pyclaw

def write_plots(plot_spec):
    r"""
    Write image files to disk.  Multiple figures are written to different
    subdirectories.
    """
    path = './_plots/'
    import os
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(len(plot_spec[0]['data'])):
        plot_objects = plot_frame(plot_spec,i)

        figures = _get_figures(plot_objects)
        for figure in figures:
            subdir = 'fig%s/' % str(figure.number)
            if not os.path.exists(path+subdir):
                os.mkdir(path+subdir)
            filename = 'frame%s.png' % str(i).zfill(4)
            figure.savefig(path+subdir+filename)

def plot_frame(plot_spec,frame_num=0):
    r"""
    Plot a list of items, specified in plot_spec, using `frame[frame_num]`.
    """
    assert _valid_plot_spec(plot_spec)

    # Fill in default values of None
    for item in plot_spec:
        for attr in ['plot_obj','axes']:
            item[attr] = item.get(attr)
        if not item.has_key('plotargs'):
            item['plotargs'] = {}
        if item['axes'] is not None:
            item['axes'].cla()

    all_plot_objects = []

    for item in plot_spec:
        # Add data field if necessary
        if not item.has_key('data'):
            item['data'] = [None]*_get_num_data_files(item['data_path'])

        gridded_data = item['data'][frame_num]

        # Load data from file if necessary
        if gridded_data is None:
            gridded_data = pyclaw.Solution(frame_num,path=item['data_path'])


        plot_objects = plot_item(gridded_data, \
                              item['field'],item['plot_obj'], \
                              item['axes'],**item['plotargs'])
        #item['plot_obj'] = plot_obj
        item['axes'] = plot_objects[0].axes
        all_plot_objects.append(plot_objects)

    return all_plot_objects


def plot_item(gridded_data,field,plot_objects=None,axes=None,**plotargs):
    r"""
    Plot a single item (typically one field of one gridded_data) on a specified
    axis.  If plot_obj is specified, it simply updates the data on that object.
    Note that this will not cause the plot to refresh.

    Inputs:
        - gridded_data : a PyClaw Solution object
        - field : an integer or a function.  If an integer, plot
            state.q[i,...] for each state in gridded_data.states.  If a
            function, it should accept a state as an argument and return a
            computed field.

    Returns the handle to the plot object (e.g., line).
    """
    num_dim = gridded_data.state.num_dim

    if plot_objects is None:
        plot_objects = [None]*len(gridded_data.states)

    patch_values = []
    for state in gridded_data.states:
        if type(field) is int:
            q = state.q[field,...]
        elif hasattr(field, '__call__'):
            q = field(state)
        else:
            raise Exception('Unrecognized field argument in plot_item: ', field)
        patch_values.append(q)


    if num_dim == 1:
        plot_type = 'line'
    elif num_dim == 2:
        plot_type = 'pcolor'
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
            plot_objects[i] = axes.plot(xc,q,**plotargs)[0]
        elif plot_type == 'pcolor':
            xe, ye = state.grid.p_edges
            plot_objects[i] = axes.pcolormesh(xe, ye, q, vmin=zmin, vmax=zmax, shading='flat')
            axes.axis('image')

    return plot_objects


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
    import os

    if not os.path.exists(plot_path):
        raise Exception('plot_path does not exist: %s' % plot_path)

    settings = _DEFAULT_CONFIG
    settings['source'] = plot_path
    settings['index_in_url'] = True
    settings['use_orig'] = True
    settings['title'] = 'Plots'
    gal = Gallery(settings)
    gal.build()
    print 'Open your browser to ./_build/index.html'


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

def _get_num_data_files(path,file_string='fort.q'):
    r"""Count the number of output files in directory specified by path."""
    import os
    files = os.listdir(path)
    data_files = [file_string in filename for filename in files]
    return data_files.count(True)
