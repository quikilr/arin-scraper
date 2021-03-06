#!/usr/bin/env python3
# Written by jack @ nyi
# Licensed under FreeBSD's 3 clause BSD license. see LICENSE

'''This class calls the system's "ping" command and stores the results'''

class sys_ping:
    '''this class is a python wrapper for UNIX system ping command, subclass ping does the work, last stores data from the last sysping.ping'''

    def ping(target,count,opts):
        '''conducts a ping, returns the data and populates the "last" subclass'''
        import subprocess
        #check to see if the ping count can be used as number, if not, return with an error code
        try:
            int(count)
        except:
            return -1
        count = str(count)
        indata = ""
        sys_ping.last.opts = opts
        sys_ping.last.host = target
        #actually do a syscall for the ping and output the data to indata. If ping fails to find a host, it returns error status 2, capture the error and return an error message
        try:
            if opts == None:
                indata = subprocess.check_output(["ping","-c",count,target],stderr=subprocess.STDOUT)
            else:
                sys_ping.last.opts = opts
                indata = subprocess.check_output(["ping","-c",count,opts,target],stderr=subprocess.STDOUT)
            #if this works, return a success, which is the default state.
            sys_ping.last.success = True
        except subprocess.CalledProcessError:
            #if ping returns an error code, return a failure, and mark the success flag as false
            sys_ping.last.success = False
            return {-1:"error: ping host unreachable"}
        #strip trailing and leading characters, and split the lines into a list.
        indata = str(indata).strip("b'")
        indata = indata.strip()
        indata = indata.split('\\n')
        #last line is a blank, get rid of it
        indata.pop()
        #next line is the averages, keep splitting until we have a list of the averages.
        avg_line     = indata.pop()
        avg_line     = avg_line.split()[3]
        avg_line     = avg_line.split("/")
        #fill the "last" class with data from the avg_line
        sys_ping.last.min_time  = avg_line[0]
        sys_ping.last.avg_time  = avg_line[1]
        sys_ping.last.max_time  = avg_line[2]
        sys_ping.last.mdev_time = avg_line[3]
        #then comes the summary line split and populate "last" class
        sum_line               = indata.pop()
        sum_line               = sum_line.split()
        sys_ping.last.sent     = sum_line[0]
        sys_ping.last.recieved = sum_line[3]
        sys_ping.last.pct_loss = sum_line[5]
        sys_ping.last.op_time  = sum_line[9]
        #this is basicly a spacer line, throw it out as well, and a blank line above it
        indata.pop()
        indata.pop()
        #after this is the result of the ping packets. fill a sequnce list
        sequence = {}
        #the first line is a worthless header.
        del(indata[0])
        #the rest of them are the actual ping sequence, fill them into a dictionary of sequence:pingtime
        for line in indata:
            line = line.split()
            #fifth [4] entry is the first we care about, the sequence number. its generally icmp_seq=<#> lets keep splitting until we get the raw number.
            seq  = line[4].split("=")[1]
            #seventh [6] entry is the second thing we care about, its the actual ping time in milliseconds.
            time = line[6].split("=")[1]
            sequence[seq] = time
        sys_ping.last.sequence = sequence
        return sequence
    class last:
        '''This class stores data from last sys_ping.ping()'''
        #blank items for avg_line
        min_time,avg_time,max_time,mdev_time = 0,0,0,0
        #blank items for sum_line
        sent,recieved,pct_loss,op_time = 0,0,0,0
        host = ""
        opts = ""
        success = ""
        sequence = {}

