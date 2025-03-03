#
#
# Name: maude2aut.py - transformation of Maude LTS to CADP LTS (aut) + bisim check with CADP
# Authors: Gwen and Paco
#
################################################################################

#!/usr/bin/python3

import sys
import re
import os

from subprocess import call

class MAUDEtoAUT:

    def __init__(self):
        print()

    def readLTS(self, filename):
            ff = open(filename, 'r')
            alllines=ff.read()

            # extract name LTS
            pattern=r'lts\(\"(.*?)\"\)'
            result = re.search(pattern, alllines)
            if result:
                ltsname=result.group(1)

            # initial state
            pattern=r'initial : state\(\"(.*?)\"\)'
            result = re.search(pattern, alllines)
            if result:
                initstate=result.group(1)

            # all states (set)
            pattern=r'state\(\"(.*?)\"\)'
            result = re.findall(pattern, alllines)
            states=set()
            for s in result:
                states.add(s)

            # all transitions (set)
            pattern=r'transition\(state\(\"(.*?)\"\), \"(.*?)\", state\(\"(.*?)\"\)\)'
            result = re.findall(pattern, alllines)
            transitions=set()
            for t in result:
                transitions.add(t)

            return (ltsname, initstate, states, transitions)

    def dumpAUT(self, lts):
        stid = dict()   # new state identifiers starting from 0 and successive numbers
        counter=1
        for s in lts[2]:
            if (s==lts[1]):
                stid[s]=0
            else:
                stid[s]=counter
                counter=counter+1

        ofile=open(lts[0]+'.aut', 'w')
        ofile.write("des(0,"+str(len(lts[3]))+","+str(len(lts[2]))+")\n")
        for t in lts[3]:
            ofile.write("("+str(stid[t[0]]) + ",\"" + t[1]+ "\"," +str(stid[t[2]])+")\n")

    # Generates two aut and call CADP for comparing them wrt branching bisimulation
    def dumpAndCompare(self, firstarg, secondarg):
        res1=self.readLTS(firstarg)
        self.dumpAUT(res1)
        res2=self.readLTS(secondarg)
        self.dumpAUT(res2)
        call('bcg_io '+res1[0]+'.aut .bcg', shell=True)
        call('bcg_io '+res2[0]+'.aut .bcg', shell=True)
        res=call('bcg_open '+res1[0]+'.bcg bisimulator -branching '+res2[0]+'.bcg', shell=True)
        print(res)



if __name__ == '__main__':

    firstarg=sys.argv[1]
    secondarg=sys.argv[2]
    m2a=MAUDEtoAUT()
    m2a.dumpAndCompare(firstarg, secondarg)
