r"""
Griddle: plotting time-series data on structured grids.
"""
import matplotlib.pyplot as plt

def plot_frame(gridded_data,plot_spec):
    r"""
    Plot a list of items based on data in gridded_data.  Optionally, use a
    provided list of figures to place the plots on.
    """
    # Fill in default values of None
    for item in plot_spec:
        for attr in ['plot_obj','axes']:
            item[attr] = item.get(attr)
        if not item.has_key('plotargs'):
            item['plotargs'] = {}

    plot_objects = []

    for item in plot_spec:
        plot_obj, = \
                plot_item(gridded_data,item['field'],item['plot_obj'],item['axes'],**item['plotargs'])
        item['plot_obj'] = plot_obj
        plot_objects.append(plot_obj)

    #figures = [item['plot_obj'].figure for item in plot_items]
    #figures = list(set(figures)) # Discard duplicates

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

