#"Copyright 2009 Bryan Harris"
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

def strip_term(line):
    line_end=len(line)
    for i in range(1,min(line_end,5)):
        if ord(line[-i]) == 10 or ord(line[-i]) == 13:
            line_end = line_end - 1
    line = line[0:line_end]
    return line
        
class dataFile:
    Has_Measurement_File = False
    TIME     =  0
    STROKE   =  1
    LOAD     =  2
    column_labels=[]
    Specimen_ID = "STL xxx-xxx"
    Test_Temp_F = 32.0
    Test_Temp_C = 0.0
    Machine_Rate = 0.0
    Machine_Rate_m = 0.0
    Machine_Rate_in = 0.0
    Width_in = 0.0
    Thickness_in = 0.0
    CS_Area_in2 = 0.0
    Width_mm = 0.0
    Thickness_mm = 0.0
    CS_Area_mm2 = 0.0
    Gage_Length_in = 0.0
    Gage_Length_mm = 0.0
    Load_Drop_Line = 0
    Area_End_Line = 0
    End_Of_Stroke_Line = 0
    def __init__(self, *args, **kwargs):
        self.textfile = "Default Datafile"
        self.number_of_columns = 0
        self.number_of_lines = 2
        self.traces = []
        self.get_traces()
        self.column_lengths=self.get_column_lengths()
        
    def __str__(self):
        inventory = ""
        for trace in self.traces :
            inventory += str(trace) + '\n'
        return inventory
    
    def find_neg(self,start):
        count = 0
        for line in self.getLoadData()[start:]:
            if float(line) < 0:
                return start+count
            count += 1
            
    def find_load(self, zero_load):
    
        count = 0
        for line in self.getLoadData():
            if float(line) > zero_load:
                return count
            count += 1

    def find_load_pct(self, zero_pct):
    
        count = 0
        loadData = self.getLoadData()
        max_load = max(loadData)
        zero_load = zero_pct * max_load
        for line in self.getLoadData():
            if float(line) > zero_load:
                return count
            count += 1
         
    def getLoadTrace(self): return self.traces[self.LOAD]
    def getStrokeTrace(self): return self.traces[self.STROKE]
    def getTimeTrace(self): return self.traces[self.TIME]
    def getLoadData(self): return self.traces[self.LOAD].getData()
    def getStrokeData(self): return self.traces[self.STROKE].getData()
    def getTimeData(self): return self.traces[self.TIME].getData()
    def get_number_of_lines(self): return self.number_of_lines
    def get_number_of_columns(self, textfile):
        return len(self.traces)
    
    def count_lines(self):
        
        f = open(self.textfile, 'rU')
        f.readline(),
        try:
            count = 0
            for line in f:
                count += 1
        finally:
            f.close()
        return count
    
    def getColumn(aFile,column_number):
        
        aFile.seek(0),
        column_data = []
        for line in aFile:
            words = line.split('\t')
            column_data += [words[column_number]]
        return column_data
    
    def get_column_lengths(self):
         
        try :
            column_lengths=[]
            f = open(self.textfile, 'rU')
            f.readline(),
            try:
                for trace in self.traces:
                    if len(trace)>0:
                        column_lengths+=[len(trace)-1]
                    else : column_lengths+=[0]
            finally:
                f.close()
        except(IOError):
            column_lengths=[]
            
        return column_lengths
    
    def append_column(self,column_data,heading):
    
        f = open(self.textfile, 'rU')
        temp=tempfile.mktemp()
        g = open(temp, 'w')
        index=0
        header=""
        for label in self.column_labels:
            header += '\t'
            header += label
        header = header[1:]+'\t'+heading.strip()+'\n'
        g.write(header)
        try:
            for line in f:
                if index == 0:
                    index += 1
                    continue
                else :
                    if len(strip_term(line))>1:
                        try:
                            line=strip_term(line)+'\t'+str(column_data[index-1])+'\n'
                        except(IndexError):
                            line=strip_term(line)+'\t''\n'
                        
                        g.write(line)
                        index += 1
        finally:
            f.close()
            g.close()
        shutil.move(temp,self.textfile)
        self.number_of_columns+=1
        
        try:
            aTrace=dataTrace(self.textfile,self.number_of_columns-1,heading)
        except(IndexError):
            aTrace=dataTrace(self.textfile,self.number_of_columns-1,"")
        self.traces+=[aTrace]
        self.column_labels+=[aTrace.label]
            
        self.column_lengths+=[len(column_data)]
        
    def get_traces(self):
        self.traces=[]
        #print "get_traces"
        count = 0
        while True :
            try:
                trace=dataTrace(self.textfile,count,self.column_labels[count])
            except(IndexError):
                trace=dataTrace(self.textfile,count,"")
            if trace.getLength()>0:
                self.traces+=[trace]
                try:
                    self.column_labels[count]=trace.label
                except(IndexError):
                    self.column_labels+=[trace.label]
            else:
                break
            count += 1
        self.column_lengths=[]
        self.column_lengths=self.get_column_lengths()
        return self.traces
    
    def find_start(self,loadpct,strokepct):
        
        load = self.getLoadData()
        stroke = self.getStrokeData()
        
        loadlinenumber = 0
        strokelinenumber = 0
        
        maxload = max(load)
        maxstroke = max(stroke)
        ## look for the beginning of the load pulse
        for each_load in load :
            loadlinenumber += 1
            if (each_load) > loadpct*maxload : 
                #print loadlinenumber, each_load
                break
        ## look for the knee in the displacement curve
        for each_stroke in stroke :
            strokelinenumber +=1
            if (each_stroke > strokepct * maxstroke) : 
                #print strokelinenumber, each_stroke
                break
        return max([loadlinenumber,strokelinenumber])

    def find_preload(self,size):
        
        array = self.getLoadData()
        if len(array) > size : return self.find_average(array[:size])
        else : return self.find_average(array)
        
    def find_postload(self,start):
        
        array = self.getLoadData()
    
        return self.find_average(array[start:])
    
    def find_average(self,array):
        
        count = 0.0
        sum = 0.0
        for number in array :
            count += 1.0
            sum += number
        if count>0:
            return sum/count
        else : return 0
    
    def find_end(self):
        time = self.getTimeData()
        disp = self.getStrokeData()
        load = self.getLoadData()
    
        #calculate end based on load drop
        ld_count = 0
        pprime = []
        dlength=len(load)
        dfraction=dlength/100
        #print dfraction
        for d in load[0:-(dfraction+1)]:
            e = load[ld_count+dfraction]
            ld_count += 1
            pprime.append(d-e)
            #if ld_count<14000:print ld_count, d-e
        #print "ld_count",ld_count
        ld_count = 0
        pprime_max = max(pprime)
        #print "pprime", pprime
        #print "pprime_max" ,pprime_max
        
        for each in pprime[:-1] :
            ld_count += 1
            #print "ld_count", ld_count
            #print "each_pprime",each
            if each > .99 * pprime_max : break
        if ld_count>=(dlength-dfraction-5):
            ld_count=dlength

        #calculate end based on end of stroke
        maxdisp = max(disp)
        stroke_count = 0
        for each in disp :
            stroke_count += 1
            if each > .95 * maxdisp : break

        #calculate end based on area under curve
        area = 0
        maxarea = 0
        deltat = time[2] - time[1]
        count = 0
        for each_load in load[:-21] :
            count += 1
            deltaA = (load[count]+each_load)/2 * deltat
            maxarea=max(area,maxarea)
            area += deltaA
            #print area
            
        area_count = 0
        area2 = 0
        for each_load in load[:-1] :
            area_count += 1
            area2 += (load[area_count]+each_load)/2 * deltat
            #print "area_count",area_count,"area",area,"area2", area2
            if ((maxarea - area2) < .015*area) : 
                break
        for each_load in load[area_count:-1] :
            if each_load>0 :
                area_count += 1
            else :
                break

        self.Load_Drop_Line = ld_count
        #print self.Load_Drop_Line
        self.Area_End_Line = area_count
        #print self.Area_End_Line
        self.End_Of_Stroke_Line = stroke_count
        #print self.End_Of_Stroke_Line
               
        #check for very low counts and return reasonable lowest value
        if area_count<10 and ld_count<10 and stroke_count<10 :
            return size(load)
        elif ld_count<10 and stroke_count<10:
            return area_count
        elif area_count<10 and stroke_count<10:
            return ld_count
        elif area_count<10 and ld_count<10:
            return stroke_count
        elif area_count<10 :
            return min([ld_count, stroke_count])+1
        elif ld_count<10 :
            return min([area_count, stroke_count])+1
        elif stroke_count<10 :
            return min([area_count, ld_count])+1
        else:
            return min([area_count, ld_count, stroke_count])+1
        
    def find_rate(self,pulse_start,pulse_end):
        time = self.getTimeData()
        disp = self.getStrokeData()
        dispsum=0
        timesum=0
        for i in range(pulse_end-pulse_start):
            if i>0 : 
                dispsum+=(disp[pulse_start+i]-disp[pulse_start+i-1])
                timesum+=(time[pulse_start+i]-time[pulse_start+i-1])
        rate=dispsum/timesum
        self.Machine_Rate = rate
        return rate
    
        
