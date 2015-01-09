import griddle
import matplotlib
import matplotlib.pyplot as plt
from clawpack import pyclaw
import numpy as np

# ===================================
# Setup functions
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

def run_pyclaw_1d():
    from clawpack.pyclaw import examples
    claw = examples.acoustics_1d_homogeneous.acoustics_1d.setup()
    claw.run()
    return claw

def run_pyclaw_2d():
    from clawpack.pyclaw import examples
    claw = examples.radial_dam_break.setup()
    claw.run()
    return claw
# ===================================

# ===================================
# Test functions
def test_plot_item():
    sol = set_up_solution()
    line, = griddle.plot_item(sol,0,'line')
    assert type(line) == matplotlib.lines.Line2D
    assert line.get_data()[0].shape == (100,)

def test_animation():
    claw = run_pyclaw_1d()
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)
    item1 = {'data' : claw.frames,
             'field' : 0,
             'axes' : ax1,
             'plotargs' : {'ls' : '--', 'color' : 'green'}}
    item2 = {'data' : claw.frames, 'field' : 1, 'axes' : ax2}
    plotitems = [item1,item2]
    animation = griddle.animate(plotitems)

def test_iplot():
    claw = run_pyclaw_1d()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot_spec = [{'data' : claw.frames, 'field' : 0, 'axes' : ax1}]
    ip = griddle.Iplotsol(claw.frames,plot_spec)

def test_gallery():
    claw = run_pyclaw_1d()
    fig1 = plt.figure()
    fig2 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax2 = fig2.add_subplot(111)
    item1 = {'data' : claw.frames,
             'field' : 0,
             'axes' : ax1,
             'plotargs' : {'ls' : '--', 'color' : 'green'}}
    item2 = {'data' : claw.frames,
             'field' : 1,
             'axes' : ax2}
    plot_spec = [item1, item2]
    griddle.write_plots(plot_spec)
    griddle.make_plot_gallery()

def test_pcolor():
    claw = run_pyclaw_2d()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot_spec = [{'data' : claw.frames,
                  'field' : 0}]
    plot_object = griddle.plot_frame(plot_spec)
    assert type(plot_object[0][0]) is matplotlib.collections.QuadMesh

def test_read_data():
    pass

def test_amr_plotting():
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    item5 = {'data_path' : './test_data/_amrclaw_2d_acoustics/',
             'field' : 0,
             'axes' : ax}
    plot_spec = [item5]
    plot_objects = griddle.plot_frame(plot_spec,frame_num=5);
    assert len(plot_objects[0]) == 20
    assert type(plot_objects[0][0]) is matplotlib.collections.QuadMesh

def test_yt_slice_plot():
    import yt.visualization
    plot_spec = [{'data_path' : './test_data/_pyclaw_3d_shocktube',
                  'field' : 'Density',
                  'plotargs' : {'normal' : 'z',
                                'origin'  : "native",
                                'center' : [1., 0.25, 0.]}}]
    plot_objects = griddle.plot_frame(plot_spec)
    assert type(plot_objects[0][0]) is yt.visualization.plot_window.AxisAlignedSlicePlot
# ===================================
