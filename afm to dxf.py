# Short script to export afm scan lines as individual dxf files
# which can the be used to create 3d models using CAD
#%%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import ezdxf
from ezdxf import units

#%%
# This imports afm data from a txt file (can be changed)
# in gwyddion go to file --> save as, and select the ASCII data matrix file type
# (remember to type .txt in the filename when saving)

filepath = 'C:\\Users\\lukas\\Documents\\uniproject2\\test\\' #<-- enter file location
filename = 'Seyma_ALD_5_5nm0002 - Kopie.txt' #<--- enter file name

afm_array = pd.read_csv(filepath + filename,sep=None,engine='python') 
afm_array = pd.DataFrame.to_numpy(afm_array)

#fix 0
afm_array = afm_array - np.min(afm_array)

#normalising
afm_max = np.max(afm_array) # heighest point in image for normalising
# (The max value may need to be adjusted manually if there are anomalies in the data)
afm_array = afm_array/np.max(afm_array)

#clipping incase there were anomalies above
afm_array = np.clip(afm_array,0,1)

#%%
# Plotting the image for reference

fig = plt.figure()
im = plt.imshow(afm_array, cmap='afmhot')
fig.colorbar(im,label='Height')
plt.show()

#%%
# Loop to export each scan line and put them on a separate layer in a dxf file

# Setting how many scan lines to extract (will be evenly spaced across image)
num_lines = 120 #<--- input number of lines here
line_list = np.linspace(0,len(afm_array[0,:])-1,num_lines).astype(int)

#parameters for the loop
width = 780 #mm <--- set physical width of model here
depth = 100 #mm <--- set physical height/depth of model here

# for the desired model dimensions you need to consider
# (num_lines x line thickness) x width (x depth)
# where the line thickness is thickness of the material you will use

#setting up file
filename_dxf = 'scanlines_{}.dxf'.format(filename[0:filename.find('.')])
doc = ezdxf.new('R2010')  # Use AutoCAD 2010 format
doc.units = units.MM  # set units (millimeters)
msp = doc.modelspace()

#loop
for i in line_list:

    #getting and smoothing the line
    scanline = afm_array[:,i] 
    smoothed_scanline = savgol_filter(scanline, 10, 3) # smotthing the scanline slightly with a Savitzky-Golay filter
   
    #setting up points in mm with the scanline
    x_mm = np.linspace(0,width,len(scanline))
    y_mm = smoothed_scanline*depth 
    points = []

    for idx, x in enumerate(x_mm):
        points.append((x,y_mm[idx]))
   
    #adding layer
    doc.layers.add(name='line_{}'.format(i))

    #adding line 
    msp.add_lwpolyline(points,dxfattribs={"layer": 'line_{}'.format(i)})
    
#saving
doc.saveas(filename_dxf)
print(f"DXF file saved as: {filename_dxf}")

    

#%%
#plotting how the afm image looks after smoothing (just for fun)

smooth_afm = []
smooth_factor = 10
poly = 3

for l in afm_array:
    sml = savgol_filter(l, smooth_factor, poly)
    smooth_afm.append(sml)



fig = plt.figure()
im = plt.imshow(smooth_afm, cmap='afmhot')
fig.colorbar(im,label='Height')
plt.show()