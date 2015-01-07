import griddle
import matplotlib
import matplotlib.pyplot as plt
from clawpack import pyclaw
import numpy as np

def set_up_solution():
    x = pyclaw.Dimension(0.,1.,100)
    g = pyclaw.geometry.Patch([x])
    s = pyclaw.State(g,num_eqn=2)
    d = pyclaw.Domain(g)
    xc, = g.grid.p_centers
    s.q[0,:] = np.sin(4*np.pi*xc)
    s.q[1,:] = np.exp(xc)
    sol = pyclaw.Solution(s,d)
    return sol

def run_clawpack():
    from clawpack.pyclaw import examples
    claw = examples.acoustics_1d_homogeneous.acoustics_1d.setup()
    claw = examples.acoustics_1d_homogeneous.acoustics_1d.setup()
    claw.run()
    return claw

def test_plot_item():
    sol = set_up_solution()
    line, = griddle.plot_item(sol,0)
    assert type(line) == matplotlib.lines.Line2D
    assert line.get_data()[0].shape == (100,)

def test_animation():
    claw = run_clawpack()
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)
    item1 = {'field' : 0,
             'axes' : ax1,
             'plotargs' : {'ls' : '--', 'color' : 'green'}}
    item2 = {'field' : 1, 'axes' : ax2}
    plotitems = [item1,item2]
    animation = griddle.ianimate(claw,plotitems)

def test_iplot():
    claw = run_clawpack()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot_spec = [{'field' : 0, 'axes' : ax1}]
    ip = griddle.Iplotsol(claw.frames,plot_spec)
