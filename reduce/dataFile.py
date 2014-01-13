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

import os
import csv
import tempfile
import shutil

from reducePlot import *

def strip_term(line):
    return line.rstrip('\n\r')
    #!!! the old code for strip_term is preserved below
    line_end = len(line)
    for i in range(1, min(line_end, 5)): #!!! needs study
        if line[-i] == '\n' or line[-i] == '\r':
            line_end -= 1
    line = line[:line_end]
    return line

class DataFile:
    has_measurement_file = False
    TIME, STROKE, LOAD = range(3) #!!! is there a better way of associating these enumerated types with their use? 
    column_labels = []
    if False: #!!! unused variablles, consider deleting them. 
        test_temp_f = 32.0
        test_temp_c = 0.0
    machine_rate = 0.0
    if False: #!!! unused variablles, consider deleting them. 
        machine_rate_m = 0.0
        machine_rate_in = 0.0
    cs_area_in2 = 0.0
    if False: #!!! unused variablles, consider deleting them. 
        width_mm = 0.0
        thickness_mm = 0.0
        cs_area_mm2 = 0.0
    gage_length_in = 0.0
    if False: #!!! unused variablles, consider deleting them. 
        gage_length_mm = 0.0
    load_drop_line = 0
    area_end_line = 0
    end_of_stroke_line = 0
    def __init__(self, *args, **kwargs):
        self.textfile = 'Default Datafile'
        self.number_of_columns = 0
        self.number_of_lines = 2
        self.traces = []
        self.get_traces()
        self.column_lengths = self.get_column_lengths()

    def __str__(self):
        inventory = ''
        for trace in self.traces:
            inventory += str(trace) + '\n'
        return inventory

    def find_neg(self, start):
        count = 0
        for line in self.get_load_data()[start:]:
            if float(line) < 0:
                return start + count
            count += 1

    def find_load(self, zero_load):
        count = 0
        for line in self.get_load_data():
            if float(line) > zero_load:
                return count
            count += 1

    def find_load_pct(self, zero_pct):
        count = 0
        load_data = self.get_load_data()
        max_load = max(load_data)
        zero_load = zero_pct * max_load
        for line in self.get_load_data():
            if float(line) > zero_load:
                return count
            count += 1

    def get_load_data(self):
        return self.traces[self.LOAD].get_data()
    def get_stroke_data(self):
        return self.traces[self.STROKE].get_data()
    def get_time_data(self):
        return self.traces[self.TIME].get_data()
    def get_number_of_columns(self, textfile):
        return len(self.traces)

    def count_lines(self):
        f = open(self.textfile, 'rU')
        f.readline(), #!!! to skip over header line without counting it? #!!! what is trailing comma for? 
        try:
            count = 0
            for line in f:
                count += 1
        finally:
            f.close()
        if False:
            #!!! Notice that first line count is one less than second line count. Why? Not counting header line? 
            print '@@@@@@@@@@@@@@ self.textfile="%s", count_lines=%s' % (
                self.textfile, count)
            print '@@@@@@@@@@@@@@ len(open(self.textfile, \'rU\')=', len(
                open(self.textfile, 'rU').readlines())
        return count

    def get_column(a_file, column_number):
        a_file.seek(0),
        column_data = []
        for line in a_file:
            words = line.split('\t') #!!! Why not split on any whitespace? 
            column_data += [words[column_number]]
        return column_data

    def get_column_lengths(self):
        try:
            column_lengths = []
            f = open(self.textfile, 'rU')
            f.readline(), #!!! to skip over header line without counting it? #!!! what is trailing comma for? 
            try:
                for trace in self.traces:
                    if len(trace) > 0:
                        column_lengths += [len(trace) - 1]
                    else:
                        column_lengths += [0]
            finally:
                f.close()
        except IOError:
            column_lengths = []
        return column_lengths

    def append_column(self, column_data, heading):
        f = open(self.textfile, 'rU')
        temp = tempfile.mktemp()
        g = open(temp, 'w')
        index = 0 #!!! index usage is awkward
        header = ''
        for label in self.column_labels:
            header += '\t'
            header += label
        header = header[1:] + '\t' + heading.strip() + '\n'
        g.write(header)
        try:
            for line in f:
                if index == 0: #!!! skipping over header
                    index += 1
                    continue
                else:
                    if len(strip_term(line)) > 1:
                        try:
                            line = strip_term(line) + '\t' + str(column_data[index - 1]) + '\n'
                        except IndexError:
                            line = strip_term(line) + '\t''\n' #!!! ???

                        g.write(line)
                        index += 1
        finally:
            f.close()
            g.close()
        shutil.move(temp, self.textfile)
        self.number_of_columns += 1

        try:
            a_trace = DataTrace(self.textfile, self.number_of_columns - 1, heading)
        except IndexError:
            a_trace = DataTrace(self.textfile, self.number_of_columns - 1, '')
        self.traces += [a_trace]
        self.column_labels += [a_trace.label]

        self.column_lengths += [len(column_data)]

    def get_traces(self):
        self.traces = []
        count = 0
        while True:
            try:
                trace = DataTrace(self.textfile, count, self.column_labels[count])
            except IndexError:
                trace = DataTrace(self.textfile, count, '')
            if trace.get_length() > 0:
                self.traces += [trace]
                try:
                    self.column_labels[count] = trace.label
                except IndexError:
                    self.column_labels += [trace.label]
            else:
                break
            count += 1
        self.column_lengths = []
        self.column_lengths = self.get_column_lengths()
        return self.traces

    def find_start(self, loadpct, strokepct):
        load = self.get_load_data()
        stroke = self.get_stroke_data()

        loadlinenumber = 0
        strokelinenumber = 0

        maxload = max(load)
        maxstroke = max(stroke)
        ## look for the beginning of the load pulse
        for each_load in load:
            loadlinenumber += 1
            if (each_load) > loadpct*maxload:
                #print loadlinenumber, each_load
                break
        ## look for the knee in the displacement curve
        for each_stroke in stroke:
            strokelinenumber += 1
            if each_stroke > strokepct * maxstroke:
                #print strokelinenumber, each_stroke
                break
        return max([loadlinenumber, strokelinenumber])

    def find_preload(self, size):
        array = self.get_load_data()
        if len(array) > size:
            return self.find_average(array[:size])
        else:
            return self.find_average(array)

    def find_postload(self, start):
        array = self.get_load_data()

        return self.find_average(array[start:])

    def find_average(self, array):
        try:
            average = sum(array)/len(array)
        except ZeroDivisionError:
            average = 0
        return average
        #!!! delete the old code below when the above is known to work. 
        #count = 0.0
        #sum = 0.0
        #for number in array:
        #    count += 1.0
        #    sum += number
        #if count > 0:
        #    return sum / count
        #else:
        #    return 0

    def find_end(self):
        time = self.get_time_data()
        disp = self.get_stroke_data()
        load = self.get_load_data()

        #calculate end based on load drop
        ld_count = 0
        pprime = []
        dlength = len(load)
        dfraction = dlength / 100
        #print dfraction
        for d in load[0:-(dfraction + 1)]:
            e = load[ld_count + dfraction]
            ld_count += 1
            pprime.append(d - e)
            #if ld_count < 14000:print ld_count, d - e
        #print 'ld_count', ld_count
        ld_count = 0
        pprime_max = max(pprime)
        #print 'pprime', pprime
        #print 'pprime_max' , pprime_max

        for each in pprime[:-1]:
            ld_count += 1
            #print 'ld_count', ld_count
            #print 'each_pprime', each
            if each > .99 * pprime_max:
                break
        if ld_count >= (dlength - dfraction - 5):
            ld_count = dlength

        #calculate end based on end of stroke
        maxdisp = max(disp)
        stroke_count = 0
        for each in disp:
            stroke_count += 1
            if each > .95 * maxdisp:
                break

        #calculate end based on area under curve
        area = 0
        maxarea = 0
        delta_t = time[2] - time[1]
        count = 0
        for each_load in load[:-21]:
            count += 1
            delta_a = (load[count] + each_load) / 2 * delta_t
            maxarea = max(area, maxarea)
            area += delta_a
            #print area

        area_count = 0
        area2 = 0
        for each_load in load[:-1]:
            area_count += 1
            area2 += (load[area_count] + each_load) / 2 * delta_t
            #print 'area_count', area_count, 'area', area, 'area2', area2
            if maxarea - area2 < .015 * area:
                break
        for each_load in load[area_count:-1]:
            if each_load > 0:
                area_count += 1
            else:
                break

        self.load_drop_line = ld_count
        self.area_end_line = area_count
        self.end_of_stroke_line = stroke_count

        #check for very low counts and return reasonable lowest value
        if area_count < 10 and ld_count < 10 and stroke_count < 10:
            return size(load)
        elif ld_count < 10 and stroke_count < 10:
            return area_count
        elif area_count < 10 and stroke_count < 10:
            return ld_count
        elif area_count < 10 and ld_count < 10:
            return stroke_count
        elif area_count < 10:
            return min([ld_count, stroke_count]) + 1
        elif ld_count < 10:
            return min([area_count, stroke_count]) + 1
        elif stroke_count < 10:
            return min([area_count, ld_count]) + 1
        else:
            return min([area_count, ld_count, stroke_count]) + 1

    def find_rate(self, pulse_start, pulse_end):
        time = self.get_time_data()
        disp = self.get_stroke_data()
        dispsum = 0
        timesum = 0
        for i in range(pulse_end - pulse_start):
            if i > 0:
                dispsum += (disp[pulse_start + i] - disp[pulse_start + i - 1])
                timesum += (time[pulse_start + i] - time[pulse_start + i - 1])
        rate = dispsum / timesum
        self.machine_rate = rate
        return rate


