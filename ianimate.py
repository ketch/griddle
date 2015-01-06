"""
Interactive animations in IPython notebooks using matplotlib and JSAnimation.
"""


def ianimate(solutions,plot_items,ivar=0,varname=None,**kargs):
    """
        solutions may be:

            - a list of Solution objects
            - a controller possessing a list of Solution objects
    """
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from clawpack.visclaw.JSAnimation import IPython_display
    from clawpack import pyclaw
    import numpy as np
    import structviz

    if isinstance(solutions,pyclaw.Controller):
        solutions = solutions.frames

    frame = solutions[0]
    plot_items = structviz.plot_frame(frame,plot_items)
    fig = plot_items[0]['plot_obj'].figure

    def fplot(frame_number):
        frame = solutions[frame_number]
        structviz.plot_frame(frame,plot_items)
        return plot_items[0]['plot_obj']

    return animation.FuncAnimation(fig, fplot, frames=len(solutions))
