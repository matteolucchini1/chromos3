# Master Project - Scripts for working with RXTE-data
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

from subscripts.download_data import *
from subscripts.locate_files import *
from subscripts.determine_info import *
from subscripts.spacecraft_filters import *
from subscripts.goodxenon_to_fits import *
from subscripts.pcu_filters import *
from subscripts.create_backgrounds import *
from subscripts.find_channels import *
from subscripts.extract_lc_and_sp import *

# Run setup_xray first
# Do not deviate from this order in pipeline, as the subscripts all depend on
# each other to have run in a particular order.

#download()
#locate_files()
#determine_info()
#spacecraft_filters()
#goodxenon_to_fits()
#pcu_filters()
#create_backgrounds()
#find_channels()
extract_lc_and_sp()
