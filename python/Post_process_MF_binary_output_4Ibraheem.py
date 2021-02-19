# in python, spacing matters! If you indent script, it must correspond to an if 
# statement, or a for loop, for example.  Its annoying at first, but once you get
# used to it, it really helps keep the code organized

# Some helpful libraries
import os
import numpy as np
import flopy
import flopy.utils.binaryfile as bf
from matplotlib import pyplot as plt

out_pth = r'C:\Temp\ibraheem'
ccf_file = 'DSModel_09.ccf'
ccf_out = os.path.join(out_pth, ccf_file)

modobj = bf.CellBudgetFile(ccf_out)

modobj.list_unique_records()
modobj.get_unique_record_names()

# CONSTANT HEAD        2
# FLOW RIGHT FACE      1
# FLOW FRONT FACE      1
# FLOW LOWER FACE      1
# WELLS                5
# RIVER LEAKAGE        5
# STORAGE              1

# create a lookup array that holds the ID of each cell
cell_list = np.arange(0, 2*102*217)
cell_list_arr = cell_list.reshape((2, 102, 217))
# create a lookup dictionary
id_dict = {}
for val in cell_list:
    address = np.argwhere(cell_list_arr == val)[0]
    lay = address[0]
    row = address[1]
    col = address[2]
    id_dict.update({val: (lay, row, col)})  # will be 0-based


# Get a list of all the available stored output times
ckstpkper = modobj.get_kstpkper()

# Instantiate a list to store output in
rivflx = []

# Get data of a particular type from the binary output file
# loop over everytime step
for current_kstpkper in ckstpkper:
    riv_rawdat = modobj.get_data(kstpkper = current_kstpkper, text = '   RIVER LEAKAGE')
    
    # Convert the retrieved data to a numpy array for further processing
    riv_np = np.array(riv_rawdat)
    # really only need the first item of the first index, since there's only one
    riv_np = riv_np[0]
    
    # cycle through the indices
    riv_flx_step = np.zeros((2,102,217))
    for entry in riv_np:
        cellID = entry[0]
        flx = entry[1]
        lay, row, col = id_dict[cellID]
        riv_flx_step[lay, row, col] += flx
    
    rivflx.append(riv_flx_step)
    print('finished processing step: ' + str(current_kstpkper))

# Convert the 'appended' lists to numpy arrays
rivflx = np.array(rivflx)

# Note the shape of the the rivflx numpy array:
rivflx.shape
# (292, 2, 102, 217)  # time steps, lay, row, col

# Now you can do all kinds of powerful (and fast) analyses:
# If you want to see the mean riv flux as a 2D array (so 'flattened' over the rows
# and columns, you could do:
rivflx_2D_all_time = rivflx[:,:,:,:].sum(axis=1).mean(axis=0)
rivflx_2D_all_time
rivflx_2D_all_time.shape
# (102, 217)
    
# Or, to get all rivflx for the entire model during the entire simulation period:
rivflx.sum()
# -149439884.06629434  # keep in mind this is a net of positive and negative!


# The above values will be in total m^3.   Total rivflx in ac*ft is:
rivflx.sum() * 35.315 / 43560
# -121154.0290587967

# Also, you can focus the queries by providing ranges to sum over.
# The following sums up the rivflx for stress periods 11 through 20.
# A couple of notes about python, it is 0-based, so the 10 is 
# really an 11 if you convert back to 1-based, which is what MODFLOW
# is. Also, when providing a range in python it stops before the 
# end of the last number in the range.  Hence, "10:20" is 11:20
# because the 20 is really a 21, but python stops just before the
# last value given, so it stops at true time step 20. 
#
# Also, in regard to the indices related to space (lay, row, col)
# I'm requesting that it sum over layer 1 only (remember, the 0 is a 1
# in the 2nd position, and the ":" directs python to use all indices
# in the entire range.  Because I'm using two ":" in both the row
# and column positions, when I run the "sum" operation, I need to tell
# it which index I want to flatten the array over.  You can read
# more about this online.  But what follows is really nice because 
# it returns a 2D array that you could print to a txt file for 
# displaying in arc, or you could plot in python using matplotlib
lay1_total_rivflx_10days = rivflx[10:20, 0, :, :].sum(axis=0)

# So you can run operations on the data that was returned by the above:
lay1_total_rivflx_10days.sum()
# -172719.67539118743   # Remember a net value!

# and for grins, you could also do a quick plot in python:
rivflx_2D_all_time_plt = rivflx_2D_all_time.copy()
rivflx_2D_all_time_plt[rivflx_2D_all_time_plt == 0] = np.nan
plt.imshow(rivflx_2D_all_time_plt)
plt.show()