class dataFile_SL(dataFile):
    BLANK1   =  3
    BLANK2   =  4
    BLANK3   =  5
    ZL       =  6
    NOM_STRAIN   =  7
    PSI      =  8
    KSI      =  9
    MPA      = 10
    def __init__(self, name, *args, **kwargs):
        dataFile.__init__(self, *args, **kwargs)
        self.textfile=name
        self.traces=[dataTrace(self.textfile,0,""),dataTrace(self.textfile,1,""),dataTrace(self.textfile,2,"")]
        self.column_labels=[]
        self.traces=self.get_traces()
        self.number_of_columns=self.get_number_of_columns(self.textfile)
        self.number_of_lines=self.count_lines()
        self.filebase=os.path.splitext(self.textfile)[0]
        self.extension=os.path.splitext(self.textfile)[1]
        self.column_labels[self.TIME]="Time [sec]"
        self.column_labels[self.LOAD]="Load [lbf]"
        self.column_labels[self.STROKE]="Stroke [in]"
    
    def getZLTrace(self): return self.traces[self.ZL]
    def getZLData(self): return self.traces[self.ZL].getData()
    
    def log_info(self, logfile, end_line):
        logfile.write("\n" + self.filebase+ "\t"+ str(self.Machine_Rate)+ "\t"+ str(max(self.traces[6].data[:end_line])))
        #print self.traces[6].data[:end_line]

    
