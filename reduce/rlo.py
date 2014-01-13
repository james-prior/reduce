#!/usr/bin/env python


#"Copyright 2009 Bryan Harris"
# COpyright 2011 James Prior
#
#This file is part of Reduce.
#
#    Reduce is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Reduce is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Reduce.  If not, see <http://www.gnu.org/licenses/>.
#

import tempfile
import shutil
import os
import time
import sys

import numpy
import getopt

from dataFile import *
from reducePlot import *
from measurementFile import *
from tee import *
from xlrd import *

'''
Reduces and plots a load-only time-stoke-load thisDataFile
Input should be tab delimited data with the first two lines 
containing column names and units respectively.
'''
zero_load=10
if __name__ != '__main__':
    print >>sys.stderr, 'ERROR: The', __name__, 
    print >>sys.stderr, 'module is meant to be run only as the main module.  '
    sys.exit(os.EX_USAGE)

def usage():
    print >>sys.stderr, "%s [-h] [--help]"% sys.argv[0]

opts=None

try:
    opts, args=getopt.gnu_getopt(sys.argv[1:],'hn:t:g:',('help', 'passes=', 'threshold=' ,'gage='))
    passes = -1
    threshold = .5
    Gage_Length_in = 0
    for o, a in opts:
        if o in ('-n','--passes'):
            passes=int(a)
        elif o in ('-h', '--help'):
            raise getopt.GetoptError("")
        elif o in ('-t','--threshold'):
            threshold=float(a)
        elif o in ('-g','--gage'):
            Gage_Length_in = float(a)
except getopt.GetoptError, info:
    print info
    usage()
    exit()

# where am I?
base_path = os.getcwd() 

# Here I am.
print "base_path: " + base_path 

# Where to put reduced data
reduce_path=os.path.join(base_path,"reduced")  
print "reduce_path: " + reduce_path  

# Where to put pretty pictures
image_path=os.path.join(reduce_path,"png") 
print "image_path: " + image_path

# Where to generate measurement files
log_file_name = "script.log"
log_file_path = os.path.join(base_path,log_file_name)
measurement_file_present=False 
meas_file_name = "measurements.csv"  
meas_file_path = os.path.join(base_path,meas_file_name)
print "meas_file_path: " + meas_file_path
summary_file_path = os.path.join(base_path,"summary.dat")
print "summary_file_path: " + summary_file_path
working_files=[]
measurement_file_names=[]
measurement_files=[]

# Create the directories. 
for directory in [reduce_path, image_path]:
    if False:
        print 'Path is %s' % directory

    # Create directory if needed. 
    if not os.access(directory, os.R_OK):
        try:
            os.mkdir(directory) 
        except:
            print >>sys.stderr, ('ERROR: Could not create %s directory. '
                % directory)
            sys.exit(os.EX_USAGE)
        else:
            print directory + ' created'

    # Test for ability to write to directory. 
    if not os.access(directory, os.W_OK):
        print >>sys.stderr, ('ERROR: Could not write to the %s directory.' 
            % directory)
        sys.exit(os.EX_USAGE)

# move the text files into a working directory and make lists of data files and measurement files
os.chdir(reduce_path)
for somefilename in os.listdir(base_path) :
    sourcefile = os.path.join(base_path,somefilename)
    destfile = os.path.join(reduce_path,somefilename)
    if somefilename.endswith(".txt") or somefilename.endswith(".TXT") :

        shutil.copyfile(sourcefile, destfile)
        working_files.append(destfile)
    if somefilename.endswith(".xls") or somefilename.endswith(".XLS") :

        shutil.copyfile(sourcefile, destfile)
        measurement_file_names.append(destfile)
        
# Remove the second header line so the script doesn't choke
temp = tempfile.mktemp()
for foo in working_files :
    shutil.move(foo, temp)
    file1 = open(foo, 'w')
    file2 = open(temp, 'rU')
    i=1
    for line in file2.readlines():
        if i!=2 : file1.write(line)
        i += 1
    file1.close()
    file2.close()
if (os.access(temp, os.W_OK)) : os.remove(temp)

# go into the working file directory and create the summary file

