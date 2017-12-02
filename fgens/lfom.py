"""This module can take an LFOM doc, and specify the number of holes per row

"""

import adsk
import cylindrical_pattern_feature
import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__ ,"../..")))
import adsk_utilities as a_ut
import utilities as ut

def start(hole_list, max_holes, feature_name_odd, feature_name_even, seed_name_odd, seed_name_even, fdoc):
    a_ut.open_template(ut.abs_path("archives/constant_head_tank.f3z"))
    # split the list into odd and even
    cylindrical_pattern_feature.start(hole_list[::2], max_holes, feature_name_odd, seed_name_odd, fdoc)
    cylindrical_pattern_feature.start(hole_list[1::2], max_holes, feature_name_even, seed_name_even, fdoc)
