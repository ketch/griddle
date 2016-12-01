"""
Module Iplot for interactive plotting.

For more instructions see the Usage notes in class Iplot below. 

For options during looping type:
  >>> ip = iplot()    # doctest: +SKIP
  >>> ip.plotloop()    # doctest: +SKIP
  IPLOT> help
"""

import cmd, os
import matplotlib
matplotlib.rc('text', usetex=False)
matplotlib.interactive(True)
import matplotlib.pyplot as plt
import griddle


class Iplot(cmd.Cmd):
    """
    Class for interactively stepping through plots.
    Takes a plot_spec as argument

    Usage:
    ------
    >>> from griddle.iplot import Iplot    # doctest: +SKIP
    >>> ip = Iplot(plot_spec)              # new instantiation    # doctest: +SKIP
    >>> ip.plotloop()             # to start looping    # doctest: +SKIP
    IPLOT > help                  # for list of available commands
    IPLOT > q                     # to quit looping and return to python
    >>> ip.plotloop()             # to restart looping at previous frame    # doctest: +SKIP

    Arguments:
    ----------
    - plot_spec is the only required arguments.

    Other (optional) arguments of Iplot rarely need to be changed:
        completekey='tab', stdin=None, stdout=None

    The optional argument 'completekey' is the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        not None and the readline module is available, command completion
        is done automatically. The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.

    """
    # initialization:
    # ---------------

    prompt = 'IPLOT > '
    lastcmd = 'n'             # initialize so <return> advances frame'

    def __init__(self, plot_spec,\
                 completekey='tab', stdin=None, stdout=None):
        """Instantiate a line-oriented interpreter framework."""

        import sys

        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin
        if stdout is not None:
            self.stdout = stdout
        else:
            self.stdout = sys.stdout
        self.cmdqueue = []
        self.completekey = completekey
 
        for item in plot_spec:
            griddle.plot._set_up_time_series(item)
        self.plot_spec = plot_spec

        self.restart = False
        self.prevframeno = 0

        self.frames = {}

    def plot_frame(self,frame):
        plot_objects = griddle.plot_frame(self.plot_spec,frame)
        figures = [obj[0].figure for obj in plot_objects]
        figures = list(set(figures)) # Discard duplicates
        for figure in figures:
            figure.canvas.draw()
 

    def preloop(self):
        print('\nInteractive plotting... ')
        print('Type ? at IPLOT prompt for list of commands')

        startframeno = raw_input('\n    Start at which frame [default=%i] ? '\
                                % self.prevframeno)

        makeplot = True 

        if startframeno == '':
            self.frameno = self.prevframeno
            if self.restart:
                replot = raw_input('    Replot data for frame %s [no] ? ' \
                                % self.frameno)

                if replot not in ('y','yes','Y'):
                    makeplot = False

                if makeplot:
                    reload = raw_input('    Reload data for frame %s [no] ? ' \
                                    % self.frameno)
                    if reload in ('y','yes','Y'):
                        self.frames.pop(str(self.frameno))
        else:
            try:
                self.frameno = int(startframeno)
            except ValueError:
                print('\n    *** Error: frameno must be an integer, resetting to 0')
                self.frameno = 0

        if makeplot:
            self.plot_frame(self.frameno)

        self.lastcmd = 'n'
        self.restart = True 

    # end of initialization 
    # ---------------------

    def postloop(self):
        self.prevframeno = self.frameno


    # Commands that can be typed at the IPLOT> prompt:
    # ---------------------------------------------------

    # help command:
    # -------------
    def help_help(self):
        print('print this list of valid commands\n')

    # next frame:
    # -----------
    def do_n(self, rest):
        self.frameno = self.frameno+1
        self.plot_frame(self.frameno)
    def help_n(self):
        print('n: advance to next frame\n')

    # previous frame:
    # ---------------
    def do_p(self, rest):
        self.frameno = max(self.frameno-1, 0)
        self.plot_frame(self.frameno)
    def help_p(self):
        print('p: go back to previous frame\n')

    # jump to arbitrary frame:
    # ------------------------
    def do_j(self, rest):
        try:
            newframeno = int(rest)
        except:
            newframeno = raw_input('\n    Jump to which frame? ')
        if newframeno == 'n': 
            self.do_n(rest)
            self.lastcmd = 'n'
        elif newframeno == 'p': 
            self.do_p(rest)
            self.lastcmd = 'p'
        else:
            try:
                newframeno = int(newframeno)
            except ValueError:
                print('\n    *** Error: frameno must be an integer, n, or p')
            self.frameno = newframeno
            self.plot_frame(self.frameno)
    def help_j(self):
        print('j N: jump to frame N\n')
        print('j:   jump to some other frame (will prompt for N)\n')

    # redraw frame:
    # -------------
    def do_r(self, rest):
        self.plot_frame(self.frameno)
    def help_r(self):
        print('r: redraw the current frame,  rr: reload and redraw\n')

    def do_rr(self, rest):
        try:
            self.frames.pop(str(self.frameno))
            print('Cleared data for frame ',self.frameno)
        except KeyError:
           print('No frame data to clear for frame ',self.frameno)
        self.plot_frame(self.frameno)
    def help_rr(self):
        print('r: redraw the current frame,  rr: reload and redraw\n')

    # clearframes
    # ---------
    def do_clearframes(self, rest):
        if rest=='':
            self.frames.clear()
            print('Cleared all frames')
        else:
            for framestr in rest.split():
                try:
                    frameno = int(framestr)
                except ValueError:
                    print('Error in clearframes: unrecognized input')
                popped_frame = self.frames.pop(str(frameno),None)
                if popped_frame is None:
                   print('No frame data to clear for frame ',frameno)
                else:
                   print('Cleared data for frame ',frameno)

    def help_clearframes(self):
        print('clearframes: delete frame data from cache to replot')
        print('    use if you have rerun the code and want to plot the')
        print('    latest results')
        print('          clearframes framenos  clears one or more frames')
        print('          clearframes           clears all frames')


    # save
    # ---------
    def do_save(self, rest):
        rest = rest.split()
        if len(rest)==2:
            try:
                figno = int(rest[0])
            except ValueError:
                print("*** Expected figure number, got: ",rest[0])
            fname = rest[1]
            plt.figure(figno)
            try:
                plt.savefig(fname)
                print("Saved figure number %s to file %s" % (figno,fname))
            except ValueError:
                print("Don't put quotes around the filename.")
        else:
            print("*** save requires two arguments: figno, fname")
            print("*** got: ",rest)

    def help_save(self):
        print('save figno fname: save figure figno to file fname using savefig.')


    # print working directory:
    # ------------------------
    def do_pwd(self, rest):
        print('  now in directory: ',os.getcwd())
        print('  data from outdir: ',self.plotdata.outdir)
    def help_pwd(self):
        print('pwd: print current working directory and outdir')
        print('     fort.* files in outdir provide frame data\n')


    # print figure to a file:
    # -----------------------
    def do_print(self, rest):
        fname = rest
        for figno in plt.get_fignums():
            if len(fname)>0:
                import string
                # doesn't work properly!
                plt.figure(figno)
                name = fname.split('.')[0]+string.zfill(figno,4)+'.'+fname.split('.')[1]
                plt.savefig(name)
            else:
                print('You must specify a file name.')

    def help_print(self):
        print('print: print all figures for this frame to files of the form')
        print('      frame000NfigJ.png')
        print('To print a single figure or with different style, try e.g.')
        print('     IPLOT > q')
        print('     figure(2)')
        print('     savefig("myname.jpg")\n')
        

    # use vi e.g. to edit setplot.py:
    # -------------------------------
    def do_vi(self, rest):
        exitcode = os.system('vi %s' % rest)
        if exitcode != 0:
            print('*** System vi command failed.  Try "help edit"')

    def help_vi(self):
        print('Edit file using vi, for example to change the plot parameters:')
        print('    IPLOT> vi setplot.py ')
        print('    IPLOT> resetplot ')
        print('See also "help edit" for use of other editors.\n')
        

    # edit a file using editor specified by environment variable EDITOR:
    # -----------------------------------------------------------------
    def do_edit(self, rest):
        try:
            editor = os.environ['EDITOR']
            eval("os.system('%s %s')" % (editor,rest))
        except:
            print('*** Environment variable EDITOR not set... ')
            print('*** Type "help edit" for more info')

    def help_edit(self):
        print('Edit file, for example to change the plot parameters:')
        print('    IPLOT> edit setplot.py ')
        print('    IPLOT> resetplot ')
        print('Specify the editor by setting environment variable EDITOR')
        print('  before starting Python shell.')
        print('If you want to use vi, see also "help vi".\n')

        
    # quit commands:
    # --------------
    def do_quit(self, rest):
        print('quitting...')
        return True
    def help_quit(self):
        print('q or quit: terminates the command loop\n')
        
    def do_q(self, rest):
        print('quitting...')
        return True
    def help_q(self):
        print('q or quit: terminates the command loop\n')
        
    def do_k(self, rest):
        print('quitting...')
        return True
    def help_k(self):
        print('k: terminates the command loop\n')
        
    def do_EOF(self, rest):
        print("quitting...")
        return True
    def help_EOF(self):
        print("Terminates the command loop\n")
        
    # alias plotloop = cmdloop:
    # -------------------------
    def plotloop(self):
        self.cmdloop()
