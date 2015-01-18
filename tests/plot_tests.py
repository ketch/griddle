import matplotlib
import griddle
import matplotlib.pyplot as plt
from clawpack import pyclaw
import numpy as np
from matplotlib.testing.decorators import image_comparison
from nose import SkipTest


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
@image_comparison(baseline_images=['item'],extensions=['png'])
def test_plot_item():
    fig  = plt.figure(figsize=(8,6),dpi=100)
    ax   = fig.add_subplot(111)
    sol  = set_up_solution()
    item = {'frames' : griddle.data.TimeSeries([sol]),
            'axes' : ax,
            'field' : 0,
            'plot_type' : 'line'}
    line, = griddle.plot_item(item,0)
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
             'plot_args' : {'ls' : '--', 'color' : 'green'}}
    item2 = {'data' : claw.frames, 'field' : 1, 'axes' : ax2}
    plotitems = [item1,item2]
    animation = griddle.animate(plotitems)

def test_iplot():
    claw = run_pyclaw_1d()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot_spec = [{'data' : claw.frames, 'field' : 0, 'axes' : ax1}]
    ip = griddle.Iplot(plot_spec)

def test_gallery():
    claw = run_pyclaw_1d()
    fig1 = plt.figure()
    fig2 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax2 = fig2.add_subplot(111)
    item1 = {'data' : claw.frames,
             'field' : 0,
             'axes' : ax1,
             'plot_args' : {'ls' : '--', 'color' : 'green'}}
    item2 = {'data' : claw.frames,
             'field' : 1,
             'axes' : ax2}
    plot_spec = [item1, item2]
    griddle.write_plots(plot_spec)
    griddle.make_plot_gallery()

@image_comparison(baseline_images=['pcolor'],extensions=['png'])
def test_pcolor():
    claw = run_pyclaw_2d()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot_spec = [{'data' : claw.frames,
                  'axes' : ax,
                  'field' : 0}]
    plot_object = griddle.plot_frame(plot_spec)
    assert type(plot_object[0][0]) is matplotlib.collections.QuadMesh

@image_comparison(baseline_images=['sill'],extensions=['png'])
def test_fill_between():
    r"""Also tests derived quantities."""
    def bathymetry(state):
        return state.aux[0,...]

    def surface(state):
        return state.aux[0,...] + state.q[0,...]

    def bottom(state):
        return state.aux[0,...]*0.-1.

    from clawpack.pyclaw import examples
    claw = examples.sill.setup()
    claw.verbosity = 0
    claw.run()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    water = {'data' : claw.frames,
             'field' : (bathymetry,surface),
             'name' : 'depth',
             'axes' : ax,
             'plot_type' : 'fill_between'}
    land = {'data' : claw.frames,
             'field' : (bathymetry, bottom),
             'name' : 'bathy',
             'axes' : ax,
             'plot_type' : 'fill_between',
             'plot_args' : {'color' : 'brown',
                            'edgecolor' : 'k'}}
    griddle.animate([water,land])

def test_read_data():
    pass

@image_comparison(baseline_images=['amr'],extensions=['pdf'])
def test_amr_plotting():
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111)
    item5 = {'data_path' : './test_data/_amrclaw_2d_acoustics/',
             'field' : 0,
             'show_patch_boundaries' : True,
             'axes' : ax}
    plot_spec = [item5]
    plot_objects = griddle.plot_frame(plot_spec,frame_num=5);
    assert len(plot_objects[0]) == 20
    assert type(plot_objects[0][0]) is matplotlib.collections.QuadMesh

def test_yt_slice_plot():
    try:
        import yt
    except:
        raise SkipTest("yt import failed; skipping yt test.")
    plot_spec = [{'data_path' : './test_data/_pyclaw_3d_shocktube',
                  'field' : 'Density',
                  'plot_args' : {'normal' : 'z',
                                'origin'  : "native",
                                'center' : [1., 0.25, 0.]}}]
    plot_objects = griddle.plot_frame(plot_spec)
    assert type(plot_objects[0][0]) is yt.visualization.plot_window.AxisAlignedSlicePlot
# ===================================
