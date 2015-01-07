r"""
Griddle: plotting time-series data on structured grids.
"""
import matplotlib.pyplot as plt

def valid_plot_spec(plot_spec):
    r"""Check that a plot_spec argument is valid.

    A plot_spec should be a list of dictionaries.
    """
    for item in plot_spec:
        if not type(item) is dict:
            raise Exception('Each plot_spec entry should be a dictionary.')
        if not item.has_key('data'):
            raise Exception('Data source not specified.')
        if not hasattr(item['data'],'__getitem__'):
            raise Exception('Data source should be a list.')
    return True

def get_figures(plot_objects):
    figures_with_dupes = [plot_object.figure for plot_object in plot_objects]
    figures = list(set(figures_with_dupes)) # Discard duplicates
    return figures

def write_plots(plot_spec):
    path = './_plots/'
    print path
    import os
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(len(plot_spec[0]['data'])):
        plot_objects = plot_frame(plot_spec,i)

        figures = get_figures(plot_objects)
        for figure in figures:
            filename = 'frame%sfig%s.png' % (str(i).zfill(4), str(figure.number))
            figure.savefig(path+filename)

def make_plot_gallery(plot_path='./_plots'):
    from sigal.gallery import Gallery
    from sigal.settings import _DEFAULT_CONFIG

    settings = _DEFAULT_CONFIG
    settings['source'] = plot_path
    settings['index_in_url'] = True
    settings['use_orig'] = True
    gal = Gallery(settings)
    gal.build()
    print 'Open your browser to ./_build/index.html'

def plot_frame(plot_spec,frame_num=0):
    r"""
    Plot a list of items.  Optionally, use a provided list of figures to place
    the plots on.
    """
    assert valid_plot_spec(plot_spec)

    # Fill in default values of None
    for item in plot_spec:
        for attr in ['plot_obj','axes']:
            item[attr] = item.get(attr)
        if not item.has_key('plotargs'):
            item['plotargs'] = {}

    plot_objects = []

    for item in plot_spec:
        gridded_data = item['data'][frame_num]
        plot_obj, = plot_item(gridded_data, \
                              item['field'],item['plot_obj'], \
                              item['axes'],**item['plotargs'])
        item['plot_obj'] = plot_obj
        plot_objects.append(plot_obj)

    return plot_objects


def plot_item(gridded_data,field,plot_obj=None,axes=None,**plotargs):
    r"""
    Plot a single item (typically one field of one gridded_data) on a specified
    axis.  If plot_obj is specified, it simply updates the data
    on that object.  Note that this will not cause the plot to refresh.

    Returns the handle to the plot object (e.g., line).

    In principle, field could be:
    - an index
    - a numpy array
    - a name (string) that lives in a dictionary that is part of gridded_data
    """
    x = gridded_data.grid.p_centers[0]
    if type(field) is int:
        q = gridded_data.state.q[field,...]
    elif hasattr(field, '__call__'):
        q = field(gridded_data)
    else:
        raise Exception('Unrecognized field argument in plot_item: ', field)

    if plot_obj is not None:
        plot_obj.set_data(x,q)

        # Rescale axes automatically
        plot_obj.axes.relim()
        plot_obj.axes.autoscale_view(True,True,True)

        return plot_obj,

    if axes is None:
        figure = plt.figure()
        axes = figure.add_subplot(111)

    if plotargs is not None:
        return axes.plot(x,q,**plotargs)
    else:
        return axes.plot(x,q)