os.chdir(reduce_path)
summary_file=open(summary_file_path, 'w');
summary_file.write('Specimen\tRate\tPeak Load')
log_file=open(log_file_path, 'w');
t=Tee([sys.stdout, log_file])

#Start looking at the data files

print >>t, time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.localtime())
print >>t, 'user:', os.times()[0], 's'
print >>t, 'system:', os.times()[1], ' s' 

print >>t, 'Measurement Files:'

for meas_file_name in measurement_file_names :
    print >>t, meas_file_name
    measurement_files.append(measFile(meas_file_name))
    
    
for foo in working_files :

    #get the name of the next file

    foo_name=os.path.basename(foo)
    print >>t, 'Analyzing:', foo_name
    
    

    #plot the raw data and move the picture into out pictures directory

    thisDataFile=dataFile_SL(foo_name)
    if Gage_Length_in != 0 : thisDataFile.Gage_Length_in = Gage_Length_in
    
    for mfn in measurement_files :
        for specimen in mfn.specimens :
            #print specimen
            if foo_name.find(specimen.stl_ID) != -1:
                print foo_name, "appears to have a measurement file entry:"
                print specimen
                thisDataFile.Has_Measurement_File = True
                thisDataFile.Thickness_in = specimen.thick
                thisDataFile.Width_in = specimen.width
                thisDataFile.Specimen_ID = "STL " + str(specimen.stl_ID)

                thisDataFile.CS_Area_in2 = specimen.area
    
    picturename = plot_time_disp_load(thisDataFile,'-raw',0,1,0.1,1)
    shutil.move(picturename,os.path.join(image_path,picturename))


    picturename = plot_time_disp_load(thisDataFile,'_zerocheck',0,1,0.1,0.1)
    shutil.move(picturename,os.path.join(image_path,picturename))        
    
    thisDataFile.traces[thisDataFile.TIME].setLabel("Time [sec]")
    thisDataFile.traces[thisDataFile.STROKE].setLabel("Stroke [in]")
    thisDataFile.traces[thisDataFile.LOAD].setLabel("Load [lbf]")

    #Count the number of rows        
    print >>t, 'The number of lines is:', thisDataFile.number_of_lines

    #Get an initial estimate of the preload from the first 150 points.

    leadave=thisDataFile.find_preload(150)
    print >>t, 'The initial preload estimate is:', leadave

    #determine the failure point

    test_end=thisDataFile.find_end()
    if thisDataFile.Load_Drop_Line<thisDataFile.number_of_lines-1:
        print >>t, 'Load drop found at line:', thisDataFile.Load_Drop_Line
    
    print >>t, 'The max area occurs at line:', thisDataFile.Area_End_Line
    print >>t, 'The 95% stroke value is at line:',
    print >>t, thisDataFile.End_Of_Stroke_Line
    
    print >>t, 'The end of the test is line:', test_end
    
    print >>t, 'The end of the test is time:',
    print >>t, thisDataFile.getTimeData()[test_end]
    

    #get the load shift from the post failure region

    
    
    if thisDataFile.Area_End_Line<0.99*thisDataFile.number_of_lines:
        test_end=max([test_end,thisDataFile.Area_End_Line])
    postload_line=int(test_end+0.2*(thisDataFile.number_of_lines-test_end))
    #print postload_line
    postload=thisDataFile.find_postload(postload_line)
    #print postload
    #print 0.5*max(thisDataFile.getLoadData())
    
    if ( (test_end >= (0.99 * thisDataFile.number_of_lines) and leadave != 0)
        or postload > 0.5 * max(thisDataFile.getLoadData())): 
        print >>t, 'no post-failure zero-load data, using initial trace'
        loadshift = leadave
    else :
        loadshift = postload
        print >>t, 'Load offset from post failure data:', postload

    #Zero the load trace

    
    new_column=thisDataFile.getLoadData()
    for i in range(len(new_column)):
        new_column[i]-=loadshift
        
    while thisDataFile.number_of_columns < thisDataFile.ZL:
        thisDataFile.append_column([], "blank")
    
    thisDataFile.append_column(new_column, "Zeroed Load [lbf]")
    
    #Plot the data raw data and the blown up axis after zeroing the load

    picturename = plot_time_disp_zeroed_load(thisDataFile,'-post-shift',0,1,0.1,1)
    shutil.move(picturename,os.path.join(image_path,picturename)) 
    
    picturename = plot_time_disp_zeroed_load(thisDataFile,'_zerocheck-post-shift',0,1,0.1,0.1)
    shutil.move(picturename,os.path.join(image_path,picturename)) 
    

    # Find a new, better end point based on the shifted data

    test_end=thisDataFile.find_end()
    print >>t, 'The failure line is:', test_end


    # If there is a post failure region, cut it off.

    

    # Get and subtract out the initial displacement and time

    disp_start = 0.0
    disp_start=thisDataFile.getStrokeTrace().get_point(0)
    print >>t, 'Start displacement is:', disp_start
    thisDataFile.traces[1].shift_column(-disp_start)
    
    time_start = 0.0
    time_start = thisDataFile.getTimeTrace().get_point(0)
    print >>t, 'Start time is:', time_start
    thisDataFile.traces[0].shift_column(-time_start)
    

    # Plot the time and displcaement shifted data

    picturename = plot_time_zeroed_load(thisDataFile)
    shutil.move(picturename,os.path.join(image_path,picturename))
   

    #Cut off the initial, pre-test trace and plot the result     

    pulse_start=thisDataFile.find_start(0.4,0.05)
    print >>t, 'The start line is:', pulse_start
    
    if pulse_start>test_end :
        print >>t, 'start > end, adjusting...'