class dataTrace:
    def __init__(self, filename, column, label, *args, **kwargs):
        
        self.textfile=filename
        self.column=column
        self.length=0
        self.data=self.getData()
        self.length=self.getLength()
        if label == "":
            self.label=self.getLabel()
        else : self.label=label
        
    def __len__(self):
        return self.getLength()
                
    def __str__(self):
        return str(self.textfile)+' '+str(self.column)+' '+self.label+' '+str(self.length)
        
    def getLength(self):
        
        length = len(self.data)
        if length!=0:
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
                    if line[self.column].strip() != "":
                        length += 1
                except:
                    continue
            f.close()
        self.length=length
        return length
    
    def getLabel(self):
        
        if os.access(self.textfile, os.R_OK):
            f = open(self.textfile, 'rU')
            firstLine=f.readline().split('\t')
            if len(firstLine)>self.column:
                self.label=firstLine[self.column].strip()
            else :
                self.label="default no-label"
        else :
            self.label="default no-file"
        return self.label
    
    def setLabel(self, label):
        
        self.label=label.strip()
        return self.label
        
    def getData(self):
        if self.length!=0:
            return self.data   
        elif os.access(self.textfile, os.R_OK):
            f = open(self.textfile, 'rU')
            reader = csv.reader(f, delimiter='\t')
            data = []

            skip=True
            for line in reader:
                #words = line.split('\t')
                #words = self.tdd_split(line)
                if skip == True :
                    skip = False
                    continue
                if len(line)>self.column and line[self.column] != "":
                    try:
                        data += [float(line[self.column].strip())]
                    except(IndexError):
                        print "IndexError",len(line),self.column
                    except(ValueError):
                        print "ValueError","point:",line[self.column],"length:",len(line),"column:",self.column
                        continue
            f.close()
        else:
            data = []
            #print "NO DATA!!!"
        return data
    
    def tdd_split(self,line):
        words = []
        while line!="":
            temp=line.partition('\t')
            words+=[temp[0].strip()]
            line=temp[2]
            #print temp
        #print words
        return words
    
    def get_point(self, row):
        count = 0
        for word in self.getData():
            if count == row :
                return float(word)
            count += 1
        return 1/0
    
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
                try :
                    number = float(line[self.column])
                    number += shift
                    output_line = line[0:self.column]+[str(number)]+line[self.column+1:]
                    #print line
                    #print output_line
                except(ValueError):
                    #print "ValueError",line
                    continue
                except(IndexError):
                    #print "IndexError",line
                    continue
                writer.writerow(output_line)
        f.close()
        g.close()
        
        shutil.move(temp,self.textfile)
        
        self.length=0
        self.getData()
        self.length=self.getLength()
        
