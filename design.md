# griddle.plot design decisions


## In-place plot updates versus generating new plot objects
The original plan was to always update plot objects in place, by
calling `line.set_data()`, `quad.set_array()`, etc.  This is not
possible for AMR plots since the number of patches changes from
one frame to the next.

So far, we have 3 major types of plots with conflicting requirements:
- Single-patch matplotlib plot: can pre-specify axes, update in-place.
- Multi-patch matplotlib plot: can pre-specify axes, but cannot update in-place
  since number and extent of plot objects varies from one frame to next
- yt plot: cannot pre-specify axes or figure, but can update in-place.
  In-place update is required for animation!

So, we must use in-place updates for yt, we could use it for single-patch, and
we can't use it for multi-patch.

Decision for now: for matplotlib we always clear the axes and generate new plot
objects, while for yt we always update in-place.

## yt data structures
When to convert from Solution to ds for yt plots?  Only inside plot_item, so
that we can assume we're dealing with Solutions almost everywhere.

## Loop over patches
Unlike in visclaw, this loop is at the lowest level, inside the loop over
items.  We can do this because the matplotlib argument `zorder` can be used
to avoid patch plots of different items covering each other.


# (woefully incomplete) list of things that need to be implemented

- [ ] plot subset of all frames
- [x] image comparison tests (using matplotlib's decorator)
- [x] test for fill_between
- [x] test for show_patch_boundaries
- [x] test for axis titles
- [ ] caching data across multiple items
- [ ] automatically get and use field names from Riemann