##work in progress


        test_end=thisDataFile.number_of_lines
    picturename = plot_rate_measure(thisDataFile, pulse_start, test_end)
    shutil.move(picturename,os.path.join(image_path,picturename)) 
    

    #Get the new time and displacement zeroes, subtract them, and plot the result

    
    picturename = plot_time_disp_zeroed_load(thisDataFile,'-reduced',0,1,0,1)
    new_picturename=picturename[:-4] + ".png"
    shutil.move(picturename,new_picturename)
    shutil.move(new_picturename,os.path.join(image_path,picturename))


    #Plot the final load-stroke curve

    picturename = plot_disp_zeroed_load(thisDataFile)
    shutil.move(picturename,os.path.join(image_path,picturename))
    
    thisDataFile.log_info(summary_file,test_end)
    
    if thisDataFile.Has_Measurement_File :
        if thisDataFile.Gage_Length_in !=0 and thisDataFile.CS_Area_in2 != 0:
            
            new_column=thisDataFile.getStrokeData()
            load_data=thisDataFile.getLoadData()
            
            slope_start = thisDataFile.find_load_pct(0.4)
            slope_end = thisDataFile.find_load_pct(0.5)

            slope = (load_data[slope_end] - load_data[slope_start])/\
                    (new_column[slope_end] - new_column[slope_start])
            print "modulus = ", str(slope/thisDataFile.CS_Area_in2)
            intercept = new_column[slope_start]-load_data[slope_start]/slope
            print "intercept = ",str(intercept)


            for i in range(len(new_column)):
                new_column[i]=(new_column[i]-intercept)/thisDataFile.Gage_Length_in
            thisDataFile.append_column(new_column,"Nominal Strain [in/in]")
            thisDataFile.NOM_STRAIN = len(thisDataFile.traces)-1
            
            new_column=thisDataFile.getZLData()
            for i in range(len(new_column)):
                new_column[i]=new_column[i]/thisDataFile.CS_Area_in2
            thisDataFile.append_column(new_column,"Stress [psi]")
            thisDataFile.PSI = len(thisDataFile.traces)-1

            test_end=thisDataFile.find_neg(test_end)

            picturename = \
            plot_stress_strain(thisDataFile,thisDataFile.PSI,thisDataFile.NOM_STRAIN, \
            0,test_end)
            shutil.move(picturename,os.path.join(image_path,picturename)) 
            


    #Calculate stuff and save it to the summary file

    #thisDataFile.log_info(summary_file,test_end)
    
    print >>t, time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.localtime())
    print >>t, 'user:', os.times()[0], 's'
    print >>t, 'system:', os.times()[1], 's'

    print >>t, ''
    

    #(end of analysis loop)


#Were all done, close the summary file

summary_file.close()
log_file.close()

