#"Copyright 2009 Bryan Harris"
# Copyright 2011 James Prior
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

import pylab as p
import tempfile
import os

MAX_PLOT_POINTS = 500 #!!! Why bother with a limit? What's the drawback of not limiting them? 

def decimate(array, points):
    if not isinstance(points, int):
        raise Error, 'number of points should be an integer'
    if len(array) / 2 <= points:
        return array
    interval = int(len(array)/points)
    return(array[::interval])

def plot_time_disp_load(f, extra_label, xmin_pct, xmax_pct, ymin_pct, ymax_pct):
    #Get the filename without the (!3 digit!) extension and create a picture name based on that

    picturename = f.filebase + '-time-stroke-load' + extra_label + '.png'
    #!!! 2011-07-23 delete f line after a few days f = open(f.textfile, 'rU') #!!! f is never referenced. 
    p.title('Time - Disp - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_time_data(), f.get_load_data(), 'b-', label='Load')
    p.ylabel('Load [lbf]')
    p.legend(loc=2)
    p.axhline(0, color='k')
    v = p.axis()
    p.axis((xmin_pct * v[0], xmax_pct * v[1], ymin_pct * v[2], ymax_pct * v[3]))
    p.twinx()

    p.plot(f.get_time_data(), f.get_stroke_data(), 'r--', label='Disp')
    v = p.axis()
    p.axis((xmin_pct * v[0], xmax_pct * v[1], ymin_pct * v[2], ymax_pct * v[3]))
    p.xlabel('Time [sec]')
    p.ylabel('Disp [in]')
    p.legend(loc=1)
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_time_disp_zeroed_load(f, extra_label, xmin_pct, xmax_pct, ymin_pct, ymax_pct):
    #Get the filename without the (!3 digit!) extension and create a picture name based on that

    picturename = f.filebase + '-time-stroke-load' + extra_label + '.png'

    p.title('Time - Disp - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_time_data(), f.get_zl_data(), 'b-', label='Load')
    p.ylabel('Load [lbf]')
    p.legend(loc=2)
    p.axhline(0, color='k')
    v = p.axis()
    p.axis((xmin_pct * v[0], xmax_pct * v[1], ymin_pct * v[2], ymax_pct * v[3]))
    p.twinx()
    p.plot(f.get_time_data(), f.get_stroke_data(), 'r--', label='Disp')
    v = p.axis()
    p.axis((xmin_pct * v[0], xmax_pct * v[1], ymin_pct * v[2], ymax_pct * v[3]))
    p.xlabel('Time [sec]')
    p.ylabel('Disp [in]')
    p.legend(loc=1)
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_time_load(f):
    picturename = f.filebase + '-time-load.png'

    p.title('Time - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_time_data(), f.get_load_data(), 'k+', lw=2)
    v = p.axis()
    p.axis((0, v[1], 0, v[3]))
    p.xlabel('Time [sec]')
    p.ylabel('Load [lbf]')
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_time_zeroed_load(f):
    picturename = f.filebase + '-time-load.png'

    p.title('Time - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_time_data(), f.get_zl_data(), 'k+', lw=2)
    v = p.axis()
    p.axis((0, v[1], 0, v[3]))
    p.xlabel('Time [sec]')
    p.ylabel('Load [lbf]')
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_rate_measure(f, start_line, end_line):
    time_trace = f.get_time_data()
    stroke_trace = f.get_stroke_data()

    picturename = f.filebase + '-rate_measure.png'
    p.title('Time - Disp - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(decimate(time_trace[start_line:end_line], MAX_PLOT_POINTS),
        decimate(stroke_trace[start_line:end_line], MAX_PLOT_POINTS),
        'b-', label='Disp')

    stroke_rate = f.find_rate(start_line, end_line)
    fit_disp = []
    stroke_offset = stroke_trace[start_line] - stroke_rate * time_trace[start_line]
    time_points = decimate(time_trace[start_line:end_line], 10)
    for each in time_points:
        fit_disp.append(stroke_rate * each + stroke_offset)
    fit_label = 'rate=' + str('%10.*f' % (8, stroke_rate)) + ' in/sec'
    p.plot(time_points, fit_disp, 'kx-', label=fit_label, ms=7)
#    p.text(.5, .5, 'HERE IS SOME TEXT!!!', color='k')

    p.ylabel('Disp [in]')
    p.legend(loc=2)

    p.twinx()
    p.plot(decimate(time_trace[start_line:end_line], MAX_PLOT_POINTS),
        decimate(f.get_zl_data()[start_line:end_line], MAX_PLOT_POINTS),
        'r--', label='Load')
    v = p.axis()
    p.axis((v[0], v[1], 0, v[3]))
    p.xlabel('Time [sec]')
    p.ylabel('Load [lbf]')
    p.legend(loc=1)
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_disp_load(f):
    picturename = f.filebase + '-stroke-load.png'
    p.title('Disp - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_stroke_data(), f.get_load_data(), 'g-')
    v = p.axis()
    p.axis((0, v[1], 0, v[3]))
    p.ylabel('Load [lbf]')
    p.xlabel('Disp [in]')
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_disp_zeroed_load(f):
    picturename = f.filebase + '-stroke-load.png'
    p.title('Disp - Load' + '\n' + os.path.basename(f.filebase))
    p.plot(f.get_stroke_data(), f.get_zl_data(), 'g-')
    v = p.axis()
    p.axis((0, v[1], 0, v[3]))
    p.ylabel('Load [lbf]')
    p.xlabel('Disp [in]')
    p.savefig(picturename)
    p.close('all')
    return picturename

def plot_stress_strain(f, stress, strain, start_line, end_line):
    picturename = f.filebase + '-stress-strain.png'
    p.title('Stress - Nominal Strain' + '\n' + os.path.basename(f.filebase))
    strain_data = f.traces[strain].get_data()
    #print start_line
    #print end_line
    #print len(strain_data)
    strain_data = strain_data[start_line:end_line]
    #print len(strain_data)
    stress_data = f.traces[stress].get_data()
    stress_data = stress_data[start_line:end_line]
    p.plot(strain_data, stress_data, 'g-')
    v = p.axis()
    p.axis((0, v[1], 0, v[3]))
    p.ylabel(f.traces[stress].label)
    p.xlabel(f.traces[strain].label)
    p.savefig(picturename)
    p.close('all')
    return picturename