class DataFile_SL(DataFile):
    ZL = 6 #!!! need better name for this constant !!! value is suspect also

    def __init__(self, name, *args, **kwargs):
        DataFile.__init__(self, *args, **kwargs)
        self.textfile = name
        self.traces = [ #!!! use map()?
            DataTrace(self.textfile, 0, ''),
            DataTrace(self.textfile, 1, ''),
            DataTrace(self.textfile, 2, '')]
        self.column_labels = []
        self.traces = self.get_traces()
        self.number_of_columns = self.get_number_of_columns(self.textfile)
        self.number_of_lines = self.count_lines()
        #self.filebase = os.path.splitext(self.textfile)[0]
        self.filebase = ''
        self.extension = os.path.splitext(self.textfile)[1]
        self.column_labels[self.TIME] = 'Time [sec]'
        self.column_labels[self.LOAD] = 'Load [lbf]'
        self.column_labels[self.STROKE] = 'Stroke [in]'

    def get_zl_trace(self): return self.traces[self.ZL]
    def get_zl_data(self): return self.traces[self.ZL].get_data()

    def log_info(self, logfile, end_line):
        print >>logfile, '%s\t%s\t%s' % (
            os.path.basename(self.filebase),
            str(self.machine_rate),
            str(max(self.traces[6].data[:end_line])))
        #print self.traces[6].data[:end_line]

    def moby_foo(
        self,
        image_path,
        measurement_files,
        gage_length_in,
        n_points_for_est,
        summary_file):
        #!!! a better name for this method is needed and will reveal itself 
        #!!! as the refactoring work continues. 

        #!!! While I am converting following code to use method calls instead 
        #!!! of directly accessing f's variables, the code will get ugly. 
        #!!! After I figure out where the code really belongs, 
        #!!! it will become much simpler (and pretty). 
        #!!! 
        #!!! Please be patient.

        self.filebase = os.path.join(image_path,os.path.splitext(self.textfile)[0])

        if gage_length_in != 0: #!!! better way than sentinel value? 
            self.gage_length_in = gage_length_i

        for mfn in measurement_files:
            for specimen in mfn.specimens:
                if filename.find(specimen.stl_id) != -1:
                    print filename, 
                    print 'appears to have a measurement file entry:',
                    print specimen
                    self.has_measurement_file = True
                    self.cs_area_in2 = specimen.area

        plot_time_disp_load(self, '-raw', 0, 1, 0.1, 1)

        plot_time_disp_load(self, '_zerocheck', 0, 1, 0.1, 0.1)

        self.traces[self.TIME].set_label('Time [sec]') #!!!
        self.traces[self.STROKE].set_label('Stroke [in]') #!!!
        self.traces[self.LOAD].set_label('Load [lbf]') #!!!

        print 'The number of lines is:', self.number_of_lines

        # Get an initial estimate of the preload 
        # from the first n_points_for_est points. 
        leadave = self.find_preload(n_points_for_est)
        print 'The initial preload estimate is:', leadave

        # Determine the failure point. 
        test_end = self.find_end()
        if self.load_drop_line < self.number_of_lines - 1:
            print 'Load drop found at line:', self.load_drop_line

        print 'The max area occurs at line:', self.area_end_line
        print 'The 95% stroke value is at line:', self.end_of_stroke_line

        print 'The end of the test is line:', test_end
        print 'The end of the test is time:', self.get_time_data()[test_end] #!!! [test_end] is curious

        # Get the load shift from the post failure region. 
        if self.area_end_line < 0.99 * self.number_of_lines:
            test_end = max([test_end, self.area_end_line])
        postload_line = int(test_end + 0.2 * (self.number_of_lines - test_end))
        postload = self.find_postload(postload_line)

        if ((test_end >= 0.99 * self.number_of_lines and leadave != 0)
        or postload > 0.5 * max(self.get_load_data())):
            print 'no post-failure zero-load data, using initial trace'
            loadshift = leadave
        else:
            loadshift = postload
            print 'Load offset from post failure data:', postload

        #Zero the load trace #!!!

        new_column = self.get_load_data()
        for i in range(len(new_column)):
            new_column[i] -= loadshift

        while self.number_of_columns < self.ZL:
            self.append_column([], 'blank')

        self.append_column(new_column, 'Zeroed Load [lbf]')

        #Plot the data raw data and the blown up axis after zeroing the load

        plot_time_disp_zeroed_load(self, '-post-shift', 0, 1, 0.1, 1)

        plot_time_disp_zeroed_load(self, '_zerocheck-post-shift', 0, 1, 0.1, 0.1)

        # Find a new, better end point based on the shifted data
        test_end = self.find_end()
        print 'The failure line is:', test_end

        # If there is a post failure region, cut it off. !!!?

        # Get and subtract out the initial displacement and time

        disp_start = self.traces[self.STROKE].get_point(0)
        print 'Start displacement is:', disp_start
        self.traces[1].shift_column(-disp_start)

        time_start = self.traces[self.TIME].get_point(0)
        print 'Start time is:', time_start
        self.traces[0].shift_column(-time_start)

        # Plot the time and displacement shifted data. 
        plot_time_zeroed_load(self)

        # Cut off the initial, pre-test trace and plot the result. 
        pulse_start = self.find_start(0.4, 0.05)
        print 'The start line is:', pulse_start

        if pulse_start > test_end:
            print 'start > end, adjusting...'

                ##work in progress

            test_end = self.number_of_lines

        plot_rate_measure(self, pulse_start, test_end)

        # Get the new time and displacement zeroes, subtract them, 
        # and plot the result. 
        plot_time_disp_zeroed_load(self, '-reduced', 0, 1, 0, 1)

        # Plot the final load-stroke curve. 
        plot_disp_zeroed_load(self)

        self.log_info(summary_file, test_end)

        if self.has_measurement_file \
        and self.gage_length_in != 0 \
        and self.cs_area_in2 != 0:
            new_column = self.get_stroke_data()
            load_data = self.get_load_data()

            slope_start = self.find_load_pct(0.4)
            slope_end = self.find_load_pct(0.5)

            slope = ((load_data[slope_end] - load_data[slope_start])
            /       (new_column[slope_end] - new_column[slope_start]))
            print 'modulus =', slope / self.cs_area_in2
            intercept = new_column[slope_start]-load_data[slope_start] / slope
            print 'intercept =', intercept

            for i in range(len(new_column)):
                new_column[i] = (new_column[i]-intercept) / self.gage_length_in
            self.append_column(new_column, 'Nominal Strain [in/in]')
            nom_strain = len(self.traces)-1

            new_column = self.ZL
            for i in range(len(new_column)):
                new_column[i] /= self.cs_area_in2
            self.append_column(new_column, 'Stress [psi]')
            psi = len(self.traces) - 1

            test_end = self.find_neg(test_end)

            plot_stress_strain(self, psi, nom_strain, 0, test_end)

