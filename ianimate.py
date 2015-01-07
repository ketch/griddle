"""
Interactive animations in IPython notebooks using matplotlib and JSAnimation.
"""


def ianimate(gridded_data_series,plot_spec,ivar=0,varname=None,**kargs):
    """
        gridded_data_series may be:

            - a list of Solution objects
            - a controller possessing a list of Solution objects
    """
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from clawpack.visclaw.JSAnimation import IPython_display
    from clawpack import pyclaw
    import numpy as np
    import griddle

    if isinstance(gridded_data_series,pyclaw.Controller):
        gridded_data_series = gridded_data_series.frames

    frame = gridded_data_series[0]
    plot_objects = griddle.plot_frame(frame,plot_spec)
    fig = plot_objects[0].figure

    def fplot(frame_number):
        frame = gridded_data_series[frame_number]
        griddle.plot_frame(frame,plot_spec)
        return plot_objects[0]

    return animation.FuncAnimation(fig, fplot, frames=len(gridded_data_series))
