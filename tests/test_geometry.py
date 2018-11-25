import griddle
import unittest

# ===================================
# Setup functions
def set_up_patch():
    x = griddle.Dimension(0.,1.,100)
    g = griddle.geometry.Patch(x)
    return g

# ===================================

# ===================================
# Test functions
class test_patch_properties(unittest.TestCase):
    def test_basics(self):
        g = set_up_patch()
        assert g.lower_global == [0.0]
        assert g.upper_global == [1.0]
        assert g.num_cells_global == [100]
        assert len(g.dimensions) == 1
        assert g.delta == [0.01]
        g2 = g.__deepcopy__()
        print(g)

    def test_cant_add_same_dim(self):
        x = griddle.Dimension(0.,1.,100)
        g = griddle.geometry.Patch(x)
        with self.assertRaises(Exception):
            g.add_dimension(x)
# ===================================