class DataTrace:
    def __init__(self, filename, column, label, *args, **kwargs):
        self.textfile = filename
        self.column = column
        self.length = 0 #!!! delete this line? 
        self.data = self.get_data()
        self.length = self.get_length()
        if label == '':
            self.label = self.get_label()
        else:
            self.label = label

    def __len__(self):
        return self.get_length()

    def __str__(self):
        return str(self.textfile) + ' ' + str(self.column) + ' ' + self.label + ' ' + str(self.length)

    def get_length(self): #!!! return value versus self.length? 
        length = len(self.data)
        if length != 0:
            return length
        elif os.access(self.textfile, os.R_OK):
            f = open(self.textfile, 'rU')
            reader = csv.reader(open(self.textfile, 'rU'), delimiter='\t')
            length = 0
            for line in reader:
                try:
                    #words = line.split('\t')
                    #words = self.tdd_split(line)
                    #print words
                    if line[self.column].strip() != '':
                        length += 1
                except:
                    continue
            f.close()
        self.length = length
        return length

    def get_label(self):
        if os.access(self.textfile, os.R_OK):
            f = open(self.textfile, 'rU')
            first_line = f.readline().split('\t')
            if len(first_line) > self.column:
                self.label = first_line[self.column].strip()
            else:
                self.label = 'default no-label'
        else:
            self.label = 'default no-file'
        return self.label

    def set_label(self, label):
        self.label = label.strip()
        return self.label

    def get_data(self):
        if self.length != 0:
            return self.data
        elif os.access(self.textfile, os.R_OK):
            f = open(self.textfile, 'rU')
            reader = csv.reader(f, delimiter='\t')
            data = []

            is_first_time = True
            for line in reader:
                #words = line.split('\t')
                #words = self.tdd_split(line)
                if is_first_time:
                    is_first_time = False
                    continue
                if len(line) > self.column and line[self.column] != '':
                    try:
                        data += [float(line[self.column].strip())]
                    except IndexError:
                        print 'IndexError', len(line), self.column
                    except ValueError:
                        print 'ValueError', 'point:', line[self.column], 'length:', len(line), 'column:', self.column
                        continue
            f.close()
        else:
            data = []
            #print 'NO DATA!!!'
        return data

    def tdd_split(self, line):
        words = []
        while line != '':
            temp = line.partition('\t')
            words += [temp[0].strip()]
            line = temp[2]
            #print temp
        #print words
        return words

    def get_point(self, row):
        count = 0
        for word in self.get_data():
            if count == row:
                return float(word)
            count += 1
        return 1 / 0 #!!! ???

    def shift_column(self, shift):
        temp = tempfile.mktemp()
        f = open(self.textfile, 'rU')
        reader = csv.reader(f, delimiter='\t')
        g = open(temp, 'w')
        writer = csv.writer(g, delimiter='\t')
        array = []
        firstline = True
        for line in reader:
            #print line
            if firstline == True:
                writer.writerow(line)
                firstline = False
            else:
                try:
                    number = float(line[self.column])
                    number += shift
                    output_line = line[0:self.column] + [str(number)] + line[self.column + 1:]
                    #print line
                    #print output_line
                except ValueError:
                    #print 'ValueError', line
                    continue
                except IndexError:
                    #print 'IndexError', line
                    continue
                writer.writerow(output_line)
        f.close()
        g.close()

        shutil.move(temp, self.textfile)

        self.length = 0
        self.get_data()
        self.length = self.get_length()

