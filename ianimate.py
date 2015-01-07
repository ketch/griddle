"""
Interactive animations in IPython notebooks using matplotlib and JSAnimation.
"""


def ianimate(plot_spec):
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

    plot_objects = griddle.plot_frame(plot_spec)
    fig = plot_objects[0].figure

    def fplot(frame_number):
        plot_objects = griddle.plot_frame(plot_spec,frame_number)
        return plot_objects[0]

    return animation.FuncAnimation(fig, fplot, frames=len(plot_spec[0]['data']))
