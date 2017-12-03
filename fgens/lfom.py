"""This module can take an LFOM doc, and specify the number of holes per row

"""

import adsk
import cylindrical_pattern_feature
import sys, os
sys.path.append(os.path.abspath(os.path.join(__file__ ,"../..")))
import adsk_utilities as a_ut
import utilities as ut
import urllib.request

def start(hole_list, max_holes, feature_name_odd, feature_name_even, seed_name_odd, seed_name_even, fdoc):

    print('Beginning file download with urllib2...')
    url = 'http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'
    urllib.request.urlretrieve(url, '/Users/ethankeller/Downloads/cat.jpg')

    a_ut.open_template(ut.abs_path("archives/constant_head_tank.f3z"))
    # split the list into odd and even
    cylindrical_pattern_feature.start(hole_list[::2], max_holes, feature_name_odd, seed_name_odd, fdoc)
    cylindrical_pattern_feature.start(hole_list[1::2], max_holes, feature_name_even, seed_name_even, fdoc)
